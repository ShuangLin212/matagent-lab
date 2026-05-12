from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from matagent_lab.chemistry import estimate_material_properties
from matagent_lab.simulation_io import parse_chemical_potentials, write_lammps_inputs
from matagent_lab.visualization import write_md_summary_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare LAMMPS MD inputs and write a visual result preview.")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--engine", choices=["lammps"], default="lammps")
    parser.add_argument("--temperature", type=float, default=300.0)
    parser.add_argument("--steps", type=int, default=50000)
    parser.add_argument("--potential", choices=["reaxff", "lj", "eam", "tersoff"], default="reaxff")
    parser.add_argument("--potential-file", default="ffield.reax")
    parser.add_argument(
        "--chemical-potential",
        action="append",
        default=[],
        help="Chemical potential variable as Element=value, repeat for sweeps.",
    )
    parser.add_argument("--prototype", choices=["auto", "perovskite", "cubic"], default="auto")
    parser.add_argument("--input-dir", default=None)
    parser.add_argument("--plot", default=None, help="Optional SVG plot path. Use --no-plot to skip.")
    parser.add_argument("--no-plot", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    properties = estimate_material_properties(args.formula, "cross_domain")
    chemical_potentials = parse_chemical_potentials(args.chemical_potential)
    input_root = Path(args.input_dir or f"runs/{_safe_name(args.formula)}_md_inputs")
    input_set = write_lammps_inputs(
        args.formula,
        input_root,
        prototype=args.prototype,
        potential=args.potential,
        potential_file=args.potential_file,
        temperature=args.temperature,
        steps=args.steps,
        chemical_potentials=chemical_potentials,
    )
    result = {
        "workflow": "md",
        "formula": args.formula,
        "engine": args.engine,
        "temperature": args.temperature,
        "steps": args.steps,
        "potential": args.potential,
        "potential_file": args.potential_file,
        "chemical_potentials": chemical_potentials,
        "input_dir": str(input_root),
        "input_files": [str(path) for path in input_set.files],
        "input_metadata": input_set.metadata,
        "properties": properties,
        "strain_score": properties["strain_score"],
        "processability_score": properties["processability_score"],
        "thermo_trace": _demo_thermo_trace(properties, args.temperature, args.steps),
        "rdf_trace": _demo_rdf_trace(properties),
    }
    if not args.no_plot:
        plot_path = Path(args.plot or f"runs/{_safe_name(args.formula)}_md.svg")
        write_md_summary_svg(result, plot_path)
        result["plot_svg"] = str(plot_path)
    output_path = Path(args.out or f"runs/{_safe_name(args.formula)}_md.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    if result.get("plot_svg"):
        print(f"Wrote {result['plot_svg']}")


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum())


def _demo_thermo_trace(
    properties: dict[str, float],
    temperature: float,
    steps: int,
) -> list[dict[str, float]]:
    stability = properties["stability_score"]
    strain = properties["strain_score"]
    interval = max(1, steps // 10)
    trace = []
    for index in range(11):
        step = index * interval
        damping = math.exp(-index / 3.2)
        oscillation = math.sin(index * 0.9)
        trace.append(
            {
                "step": float(step),
                "temperature_k": round(temperature + (18.0 * damping * oscillation), 3),
                "potential_energy_ev": round(-2.5 - 4.2 * stability - 0.22 * index + 0.08 * oscillation, 5),
                "pressure_bar": round((1.0 - stability) * 900.0 * damping * math.cos(index * 0.7), 3),
                "volume_a3": round(120.0 * (1.0 + 0.04 * strain * (1.0 - damping)), 4),
            }
        )
    return trace


def _demo_rdf_trace(properties: dict[str, float]) -> list[dict[str, float]]:
    density = properties["density_proxy"]
    trace = []
    for index in range(1, 40):
        radius = 0.15 * index
        first_shell = math.exp(-((radius - 1.9) ** 2) / 0.10)
        second_shell = 0.62 * math.exp(-((radius - 3.3) ** 2) / 0.22)
        baseline = 0.18 + 0.35 * (1.0 - math.exp(-radius / 2.0))
        trace.append(
            {
                "r_angstrom": round(radius, 3),
                "g_r": round(baseline + (1.0 + density) * first_shell + second_shell, 4),
            }
        )
    return trace


if __name__ == "__main__":
    main()
