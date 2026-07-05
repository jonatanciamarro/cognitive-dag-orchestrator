"""Digital Twin Layer — AG-Kit Evolution Phase 16.

The system creates a sandboxed copy of itself to run experiments
before touching production. Every change is simulated before deployment.

Builds on Phases 11-14:
  - ConstraintGraph → twin constraints
  - WorldModel → twin prediction
  - EconomicEngine → twin allocation
  - AgentEvolutionEngine → twin evolution experiments

Workflow:
  Production → snapshot → Digital Twin → experiment → validate → deploy

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - Snapshot is JSON-serializable (dict-based, no pickle)
  - Experiments are deterministic (seeded RNG)
  - SafeDeployer generates a deployment plan, does NOT auto-deploy
  - Thread-safe, integrates with existing architecture
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


class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


class ValidationVerdict(Enum):
    APPROVED = "approved"  # experiment outperforms baseline
    REJECTED = "rejected"  # experiment underperforms baseline
    INCONCLUSIVE = "inconclusive"  # not enough data to decide
    CONDITIONAL = "conditional"  # approved with caveats


# ── Domain Models ─────────────────────────────────────────────


@dataclass
class SystemSnapshot:
    """Complete, serializable snapshot of the system's configuration and state.

    Captures all layers of the AG-Kit stack at a point in time.
    Can be used to restore or fork the system state.
    """

    snapshot_id: str
    timestamp: float
    description: str = ""

    # Agent genomes (serialized)
    agent_genomes: dict[str, dict] = field(default_factory=dict)

    # Constraint graph (serialized)
    constraint_nodes: dict[str, dict] = field(default_factory=dict)

    # Economic state
    channel_metrics: dict[str, dict] = field(default_factory=dict)
    portfolio_summary: dict = field(default_factory=dict)
    allocation_decisions: list[dict] = field(default_factory=list)

    # World model state
    metric_history: dict[str, dict] = field(default_factory=dict)
    world_model_report: dict = field(default_factory=dict)

    # System configuration
    active_channels: list[str] = field(default_factory=list)
    strategy: str = "balanced"
    config: dict = field(default_factory=dict)

    # Metadata
    parent_snapshot_id: str | None = None
    tags: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls, description: str = "", parent_id: str | None = None
    ) -> SystemSnapshot:
        """Create a new snapshot with a unique ID."""
        return cls(
            snapshot_id=uuid.uuid4().hex[:12],
            timestamp=time.time(),
            description=description,
            parent_snapshot_id=parent_id,
        )

    def age_hours(self) -> float:
        return (time.time() - self.timestamp) / 3600

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> SystemSnapshot:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def summary(self) -> str:
        return (
            f"Snapshot {self.snapshot_id} ({self.description}) — "
            f"{len(self.agent_genomes)} agents, "
            f"{len(self.constraint_nodes)} constraints, "
            f"{len(self.channel_metrics)} channels, "
            f"{self.age_hours():.1f}h old"
        )


@dataclass
class ExperimentResult:
    """Result of running an experiment on the Digital Twin."""

    experiment_id: str
    snapshot_id: str
    description: str
    status: ExperimentStatus
    started_at: float
    finished_at: float = 0.0

    # Changes applied
    mutations_applied: list[dict] = field(default_factory=list)  # what was changed

    # Predicted outcomes
    predicted_revenue: float = 0.0
    predicted_cost: float = 0.0
    predicted_profit: float = 0.0
    predicted_roi: float = 0.0
    predicted_traffic: float = 0.0

    # Comparison with baseline
    revenue_delta_pct: float = 0.0
    profit_delta_pct: float = 0.0
    roi_delta_pct: float = 0.0

    # Metrics
    metrics: dict[str, float] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def duration_ms(self) -> float:
        if self.finished_at <= 0:
            return 0.0
        return (self.finished_at - self.started_at) * 1000

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "snapshot_id": self.snapshot_id,
            "description": self.description,
            "status": self.status.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "mutations_applied": self.mutations_applied,
            "predicted_revenue": self.predicted_revenue,
            "predicted_cost": self.predicted_cost,
            "predicted_profit": self.predicted_profit,
            "predicted_roi": self.predicted_roi,
            "revenue_delta_pct": self.revenue_delta_pct,
            "profit_delta_pct": self.profit_delta_pct,
            "roi_delta_pct": self.roi_delta_pct,
            "metrics": dict(self.metrics),
            "duration_ms": self.duration_ms(),
        }


@dataclass
class ValidationResult:
    """Comparison between baseline and experiment outcomes."""

    experiment_id: str
    verdict: ValidationVerdict
    confidence: str  # high, medium, low
    reasoning: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metrics_delta: dict[str, float] = field(default_factory=dict)

    def approved(self) -> bool:
        return self.verdict == ValidationVerdict.APPROVED

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "verdict": self.verdict.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "risks": self.risks,
            "recommendations": self.recommendations,
            "metrics_delta": dict(self.metrics_delta),
        }


# ── Snapshot Manager ──────────────────────────────────────────


class SnapshotManager:
    """Manages the lifecycle of system snapshots.

    Creates snapshots from live system state, loads/saves them,
    and tracks snapshot lineage (parent → child).
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, SystemSnapshot] = {}
        self._lock = threading.Lock()

    def save(self, snapshot: SystemSnapshot) -> None:
        with self._lock:
            self._snapshots[snapshot.snapshot_id] = snapshot

    def load(self, snapshot_id: str) -> SystemSnapshot | None:
        return self._snapshots.get(snapshot_id)

    def list_all(self) -> list[SystemSnapshot]:
        return list(self._snapshots.values())

    def list_recent(self, n: int = 5) -> list[SystemSnapshot]:
        return sorted(self._snapshots.values(), key=lambda s: -s.timestamp)[:n]

    def lineage(self, snapshot_id: str) -> list[SystemSnapshot]:
        """Trace the parent chain of a snapshot."""
        chain = []
        current = self._snapshots.get(snapshot_id)
        while current:
            chain.append(current)
            current = (
                self._snapshots.get(current.parent_snapshot_id)
                if current.parent_snapshot_id
                else None
            )
        return chain

    def take_snapshot(
        self,
        constraint_graph: Any | None = None,
        agent_genomes: list[Any] | None = None,
        channel_metrics: list[Any] | None = None,
        world_model: Any | None = None,
        strategy: str = "balanced",
        description: str = "",
        parent_id: str | None = None,
    ) -> SystemSnapshot:
        """Create a snapshot from live system components."""
        snap = SystemSnapshot.create(description=description, parent_id=parent_id)
        snap.strategy = strategy

        # Capture constraint graph
        if constraint_graph:
            snap.constraint_nodes = (
                {nid: node.to_dict() for nid, node in constraint_graph.nodes.items()}
                if hasattr(constraint_graph, "nodes")
                else {}
            )

        # Capture agent genomes
        if agent_genomes:
            snap.agent_genomes = {g.agent_id: g.to_dict() for g in agent_genomes}

        # Capture channel metrics
        if channel_metrics:
            snap.channel_metrics = {c.channel: c.to_dict() for c in channel_metrics}

        # Capture world model
        if world_model:
            snap.world_model_report = getattr(world_model, "report", lambda: {})()
            snap.metric_history = (
                {
                    m: h.to_dict()
                    for m, h in getattr(world_model.predictor, "_history", {}).items()
                }
                if hasattr(world_model, "predictor")
                else {}
            )

        self.save(snap)
        return snap


# ── Experiment Runner ─────────────────────────────────────────


class ExperimentRunner:
    """Runs experiments on a Digital Twin (snapshot).

    Applies mutations to the snapshot's genomes/constraints/config,
    then simulates outcomes using WorldModel + EconomicEngine logic.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._results: dict[str, ExperimentResult] = {}

    def run(
        self,
        snapshot: SystemSnapshot,
        description: str = "",
        agent_mutations: dict[str, dict] | None = None,
        constraint_changes: dict[str, float] | None = None,
        channel_budget_changes: dict[str, float] | None = None,
        new_channels: list[str] | None = None,
        strategy_change: str | None = None,
        seed: int = 42,
    ) -> ExperimentResult:
        """Run an experiment on a snapshot.

        Args:
            snapshot: The system state to fork from
            agent_mutations: {agent_id: {field: new_value}}
            constraint_changes: {constraint_id: new_threshold}
            channel_budget_changes: {channel: budget_multiplier}
            new_channels: Channels to simulate adding
            strategy_change: Override strategy
            seed: Random seed for deterministic results
        """
        import random as rng

        rng.seed(seed)

        exp_id = uuid.uuid4().hex[:12]
        result = ExperimentResult(
            experiment_id=exp_id,
            snapshot_id=snapshot.snapshot_id,
            description=description or f"Experiment on {snapshot.snapshot_id}",
            status=ExperimentStatus.RUNNING,
            started_at=time.time(),
        )

        mutations_applied = []

        # 1. Apply agent mutations
        mutated_genomes = dict(snapshot.agent_genomes)
        if agent_mutations:
            for agent_id, changes in agent_mutations.items():
                if agent_id in mutated_genomes:
                    for field, value in changes.items():
                        mutated_genomes[agent_id][field] = value
                    mutations_applied.append(
                        {
                            "type": "agent_mutation",
                            "target": agent_id,
                            "changes": changes,
                        }
                    )
            result.mutations_applied.extend(mutations_applied)

        # 2. Apply constraint changes
        mutated_constraints = dict(snapshot.constraint_nodes)
        if constraint_changes:
            for cid, new_val in constraint_changes.items():
                if cid in mutated_constraints:
                    mutated_constraints[cid]["min_value"] = new_val
                    mutations_applied.append(
                        {
                            "type": "constraint_change",
                            "target": cid,
                            "new_value": new_val,
                        }
                    )
            result.mutations_applied.extend(mutations_applied)

        # 3. Apply channel budget changes
        mutated_channels = dict(snapshot.channel_metrics)
        if channel_budget_changes:
            for ch, mult in channel_budget_changes.items():
                if ch in mutated_channels:
                    old_cost = (
                        mutated_channels[ch].get("cost", 0)
                        if isinstance(mutated_channels[ch], dict)
                        else getattr(mutated_channels[ch], "cost", 0)
                    )
                    if isinstance(mutated_channels[ch], dict):
                        mutated_channels[ch]["cost"] = old_cost * mult
                    mutations_applied.append(
                        {
                            "type": "budget_change",
                            "target": ch,
                            "multiplier": mult,
                        }
                    )
            result.mutations_applied.extend(mutations_applied)

        # 4. Add new channels
        if new_channels:
            for ch in new_channels:
                if ch not in mutated_channels:
                    mutated_channels[ch] = {
                        "channel": ch,
                        "revenue": 0,
                        "cost": 100,
                        "traffic": 0,
                        "conversions": 0,
                        "content_count": 0,
                        "active_days": 1,
                    }
                    mutations_applied.append(
                        {
                            "type": "new_channel",
                            "target": ch,
                        }
                    )
            result.mutations_applied.extend(mutations_applied)

        # 5. Simulate outcomes
        # Calculate baseline
        total_revenue = sum(
            c.get("revenue", 0) if isinstance(c, dict) else getattr(c, "revenue", 0)
            for c in mutated_channels.values()
        )
        total_cost = sum(
            c.get("cost", 0) if isinstance(c, dict) else getattr(c, "cost", 0)
            for c in mutated_channels.values()
        )

        # Simulate growth from agent mutations
        growth_factor = 1.0
        agent_quality = 0.5
        for g in mutated_genomes.values():
            skills = (
                g.get("skills", []) if isinstance(g, dict) else getattr(g, "skills", [])
            )
            agent_quality += len(skills) * 0.02

        if agent_mutations:
            growth_factor += 0.05 * len(agent_mutations)
        if new_channels:
            growth_factor += 0.08 * len(new_channels)
        if strategy_change:
            strategy_mult = {
                "aggressive": 1.2,
                "balanced": 1.0,
                "conservative": 0.85,
                "opportunistic": 1.1,
            }
            growth_factor *= strategy_mult.get(strategy_change, 1.0)

        # Apply constraint changes effect
        constraint_penalty = 1.0
        if constraint_changes:
            for cid, new_val in constraint_changes.items():
                if new_val is not None and new_val < 0.5:
                    constraint_penalty -= 0.05

        # Final prediction
        result.predicted_revenue = round(
            total_revenue * growth_factor * constraint_penalty
            + rng.gauss(0, total_revenue * 0.02),
            2,
        )
        result.predicted_cost = round(total_cost * (1 + growth_factor * 0.1), 2)
        result.predicted_profit = round(
            result.predicted_revenue - result.predicted_cost, 2
        )
        result.predicted_roi = round(
            result.predicted_profit / max(result.predicted_cost, 1) * 100, 2
        )

        # Calculate deltas from baseline
        baseline_revenue = total_revenue
        baseline_cost = total_cost
        result.revenue_delta_pct = round(
            (result.predicted_revenue - baseline_revenue)
            / max(baseline_revenue, 1)
            * 100,
            2,
        )
        result.profit_delta_pct = round(
            (result.predicted_profit - (baseline_revenue - baseline_cost))
            / max(baseline_revenue - baseline_cost, 1)
            * 100,
            2,
        )

        # Additional metrics
        result.metrics = {
            "agent_quality_score": round(agent_quality, 2),
            "constraint_penalty": round(constraint_penalty, 4),
            "growth_factor": round(growth_factor, 4),
            "channel_count": len(mutated_channels),
            "agent_count": len(mutated_genomes),
            "mutation_count": len(mutations_applied),
        }

        result.status = (
            ExperimentStatus.PASSED
            if result.predicted_profit >= 0
            else ExperimentStatus.FAILED
        )
        result.finished_at = time.time()

        with self._lock:
            self._results[exp_id] = result

        return result

    def get_result(self, experiment_id: str) -> ExperimentResult | None:
        return self._results.get(experiment_id)

    def list_results(self) -> list[ExperimentResult]:
        return list(self._results.values())


# ── Validator ─────────────────────────────────────────────────


class ExperimentValidator:
    """Compares experiment results against baseline thresholds.

    Determines if an experiment should be approved for production.
    """

    def __init__(self) -> None:
        self._thresholds = {
            "min_revenue_growth_pct": 5.0,  # need at least 5% revenue lift
            "max_cost_increase_pct": 20.0,  # cost can't increase more than 20%
            "min_profit_growth_pct": 3.0,  # need at least 3% profit lift
            "max_roi_decline_pct": -10.0,  # ROI can't drop more than 10%
        }

    def set_threshold(self, key: str, value: float) -> None:
        self._thresholds[key] = value

    def validate(
        self,
        experiment: ExperimentResult,
        baseline_snapshot: SystemSnapshot | None = None,
    ) -> ValidationResult:
        """Validate experiment results against thresholds."""
        reasoning = []
        risks = []
        recommendations = []
        metrics_delta = {}

        # Revenue check
        rev_delta = experiment.revenue_delta_pct
        metrics_delta["revenue_delta_pct"] = rev_delta
        if rev_delta >= self._thresholds["min_revenue_growth_pct"]:
            reasoning.append(
                f"Revenue growth +{rev_delta:.1f}% meets threshold "
                f"({self._thresholds['min_revenue_growth_pct']:.0f}%)"
            )
        else:
            risks.append(
                f"Revenue growth +{rev_delta:.1f}% below "
                f"{self._thresholds['min_revenue_growth_pct']:.0f}% threshold"
            )
            recommendations.append(
                "Increase mutation intensity or target higher-ROI channels"
            )

        # Cost check
        bl_cost = 0
        if hasattr(baseline_snapshot, "channel_metrics"):
            bl_cost = sum(
                c.get("cost", 0) if isinstance(c, dict) else getattr(c, "cost", 0)
                for c in baseline_snapshot.channel_metrics.values()
            )
        cost_delta = ((experiment.predicted_cost - bl_cost) / max(bl_cost, 1)) * 100
        metrics_delta["cost_delta_pct"] = round(cost_delta, 2)
        if cost_delta <= self._thresholds["max_cost_increase_pct"]:
            reasoning.append(f"Cost increase {cost_delta:.1f}% within threshold")
        else:
            risks.append(
                f"Cost increase {cost_delta:.1f}% exceeds "
                f"{self._thresholds['max_cost_increase_pct']:.0f}% threshold"
            )
            recommendations.append("Optimize cost structure before deploying")

        # Profit check
        profit_delta = experiment.profit_delta_pct
        metrics_delta["profit_delta_pct"] = profit_delta
        if profit_delta >= self._thresholds["min_profit_growth_pct"]:
            reasoning.append(f"Profit growth +{profit_delta:.1f}% meets threshold")
        else:
            risks.append(f"Profit growth +{profit_delta:.1f}% below threshold")
            recommendations.append("Consider different mutation strategy")

        # Determine verdict
        passed_rev = rev_delta >= self._thresholds["min_revenue_growth_pct"]
        passed_cost = cost_delta <= self._thresholds["max_cost_increase_pct"]
        passed_profit = profit_delta >= self._thresholds["min_profit_growth_pct"]

        if passed_rev and passed_profit and passed_cost:
            verdict = ValidationVerdict.APPROVED
            confidence = "high"
            reasoning.append("All thresholds met — experiment approved for production")
        elif passed_profit and (passed_rev or passed_cost):
            verdict = ValidationVerdict.CONDITIONAL
            confidence = "medium"
            reasoning.append("Partial threshold pass — conditional approval")
        elif experiment.status == ExperimentStatus.FAILED:
            verdict = ValidationVerdict.REJECTED
            confidence = "high"
            reasoning.append("Experiment failed — predicted loss")
        else:
            verdict = ValidationVerdict.INCONCLUSIVE
            confidence = "low"
            reasoning.append("Mixed signals — more data needed")

        return ValidationResult(
            experiment_id=experiment.experiment_id,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            risks=risks,
            recommendations=recommendations,
            metrics_delta=metrics_delta,
        )


# ── Safe Deployer ─────────────────────────────────────────────


@dataclass
class DeploymentPlan:
    """A plan for deploying changes validated by the Digital Twin."""

    plan_id: str
    snapshot_id: str
    experiment_id: str
    created_at: float

    # Changes to deploy
    agent_mutations: dict[str, dict] = field(default_factory=dict)
    constraint_changes: dict[str, float] = field(default_factory=dict)
    budget_changes: dict[str, float] = field(default_factory=dict)
    new_channels: list[str] = field(default_factory=list)
    strategy_change: str | None = None

    # Validation
    validation: dict = field(default_factory=dict)
    expected_revenue_lift: float = 0.0
    expected_profit_lift: float = 0.0
    risk_level: str = "medium"

    # Status
    applied: bool = False
    applied_at: float = 0.0
    result_notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class SafeDeployer:
    """Generates deployment plans from validated experiments.

    Does NOT auto-deploy — generates a plan for human (or external CI) review.
    """

    def __init__(self) -> None:
        self._plans: dict[str, DeploymentPlan] = {}
        self._lock = threading.Lock()

    def create_plan(
        self,
        experiment: ExperimentResult,
        validation: ValidationResult,
        snapshot: SystemSnapshot,
    ) -> DeploymentPlan:
        """Create a deployment plan from a validated experiment."""
        plan = DeploymentPlan(
            plan_id=uuid.uuid4().hex[:12],
            snapshot_id=snapshot.snapshot_id,
            experiment_id=experiment.experiment_id,
            created_at=time.time(),
            expected_revenue_lift=experiment.revenue_delta_pct,
            expected_profit_lift=experiment.profit_delta_pct,
            validation=validation.to_dict(),
            risk_level="low" if validation.approved() else "medium",
        )

        # Extract deployable changes from experiment mutations
        for mutation in experiment.mutations_applied:
            mtype = mutation.get("type", "")
            target = mutation.get("target", "")
            if mtype == "agent_mutation":
                plan.agent_mutations[target] = mutation.get("changes", {})
            elif mtype == "constraint_change":
                plan.constraint_changes[target] = mutation.get("new_value", 0)
            elif mtype == "budget_change":
                plan.budget_changes[target] = mutation.get("multiplier", 1.0)
            elif mtype == "new_channel":
                plan.new_channels.append(target)

        # Strategy change
        plan.strategy_change = snapshot.strategy

        with self._lock:
            self._plans[plan.plan_id] = plan

        return plan

    def mark_applied(self, plan_id: str, notes: str = "") -> bool:
        with self._lock:
            plan = self._plans.get(plan_id)
            if plan and not plan.applied:
                plan.applied = True
                plan.applied_at = time.time()
                plan.result_notes = notes
                return True
            return False

    def list_plans(self, only_pending: bool = False) -> list[DeploymentPlan]:
        plans = list(self._plans.values())
        if only_pending:
            plans = [p for p in plans if not p.applied]
        return sorted(plans, key=lambda p: -p.created_at)


# ── Digital Twin (Orchestrator) ───────────────────────────────


class DigitalTwin:
    """Main Digital Twin — sandboxed copy of the system.

    Full workflow:
      1. snapshot = twin.take_snapshot(...)
      2. exp = twin.run_experiment(snapshot, mutations={...})
      3. val = twin.validate(exp, snapshot)
      4. if val.approved():
           plan = twin.create_deployment_plan(exp, val, snapshot)
           # plan is reviewed, then applied manually or via CI
    """

    def __init__(self) -> None:
        self.snapshots = SnapshotManager()
        self.experiments = ExperimentRunner()
        self.validator = ExperimentValidator()
        self.deployer = SafeDeployer()
        self._lock = threading.Lock()

    def take_snapshot(self, **kwargs: Any) -> SystemSnapshot:
        """Snapshot the current system state."""
        return self.snapshots.take_snapshot(**kwargs)

    def fork(
        self, snapshot_id: str, description: str = "", **mutations: Any
    ) -> tuple[SystemSnapshot, ExperimentResult]:
        """Fork a snapshot and run an experiment on it.

        This is the main high-level API:
          snapshot, result = twin.fork("snap_abc", agent_mutations={...})
        """
        snapshot = self.snapshots.load(snapshot_id)
        if snapshot is None:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        child = SystemSnapshot.create(
            description=description,
            parent_id=snapshot_id,
        )
        # Copy state from parent
        child.agent_genomes = dict(snapshot.agent_genomes)
        child.constraint_nodes = dict(snapshot.constraint_nodes)
        child.channel_metrics = dict(snapshot.channel_metrics)
        child.portfolio_summary = dict(snapshot.portfolio_summary)
        child.active_channels = list(snapshot.active_channels)
        child.strategy = snapshot.strategy
        self.snapshots.save(child)

        exp = self.experiments.run(
            child,
            description=description,
            **mutations,
        )
        return child, exp

    def run_experiment(
        self, snapshot: SystemSnapshot, **kwargs: Any
    ) -> ExperimentResult:
        """Run an experiment on a snapshot."""
        return self.experiments.run(snapshot, **kwargs)

    def validate(
        self, experiment: ExperimentResult, baseline: SystemSnapshot | None = None
    ) -> ValidationResult:
        """Validate experiment results."""
        return self.validator.validate(experiment, baseline)

    def create_deployment_plan(
        self,
        experiment: ExperimentResult,
        validation: ValidationResult,
        snapshot: SystemSnapshot,
    ) -> DeploymentPlan:
        """Create a deployable plan from a validated experiment."""
        return self.deployer.create_plan(experiment, validation, snapshot)

    def full_cycle(self, snapshot_kwargs: dict, experiment_kwargs: dict) -> dict:
        """Run a complete twin cycle: snapshot → experiment → validate → plan.

        Returns:
            {
                "snapshot": SystemSnapshot,
                "experiment": ExperimentResult,
                "validation": ValidationResult,
                "plan": DeploymentPlan | None,
            }
        """
        snap = self.take_snapshot(**snapshot_kwargs)
        exp = self.run_experiment(snap, **experiment_kwargs)
        val = self.validate(exp, snap)
        plan = self.create_deployment_plan(exp, val, snap) if val.approved() else None
        return {
            "snapshot": snap,
            "experiment": exp,
            "validation": val,
            "plan": plan,
        }

    def report(self) -> dict:
        return {
            "snapshot_count": len(self.snapshots.list_all()),
            "experiment_count": len(self.experiments.list_results()),
            "pending_plans": len(self.deployer.list_plans(only_pending=True)),
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Demonstrate the Digital Twin Layer."""
    twin = DigitalTwin()

    # 1. Take a snapshot
    snap = twin.take_snapshot(
        description="Production baseline — June 2026",
        agent_genomes=[
            type(
                "G",
                (),
                {
                    "agent_id": "seo_v1",
                    "skills": ["seo", "keyword"],
                    "to_dict": lambda self: {
                        "agent_id": "seo_v1",
                        "skills": ["seo", "keyword"],
                    },
                },
            )(),
            type(
                "G",
                (),
                {
                    "agent_id": "content_v1",
                    "skills": ["copywriting", "storytelling"],
                    "to_dict": lambda self: {
                        "agent_id": "content_v1",
                        "skills": ["copywriting", "storytelling"],
                    },
                },
            )(),
        ],
        channel_metrics=[
            type(
                "C",
                (),
                {
                    "channel": "blog",
                    "revenue": 3000,
                    "cost": 500,
                    "to_dict": lambda self: {
                        "channel": "blog",
                        "revenue": 3000,
                        "cost": 500,
                    },
                },
            )(),
            type(
                "C",
                (),
                {
                    "channel": "youtube",
                    "revenue": 5000,
                    "cost": 1200,
                    "to_dict": lambda self: {
                        "channel": "youtube",
                        "revenue": 5000,
                        "cost": 1200,
                    },
                },
            )(),
        ],
        strategy="balanced",
    )
    print("=== Digital Twin Layer — Demo ===")
    print(f"1. Snapshot: {snap.summary()}")
    print(f"   Channels: {', '.join(snap.channel_metrics.keys())}")
    print(f"   Agents: {', '.join(snap.agent_genomes.keys())}")

    # 2. Run experiment: add skills to SEO agent + add Pinterest channel
    print("\n2. Running experiment: add Pinterest + boost SEO agent...")
    snap2, exp = twin.fork(
        snap.snapshot_id,
        description="Experiment: add Pinterest channel + boost SEO skills",
        agent_mutations={
            "seo_v1": {"skills": ["seo", "keyword", "analytics", "content_strategy"]},
        },
        new_channels=["pinterest"],
        channel_budget_changes={"youtube": 1.5},  # 50% more budget
    )
    print(f"   Experiment: {exp.description}")
    print(f"   Status: {exp.status.value}")
    print(
        f"   Predicted revenue: ${exp.predicted_revenue:.0f} "
        f"(delta: {exp.revenue_delta_pct:+.1f}%)"
    )
    print(
        f"   Predicted profit: ${exp.predicted_profit:.0f} "
        f"(delta: {exp.profit_delta_pct:+.1f}%)"
    )

    # 3. Validate
    val = twin.validate(exp, snap)
    print(f"\n3. Validation: {val.verdict.value}")
    for r in val.reasoning:
        print(f"   → {r}")
    if val.risks:
        for r in val.risks:
            print(f"   ⚠ {r}")

    # 4. Create deployment plan if approved
    if val.approved():
        plan = twin.create_deployment_plan(exp, val, snap)
        print(f"\n4. Deployment plan: {plan.plan_id}")
        print(f"   Expected revenue lift: {plan.expected_revenue_lift:+.1f}%")
        print(
            f"   Changes: {len(plan.agent_mutations)} agent mutations, "
            f"{len(plan.new_channels)} new channels"
        )
    else:
        print("\n4. No deployment plan — experiment not approved")

    print(f"\n5. Twin status: {json.dumps(twin.report(), indent=2)}")


if __name__ == "__main__":
    demo()
