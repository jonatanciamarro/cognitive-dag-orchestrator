from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)
from .analytics import AnalyticsAgent
from .compliance import ComplianceAgent
from .memory_agent import MemoryLookupAgent
from .optimization import OptimizationAgent
from .seo_research import SEOResearchAgent
from .offer_lookup import OfferLookupAgent
from .content_planner import ContentPlannerAgent
from .publisher import PublisherAgent
from .content_generator import ContentGeneratorAgent
from .wp_publisher import WordPressPublisherAgent
from .youtube_marketing import YouTubeMarketingAgent
from .email_marketing import EmailMarketingAgent
from .pinterest_marketing import PinterestMarketingAgent
from .analytics_feedback import AnalyticsFeedbackAgent
from .whatsapp_marketing import WhatsAppMarketingAgent
from .lead_capture import LeadCaptureAgent
from .content_repurposer import ContentRepurposerAgent
from .revenue_monitor import RevenueMonitorAgent
from .seo_scraper import SEOScraperAgent
from .competitor_analysis import CompetitorAnalysisAgent
from .rank_tracker import RankTrackerAgent
from .content_optimizer import ContentOptimizerAgent
from .bulk_publisher import BulkPublisherAgent
from .site_deploy import SiteDeployAgent
from .instagram_marketing import InstagramMarketingAgent
from .tiktok_marketing import TikTokMarketingAgent
from .twitter_marketing import TwitterMarketingAgent
from .platform_compliance import PlatformComplianceAgent
from .organic_growth import OrganicTrafficGrowthHackerAgent
from .free_image_gen import FreeImageGeneratorAgent
from .free_video_producer import FreeVideoProducerAgent
from .meta_orchestrator import MetaOrchestratorAgent
from .strategy_evolution import StrategyEvolutionAgent
from .agent_perf_monitor import AgentPerformanceMonitor
from .self_healing import SelfHealingAgent
from .agent_factory import AgentFactory
from .evolution_engine import EvolutionEngine
from .circuit_breaker import CircuitBreaker
from .cinematic_image_agent import CinematicImageAgent
from .cinematic_video_agent import CinematicVideoAgent
from .cinematic_fiapi_agent import CinematicFIAPIAgent
from .audio_production_agent import AudioProductionAgent
from .media_pipeline_agent import MediaPipelineAgent
from .storyboard_agent import StoryboardAgent
from .content_excellence_agent import ContentExcellenceAgent
from .storytelling_specialist import StorytellingSpecialistAgent
from .psychology_specialist import PsychologySpecialistAgent
from .neuromarketing_specialist import NeuromarketingSpecialistAgent
from .governance_agent import GovernanceAgent
from .epistemic_agent import EpistemicAgent
from .observer_fusion_agent import ObserverFusionAgent
from .value_evolution_agent import ValueEvolutionAgent
from .revenue.parallel_tree import ParallelRevenueTreeAgent
from .paid_traffic.flywheel_agent import PaidTrafficFlywheelAgent
from .ui_design import UIDesignAgent
from .revenue.branch_agent import RevenueBranchAgent
from .recursive_observer_agent import RecursiveObserverAgent
from .third_order_orchestrator import ThirdOrderOrchestrator
from ..workflow import (
    ExecutionAction,
    ExecutionPlan,
    WorkflowRunner,
    WorkflowRunResult,
    WorkflowSpec,
)
from ..memory import MemoryStore
from ..feedback import OutcomeStore
from ..synthesis import KnowledgeSynthesisEngine
from ..goals import GoalRegistry


class ExecutionPlanningAgent(AgentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__("execution_planning", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        optimization = context.step_results.get("optimization", {})
        analytics = context.step_results.get("analytics", {})
        compliance = context.step_results.get("compliance", {})
        memory = context.step_results.get("memory_lookup", {})

        optimization_output = (
            optimization.get("output", {}) if isinstance(optimization, dict) else {}
        )
        actions = []
        for index, action in enumerate(optimization_output.get("actions", []), start=1):
            actions.append(
                ExecutionAction(
                    id=str(action.get("id") or f"action_{index}"),
                    title=str(action.get("title", "Execute recommendation")),
                    owner=str(action.get("owner", "ops")),
                    channel=str(action.get("channel", "primary")),
                    change=str(action.get("change", "")),
                    priority=str(action.get("priority", "medium")),
                    rationale=str(action.get("rationale", "")),
                    success_metric=str(
                        action.get(
                            "success_metric", "Track downstream performance lift."
                        )
                    ),
                    guardrails=[str(item) for item in action.get("guardrails", [])],
                )
            )

        compliance_output = (
            compliance.get("output", {}) if isinstance(compliance, dict) else {}
        )
        if compliance_output.get("status") == "block":
            summary = "Execution is paused until compliance issues are resolved."
            status = "blocked"
        elif not actions:
            summary = "No executable optimization actions were produced."
            status = "empty"
        else:
            summary = (
                "Execute the recommended campaign optimization steps in priority order."
            )
            status = "ready"

        plan = ExecutionPlan(
            objective=str(context.campaign.get("objective", "campaign optimization")),
            summary=summary,
            status=status,
            actions=actions,
            risks=[str(item) for item in optimization_output.get("risks", [])],
            guardrails=[
                str(item) for item in optimization_output.get("guardrails", [])
            ],
            insights={
                "analytics": analytics.get("output", {})
                if isinstance(analytics, dict)
                else {},
                "compliance": compliance_output,
                "memory": memory.get("output", {}) if isinstance(memory, dict) else {},
                "optimization": optimization_output,
            },
            source_steps=[
                "analytics",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
            ],
        )
        finished_at = utc_now_iso()
        duration_ms = iso_duration_ms(started_at, finished_at)
        trace = AgentTrace(
            agent=self.name,
            step_id="execution_planning",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            thread_name="main",
            notes=["Converted optimization output into a serializable execution plan."],
            metadata={"action_count": len(actions), "plan_status": status},
        )
        return AgentResult(agent=self.name, status="success", output=plan, trace=trace)


class CampaignOrchestrator(AgentBase):
    def __init__(
        self,
        workflow_path: str | Path | None = None,
        runner: WorkflowRunner | None = None,
        memory_store: MemoryStore | None = None,
    ) -> None:
        super().__init__("orchestrator")
        project_root = Path(__file__).resolve().parents[3]
        self.workflow_path = (
            Path(workflow_path)
            if workflow_path
            else project_root / "workflows" / "campaign_cycle.json"
        )
        self.runner = runner or WorkflowRunner()
        self.memory_store = memory_store
        self.semantic_memory: "Optional[Any]" = None
        self.explanation_store: "Optional[Any]" = None
        # Initialize cognitive stores if memory_store is available
        if memory_store is not None:
            from ..semantic_memory import SemanticMemoryStore
            from ..explanation import ExplanationStore

            self.semantic_memory = SemanticMemoryStore(memory_store._conn)
            self.explanation_store = ExplanationStore(memory_store._conn)
        self.goal_registry: "Optional[Any]" = None
        self.outcome_store: "Optional[Any]" = None
        self.synthesis_engine: "Optional[Any]" = None
        self._observers_registered: bool = False
        if memory_store is not None:
            self.outcome_store = OutcomeStore(memory_store._conn)
            self.goal_registry = GoalRegistry(memory_store._conn)
            if self.semantic_memory is not None:
                self.synthesis_engine = KnowledgeSynthesisEngine(self.semantic_memory)
        self.registry = {
            "analytics": AnalyticsAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "compliance": ComplianceAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "memory_lookup": MemoryLookupAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "optimization": OptimizationAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "execution_planning": ExecutionPlanningAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "seo_research": SEOResearchAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "offer_lookup": OfferLookupAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "content_planner": ContentPlannerAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "publisher": PublisherAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "content_generator": ContentGeneratorAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "wp_publisher": WordPressPublisherAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "youtube_marketing": YouTubeMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "email_marketing": EmailMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "pinterest_marketing": PinterestMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "analytics_feedback": AnalyticsFeedbackAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "whatsapp_marketing": WhatsAppMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "lead_capture": LeadCaptureAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "content_repurposer": ContentRepurposerAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "revenue_monitor": RevenueMonitorAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "seo_scraper": SEOScraperAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "competitor_analysis": CompetitorAnalysisAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "rank_tracker": RankTrackerAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "content_optimizer": ContentOptimizerAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "bulk_publisher": BulkPublisherAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "site_deploy": SiteDeployAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "instagram_marketing": InstagramMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "tiktok_marketing": TikTokMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "twitter_marketing": TwitterMarketingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "platform_compliance": PlatformComplianceAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "organic_growth": OrganicTrafficGrowthHackerAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "free_image_gen": FreeImageGeneratorAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "free_video_producer": FreeVideoProducerAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "meta_orchestrator": MetaOrchestratorAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "strategy_evolution": StrategyEvolutionAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "agent_perf_monitor": AgentPerformanceMonitor(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "evolution_engine": EvolutionEngine(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "circuit_breaker": CircuitBreaker(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "agent_factory": AgentFactory(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "cinematic_image_gen": CinematicImageAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "cinematic_fiapi_gen": CinematicFIAPIAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "cinematic_video_producer": CinematicVideoAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "audio_production": AudioProductionAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "media_pipeline": MediaPipelineAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "storyboard": StoryboardAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "content_excellence": ContentExcellenceAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "storytelling_specialist": StorytellingSpecialistAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "psychology_specialist": PsychologySpecialistAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "neuromarketing_specialist": NeuromarketingSpecialistAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "resource_manager": GovernanceAgent(
                delegate="resource_manager",
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "quality_assurance": GovernanceAgent(
                delegate="quality_assurance",
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "risk_management": GovernanceAgent(
                delegate="risk_management",
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "external_monitor": GovernanceAgent(
                delegate="external_monitor",
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "rollback_manager": GovernanceAgent(
                delegate="rollback_manager",
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "epistemic": EpistemicAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "observer_fusion": ObserverFusionAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "value_evolution": ValueEvolutionAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "recursive_observer": RecursiveObserverAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "third_order_orchestrator": ThirdOrderOrchestrator(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "self_healing": SelfHealingAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "revenue_hotmart": RevenueBranchAgent(source="hotmart"),
            "revenue_kiwify": RevenueBranchAgent(source="kiwify"),
            "revenue_eduzz": RevenueBranchAgent(source="eduzz"),
            "revenue_monetizze": RevenueBranchAgent(source="monetizze"),
            "revenue_mercadolivre": RevenueBranchAgent(source="mercadolivre"),
            "revenue_shopee": RevenueBranchAgent(source="shopee"),
            "revenue_shein": RevenueBranchAgent(source="shein"),
            "revenue_aliexpress": RevenueBranchAgent(source="aliexpress"),
            "revenue_amazon": RevenueBranchAgent(source="amazon"),
            "revenue_adsense": RevenueBranchAgent(source="adsense"),
            "revenue_cpa": RevenueBranchAgent(source="cpa"),
            "revenue_digital_product": RevenueBranchAgent(source="digital_product"),
            "revenue_membership": RevenueBranchAgent(source="membership"),
            "paid_traffic_flywheel": PaidTrafficFlywheelAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "parallel_revenue_tree": ParallelRevenueTreeAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
            "ui_design": UIDesignAgent(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),
        }

    def _ensure_observers_registered(self) -> None:
        """Register all workflow agents as semantic observers (once per session)."""
        if self._observers_registered or self.semantic_memory is None:
            return
        for agent_id in (
            "analytics",
            "compliance",
            "memory_lookup",
            "optimization",
            "execution_planning",
            "seo_research",
            "offer_lookup",
            "content_planner",
            "publisher",
            "content_generator",
            "wp_publisher",
            "youtube_marketing",
            "email_marketing",
            "pinterest_marketing",
            "analytics_feedback",
            "whatsapp_marketing",
            "lead_capture",
            "content_repurposer",
            "revenue_monitor",
            "seo_scraper",
            "competitor_analysis",
            "rank_tracker",
            "content_optimizer",
            "bulk_publisher",
            "site_deploy",
            "instagram_marketing",
            "tiktok_marketing",
            "twitter_marketing",
            "platform_compliance",
            "organic_growth",
            "free_image_gen",
            "free_video_producer",
            "meta_orchestrator",
            "strategy_evolution",
            "agent_perf_monitor",
            "self_healing",
            "evolution_engine",
            "circuit_breaker",
            "agent_factory",
            "ontology_steward",
            "orchestrator",
        ):
            self.semantic_memory.register_observer(
                observer_id=agent_id,
                observer_type="AGENT",
                name=f"{agent_id}_agent",
                reliability=0.7,
                bias_profile={"domain": "campaign_optimization", "agent_id": agent_id},
            )
        self._observers_registered = True

    def orchestrate(self, context: CampaignContext) -> WorkflowRunResult:
        spec = WorkflowSpec.load(self.workflow_path)
        self._ensure_observers_registered()
        result = self.runner.run(spec, context, self.registry)

        # Record expected outcome from the execution plan for feedback loop
        if self.outcome_store and result.output is not None:
            plan = result.output
            if hasattr(plan, "to_dict"):
                plan_dict = plan.to_dict()
            elif isinstance(plan, dict):
                plan_dict = plan
            else:
                plan_dict = {}
            self.outcome_store.record_expected(
                cycle_id=context.run_id,
                expected_outcome={
                    "status": plan_dict.get("status", result.status),
                    "action_count": len(plan_dict.get("actions", [])),
                    "objective": context.campaign.get("objective", ""),
                },
                source_step_id="execution_planning",
            )

        # Snapshot ontology for versioning
        if self.semantic_memory:
            version_id = f"{spec.name}_{context.run_id[:8]}"
            self.semantic_memory.snapshot_ontology(version_id)

        # Knowledge synthesis: cross-cycle pattern detection with epistemic-aware decay
        if self.synthesis_engine:
            self.synthesis_engine.synthesize(cycle_id=context.run_id)
            # Apply epistemic-weighted confidence decay
            from ..semantic_memory import _DEFAULT_DECAY_RATES

            if self.semantic_memory:
                self.semantic_memory.decay_confidence(
                    rates_by_status=_DEFAULT_DECAY_RATES
                )

        # Goal evaluation: evaluate active goals against the execution plan
        if self.goal_registry and result.output is not None:
            plan = result.output
            plan_dict = (
                plan.to_dict()
                if hasattr(plan, "to_dict")
                else (plan if isinstance(plan, dict) else {})
            )
            outcome_data = {
                "status_achieved": 1.0 if plan_dict.get("status") == "ready" else 0.0,
                "action_count": float(len(plan_dict.get("actions", []))),
            }
            self.goal_registry.evaluate_from_outcome(
                cycle_id=context.run_id,
                outcome_data=outcome_data,
            )

        # Ontology drift check if multiple versions exist
        if self.semantic_memory:
            self._check_ontology_drift(spec.name, context.run_id)

        return result

    def _check_ontology_drift(self, workflow_name: str, run_id: str) -> None:
        """Check for semantic drift between the last two ontology versions."""
        versions = self.semantic_memory._execute(
            "SELECT version_id FROM semantic_ontology_versions ORDER BY released_at DESC LIMIT 2"
        ).fetchall()
        if len(versions) >= 2:
            drift = self.semantic_memory.diff_ontology(
                versions[1]["version_id"], versions[0]["version_id"]
            )
            if drift.get("semantic_risk") in ("HIGH", "MEDIUM"):
                # Record drift as semantic knowledge
                drift_concept = self.semantic_memory.find_concept(
                    "semantic_drift", "meta"
                )
                if not drift_concept:
                    drift_concept_id = self.semantic_memory.register_concept(
                        "semantic_drift",
                        "meta",
                        "Detected changes in ontology across cycles",
                    )
                else:
                    drift_concept_id = drift_concept["concept_id"]
                context_concept_id = self.semantic_memory.register_concept(
                    f"drift_{run_id[:8]}",
                    "meta",
                    f"Drift risk: {drift.get('semantic_risk')}, score: {drift.get('drift_score')}",
                )
                self.semantic_memory.assert_claim(
                    subject=drift_concept_id,
                    predicate="warns",
                    object=context_concept_id,
                    confidence=0.8 if drift.get("semantic_risk") == "HIGH" else 0.5,
                    evidence_type="STATISTICAL_INFERENCE",
                    epistemic_status="INFERRED",
                    supporting_data=drift,
                    source_cycle_id=run_id,
                    asserted_by="ontology_steward",
                    observer_id="ontology_steward",
                )

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        workflow_result = self.orchestrate(context)
        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="orchestrator",
            status=workflow_result.status,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=workflow_result.duration_ms,
            thread_name="main",
            notes=[
                "Ran the campaign workflow from analytics through execution planning."
            ],
            metadata={
                "workflow_name": workflow_result.workflow_name,
                "step_count": len(workflow_result.step_results),
            },
        )
        return AgentResult(
            agent=self.name,
            status=workflow_result.status,
            output=workflow_result.to_dict(),
            trace=trace,
        )
