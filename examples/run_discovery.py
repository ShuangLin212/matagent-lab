from __future__ import annotations

import json
from pathlib import Path

from matagent_lab import DiscoveryOrchestrator, RunConfig


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = RunConfig.from_json(repo_root / "configs" / "ar_glasses.json")
    report = DiscoveryOrchestrator(config).run()
    print(json.dumps(report.to_dict()["ranked_results"][:2], indent=2))


if __name__ == "__main__":
    main()

