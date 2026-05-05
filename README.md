# MatAgent Lab

[![CI](https://github.com/ShuangLin212/matagent-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/ShuangLin212/matagent-lab/actions/workflows/ci.yml)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-28566a)
![License MIT](https://img.shields.io/badge/license-MIT-417b5a)
![Domain Materials AI](https://img.shields.io/badge/domain-materials%20AI-9b6a17)

MatAgent Lab is a research-oriented prototype for **agentic AI in materials and chemistry discovery**. It coordinates scientific retrieval, candidate generation, formula-level screening, synthesis critique, ranking, benchmarking, and HPC job preparation in one auditable loop.

The default implementation runs locally with pure Python and no API keys. The interfaces are intentionally designed so real LLM agents, vector search, DFT/MD/Monte Carlo engines, active learning, knowledge graphs, or lab automation APIs can replace the deterministic demo agents.

![Closed-loop agentic materials discovery architecture](docs/figures/closed_loop_architecture.svg)

## Why It Matters

Materials discovery is not only a prediction problem. Useful candidates must satisfy evidence, physics, synthesis feasibility, device constraints, safety, resource risk, and follow-up compute cost. MatAgent Lab demonstrates a closed-loop architecture for that workflow, targeting two hardware-relevant domains:

- transparent, lightweight materials for AR glasses
- sensing and actuating materials for robotics

The current scoring functions are transparent heuristics, not validated physical models. That is deliberate: the project makes the system design inspectable while leaving clear hooks for production scientific backends.

## What It Does

- Retrieves scientific context from a local BM25-style RAG index.
- Generates candidate materials for AR-glasses and robotics tasks.
- Parses chemical formulas, including fractional stoichiometries such as `Pb(Zr0.52Ti0.48)O3`.
- Screens optical, electromechanical, density, toxicity, resource-risk, processability, and compute-cost signals.
- Scores synthesis viability, route complexity, and practical risk flags.
- Ranks candidates against domain constraints with auditable agent traces.
- Emits JSON reports, benchmark metrics, and Slurm templates for DFT, MD, or Monte Carlo follow-up.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

matagent-lab discover --config configs/ar_glasses.json --out runs/ar_glasses_report.json
matagent-lab benchmark --config configs/robotics_actuator.json --out runs/robotics_benchmark.json
matagent-lab slurm --formula BaTiO3 --workflow dft --out runs/BaTiO3_dft.slurm
```

Without installing:

```bash
PYTHONPATH=src python -m matagent_lab discover --config configs/ar_glasses.json
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Outputs

Discovery reports include:

- `ranked_results`: candidates, scores, constraint status, risks, routes, and next experiments
- `metrics`: throughput, pass rate, retrieval coverage, viability, Pareto-front size, formula diversity, constraint satisfaction, and top score
- `agent_traces`: retrieved evidence IDs, generated formulas, screening scores, and ranking artifacts

Committed examples:

- [AR glasses report](examples/sample_ar_glasses_report.json)
- [Robotics benchmark](examples/sample_robotics_benchmark.json)
- [BaTiO3 Slurm template](examples/BaTiO3_dft.slurm)
- [Candidate ranking figure](docs/figures/ar_candidate_ranking.svg)
- [Benchmark dashboard figure](docs/figures/benchmark_dashboard.svg)

## Architecture

```text
Task Config
  -> Literature Agent
  -> Candidate Agent
  -> Simulation Agent
  -> Synthesis Agent
  -> Critic Agent
  -> Ranked Report + HPC Templates
```

Core modules:

```text
src/matagent_lab/
  agents.py          agent roles
  chemistry.py       formula parsing and screening features
  rag.py             local scientific retrieval
  orchestrator.py    end-to-end workflow
  benchmark.py       repeated-run evaluation
  hpc.py             Slurm generation
  cli.py             command-line interface
```

## Research Notes

- [Manuscript draft](docs/MANUSCRIPT.md)
- [Research positioning](docs/RESEARCH_POSITIONING.md)
- [System design](docs/SYSTEM_DESIGN.md)
- [Portfolio notes](docs/PORTFOLIO_NOTES.md)

## Roadmap

- Replace demo heuristics with calibrated surrogate models and physics-based DFT/MD/Monte Carlo backends.
- Add crystal-structure and molecular-geometry generation.
- Integrate dense retrieval over papers, patents, and lab notebooks.
- Add active learning to select the next highest-value simulation or experiment.
- Parse completed HPC or lab results back into the discovery loop.
