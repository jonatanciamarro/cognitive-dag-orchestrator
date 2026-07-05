from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping
import json
import threading
import traceback

from .agents.base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    _jsonable,
    duration_ms,
    iso_duration_ms,
    utc_now_iso,
)


@dataclass(frozen=True)
class WorkflowStepSpec:
    id: str
    agent: str
    depends_on: list[str] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "WorkflowStepSpec":
        return cls(
            id=str(payload["id"]),
            agent=str(payload["agent"]),
            depends_on=[str(item) for item in payload.get("depends_on", [])],
            description=str(payload.get("description", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent": self.agent,
            "depends_on": list(self.depends_on),
            "description": self.description,
        }


@dataclass(frozen=True)
class WorkflowSpec:
    name: str
    description: str = ""
    max_workers: int = 4
    steps: list[WorkflowStepSpec] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "WorkflowSpec":
        return cls(
            name=str(payload["name"]),
            description=str(payload.get("description", "")),
            max_workers=max(1, int(payload.get("max_workers", 4))),
            steps=[
                WorkflowStepSpec.from_mapping(step) for step in payload.get("steps", [])
            ],
        )

    @classmethod
    def load(cls, path: str | Path) -> "WorkflowSpec":
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return cls.from_mapping(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "max_workers": self.max_workers,
            "steps": [step.to_dict() for step in self.steps],
        }


@dataclass
class StepResult:
    step_id: str
    agent: str
    status: str
    output: Any = None
    error: str | None = None
    started_at: str = ""
    finished_at: str = ""
    duration_ms: int = 0
    thread_name: str = ""
    dependencies: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_agent_result(
        cls,
        step_id: str,
        dependencies: Iterable[str],
        result: AgentResult,
        started_at: str,
        finished_at: str,
        thread_name: str,
        fallback_error: str | None = None,
    ) -> "StepResult":
        trace = result.trace
        metadata = dict(trace.metadata) if trace else {}
        notes = list(trace.notes) if trace else []
        return cls(
            step_id=step_id,
            agent=result.agent,
            status=result.status,
            output=result.output,
            error=(
                result.trace.error
                if result.trace and result.trace.error
                else fallback_error
            ),
            started_at=trace.started_at if trace else started_at,
            finished_at=trace.finished_at if trace else finished_at,
            duration_ms=trace.duration_ms
            if trace
            else duration_ms(started_at, finished_at),
            thread_name=trace.thread_name if trace else thread_name,
            dependencies=list(dependencies),
            notes=notes,
            metadata=metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "agent": self.agent,
            "status": self.status,
            "output": _jsonable(self.output),
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "thread_name": self.thread_name,
            "dependencies": list(self.dependencies),
            "notes": list(self.notes),
            "metadata": _jsonable(self.metadata),
        }


@dataclass
class ExecutionAction:
    id: str
    title: str
    owner: str
    channel: str
    change: str
    priority: str
    rationale: str
    success_metric: str
    guardrails: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionPlan:
    objective: str
    summary: str
    status: str
    actions: list[ExecutionAction] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    guardrails: list[str] = field(default_factory=list)
    insights: Dict[str, Any] = field(default_factory=dict)
    source_steps: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "summary": self.summary,
            "status": self.status,
            "actions": [action.to_dict() for action in self.actions],
            "risks": list(self.risks),
            "guardrails": list(self.guardrails),
            "insights": _jsonable(self.insights),
            "source_steps": list(self.source_steps),
            "generated_at": self.generated_at,
        }


@dataclass
class WorkflowRunResult:
    workflow_name: str
    status: str
    started_at: str
    finished_at: str
    duration_ms: int
    output: Any
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    trace: list[Dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "output": _jsonable(self.output),
            "step_results": {
                key: value.to_dict() for key, value in self.step_results.items()
            },
            "trace": list(self.trace),
            "errors": list(self.errors),
        }


class WorkflowRunner:
    def __init__(self, max_workers: int | None = None) -> None:
        self.max_workers = max_workers

    def load_spec(self, path: str | Path) -> WorkflowSpec:
        return WorkflowSpec.load(path)

    def run(
        self,
        spec: WorkflowSpec,
        context: CampaignContext,
        registry: Mapping[str, AgentBase | Callable[[CampaignContext], AgentResult]],
    ) -> WorkflowRunResult:
        started_at = utc_now_iso()
        started = datetime.now(timezone.utc)
        completed: set[str] = set()
        scheduled: set[str] = set()
        step_results: Dict[str, StepResult] = {}
        trace: list[Dict[str, Any]] = []
        errors: list[str] = []
        step_by_id = {step.id: step for step in spec.steps}
        remaining = set(step_by_id)
        max_workers = max(1, self.max_workers or spec.max_workers or 1)

        def execute_step(step: WorkflowStepSpec) -> StepResult:
            thread_name = threading.current_thread().name
            run_started = utc_now_iso()
            try:
                agent = self._resolve_agent(step.agent, registry)
                if agent is None:
                    raise KeyError(f"Unknown agent '{step.agent}'")
                result = (
                    agent.run(context)
                    if isinstance(agent, AgentBase)
                    else agent(context)
                )
                if not isinstance(result, AgentResult):
                    result = AgentResult(
                        agent=step.agent, status="success", output=result
                    )
                finished_at = utc_now_iso()
                step_result = StepResult.from_agent_result(
                    step_id=step.id,
                    dependencies=step.depends_on,
                    result=result,
                    started_at=run_started,
                    finished_at=finished_at,
                    thread_name=thread_name,
                )
                return step_result
            except Exception as exc:  # noqa: BLE001
                finished_at = utc_now_iso()
                error_text = "".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__)
                )
                trace_record = AgentTrace(
                    agent=step.agent,
                    step_id=step.id,
                    status="failed",
                    started_at=run_started,
                    finished_at=finished_at,
                    duration_ms=iso_duration_ms(run_started, finished_at),
                    thread_name=thread_name,
                    dependencies=list(step.depends_on),
                    error=error_text,
                    metadata={"exception_type": type(exc).__name__},
                )
                return StepResult(
                    step_id=step.id,
                    agent=step.agent,
                    status="failed",
                    error=error_text,
                    started_at=trace_record.started_at,
                    finished_at=trace_record.finished_at,
                    duration_ms=trace_record.duration_ms,
                    thread_name=trace_record.thread_name,
                    dependencies=list(step.depends_on),
                    metadata=trace_record.metadata,
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            in_flight: Dict[Any, str] = {}
            while remaining or in_flight:
                ready = []
                for step in spec.steps:
                    if step.id not in remaining or step.id in scheduled:
                        continue
                    if all(dep in completed for dep in step.depends_on):
                        ready.append(step)
                while ready and len(in_flight) < max_workers:
                    step = ready.pop(0)
                    scheduled.add(step.id)
                    remaining.discard(step.id)
                    future = executor.submit(execute_step, step)
                    in_flight[future] = step.id

                if not in_flight:
                    if remaining:
                        unresolved = ", ".join(sorted(remaining))
                        raise RuntimeError(
                            f"Workflow '{spec.name}' is blocked by unresolved dependencies: {unresolved}"
                        )
                    break

                done, _ = wait(list(in_flight), return_when=FIRST_COMPLETED)
                for future in done:
                    step_id = in_flight.pop(future)
                    step_result = future.result()
                    step_results[step_id] = step_result
                    completed.add(step_id)
                    context.step_results[step_id] = step_result.to_dict()
                    trace.append(
                        {
                            "step_id": step_id,
                            "agent": step_result.agent,
                            "status": step_result.status,
                            "started_at": step_result.started_at,
                            "finished_at": step_result.finished_at,
                            "duration_ms": step_result.duration_ms,
                            "dependencies": list(step_result.dependencies),
                            "thread_name": step_result.thread_name,
                            "error": step_result.error,
                        }
                    )
                    if step_result.status == "failed" and step_result.error:
                        errors.append(
                            f"{step_id}: {step_result.error.splitlines()[-1]}"
                        )

        final_step = spec.steps[-1].id if spec.steps else ""
        output = step_results[final_step].output if final_step in step_results else None
        finished_at = utc_now_iso()
        status = "success" if not errors else "completed_with_errors"
        return WorkflowRunResult(
            workflow_name=spec.name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=max(
                0, int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
            ),
            output=output,
            step_results=step_results,
            trace=trace,
            errors=errors,
        )

    @staticmethod
    def _resolve_agent(
        name: str,
        registry: Mapping[str, AgentBase | Callable[[CampaignContext], AgentResult]],
    ) -> AgentBase | Callable[[CampaignContext], AgentResult] | None:
        if name in registry:
            return registry[name]
        aliases = {
            "analytics": "analytics",
            "compliance": "compliance",
            "memory_lookup": "memory_lookup",
            "optimization": "optimization",
            "execution_planning": "execution_planning",
        }
        alias = aliases.get(name)
        if alias and alias in registry:
            return registry[alias]
        return None
