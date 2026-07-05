"""Revenue Agents — Multiplas fontes de renda com protocolos E2E."""

from .base import RevenueBaseAgent, RevenueProtocol
from .memory import RevenueMemory, REVENUE_SOURCES
from .orchestrator import RevenueOrchestratorAgent
from .generic_affiliate import GenericAffiliateNetworkAgent
from .adsense import AdSenseAgent
from .cpa import CPAAgent
from .platform_products import (
    PLATFORM_LINK_PATTERNS,
    CURATED_PRODUCTS,
    get_products_by_niche,
    get_products_by_platform,
    get_all_platforms,
)
from .platform_agent import PlatformAffiliateAgent, AllPlatformsSetupAgent

__all__ = [
    "RevenueBaseAgent",
    "RevenueProtocol",
    "RevenueMemory",
    "REVENUE_SOURCES",
    "RevenueOrchestratorAgent",
    "GenericAffiliateNetworkAgent",
    "AdSenseAgent",
    "CPAAgent",
    "PlatformAffiliateAgent",
    "AllPlatformsSetupAgent",
    "get_products_by_niche",
    "get_products_by_platform",
    "get_all_platforms",
]
