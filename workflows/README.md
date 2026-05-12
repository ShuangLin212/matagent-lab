# Workflow Scripts

These scripts make the Slurm templates executable in a demo environment and show where production DFT, molecular dynamics, and Monte Carlo workflows connect.

`run_dft.py` prepares Quantum ESPRESSO and/or VASP input decks from a formula using deterministic prototype structures. Simple `ABO3` perovskites become cubic perovskite cells; other formulas use a bounded cubic packing that preserves stoichiometry as closely as practical. The workflow also writes JSON output and an SVG preview with screening descriptors, SCF convergence, relaxation energy, and band-path traces.

```bash
PYTHONPATH=src python workflows/run_dft.py \
  --formula BaTiO3 \
  --engine both \
  --relax \
  --bands
```

`run_md.py` prepares LAMMPS inputs, including ReaxFF, LJ, EAM, or Tersoff pair-style scaffolds. ReaxFF decks automatically replicate very small prototype cells before dynamics. Chemical-potential choices can be exposed as LAMMPS variables for reactive, GCMC, or custom sensitivity-sweep extensions.

```bash
PYTHONPATH=src python workflows/run_md.py \
  --formula BaTiO3 \
  --potential reaxff \
  --chemical-potential O=-4.5 \
  --chemical-potential Ti=-7.1
```

Production replacements can call:

- Quantum ESPRESSO, VASP, CP2K, or GPAW for DFT.
- LAMMPS, OpenMM, GROMACS, or ASE for molecular dynamics.
- Custom Monte Carlo samplers for configurational disorder, dopants, or alloy phase space.
