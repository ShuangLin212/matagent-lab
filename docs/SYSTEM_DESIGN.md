# System Design

MatAgent Lab is structured as a closed-loop materials discovery scaffold. The current implementation uses deterministic local agents so the repository is easy to run, test, and review. The interfaces are intentionally close to what production LLM and simulation integrations would need.

## Agent Roles

`LiteratureAgent` queries a local BM25-style index over scientific notes. In a production system, the same interface can wrap embeddings, vector search, knowledge graphs, or enterprise document stores.

`CandidateAgent` proposes candidate materials from retrieved context and domain templates. In a production system, this role can become an LLM tool-use agent that calls structure generators, patent search, or retrosynthesis tools.

`SimulationAgent` estimates properties from parsed chemistry features. In a production system, it can dispatch to DFT, molecular dynamics, Monte Carlo, or surrogate ML models.

`SynthesisAgent` scores practical viability and produces first-pass processing routes. In a production system, it can query inventory, lab automation constraints, safety systems, and synthesis-planning models.

`CriticAgent` combines evidence, simulated properties, constraints, and viability into a ranked report. This is where active-learning policies or human-in-the-loop review can choose the next experiment.

## Data Flow

1. Load a task config with domain, objective, constraints, seed formulas, corpus path, and candidate budget.
2. Retrieve supporting context from the scientific corpus.
3. Generate candidate formulas and rationale.
4. Parse formulas and estimate material properties.
5. Assess synthesis route, process burden, and risks.
6. Rank candidates and emit auditable traces.
7. Optionally generate HPC Slurm scripts for deeper simulation.

## Production Extension Points

- Literature ingestion: parse PDFs, patents, lab notebooks, and internal reports into structured records.
- Retrieval: replace BM25 with dense embeddings, hybrid search, reranking, and knowledge-graph constraints.
- LLM orchestration: add tool-calling agents with guardrails and structured output schemas.
- Simulation: connect ASE, VASP, Quantum ESPRESSO, LAMMPS, OpenMM, or internal surrogate models.
- HPC: submit Slurm jobs, track status, parse outputs, and feed results back into the discovery memory.
- Evaluation: benchmark accuracy against known materials, throughput, cost per candidate, and synthesis hit rate.

## Engineering Choices

- Pure Python core for low-friction review and testing.
- Typed dataclasses for structured reports and auditable traces.
- Deterministic scores so CI remains stable.
- Small, readable modules that can be replaced by real scientific backends.

