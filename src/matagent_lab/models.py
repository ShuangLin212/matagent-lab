from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class TaskSpec:
    """Scientific discovery task loaded from a JSON config."""

    name: str
    domain: str
    objective: str
    constraints: dict[str, float]
    seed_formulas: list[str] = field(default_factory=list)
    corpus_path: str = "data/literature_corpus.jsonl"
    retrieval_k: int = 4
    max_candidates: int = 8


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    abstract: str
    tags: list[str]
    materials: list[str]
    domain: str = "general"

    @property
    def text(self) -> str:
        fields = [self.title, self.abstract, " ".join(self.tags), " ".join(self.materials)]
        return " ".join(fields)


@dataclass(frozen=True)
class RetrievedDocument:
    document: Document
    score: float
    matched_terms: list[str]


@dataclass(frozen=True)
class MaterialCandidate:
    id: str
    formula: str
    name: str
    domain: str
    rationale: str
    evidence_ids: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SynthesisAssessment:
    viability_score: float
    route: str
    estimated_steps: int
    risk_flags: list[str]


@dataclass(frozen=True)
class ChemistryInsight:
    material_family: str
    structure_motif: str
    bonding_character: str
    mechanism_hypotheses: list[str]
    tradeoff_notes: list[str]
    validation_priorities: list[str]
    descriptors: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScreeningResult:
    candidate: MaterialCandidate
    properties: dict[str, float]
    synthesis: SynthesisAssessment
    chemistry: ChemistryInsight
    total_score: float
    passed_constraints: bool
    violations: list[str]
    risks: list[str]
    next_experiments: list[str]


@dataclass(frozen=True)
class AgentTrace:
    agent: str
    summary: str
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoveryReport:
    task: TaskSpec
    generated_at: str
    ranked_results: list[ScreeningResult]
    metrics: dict[str, float]
    agent_traces: list[AgentTrace]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
