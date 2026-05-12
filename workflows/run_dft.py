from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from matagent_lab.chemistry import estimate_material_properties
from matagent_lab.simulation_io import write_quantum_espresso_inputs, write_vasp_inputs
from matagent_lab.visualization import write_dft_summary_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare DFT inputs and write a visual result preview.")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--engine", choices=["qe", "vasp", "both"], default="qe")
    parser.add_argument("--relax", action="store_true")
    parser.add_argument("--bands", action="store_true")
    parser.add_argument("--prototype", choices=["auto", "perovskite", "cubic"], default="auto")
    parser.add_argument("--kpoints", default="4,4,4", help="Comma-separated Monkhorst-Pack mesh.")
    parser.add_argument("--encut", type=int, default=520, help="VASP plane-wave cutoff in eV.")
    parser.add_argument("--ecutwfc", type=float, default=60.0, help="QE wavefunction cutoff in Ry.")
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--plot", default=None, help="Optional SVG plot path. Use --no-plot to skip.")
    parser.add_argument("--no-plot", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    properties = estimate_material_properties(args.formula, "cross_domain")
    input_root = Path(args.input_dir or f"runs/{_safe_name(args.formula)}_dft_inputs")
    kpoints = _parse_mesh(args.kpoints)
    input_sets = []
    if args.engine in {"qe", "both"}:
        input_sets.append(
            write_quantum_espresso_inputs(
                args.formula,
                input_root / "qe" if args.engine == "both" else input_root,
                prototype=args.prototype,
                kpoints=kpoints,
                ecutwfc=args.ecutwfc,
                relax=args.relax,
            )
        )
    if args.engine in {"vasp", "both"}:
        input_sets.append(
            write_vasp_inputs(
                args.formula,
                input_root / "vasp" if args.engine == "both" else input_root,
                prototype=args.prototype,
                kpoints=kpoints,
                encut=args.encut,
                relax=args.relax,
                bands=args.bands,
            )
        )

    result = {
        "workflow": "dft",
        "formula": args.formula,
        "engine": args.engine,
        "relaxed": args.relax,
        "bands": args.bands,
        "input_dir": str(input_root),
        "input_files": [str(path) for input_set in input_sets for path in input_set.files],
        "input_metadata": [input_set.metadata for input_set in input_sets],
        "properties": properties,
        "bandgap_proxy_ev": properties["bandgap_proxy_ev"],
        "stability_score": properties["stability_score"],
        "scf_trace": _demo_scf_trace(properties),
        "relaxation_trace": _demo_relaxation_trace(properties) if args.relax else [],
        "band_trace": _demo_band_trace(properties) if args.bands else [],
    }
    if not args.no_plot:
        plot_path = Path(args.plot or f"runs/{_safe_name(args.formula)}_dft.svg")
        write_dft_summary_svg(result, plot_path)
        result["plot_svg"] = str(plot_path)
    output_path = Path(args.out or f"runs/{_safe_name(args.formula)}_dft.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    if result.get("plot_svg"):
        print(f"Wrote {result['plot_svg']}")


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum())


def _parse_mesh(raw: str) -> tuple[int, int, int]:
    parts = [int(part.strip()) for part in raw.replace("x", ",").split(",") if part.strip()]
    if len(parts) != 3:
        raise ValueError("--kpoints must contain three integers, for example 4,4,4")
    return parts[0], parts[1], parts[2]


def _demo_scf_trace(properties: dict[str, float]) -> list[dict[str, float]]:
    base_gap = properties["bandgap_proxy_ev"]
    return [
        {
            "iteration": float(index),
            "residual": round(10 ** (-1.2 - 0.55 * index), 10),
            "energy_ev": round(-8.0 - 0.18 * base_gap - 0.42 * (1.0 - math.exp(-index / 3.0)), 6),
        }
        for index in range(1, 13)
    ]


def _demo_relaxation_trace(properties: dict[str, float]) -> list[dict[str, float]]:
    stability = properties["stability_score"]
    return [
        {
            "step": float(index),
            "energy_ev": round(-6.0 - stability * 2.4 - 0.55 * (1.0 - math.exp(-index / 2.0)), 6),
            "force_ev_a": round(0.38 * math.exp(-index / 2.6), 6),
        }
        for index in range(0, 9)
    ]


def _demo_band_trace(properties: dict[str, float]) -> list[dict[str, float]]:
    gap = properties["bandgap_proxy_ev"]
    trace = []
    for index in range(13):
        k_distance = index / 12.0
        curvature = (k_distance - 0.5) ** 2
        trace.append(
            {
                "k_distance": round(k_distance, 4),
                "valence_ev": round(-0.18 - 1.25 * curvature, 4),
                "conduction_ev": round(gap + 0.20 + 1.05 * curvature, 4),
            }
        )
    return trace


if __name__ == "__main__":
    main()
