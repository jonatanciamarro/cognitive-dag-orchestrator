from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, TYPE_CHECKING
import copy
import uuid

if TYPE_CHECKING:
    from ..semantic_memory import SemanticMemoryStore
    from ..explanation import ExplanationStore


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def iso_duration_ms(started_at: str, finished_at: str) -> int:
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(finished_at)
    return max(0, int((end - start).total_seconds() * 1000))


def duration_ms(started_at: str | None, finished_at: str | None) -> int:
    if not started_at or not finished_at:
        return 0
    return iso_duration_ms(started_at, finished_at)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if dataclass_is_instance(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def dataclass_is_instance(value: Any) -> bool:
    return hasattr(value, "__dataclass_fields__")


@dataclass
class CampaignContext:
    campaign: Dict[str, Any] = field(default_factory=dict)
    signals: Dict[str, Any] = field(default_factory=dict)
    memory: list[Dict[str, Any]] = field(default_factory=list)
    policy: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict, repr=False)
    artifacts: Dict[str, Any] = field(default_factory=dict, repr=False)
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "CampaignContext":
        memory = payload.get("memory", payload.get("memory_records", []))
        policy = payload.get("policy", payload.get("compliance_policy", {}))
        signals = payload.get("signals", payload.get("metrics", {}))
        return cls(
            campaign=dict(payload.get("campaign", {})),
            signals=dict(signals),
            memory=list(memory),
            policy=dict(policy),
            artifacts=dict(payload.get("artifacts", {})),
        )

    def snapshot(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "campaign": copy.deepcopy(self.campaign),
            "signals": copy.deepcopy(self.signals),
            "memory": copy.deepcopy(self.memory),
            "policy": copy.deepcopy(self.policy),
            "step_results": {
                key: _jsonable(value) for key, value in self.step_results.items()
            },
            "artifacts": copy.deepcopy(self.artifacts),
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.snapshot()


@dataclass
class AgentTrace:
    agent: str
    step_id: str
    status: str
    started_at: str
    finished_at: str
    duration_ms: int
    thread_name: str
    dependencies: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "step_id": self.step_id,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "thread_name": self.thread_name,
            "dependencies": list(self.dependencies),
            "notes": list(self.notes),
            "error": self.error,
            "metadata": _jsonable(self.metadata),
        }


@dataclass
class AgentResult:
    agent: str
    status: str
    output: Any = None
    trace: AgentTrace | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "status": self.status,
            "output": _jsonable(self.output),
            "trace": self.trace.to_dict() if self.trace else None,
            "warnings": list(self.warnings),
        }


class AgentBase(ABC):
    name: str

    def __init__(
        self,
        name: str | None = None,
        semantic_memory: "SemanticMemoryStore | None" = None,
        explanation_store: "ExplanationStore | None" = None,
    ) -> None:
        self.name = name or self.__class__.__name__.replace("Agent", "").lower()
        self.semantic_memory = semantic_memory
        self.explanation_store = explanation_store

    @abstractmethod
    def run(self, context: CampaignContext) -> AgentResult:
        raise NotImplementedError


# ── Structured Logging Mixin ──────────────────────────────────

from ..logging_utils import StructuredLogger


class LoggedAgent(AgentBase):
    """AgentBase with structured logging built-in."""

    def __init__(
        self,
        name: str | None = None,
        semantic_memory=None,
        explanation_store=None,
    ) -> None:
        super().__init__(name, semantic_memory, explanation_store)
        self.log = StructuredLogger(self.name)

    def log_start(self, context: "CampaignContext") -> None:
        """Log agent execution start."""
        self.log.info(
            "agent_start",
            agent=self.name,
            campaign=context.campaign.campaign_id
            if hasattr(context.campaign, "campaign_id")
            else "unknown",
            objective=context.campaign.objective
            if hasattr(context.campaign, "objective")
            else "",
        )

    def log_success(self, result: "AgentResult") -> None:
        """Log agent execution success with metrics."""
        self.log.info(
            "agent_success",
            agent=self.name,
            status=result.status,
            actions=len(result.actions),
            confidence=result.confidence,
            duration_ms=getattr(result, "_duration_ms", 0),
        )

    def log_failure(
        self, error: Exception, context: "CampaignContext"
    ) -> "AgentResult":
        """Log agent execution failure and return safe error result."""
        self.log.error(
            "agent_failure",
            agent=self.name,
            error=str(error)[:200],
            error_type=type(error).__name__,
        )
        return AgentResult(
            agent=self.name,
            status="failed",
            actions=[],
            confidence=0.0,
            summary=f"Falha na execução: {error}",
            errors=[str(error)],
        )

    def run_with_logging(self, context: "CampaignContext") -> "AgentResult":
        """Run agent with automatic logging, timing and error handling."""
        import time

        self.log_start(context)
        t0 = time.time()
        try:
            result = self.run(context)
            result._duration_ms = int((time.time() - t0) * 1000)
            self.log_success(result)
            return result
        except Exception as e:
            result = self.log_failure(e, context)
            result._duration_ms = int((time.time() - t0) * 1000)
            return result
