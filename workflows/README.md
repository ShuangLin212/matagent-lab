# Workflow Stubs

These scripts are local stand-ins for real HPC simulation entrypoints. They make the Slurm templates executable in a demo environment and show where production DFT, molecular dynamics, and Monte Carlo workflows would connect.

Production replacements might call:

- Quantum ESPRESSO, VASP, CP2K, or GPAW for DFT.
- LAMMPS, OpenMM, GROMACS, or ASE for molecular dynamics.
- Custom Monte Carlo samplers for configurational disorder, dopants, or alloy phase space.

