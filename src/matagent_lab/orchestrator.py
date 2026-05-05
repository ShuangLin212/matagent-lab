from __future__ import annotations

import json
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from .agents import CandidateAgent, CriticAgent, LiteratureAgent, SimulationAgent, SynthesisAgent
from .models import AgentTrace, DiscoveryReport, TaskSpec
from .rag import ScientificRetrievalIndex


class RunConfig:
    def __init__(self, task: TaskSpec, config_path: Path | None = None) -> None:
        self.task = task
        self.config_path = config_path

    @classmethod
    def from_json(cls, path: str | Path) -> "RunConfig":
        config_path = Path(path)
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        task = TaskSpec(**payload)
        if not Path(task.corpus_path).is_absolute():
            repo_root = config_path.parent.parent
            task = replace(task, corpus_path=str(repo_root / task.corpus_path))
        return cls(task=task, config_path=config_path)


class DiscoveryOrchestrator:
    """Coordinates the local agent loop from retrieval to ranked report."""

    def __init__(self, config: RunConfig) -> None:
        self.config = config
        self.index = ScientificRetrievalIndex.from_jsonl(config.task.corpus_path)
        self.literature_agent = LiteratureAgent(self.index)
        self.candidate_agent = CandidateAgent()
        self.simulation_agent = SimulationAgent()
        self.synthesis_agent = SynthesisAgent()
        self.critic_agent = CriticAgent()

    def run(self) -> DiscoveryReport:
        start = time.perf_counter()
        traces: list[AgentTrace] = []
        task = self.config.task

        retrieved, trace = self.literature_agent.run(task)
        traces.append(trace)
        candidates, trace = self.candidate_agent.run(task, retrieved)
        traces.append(trace)
        properties, trace = self.simulation_agent.run(task, candidates)
        traces.append(trace)
        synthesis, trace = self.synthesis_agent.run(candidates)
        traces.append(trace)
        ranked_results, trace = self.critic_agent.run(task, candidates, properties, synthesis)
        traces.append(trace)

        elapsed_seconds = time.perf_counter() - start
        metrics = self._metrics(ranked_results, elapsed_seconds)
        return DiscoveryReport(
            task=task,
            generated_at=datetime.now(timezone.utc).isoformat(),
            ranked_results=ranked_results,
            metrics=metrics,
            agent_traces=traces,
        )

    def _metrics(self, ranked_results, elapsed_seconds: float) -> dict[str, float]:
        candidate_count = len(ranked_results)
        pass_count = sum(result.passed_constraints for result in ranked_results)
        mean_total = sum(result.total_score for result in ranked_results) / max(candidate_count, 1)
        mean_viability = (
            sum(result.synthesis.viability_score for result in ranked_results) / max(candidate_count, 1)
        )
        retrieval_coverage = (
            sum(1 for result in ranked_results if result.candidate.evidence_ids) / max(candidate_count, 1)
        )
        return {
            "elapsed_seconds": round(elapsed_seconds, 4),
            "candidate_count": float(candidate_count),
            "candidates_per_second": round(candidate_count / max(elapsed_seconds, 1e-9), 3),
            "pass_rate": round(pass_count / max(candidate_count, 1), 3),
            "mean_total_score": round(mean_total, 3),
            "mean_viability_score": round(mean_viability, 3),
            "retrieval_coverage": round(retrieval_coverage, 3),
            "top_score": ranked_results[0].total_score if ranked_results else 0.0,
        }

