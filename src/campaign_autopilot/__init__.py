"""Campaign Autopilot package."""

from .models import Campaign, Decision, Event, Metrics, Policy
from .memory import MemoryStore
from .metrics import calculate_metrics
from .policy import DecisionPlan, PolicyEngine
from .workflow import (
    ExecutionAction,
    ExecutionPlan,
    StepResult,
    WorkflowRunner,
    WorkflowRunResult,
    WorkflowSpec,
)
from .agents.base import CampaignContext
from .semantic_memory import SemanticMemoryStore
from .explanation import ExplanationStore
from .feedback import OutcomeStore
from .synthesis import KnowledgeSynthesisEngine
from .goals import GoalRegistry
from .affiliate import (
    OfferManager,
    AffiliateOffer,
    AffiliateLink,
    ContentBrief,
    AmazonAssociates,
    Hotmart,
    GenericAffiliate,
)
from .agents.content_generator import ContentGeneratorAgent
from .agents.wp_publisher import WordPressPublisherAgent
from .agents.youtube_marketing import YouTubeMarketingAgent
from .agents.email_marketing import EmailMarketingAgent
from .agents.pinterest_marketing import PinterestMarketingAgent
from .agents.analytics_feedback import AnalyticsFeedbackAgent
from .agents.whatsapp_marketing import WhatsAppMarketingAgent
from .agents.lead_capture import LeadCaptureAgent
from .agents.content_repurposer import ContentRepurposerAgent
from .agents.revenue_monitor import RevenueMonitorAgent
from .agents.seo_scraper import SEOScraperAgent
from .agents.competitor_analysis import CompetitorAnalysisAgent
from .agents.rank_tracker import RankTrackerAgent
from .agents.content_optimizer import ContentOptimizerAgent
from .agents.bulk_publisher import BulkPublisherAgent
from .agents.site_deploy import SiteDeployAgent
from .agents.orchestrator import CampaignOrchestrator

# ── AG-Kit Evolution Modules (Phases 11-17) ──────────────────────────
from .constraint_intelligence import (
    ConstraintGraph,
    ConstraintNode,
    ConstraintAwareWorkflow,
    ConstraintDetector,
    ConstraintType,
    ConstraintSeverity,
    build_default_constraint_graph,
    diagnose,
)
from .world_model import (
    WorldModel,
    WorldState,
    Action,
    StatePredictor,
    ScenarioSimulator,
    CounterfactualEngine,
)
from .economic_intelligence import (
    EconomicEngine,
    CapitalAllocationEngine,
    ChannelROIModel,
    OpportunityCostEngine,
    PortfolioSummary,
    AllocationDecision,
    InvestmentStrategy,
)
from .agent_evolution import (
    AgentEvolutionEngine,
    AgentGenome,
    MutationEngine,
    SelectionEngine,
    AgentBreeder,
    MutationType,
    FitnessMetric,
)
from .digital_twin import (
    DigitalTwin,
    SystemSnapshot,
    ExperimentResult,
    ValidationResult,
    DeploymentPlan,
    SnapshotManager,
    ExperimentRunner,
    ExperimentValidator,
    SafeDeployer,
)
from .organization_agent import (
    OrganizationAgent,
    OrganizationState,
    OrganizationMemory,
    DepartmentRegistry,
    Department,
    Objective,
    DepartmentRole,
    ObjectiveStatus,
    OrganizationPhase,
)


from .cognitive_mesh import (
    CognitiveMesh,
    MessageBus,
    MeshMessage,
    MeshAgent,
    Hypothesis,
    HypothesisShare,
    Belief,
    BeliefPropagation,
    MessagePriority,
    HypothesisStatus,
)


from .constraint_genealogy import (
    ConstraintGenealogy,
    GenealogyStore,
    GenealogyNode,
    GenealogyPath,
    CausalTracer,
    GenealogyBuilder,
    NodeType,
    SurvivalStatus,
)


from .self_improvement import (
    SelfImprovementEngine,
    SelfDiagnosis,
    DiagnosisReport,
    Finding,
    ImprovementPlan,
    Patch,
)

# ── All agent exports ────────────────────────────────────────────
from .agents.base import AgentBase, AgentResult, AgentTrace
from .agents.analytics import AnalyticsAgent
from .agents.compliance import ComplianceAgent
from .agents.memory_agent import MemoryLookupAgent
from .agents.optimization import OptimizationAgent
from .agents.seo_research import SEOResearchAgent
from .agents.offer_lookup import OfferLookupAgent
from .agents.content_planner import ContentPlannerAgent
from .agents.publisher import PublisherAgent
from .agents.instagram_marketing import InstagramMarketingAgent
from .agents.tiktok_marketing import TikTokMarketingAgent
from .agents.twitter_marketing import TwitterMarketingAgent
from .agents.platform_compliance import PlatformComplianceAgent
from .agents.organic_growth import OrganicTrafficGrowthHackerAgent
from .agents.free_image_gen import FreeImageGeneratorAgent
from .agents.free_video_producer import FreeVideoProducerAgent
from .agents.meta_orchestrator import MetaOrchestratorAgent
from .agents.strategy_evolution import StrategyEvolutionAgent
from .agents.agent_perf_monitor import AgentPerformanceMonitor
from .agents.self_healing import SelfHealingAgent
from .agents.circuit_breaker import CircuitBreaker
from .agents.evolution_engine import EvolutionEngine
from .agents.agent_factory import AgentFactory
from .agents.cinematic_image_agent import CinematicImageAgent
from .agents.cinematic_video_agent import CinematicVideoAgent
from .agents.audio_production_agent import AudioProductionAgent
from .agents.media_pipeline_agent import MediaPipelineAgent
from .agents.storyboard_agent import StoryboardAgent
from .agents.content_excellence_agent import ContentExcellenceAgent
from .agents.storytelling_specialist import StorytellingSpecialistAgent
from .agents.psychology_specialist import PsychologySpecialistAgent
from .agents.neuromarketing_specialist import NeuromarketingSpecialistAgent
from .agents.governance_agent import GovernanceAgent
from .agents.traffic_recycler import TrafficRecyclerAgent
from .agents.epistemic_agent import EpistemicAgent
from .agents.observer_fusion_agent import ObserverFusionAgent
from .agents.value_evolution_agent import ValueEvolutionAgent
from .agents.recursive_observer_agent import RecursiveObserverAgent
from .agents.third_order_orchestrator import ThirdOrderOrchestrator

# ── Sub-package agents (news, money, revenue, paid_traffic, social, meta, hotmart) ──
from .agents.news import (
    ContentResearchAgent,
    SEOContentWriterAgent,
    EEATValidatorAgent,
    SEOTechnicalAgent,
    SEOMultimediaAgent,
    InternalLinkerAgent,
    SitePublisherAgent,
)
from .agents.money import (
    DigitalProductAgent,
    MembershipAgent,
    AffiliateLinkInserterAgent,
)
from .agents.revenue import (
    RevenueOrchestratorAgent,
    GenericAffiliateNetworkAgent,
    AdSenseAgent,
    CPAAgent,
)
from .agents.paid_traffic import (
    PaidTrafficOrchestratorAgent,
    BudgetOptimizerAgent,
    GoogleAdsAgent,
    MetaAdsAgent,
    NativeAdsAgent,
    AdCopyGeneratorAgent,
    LandingPageAgent,
    PerformanceTrackerAgent,
)
from .agents.social_publishers import (
    SocialPublishingOrchestratorAgent,
    YouTubePublisherAgent,
    TwitterPublisherAgent,
    InstagramPublisherAgent,
    TikTokPublisherAgent,
    PinterestPublisherAgent,
    LinkedInPublisherAgent,
    TelegramPublisherAgent,
    FacebookPublisherAgent,
    BrowserAutomationAgent,
)
from .agents.meta import (
    PortfolioOptimizerAgent,
    CompoundingEngine,
    OpportunityDetectorAgent,
    CrossPollinationHub,
    KnowledgeSynthesisBridge,
)
from .agents.hotmart import (
    HotmartLinkManagerAgent,
    ProductMatcherAgent,
    AffiliateConfigUpdaterAgent,
    LinkValidatorAgent,
)
from .agents.kollektiv import KollektivAgent
from .agents.temporal_engine import TemporalEngineAgent
from .agents.creative_engine import (
    CreativeEngine,
    NicheGenesisAgent,
    NovelValueGenerator,
)
from .agents.safe_mass_posting import SafeMassPostingAgent

# ── Product Forge (Open Design integration) ──────────────────
from .product_forge import (
    DesignSystem,
    DesignToken,
    ColorToken,
    TypographyToken,
    SpacingToken,
    ComponentSpec,
    LayoutSpec,
    DesignSystemRegistry,
    load_design_system,
    default_lyzer_design_system,
    ArtifactGenerator,
    ArtifactSpec,
    ArtifactType,
    ArtifactResult,
    RenderTemplate,
    ComponentRenderer,
    LayoutRenderer,
    LandingPageGenerator,
    LandingPageSpec,
    HeroSection,
    FeaturesSection,
    CTASection,
    TestimonialsSection,
    PricingSection,
    FooterSection,
    SectionBase,
    DashboardGenerator,
    DashboardSpec,
    MetricCard,
    ChartSpec,
    ChartType,
    TableSpec,
    KPIRow,
    EmailTemplateGenerator,
    EmailSpec,
    EmailSection,
    EmailStyle,
    PresentationGenerator,
    PresentationSpec,
    SlideSpec,
    SlideType,
    SlideSection,
    PresentationTheme,
    LYZER_COLORS,
    LYZER_GRADIENTS,
    LYZER_SHADOWS,
    LYZER_TYPOGRAPHY,
    generate_css_variables,
    generate_tailwind_config,
)

# ── Module-level exports ──────────────────────────────
from . import free_llm_providers
from . import free_content_generator
from . import media_providers
from . import model_router
from . import trace_store
from . import workflow_checkpoint
from . import evaluation_engine
from . import capability_registry

# ── Enterprise Kernel (Phase 20) ──────────────────────
from .enterprise_kernel import (
    AutonomousEnterpriseKernel,
    KernelSnapshot,
    KernelStatus,
)

# ── Quality Layers (Phase 21+) ────────────────────────
from .quality_layers import (
    OutputCritic,
    CriticVerdict,
    DebateOrchestrator,
    BenchmarkDB,
    CampaignKnowledge,
    RAGEngine,
    TruthAgent,
    RiskAgent,
    ConsistencyAgent,
    ELORanking,
)

# ── Prompt Architect ──────────────────────────────────
from .prompt_architect import (
    MediaPromptArchitect,
    CTOMediaPromptIntegrator,
)


__all__ = [
    "SemanticMemoryStore",
    "ExplanationStore",
    "OutcomeStore",
    "KnowledgeSynthesisEngine",
    "CampaignContext",
    "Campaign",
    "Decision",
    "DecisionPlan",
    "ExecutionAction",
    "ExecutionPlan",
    "Event",
    "MemoryStore",
    "Metrics",
    "Policy",
    "PolicyEngine",
    "CampaignOrchestrator",
    "ContentGeneratorAgent",
    "WordPressPublisherAgent",
    "YouTubeMarketingAgent",
    "EmailMarketingAgent",
    "PinterestMarketingAgent",
    "AnalyticsFeedbackAgent",
    "WhatsAppMarketingAgent",
    "LeadCaptureAgent",
    "ContentRepurposerAgent",
    "RevenueMonitorAgent",
    "SEOScraperAgent",
    "CompetitorAnalysisAgent",
    "RankTrackerAgent",
    "ContentOptimizerAgent",
    "BulkPublisherAgent",
    "SiteDeployAgent",
    "GoalRegistry",
    "OfferManager",
    "AffiliateOffer",
    "AffiliateLink",
    "ContentBrief",
    "AmazonAssociates",
    "Hotmart",
    "GenericAffiliate",
    "calculate_metrics",
    "StepResult",
    "WorkflowRunner",
    "WorkflowRunResult",
    "WorkflowSpec",
    "AgentBase",
    "AgentResult",
    "AgentTrace",
    "AnalyticsAgent",
    "ComplianceAgent",
    "MemoryLookupAgent",
    "OptimizationAgent",
    "SEOResearchAgent",
    "OfferLookupAgent",
    "ContentPlannerAgent",
    "PublisherAgent",
    "InstagramMarketingAgent",
    "TikTokMarketingAgent",
    "TwitterMarketingAgent",
    "PlatformComplianceAgent",
    "OrganicTrafficGrowthHackerAgent",
    "FreeImageGeneratorAgent",
    "FreeVideoProducerAgent",
    "MetaOrchestratorAgent",
    "StrategyEvolutionAgent",
    "AgentPerformanceMonitor",
    "SelfHealingAgent",
    "CircuitBreaker",
    "EvolutionEngine",
    "AgentFactory",
    "CinematicImageAgent",
    "CinematicVideoAgent",
    "AudioProductionAgent",
    "MediaPipelineAgent",
    "StoryboardAgent",
    "ContentExcellenceAgent",
    "StorytellingSpecialistAgent",
    "PsychologySpecialistAgent",
    "NeuromarketingSpecialistAgent",
    "GovernanceAgent",
    "TrafficRecyclerAgent",
    "EpistemicAgent",
    "ObserverFusionAgent",
    "ValueEvolutionAgent",
    "RecursiveObserverAgent",
    "ThirdOrderOrchestrator",
    "ConstraintGraph",
    "ConstraintNode",
    "ConstraintAwareWorkflow",
    "ConstraintDetector",
    "build_default_constraint_graph",
    "diagnose",
    "WorldModel",
    "WorldState",
    "Action",
    "StatePredictor",
    "ScenarioSimulator",
    "CounterfactualEngine",
    "EconomicEngine",
    "CapitalAllocationEngine",
    "ChannelROIModel",
    "OpportunityCostEngine",
    "PortfolioSummary",
    "AllocationDecision",
    "InvestmentStrategy",
    "AgentEvolutionEngine",
    "AgentGenome",
    "MutationEngine",
    "SelectionEngine",
    "AgentBreeder",
    "DigitalTwin",
    "SystemSnapshot",
    "ExperimentResult",
    "ValidationResult",
    "DeploymentPlan",
    "SnapshotManager",
    "ExperimentRunner",
    "ExperimentValidator",
    "SafeDeployer",
    "SelfImprovementEngine",
    "SelfDiagnosis",
    "DiagnosisReport",
    "Finding",
    "ImprovementPlan",
    "ConstraintGenealogy",
    "GenealogyStore",
    "GenealogyNode",
    "GenealogyPath",
    "CausalTracer",
    "GenealogyBuilder",
    "CognitiveMesh",
    "MessageBus",
    "MeshMessage",
    "MeshAgent",
    "Hypothesis",
    "HypothesisShare",
    "Belief",
    "BeliefPropagation",
    "OrganizationAgent",
    "OrganizationState",
    "OrganizationMemory",
    "DepartmentRegistry",
    "Department",
    "Objective",
    "DepartmentRole",
    "ObjectiveStatus",
    "OrganizationPhase",
    "Patch",
    "ContentResearchAgent",
    "SEOContentWriterAgent",
    "EEATValidatorAgent",
    "SEOTechnicalAgent",
    "SEOMultimediaAgent",
    "InternalLinkerAgent",
    "SitePublisherAgent",
    "DigitalProductAgent",
    "MembershipAgent",
    "AffiliateLinkInserterAgent",
    "RevenueOrchestratorAgent",
    "GenericAffiliateNetworkAgent",
    "AdSenseAgent",
    "CPAAgent",
    "PaidTrafficOrchestratorAgent",
    "BudgetOptimizerAgent",
    "GoogleAdsAgent",
    "MetaAdsAgent",
    "NativeAdsAgent",
    "AdCopyGeneratorAgent",
    "LandingPageAgent",
    "PerformanceTrackerAgent",
    "SocialPublishingOrchestratorAgent",
    "YouTubePublisherAgent",
    "TwitterPublisherAgent",
    "InstagramPublisherAgent",
    "TikTokPublisherAgent",
    "PinterestPublisherAgent",
    "LinkedInPublisherAgent",
    "TelegramPublisherAgent",
    "FacebookPublisherAgent",
    "BrowserAutomationAgent",
    "PortfolioOptimizerAgent",
    "CompoundingEngine",
    "OpportunityDetectorAgent",
    "CrossPollinationHub",
    "KnowledgeSynthesisBridge",
    "HotmartLinkManagerAgent",
    "ProductMatcherAgent",
    "AffiliateConfigUpdaterAgent",
    "LinkValidatorAgent",
    "KollektivAgent",
    "TemporalEngineAgent",
    "CreativeEngine",
    "NicheGenesisAgent",
    "NovelValueGenerator",
    "SafeMassPostingAgent",
    "DesignSystem",
    "DesignToken",
    "ColorToken",
    "TypographyToken",
    "SpacingToken",
    "ComponentSpec",
    "LayoutSpec",
    "DesignSystemRegistry",
    "load_design_system",
    "default_lyzer_design_system",
    "ArtifactGenerator",
    "ArtifactSpec",
    "ArtifactType",
    "ArtifactResult",
    "LandingPageGenerator",
    "LandingPageSpec",
    "DashboardGenerator",
    "DashboardSpec",
    "MetricCard",
    "ChartSpec",
    "ChartType",
    "EmailTemplateGenerator",
    "EmailSpec",
    "PresentationGenerator",
    "PresentationSpec",
    "SlideSpec",
    "SlideType",
    "LYZER_COLORS",
    "LYZER_GRADIENTS",
    "generate_css_variables",
    "generate_tailwind_config",
    "free_llm_providers",
    "free_content_generator",
    "media_providers",
    "model_router",
    "trace_store",
    "workflow_checkpoint",
    "evaluation_engine",
    "capability_registry",
]
