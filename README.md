# MatAgent Lab

MatAgent Lab is a runnable portfolio project for AI-driven materials and chemistry discovery. It demonstrates an LLM-style multi-agent workflow that retrieves scientific context, proposes candidates, estimates material properties, checks synthesis viability, ranks candidates, and emits HPC job templates for deeper simulation.

The project is intentionally lightweight: the default demo runs locally with pure Python and no API keys. The architecture is designed so real LLM calls, DFT/MD engines, or lab automation APIs can replace the deterministic demo agents later.

## Project Pitch

MatAgent Lab demonstrates how agentic AI can compress early materials discovery by coordinating literature retrieval, candidate generation, computational screening, synthesis-aware critique, and HPC job preparation in one auditable loop. The demo focuses on two hardware-relevant domains: transparent, lightweight materials for AR glasses and sensing or actuating materials for robotics.

This is not just a chatbot wrapper. It is a systems prototype for scientific decision-making: each agent produces structured artifacts, every candidate is scored against physical and practical constraints, and the final report explains the evidence, risks, next experiments, and compute path for follow-up validation.

## Why This Project Exists

Materials discovery teams increasingly need AI systems that can close the loop between literature, computational screening, synthesis planning, and experimental feedback. This repository shows that shape end to end:

- Multi-agent orchestration for materials discovery tasks.
- Retrieval-augmented generation over a small scientific-note corpus.
- Candidate generation for AR glasses, transparent conductors, dielectric coatings, robotics actuators, and sensing materials.
- Screening heuristics for optical transparency, piezoelectric response, density, toxicity, resource risk, and simulation cost.
- Synthetic viability scoring with route suggestions and risk flags.
- HPC-oriented Slurm job generation for DFT, molecular dynamics, and Monte Carlo workflows.
- Benchmarks for throughput, pass rate, score quality, and retrieval coverage.

## How It Works

1. A task config defines the scientific objective, domain, constraints, seed formulas, retrieval budget, and candidate budget.
2. The literature agent retrieves relevant scientific notes using a small BM25-style RAG index.
3. The candidate agent proposes materials and attaches retrieved evidence to each candidate.
4. The simulation agent parses each chemical formula and estimates transparent, auditable screening features.
5. The synthesis agent estimates process route, viability, step count, toxicity, and supply-chain risks.
6. The critic agent ranks candidates by domain score, synthesis viability, constraint satisfaction, and evidence coverage.
7. The CLI writes a structured discovery report, benchmark metrics, or Slurm script for deeper DFT, MD, or Monte Carlo validation.

## Scientific Impact

The scientific value is the closed-loop design pattern. Materials teams often lose time moving manually between papers, candidate lists, simulations, synthesis feasibility checks, and HPC job setup. MatAgent Lab shows how those steps can become one reproducible workflow with explicit handoffs and measurable outcomes.

For AR glasses, the workflow prioritizes optical transparency, low density, environmental stability, toxicity, and scarce-element risk. For robotics, it balances piezoelectric response, strain potential, processability, fatigue-relevant follow-up experiments, and safe synthesis. That makes the system relevant to real hardware discovery problems where the best material is not just high-performing, but manufacturable, safe, and compatible with device constraints.

The default models are transparent heuristics, not validated physics. That is intentional for a portfolio repository: reviewers can inspect the logic, run the tests, and see exactly where production integrations would connect to DFT, molecular dynamics, Monte Carlo, active learning, or laboratory automation.

## Architecture

```mermaid
flowchart LR
    A[Task Config] --> B[Literature Agent]
    B --> C[RAG Index]
    B --> D[Candidate Agent]
    D --> E[Simulation Agent]
    E --> F[Synthesis Agent]
    F --> G[Critic Agent]
    G --> H[Ranked Discovery Report]
    H --> I[HPC Slurm Templates]
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
matagent-lab discover --config configs/ar_glasses.json --out runs/ar_glasses_report.json
matagent-lab benchmark --config configs/robotics_actuator.json --out runs/robotics_benchmark.json
matagent-lab slurm --formula BaTiO3 --workflow dft --out runs/BaTiO3_dft.slurm
```

Without installing the package:

```bash
PYTHONPATH=src python -m matagent_lab discover --config configs/ar_glasses.json
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Example Output

The discovery command writes a JSON report with:

- `ranked_results`: screened candidates with scores, risks, routes, and next experiments.
- `metrics`: candidate throughput, pass rate, retrieval coverage, and top score.
- `agent_traces`: auditable steps from each agent.

Committed examples:

- `examples/sample_ar_glasses_report.json`
- `examples/sample_robotics_benchmark.json`
- `examples/BaTiO3_dft.slurm`

## Repository Structure

```text
src/matagent_lab/
  agents.py          Multi-agent discovery roles
  benchmark.py       Evaluation harness and metrics
  chemistry.py       Formula parsing and chemistry features
  cli.py             Command-line interface
  hpc.py             Slurm job template generation
  models.py          Typed dataclasses
  orchestrator.py    End-to-end workflow runner
  rag.py             Local scientific retrieval index
configs/             Discovery task configurations
data/                Demo literature corpus
docs/                System design and portfolio notes
tests/               Standard-library unit tests
workflows/           Demo DFT, MD, and Monte Carlo entrypoints
```

## Good Next Extensions

- Replace deterministic candidate generation with tool-calling LLM agents.
- Connect the simulation agent to ASE, VASP, Quantum ESPRESSO, LAMMPS, or OpenMM.
- Add a real literature ingestion pipeline from papers, patents, and internal notes.
- Store candidate-property-evidence triples in a graph database.
- Add active learning to choose the next DFT or synthesis experiment.
- Connect generated Slurm scripts to an HPC scheduler and parse completed results back into the loop.

## Caveat

This repository is a demonstration scaffold. The default screening functions are transparent heuristics, not validated physical models. They are meant to show system design, orchestration, software quality, and extension points for production scientific AI systems.
