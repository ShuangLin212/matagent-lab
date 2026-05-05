from __future__ import annotations

import unittest
from pathlib import Path

from matagent_lab.benchmark import BenchmarkRunner
from matagent_lab.orchestrator import RunConfig


class BenchmarkTest(unittest.TestCase):
    def test_benchmark_reports_multi_objective_metrics(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config = RunConfig.from_json(repo_root / "configs" / "robotics_actuator.json")
        payload = BenchmarkRunner(config, repeats=2).run()
        self.assertGreaterEqual(payload["mean_pareto_front_size"], 1.0)
        self.assertGreater(payload["mean_formula_diversity"], 0.0)
        self.assertGreater(payload["mean_constraint_satisfaction_score"], 0.0)


if __name__ == "__main__":
    unittest.main()

