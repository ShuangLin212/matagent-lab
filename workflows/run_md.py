from __future__ import annotations

import argparse
import json
from pathlib import Path

from matagent_lab.chemistry import estimate_material_properties


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo molecular dynamics workflow stub.")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--temperature", type=float, default=300.0)
    parser.add_argument("--steps", type=int, default=50000)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    properties = estimate_material_properties(args.formula, "cross_domain")
    result = {
        "workflow": "md",
        "formula": args.formula,
        "temperature": args.temperature,
        "steps": args.steps,
        "strain_score": properties["strain_score"],
        "processability_score": properties["processability_score"],
    }
    output_path = Path(args.out or f"runs/{_safe_name(args.formula)}_md.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum())


if __name__ == "__main__":
    main()

