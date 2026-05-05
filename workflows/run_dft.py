from __future__ import annotations

import argparse
import json
from pathlib import Path

from matagent_lab.chemistry import estimate_material_properties


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo DFT workflow stub.")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--relax", action="store_true")
    parser.add_argument("--bands", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    properties = estimate_material_properties(args.formula, "cross_domain")
    result = {
        "workflow": "dft",
        "formula": args.formula,
        "relaxed": args.relax,
        "bands": args.bands,
        "bandgap_proxy_ev": properties["bandgap_proxy_ev"],
        "stability_score": properties["stability_score"],
    }
    output_path = Path(args.out or f"runs/{_safe_name(args.formula)}_dft.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum())


if __name__ == "__main__":
    main()

