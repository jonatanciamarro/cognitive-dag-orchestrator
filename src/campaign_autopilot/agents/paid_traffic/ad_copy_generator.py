"""AdCopyGeneratorAgent — Gera criativos de anúncio a partir do conteúdo existente.

Cria:
- Google Ads: 3 headlines, 2 descriptions, 15-30-30 chars
- Meta Ads: Primary text, headline, description (limit 125 chars)
- Native Ads: Headline + body (50-100 chars)
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("ad_copy_generator")


class AdCopyGeneratorAgent(AgentBase):
    """Gera criativos de anúncio para múltiplas plataformas."""

    def __init__(self, **kwargs) -> None:
        super().__init__("ad_copy_generator", **kwargs)

    def _truncate(self, text: str, max_len: int) -> str:
        """Trunca texto mantendo palavras completas."""
        if len(text) <= max_len:
            return text
        return text[:max_len].rsplit(" ", 1)[0] + "..."

    def _generate_google_ads(self, article: dict) -> list[dict]:
        """Gera criativos para Google Ads (Responsive Search Ad)."""
        content = article.get("content", article)
        title = content.get("title", "")
        intro = content.get("introduction", "")
        meta = content.get("meta_description", "")

        headlines = [
            self._truncate(title, 30),
            self._truncate(f"Melhor {title}", 30),
            self._truncate(f"Guia: {title}", 30),
            self._truncate(meta, 30),
            "Oferta Exclusiva",
            "Compre Agora",
            "Resultados Garantidos",
            f"{self._truncate(title, 25)} 2026",
            "Aproveite Agora",
            "Não Perca",
            "Melhor Preço",
            "Oferta Limitada",
            f"Descubra {self._truncate(title, 22)}",
            "Promoção Imperdível",
            f"Saiba Mais Sobre {self._truncate(title, 18)}",
        ]

        descriptions = [
            self._truncate(
                intro[:120]
                if len(intro) > 30
                else f"Confira o guia completo sobre {title}. Informações atualizadas e dicas exclusivas.",
                90,
            ),
            self._truncate(
                f"Descubra as melhores opções de {title}. Compare preços, leia reviews e encontre a melhor escolha para você.",
                90,
            ),
        ]

        return [
            {
                "platform": "google_ads",
                "type": "responsive_search_ad",
                "headlines": headlines[:15],
                "descriptions": descriptions,
                "final_url": content.get("slug", ""),
            },
        ]

    def _generate_meta_ads(self, article: dict) -> list[dict]:
        """Gera criativos para Meta Ads (Facebook/Instagram)."""
        content = article.get("content", article)
        title = content.get("title", "")
        intro = content.get("introduction", "")

        primary_texts = [
            self._truncate(f"{intro[:150]} Clique no link e confira!", 125),
            self._truncate(
                f"Guia completo sobre {title}. {intro[:100]} Saiba mais!", 125
            ),
            self._truncate(f"Você sabia? {intro[:120]} Descubra agora!", 125),
        ]

        return [
            {
                "platform": "meta_ads",
                "type": "feed_ad",
                "primary_text": pt,
                "headline": self._truncate(title, 40),
                "description": self._truncate(intro[:80], 30),
                "final_url": content.get("slug", ""),
            }
            for pt in primary_texts
        ]

    def _generate_native_ads(self, article: dict) -> list[dict]:
        """Gera criativos para native ads (Taboola/Outbrain)."""
        content = article.get("content", article)
        title = content.get("title", "")

        return [
            {
                "platform": "native_ads",
                "type": "content_recommendation",
                "headline": self._truncate(f"Você Não Vai Acreditar: {title}", 60),
                "body": self._truncate("Descubra o guia completo.", 100),
                "final_url": content.get("slug", ""),
            },
            {
                "platform": "native_ads",
                "type": "content_recommendation",
                "headline": self._truncate(f"{title}: O Guia Definitivo", 60),
                "body": self._truncate("Informações exclusivas e atualizadas.", 100),
                "final_url": content.get("slug", ""),
            },
        ]

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        platforms = campaign.get("platforms", ["google_ads", "meta_ads", "native_ads"])

        all_creatives = []
        for article in articles:
            creatives = []
            if "google_ads" in platforms:
                creatives.extend(self._generate_google_ads(article))
            if "meta_ads" in platforms:
                creatives.extend(self._generate_meta_ads(article))
            if "native_ads" in platforms:
                creatives.extend(self._generate_native_ads(article))
            all_creatives.extend(creatives)

        output = {
            "total_creatives": len(all_creatives),
            "creatives_by_platform": {
                plat: len([c for c in all_creatives if c["platform"] == plat])
                for plat in platforms
            },
            "creatives": all_creatives,
            "best_practices": [
                "Google Ads: Teste 3 headlines + 2 descrições por grupo de anúncio",
                "Meta Ads: Use imagens/vídeos de alta qualidade (1:1 ou 4:5)",
                "Native Ads: Headline curta com curiosidade (50-60 chars)",
                "A/B Teste: Sempre teste 2+ variações de criativo",
                "CTA: Inclua call-to-action claro em todos os anúncios",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="ad_copy_generator",
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
                f"{len(all_creatives)} criativos gerados para {len(platforms)} plataformas"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
