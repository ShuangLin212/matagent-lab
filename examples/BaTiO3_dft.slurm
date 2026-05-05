#!/bin/bash
#SBATCH --job-name=dft-BaTiO3
#SBATCH --account=materials-ai
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=04:00:00
#SBATCH --output=runs/%x-%j.out
#SBATCH --error=runs/%x-%j.err

set -euo pipefail

module purge
module load python/3.11
module load quantum-espresso

export PYTHONPATH="${SLURM_SUBMIT_DIR}/src:${PYTHONPATH:-}"

echo 'Starting dft workflow for BaTiO3'
srun python workflows/run_dft.py --formula BaTiO3 --relax --bands
echo 'Workflow complete'
