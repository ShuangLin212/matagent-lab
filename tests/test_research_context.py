from __future__ import annotations

import unittest

from matagent_lab.models import TaskSpec
from matagent_lab.research_context import TOP_LITERATURE, build_research_context_trace


class ResearchContextTest(unittest.TestCase):
    def test_research_context_contains_key_literature(self) -> None:
        task = TaskSpec(
            name="test",
            domain="robotics_actuator",
            objective="screen actuator materials",
            constraints={},
        )
        trace = build_research_context_trace(task)
        keys = {paper["key"] for paper in TOP_LITERATURE}
        self.assertIn("Coscientist", keys)
        self.assertIn("ChemCrow", keys)
        self.assertIn("A-Lab", keys)
        self.assertEqual(trace.agent, "ResearchContextAgent")
        self.assertTrue(trace.artifacts["domain_hooks"])


if __name__ == "__main__":
    unittest.main()

