from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from matagent_lab.simulation_io import (
    build_structure,
    parse_chemical_potentials,
    write_lammps_inputs,
    write_quantum_espresso_inputs,
    write_vasp_inputs,
)


class SimulationIoTest(unittest.TestCase):
    def test_builds_simple_perovskite_structure(self) -> None:
        structure = build_structure("BaTiO3")
        self.assertEqual(structure.prototype, "cubic_perovskite")
        self.assertEqual(structure.natoms, 5)
        self.assertEqual(structure.integer_counts["O"], 3)

    def test_writes_vasp_and_qe_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            vasp = write_vasp_inputs("BaTiO3", root / "vasp", relax=True, bands=True)
            qe = write_quantum_espresso_inputs("BaTiO3", root / "qe", relax=True)

            self.assertTrue((root / "vasp" / "POSCAR").exists())
            self.assertTrue((root / "vasp" / "INCAR").read_text(encoding="utf-8").startswith("SYSTEM = BaTiO3"))
            self.assertIn("pw.in", [path.name for path in qe.files])
            self.assertIn("ATOMIC_POSITIONS crystal", (root / "qe" / "pw.in").read_text(encoding="utf-8"))
            self.assertEqual(vasp.metadata["prototype"], "cubic_perovskite")

    def test_writes_lammps_reaxff_inputs_with_mu_variables(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            potentials = parse_chemical_potentials(["O=-4.5", "Ti=-7.1"])
            prepared = write_lammps_inputs(
                "BaTiO3",
                temporary,
                potential="reaxff",
                chemical_potentials=potentials,
            )

            script = Path(temporary, "in.lammps").read_text(encoding="utf-8")
            self.assertIn("pair_style reaxff", script)
            self.assertIn("replicate 3 3 3", script)
            self.assertIn("variable mu_O equal -4.5", script)
            self.assertIn("structure.data", [path.name for path in prepared.files])


if __name__ == "__main__":
    unittest.main()
