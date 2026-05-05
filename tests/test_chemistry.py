from __future__ import annotations

import unittest

from matagent_lab.chemistry import estimate_material_properties, molecular_weight, parse_formula
from matagent_lab.insights import infer_chemistry_insight
from matagent_lab.models import MaterialCandidate


class ChemistryTest(unittest.TestCase):
    def test_parse_fractional_perovskite(self) -> None:
        counts = parse_formula("Pb(Zr0.52Ti0.48)O3")
        self.assertAlmostEqual(counts["Pb"], 1.0)
        self.assertAlmostEqual(counts["Zr"], 0.52)
        self.assertAlmostEqual(counts["Ti"], 0.48)
        self.assertAlmostEqual(counts["O"], 3.0)

    def test_molecular_weight(self) -> None:
        self.assertGreater(molecular_weight("BaTiO3"), 230.0)

    def test_estimate_ar_properties(self) -> None:
        properties = estimate_material_properties("MgAl2O4", "ar_glasses")
        self.assertIn("optical_score", properties)
        self.assertGreater(properties["stability_score"], 0.5)

    def test_perovskite_descriptors(self) -> None:
        properties = estimate_material_properties("K0.5Na0.5NbO3", "robotics_actuator")
        self.assertGreater(properties["perovskite_tolerance_factor"], 0.0)
        self.assertGreater(properties["perovskite_stability_score"], 0.0)

    def test_chemistry_insight_for_pzt(self) -> None:
        candidate = MaterialCandidate(
            id="test",
            formula="Pb(Zr0.52Ti0.48)O3",
            name="PZT",
            domain="robotics_actuator",
            rationale="reference",
            evidence_ids=["lit-005"],
        )
        insight = infer_chemistry_insight(
            candidate,
            estimate_material_properties(candidate.formula, candidate.domain),
            candidate.domain,
        )
        self.assertEqual(insight.material_family, "oxide perovskite")
        self.assertIn("perovskite", insight.structure_motif)

    def test_sesquioxide_is_not_perovskite(self) -> None:
        candidate = MaterialCandidate(
            id="test",
            formula="Al2O3",
            name="alumina",
            domain="ar_glasses",
            rationale="barrier",
            evidence_ids=["lit-002"],
        )
        insight = infer_chemistry_insight(
            candidate,
            estimate_material_properties(candidate.formula, candidate.domain),
            candidate.domain,
        )
        self.assertEqual(insight.material_family, "functional oxide")
        self.assertNotIn("perovskite", insight.structure_motif)


if __name__ == "__main__":
    unittest.main()
