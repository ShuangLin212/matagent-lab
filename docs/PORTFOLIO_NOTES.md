# Portfolio Notes

Use this project to discuss agentic AI for materials discovery in interviews.

## Resume Bullet Options

- Built MatAgent Lab, a Python multi-agent materials discovery system that combines scientific RAG, candidate generation, property screening, synthesis-viability scoring, and Slurm job generation.
- Implemented chemistry-aware formula parsing, deterministic screening heuristics, and benchmark metrics for transparent conductors, optical coatings, soft robotic polymers, and piezoelectric actuators.
- Designed extension points for LLM tool-use agents, DFT/MD/Monte Carlo simulation backends, HPC orchestration, and active-learning feedback loops.

## Interview Talk Track

The project mirrors a closed-loop discovery workflow. A literature agent retrieves context, a candidate agent proposes materials, a simulation agent estimates screening properties, a synthesis agent filters for practical routes, and a critic ranks candidates against domain constraints. The default implementation is local and deterministic so it can run in CI, but the module boundaries are ready for LLMs, HPC jobs, and real computational chemistry tools.

## Strong Demo Commands

```bash
PYTHONPATH=src python -m matagent_lab discover --config configs/ar_glasses.json
PYTHONPATH=src python -m matagent_lab benchmark --config configs/robotics_actuator.json --repeats 5
PYTHONPATH=src python -m matagent_lab slurm --formula "Pb(Zr0.52Ti0.48)O3" --workflow dft
```

## Honest Limitations

The current scoring functions are not validated physical models. They are explainable placeholders that make the software architecture visible. The next serious step is to connect the `SimulationAgent` to real DFT, MD, Monte Carlo, or ML surrogate models and compare ranking quality against known benchmark materials.

