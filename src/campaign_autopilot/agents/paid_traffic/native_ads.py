"""NativeAdsAgent — Gerencia campanhas de native ads (Taboola, Outbrain).

Native ads são anúncios nativos recomendados como "conteúdo patrocinado"
em sites de notícias. Ótimos para reconhecimento de marca e topo de funil.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("native_ads")


class NativeAdsAgent(AgentBase):
    """Cria e gerencia campanhas de native ads (Taboola/Outbrain)."""

    def __init__(self, **kwargs) -> None:
        super().__init__("native_ads", **kwargs)
        self._is_configured = bool(os.environ.get("TABOOLA_ACCOUNT_ID"))

    def _create_campaign_structure(
        self, niche: str, daily_budget: float, articles: list[dict]
    ) -> dict[str, Any]:
        """Cria estrutura de campanha de native ads."""
        campaign_name = f"Native_{niche}_{datetime.now().strftime('%Y%m')}"

        # Native ads performam melhor com conteúdo editorial (não venda direta)
        promoted_content = []
        for article in articles[:5]:
            content = article.get("content", article)
            title = content.get("title", "")
            slug = content.get("slug", "")
            promoted_content.append(
                {
                    "title": title[:60],
                    "url": f"/{slug}" if slug else "/",
                    "thumbnail": "",  # URL da imagem
                }
            )

        return {
            "campaign_name": campaign_name,
            "campaign_type": "content_recommendation",
            "daily_budget": daily_budget,
            "platforms": ["taboola", "outbrain"],
            "objective": "awareness",
            "targeting": {
                "locations": ["BR"],
                "device": ["desktop", "mobile"],
                "os": ["windows", "macos", "android", "ios"],
            },
            "promoted_content": promoted_content,
            "optimization_goal": "engaged_visitors",
            "tracking": {"pixel_url": "", "conversion_window": "1_day_click"},
            "content_guidelines": [
                "Headline: 50-60 chars com curiosidade",
                "Imagem: 1200×628px, texto < 20% da imagem",
                "Tom editorial (não parece anúncio)",
                "CTA sutil: 'Saiba Mais' ou 'Descubra'",
            ],
            "simulated_only": not self._is_configured,
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        niche = campaign.get("niche", "tecnologia")
        daily_budget = float(campaign.get("daily_budget", 10))
        articles = campaign.get("articles", [])

        structure = self._create_campaign_structure(niche, daily_budget, articles)

        output = {
            "platform": "native_ads",
            "mode": "real" if self._is_configured else "simulated",
            "campaign": structure,
            "estimated_metrics": {
                "daily_clicks": int(daily_budget / 1.50),
                "daily_impressions": int(daily_budget / 1.50 * 50),
                "estimated_ctr": 0.8,
                "estimated_cpc": 1.50,
                "estimated_ecpm": 8.00,
            }
            if not self._is_configured
            else None,
            "setup_required": {
                "taboola_account_id": "TABOOLA_ACCOUNT_ID no .env",
                "taboola_api_key": "TABOOLA_API_KEY",
                "guide": "https://developers.taboola.com/",
            }
            if not self._is_configured
            else {},
            "best_practices": [
                "Use headlines que parecem notícias reais (não anúncio)",
                "Imagens autênticas performam melhor que stock photos",
                "Teste 5+ headlines diferentes por conteúdo",
                "Native ads são melhores para topo de funil",
                "Combine com remarketing para conversão",
            ],
            "next_steps": [
                "1. Configure TABOOLA_ACCOUNT_ID para campanhas reais",
                "2. Crie thumbnails para cada conteúdo promovido",
                "3. Lance campanha com budget mínimo (R$ 10/dia)",
                "4. Acompanhe CTR e engaged visitors",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="native_ads",
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
                f"Campanha native '{structure['campaign_name']}' com {len(structure['promoted_content'])} conteúdos"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
