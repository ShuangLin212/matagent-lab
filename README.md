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
- Screens optical, electromechanical, perovskite-tolerance, density, toxicity, resource-risk, processability, and compute-cost signals.
- Infers chemistry families, structural motifs, bonding character, likely mechanisms, and validation priorities.
- Adds literature-informed design traces from Coscientist, ChemCrow, A-Lab, GNoME, SciAgents, and chemistry-agent reviews.
- Scores synthesis viability, route complexity, and practical risk flags.
- Ranks candidates against domain constraints with auditable agent traces.
- Emits JSON reports, benchmark metrics, and Slurm templates for DFT, MD, or Monte Carlo follow-up.
- Prepares prototype DFT input decks for Quantum ESPRESSO and VASP, plus LAMMPS MD decks with ReaxFF, LJ, EAM, or Tersoff settings.
- Writes automated SVG result previews for DFT and MD setup, screening descriptors, convergence traces, energy traces, and MD structural summaries.

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

## Try Demo

Run the full loop without installing the package:

```bash
PYTHONPATH=src python -m matagent_lab discover \
  --config configs/ar_glasses.json \
  --out runs/demo_ar_glasses_report.json
```

Then inspect the top candidate and metrics:

```bash
python -m json.tool runs/demo_ar_glasses_report.json
```

What to look for:

- top-ranked transparent materials such as `MgAl2O4` and `ZrO2`
- constraint pass/fail status for each candidate
- chemistry families, structural motifs, and mechanism hypotheses
- synthesis routes, toxicity or supply-risk flags, and next experiments
- metrics such as retrieval coverage, Pareto-front size, formula diversity, and constraint satisfaction

Generate an HPC-ready follow-up job:

```bash
PYTHONPATH=src python -m matagent_lab slurm \
  --formula BaTiO3 \
  --workflow dft \
  --out runs/demo_BaTiO3_dft.slurm
```

Prepare local DFT inputs and a visual preview:

```bash
PYTHONPATH=src python workflows/run_dft.py \
  --formula BaTiO3 \
  --engine both \
  --relax \
  --bands
```

This writes Quantum ESPRESSO and VASP input decks under `runs/BaTiO3_dft_inputs/`,
a JSON result file, and an SVG summary at `runs/BaTiO3_dft.svg`.

Prepare a LAMMPS/ReaxFF MD input deck with chemical-potential sweep variables:

```bash
PYTHONPATH=src python workflows/run_md.py \
  --formula BaTiO3 \
  --potential reaxff \
  --chemical-potential O=-4.5 \
  --chemical-potential Ti=-7.1
```

## Outputs

Discovery reports include:

- `ranked_results`: candidates, scores, constraint status, risks, routes, and next experiments
- `metrics`: throughput, pass rate, retrieval coverage, viability, Pareto-front size, formula diversity, constraint satisfaction, and top score
- `chemistry`: material family, structural motif, bonding character, mechanisms, tradeoffs, and validation priorities
- `agent_traces`: retrieved evidence IDs, generated formulas, mechanism summaries, literature-derived design principles, screening scores, and ranking artifacts

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
  -> Mechanism Agent
  -> Synthesis Agent
  -> Critic Agent
  -> Research Context Agent
  -> Ranked Report + HPC Templates
```

Core modules:

```text
src/matagent_lab/
  agents.py          agent roles
  chemistry.py       formula parsing and screening features
  insights.py        chemistry family, motif, and mechanism inference
  rag.py             local scientific retrieval
  orchestrator.py    end-to-end workflow
  benchmark.py       repeated-run evaluation
  hpc.py             Slurm generation
  cli.py             command-line interface
```

## Research Notes

- [Research positioning](docs/RESEARCH_POSITIONING.md)
- [System design](docs/SYSTEM_DESIGN.md)
- [Portfolio notes](docs/PORTFOLIO_NOTES.md)

## Roadmap

- Replace demo heuristics with calibrated surrogate models and physics-based DFT/MD/Monte Carlo backends.
- Add crystal-structure and molecular-geometry generation.
- Integrate dense retrieval over papers, patents, and lab notebooks.
- Add active learning to select the next highest-value simulation or experiment.
- Parse completed HPC or lab results back into the discovery loop.
