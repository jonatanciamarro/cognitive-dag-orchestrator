"""Orchestrator v2 — Closing the loops across all 3 orders.

Extends CampaignOrchestrator with:
- Post-cycle governance (auto-evolution loop)
- Third-order integration
- Adaptive parameter optimization
- Auto-ontology correction
- Auto-goal generation
"""

from __future__ import annotations

import json
from pathlib import Path
import uuid
from typing import Any, Optional

from .agents.base import CampaignContext
from .agents.orchestrator import CampaignOrchestrator
from .agents.meta_orchestrator import MetaOrchestratorAgent
from .agents.evolution_engine import EvolutionEngine
from .agents.agent_factory import AgentFactory
from .agents.circuit_breaker import CircuitBreaker
from .agents.self_healing import SelfHealingAgent
from .agents.third_order_orchestrator import ThirdOrderOrchestrator
from .agents.agent_perf_monitor import AgentPerformanceMonitor
from .agents.strategy_evolution import StrategyEvolutionAgent
from .third_order.epistemic_engine import EpistemicEngine as ThirdOrderEpistemic
from .third_order.value_system import ValueSystemEngine
from .enterprise_kernel import AutonomousEnterpriseKernel
from .quality_layers import (
    OutputCritic,
    DebateOrchestrator,
    BenchmarkDB,
    CampaignKnowledge,
    RAGEngine,
    TruthAgent,
    RiskAgent,
    ConsistencyAgent,
    ELORanking,
)
from .logging_utils import StructuredLogger

log = StructuredLogger("orchestrator_v2")


class OrchestratorV2(CampaignOrchestrator):
    """Enhanced orchestrator with closed loops across all orders.

    Execution cycle:
    1. First Order: Run base workflow (DAG)
    2. First Order: Knowledge synthesis + drift detection
    3. Second Order: Agent performance monitoring
    4. Second Order: Meta-orchestrator (diagnose + prescribe)
    5. Second Order: Strategy evolution (multi-cycle)
    6. Second Order: Self-healing (fix failed agents)
    7. Second Order: Evolution engine (apply prescriptions)
    8. Second Order: Agent factory (fill gaps)
    9. Second Order: Circuit breaker (check health)
    10. Third Order: Epistemic analysis (what we know/don't know)
    11. Third Order: Value system evolution
    12. Third Order: Observer fusion (multiple perspectives)
    13. Third Order: Recursive observation
    14. Third Order: Governance audit
    15. Auto: Adaptive parameter tuning
    16. Auto: Ontology correction
    17. Auto: Goal generation
    """

    def __init__(
        self,
        workflow_path: str | Path | None = None,
        runner=None,
        memory_store=None,
        enable_second_order: bool = True,
        enable_third_order: bool = True,
        enable_auto_evolution: bool = True,
    ):
        super().__init__(
            workflow_path=workflow_path, runner=runner, memory_store=memory_store
        )

    def _check_product_availability(self) -> dict:
        """Pre-flight: verify qualified products exist before content generation."""
        import sqlite3
        db = Path(__file__).resolve().parent.parent.parent / ".state" / "hotmart_intelligence.db"
        cfg = Path(__file__).resolve().parent.parent.parent / "configs" / "affiliate_offers.json"
        available = {"hotmart_db": 0, "config_offers": 0, "status": "ok"}
        if db.exists():
            try:
                conn = sqlite3.connect(str(db))
                count = conn.execute("SELECT COUNT(*) FROM products WHERE status='activated'").fetchone()[0]
                available["hotmart_db"] = count
                conn.close()
            except Exception:
                pass
        if cfg.exists():
            import json
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
                total = sum(len(v) for v in data.get("offers_by_niche", {}).values())
                available["config_offers"] = total
            except Exception:
                pass
        total = available["hotmart_db"] + available["config_offers"]
        if total == 0:
            available["status"] = "no_products"
            log.warning("No affiliate products found. Add products before running content generation.")
        else:
            log.info(f"Products available: {available['hotmart_db']} DB + {available['config_offers']} config = {total} total")
        return available
        self.enable_second_order = enable_second_order
        self.enable_third_order = enable_third_order
        self.enable_auto_evolution = enable_auto_evolution

        # Second-order agents
        self._meta_orchestrator: Optional[MetaOrchestratorAgent] = None
        self._evolution_engine: Optional[EvolutionEngine] = None
        self._agent_factory: Optional[AgentFactory] = None
        self._circuit_breaker: Optional[CircuitBreaker] = None
        self._self_healing: Optional[SelfHealingAgent] = None
        self._strategy_evolution: Optional[StrategyEvolutionAgent] = None
        self._agent_perf_monitor: Optional[AgentPerformanceMonitor] = None
        # Phase 20: Autonomous Enterprise Kernel
        self._kernel: Optional[AutonomousEnterpriseKernel] = None
        # Quality Layers (Phase 21+)
        self._critic: Optional[OutputCritic] = None
        self._debate: Optional[DebateOrchestrator] = None
        self._benchmark: Optional[BenchmarkDB] = None
        self._campaign_knowledge: Optional[CampaignKnowledge] = None
        self._rag: Optional[RAGEngine] = None
        self._truth: Optional[TruthAgent] = None
        self._risk: Optional[RiskAgent] = None
        self._consistency: Optional[ConsistencyAgent] = None
        self._elo: Optional[ELORanking] = None

        # Quality layers
        self._init_quality_layers()

        # Third-order agents
        self._third_order: Optional[ThirdOrderOrchestrator] = None
        self._epistemic: Optional[ThirdOrderEpistemic] = None
        self._value_system: Optional[ValueSystemEngine] = None

        self._init_governance_agents()

    def _init_quality_layers(self) -> None:
        """Initialize Quality Layers (Phase 21+)."""
        try:
            from .quality_layers import (
                OutputCritic,
                DebateOrchestrator,
                BenchmarkDB,
                CampaignKnowledge,
                RAGEngine,
                TruthAgent,
                RiskAgent,
                ConsistencyAgent,
                ELORanking,
            )

            self._critic = OutputCritic(threshold=85)
            self._debate = DebateOrchestrator()
            self._benchmark = BenchmarkDB()
            self._campaign_knowledge = CampaignKnowledge()
            self._rag = RAGEngine(
                self._benchmark if hasattr(self, "_benchmark") else None,
                self._campaign_knowledge
                if hasattr(self, "_campaign_knowledge")
                else None,
            )
            self._truth = TruthAgent()
            self._risk = RiskAgent()
            self._consistency = ConsistencyAgent()
            self._elo = ELORanking()
            log.info("Quality layers initialized")
        except Exception as e:
            log.warning(f"Quality layers init failed: {e}")

    def _init_governance_agents(self) -> None:
        """Initialize governance agents with shared cognitive stores."""
        if self.semantic_memory is None:
            return

        conn = (
            self.semantic_memory._conn
            if hasattr(self.semantic_memory, "_conn")
            else None
        )

        # Second order
        self._agent_perf_monitor = AgentPerformanceMonitor(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )
        self._meta_orchestrator = MetaOrchestratorAgent(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )
        self._strategy_evolution = StrategyEvolutionAgent(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )
        self._self_healing = SelfHealingAgent(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )
        self._evolution_engine = EvolutionEngine(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )
        self._agent_factory = AgentFactory(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )
        self._circuit_breaker = CircuitBreaker(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )

        # Third order
        self._epistemic = ThirdOrderEpistemic
        self._value_system = ValueSystemEngine
        self._third_order = ThirdOrderOrchestrator(
            semantic_memory=self.semantic_memory,
            explanation_store=self.explanation_store,
        )

    def orchestrate(self, context: CampaignContext) -> Any:
        """Run the complete 3-order cycle."""
        # ── PHASE 1: First Order — Base Workflow ──────────────────
        log.info("phase_1_first_order_start")
        result = super().orchestrate(context)
        log.info(
            "phase_1_first_order_complete",
            status=result.status,
            step_count=len(result.step_results),
        )

        # Inject execution data for downstream governance agents
        # Store full workflow result in artifacts to avoid polluting step_results
        wf_dict = result.to_dict() if hasattr(result, "to_dict") else {}
        if isinstance(wf_dict, dict):
            context.artifacts["workflow_result"] = wf_dict

        # ── PHASE 2: Second Order — Governance ────────────────────
        if self.enable_second_order and self.semantic_memory:
            log.info("phase_2_second_order_start")
            self._run_second_order_governance(context, result)
            log.info("phase_2_second_order_complete")

        # ── PHASE 3: Third Order — Auto-Transcendence ─────────────
        if self.enable_third_order and self.semantic_memory:
            log.info("phase_3_third_order_start")
            self._run_third_order(context, result)
            log.info("phase_3_third_order_complete")

        # ── PHASE 4: Auto-Adaptation ──────────────────────────────
        if self.enable_auto_evolution:
            log.info("phase_4_auto_adaptation_start")
            self._run_auto_adaptation(context, result)
            log.info("phase_4_auto_adaptation_complete")

        # Phase 20: Boot Enterprise Kernel (once)
        self._boot_enterprise_kernel()

        # ── PHASE 20: Autonomous Enterprise Kernel ──────────────────
        if self._kernel is not None:
            try:
                cycle_result = self._kernel.run_cycle()
                context.step_results["enterprise_kernel"] = cycle_result
                log.info(
                    "phase_20_kernel_cycle",
                    cycle=cycle_result.get("cycle_number", 0),
                    healthy=f"{cycle_result.get('subsystems_healthy', 0)}/"
                    f"{cycle_result.get('subsystems_total', 0)}",
                )
            except Exception as e:
                log.warning(f"phase_20_kernel_cycle_failed: {e}")

        return result

    def _boot_enterprise_kernel(self) -> None:
        """Phase 20: Initialize the Autonomous Enterprise Kernel."""
        if self._kernel is None:
            try:
                kernel = AutonomousEnterpriseKernel.get_instance()
                kernel.boot(orchestrator=self)
                # Register available phase modules
                try:
                    from .world_model import WorldModel

                    kernel.register_world_model(WorldModel())
                except (ImportError, Exception):
                    pass
                try:
                    from .constraint_intelligence import ConstraintGraph

                    kernel.register_constraint_graph(ConstraintGraph())
                except (ImportError, Exception):
                    pass
                try:
                    from .economic_intelligence import EconomicEngine

                    kernel.register_economic_engine(EconomicEngine())
                except (ImportError, Exception):
                    pass
                try:
                    from .digital_twin import DigitalTwin

                    kernel.register_digital_twin(DigitalTwin())
                except (ImportError, Exception):
                    pass
                try:
                    from .self_improvement import SelfImprovementEngine

                    kernel.register_self_improvement(SelfImprovementEngine())
                except (ImportError, Exception):
                    pass
                try:
                    from .organization_agent import OrganizationAgent

                    kernel.register_organization(OrganizationAgent())
                except (ImportError, Exception):
                    pass
                try:
                    from .cognitive_mesh import CognitiveMesh

                    kernel.register_cognitive_mesh(CognitiveMesh())
                except (ImportError, Exception):
                    pass
                self._kernel = kernel
                log.info("phase_20_kernel_booted")
            except Exception as e:
                log.warning(f"phase_20_kernel_boot_failed: {e}")

    def _run_second_order_governance(
        self, context: CampaignContext, result: Any
    ) -> None:
        """Execute second-order governance cycle."""
        # 2.1 Agent performance monitoring
        perf_result = (
            self._agent_perf_monitor.run(context) if self._agent_perf_monitor else None
        )
        context.step_results["agent_perf_monitor"] = (
            perf_result.to_dict() if perf_result else {}
        )

        # 2.2 Meta-orchestrator: diagnose bottlenecks, prescribe changes
        meta_result = (
            self._meta_orchestrator.run(context) if self._meta_orchestrator else None
        )
        context.step_results["meta_orchestrator"] = (
            meta_result.to_dict() if meta_result else {}
        )

        meta_output = meta_result.output if meta_result else {}
        prescriptions = (
            meta_output.get("prescriptions", [])
            if isinstance(meta_output, dict)
            else []
        )

        # 2.3 Strategy evolution (multi-cycle planning)
        strat_result = (
            self._strategy_evolution.run(context) if self._strategy_evolution else None
        )
        context.step_results["strategy_evolution"] = (
            strat_result.to_dict() if strat_result else {}
        )

        # 2.4 Self-healing: detect and fix failed agents
        heal_result = self._self_healing.run(context) if self._self_healing else None
        context.step_results["self_healing"] = (
            heal_result.to_dict() if heal_result else {}
        )

        # 2.5 Evolution engine: apply prescriptions automatically
        if prescriptions and self._evolution_engine and self.enable_auto_evolution:
            evo_result = self._evolution_engine.run(context)
            context.step_results["evolution_engine"] = (
                evo_result.to_dict() if evo_result else {}
            )

        # 2.6 Agent factory: detect and fill capability gaps
        if self._agent_factory and self.enable_auto_evolution:
            factory_result = self._agent_factory.run(context)
            context.step_results["agent_factory"] = (
                factory_result.to_dict() if factory_result else {}
            )

        # 2.7 Circuit breaker: health check
        cb_result = (
            self._circuit_breaker.run(context) if self._circuit_breaker else None
        )
        context.step_results["circuit_breaker"] = (
            cb_result.to_dict() if cb_result else {}
        )

    def _run_third_order(self, context: CampaignContext, result: Any) -> None:
        """Execute third-order auto-transcendence cycle."""
        if not self.memory_store:
            return

        conn = self.memory_store._conn if hasattr(self.memory_store, "_conn") else None
        if not conn:
            return

        # 3.1 Epistemic analysis: map knowledge boundaries
        niche = (
            context.campaign.get("niche", "marketing digital")
            if isinstance(context.campaign, dict)
            else "marketing digital"
        )
        if self._epistemic:
            kMap = self._epistemic.create_knowledge_map(niche)
            blind_spots = []
            if hasattr(kMap, "assumptions"):
                assumptions_list = (
                    kMap.assumptions if isinstance(kMap.assumptions, list) else []
                )
                blind_spots = [
                    a
                    for a in assumptions_list
                    if isinstance(a, dict) and a.get("confidence", 1) < 0.5
                ]
            context.step_results["epistemic"] = {
                "niche": niche,
                "blind_spots": len(blind_spots),
            }

        # 3.2 Value system evolution
        if self._value_system:
            profile = (
                self._value_system.ValueProfile()
                if hasattr(self._value_system, "ValueProfile")
                else {}
            )
            context.step_results["value_evolution"] = {
                "status": "completed",
            }

        # 3.3 Third-order orchestrator
        if self._third_order:
            third_result = self._third_order.run(context)
            context.step_results["third_order"] = (
                third_result.to_dict()
                if third_result
                else {
                    "status": "completed",
                    "note": "Third-order analysis finished",
                }
            )

    def _run_auto_adaptation(self, context: CampaignContext, result: Any) -> None:
        """Run automatic parameter adaptation based on performance."""
        try:
            # 4.1 Adaptive decay rates
            if self.semantic_memory and self.outcome_store:
                self._adapt_decay_rates()

            # 4.2 Auto-ontology correction
            if self.semantic_memory and self.outcome_store:
                self._auto_correct_ontology(context)

            # 4.3 Auto-goal generation
            if self.goal_registry:
                self._auto_generate_goals(context)

            # 4.4 Adaptive resource allocation
            self._adapt_workers(result)
        except Exception as exc:
            log.warning("auto_adaptation_error", error=str(exc))

    def _adapt_decay_rates(self) -> None:
        """Adjust confidence decay rates based on prediction accuracy."""
        if not (self.semantic_memory and self.outcome_store):
            return

        conn = (
            self.semantic_memory._conn
            if hasattr(self.semantic_memory, "_conn")
            else None
        )
        if not conn:
            return

        # Check last N outcomes for prediction accuracy
        outcomes = conn.execute(
            "SELECT expected_outcome, actual_outcome FROM feedback_outcomes ORDER BY evaluated_at DESC LIMIT 10"
        ).fetchall()

        if len(outcomes) < 5:
            return

        # Calculate accuracy ratio
        accurate = 0
        for exp, act in outcomes:
            try:
                e = json.loads(exp) if isinstance(exp, str) else exp
                a = json.loads(act) if isinstance(act, str) else act
                if isinstance(e, dict) and isinstance(a, dict):
                    e_status = e.get("status_achieved", e.get("status", 0))
                    a_status = a.get("status_achieved", a.get("status", 0))
                    if e_status == a_status:
                        accurate += 1
            except (json.JSONDecodeError, TypeError):
                continue

        accuracy = accurate / len(outcomes)

        # Adapt decay rates: high accuracy → slower decay (trust knowledge more)
        if accuracy > 0.8:
            # Slower decay - knowledge is reliable
            rates = {
                "VERIFIED": 0.98,
                "INFERRED": 0.92,
                "ASSUMED": 0.85,
                "HYPOTHETICAL": 0.78,
            }
        elif accuracy > 0.5:
            # Medium decay
            rates = {
                "VERIFIED": 0.95,
                "INFERRED": 0.85,
                "ASSUMED": 0.75,
                "HYPOTHETICAL": 0.65,
            }
        else:
            # Faster decay - knowledge is unreliable
            rates = {
                "VERIFIED": 0.90,
                "INFERRED": 0.78,
                "ASSUMED": 0.65,
                "HYPOTHETICAL": 0.50,
            }

        from .semantic_memory import _DEFAULT_DECAY_RATES

        new_rates = dict(_DEFAULT_DECAY_RATES)
        for k, v in rates.items():
            if k in new_rates:
                new_rates[k] = v

        self.semantic_memory.decay_confidence(rates_by_status=new_rates)
        log.info("adaptive_decay_applied", accuracy=accuracy, rates=new_rates)

    def _auto_correct_ontology(self, context: CampaignContext) -> None:
        """Auto-correct ontology drift by merging conflicting concepts."""
        if not self.semantic_memory:
            return

        conn = (
            self.semantic_memory._conn
            if hasattr(self.semantic_memory, "_conn")
            else None
        )
        if not conn:
            return

        # Get last drift detection
        versions = conn.execute(
            "SELECT version_id FROM semantic_ontology_versions ORDER BY released_at DESC LIMIT 2"
        ).fetchall()

        if len(versions) < 2:
            return

        drift = self.semantic_memory.diff_ontology(
            versions[1]["version_id"], versions[0]["version_id"]
        )
        drift_type = drift.get("type", "")

        if drift_type == "CONCEPT_DRIFT":
            # Merge similar concepts (concepts with same name but different IDs)
            similar = drift.get("similar_concepts", [])
            for item in similar:
                if isinstance(item, dict):
                    concept_a = item.get("concept_a", "")
                    concept_b = item.get("concept_b", "")
                    if concept_a and concept_b:
                        # Merge b into a
                        conn.execute(
                            "UPDATE semantic_claims SET subject = ? WHERE subject = ?",
                            (concept_a, concept_b),
                        )
                        conn.execute(
                            "UPDATE semantic_claims SET object = ? WHERE object = ?",
                            (concept_a, concept_b),
                        )
                        conn.execute(
                            "DELETE FROM semantic_concepts WHERE concept_id = ?",
                            (concept_b,),
                        )
                        conn.commit()

            log.info(
                "ontology_corrected", drift_type=drift_type, corrections=len(similar)
            )

        elif drift_type == "CONFLICTING_CLAIMS":
            # Resolve conflicting claims by keeping the one with higher confidence
            conflicts = drift.get("conflicts", [])
            for conflict in conflicts:
                if isinstance(conflict, dict):
                    # Keep higher-confidence claim, archive lower
                    for key in ("high_conf", "low_conf"):
                        claim = conflict.get(key)
                        if claim and isinstance(claim, dict):
                            claim_id = claim.get("claim_id")
                            if claim_id:
                                conn.execute(
                                    "UPDATE semantic_claims SET epistemic_status = 'ARCHIVED' WHERE claim_id = ? AND confidence < 0.5",
                                    (claim_id,),
                                )
                    conn.commit()

            log.info("ontology_conflicts_resolved", count=len(conflicts))

    def _auto_generate_goals(self, context: CampaignContext) -> None:
        """Auto-generate strategic goals based on system performance."""
        if not (self.goal_registry and self.outcome_store):
            return

        conn = (
            self.goal_registry._conn if hasattr(self.goal_registry, "_conn") else None
        )
        if not conn:
            return

        # Check current metrics
        try:
            revenue_row = conn.execute(
                "SELECT COALESCE(total_words_generated, 0), COALESCE(total_videos_generated, 0) FROM autopilot_cycles ORDER BY cycle_id DESC LIMIT 1"
            ).fetchone()
        except Exception:
            revenue_row = None

        words = revenue_row[0] if revenue_row else 0
        videos = revenue_row[1] if revenue_row else 0

        # Generate goals based on gaps
        goals_to_create = []

        if words < 10000:
            goals_to_create.append(
                {
                    "objective": "Atingir 10.000 palavras de conteúdo geradas",
                    "success_criteria": {"min_words": 10000},
                }
            )

        if videos < 5:
            goals_to_create.append(
                {
                    "objective": "Produzir 5 vídeos cinematográficos",
                    "success_criteria": {"min_videos": 5},
                }
            )

        # Check if there are channels not yet utilized
        goals_to_create.append(
            {
                "objective": "Distribuir conteúdo em pelo menos 3 canais diferentes",
                "success_criteria": {"min_channels": 3},
            }
        )

        # Register new goals
        for goal in goals_to_create:
            existing = conn.execute(
                "SELECT goal_id FROM goals WHERE objective = ?",
                (goal["objective"],),
            ).fetchone()
            if not existing:
                self.goal_registry.register_goal(
                    objective=goal["objective"],
                    success_criteria=goal["success_criteria"],
                )
                log.info("auto_goal_created", objective=goal["objective"])

    def _adapt_workers(self, result: Any) -> None:
        """Adapt max_workers based on step count and parallelism."""
        step_count = len(result.step_results) if hasattr(result, "step_results") else 0
        if step_count > 20:
            new_workers = max(4, min(14, step_count // 3))
        elif step_count > 10:
            new_workers = max(2, min(8, step_count // 2))
        else:
            new_workers = 2

        if self.runner and hasattr(self.runner, "max_workers"):
            self.runner.max_workers = new_workers
            log.info("workers_adapted", step_count=step_count, new_workers=new_workers)


def create_orchestrator(
    workflow_path: str | Path | None = None,
    runner=None,
    memory_store=None,
    mode: str = "full",
) -> OrchestratorV2:
    """Factory function for the orchestrator.

    Modes:
    - 'full': All 3 orders + auto-evolution
    - 'first_order': Only base workflow
    - 'first_second': First + second order
    - 'first_third': First + third order
    """

    enable_second = mode in ("full", "first_second")
    enable_third = mode in ("full", "first_third")
    enable_evolution = mode == "full"

    return OrchestratorV2(
        workflow_path=workflow_path,
        runner=runner,
        memory_store=memory_store,
        enable_second_order=enable_second,
        enable_third_order=enable_third,
        enable_auto_evolution=enable_evolution,
    )
