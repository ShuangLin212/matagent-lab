from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .chemistry import estimate_material_properties, parse_formula
from .models import (
    AgentTrace,
    MaterialCandidate,
    RetrievedDocument,
    ScreeningResult,
    SynthesisAssessment,
    TaskSpec,
)
from .rag import ScientificRetrievalIndex


@dataclass(frozen=True)
class CandidateTemplate:
    formula: str
    name: str
    domain: str
    rationale: str
    metadata: dict[str, str]


AR_CANDIDATES = [
    CandidateTemplate(
        "Al2O3",
        "ALD alumina optical barrier",
        "ar_glasses",
        "Low-mass oxide barrier candidate for transparent protective coatings.",
        {"workflow": "dft", "processing": "atomic layer deposition"},
    ),
    CandidateTemplate(
        "MgAl2O4",
        "Magnesium aluminate spinel",
        "ar_glasses",
        "Transparent ceramic spinel with useful hardness and optical-window heritage.",
        {"workflow": "dft", "processing": "sintering or sputtered thin film"},
    ),
    CandidateTemplate(
        "ZnO",
        "Al-doped zinc oxide",
        "ar_glasses",
        "Transparent conducting oxide candidate with lower indium exposure.",
        {"workflow": "dft", "dopant": "Al", "processing": "sputtering"},
    ),
    CandidateTemplate(
        "SnO2",
        "F-doped tin oxide",
        "ar_glasses",
        "Transparent conducting oxide baseline with mature thin-film process routes.",
        {"workflow": "dft", "dopant": "F", "processing": "spray pyrolysis or sputtering"},
    ),
    CandidateTemplate(
        "Ga2O3",
        "Gallium oxide dielectric layer",
        "ar_glasses",
        "Wide-bandgap oxide for transparent dielectric and sensing stacks.",
        {"workflow": "dft", "processing": "MOCVD or sputtering"},
    ),
    CandidateTemplate(
        "SiO2",
        "Silica flexible encapsulant",
        "ar_glasses",
        "Transparent, abundant dielectric baseline for optical and moisture barriers.",
        {"workflow": "md", "processing": "plasma enhanced CVD"},
    ),
    CandidateTemplate(
        "ZrO2",
        "Zirconia high-index nanolaminate",
        "ar_glasses",
        "Mechanically robust oxide for optical stack tuning and scratch resistance.",
        {"workflow": "dft", "processing": "ALD nanolaminate"},
    ),
    CandidateTemplate(
        "In2O3",
        "Indium oxide transparent conductor",
        "ar_glasses",
        "High-performance transparent conducting oxide baseline with supply-risk tradeoffs.",
        {"workflow": "dft", "processing": "sputtering"},
    ),
]

ROBOTICS_CANDIDATES = [
    CandidateTemplate(
        "BaTiO3",
        "Lead-free barium titanate actuator ceramic",
        "robotics_actuator",
        "Ferroelectric perovskite baseline for piezoelectric sensing and actuation.",
        {"workflow": "dft", "processing": "solid-state synthesis and poling"},
    ),
    CandidateTemplate(
        "Pb(Zr0.52Ti0.48)O3",
        "PZT morphotropic actuator reference",
        "robotics_actuator",
        "High-response piezoelectric reference material with toxicity concerns.",
        {"workflow": "dft", "processing": "oxide calcination and poling"},
    ),
    CandidateTemplate(
        "C2H2F2",
        "PVDF electroactive polymer repeat unit",
        "robotics_actuator",
        "Flexible fluoropolymer candidate for lightweight soft robotic actuators.",
        {"workflow": "md", "processing": "solution casting, stretching, and poling"},
    ),
    CandidateTemplate(
        "C2H6OSi",
        "PDMS silicone elastomer repeat unit",
        "robotics_actuator",
        "Soft, processable elastomer baseline for stretchable sensing skins.",
        {"workflow": "md", "processing": "crosslinking and soft lithography"},
    ),
    CandidateTemplate(
        "NiTi",
        "Nickel titanium shape-memory alloy",
        "robotics_actuator",
        "High strain-density actuator reference for compact robotic mechanisms.",
        {"workflow": "monte_carlo", "processing": "arc melting and thermomechanical training"},
    ),
    CandidateTemplate(
        "SrTiO3",
        "Strontium titanate dielectric actuator",
        "robotics_actuator",
        "Lead-free perovskite platform for tunable dielectrics and oxide electronics.",
        {"workflow": "dft", "processing": "oxide thin-film growth"},
    ),
]


class LiteratureAgent:
    def __init__(self, index: ScientificRetrievalIndex) -> None:
        self.index = index

    def run(self, task: TaskSpec) -> tuple[list[RetrievedDocument], AgentTrace]:
        query = " ".join([task.objective, task.domain, *task.seed_formulas])
        documents = self.index.search(query, top_k=task.retrieval_k, domain=task.domain)
        trace = AgentTrace(
            agent="LiteratureAgent",
            summary=f"Retrieved {len(documents)} relevant scientific notes for {task.domain}.",
            artifacts={
                "document_ids": [item.document.id for item in documents],
                "scores": [item.score for item in documents],
            },
        )
        return documents, trace


class CandidateAgent:
    def run(
        self, task: TaskSpec, retrieved_documents: list[RetrievedDocument]
    ) -> tuple[list[MaterialCandidate], AgentTrace]:
        templates = list(self._templates_for_domain(task.domain))
        templates = self._prioritize_seed_formulas(templates, task.seed_formulas)
        candidates: list[MaterialCandidate] = []

        for index, template in enumerate(templates[: task.max_candidates], start=1):
            evidence_ids = self._evidence_ids(template, retrieved_documents)
            candidates.append(
                MaterialCandidate(
                    id=f"cand-{index:03d}",
                    formula=template.formula,
                    name=template.name,
                    domain=task.domain,
                    rationale=self._augment_rationale(template, retrieved_documents),
                    evidence_ids=evidence_ids,
                    metadata=dict(template.metadata),
                )
            )

        trace = AgentTrace(
            agent="CandidateAgent",
            summary=f"Generated {len(candidates)} candidates from domain templates and retrieved evidence.",
            artifacts={"formulas": [candidate.formula for candidate in candidates]},
        )
        return candidates, trace

    def _templates_for_domain(self, domain: str) -> Iterable[CandidateTemplate]:
        if domain == "ar_glasses":
            return AR_CANDIDATES
        if domain == "robotics_actuator":
            return ROBOTICS_CANDIDATES
        return [*AR_CANDIDATES, *ROBOTICS_CANDIDATES]

    def _prioritize_seed_formulas(
        self, templates: list[CandidateTemplate], seed_formulas: list[str]
    ) -> list[CandidateTemplate]:
        seed_order = {formula: index for index, formula in enumerate(seed_formulas)}
        return sorted(templates, key=lambda item: seed_order.get(item.formula, len(seed_order) + 1))

    def _evidence_ids(
        self, template: CandidateTemplate, retrieved_documents: list[RetrievedDocument]
    ) -> list[str]:
        formula_elements = set(parse_formula(template.formula))
        evidence_ids: list[str] = []
        for retrieved in retrieved_documents:
            document_text = retrieved.document.text.lower()
            material_hit = template.formula.lower() in document_text or template.name.lower() in document_text
            element_hit = sum(element.lower() in document_text for element in formula_elements) >= 2
            if material_hit or element_hit:
                evidence_ids.append(retrieved.document.id)
        if not evidence_ids and retrieved_documents:
            evidence_ids.append(retrieved_documents[0].document.id)
        return evidence_ids[:3]

    def _augment_rationale(
        self, template: CandidateTemplate, retrieved_documents: list[RetrievedDocument]
    ) -> str:
        if not retrieved_documents:
            return template.rationale
        top_tags = []
        for retrieved in retrieved_documents:
            top_tags.extend(retrieved.document.tags[:2])
        unique_tags = list(dict.fromkeys(top_tags))[:3]
        if unique_tags:
            return f"{template.rationale} Retrieval context: {', '.join(unique_tags)}."
        return template.rationale


class SimulationAgent:
    def run(
        self, task: TaskSpec, candidates: list[MaterialCandidate]
    ) -> tuple[dict[str, dict[str, float]], AgentTrace]:
        properties = {
            candidate.id: estimate_material_properties(candidate.formula, task.domain)
            for candidate in candidates
        }
        trace = AgentTrace(
            agent="SimulationAgent",
            summary="Estimated screening properties with transparent chemistry heuristics.",
            artifacts={
                "domain_scores": {
                    candidate_id: values["domain_score"] for candidate_id, values in properties.items()
                }
            },
        )
        return properties, trace


class SynthesisAgent:
    def run(
        self, candidates: list[MaterialCandidate]
    ) -> tuple[dict[str, SynthesisAssessment], AgentTrace]:
        assessments = {candidate.id: self._assess(candidate) for candidate in candidates}
        trace = AgentTrace(
            agent="SynthesisAgent",
            summary="Estimated synthetic viability, process route, and handling risks.",
            artifacts={
                candidate_id: {
                    "viability": assessment.viability_score,
                    "risks": assessment.risk_flags,
                }
                for candidate_id, assessment in assessments.items()
            },
        )
        return assessments, trace

    def _assess(self, candidate: MaterialCandidate) -> SynthesisAssessment:
        counts = parse_formula(candidate.formula)
        elements = set(counts)
        risks: list[str] = []
        viability = 0.72
        estimated_steps = 4

        if "Pb" in elements:
            risks.append("lead toxicity and RoHS constraints")
            viability -= 0.22
        if "In" in elements or "Ga" in elements:
            risks.append("supply risk for scarce transparent-electronics element")
            viability -= 0.08
        if {"C", "F"} <= elements:
            route = "solution casting, stretching, electrode deposition, and electric-field poling"
            viability += 0.08
            estimated_steps = 5
        elif {"Si", "O", "C", "H"} <= elements:
            route = "elastomer mixing, degassing, casting, thermal cure, and electrode integration"
            viability += 0.10
            estimated_steps = 4
        elif {"Ni", "Ti"} <= elements:
            route = "vacuum arc melting, homogenization, cold working, and shape-setting heat treatment"
            risks.append("nickel sensitivity and phase-control complexity")
            viability -= 0.06
            estimated_steps = 6
        elif "O" in elements:
            route = "precursor mixing, calcination, densification or film deposition, annealing, and characterization"
            viability += 0.04
            estimated_steps = 5
        else:
            route = "literature-guided synthesis planning followed by small-batch screening"
            viability -= 0.05

        if len(elements) >= 5:
            risks.append("large composition space may need design-of-experiments optimization")
            viability -= 0.04

        return SynthesisAssessment(
            viability_score=round(max(0.0, min(1.0, viability)), 3),
            route=route,
            estimated_steps=estimated_steps,
            risk_flags=risks,
        )


class CriticAgent:
    def run(
        self,
        task: TaskSpec,
        candidates: list[MaterialCandidate],
        properties: dict[str, dict[str, float]],
        synthesis: dict[str, SynthesisAssessment],
    ) -> tuple[list[ScreeningResult], AgentTrace]:
        results = [
            self._score_candidate(task, candidate, properties[candidate.id], synthesis[candidate.id])
            for candidate in candidates
        ]
        results.sort(key=lambda item: item.total_score, reverse=True)
        trace = AgentTrace(
            agent="CriticAgent",
            summary="Ranked candidates by domain score, viability, constraints, and evidence coverage.",
            artifacts={
                "top_candidate": results[0].candidate.formula if results else None,
                "pass_rate": sum(result.passed_constraints for result in results) / max(len(results), 1),
            },
        )
        return results, trace

    def _score_candidate(
        self,
        task: TaskSpec,
        candidate: MaterialCandidate,
        properties: dict[str, float],
        synthesis: SynthesisAssessment,
    ) -> ScreeningResult:
        violations = self._constraint_violations(task.constraints, properties)
        evidence_score = min(1.0, len(candidate.evidence_ids) / max(task.retrieval_k, 1))
        total = (
            0.62 * properties["domain_score"]
            + 0.28 * synthesis.viability_score
            + 0.10 * evidence_score
            - 0.09 * len(violations)
        )
        total = round(max(0.0, min(1.0, total)), 3)
        risks = list(synthesis.risk_flags)
        if properties["toxicity_score"] > 0.2:
            risks.append("toxicity score exceeds early-screening target")
        if properties["hpc_cost_hours"] > task.constraints.get("max_hpc_cost_hours", 99.0):
            risks.append("simulation cost estimate above target budget")

        return ScreeningResult(
            candidate=candidate,
            properties=properties,
            synthesis=synthesis,
            total_score=total,
            passed_constraints=not violations,
            violations=violations,
            risks=risks,
            next_experiments=self._next_experiments(task.domain, candidate),
        )

    def _constraint_violations(
        self, constraints: dict[str, float], properties: dict[str, float]
    ) -> list[str]:
        violations: list[str] = []
        for key, threshold in constraints.items():
            if key.startswith("min_"):
                property_name = key.removeprefix("min_")
                if properties.get(property_name, 0.0) < threshold:
                    violations.append(f"{property_name} below {threshold}")
            elif key.startswith("max_"):
                property_name = key.removeprefix("max_")
                if properties.get(property_name, 0.0) > threshold:
                    violations.append(f"{property_name} above {threshold}")
        return violations

    def _next_experiments(self, domain: str, candidate: MaterialCandidate) -> list[str]:
        workflow = candidate.metadata.get("workflow", "dft")
        if domain == "ar_glasses":
            return [
                f"Run {workflow.upper()} bandgap and defect screening for {candidate.formula}.",
                "Simulate thin-film optical stack impact at target wavelength bands.",
                "Measure film stress, haze, adhesion, and accelerated humidity stability.",
            ]
        if domain == "robotics_actuator":
            return [
                f"Run {workflow.upper()} or MD screening for electromechanical response.",
                "Estimate fatigue under cyclic strain and thermal loading.",
                "Prototype coupon-scale actuator and compare displacement per gram.",
            ]
        return [f"Run {workflow.upper()} validation and close the loop with measured properties."]

