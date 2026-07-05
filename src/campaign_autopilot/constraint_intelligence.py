"""Constraint Intelligence Layer — AG-Kit Evolution Phase 11.

Explicitly models the constraints that govern reality.

Instead of implicit constraints scattered across policy.py, compliance.py,
and governance modules, this module provides a unified ConstraintGraph
that can be queried, visualized, and used to dynamically reconfigure workflows.

Phase 11 of AG-Kit Evolution:
  Today:  implicit constraints → runtime errors
  Future: explicit ConstraintGraph → dynamic workflow adaptation

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - Wraps existing constraint logic from policy.py, compliance.py, governance/
  - Does NOT replace existing modules — adds a queryable layer on top
  - Thread-safe with threading.Lock
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable


# ── Types ─────────────────────────────────────────────────────


class ConstraintType(Enum):
    THRESHOLD = "threshold"  # value must stay above/below limit
    BOOLEAN = "boolean"  # must be true/false
    RANGE = "range"  # value must be within range
    RATE = "rate"  # rate of change must not exceed
    DEPENDENCY = "dependency"  # depends on another constraint
    COMPLIANCE = "compliance"  # regulatory/policy constraint
    RESOURCE = "resource"  # budget, API calls, time
    QUALITY = "quality"  # output quality benchmarks


class ConstraintSeverity(Enum):
    INFO = "info"  # notification only
    WARNING = "warning"  # should address
    ERROR = "error"  # must resolve
    CRITICAL = "critical"  # system halt


class ConstraintStatus(Enum):
    ACTIVE = "active"  # currently enforced
    VIOLATED = "violated"  # currently breached
    PAUSED = "paused"  # temporarily suspended
    RESOLVED = "resolved"  # was violated, now fixed
    OBSOLETE = "obsolete"  # no longer relevant


# ── Domain Models ─────────────────────────────────────────────


@dataclass
class CausalLink:
    """Links a constraint to outcomes it affects."""

    target_id: str  # affected constraint or metric
    relationship: str  # "amplifies", "mitigates", "causes", "correlates"
    strength: float = 0.5  # 0.0 to 1.0
    lag_hours: int = 0  # time delay for effect to appear

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConstraintNode:
    """A single constraint in the graph."""

    id: str
    name: str
    type: ConstraintType
    severity: ConstraintSeverity
    description: str

    # Current state
    current_value: float | bool | None = None
    status: ConstraintStatus = ConstraintStatus.ACTIVE
    last_checked: float = 0.0
    last_violated: float = 0.0
    violation_count: int = 0

    # Thresholds (for THRESHOLD and RANGE types)
    min_value: float | None = None
    max_value: float | None = None

    # Impact
    impact_fn: str = ""  # "pause_channel", "reduce_budget", "alert", etc.
    causal_links: list[CausalLink] = field(default_factory=list)

    # Metadata
    owner: str = "system"
    source: str = ""  # module that defined this constraint
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self) -> None:
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def evaluate(self, value: float | bool) -> ConstraintStatus:
        """Evaluate a value against this constraint. Returns new status."""
        self.current_value = value
        self.last_checked = time.time()
        old_status = self.status

        if self.type == ConstraintType.THRESHOLD:
            if self.min_value is not None and value < self.min_value:
                self.status = ConstraintStatus.VIOLATED
            elif self.max_value is not None and value > self.max_value:
                self.status = ConstraintStatus.VIOLATED
            else:
                self.status = ConstraintStatus.ACTIVE

        elif self.type == ConstraintType.BOOLEAN:
            if isinstance(value, bool):
                self.status = (
                    ConstraintStatus.ACTIVE if value else ConstraintStatus.VIOLATED
                )

        elif self.type == ConstraintType.RANGE:
            lo = self.min_value or float("-inf")
            hi = self.max_value or float("inf")
            self.status = (
                ConstraintStatus.ACTIVE
                if lo <= value <= hi
                else ConstraintStatus.VIOLATED
            )

        elif self.type == ConstraintType.COMPLIANCE:
            self.status = (
                ConstraintStatus.ACTIVE if value else ConstraintStatus.VIOLATED
            )

        else:
            self.status = ConstraintStatus.ACTIVE

        if (
            self.status == ConstraintStatus.VIOLATED
            and old_status != ConstraintStatus.VIOLATED
        ):
            self.last_violated = time.time()
            self.violation_count += 1

        self.updated_at = time.time()
        return self.status

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value
        d["severity"] = self.severity.value
        d["status"] = self.status.value
        d["causal_links"] = [cl.to_dict() for cl in self.causal_links]
        return d


@dataclass
class ConstraintGraph:
    """Graph of all constraints in the system. Queryable and visualizable."""

    nodes: dict[str, ConstraintNode] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def add(self, node: ConstraintNode) -> None:
        with self._lock:
            self.nodes[node.id] = node

    def remove(self, node_id: str) -> None:
        with self._lock:
            self.nodes.pop(node_id, None)

    def get(self, node_id: str) -> ConstraintNode | None:
        return self.nodes.get(node_id)

    def query(self, **filters: Any) -> list[ConstraintNode]:
        """Query constraints by any field. E.g., query(type=ConstraintType.THRESHOLD, status=ConstraintStatus.VIOLATED)"""
        results = list(self.nodes.values())
        for key, value in filters.items():
            results = [n for n in results if getattr(n, key, None) == value]
        return results

    def violated(self) -> list[ConstraintNode]:
        """Return all currently violated constraints."""
        return self.query(status=ConstraintStatus.VIOLATED)

    def active(self) -> list[ConstraintNode]:
        return self.query(status=ConstraintStatus.ACTIVE)

    def by_severity(self, severity: ConstraintSeverity) -> list[ConstraintNode]:
        return self.query(severity=severity)

    def critical(self) -> list[ConstraintNode]:
        """Return all critical constraints (regardless of status)."""
        return self.by_severity(ConstraintSeverity.CRITICAL)

    def snapshot(self) -> dict:
        """Full snapshot of the constraint graph."""
        with self._lock:
            return {
                "total": len(self.nodes),
                "violated": len(self.violated()),
                "by_severity": {
                    s.value: len(self.by_severity(s)) for s in ConstraintSeverity
                },
                "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            }

    def evaluate_all(self, values: dict[str, float | bool]) -> list[dict]:
        """Evaluate multiple constraints at once. Returns list of violations."""
        violations = []
        with self._lock:
            for node_id, value in values.items():
                if node_id in self.nodes:
                    status = self.nodes[node_id].evaluate(value)
                    if status == ConstraintStatus.VIOLATED:
                        violations.append(self.nodes[node_id].to_dict())
        return violations

    def to_json(self, path: str | None = None) -> str:
        """Export the constraint graph as JSON."""
        data = self.snapshot()
        js = json.dumps(data, indent=2, default=str)
        if path:
            with open(path, "w") as f:
                f.write(js)
        return js


# ── Default System Constraints ─────────────────────────────────


def build_default_constraint_graph() -> ConstraintGraph:
    """Build the default set of system constraints.

    These are the constraints currently scattered across policy.py,
    compliance.py, and governance modules — now centralized and queryable.
    """
    g = ConstraintGraph()

    # ── Resource Constraints ──
    g.add(
        ConstraintNode(
            id="api_calls_daily",
            name="Limite de chamadas de API por dia",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.WARNING,
            description="Número de chamadas de API não deve exceder o limite diário",
            max_value=1000,
            min_value=0,
            owner="resource_manager",
            source="governance.resource_manager",
        )
    )
    g.add(
        ConstraintNode(
            id="concurrent_tasks",
            name="Tarefas concorrentes máximas",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.WARNING,
            description="Número de tarefas executando simultaneamente",
            max_value=5,
            min_value=0,
            owner="resource_manager",
            source="governance.resource_manager",
        )
    )

    # ── Quality Constraints ──
    g.add(
        ConstraintNode(
            id="article_min_words",
            name="Tamanho mínimo do artigo",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.ERROR,
            description="Artigos devem ter no mínimo 800 palavras para SEO",
            min_value=800,
            owner="quality_assurance",
            source="governance.quality_assurance",
            causal_links=[CausalLink("seo_traffic", "correlates", strength=0.6)],
        )
    )
    g.add(
        ConstraintNode(
            id="article_min_words_strict",
            name="Tamanho mínimo rigoroso",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.CRITICAL,
            description="Mínimo absoluto de palavras em qualquer conteúdo",
            min_value=300,
            owner="quality_assurance",
            source="governance.quality_assurance",
        )
    )

    # ── Compliance Constraints ──
    g.add(
        ConstraintNode(
            id="opt_in_required",
            name="Opt-in obrigatório para email marketing",
            type=ConstraintType.COMPLIANCE,
            severity=ConstraintSeverity.CRITICAL,
            description="Usuários devem consentir antes de receber emails",
            owner="compliance",
            source="policy.py",
        )
    )
    g.add(
        ConstraintNode(
            id="disclosure_required",
            name="Disclosure de links de afiliado",
            type=ConstraintType.COMPLIANCE,
            severity=ConstraintSeverity.CRITICAL,
            description="Todo conteúdo com links de afiliado deve ter disclosure",
            owner="compliance",
            source="policy.py",
        )
    )
    g.add(
        ConstraintNode(
            id="restricted_terms",
            name="Termos restritos bloqueados",
            type=ConstraintType.COMPLIANCE,
            severity=ConstraintSeverity.ERROR,
            description="Conteúdo não pode conter termos restritos (medicina, finanças, etc.)",
            owner="compliance",
            source="policy.py",
        )
    )

    # ── SEO Constraints ──
    g.add(
        ConstraintNode(
            id="keyword_density_min",
            name="Densidade mínima de keyword",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.WARNING,
            description="Densidade da palavra-chave principal no conteúdo",
            min_value=0.5,
            max_value=3.0,
            owner="seo",
            source="governance.quality_assurance",
            causal_links=[CausalLink("seo_ranking", "correlates", strength=0.4)],
        )
    )
    g.add(
        ConstraintNode(
            id="image_min_width",
            name="Largura mínima de imagem",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.WARNING,
            description="Imagens devem ter largura mínima para qualidade visual",
            min_value=1080,
            owner="media_pipeline",
            source="governance.quality_assurance",
        )
    )

    # ── Revenue Constraints ──
    g.add(
        ConstraintNode(
            id="cpa_max_limit",
            name="Custo por aquisição máximo",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.ERROR,
            description="CPA não deve exceder o limite definido na política",
            max_value=50.0,
            owner="revenue",
            source="metrics.py",
            causal_links=[CausalLink("channel_viability", "determines", strength=0.9)],
        )
    )
    g.add(
        ConstraintNode(
            id="min_sample_size",
            name="Tamanho mínimo de amostra",
            type=ConstraintType.THRESHOLD,
            severity=ConstraintSeverity.ERROR,
            description="Amostra mínima para decisões estatísticas",
            min_value=30,
            owner="revenue",
            source="metrics.py",
        )
    )

    # ── Platform Constraints ──
    g.add(
        ConstraintNode(
            id="organic_only",
            name="Apenas tráfego orgânico",
            type=ConstraintType.BOOLEAN,
            severity=ConstraintSeverity.WARNING,
            description="Modo organic_only: sem tráfego pago",
            owner="policy",
            source="policy.py",
        )
    )

    return g


# ── ConstraintAwareWorkflow ────────────────────────────────────


class ConstraintAwareWorkflow:
    """Wraps a workflow to make it constraint-aware.

    Before executing each step, checks relevant constraints.
    If a critical constraint is violated, the step is skipped.
    """

    def __init__(self, graph: ConstraintGraph | None = None) -> None:
        self.graph = graph or build_default_constraint_graph()
        self._step_constraints: dict[str, list[str]] = {}  # step_id -> [constraint_ids]

    def register_step_constraints(
        self, step_id: str, constraint_ids: list[str]
    ) -> None:
        """Associate constraints with a workflow step."""
        self._step_constraints[step_id] = constraint_ids

    def check_step(self, step_id: str, values: dict[str, float | bool]) -> list[dict]:
        """Check constraints for a step before execution. Returns violations."""
        cids = self._step_constraints.get(step_id, [])
        relevant = {
            cid: values.get(cid)
            for cid in cids
            if cid in values and cid in self.graph.nodes
        }
        violations = []
        for cid, val in relevant.items():
            node = self.graph.get(cid)
            if node and val is not None:
                status = node.evaluate(val)
                if status == ConstraintStatus.VIOLATED:
                    violations.append(node.to_dict())
        return violations

    def can_execute(
        self, step_id: str, values: dict[str, float | bool]
    ) -> tuple[bool, list[dict]]:
        """Returns (can_execute, violations). Blocks if CRITICAL or ERROR violated."""
        violations = self.check_step(step_id, values)
        for v in violations:
            sev = v.get("severity", "warning")
            if sev in ("critical", "error"):
                return False, violations
        return True, violations


# ── ConstraintDetector ─────────────────────────────────────────


class ConstraintDetector:
    """Monitors external signals and detects constraint changes.

    Runs in background (call check() periodically) or on-demand.
    """

    def __init__(self, graph: ConstraintGraph) -> None:
        self.graph = graph
        self._detectors: dict[str, Callable[[], Any]] = {}

    def register(self, constraint_id: str, detector_fn: Callable[[], Any]) -> None:
        """Register a function that checks this constraint's current value."""
        self._detectors[constraint_id] = detector_fn

    def check_all(self) -> list[dict]:
        """Run all registered detectors. Returns violations found."""
        violations = []
        for cid, fn in self._detectors.items():
            try:
                value = fn()
                node = self.graph.get(cid)
                if node:
                    status = node.evaluate(value)
                    if status == ConstraintStatus.VIOLATED:
                        violations.append(node.to_dict())
            except Exception:
                continue
        return violations

    def check_one(self, constraint_id: str) -> dict | None:
        """Run a single detector. Returns violation or None."""
        fn = self._detectors.get(constraint_id)
        if not fn:
            return None
        try:
            value = fn()
            node = self.graph.get(constraint_id)
            if node:
                status = node.evaluate(value)
                if status == ConstraintStatus.VIOLATED:
                    return node.to_dict()
        except Exception:
            pass
        return None


# ── Quick Diagnostic ───────────────────────────────────────────


def diagnose(graph: ConstraintGraph | None = None) -> dict:
    """Quick diagnostic of the constraint system."""
    g = graph or build_default_constraint_graph()
    snap = g.snapshot()
    snap["by_status"] = {s.value: len(g.query(status=s)) for s in ConstraintStatus}
    snap["by_type"] = {t.value: len(g.query(type=t)) for t in ConstraintType}
    snap["health"] = "healthy" if len(g.violated()) == 0 else "degraded"
    snap["critical_count"] = len(g.critical())
    return snap


if __name__ == "__main__":
    # Demo
    g = build_default_constraint_graph()
    print("=== Constraint Intelligence Layer ===")
    print(f"Total constraints: {len(g.nodes)}")
    print(f"Critical: {len(g.critical())}")
    print()

    # Simulate evaluation
    violations = g.evaluate_all(
        {
            "article_min_words": 450,
            "cpa_max_limit": 75.0,
            "opt_in_required": False,
        }
    )
    print(f"Violations found: {len(violations)}")
    for v in violations:
        print(f"  ✗ {v['name']} ({v['severity']})")

    print()
    snap = diagnose(g)
    print(f"System health: {snap['health']}")
    print(f"By severity: {snap['by_severity']}")
