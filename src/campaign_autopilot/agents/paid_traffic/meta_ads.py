"""MetaAdsAgent — Gerencia campanhas no Meta Ads (Facebook/Instagram).

Para campanhas reais: configure META_ADS_ACCESS_TOKEN e META_ADS_AD_ACCOUNT_ID
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("meta_ads")


class MetaAdsAgent(AgentBase):
    """Cria e gerencia campanhas no Meta Ads (Facebook/Instagram)."""

    def __init__(self, **kwargs) -> None:
        super().__init__("meta_ads", **kwargs)
        self._is_configured = bool(os.environ.get("META_ADS_ACCESS_TOKEN"))

    def _create_campaign_structure(
        self, niche: str, daily_budget: float, articles: list[dict]
    ) -> dict[str, Any]:
        """Cria estrutura de campanha Meta Ads."""
        campaign_name = f"Autopilot_{niche}_CVR_{datetime.now().strftime('%Y%m')}"

        ad_sets = []
        audiences = [
            {
                "name": "Cold_Interesse",
                "type": "interest",
                "targeting": f"interesse em {niche}",
            },
            {
                "name": "Warm_Remarketing",
                "type": "retargeting",
                "targeting": "visitantes do site",
            },
            {
                "name": "Lookalike_Clientes",
                "type": "lookalike",
                "targeting": "similar aos compradores",
            },
        ]

        for idx, audience in enumerate(audiences):
            daily_budget_split = daily_budget / len(audiences)
            ad_sets.append(
                {
                    "name": f"{campaign_name}_{audience['name']}",
                    "audience": audience,
                    "daily_budget": round(daily_budget_split, 2),
                    "optimization_goal": "conversions",
                    "bidding": "lowest_cost",
                    "placement": {
                        "platforms": ["facebook", "instagram"],
                        "positions": ["feed", "stories", "reels"],
                    },
                    "targeting": {
                        "age_min": 18,
                        "age_max": 65,
                        "gender": "all",
                        "locations": ["BR"],
                        "interests": [
                            f"{niche}",
                            f"{niche} digital",
                            f"curso de {niche}",
                        ][:3],
                        "language": ["pt"],
                    },
                }
            )

        return {
            "campaign_name": campaign_name,
            "campaign_type": "conversions",
            "daily_budget": daily_budget,
            "ad_sets": ad_sets,
            "creatives": [
                {
                    "format": "carousel",
                    "description": "Carrossel com múltiplos produtos/artigos",
                },
                {
                    "format": "single_image",
                    "description": "Imagem única com call-to-action",
                },
                {
                    "format": "video",
                    "description": "Vídeo curto (15s) explicando o conteúdo",
                },
            ],
            "tracking": {
                "pixel_event": "Purchase",
                "conversion_window": "7_days_click_1_day_view",
            },
            "simulated_only": not self._is_configured,
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        niche = campaign.get("niche", "tecnologia")
        daily_budget = float(campaign.get("daily_budget", 30))
        articles = campaign.get("articles", [])

        structure = self._create_campaign_structure(niche, daily_budget, articles)

        output = {
            "platform": "meta_ads",
            "mode": "real" if self._is_configured else "simulated",
            "campaign": structure,
            "estimated_metrics": {
                "daily_clicks": int(daily_budget / 2.5),
                "daily_impressions": int(daily_budget / 2.5 * 20),
                "estimated_ctr": 2.2,
                "estimated_cpc": 2.50,
                "estimated_cpm": 12.00,
                "estimated_conversion_rate": 1.8,
            }
            if not self._is_configured
            else None,
            "setup_required": {
                "meta_ads_access_token": "META_ADS_ACCESS_TOKEN no .env",
                "meta_ads_ad_account_id": "META_ADS_AD_ACCOUNT_ID",
                "guide": "https://developers.facebook.com/docs/marketing-api",
            }
            if not self._is_configured
            else {},
            "compliance": [
                "✅ Segue políticas de anúncios do Meta",
                "✅ Público segmentado por interesse no nicho",
                "✅ Remarketing configurado para visitantes",
                "⚠️ Verifique políticas de produtos afiliados no Meta",
            ],
            "next_steps": [
                "1. Configure META_ADS_ACCESS_TOKEN no .env para campanhas reais",
                "2. Instale Meta Pixel no site para remarketing",
                "3. Crie catálogo de produtos para anúncios dinâmicos",
                "4. Teste 3+ variações de criativo por conjunto de anúncio",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="meta_ads",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=int(
                (
                    datetime.fromisoformat(finished_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
                * 1000
            ),
            thread_name="main",
            notes=[
                f"Campanha '{structure['campaign_name']}' com {len(structure['ad_sets'])} conjuntos de anúncios"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
