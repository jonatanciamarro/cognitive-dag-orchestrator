"""Hotmart Agent Package — Automacao de coleta, gestao e selecao de links de afiliado."""

from .link_manager import HotmartLinkManagerAgent
from .product_matcher import ProductMatcherAgent
from .config_updater import AffiliateConfigUpdaterAgent
from .link_validator import LinkValidatorAgent
from .product_researcher import (
    HotmartProductResearcherAgent,
    HotmartAffiliateSelectorAgent,
)
from .marketplace_collector import HotmartMarketplaceAgent

__all__ = [
    "HotmartLinkManagerAgent",
    "ProductMatcherAgent",
    "AffiliateConfigUpdaterAgent",
    "LinkValidatorAgent",
    "HotmartProductResearcherAgent",
    "HotmartAffiliateSelectorAgent",
    "HotmartMarketplaceAgent",
]
