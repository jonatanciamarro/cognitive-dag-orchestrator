"""Paid Traffic Agents — Reinvestimento automático de lucro em tráfego pago.

Quando a receita orgânica atinge um threshold configurável, o sistema
automaticamente cria e gerencia campanhas de tráfego pago em múltiplas plataformas.

Fluxo:
1. RevenueMonitor detecta que atingiu threshold
2. BudgetOptimizer aloca % do lucro para tráfego pago
3. PaidTrafficOrchestrator coordena campanhas
4. Platform agents criam anúncios (Google Ads, Meta Ads, Native)
5. AdCopyGenerator cria criativos a partir do conteúdo existente
6. LandingPageAgent cria páginas de conversão
7. PerformanceTracker monitora ROAS e ajusta
"""

from .revenue_monitor import RevenueMonitorAgent
from .budget_optimizer import BudgetOptimizerAgent
from .paid_traffic_orchestrator import PaidTrafficOrchestratorAgent
from .google_ads import GoogleAdsAgent
from .meta_ads import MetaAdsAgent
from .native_ads import NativeAdsAgent
from .ad_copy_generator import AdCopyGeneratorAgent
from .landing_page import LandingPageAgent
from .performance_tracker import PerformanceTrackerAgent

__all__ = [
    "RevenueMonitorAgent",
    "BudgetOptimizerAgent",
    "PaidTrafficOrchestratorAgent",
    "GoogleAdsAgent",
    "MetaAdsAgent",
    "NativeAdsAgent",
    "AdCopyGeneratorAgent",
    "LandingPageAgent",
    "PerformanceTrackerAgent",
]
