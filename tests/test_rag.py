from __future__ import annotations

import unittest

from matagent_lab.models import Document
from matagent_lab.rag import ScientificRetrievalIndex


class RetrievalTest(unittest.TestCase):
    def test_search_ranks_domain_document(self) -> None:
        index = ScientificRetrievalIndex(
            [
                Document(
                    id="a",
                    title="Transparent oxide conductors",
                    abstract="zinc oxide and tin oxide support wearable transparent electrodes",
                    tags=["transparent_conductor", "oxide"],
                    materials=["ZnO", "SnO2"],
                    domain="ar_glasses",
                ),
                Document(
                    id="b",
                    title="Soft robotic polymers",
                    abstract="silicone elastomer for stretchable actuators",
                    tags=["soft_robotics"],
                    materials=["C2H6OSi"],
                    domain="robotics_actuator",
                ),
            ]
        )
        results = index.search("transparent oxide wearable", domain="ar_glasses")
        self.assertEqual(results[0].document.id, "a")
        self.assertGreater(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()

