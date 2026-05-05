from __future__ import annotations

import statistics
import time

from .models import DiscoveryReport
from .orchestrator import DiscoveryOrchestrator, RunConfig


class BenchmarkRunner:
    def __init__(self, config: RunConfig, repeats: int = 3) -> None:
        self.config = config
        self.repeats = repeats

    def run(self) -> dict[str, float | list[dict[str, float]]]:
        reports: list[DiscoveryReport] = []
        elapsed: list[float] = []
        for _ in range(self.repeats):
            start = time.perf_counter()
            reports.append(DiscoveryOrchestrator(self.config).run())
            elapsed.append(time.perf_counter() - start)

        top_scores = [report.metrics["top_score"] for report in reports]
        pass_rates = [report.metrics["pass_rate"] for report in reports]
        throughput = [report.metrics["candidates_per_second"] for report in reports]
        coverage = [report.metrics["retrieval_coverage"] for report in reports]

        return {
            "repeats": float(self.repeats),
            "mean_elapsed_seconds": round(statistics.mean(elapsed), 4),
            "mean_top_score": round(statistics.mean(top_scores), 3),
            "mean_pass_rate": round(statistics.mean(pass_rates), 3),
            "mean_candidates_per_second": round(statistics.mean(throughput), 3),
            "mean_retrieval_coverage": round(statistics.mean(coverage), 3),
            "runs": [report.metrics for report in reports],
        }

