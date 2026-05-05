# Portfolio Notes

Use this project to discuss agentic AI for materials discovery in interviews.

## Resume Bullet Options

- Built MatAgent Lab, a Python multi-agent materials discovery system that combines scientific RAG, candidate generation, chemistry-aware screening, synthesis-viability critique, benchmark metrics, and Slurm-based HPC workflow preparation.
- Implemented transparent formula parsing and multi-objective ranking for AR-glasses and robotics materials, including optical, electromechanical, toxicity, density, resource-risk, processability, and compute-cost signals.
- Designed production extension points for LLM tool-use agents, vector search, knowledge graphs, DFT/MD/Monte Carlo simulation backends, HPC orchestration, active learning, and closed-loop experimental feedback.

## Interview Talk Track

The project mirrors a closed-loop discovery workflow. A literature agent retrieves context, a candidate agent proposes materials, a simulation agent estimates screening properties, a synthesis agent filters for practical routes, and a critic ranks candidates against domain constraints. The default implementation is local and deterministic so it can run in CI, but the module boundaries are ready for LLMs, vector search, HPC jobs, physics-based simulation, active learning, and lab feedback.

## Short Introduction

MatAgent Lab is an end-to-end agentic AI prototype for materials and chemistry discovery. It shows how a multi-agent system can move from scientific literature to candidate materials, screening scores, synthesis critique, benchmark metrics, and HPC-ready simulation scripts. The project targets materials for AR glasses and robotics, which makes it directly relevant to hardware teams that need faster discovery loops for optical, sensing, and actuating materials.

## Scientific Impact Summary

The impact is not a single predicted material; it is a reproducible workflow for reducing discovery cycle time. By making retrieval, screening, synthesis feasibility, and simulation setup part of the same loop, the system can help scientists spend less time coordinating tools and more time validating the most promising candidates. The current scoring functions are transparent placeholders, but the architecture is ready for physics-based simulation engines, uncertainty-aware surrogate models, and active-learning feedback from experiments.

## Frontier Framing

The strongest way to frame the project is as a coordination layer for scientific AI. Many models can predict one property, but real materials discovery requires coordinating evidence, simulation, synthesis feasibility, device constraints, and experimental follow-up. MatAgent Lab demonstrates that full loop in a runnable form.

## Strong Demo Commands

```bash
PYTHONPATH=src python -m matagent_lab discover --config configs/ar_glasses.json
PYTHONPATH=src python -m matagent_lab benchmark --config configs/robotics_actuator.json --repeats 5
PYTHONPATH=src python -m matagent_lab slurm --formula "Pb(Zr0.52Ti0.48)O3" --workflow dft
```

## Honest Limitations

The current scoring functions are not validated physical models. They are explainable placeholders that make the software architecture visible. The next serious step is to connect the `SimulationAgent` to real DFT, MD, Monte Carlo, or ML surrogate models and compare ranking quality against known benchmark materials.
