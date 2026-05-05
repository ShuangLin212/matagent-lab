from __future__ import annotations

import unittest

from matagent_lab.hpc import SlurmScriptBuilder, SlurmSpec


class HpcTest(unittest.TestCase):
    def test_build_dft_slurm_script(self) -> None:
        script = SlurmScriptBuilder().build(SlurmSpec(formula="BaTiO3", workflow="dft"))
        self.assertIn("#SBATCH --job-name=dft-BaTiO3", script)
        self.assertIn("quantum-espresso", script)
        self.assertIn("--formula BaTiO3", script)


if __name__ == "__main__":
    unittest.main()

