"""Evaluation Engine — Benchmark and score agent performance.

Mede:
- Acuracia: resultados corretos vs incorretos
- Custo: USD por execucao
- Latencia: tempo de resposta
- Confiabilidade: taxa de sucesso vs falha
- Taxa de recuperacao: recuperacao apos falha

Uso:
    engine = EvaluationEngine()
    scorecard = engine.evaluate("agent_name", trace_data)
    benchmark = engine.run_benchmark("agent_name", test_cases)
"""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentScorecard:
    """Scorecard for a single agent evaluation."""

    agent_name: str
    accuracy: float = 0.0  # 0-1
    cost_efficiency: float = 0.0  # 0-1 (higher = cheaper)
    avg_latency_ms: float = 0.0
    reliability: float = 1.0  # 0-1 (success_rate)
    recovery_rate: float = 1.0  # 0-1
    overall_score: float = 0.0  # 0-100 weighted composite
    total_calls: int = 0
    total_cost: float = 0.0
    total_errors: int = 0
    total_recoveries: int = 0
    samples: list[dict[str, Any]] = field(default_factory=list)
    evaluated_at: str = field(default_factory=_now_iso)

    def compute_overall(self) -> float:
        """Compute weighted overall score (0-100)."""
        w_accuracy = 0.35
        w_cost = 0.15
        w_latency = 0.15
        w_reliability = 0.25
        w_recovery = 0.10

        # Normalize latency: <100ms = 1.0, >10s = 0.0
        latency_score = (
            max(0, 1.0 - self.avg_latency_ms / 10000)
            if self.avg_latency_ms > 0
            else 1.0
        )

        score = (
            self.accuracy * w_accuracy
            + self.cost_efficiency * w_cost
            + latency_score * w_latency
            + self.reliability * w_reliability
            + self.recovery_rate * w_recovery
        ) * 100

        self.overall_score = round(score, 1)
        return self.overall_score

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "overall_score": self.overall_score,
            "accuracy": round(self.accuracy, 3),
            "cost_efficiency": round(self.cost_efficiency, 3),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "reliability": round(self.reliability, 3),
            "recovery_rate": round(self.recovery_rate, 3),
            "total_calls": self.total_calls,
            "total_cost": round(self.total_cost, 6),
            "total_errors": self.total_errors,
            "evaluated_at": self.evaluated_at,
        }


@dataclass
class BenchmarkCase:
    """A single test case for benchmarking."""

    name: str
    input_data: dict[str, Any]
    expected_output: Any = None
    expected_status: str = "success"
    timeout_ms: int = 30000
    tags: list[str] = field(default_factory=list)


class EvaluationEngine:
    """Engine for evaluating and benchmarking agent performance.

    Mantem um historico de scorecards para acompanhar evolucao.
    """

    def __init__(self):
        self._scorecards: dict[str, AgentScorecard] = {}

    def evaluate_from_traces(
        self,
        agent_name: str,
        traces: list[dict[str, Any]],
    ) -> AgentScorecard:
        """Evaluate an agent from its execution traces."""
        if not traces:
            return AgentScorecard(agent_name=agent_name)

        total_calls = len(traces)
        successful = sum(1 for t in traces if t.get("status") == "success")
        failed = sum(1 for t in traces if t.get("status") == "failed")
        recovered = sum(1 for t in traces if t.get("status") == "recovered")
        total_cost = sum(t.get("cost", 0) for t in traces)
        latencies = [
            t.get("duration_ms", 0) for t in traces if t.get("duration_ms", 0) > 0
        ]

        # Calculate metrics
        reliability = successful / total_calls if total_calls > 0 else 1.0
        recovery_rate = (
            recovered / (failed + recovered) if (failed + recovered) > 0 else 1.0
        )
        avg_latency = statistics.mean(latencies) if latencies else 0.0

        # Cost efficiency: <$0.001 per call = 1.0, >$0.10 per call = 0.0
        cost_per_call = total_cost / total_calls if total_calls > 0 else 0
        cost_efficiency = max(0, 1.0 - cost_per_call * 10)

        scorecard = AgentScorecard(
            agent_name=agent_name,
            accuracy=reliability,  # Simplified: reliability as accuracy proxy
            cost_efficiency=round(cost_efficiency, 4),
            avg_latency_ms=round(avg_latency, 1),
            reliability=round(reliability, 4),
            recovery_rate=round(recovery_rate, 4),
            total_calls=total_calls,
            total_cost=round(total_cost, 6),
            total_errors=failed,
            total_recoveries=recovered,
            samples=traces[:10],  # Keep first 10 samples
        )
        scorecard.compute_overall()
        self._scorecards[agent_name] = scorecard
        return scorecard

    def run_benchmark(
        self,
        agent_name: str,
        agent_fn: Callable[[dict[str, Any]], Any],
        test_cases: list[BenchmarkCase],
    ) -> AgentScorecard:
        """Run a structured benchmark against an agent function."""
        results = []
        for case in test_cases:
            start = time.time()
            try:
                output = agent_fn(case.input_data)
                duration_ms = int((time.time() - start) * 1000)
                passed = self._check_expected(output, case)
                results.append(
                    {
                        "case": case.name,
                        "status": "success" if passed else "failed",
                        "duration_ms": duration_ms,
                        "output": output
                        if isinstance(output, dict)
                        else {"result": str(output)},
                        "cost": 0.0,
                        "tags": case.tags,
                    }
                )
            except Exception as e:
                duration_ms = int((time.time() - start) * 1000)
                results.append(
                    {
                        "case": case.name,
                        "status": "failed",
                        "duration_ms": duration_ms,
                        "error": str(e),
                        "cost": 0.0,
                        "tags": case.tags,
                    }
                )

        return self.evaluate_from_traces(agent_name, results)

    def _check_expected(self, output: Any, case: BenchmarkCase) -> bool:
        """Check if output matches expected."""
        if case.expected_output is None:
            return output is not None and output != {}
        return output == case.expected_output

    def get_scorecard(self, agent_name: str) -> AgentScorecard | None:
        """Get the latest scorecard for an agent."""
        return self._scorecards.get(agent_name)

    def list_scorecards(self) -> list[dict[str, Any]]:
        """List all evaluated agents."""
        return [s.to_dict() for s in self._scorecards.values()]

    def rank_agents(self) -> list[dict[str, Any]]:
        """Rank agents by overall score."""
        ranked = sorted(
            self._scorecards.values(),
            key=lambda s: s.overall_score,
            reverse=True,
        )
        return [s.to_dict() for s in ranked]


__all__ = [
    "EvaluationEngine",
    "AgentScorecard",
    "BenchmarkCase",
]
