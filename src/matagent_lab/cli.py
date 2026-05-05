from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import BenchmarkRunner
from .hpc import SlurmScriptBuilder, SlurmSpec
from .orchestrator import DiscoveryOrchestrator, RunConfig


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="matagent-lab",
        description="Agentic AI materials-discovery demo pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover", help="Run the multi-agent discovery pipeline.")
    discover.add_argument("--config", required=True, help="Path to discovery config JSON.")
    discover.add_argument("--out", help="Optional output JSON path.")

    benchmark = subparsers.add_parser("benchmark", help="Benchmark repeated discovery runs.")
    benchmark.add_argument("--config", required=True, help="Path to discovery config JSON.")
    benchmark.add_argument("--repeats", type=int, default=3, help="Number of repeats.")
    benchmark.add_argument("--out", help="Optional output JSON path.")

    slurm = subparsers.add_parser("slurm", help="Generate a Slurm script for a candidate workflow.")
    slurm.add_argument("--formula", required=True, help="Chemical formula, for example BaTiO3.")
    slurm.add_argument(
        "--workflow",
        choices=["dft", "md", "monte_carlo", "custom"],
        default="dft",
        help="Simulation workflow family.",
    )
    slurm.add_argument("--account", default="materials-ai")
    slurm.add_argument("--partition", default="batch")
    slurm.add_argument("--hours", type=int, default=4)
    slurm.add_argument("--nodes", type=int, default=1)
    slurm.add_argument("--ntasks", type=int, default=16)
    slurm.add_argument("--out", help="Optional output Slurm path.")

    args = parser.parse_args(argv)
    if args.command == "discover":
        payload = DiscoveryOrchestrator(RunConfig.from_json(args.config)).run().to_dict()
        _write_or_print_json(payload, args.out)
    elif args.command == "benchmark":
        payload = BenchmarkRunner(RunConfig.from_json(args.config), repeats=args.repeats).run()
        _write_or_print_json(payload, args.out)
    elif args.command == "slurm":
        script = SlurmScriptBuilder().build(
            SlurmSpec(
                formula=args.formula,
                workflow=args.workflow,
                account=args.account,
                partition=args.partition,
                hours=args.hours,
                nodes=args.nodes,
                ntasks=args.ntasks,
            )
        )
        _write_or_print_text(script, args.out)


def _write_or_print_json(payload: dict, out: str | None) -> None:
    encoded = json.dumps(payload, indent=2)
    if out:
        output_path = Path(out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(encoded + "\n", encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(encoded)


def _write_or_print_text(payload: str, out: str | None) -> None:
    if out:
        output_path = Path(out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(payload)


if __name__ == "__main__":
    main()

