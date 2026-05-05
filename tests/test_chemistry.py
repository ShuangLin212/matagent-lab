from __future__ import annotations

import unittest

from matagent_lab.chemistry import estimate_material_properties, molecular_weight, parse_formula


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


if __name__ == "__main__":
    unittest.main()

