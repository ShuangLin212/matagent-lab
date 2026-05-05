from __future__ import annotations

import unittest
from pathlib import Path

from matagent_lab import DiscoveryOrchestrator, RunConfig


class OrchestratorTest(unittest.TestCase):
    def test_ar_glasses_report_contains_ranked_results(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config = RunConfig.from_json(repo_root / "configs" / "ar_glasses.json")
        report = DiscoveryOrchestrator(config).run()
        self.assertGreaterEqual(len(report.ranked_results), 4)
        self.assertGreater(report.metrics["retrieval_coverage"], 0.0)
        self.assertGreaterEqual(report.ranked_results[0].total_score, report.ranked_results[-1].total_score)


if __name__ == "__main__":
    unittest.main()

