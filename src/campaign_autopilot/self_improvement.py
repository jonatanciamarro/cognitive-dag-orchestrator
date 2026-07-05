"""Self-Improvement Engine — AG-Kit Evolution Phase 17.

The system diagnoses its own bottlenecks, generates patches,
tests them on the Digital Twin, and produces deployment plans.

Workflow:
  EvaluationEngine (score drop)
    ↓
  SelfDiagnosis (root cause)
    ↓
  PatchGenerator (fix candidate)
    ↓
  DigitalTwin (safe test)
    ↓
  PatchDeployer (deployment plan)

Builds on Phases 11-16:
  - ConstraintGraph → violated constraints as diagnosis input
  - WorldModel → predicted impact of patches
  - EconomicEngine → ROI of patches
  - AgentEvolutionEngine → agent genome patches
  - DigitalTwin → safe patch testing

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - Patches are data (dicts), not code — no code generation
  - DigitalTwin validates before any patch is deployed
  - SafeDeployer generates plans, does NOT auto-deploy
  - Thread-safe
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


class DiagnosisSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class PatchType(Enum):
    CONSTRAINT_TWEAK = "constraint_tweak"
    AGENT_MUTATION = "agent_mutation"
    WORKFLOW_CHANGE = "workflow_change"
    CONFIG_CHANGE = "config_change"
    STRATEGY_CHANGE = "strategy_change"
    CHANNEL_ACTION = "channel_action"


class PatchStatus(Enum):
    PROPOSED = "proposed"
    TESTING = "testing"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


# ── Diagnosis Models ──────────────────────────────────────────


@dataclass
class Finding:
    """A single finding from system diagnosis."""

    finding_id: str
    category: str  # "performance", "quality", "constraint", "revenue", "evolution"
    severity: DiagnosisSeverity
    description: str
    metric: str = ""  # affected metric
    current_value: float = 0.0
    target_value: float = 0.0
    gap: float = 0.0
    source: str = ""  # which module detected this
    timestamp: float = 0.0
    details: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "category": self.category,
            "severity": self.severity.value,
            "description": self.description,
            "metric": self.metric,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "gap": self.gap,
            "source": self.source,
            "timestamp": self.timestamp,
            "details": dict(self.details),
        }


@dataclass
class DiagnosisReport:
    """Complete diagnosis of the system's health."""

    report_id: str
    timestamp: float
    findings: list[Finding] = field(default_factory=list)

    def critical(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == DiagnosisSeverity.CRITICAL]

    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == DiagnosisSeverity.WARNING]

    def by_category(self) -> dict[str, list[Finding]]:
        cats: dict[str, list[Finding]] = {}
        for f in self.findings:
            cats.setdefault(f.category, []).append(f)
        return cats

    def score(self) -> float:
        """Health score 0.0 (bad) to 1.0 (perfect)."""
        if not self.findings:
            return 1.0
        penalties = {
            DiagnosisSeverity.INFO: 0.05,
            DiagnosisSeverity.WARNING: 0.15,
            DiagnosisSeverity.CRITICAL: 0.35,
        }
        penalty = sum(penalties.get(f.severity, 0.1) for f in self.findings)
        return max(0.0, min(1.0, 1.0 - penalty))

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "score": self.score(),
            "total_findings": len(self.findings),
            "critical_count": len(self.critical()),
            "warning_count": len(self.warnings()),
            "findings": [f.to_dict() for f in self.findings],
        }


# ── Patch Models ──────────────────────────────────────────────


@dataclass
class Patch:
    """A single patch (change) proposed by the self-improvement engine.

    Patches are data — they describe WHAT to change, not HOW.
    The actual application is done by the deployer.
    """

    patch_id: str
    patch_type: PatchType
    target: str  # what to change (constraint_id, agent_id, config_key)
    description: str
    old_value: Any = None
    new_value: Any = None
    reasoning: str = ""

    # Scoring
    estimated_impact: float = 0.0  # -1.0 to 1.0 (negative = harmful)
    confidence: float = 0.5  # 0.0 to 1.0
    complexity: str = "low"  # low, medium, high

    # Status
    status: PatchStatus = PatchStatus.PROPOSED
    digital_twin_result: dict = field(default_factory=dict)
    deployed_at: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["patch_type"] = self.patch_type.value
        d["status"] = self.status.value
        return d


@dataclass
class ImprovementPlan:
    """A plan consisting of multiple patches, ready for Digital Twin testing."""

    plan_id: str
    patches: list[Patch] = field(default_factory=list)
    created_at: float = 0.0
    expected_revenue_lift: float = 0.0
    expected_cost_reduction: float = 0.0
    risk_score: float = 0.5

    def add(self, patch: Patch) -> None:
        self.patches.append(patch)

    def estimated_impact(self) -> float:
        if not self.patches:
            return 0.0
        return sum(p.estimated_impact * p.confidence for p in self.patches) / len(
            self.patches
        )

    def complexity(self) -> str:
        complexities = {"low": 0, "medium": 1, "high": 2}
        avg = sum(complexities.get(p.complexity, 0) for p in self.patches) / max(
            len(self.patches), 1
        )
        if avg <= 0.5:
            return "low"
        elif avg <= 1.5:
            return "medium"
        return "high"

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "patch_count": len(self.patches),
            "created_at": self.created_at,
            "estimated_impact": self.estimated_impact(),
            "complexity": self.complexity(),
            "patches": [p.to_dict() for p in self.patches],
        }


# ── Self Diagnosis ────────────────────────────────────────────


class SelfDiagnosis:
    """Diagnoses the system health by analyzing multiple data sources.

    Sources:
      - ConstraintGraph: violated constraints → findings
      - Agent traces: error rates, latency → findings
      - Economic metrics: low ROI channels → findings
      - Evolution metrics: stagnation → finding
    """

    def __init__(self) -> None:
        self._detectors: list[Callable[[], list[Finding]]] = []
        self._lock = threading.Lock()

    def register_detector(self, fn: Callable[[], list[Finding]]) -> None:
        """Register a custom detector function."""
        with self._lock:
            self._detectors.append(fn)

    def diagnose(
        self,
        constraint_graph: Any | None = None,
        economic_engine: Any | None = None,
        evolution_engine: Any | None = None,
        world_model: Any | None = None,
    ) -> DiagnosisReport:
        """Run full system diagnosis. Returns a report."""
        report = DiagnosisReport(
            report_id=uuid.uuid4().hex[:12],
            timestamp=time.time(),
        )

        # 1. Check constraints
        if constraint_graph:
            for node in constraint_graph.violated():
                report.findings.append(
                    Finding(
                        finding_id=f"constraint_{node.id}",
                        category="constraint",
                        severity=(
                            DiagnosisSeverity.CRITICAL
                            if node.severity.value == "critical"
                            else DiagnosisSeverity.WARNING
                        ),
                        description=f"Constraint violated: {node.name}",
                        metric=node.id,
                        current_value=node.current_value or 0,
                        target_value=node.min_value or node.max_value or 0,
                        gap=abs((node.current_value or 0) - (node.min_value or 0)),
                        source="constraint_intelligence",
                    )
                )

        # 2. Check economic health
        if economic_engine:
            portfolio = economic_engine.portfolio()
            if portfolio.overall_roi < 0:
                report.findings.append(
                    Finding(
                        finding_id="negative_overall_roi",
                        category="revenue",
                        severity=DiagnosisSeverity.CRITICAL,
                        description=f"Overall portfolio ROI is negative: {portfolio.overall_roi:.1f}%",
                        metric="portfolio_roi",
                        current_value=portfolio.overall_roi,
                        target_value=10.0,
                        gap=abs(portfolio.overall_roi - 10.0),
                        source="economic_intelligence",
                    )
                )
            if portfolio.diversification_score < 0.3:
                report.findings.append(
                    Finding(
                        finding_id="low_diversification",
                        category="revenue",
                        severity=DiagnosisSeverity.WARNING,
                        description=f"Low channel diversification: {portfolio.diversification_score:.2f}",
                        metric="diversification",
                        current_value=portfolio.diversification_score,
                        target_value=0.6,
                        gap=0.6 - portfolio.diversification_score,
                        source="economic_intelligence",
                    )
                )

        # 3. Check evolution health
        if evolution_engine:
            pop = evolution_engine.population()
            scored = [g for g in pop if g.evaluation_count > 0]
            if scored:
                avg_fitness = sum(g.fitness_score for g in scored) / len(scored)
                if avg_fitness < 0.3:
                    report.findings.append(
                        Finding(
                            finding_id="low_avg_fitness",
                            category="evolution",
                            severity=DiagnosisSeverity.WARNING,
                            description=f"Low average agent fitness: {avg_fitness:.2f}",
                            metric="avg_fitness",
                            current_value=avg_fitness,
                            target_value=0.5,
                            gap=0.5 - avg_fitness,
                            source="agent_evolution",
                        )
                    )
                best = max(scored, key=lambda g: g.fitness_score)
                if best.fitness_score < 0.4:
                    report.findings.append(
                        Finding(
                            finding_id="no_high_performer",
                            category="evolution",
                            severity=DiagnosisSeverity.CRITICAL,
                            description=f"No high-performing agents. Best fitness: {best.fitness_score:.2f}",
                            metric="best_fitness",
                            current_value=best.fitness_score,
                            target_value=0.7,
                            gap=0.7 - best.fitness_score,
                            source="agent_evolution",
                        )
                    )

        # 4. Check world model health
        if world_model:
            report_data = getattr(world_model, "report", lambda: {})()
            metrics = report_data.get("metrics", {})
            low_conf_metrics = [
                m
                for m, d in metrics.items()
                if d.get("predict_next", {}).get("confidence") == "insufficient"
            ]
            if low_conf_metrics:
                report.findings.append(
                    Finding(
                        finding_id="insufficient_data",
                        category="performance",
                        severity=DiagnosisSeverity.WARNING,
                        description=f"Insufficient data for {len(low_conf_metrics)} metrics",
                        metric="low_confidence_count",
                        current_value=len(low_conf_metrics),
                        target_value=0,
                        gap=len(low_conf_metrics),
                        source="world_model",
                        details={"metrics": low_conf_metrics},
                    )
                )

        # 5. Custom detectors
        for detector in self._detectors:
            try:
                report.findings.extend(detector())
            except Exception:
                continue

        return report

    def suggest_patches(self, report: DiagnosisReport) -> ImprovementPlan:
        """Convert findings into concrete patches."""
        plan = ImprovementPlan(
            plan_id=uuid.uuid4().hex[:12],
            created_at=time.time(),
        )

        for finding in report.findings:
            patch = self._finding_to_patch(finding)
            if patch:
                plan.add(patch)

        return plan

    def _finding_to_patch(self, finding: Finding) -> Patch | None:
        """Convert a single finding to a patch."""
        finding_id = finding.finding_id

        # Constraint violation → relax threshold or suggest fix
        if finding.category == "constraint":
            if "_min" in finding_id:
                return Patch(
                    patch_id=f"fix_{finding_id}",
                    patch_type=PatchType.CONSTRAINT_TWEAK,
                    target=finding_id.replace("constraint_", ""),
                    description="Relax minimum threshold based on actual performance",
                    old_value=finding.target_value,
                    new_value=round(finding.current_value * 0.85, 2),
                    reasoning="Metric is consistently below min threshold. Relaxing by 15%.",
                    estimated_impact=0.3,
                    confidence=0.6,
                )
            elif "_max" in finding_id:
                return Patch(
                    patch_id=f"fix_{finding_id}",
                    patch_type=PatchType.CONSTRAINT_TWEAK,
                    target=finding_id.replace("constraint_", ""),
                    description="Increase maximum threshold",
                    old_value=finding.target_value,
                    new_value=round(finding.current_value * 1.15, 2),
                    reasoning="Metric consistently exceeds max threshold. Increasing by 15%.",
                    estimated_impact=0.2,
                    confidence=0.5,
                )

        # Low diversification → suggest new channel
        if (
            finding.metric == "diversification"
            and finding.severity == DiagnosisSeverity.WARNING
        ):
            return Patch(
                patch_id="add_new_channel",
                patch_type=PatchType.CHANNEL_ACTION,
                target="portfolio",
                description="Add a new channel to improve diversification",
                old_value=None,
                new_value="new_channel",
                reasoning=f"Diversification score {finding.current_value:.2f} is below 0.3. "
                f"Adding a new channel would reduce dependency risk.",
                estimated_impact=0.4,
                confidence=0.5,
                complexity="medium",
            )

        # Low agent fitness → suggest evolution
        if finding.category == "evolution":
            return Patch(
                patch_id=f"evolve_{finding_id}",
                patch_type=PatchType.AGENT_MUTATION,
                target="population",
                description="Run evolution cycle to improve agent fitness",
                old_value=finding.current_value,
                new_value=min(finding.current_value * 1.3, 1.0),
                reasoning=f"Agent fitness ({finding.current_value:.2f}) below target. "
                f"Running evolution cycle should improve it.",
                estimated_impact=0.5,
                confidence=0.6,
                complexity="medium",
            )

        # Insufficient data → suggest more data collection
        if finding.metric == "low_confidence_count":
            return Patch(
                patch_id="increase_data_collection",
                patch_type=PatchType.CONFIG_CHANGE,
                target="world_model",
                description="Increase data collection frequency for low-confidence metrics",
                old_value=None,
                new_value={"collection_interval_hours": 1},
                reasoning=f"{finding.current_value:.0f} metrics have insufficient data. "
                f"Increasing collection frequency.",
                estimated_impact=0.2,
                confidence=0.7,
            )

        return None


# ── Self-Improvement Engine (Orchestrator) ────────────────────


class SelfImprovementEngine:
    """Main self-improvement engine.

    Coordinates diagnosis, patching, Digital Twin testing, and deployment.
    Full cycle:
      1. diagnose() — find problems
      2. suggest_patches() — generate fixes
      3. plan = create_improvement_plan() — combine patches
      4. digital_twin.full_cycle() — test on twin
      5. if approved → deployer creates deployment plan
    """

    def __init__(self, digital_twin: Any | None = None) -> None:
        self.diagnosis = SelfDiagnosis()
        self._digital_twin = digital_twin
        self._plans: list[ImprovementPlan] = []
        self._history: list[dict] = []
        self._lock = threading.Lock()

    def set_digital_twin(self, twin: Any) -> None:
        self._digital_twin = twin

    def diagnose(self, **kwargs: Any) -> DiagnosisReport:
        """Run system diagnosis."""
        return self.diagnosis.diagnose(**kwargs)

    def suggest_patches(self, report: DiagnosisReport) -> ImprovementPlan:
        """Generate patches from diagnosis."""
        return self.diagnosis.suggest_patches(report)

    def create_improvement_plan(
        self, patches: list[Patch], description: str = ""
    ) -> ImprovementPlan:
        """Create a structured improvement plan from patches."""
        plan = ImprovementPlan(
            plan_id=uuid.uuid4().hex[:12],
            patches=patches,
            created_at=time.time(),
        )
        with self._lock:
            self._plans.append(plan)
        return plan

    def run_cycle(self, **diagnosis_kwargs: Any) -> dict:
        """Run a complete self-improvement cycle.

        Returns full result including diagnosis, patches, twin test, and plan.
        """
        # 1. Diagnose
        report = self.diagnose(**diagnosis_kwargs)
        health_score = report.score()

        # 2. Generate patches if needed
        plan = (
            self.suggest_patches(report)
            if health_score < 0.8
            else ImprovementPlan(plan_id=uuid.uuid4().hex[:12], created_at=time.time())
        )
        with self._lock:
            self._plans.append(plan)

        # 3. Test on Digital Twin if available and we have patches
        twin_result = None
        if self._digital_twin and plan.patches:
            try:
                # Create experiment input from patches
                agent_mutations = {}
                constraint_changes = {}
                new_channels = []

                for p in plan.patches:
                    if p.patch_type == PatchType.AGENT_MUTATION:
                        agent_mutations[p.target] = {"fitness_score": p.new_value}
                    elif p.patch_type == PatchType.CONSTRAINT_TWEAK:
                        constraint_changes[p.target] = p.new_value
                    elif p.patch_type == PatchType.CHANNEL_ACTION:
                        new_channels.append(str(p.new_value))

                result = self._digital_twin.full_cycle(
                    snapshot_kwargs={"description": "Pre-improvement baseline"},
                    experiment_kwargs={
                        "agent_mutations": agent_mutations if agent_mutations else None,
                        "constraint_changes": constraint_changes
                        if constraint_changes
                        else None,
                        "new_channels": new_channels if new_channels else None,
                    },
                )
                twin_result = {
                    "experiment": result["experiment"].to_dict(),
                    "validation": result["validation"].to_dict(),
                    "approved": result["validation"].approved(),
                    "plan_created": result["plan"] is not None,
                }

                # Mark patches based on twin result
                if result["validation"].approved():
                    for p in plan.patches:
                        p.status = PatchStatus.APPROVED
                else:
                    for p in plan.patches:
                        p.status = PatchStatus.REJECTED

            except Exception as e:
                twin_result = {"error": str(e)}

        # 4. Record cycle
        cycle = {
            "timestamp": time.time(),
            "health_score": health_score,
            "findings_count": len(report.findings),
            "patches_proposed": len(plan.patches),
            "twin_result": twin_result,
        }
        with self._lock:
            self._history.append(cycle)

        return {
            "diagnosis": report.to_dict(),
            "improvement_plan": plan.to_dict(),
            "twin_result": twin_result,
            "cycle": cycle,
        }

    def history(self, n: int = 5) -> list[dict]:
        return sorted(self._history, key=lambda h: -h["timestamp"])[:n]

    def report(self) -> dict:
        recent = self.history(3)
        avg_health = (
            sum(h["health_score"] for h in recent) / max(len(recent), 1)
            if recent
            else 1.0
        )
        total_patches = sum(h["patches_proposed"] for h in self._history)
        return {
            "cycles_run": len(self._history),
            "current_health": round(avg_health, 3),
            "total_patches_proposed": total_patches,
            "recent_cycles": recent,
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Demonstrate the Self-Improvement Engine."""
    sie = SelfImprovementEngine()

    # Simulate a system with problems
    class MockConstraintGraph:
        def violated(self):
            n = type(
                "N",
                (),
                {
                    "id": "cpa_max_limit",
                    "name": "CPA exceeded",
                    "severity": type("S", (), {"value": "error"})(),
                    "current_value": 75,
                    "min_value": None,
                    "max_value": 50,
                },
            )()
            return [n]

    class MockEconomicEngine:
        def portfolio(self):
            p = type(
                "P",
                (),
                {
                    "overall_roi": -5.0,
                    "diversification_score": 0.15,
                    "total_revenue": 10000,
                    "total_cost": 10500,
                },
            )()
            return p

    class MockEvolutionEngine:
        def population(self):
            g = type(
                "G",
                (),
                {"agent_id": "seo_v1", "fitness_score": 0.25, "evaluation_count": 5},
            )()
            return [g]

    print("=== Self-Improvement Engine — Demo ===")
    print()

    # Run diagnosis with simulated problems
    report = sie.diagnose(
        constraint_graph=MockConstraintGraph(),
        economic_engine=MockEconomicEngine(),
        evolution_engine=MockEvolutionEngine(),
    )
    print(
        f"Diagnosis: {len(report.findings)} findings, "
        f"health score: {report.score():.2f}"
    )
    for f in report.findings:
        print(f"  [{f.severity.value}] {f.category}: {f.description}")

    # Run full improvement cycle
    print("\nRunning full improvement cycle...")
    result = sie.run_cycle(
        constraint_graph=MockConstraintGraph(),
        economic_engine=MockEconomicEngine(),
        evolution_engine=MockEvolutionEngine(),
    )
    plan = result["improvement_plan"]
    print(f"Patches proposed: {len(plan['patches'])}")
    for p in plan["patches"]:
        print(f"  [{p['patch_type']}] {p['description']}")
        print(
            f"    Impact: {p['estimated_impact']:.1f}, "
            f"Confidence: {p['confidence']:.1f}, "
            f"Status: {p['status']}"
        )

    print("\nEngine report:")
    print(json.dumps(sie.report(), indent=2))


if __name__ == "__main__":
    demo()
