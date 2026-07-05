from .base import AgentBase, AgentResult, AgentTrace, CampaignContext
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
from .circuit_breaker import CircuitBreaker
from .evolution_engine import EvolutionEngine
from .cinematic_image_agent import CinematicImageAgent
from .cinematic_video_agent import CinematicVideoAgent
from .cinematic_fiapi_agent import CinematicFIAPIAgent
from .audio_production_agent import AudioProductionAgent
from .media_pipeline_agent import MediaPipelineAgent
from .storyboard_agent import StoryboardAgent
from .agent_factory import AgentFactory
from .content_excellence_agent import ContentExcellenceAgent
from .storytelling_specialist import StorytellingSpecialistAgent
from .psychology_specialist import PsychologySpecialistAgent
from .neuromarketing_specialist import NeuromarketingSpecialistAgent
from .governance_agent import GovernanceAgent

from .traffic_recycler import TrafficRecyclerAgent
from .epistemic_agent import EpistemicAgent
from .observer_fusion_agent import ObserverFusionAgent
from .value_evolution_agent import ValueEvolutionAgent
from .recursive_observer_agent import RecursiveObserverAgent
from .third_order_orchestrator import ThirdOrderOrchestrator

__all__ = [
    "AgentBase",
    "AgentResult",
    "AgentTrace",
    "CampaignContext",
    "AnalyticsAgent",
    "ComplianceAgent",
    "MemoryLookupAgent",
    "OptimizationAgent",
    "SEOResearchAgent",
    "OfferLookupAgent",
    "ContentPlannerAgent",
    "PublisherAgent",
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
    "CinematicFIAPIAgent",
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
]


# ── News agents (ADR-002 — SEO algoritmo-centrado) ───────────
from .news import (
    ContentResearchAgent,
    SEOContentWriterAgent,
    EEATValidatorAgent,
    SEOTechnicalAgent,
    SEOMultimediaAgent,
    InternalLinkerAgent,
    SitePublisherAgent,
)

# ── Money agents (Onda 2 — Múltiplas fontes de renda) ─────
from .money import DigitalProductAgent, MembershipAgent, AffiliateLinkInserterAgent

# ── Revenue Agents (Onda 2 — 13 fontes de renda) ──────────
from .revenue import (
    RevenueOrchestratorAgent,
    GenericAffiliateNetworkAgent,
    AdSenseAgent,
    CPAAgent,
    RevenueMemory,
)

# ── Paid Traffic agents (Reinvestimento automático em tráfego pago) ──
from .paid_traffic import (
    RevenueMonitorAgent,
    BudgetOptimizerAgent,
    PaidTrafficOrchestratorAgent,
    GoogleAdsAgent,
    MetaAdsAgent,
    NativeAdsAgent,
    AdCopyGeneratorAgent,
    LandingPageAgent,
    PerformanceTrackerAgent,
)

# ── Social Media Publishers (Publicação automática em redes sociais) ──
from .social_publishers import (
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

# ── Paid Traffic agents (Reinvestimento automático em tráfego pago) ──

# ── Meta agents (2ª e 3ª Ordem — Otimização, evolução, transcendência) ──
from .meta import (
    PortfolioOptimizerAgent,
    CompoundingEngine,
    OpportunityDetectorAgent,
    CrossPollinationHub,
    AgentFactory,
    KnowledgeSynthesisBridge,
)

# ── Safe Mass Posting Agent (Publicação segura em massa) ──
from .kollektiv import KollektivAgent
from .temporal_engine import TemporalEngineAgent
from .creative_engine import CreativeEngine, NicheGenesisAgent, NovelValueGenerator
from .hotmart import (
    HotmartLinkManagerAgent,
    ProductMatcherAgent,
    AffiliateConfigUpdaterAgent,
    LinkValidatorAgent,
)
from .safe_mass_posting import SafeMassPostingAgent


# ── UI/UX Design Agents (21st.dev-style component generation) ──
from .ui_component_design import UIComponentDesignAgent
from .ui_hero_agent import UIHeroAgent
from .ui_pricing_agent import UIPricingAgent
from .ui_faq_agent import UIFAQAgent
from .ui_testimonial_agent import UITestimonialAgent
from .ui_full_page_agent import UIFullPageAgent
