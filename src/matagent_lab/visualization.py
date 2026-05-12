from __future__ import annotations

import math
from html import escape
from pathlib import Path


PALETTE = {
    "ink": "#253238",
    "muted": "#63727a",
    "grid": "#d7e0df",
    "panel": "#f7faf9",
    "blue": "#2f6f9f",
    "green": "#4f8f6b",
    "gold": "#b8842f",
    "red": "#a94d45",
}


def write_dft_summary_svg(result: dict, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    properties = result.get("properties", {})
    scf_trace = result.get("scf_trace", [])
    relaxation_trace = result.get("relaxation_trace", [])
    band_trace = result.get("band_trace", [])

    bars = [
        ("bandgap eV", float(result.get("bandgap_proxy_ev", properties.get("bandgap_proxy_ev", 0.0))), 8.5),
        ("stability", float(result.get("stability_score", properties.get("stability_score", 0.0))), 1.0),
        ("optical", float(properties.get("optical_score", 0.0)), 1.0),
        ("domain", float(properties.get("domain_score", 0.0)), 1.0),
    ]

    svg = _svg_shell(
        960,
        600,
        [
            _title(40, 50, f"DFT setup and result preview: {result.get('formula', 'material')}"),
            _subtitle(
                40,
                76,
                f"Engine: {result.get('engine', 'unknown')} | Inputs: {result.get('input_dir', 'not written')}",
            ),
            _bar_chart(40, 110, 280, 360, "Screening descriptors", bars),
            _line_chart(
                360,
                110,
                260,
                160,
                "SCF residual",
                [(float(point["iteration"]), float(point["residual"])) for point in scf_trace],
                PALETTE["blue"],
                y_log=True,
            ),
            _line_chart(
                660,
                110,
                260,
                160,
                "Relaxation energy",
                [(float(point["step"]), float(point["energy_ev"])) for point in relaxation_trace],
                PALETTE["green"],
            ),
            _band_panel(360, 330, 560, 140, band_trace),
            _file_list_panel(360, 500, 560, 56, result.get("input_files", [])),
        ],
    )
    output_path.write_text(svg, encoding="utf-8")
    return output_path


def write_md_summary_svg(result: dict, path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    properties = result.get("properties", {})
    thermo_trace = result.get("thermo_trace", [])
    rdf_trace = result.get("rdf_trace", [])
    chemical_potentials = result.get("chemical_potentials", {})

    bars = [
        ("strain", float(result.get("strain_score", properties.get("strain_score", 0.0))), 1.0),
        ("process", float(result.get("processability_score", properties.get("processability_score", 0.0))), 1.0),
        ("stability", float(properties.get("stability_score", 0.0)), 1.0),
        ("domain", float(properties.get("domain_score", 0.0)), 1.0),
    ]

    svg = _svg_shell(
        960,
        600,
        [
            _title(40, 50, f"MD setup and result preview: {result.get('formula', 'material')}"),
            _subtitle(
                40,
                76,
                f"Engine: {result.get('engine', 'lammps')} | Potential: {result.get('potential', 'unknown')}",
            ),
            _bar_chart(40, 110, 280, 360, "MD descriptors", bars),
            _line_chart(
                360,
                110,
                260,
                160,
                "Temperature",
                [(float(point["step"]), float(point["temperature_k"])) for point in thermo_trace],
                PALETTE["red"],
            ),
            _line_chart(
                660,
                110,
                260,
                160,
                "Potential energy",
                [(float(point["step"]), float(point["potential_energy_ev"])) for point in thermo_trace],
                PALETTE["green"],
            ),
            _line_chart(
                360,
                330,
                260,
                140,
                "Pressure",
                [(float(point["step"]), float(point["pressure_bar"])) for point in thermo_trace],
                PALETTE["gold"],
            ),
            _line_chart(
                660,
                330,
                260,
                140,
                "Radial distribution",
                [(float(point["r_angstrom"]), float(point["g_r"])) for point in rdf_trace],
                PALETTE["blue"],
            ),
            _chemical_potential_panel(360, 500, 560, 56, chemical_potentials),
        ],
    )
    output_path.write_text(svg, encoding="utf-8")
    return output_path


def _svg_shell(width: int, height: int, children: list[str]) -> str:
    body = "\n".join(children)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <rect width="{width}" height="{height}" fill="#ffffff"/>
  <style>
    text {{ font-family: Inter, Arial, sans-serif; fill: {PALETTE["ink"]}; }}
    .muted {{ fill: {PALETTE["muted"]}; font-size: 12px; }}
    .axis {{ stroke: {PALETTE["grid"]}; stroke-width: 1; }}
    .panel {{ fill: {PALETTE["panel"]}; stroke: {PALETTE["grid"]}; }}
  </style>
{body}
</svg>
"""


def _title(x: int, y: int, text: str) -> str:
    return f'  <text x="{x}" y="{y}" font-size="24" font-weight="700">{escape(text)}</text>'


def _subtitle(x: int, y: int, text: str) -> str:
    return f'  <text class="muted" x="{x}" y="{y}">{escape(text)}</text>'


def _bar_chart(
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    bars: list[tuple[str, float, float]],
) -> str:
    inner_x = x + 22
    inner_y = y + 50
    bar_width = width - 44
    row_height = 66
    parts = [_panel(x, y, width, height), _panel_title(x + 20, y + 30, title)]
    for index, (label, value, maximum) in enumerate(bars):
        yy = inner_y + index * row_height
        fraction = _clamp(value / maximum if maximum else 0.0)
        color = [PALETTE["blue"], PALETTE["green"], PALETTE["gold"], PALETTE["red"]][index % 4]
        parts.extend(
            [
                f'  <text x="{inner_x}" y="{yy}" font-size="13" font-weight="600">{escape(label)}</text>',
                f'  <text x="{inner_x + bar_width}" y="{yy}" font-size="13" text-anchor="end">{value:.3g}</text>',
                f'  <rect x="{inner_x}" y="{yy + 14}" width="{bar_width}" height="18" fill="#e8efed" rx="4"/>',
                f'  <rect x="{inner_x}" y="{yy + 14}" width="{bar_width * fraction:.1f}" height="18" fill="{color}" rx="4"/>',
            ]
        )
    return "\n".join(parts)


def _line_chart(
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    points: list[tuple[float, float]],
    color: str,
    *,
    y_log: bool = False,
) -> str:
    parts = [_panel(x, y, width, height), _panel_title(x + 18, y + 28, title)]
    plot_x = x + 34
    plot_y = y + 42
    plot_w = width - 54
    plot_h = height - 66
    parts.extend(_grid(plot_x, plot_y, plot_w, plot_h))
    if not points:
        parts.append(f'  <text class="muted" x="{plot_x + 8}" y="{plot_y + 32}">No trace data</text>')
        return "\n".join(parts)

    values = [(px, _log_value(py) if y_log else py) for px, py in points]
    min_x, max_x = _extent(px for px, _ in values)
    min_y, max_y = _extent(py for _, py in values)
    coords = []
    for px, py in values:
        sx = plot_x + (px - min_x) / (max_x - min_x or 1.0) * plot_w
        sy = plot_y + plot_h - (py - min_y) / (max_y - min_y or 1.0) * plot_h
        coords.append(f"{sx:.1f},{sy:.1f}")
    parts.append(f'  <polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="3"/>')
    parts.append(f'  <text class="muted" x="{plot_x}" y="{plot_y + plot_h + 22}">{points[0][0]:.0f}</text>')
    parts.append(
        f'  <text class="muted" x="{plot_x + plot_w}" y="{plot_y + plot_h + 22}" text-anchor="end">{points[-1][0]:.0f}</text>'
    )
    return "\n".join(parts)


def _band_panel(x: int, y: int, width: int, height: int, band_trace: list[dict]) -> str:
    parts = [_panel(x, y, width, height), _panel_title(x + 18, y + 28, "Band path preview")]
    plot_x = x + 34
    plot_y = y + 42
    plot_w = width - 54
    plot_h = height - 66
    parts.extend(_grid(plot_x, plot_y, plot_w, plot_h))
    if not band_trace:
        parts.append(f'  <text class="muted" x="{plot_x + 8}" y="{plot_y + 32}">Enable --bands for a preview trace</text>')
        return "\n".join(parts)
    xs = [float(point["k_distance"]) for point in band_trace]
    min_x, max_x = _extent(xs)
    all_energies = [float(point[key]) for point in band_trace for key in ("valence_ev", "conduction_ev")]
    min_y, max_y = _extent(all_energies)
    for key, color in (("valence_ev", PALETTE["blue"]), ("conduction_ev", PALETTE["red"])):
        coords = []
        for point in band_trace:
            px = float(point["k_distance"])
            py = float(point[key])
            sx = plot_x + (px - min_x) / (max_x - min_x or 1.0) * plot_w
            sy = plot_y + plot_h - (py - min_y) / (max_y - min_y or 1.0) * plot_h
            coords.append(f"{sx:.1f},{sy:.1f}")
        parts.append(f'  <polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="3"/>')
    return "\n".join(parts)


def _file_list_panel(x: int, y: int, width: int, height: int, files: list[str]) -> str:
    shown = ", ".join(Path(file_name).name for file_name in files[:6]) or "No inputs written"
    if len(files) > 6:
        shown += ", ..."
    return "\n".join(
        [
            _panel(x, y, width, height),
            _panel_title(x + 18, y + 24, "Generated files"),
            f'  <text class="muted" x="{x + 18}" y="{y + 44}">{escape(shown)}</text>',
        ]
    )


def _chemical_potential_panel(x: int, y: int, width: int, height: int, potentials: dict[str, float]) -> str:
    if potentials:
        shown = ", ".join(f"mu_{element}={value:g}" for element, value in sorted(potentials.items()))
    else:
        shown = "No chemical-potential sweep variables selected"
    return "\n".join(
        [
            _panel(x, y, width, height),
            _panel_title(x + 18, y + 24, "Chemical potentials"),
            f'  <text class="muted" x="{x + 18}" y="{y + 44}">{escape(shown)}</text>',
        ]
    )


def _panel(x: int, y: int, width: int, height: int) -> str:
    return f'  <rect class="panel" x="{x}" y="{y}" width="{width}" height="{height}" rx="8"/>'


def _panel_title(x: int, y: int, text: str) -> str:
    return f'  <text x="{x}" y="{y}" font-size="15" font-weight="700">{escape(text)}</text>'


def _grid(x: int, y: int, width: int, height: int) -> list[str]:
    lines = []
    for index in range(4):
        yy = y + index * height / 3
        lines.append(f'  <line class="axis" x1="{x}" y1="{yy:.1f}" x2="{x + width}" y2="{yy:.1f}"/>')
    lines.append(f'  <line class="axis" x1="{x}" y1="{y}" x2="{x}" y2="{y + height}"/>')
    lines.append(f'  <line class="axis" x1="{x}" y1="{y + height}" x2="{x + width}" y2="{y + height}"/>')
    return lines


def _extent(values) -> tuple[float, float]:
    data = list(values)
    if not data:
        return 0.0, 1.0
    low = min(data)
    high = max(data)
    if low == high:
        return low - 0.5, high + 0.5
    padding = (high - low) * 0.08
    return low - padding, high + padding


def _log_value(value: float) -> float:
    value = max(value, 1e-14)
    return math.log10(value)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
