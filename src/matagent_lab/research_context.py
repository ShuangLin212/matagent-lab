from __future__ import annotations

from .models import AgentTrace, TaskSpec


TOP_LITERATURE = [
    {
        "key": "Coscientist",
        "citation": "Boiko et al., Nature 2023",
        "url": "https://doi.org/10.1038/s41586-023-06792-0",
        "lesson": "LLM scientific agents should combine planning, documentation search, code execution, and experimental tool use.",
        "package_mapping": "MatAgent Lab separates retrieval, candidate generation, simulation, mechanism reasoning, synthesis critique, and HPC job preparation into explicit agents.",
    },
    {
        "key": "ChemCrow",
        "citation": "Bran et al., Nature Machine Intelligence 2024",
        "url": "https://doi.org/10.1038/s42256-024-00832-8",
        "lesson": "Chemistry agents become more reliable when LLM reasoning is augmented with expert tools instead of relying on free-form text alone.",
        "package_mapping": "The package exposes tool-like modules for formula parsing, property screening, retrieval, benchmarking, and Slurm generation.",
    },
    {
        "key": "A-Lab",
        "citation": "Szymanski et al., Nature 2023",
        "url": "https://doi.org/10.1038/s41586-023-06734-w",
        "lesson": "Autonomous inorganic discovery needs closed-loop synthesis planning, execution, characterization, and feedback.",
        "package_mapping": "Synthesis viability, route notes, risk flags, and validation priorities are first-class report fields.",
    },
    {
        "key": "GNoME",
        "citation": "Merchant et al., Nature 2023",
        "url": "https://doi.org/10.1038/s41586-023-06735-9",
        "lesson": "Materials discovery benefits from active-learning flywheels that connect model screening with higher-fidelity validation.",
        "package_mapping": "Ranked candidates include Pareto-front metrics and HPC-ready DFT/MD/Monte Carlo follow-up hooks.",
    },
    {
        "key": "SciAgents",
        "citation": "Ghafarollahi and Buehler, Advanced Materials 2024",
        "url": "https://doi.org/10.1002/adma.202413523",
        "lesson": "Multi-agent scientific discovery can use graph-style concept reasoning to generate hypotheses and mechanisms.",
        "package_mapping": "The MechanismAgent infers chemistry families, structural motifs, bonding character, mechanism hypotheses, and validation priorities.",
    },
    {
        "key": "LLM agents in chemistry review",
        "citation": "Ramos et al., Chemical Science 2025",
        "url": "https://doi.org/10.1039/D4SC03921A",
        "lesson": "Future chemistry agents require better benchmarks, interpretability, tool integration, and experimental collaboration.",
        "package_mapping": "Reports include auditable traces, constraint metrics, formula diversity, Pareto-front size, risk flags, and extension points.",
    },
]


def build_research_context_trace(task: TaskSpec) -> AgentTrace:
    """Expose literature-derived design rationale as an auditable report trace."""

    principles = [
        "tool-using autonomy",
        "evidence-grounded retrieval",
        "synthesis-aware ranking",
        "mechanism-level interpretation",
        "closed-loop HPC or lab validation",
        "benchmarkable and auditable artifacts",
    ]
    domain_hooks = _domain_hooks(task.domain)
    return AgentTrace(
        agent="ResearchContextAgent",
        summary="Mapped literature lessons from autonomous chemistry and materials AI into package design principles.",
        artifacts={
            "design_principles": principles,
            "domain_hooks": domain_hooks,
            "top_literature": TOP_LITERATURE,
        },
    )


def _domain_hooks(domain: str) -> list[str]:
    if domain == "ar_glasses":
        return [
            "optical transparency and high-index stack validation",
            "thin-film synthesis and humidity-aging feedback",
            "scarce-element and toxicity constraints for wearable hardware",
        ]
    if domain == "robotics_actuator":
        return [
            "piezoelectric, relaxor, polymer, nitride, and shape-memory mechanism classes",
            "fatigue and cyclic-strain validation",
            "lead-free and process-compatible actuator prioritization",
        ]
    return ["multi-objective validation", "synthesis-aware feedback", "HPC workflow handoff"]

