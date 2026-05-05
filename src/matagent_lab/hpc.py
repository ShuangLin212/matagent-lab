from __future__ import annotations

import re
import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class SlurmSpec:
    formula: str
    workflow: str
    account: str = "materials-ai"
    partition: str = "batch"
    hours: int = 4
    nodes: int = 1
    ntasks: int = 16


class SlurmScriptBuilder:
    """Creates scheduler-ready templates without submitting jobs."""

    def build(self, spec: SlurmSpec) -> str:
        job_name = self._job_name(spec.formula, spec.workflow)
        command = self._workflow_command(spec)
        return "\n".join(
            [
                "#!/bin/bash",
                f"#SBATCH --job-name={job_name}",
                f"#SBATCH --account={spec.account}",
                f"#SBATCH --partition={spec.partition}",
                f"#SBATCH --nodes={spec.nodes}",
                f"#SBATCH --ntasks={spec.ntasks}",
                f"#SBATCH --time={spec.hours:02d}:00:00",
                "#SBATCH --output=runs/%x-%j.out",
                "#SBATCH --error=runs/%x-%j.err",
                "",
                "set -euo pipefail",
                "",
                "module purge",
                "module load python/3.11",
                self._module_line(spec.workflow),
                "",
                "export PYTHONPATH=\"${SLURM_SUBMIT_DIR}/src:${PYTHONPATH:-}\"",
                "",
                f"echo 'Starting {spec.workflow} workflow for {spec.formula}'",
                command,
                "echo 'Workflow complete'",
                "",
            ]
        )

    def _job_name(self, formula: str, workflow: str) -> str:
        compact_formula = re.sub(r"[^A-Za-z0-9]+", "", formula)
        return f"{workflow}-{compact_formula}"[:48]

    def _module_line(self, workflow: str) -> str:
        if workflow == "dft":
            return "module load quantum-espresso"
        if workflow == "md":
            return "module load lammps"
        if workflow == "monte_carlo":
            return "module load python/3.11"
        return "# Add workflow-specific modules here"

    def _workflow_command(self, spec: SlurmSpec) -> str:
        formula = shlex.quote(spec.formula)
        if spec.workflow == "dft":
            return f"srun python workflows/run_dft.py --formula {formula} --relax --bands"
        if spec.workflow == "md":
            return f"srun python workflows/run_md.py --formula {formula} --temperature 300 --steps 50000"
        if spec.workflow == "monte_carlo":
            return f"srun python workflows/run_monte_carlo.py --formula {formula} --samples 2000"
        return f"srun python workflows/run_custom.py --formula {formula} --workflow {shlex.quote(spec.workflow)}"
