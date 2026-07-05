"""Organization-as-Agent — AG-Kit Evolution Phase 19.

The system stops being 99 independent agents and becomes 1 organization.
Agents become departments/cells within the organization, communicating
via the Cognitive Mesh, sharing memory, budget, and strategic objectives.

Architecture:
  Before: Orchestrator coordinates 99 agents
  After:  Organization contains Departments → Cells (agents)
          Unified state, shared memory, strategic objectives
          Cognitive Mesh for internal communication

Builds on Phase 15 (Cognitive Mesh) + all previous phases.

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - OrganizationState is JSON-serializable
  - Departments map to existing agent groups (SEO, Content, Revenue, etc.)
  - OrganizationAgent wraps the system, does NOT replace AgentBase
  - Thread-safe with threading.Lock
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable


# ── Types ─────────────────────────────────────────────────────


class DepartmentRole(Enum):
    CORE = "core"  # essential operations
    SEO = "seo"  # search optimization
    CONTENT = "content"  # content creation
    MEDIA = "media"  # image, video, audio
    REVENUE = "revenue"  # monetization
    PAID_TRAFFIC = "paid_traffic"  # advertising
    SOCIAL = "social"  # social media
    INTELLIGENCE = "intelligence"  # meta-cognition, evolution
    GOVERNANCE = "governance"  # compliance, risk, quality
    RESEARCH = "research"  # future phases


class ObjectiveStatus(Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    BEHIND = "behind"
    AT_RISK = "at_risk"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class OrganizationPhase(Enum):
    SEED = "seed"  # initial setup, few agents
    GROWTH = "growth"  # scaling, adding departments
    MATURE = "mature"  # full operational capability
    SELF_IMPROVING = "self_improving"  # evolution enabled
    AUTONOMOUS = "autonomous"  # full self-governance


# ── Domain Models ─────────────────────────────────────────────


@dataclass
class Objective:
    """A strategic objective for the organization or a department.

    Decomposed from top-level strategy into department OKRs.
    """

    objective_id: str
    title: str
    description: str
    department: str  # which department owns this
    parent_id: str | None = None  # parent objective (for decomposition)

    # Targets
    target_metric: str = ""  # e.g., "revenue", "traffic", "quality_score"
    target_value: float = 0.0
    current_value: float = 0.0
    progress_pct: float = 0.0

    # Timing
    created_at: float = 0.0
    deadline: float = 0.0
    completed_at: float | None = None

    # Status
    status: ObjectiveStatus = ObjectiveStatus.ACTIVE
    priority: int = 1  # 1 (highest) to 5 (lowest)

    # Key Results (OKR format)
    key_results: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = time.time()
        self.update_progress()

    def update_progress(self) -> float:
        if self.target_value != 0:
            self.progress_pct = min(
                100.0, (self.current_value / self.target_value) * 100
            )
        if self.progress_pct >= 100:
            self.status = ObjectiveStatus.ACHIEVED
            self.completed_at = self.completed_at or time.time()
        elif (
            self.progress_pct < 25
            and self.created_at > 0
            and (time.time() - self.created_at) > 86400 * 7
        ):
            self.status = ObjectiveStatus.AT_RISK
        return self.progress_pct

    def to_dict(self) -> dict:
        self.update_progress()
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class Department:
    """A department within the organization — a cluster of agents."""

    department_id: str
    name: str
    role: DepartmentRole
    description: str = ""

    # Agents in this department
    agent_ids: list[str] = field(default_factory=list)

    # Objectives
    objectives: list[str] = field(default_factory=list)  # objective_ids

    # Budget
    allocated_budget: float = 0.0
    spent_budget: float = 0.0

    # Performance
    performance_score: float = 0.5  # 0.0 to 1.0
    last_evaluated: float = 0.0

    def add_agent(self, agent_id: str) -> None:
        if agent_id not in self.agent_ids:
            self.agent_ids.append(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        if agent_id in self.agent_ids:
            self.agent_ids.remove(agent_id)

    def add_objective(self, objective_id: str) -> None:
        if objective_id not in self.objectives:
            self.objectives.append(objective_id)

    def budget_remaining(self) -> float:
        return self.allocated_budget - self.spent_budget

    def to_dict(self) -> dict:
        return {
            "department_id": self.department_id,
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "agent_count": len(self.agent_ids),
            "agents": list(self.agent_ids),
            "objectives": list(self.objectives),
            "allocated_budget": self.allocated_budget,
            "spent_budget": self.spent_budget,
            "budget_remaining": self.budget_remaining(),
            "performance_score": self.performance_score,
        }


@dataclass
class OrganizationState:
    """Single source of truth for the entire organization.

    Captures all departments, objectives, budget, strategy, and phase.
    """

    organization_id: str
    name: str = "Campaign Autopilot"
    phase: OrganizationPhase = OrganizationPhase.GROWTH

    # Structure
    departments: dict[str, Department] = field(default_factory=dict)
    objectives: dict[str, Objective] = field(default_factory=dict)

    # Budget
    total_budget: float = 0.0
    allocated_budget: float = 0.0

    # Strategy
    current_strategy: str = "balanced"
    strategy_description: str = ""

    # Performance
    overall_health: float = 1.0  # 0.0 to 1.0
    last_assessment: float = 0.0

    # Metadata
    created_at: float = 0.0
    version: int = 1

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = time.time()

    def add_department(self, department: Department) -> None:
        self.departments[department.department_id] = department

    def add_objective(self, objective: Objective) -> None:
        self.objectives[objective.objective_id] = objective
        # Link to department
        dept = self.departments.get(objective.department)
        if dept:
            dept.add_objective(objective.objective_id)

    def get_department(self, role: DepartmentRole) -> Department | None:
        for dept in self.departments.values():
            if dept.role == role:
                return dept
        return None

    def overall_progress(self) -> float:
        active = [
            o for o in self.objectives.values() if o.status == ObjectiveStatus.ACTIVE
        ]
        if not active:
            return 100.0
        return sum(o.progress_pct for o in active) / len(active)

    def budget_utilisation(self) -> float:
        if self.total_budget <= 0:
            return 0.0
        return (self.allocated_budget / self.total_budget) * 100

    def to_dict(self) -> dict:
        self.overall_health = self.overall_progress() / 100
        return {
            "organization_id": self.organization_id,
            "name": self.name,
            "phase": self.phase.value,
            "departments": {k: v.to_dict() for k, v in self.departments.items()},
            "objectives": {k: v.to_dict() for k, v in self.objectives.items()},
            "total_budget": self.total_budget,
            "allocated_budget": self.allocated_budget,
            "current_strategy": self.current_strategy,
            "overall_health": self.overall_health,
            "overall_progress": self.overall_progress(),
            "budget_utilisation": self.budget_utilisation(),
            "version": self.version,
        }


# ── Organization Memory ──────────────────────────────────────


class OrganizationMemory:
    """Unified memory across all departments and agents.

    Provides shared read/write access to the organization's collective
    knowledge, accessible via the Cognitive Mesh.
    """

    def __init__(self, cognitive_mesh: Any | None = None) -> None:
        self._data: dict[str, Any] = {}
        self._lock = threading.Lock()
        self.mesh = cognitive_mesh

    def set(self, key: str, value: Any, source: str = "organization") -> None:
        with self._lock:
            self._data[key] = {
                "value": value,
                "source": source,
                "timestamp": time.time(),
            }
        if self.mesh:
            self.mesh.bus.publish(
                self.mesh.bus.create_message(
                    topic="org_memory",
                    sender=source,
                    content={"action": "set", "key": key},
                    msg_type="memory",
                )
            )

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._data.get(key)
            return entry["value"] if entry else None

    def get_with_meta(self, key: str) -> dict | None:
        with self._lock:
            entry = self._data.get(key)
            return dict(entry) if entry else None

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._data.pop(key, None) is not None

    def keys(self, pattern: str | None = None) -> list[str]:
        with self._lock:
            keys = list(self._data.keys())
            if pattern:
                keys = [k for k in keys if pattern in k]
            return keys

    def search(self, query: str) -> list[dict]:
        with self._lock:
            results = []
            for key, entry in self._data.items():
                if (
                    query.lower() in key.lower()
                    or query.lower() in str(entry.get("value", "")).lower()
                ):
                    results.append({"key": key, **entry})
            return results

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "total_entries": len(self._data),
                "keys": list(self._data.keys()),
            }


# ── Department Registry ──────────────────────────────────────


class DepartmentRegistry:
    """Registry of departments and their agents.

    Provides discovery: "which department does agent X belong to?"
    and "what agents are in department Y?"
    """

    def __init__(self, state: OrganizationState) -> None:
        self.state = state
        self._lock = threading.Lock()

    def register_agent(self, agent_id: str, department_id: str) -> bool:
        """Add an agent to a department."""
        dept = self.state.departments.get(department_id)
        if dept is None:
            return False
        dept.add_agent(agent_id)
        return True

    def find_department(self, agent_id: str) -> Department | None:
        """Find which department an agent belongs to."""
        for dept in self.state.departments.values():
            if agent_id in dept.agent_ids:
                return dept
        return None

    def agents_in(self, department_id: str) -> list[str]:
        dept = self.state.departments.get(department_id)
        return list(dept.agent_ids) if dept else []

    def agents_by_role(self, role: DepartmentRole) -> list[str]:
        dept = self.state.get_department(role)
        return list(dept.agent_ids) if dept else []

    def department_of(self, agent_id: str) -> str | None:
        dept = self.find_department(agent_id)
        return dept.name if dept else None

    def all_departments(self) -> list[Department]:
        return list(self.state.departments.values())

    def summary(self) -> dict:
        return {
            "total_departments": len(self.state.departments),
            "agents_by_department": {
                d.name: len(d.agent_ids) for d in self.state.departments.values()
            },
        }


# ── Organization Agent ────────────────────────────────────────


class OrganizationAgent:
    """The organization as a single agent-like entity.

    Wraps the entire system. Has a run() method like AgentBase.
    Delegates to departments via the Cognitive Mesh.

    This is the final abstraction: from outside, it looks like
    one agent. Inside, it's an organization of collaborating agents.
    """

    def __init__(
        self, name: str = "Campaign Autopilot", cognitive_mesh: Any | None = None
    ) -> None:
        self.name = name
        self.mesh = cognitive_mesh

        # Organization state
        self.state = OrganizationState(
            organization_id=uuid.uuid4().hex[:12],
            name=name,
        )
        self.memory = OrganizationMemory(cognitive_mesh)
        self.registry = DepartmentRegistry(self.state)
        self._lock = threading.Lock()

        # Callbacks for department execution
        self._department_executors: dict[str, Callable] = {}

    def register_executor(self, department_id: str, executor: Callable) -> None:
        """Register a function that executes a department's work."""
        self._department_executors[department_id] = executor

    def bootstrap(self) -> None:
        """Create default departments for the organization."""
        for role in DepartmentRole:
            dept = Department(
                department_id=role.value,
                name=role.value.title(),
                role=role,
                description=f"{role.value} department",
                allocated_budget=self.state.total_budget / len(DepartmentRole),
            )
            self.state.add_department(dept)

        # Set phase based on capabilities
        if len(self._department_executors) >= 3:
            self.state.phase = OrganizationPhase.MATURE
        if len(self._department_executors) >= 5:
            self.state.phase = OrganizationPhase.SELF_IMPROVING

    def set_objective(
        self,
        title: str,
        description: str,
        department: str,
        target_metric: str,
        target_value: float,
        current_value: float = 0.0,
        priority: int = 1,
        parent_id: str | None = None,
    ) -> Objective:
        """Set a strategic objective for a department."""
        obj = Objective(
            objective_id=uuid.uuid4().hex[:12],
            title=title,
            description=description,
            department=department,
            target_metric=target_metric,
            target_value=target_value,
            current_value=current_value,
            priority=priority,
            parent_id=parent_id,
        )
        self.state.add_objective(obj)
        return obj

    def run(self, context: Any = None) -> dict:
        """Run the organization: execute all departments.

        Returns aggregated results from all departments.
        """
        results = {}
        for dept_id, executor in self._department_executors.items():
            try:
                dept_result = executor(context)
                results[dept_id] = {
                    "status": "success",
                    "output": dept_result,
                }
            except Exception as e:
                results[dept_id] = {
                    "status": "error",
                    "error": str(e),
                }
        self.state.version += 1
        return {
            "organization": self.name,
            "phase": self.state.phase.value,
            "departments_executed": len(results),
            "results": results,
        }

    def assess_health(self) -> dict:
        """Assess organization health across all dimensions."""
        now = time.time()

        # Department health
        dept_health = {}
        for dept in self.state.departments.values():
            agent_count = len(dept.agent_ids)
            budget_usage = (dept.spent_budget / max(dept.allocated_budget, 1)) * 100
            dept_health[dept.name] = {
                "agent_count": agent_count,
                "budget_usage_pct": round(budget_usage, 1),
                "performance": dept.performance_score,
            }

        # Objective health
        objectives = list(self.state.objectives.values())
        obj_health = {
            "total": len(objectives),
            "achieved": sum(
                1 for o in objectives if o.status == ObjectiveStatus.ACHIEVED
            ),
            "at_risk": sum(
                1 for o in objectives if o.status == ObjectiveStatus.AT_RISK
            ),
            "active": sum(1 for o in objectives if o.status == ObjectiveStatus.ACTIVE),
        }

        # Overall
        overall = self.overall_health()
        self.state.overall_health = overall
        self.state.last_assessment = now

        return {
            "organization": self.name,
            "phase": self.state.phase.value,
            "overall_health": round(overall, 3),
            "departments": dept_health,
            "objectives": obj_health,
            "overall_progress": round(self.state.overall_progress(), 1),
            "budget_utilisation": round(self.state.budget_utilisation(), 1),
        }

    def overall_health(self) -> float:
        """Compute overall organization health 0.0-1.0."""
        # Department performance
        dept_scores = [d.performance_score for d in self.state.departments.values()]
        avg_dept = sum(dept_scores) / max(len(dept_scores), 1)

        # Objective progress
        obj_progress = self.state.overall_progress() / 100

        # Budget health
        budget_health = 1.0 - abs(self.state.budget_utilisation() - 50) / 100

        # Weighted
        return avg_dept * 0.4 + obj_progress * 0.4 + budget_health * 0.2

    def strategic_recommendations(self) -> list[str]:
        """Generate strategic recommendations based on organization health."""
        recs = []
        health = self.assess_health()

        # Check departments with low agent counts
        for name, dept_h in health["departments"].items():
            if dept_h["agent_count"] == 0:
                recs.append(
                    f"Department '{name}' has no agents — assign or create agents"
                )
            if dept_h["budget_usage_pct"] > 90:
                recs.append(
                    f"Department '{name}' is near budget limit — increase allocation"
                )
            if dept_h["performance"] < 0.3:
                recs.append(
                    f"Department '{name}' has low performance — investigate root cause"
                )

        # Check objectives at risk
        if health["objectives"]["at_risk"] > 0:
            recs.append(
                f"{health['objectives']['at_risk']} objectives are at risk — review strategy"
            )

        # Phase transition
        if (
            self.state.phase == OrganizationPhase.GROWTH
            and health["overall_health"] > 0.7
        ):
            recs.append(
                "Organization health is strong — consider maturing to next phase"
            )

        return recs

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.to_dict(),
            "memory": self.memory.snapshot(),
            "registry": self.registry.summary(),
            "department_count": len(self.state.departments),
            "agent_count": sum(
                len(d.agent_ids) for d in self.state.departments.values()
            ),
            "objective_count": len(self.state.objectives),
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Demonstrate the Organization-as-Agent."""
    from campaign_autopilot.cognitive_mesh import CognitiveMesh

    # Create the organization with a mesh
    mesh = CognitiveMesh()
    org = OrganizationAgent("Campaign Autopilot", cognitive_mesh=mesh)

    # Bootstrap default departments
    org.bootstrap()

    # Register agent executors (simulated)
    def run_seo(ctx):
        return {"keywords_found": 50, "opportunities": 12}

    def run_content(ctx):
        return {"articles_generated": 5, "words": 12000}

    def run_revenue(ctx):
        return {"revenue": 3500, "cost": 800, "roi": 4.375}

    org.register_executor("seo", run_seo)
    org.register_executor("content", run_content)
    org.register_executor("revenue", run_revenue)

    # Register agents in departments via mesh
    seo_agent = mesh.create_agent("seo_v1")
    content_agent = mesh.create_agent("content_v1")
    revenue_agent = mesh.create_agent("revenue_v1")

    org.registry.register_agent("seo_v1", "seo")
    org.registry.register_agent("content_v1", "content")
    org.registry.register_agent("revenue_v1", "revenue")

    # Set strategic objectives
    org.set_objective(
        title="Increase organic traffic by 50%",
        description="Grow organic search traffic through content optimization",
        department="seo",
        target_metric="traffic",
        target_value=75000,
    )
    org.set_objective(
        title="Publish 100 high-quality articles",
        description="Scale content production while maintaining quality",
        department="content",
        target_metric="articles",
        target_value=100,
        current_value=45,
    )
    org.set_objective(
        title="Double monthly revenue",
        description="Increase revenue through channel optimization",
        department="revenue",
        target_metric="revenue",
        target_value=20000,
        current_value=8500,
    )

    # Organization memory
    org.memory.set("best_performing_channel", "youtube", source="analytics")
    org.memory.set("top_niche", "marketing_digital", source="seo_research")
    org.memory.set("critical_constraint", "cpa_max_limit", source="governance")

    print("=== Organization-as-Agent — Demo ===")
    print(f"\nOrganization: {org.name}")
    print(f"Phase: {org.state.phase.value}")
    print(f"Departments: {len(org.state.departments)}")

    print("\nDepartments:")
    for dept in org.state.departments.values():
        print(
            f"  {dept.name:15s} agents={len(dept.agent_ids)}  "
            f"budget=${dept.allocated_budget:.0f}  "
            f"objectives={len(dept.objectives)}  "
            f"perf={dept.performance_score:.2f}"
        )

    # Run the organization
    print("\nRunning organization...")
    result = org.run()
    print(f"Departments executed: {result['departments_executed']}")

    # Assess health
    health = org.assess_health()
    print(f"\nOrganization Health: {health['overall_health']:.2f}")
    print(f"Phase: {health['phase']}")
    print(f"Progress: {health['overall_progress']:.1f}%")

    print("\nObjectives:")
    for obj in org.state.objectives.values():
        print(f"  [{obj.status.value:9s}] {obj.title} ({obj.progress_pct:.0f}%)")

    print("\nOrganization Memory:")
    mem_keys = org.memory.keys()
    for k in mem_keys:
        v = org.memory.get(k)
        print(f"  {k} = {v}")

    print("\nStrategic Recommendations:")
    for rec in org.strategic_recommendations():
        print(f"  • {rec}")

    print("\nDepartment Registry:")
    print(json.dumps(org.registry.summary(), indent=4))

    print("\nFull snapshot:")
    snap = org.to_dict()
    print(f"  {snap['name']} — {snap['state']['phase']}")
    print(f"  {snap['department_count']} departments, {snap['agent_count']} agents")


if __name__ == "__main__":
    demo()
