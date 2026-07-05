"""Constraint Genealogy Engine — AG-Kit Evolution Phase 18.

Traces causal genealogies of decisions through the system.

Every decision leaves a trace. When a constraint changes, that change
propagates through the system. This engine captures the complete chain.

Example:
  Google Core Update (June 2026)
    └── Constraint: EEAT requirements tightened
        └── Decision: Increase author authority signals
            ├── Impact: +15% recovery time
            └── Survival: Implemented, still active

Builds on Phase 11 (ConstraintGraph):
  ConstraintNode.causal_links → CausalLink
  GenealogyNode → traces actual propagation

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - Builds on existing CausalLink model from constraint_intelligence
  - Thread-safe with threading.Lock
  - JSON-serializable for storage/export
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


# ── Types ─────────────────────────────────────────────────────


class NodeType(Enum):
    EXTERNAL_EVENT = "external_event"  # algo no mundo real (Google update, lei nova)
    CONSTRAINT_CHANGE = "constraint_change"  # constraint foi criada/modificada/removida
    DECISION = "decision"  # decisão tomada pelo sistema
    ACTION = "action"  # ação executada
    OUTCOME = "outcome"  # resultado observado
    METRIC_SHIFT = "metric_shift"  # mudança em métrica (tráfego, receita)
    LEARNING = "learning"  # lição aprendida
    EVOLUTION = "evolution"  # mutação/evolução de agente


class SurvivalStatus(Enum):
    ACTIVE = "active"  # a genealogia ainda está ativa
    SUPERSEDED = "superseded"  # substituída por outra decisão
    ROLLED_BACK = "rolled_back"  # revertida
    OBSOLETE = "obsolete"  # não mais relevante
    COMPLETED = "completed"  # concluída com sucesso


# ── Domain Models ─────────────────────────────────────────────


@dataclass
class GenealogyNode:
    """A single node in the constraint genealogy tree.

    Each node is one event in a causal chain. Nodes link to parents
    (causes) and children (effects), forming a directed graph.
    """

    node_id: str
    node_type: NodeType
    title: str
    description: str = ""

    # The chain (linked list)
    parent_id: str | None = None  # what caused this
    child_ids: list[str] = field(default_factory=list)  # what this caused

    # Context
    domain: str = ""  # "seo", "revenue", "compliance", etc.
    agent_id: str = ""  # which agent was involved
    workflow_step: str = ""  # which workflow step

    # Values
    old_value: float | str | None = None
    new_value: float | str | None = None
    impact_score: float = 0.0  # -1.0 (negative) to 1.0 (positive)

    # Timing
    occurred_at: float = 0.0
    resolved_at: float | None = None
    duration_hours: float = 0.0

    # Survival
    survival: SurvivalStatus = SurvivalStatus.ACTIVE

    # Metadata
    tags: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)  # data proving this node
    confidence: float = 1.0  # 0.0 to 1.0

    def __post_init__(self) -> None:
        if not self.occurred_at:
            self.occurred_at = time.time()

    def link_to(self, child: GenealogyNode) -> None:
        """Link this node to a child (this caused child)."""
        if child.node_id not in self.child_ids:
            self.child_ids.append(child.node_id)
        child.parent_id = self.node_id

    def age_hours(self) -> float:
        return (time.time() - self.occurred_at) / 3600

    def is_resolved(self) -> bool:
        return self.survival in (
            SurvivalStatus.COMPLETED,
            SurvivalStatus.ROLLED_BACK,
            SurvivalStatus.OBSOLETE,
            SurvivalStatus.SUPERSEDED,
        )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["node_type"] = self.node_type.value
        d["survival"] = self.survival.value
        return d


@dataclass
class GenealogyPath:
    """A complete path through the genealogy tree (cause → effect chain)."""

    path_id: str
    nodes: list[GenealogyNode] = field(default_factory=list)
    root_cause: str = ""  # node_id of the root
    leaf_outcome: str = ""  # node_id of the final outcome
    total_impact: float = 0.0

    def append(self, node: GenealogyNode) -> None:
        self.nodes.append(node)

    def length(self) -> int:
        return len(self.nodes)

    def summary(self) -> str:
        if not self.nodes:
            return "Empty path"
        causes = [n.title for n in self.nodes[:3]]
        if len(self.nodes) > 3:
            causes.append(f"... +{len(self.nodes) - 3} more")
        return " → ".join(causes)

    def to_dict(self) -> dict:
        return {
            "path_id": self.path_id,
            "root_cause": self.root_cause,
            "leaf_outcome": self.leaf_outcome,
            "length": self.length(),
            "total_impact": self.total_impact,
            "nodes": [n.to_dict() for n in self.nodes],
            "summary": self.summary(),
        }


# ── Genealogy Store ───────────────────────────────────────────


class GenealogyStore:
    """In-memory store for genealogy data. Thread-safe.

    Supports:
      - Add nodes and link them
      - Query by type, domain, survival, agent
      - Trace paths from root to leaf
      - Export as JSON
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GenealogyNode] = {}
        self._lock = threading.Lock()

    def add(self, node: GenealogyNode) -> None:
        with self._lock:
            self._nodes[node.node_id] = node

    def add_with_link(self, node: GenealogyNode, parent_id: str | None = None) -> None:
        """Add a node and optionally link it to a parent."""
        if parent_id and parent_id in self._nodes:
            self._nodes[parent_id].link_to(node)
        self.add(node)

    def get(self, node_id: str) -> GenealogyNode | None:
        return self._nodes.get(node_id)

    def query(self, **filters: Any) -> list[GenealogyNode]:
        """Query nodes by fields. Supports node_type, domain, survival, agent_id."""
        results = list(self._nodes.values())
        for key, value in filters.items():
            results = [n for n in results if getattr(n, key, None) == value]
        return results

    def by_type(self, node_type: NodeType) -> list[GenealogyNode]:
        return self.query(node_type=node_type)

    def by_domain(self, domain: str) -> list[GenealogyNode]:
        return self.query(domain=domain)

    def by_survival(self, status: SurvivalStatus) -> list[GenealogyNode]:
        return self.query(survival=status)

    def roots(self) -> list[GenealogyNode]:
        """Nodes with no parent — root causes."""
        return [n for n in self._nodes.values() if n.parent_id is None]

    def leaves(self) -> list[GenealogyNode]:
        """Nodes with no children — final outcomes."""
        return [n for n in self._nodes.values() if not n.child_ids]

    def trace_path(
        self, from_node_id: str, to_node_id: str | None = None
    ) -> GenealogyPath:
        """Trace the path from one node to another (or to the end)."""
        path = GenealogyPath(
            path_id=uuid.uuid4().hex[:12],
        )
        current = self._nodes.get(from_node_id)
        if not current:
            return path

        path.root_cause = from_node_id
        visited = set()
        while current and current.node_id not in visited:
            visited.add(current.node_id)
            path.append(current)

            if to_node_id and current.node_id == to_node_id:
                path.leaf_outcome = to_node_id
                break

            # Follow first child (or stop)
            if current.child_ids:
                next_id = current.child_ids[0]
                current = self._nodes.get(next_id)
            else:
                path.leaf_outcome = current.node_id
                break

        path.total_impact = sum(n.impact_score for n in path.nodes)
        return path

    def trace_all_paths(self) -> list[GenealogyPath]:
        """Trace all root-to-leaf paths."""
        paths = []
        for root in self.roots():
            path = self.trace_path(root.node_id)
            paths.append(path)
        return paths

    def lineage(self, node_id: str) -> list[GenealogyNode]:
        """Trace ancestors (parents) of a node back to root."""
        lineage_nodes = []
        current = self._nodes.get(node_id)
        visited = set()
        while current and current.node_id not in visited:
            visited.add(current.node_id)
            lineage_nodes.append(current)
            if current.parent_id:
                current = self._nodes.get(current.parent_id)
            else:
                break
        return lineage_nodes

    def count(self) -> int:
        return len(self._nodes)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "total_nodes": len(self._nodes),
                "by_type": {t.value: len(self.by_type(t)) for t in NodeType},
                "by_domain": self._count_by("domain"),
                "by_survival": {
                    s.value: len(self.by_survival(s)) for s in SurvivalStatus
                },
                "roots": len(self.roots()),
                "leaves": len(self.leaves()),
                "paths": len(self.trace_all_paths()),
            }

    def _count_by(self, field: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for node in self._nodes.values():
            val = getattr(node, field, "unknown")
            counts[val] = counts.get(val, 0) + 1
        return counts

    def to_json(self, path: str | None = None) -> str:
        data = {
            "snapshot": self.snapshot(),
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
        }
        js = json.dumps(data, indent=2, default=str)
        if path:
            with open(path, "w") as f:
                f.write(js)
        return js


# ── Causal Tracer ─────────────────────────────────────────────


class CausalTracer:
    """Traces impact chains through the genealogy.

    Answers questions like:
      - "What caused the revenue drop in June?"
      - "What was the impact of the Google update?"
      - "Which decisions are still actively affecting us?"
    """

    def __init__(self, store: GenealogyStore) -> None:
        self.store = store

    def find_root_causes(self, outcome_node_id: str) -> list[GenealogyPath]:
        """Find all root causes that led to a specific outcome."""
        outcome = self.store.get(outcome_node_id)
        if not outcome:
            return []

        lineage = self.store.lineage(outcome_node_id)
        if not lineage:
            return []

        root = lineage[-1]  # furthest ancestor
        path = self.store.trace_path(root.node_id, outcome_node_id)
        return [path]

    def find_impact_of(self, event_node_id: str) -> list[GenealogyPath]:
        """Find all impacts (outcomes) of a specific event or decision."""
        event = self.store.get(event_node_id)
        if not event:
            return []

        # Trace all paths from this event to leaves
        paths = []
        if event.child_ids:
            for child_id in event.child_ids:
                path = self.store.trace_path(child_id)
                paths.append(path)
        else:
            # Event is a leaf itself
            path = GenealogyPath(path_id=uuid.uuid4().hex[:12])
            path.append(event)
            paths.append(path)

        return paths

    def active_decisions(self) -> list[GenealogyNode]:
        """All decisions still actively affecting the system."""
        return self.store.query(
            survival=SurvivalStatus.ACTIVE, node_type=NodeType.DECISION
        )

    def timeline(
        self, domain: str | None = None, limit: int = 20
    ) -> list[GenealogyNode]:
        """Get chronological timeline of events."""
        nodes = (
            self.store.by_domain(domain) if domain else list(self.store._nodes.values())
        )
        return sorted(nodes, key=lambda n: -n.occurred_at)[:limit]

    def summarize(self, node_id: str) -> str:
        """Generate a human-readable summary of a node's genealogy."""
        node = self.store.get(node_id)
        if not node:
            return "Node not found."

        # Ancestors (why)
        ancestors = self.store.lineage(node_id)[1:]  # skip self
        cause_chain = (
            " ← ".join(n.title for n in reversed(ancestors))
            if ancestors
            else "root cause"
        )

        # Descendants (impact)
        impacts = self.find_impact_of(node_id)
        impact_summary = (
            ", ".join(p.summary() for p in impacts[:3])
            if impacts
            else "no tracked impacts yet"
        )

        return (
            f"📌 {node.title}\n"
            f"   Type: {node.node_type.value} | Domain: {node.domain}\n"
            f"   Why: {cause_chain}\n"
            f"   Impact: {impact_summary}\n"
            f"   Status: {node.survival.value} | Confidence: {node.confidence:.0%}\n"
            f"   Age: {node.age_hours():.1f}h"
        )


# ── Genealogy Builder ─────────────────────────────────────────


class GenealogyBuilder:
    """Helper to build genealogies from system events.

    Provides factory methods for common node types and chains.
    """

    def __init__(self, store: GenealogyStore) -> None:
        self.store = store
        self._lock = threading.Lock()

    def record_external_event(
        self,
        title: str,
        domain: str,
        description: str = "",
        impact_score: float = 0.0,
        tags: list[str] | None = None,
    ) -> GenealogyNode:
        """Record an external event (Google update, new regulation, etc.)."""
        node = GenealogyNode(
            node_id=self._new_id("ext"),
            node_type=NodeType.EXTERNAL_EVENT,
            title=title,
            description=description,
            domain=domain,
            impact_score=impact_score,
            tags=tags or [domain],
            confidence=0.8,
        )
        self.store.add(node)
        return node

    def record_constraint_change(
        self,
        constraint_id: str,
        title: str,
        domain: str,
        old_value: float | str | None,
        new_value: float | str | None,
        parent_id: str | None = None,
        impact_score: float = 0.0,
    ) -> GenealogyNode:
        """Record a constraint being created, modified, or triggered."""
        node = GenealogyNode(
            node_id=self._new_id("constraint"),
            node_type=NodeType.CONSTRAINT_CHANGE,
            title=title,
            description=f"Constraint {constraint_id}: {old_value} → {new_value}",
            domain=domain,
            old_value=old_value,
            new_value=new_value,
            impact_score=impact_score,
            evidence={"constraint_id": constraint_id},
        )
        self.store.add_with_link(node, parent_id)
        return node

    def record_decision(
        self,
        title: str,
        domain: str,
        agent_id: str = "",
        description: str = "",
        parent_id: str | None = None,
        impact_score: float = 0.0,
        tags: list[str] | None = None,
    ) -> GenealogyNode:
        """Record a system decision."""
        node = GenealogyNode(
            node_id=self._new_id("decision"),
            node_type=NodeType.DECISION,
            title=title,
            description=description,
            domain=domain,
            agent_id=agent_id,
            impact_score=impact_score,
            tags=tags or [],
            confidence=0.9,
        )
        self.store.add_with_link(node, parent_id)
        return node

    def record_outcome(
        self,
        title: str,
        domain: str,
        old_value: float | str | None,
        new_value: float | str | None,
        parent_id: str | None = None,
        impact_score: float = 0.0,
        survival: SurvivalStatus = SurvivalStatus.COMPLETED,
    ) -> GenealogyNode:
        """Record an outcome (result of a decision or action)."""
        node = GenealogyNode(
            node_id=self._new_id("outcome"),
            node_type=NodeType.OUTCOME,
            title=title,
            description=f"{old_value} → {new_value}",
            domain=domain,
            old_value=old_value,
            new_value=new_value,
            impact_score=impact_score,
            survival=survival,
        )
        self.store.add_with_link(node, parent_id)
        return node

    def build_chain(self, nodes: list[dict]) -> list[GenealogyNode]:
        """Build a chain of nodes from a list of descriptions.

        Each dict: {"type": NodeType, "title": str, "domain": str, ...}
        """
        created = []
        prev_id = None
        for nd in nodes:
            ntype = nd.get("type", NodeType.DECISION)
            if ntype == NodeType.EXTERNAL_EVENT:
                node = self.record_external_event(**nd)
            elif ntype == NodeType.CONSTRAINT_CHANGE:
                node = self.record_constraint_change(parent_id=prev_id, **nd)
            elif ntype == NodeType.DECISION:
                node = self.record_decision(parent_id=prev_id, **nd)
            elif ntype == NodeType.OUTCOME:
                node = self.record_outcome(parent_id=prev_id, **nd)
            else:
                node = self.record_decision(parent_id=prev_id, **nd)
            created.append(node)
            prev_id = node.node_id
        return created

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ── Constraint Genealogy Engine (Orchestrator) ────────────────


class ConstraintGenealogy:
    """Main genealogy engine.

    Coordinates the store, tracer, and builder.
    Provides high-level API for recording and querying genealogies.
    """

    def __init__(self) -> None:
        self.store = GenealogyStore()
        self.tracer = CausalTracer(self.store)
        self.builder = GenealogyBuilder(self.store)

    def record(self, **kwargs: Any) -> GenealogyNode:
        """Convenience: auto-detect node type and record."""
        ntype = kwargs.get("node_type", NodeType.DECISION)
        if isinstance(ntype, str):
            ntype = NodeType(ntype)
        kwargs["node_type"] = ntype
        node = GenealogyNode(**kwargs)
        self.store.add(node)
        return node

    def query(self, **filters: Any) -> list[GenealogyNode]:
        return self.store.query(**filters)

    def why(self, outcome_node_id: str) -> list[GenealogyPath]:
        """Answer: why did this happen? (root causes)"""
        return self.tracer.find_root_causes(outcome_node_id)

    def impact(self, event_node_id: str) -> list[GenealogyPath]:
        """Answer: what was the impact? (consequences)"""
        return self.tracer.find_impact_of(event_node_id)

    def timeline(self, domain: str | None = None, limit: int = 20) -> list[dict]:
        return [n.to_dict() for n in self.tracer.timeline(domain, limit)]

    def snapshot(self) -> dict:
        return self.store.snapshot()

    def report(self) -> dict:
        return {
            "genealogy": self.store.snapshot(),
            "active_decisions": len(self.tracer.active_decisions()),
            "recent_events": len(self.tracer.timeline(limit=100)),
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Demonstrate the Constraint Genealogy Engine."""
    g = ConstraintGenealogy()

    # Build a realistic genealogy chain
    google_update = g.builder.record_external_event(
        title="Google Core Update — June 2026",
        domain="seo",
        description="Google rolled out a core algorithm update focused on content quality and EEAT",
        impact_score=-0.4,
        tags=["google", "algorithm", "seo"],
    )

    eeat_change = g.builder.record_constraint_change(
        constraint_id="eeat_requirements",
        title="EEAT requirements tightened",
        domain="seo",
        old_value="standard",
        new_value="strict",
        parent_id=google_update.node_id,
        impact_score=-0.3,
    )

    decision = g.builder.record_decision(
        title="Increase author authority signals",
        domain="content",
        agent_id="seo_research",
        description="Added author bios, credentials, and external endorsements to all articles",
        parent_id=eeat_change.node_id,
        impact_score=0.5,
        tags=["authority", "EEAT"],
    )

    outcome = g.builder.record_outcome(
        title="Recovery time: 45 days",
        domain="seo",
        old_value="unknown",
        new_value="45 days to full recovery",
        parent_id=decision.node_id,
        impact_score=0.3,
    )

    # Add a parallel chain: traffic impact
    traffic_impact = g.builder.record_external_event(
        title="Organic traffic dropped 25%",
        domain="traffic",
        description="Initial traffic loss from the algorithm update",
        impact_score=-0.6,
        tags=["traffic", "drop"],
    )
    # Link it to the chain
    google_update.link_to(traffic_impact)

    revenue_impact = g.builder.record_outcome(
        title="Revenue decline: 15%",
        domain="revenue",
        old_value="stable",
        new_value="-15% month over month",
        parent_id=traffic_impact.node_id,
        impact_score=-0.5,
    )

    # Link decision to mitigate revenue impact
    pivot = g.builder.record_decision(
        title="Shift budget to Pinterest channel",
        domain="revenue",
        agent_id="economic_engine",
        description="Reallocated 30% of SEO budget to Pinterest to compensate for traffic loss",
        parent_id=revenue_impact.node_id,
        impact_score=0.4,
    )

    recovery_outcome = g.builder.record_outcome(
        title="Revenue recovered to 95% of baseline",
        domain="revenue",
        old_value="-15%",
        new_value="-5%",
        parent_id=pivot.node_id,
        impact_score=0.3,
    )

    print("=== Constraint Genealogy Engine — Demo ===")
    print()

    # Timeline
    print("Timeline (most recent first):")
    for node in g.tracer.timeline(limit=10):
        print(
            f"  [{node.node_type.value:17s}] {node.title} ({node.survival.value}) "
            f"impact={node.impact_score:+.1f}"
        )

    print()
    print("Store snapshot:")
    snap = g.snapshot()
    print(f"  Total nodes: {snap['total_nodes']}")
    print(f"  By type: {snap['by_type']}")
    print(f"  By domain: {snap['by_domain']}")
    print(f"  Paths: {snap['paths']}")

    print()
    print("Trace: 'What caused the revenue decline?'")
    paths = g.why(revenue_impact.node_id)
    for p in paths:
        print(f"  Path ({len(p.nodes)} nodes): {p.summary()}")
        print(f"  Total impact: {p.total_impact:+.1f}")

    print()
    print("Trace: 'What was the impact of Google update?'")
    impacts = g.impact(google_update.node_id)
    for p in impacts:
        print(f"  → {p.summary()}")

    print()
    print("Active decisions still affecting system:")
    for d in g.tracer.active_decisions():
        print(
            f"  • {d.title} (age: {d.age_hours():.0f}h, impact: {d.impact_score:+.1f})"
        )

    print()
    print("Summary of Google Update genealogy:")
    print(g.tracer.summarize(google_update.node_id))


if __name__ == "__main__":
    demo()
