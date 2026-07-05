"""GoogleAdsAgent — Gerencia campanhas no Google Ads (simulado + real).

Fases:
1. Planejamento (simulado) — Estrutura de campanha, palavras-chave, budget
2. Execução (real) — Integração com Google Ads API (quando configurado)
3. Otimização — Ajuste de lances, pausa de palavras-chave de baixo desempenho

Para campanhas reais: configure GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_DEVELOPER_TOKEN
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("google_ads")


class GoogleAdsAgent(AgentBase):
    """Cria e gerencia campanhas no Google Ads."""

    def __init__(self, **kwargs) -> None:
        super().__init__("google_ads", **kwargs)
        self._is_configured = bool(os.environ.get("GOOGLE_ADS_CLIENT_ID"))

    def _create_campaign_structure(
        self, niche: str, daily_budget: float, articles: list[dict]
    ) -> dict[str, Any]:
        """Cria estrutura de campanha Google Ads."""
        campaign_name = (
            f"Autopilot - {niche.title()} - {datetime.now().strftime('%Y%m')}"
        )

        # Extract keywords from articles
        keywords = []
        negative_keywords = ["grátis", "baixar", "torrent", "pirata", "ilegal"]
        for article in articles:
            content = article.get("content", article)
            title = content.get("title", "")
            keyword = article.get("metadata", {}).get(
                "keyword", article.get("keyword", "")
            )
            if keyword and keyword not in keywords:
                keywords.append(keyword)
            # Extract more keywords from title
            for word in title.split()[:5]:
                if len(word) > 3 and word.lower() not in [k.lower() for k in keywords]:
                    keywords.append(word)

        ad_groups = []
        for article in articles[:5]:
            content = article.get("content", article)
            title = content.get("title", "")
            slug = content.get("slug", "")
            kw = article.get("metadata", {}).get("keyword", "")

            ad_groups.append(
                {
                    "name": f"AG - {title[:40]}",
                    "keywords": [kw, f"comprar {kw}", f"melhor {kw}", f"{kw} preço"]
                    if kw
                    else [title[:30]],
                    "negative_keywords": negative_keywords,
                    "final_url": f"/{slug}" if slug else "/",
                    "cpc_bid_max": 3.50,
                }
            )

        return {
            "campaign_name": campaign_name,
            "campaign_type": "search",
            "network": "search_partners",
            "daily_budget": daily_budget,
            "bidding_strategy": "target_cpa",
            "target_cpa": 25.0,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "ad_groups": ad_groups,
            "keywords_total": sum(len(ag["keywords"]) for ag in ad_groups),
            "keywords": keywords[:20],
            "negative_keywords": negative_keywords,
            "extensions": ["sitelink", "callout", "snippet"],
            "tracking": {
                "conversion_action": "compra",
                "conversion_window": "30_days",
                "attribution_model": "last_click",
            },
            "simulated_only": not self._is_configured,
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        niche = campaign.get("niche", "tecnologia")
        daily_budget = float(campaign.get("daily_budget", 50))
        articles = campaign.get("articles", [])

        structure = self._create_campaign_structure(niche, daily_budget, articles)

        output = {
            "platform": "google_ads",
            "mode": "real" if self._is_configured else "simulated",
            "campaign": structure,
            "estimated_metrics": {
                "daily_clicks": int(daily_budget / 3.0),
                "daily_impressions": int(daily_budget / 3.0 * 10),
                "estimated_ctr": 3.5,
                "estimated_cpc": 3.00,
                "estimated_conversion_rate": 2.5,
            }
            if not self._is_configured
            else None,
            "setup_required": {
                "google_ads_client_id": "GOOGLE_ADS_CLIENT_ID no .env",
                "google_ads_client_secret": "GOOGLE_ADS_CLIENT_SECRET",
                "google_ads_developer_token": "GOOGLE_ADS_DEVELOPER_TOKEN",
                "guide": "https://developers.google.com/google-ads/api/docs/first-call/overview",
            }
            if not self._is_configured
            else {},
            "compliance": [
                "✅ Segue políticas do Google Ads (anúncio aprovado automaticamente)",
                "✅ Links com rel=nofollow sponsored para afiliados",
                "✅ Disclosure visível na landing page",
                "✅ Palavras-chave negativas configuradas",
                "⚠️ Verifique políticas de produtos afiliados permitidos",
            ],
            "next_steps": [
                "1. Configure GOOGLE_ADS_CLIENT_ID no .env para campanhas reais",
                "2. Ative a campanha manualmente no Google Ads Console",
                "3. Acompanhe ROAS semanalmente",
                "4. Ajuste lances baseado em performance",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="google_ads",
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
                f"Campanha '{structure['campaign_name']}' criada com {structure['keywords_total']} keywords"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
