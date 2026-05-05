from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from matagent_lab.chemistry import estimate_material_properties


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo Monte Carlo workflow stub.")
    parser.add_argument("--formula", required=True)
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    properties = estimate_material_properties(args.formula, "cross_domain")
    samples = [properties["domain_score"] + rng.uniform(-0.04, 0.04) for _ in range(args.samples)]
    result = {
        "workflow": "monte_carlo",
        "formula": args.formula,
        "samples": args.samples,
        "mean_score": round(sum(samples) / len(samples), 4),
        "min_score": round(min(samples), 4),
        "max_score": round(max(samples), 4),
    }
    output_path = Path(args.out or f"runs/{_safe_name(args.formula)}_monte_carlo.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


def _safe_name(formula: str) -> str:
    return "".join(character for character in formula if character.isalnum())


if __name__ == "__main__":
    main()

