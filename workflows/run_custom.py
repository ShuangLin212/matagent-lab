from __future__ import annotations

import argparse
import json
from pathlib import Path

from matagent_lab.chemistry import estimate_material_properties


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo custom workflow stub.")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    result = {
        "workflow": args.workflow,
        "formula": args.formula,
        "properties": estimate_material_properties(args.formula, "cross_domain"),
    }
    output_path = Path(args.out or f"runs/{_safe_name(args.formula)}_{args.workflow}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum())


if __name__ == "__main__":
    main()

