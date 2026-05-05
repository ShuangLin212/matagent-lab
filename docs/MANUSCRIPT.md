# MatAgent Lab: An Agentic Closed-Loop Prototype for Materials and Chemistry Discovery

**Author:** Shuang Lin  
**Repository:** https://github.com/ShuangLin212/matagent-lab  
**Status:** Draft manuscript for portfolio, preprint, or technical report adaptation

## Abstract

Materials discovery is increasingly constrained not by the absence of predictive models, but by the difficulty of coordinating evidence, candidate generation, computational screening, synthesis feasibility, hardware constraints, and follow-up simulation in a reproducible loop. This manuscript introduces **MatAgent Lab**, a lightweight research prototype for agentic AI in materials and chemistry discovery. The system decomposes early-stage discovery into specialized agents for literature retrieval, candidate generation, formula-level screening, synthesis critique, candidate ranking, benchmarking, and high-performance computing (HPC) job preparation. The default implementation is deterministic and dependency-light, allowing the complete workflow to run locally without external API keys. At the same time, the software interfaces are designed so production deployments can replace the local agents with large language model (LLM) tool-use agents, dense scientific retrieval, density functional theory (DFT), molecular dynamics (MD), Monte Carlo simulation, active learning, knowledge graphs, and laboratory automation.

MatAgent Lab is evaluated on two hardware-relevant demonstration domains: transparent and lightweight materials for augmented-reality (AR) glasses, and sensing or actuating materials for robotics. In the AR-glasses task, the system screened eight candidates, achieved full retrieval coverage, identified magnesium aluminate spinel and zirconia as constraint-satisfying leads, and produced an auditable report containing scores, routes, risks, and next experiments. In the robotics-actuator benchmark, repeated local runs produced a mean top score of 0.726, mean constraint satisfaction score of 0.833, full formula diversity, and a Pareto front size of three. These results are not presented as validated materials predictions; instead, they demonstrate the architecture, artifacts, and evaluation surface required for closed-loop scientific AI. The central contribution is a transparent, runnable scaffold for moving from literature and candidate ideation to synthesis-aware ranking and HPC-ready validation.

## 1. Introduction

Accelerated materials discovery has long relied on high-throughput computation, curated databases, and machine learning models. The Materials Project helped establish a practical paradigm in which first-principles computations and open data can guide experimental search [1]. More recently, large-scale graph neural networks and active learning have expanded the number of candidate inorganic crystals available for computational screening [2]. In parallel, autonomous laboratories have begun to close the loop between computational recommendations and experimental synthesis, showing how software, robotics, analysis, and decision policies can act as a discovery engine rather than as separate tools [3,4].

Despite this progress, a gap remains between powerful prediction models and useful scientific workflows. A candidate material is rarely valuable because it optimizes one property in isolation. For device-facing applications, candidate selection must combine multiple objectives: literature evidence, predicted structure-property relationships, optical or electromechanical performance, stability, toxicity, resource availability, synthesis route, processing burden, and the cost of higher-fidelity computation. This is especially true for materials in wearable AR systems and robotics, where useful materials must be high-performing, manufacturable, safe, and compatible with hardware constraints.

LLM-based agents provide a promising coordination layer for such workflows. Agentic systems can interleave reasoning with tool use, retrieve external knowledge, call computational services, track intermediate artifacts, and adapt plans based on new results [5,6]. In chemistry, recent reviews highlight the potential of LLMs and autonomous agents for molecule design, synthesis planning, literature mining, and automated laboratory interfaces [7]. However, many demonstrations remain either conversational, single-task, or difficult to audit. Scientific users need systems that make assumptions explicit, preserve traces, expose metrics, and separate replaceable tools from stable workflow contracts.

MatAgent Lab addresses this need as a small but complete prototype. It implements a closed-loop discovery pipeline in pure Python, using deterministic local agents in place of external LLM or simulation services. The prototype is intentionally inspectable: every candidate carries evidence IDs, screening properties, synthesis assessments, ranking scores, violations, risks, and next experiments. The resulting report can be benchmarked and converted into Slurm templates for later DFT, MD, or Monte Carlo validation.

The purpose of this manuscript is to describe the system design, scientific assumptions, evaluation metrics, demonstration results, and production roadmap for MatAgent Lab. The work is best understood as a software architecture contribution rather than as a claim of newly discovered materials.

## 2. System Overview

MatAgent Lab represents materials discovery as a sequence of specialized scientific roles. A task configuration defines the domain, objective, constraints, seed formulas, retrieval budget, candidate budget, and corpus path. The orchestrator then executes five agents:

1. **Literature Agent:** builds a query from the task objective and seed formulas, then retrieves relevant scientific notes from a local BM25-style retrieval index.
2. **Candidate Agent:** proposes candidate materials from domain templates and attaches retrieved evidence to each formula.
3. **Simulation Agent:** parses formulas and computes transparent screening features, including proxies for optical, electromechanical, stability, toxicity, density, resource-risk, processability, and HPC-cost signals.
4. **Synthesis Agent:** assigns a plausible route, step count, viability score, and risk flags based on chemical class and practical synthesis constraints.
5. **Critic Agent:** ranks candidates using domain score, synthesis viability, evidence coverage, and penalties for constraint violations.

The pipeline outputs a JSON discovery report containing ranked candidates, metrics, and agent traces. It can also generate Slurm scripts for candidate-specific follow-up workflows. The default workflow stubs include DFT, MD, Monte Carlo, and custom simulation entry points, making the HPC interface concrete even without a real cluster submission.

The architecture is shown in the repository figure `docs/figures/closed_loop_architecture.svg`. The core design principle is modularity: local deterministic agents provide reproducibility for the repository, while the interfaces are compatible with replacement by production backends.

## 3. Methods

### 3.1 Task Specification

Each discovery run begins with a JSON task specification. The AR-glasses task focuses on transparent, lightweight conductive, dielectric, and barrier materials. It includes constraints on optical score, stability score, toxicity score, and estimated HPC cost. The robotics-actuator task focuses on next-generation sensing and actuating materials, with constraints on piezoelectric response, strain score, processability, toxicity, and HPC cost.

This explicit task layer is important because the same candidate can be valuable in one hardware context and weak in another. For example, a dense oxide may be acceptable in a thin optical stack but unsuitable for a lightweight actuator. Similarly, a high-response piezoelectric reference material can be scientifically informative but practically penalized by toxicity and regulatory constraints.

### 3.2 Retrieval-Augmented Scientific Context

The literature agent uses a lightweight BM25-style index over a small JSONL corpus. Documents contain titles, abstracts, tags, materials, and domain labels. The retrieval index tokenizes document fields, computes term frequencies and document frequencies, and returns scored documents matching the objective and domain.

This local index is deliberately simple. Its role is not to compete with dense scientific retrieval, but to enforce the workflow contract that candidate generation should be grounded in retrievable evidence. In a production system, this component could be replaced by embeddings, hybrid search, paper parsing, patent ingestion, laboratory notebooks, or a materials knowledge graph.

### 3.3 Candidate Generation

Candidate templates are organized by domain. The AR-glasses set includes materials such as `MgAl2O4`, `Al2O3`, `ZrO2`, `SiO2`, `ZnO`, `SnO2`, `In2O3`, and `Ga2O3`. The robotics set includes `BaTiO3`, `Pb(Zr0.52Ti0.48)O3`, PVDF-like and PDMS-like repeat units, `NiTi`, and `SrTiO3`. Seed formulas in the task configuration prioritize candidates while preserving a fixed budget.

Each generated candidate includes a formula, name, domain, rationale, metadata, and evidence IDs. The metadata includes suggested workflow type and processing route, which later supports HPC script generation and synthesis assessment.

### 3.4 Formula Parsing and Screening Features

The chemistry module parses formulas into elemental counts, including fractional stoichiometries and parenthetical groups. It computes molecular weight, average electronegativity, electronegativity spread, covalent-radius statistics, oxygen fraction, halogen fraction, transition-metal fraction, polymer-element fraction, toxic-element fraction, supply-risk fraction, density proxy, and lightness score.

Screening properties are then estimated using transparent rules. For AR-glasses materials, the domain score emphasizes optical score, lightness, stability, resource score, and modulus proxy. For robotics materials, the score emphasizes piezoelectric response, strain score, processability, stability, and low toxicity. These functions are heuristics, not validated physical models. They are included to make the system executable, inspectable, and ready for replacement by real simulation or surrogate models.

### 3.5 Synthesis-Aware Critique

The synthesis agent estimates route and viability based on chemistry class. Oxides receive routes such as precursor mixing, calcination, densification or film deposition, annealing, and characterization. Fluoropolymers receive solution casting, stretching, electrode deposition, and poling routes. Silicone-like materials receive elastomer mixing, degassing, casting, curing, and electrode integration. NiTi receives a shape-memory-alloy processing route. Candidates containing lead, indium, or gallium receive toxicity or supply-risk flags where appropriate.

This component is central to the scientific thesis of the work. Many AI materials workflows rank candidates by predicted property alone. MatAgent Lab treats synthesizability, process complexity, toxicity, and supply risk as first-class ranking signals.

### 3.6 Ranking and Multi-Objective Metrics

The critic agent computes a total score from domain score, synthesis viability, evidence coverage, and constraint penalties. In the current implementation, the score uses weights of 0.62, 0.28, and 0.10 for domain score, viability, and evidence coverage, respectively, with a penalty for each constraint violation. The output includes pass/fail status, violation messages, risk flags, and next experiments.

The orchestrator reports both operational and scientific metrics:

- candidate count
- candidates per second
- pass rate
- mean total score
- mean viability score
- retrieval coverage
- mean constraint violations
- constraint satisfaction score
- mean risk flags
- mean toxicity score
- mean HPC cost
- formula diversity
- Pareto front size
- score spread
- whether the top candidate passed constraints

The Pareto front is computed over domain score, synthesis viability, evidence coverage, and constraint satisfaction. This gives a compact view of whether the ranked set contains multiple scientifically meaningful tradeoffs.

## 4. Demonstration Experiments

Two demonstration tasks were run using the committed configurations and local corpus.

### 4.1 AR-Glasses Materials

The AR-glasses task screened eight candidates for transparent, lightweight, stable materials compatible with wearable optical systems. The top ranked candidate was magnesium aluminate spinel (`MgAl2O4`) with a total score of 0.706 and passing constraint status. Zirconia (`ZrO2`) ranked second with a score of 0.618 and also passed constraints. The full report achieved retrieval coverage of 1.0, formula diversity of 1.0, and a pass rate of 0.25. The system reported a mean total score of 0.520, mean viability score of 0.740, mean HPC cost of 0.863 hours, and a score spread of 0.330.

The ranking is scientifically plausible for a demonstration system. Spinel is a known transparent ceramic class with optical-window relevance, while zirconia and alumina are common oxide candidates for mechanically robust coatings and dielectric layers. The system also penalized materials with poorer constraint fit or supply-risk considerations, such as indium- and gallium-containing oxides.

### 4.2 Robotics Actuator Materials

The robotics-actuator benchmark repeated the discovery workflow three times. Because the default implementation is deterministic, repeated runs produced identical ranking-level scientific metrics and small runtime variation. The benchmark reported a mean top score of 0.726, mean pass rate of 0.333, mean retrieval coverage of 1.0, mean Pareto front size of 3.0, mean formula diversity of 1.0, and mean constraint satisfaction score of 0.833.

These metrics show that the candidate set includes multiple tradeoff-relevant options rather than a single overwhelming lead. For example, barium titanate offers a lead-free piezoelectric ceramic pathway, PZT remains a high-response reference with toxicity penalties, PVDF-like polymers offer lightweight flexibility, and NiTi represents a distinct shape-memory actuator class. A production system could use the Pareto front to allocate follow-up simulations or experiments across different mechanistic classes.

### 4.3 HPC Script Generation

The `slurm` command converts candidate formulas and workflow types into scheduler-ready templates. For example, `BaTiO3` with the DFT workflow produces a script that loads a quantum-chemistry module, exports the repository source path, and calls a DFT workflow entry point. The included scripts are stubs, but they define the expected handoff between agentic ranking and high-fidelity computation.

This handoff is important because autonomous discovery systems need a way to convert ranked hypotheses into executable compute jobs. In future work, these scripts could be submitted to an actual scheduler, monitored, parsed, and returned to the discovery memory.

## 5. Discussion

MatAgent Lab illustrates how agentic AI can act as a coordination layer for scientific discovery. Its main contribution is not a new surrogate model, crystal generator, or synthesis planner. Instead, it defines a workflow in which such tools can cooperate through structured artifacts. Each agent has a narrow responsibility, and each output is inspectable.

The design has several strengths. First, the system separates scientific concerns: retrieval, generation, screening, synthesis, ranking, benchmarking, and HPC preparation are independent modules. Second, the reports are auditable: a reviewer can trace a candidate from retrieved evidence to formula features, synthesis risks, constraint violations, and next experiments. Third, the metrics go beyond runtime and top score, capturing retrieval coverage, diversity, risk burden, constraint satisfaction, and Pareto-front structure. Fourth, the repository is easy to run, making it suitable for code review and further extension.

The design also exposes important limitations. Formula-level heuristics cannot replace DFT, MD, Monte Carlo, experimental characterization, or calibrated ML surrogate models. The local literature corpus is small and manually curated. Candidate generation is template-based rather than generative. The synthesis agent uses rules rather than real retrosynthesis, precursor availability, safety database integration, or lab inventory constraints. The current results should therefore be interpreted as a systems demonstration, not as validated discovery.

Nevertheless, the workflow is aligned with the direction of modern scientific AI. Large materials models can generate or score candidates, autonomous labs can synthesize and characterize materials, and LLM agents can coordinate tool use and retrieval. The missing layer is often the reproducible orchestration contract: what agents exchange, how results are scored, how risks are surfaced, and how follow-up jobs are launched. MatAgent Lab makes that layer concrete.

## 6. Future Work

Several extensions would move MatAgent Lab from prototype toward research-grade autonomous discovery:

1. Replace formula heuristics with DFT, MD, Monte Carlo, and calibrated surrogate models.
2. Add uncertainty estimates and expected-improvement policies for active learning.
3. Generate structures and molecular geometries instead of screening formulas alone.
4. Replace local BM25 retrieval with dense search over papers, patents, databases, and internal reports.
5. Store candidate-property-evidence relationships in a graph database.
6. Connect Slurm submission, job monitoring, output parsing, and feedback into the agent memory.
7. Validate ranking quality against known benchmark materials and expert review.
8. Add laboratory constraints such as precursor availability, safety limits, tool compatibility, and characterization cost.

These extensions would enable the system to move from demonstration to closed-loop computational and experimental discovery.

## 7. Conclusion

MatAgent Lab provides a runnable, inspectable prototype for agentic AI in materials and chemistry discovery. It demonstrates how literature retrieval, candidate generation, formula parsing, multi-objective screening, synthesis critique, ranking, benchmarking, and HPC preparation can be organized into one closed-loop workflow. The system targets hardware-relevant AR-glasses and robotics materials while remaining honest about the limitations of its current heuristics. Its scientific value lies in the architecture and evaluation surface: it shows how future LLM agents, simulation engines, active learning policies, and lab automation systems can be connected through auditable, reproducible artifacts.

## References

[1] Jain, A., Ong, S. P., Hautier, G., Chen, W., Richards, W. D., Dacek, S., Cholia, S., Gunter, D., Skinner, D., Ceder, G., and Persson, K. A. "Commentary: The Materials Project: A materials genome approach to accelerating materials innovation." *APL Materials* 1, 011002 (2013). https://doi.org/10.1063/1.4812323

[2] Merchant, A., Batzner, S., Schoenholz, S. S., Aykol, M., Cheon, G., and Cubuk, E. D. et al. "Scaling deep learning for materials discovery." *Nature* 624, 80-85 (2023). https://doi.org/10.1038/s41586-023-06735-9

[3] Szymanski, N. J., Rendy, B., Fei, Y., Kumar, R. E., He, T., Milsted, D., McDermott, M. J., Gallant, M., and others. "An autonomous laboratory for the accelerated synthesis of inorganic materials." *Nature* 624, 86-91 (2023). https://doi.org/10.1038/s41586-023-06734-w

[4] Abolhasani, M. and Kumacheva, E. "The rise of self-driving labs in chemical and materials sciences." *Nature Synthesis* 2, 483-492 (2023). https://www.nature.com/articles/s44160-022-00231-0

[5] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., and Cao, Y. "ReAct: Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629 (2022). https://arxiv.org/abs/2210.03629

[6] Lei, G., Docherty, R., and Cooper, S. J. "Materials science in the era of large language models: a perspective." *Digital Discovery* 3, 1257-1272 (2024). https://doi.org/10.1039/D4DD00074A

[7] Ramos, M. C., Collison, C. J., and White, A. D. "A review of large language models and autonomous agents in chemistry." *Chemical Science* 16, 2514-2572 (2025). https://doi.org/10.1039/D4SC03921A

