"""MembershipAgent — Gerencia assinaturas, conteúdo exclusivo e comunidade paga.

Modelos de receita recorrente:
- Assinatura mensal (Patreon-style)
- Conteúdo premium (artigos exclusivos, vídeos)
- Comunidade (grupo fechado, mentoria em grupo)
- Newsletter paga (Substack-style)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("membership")


MEMBERSHIP_TIERS = {
    "free": {
        "name": "Grátis",
        "price_monthly": 0,
        "benefits": [
            "Newsletter semanal",
            "Acesso a 5 artigos/mês",
            "Conteúdo do blog",
        ],
    },
    "basic": {
        "name": "Básico",
        "price_monthly": 19.90,
        "benefits": [
            "Newsletter exclusiva (3x/semana)",
            "Acesso ilimitado a artigos",
            "E-book mensal",
            "Comunidade no WhatsApp",
        ],
    },
    "premium": {
        "name": "Premium",
        "price_monthly": 49.90,
        "benefits": [
            "Tudo do Básico",
            "Grupo exclusivo Telegram",
            "Encontros mensais ao vivo",
            "Mentoria em grupo (1x/mês)",
            "Desconto em todos os produtos",
        ],
    },
    "vip": {
        "name": "VIP",
        "price_monthly": 97.00,
        "benefits": [
            "Tudo do Premium",
            "Mentoria individual (1x/mês)",
            "Acesso a conteúdo PLR",
            "Indicação nos agradecimentos",
            "Sorteios e brindes exclusivos",
        ],
    },
}


class MembershipAgent(AgentBase):
    """Gerencia planos de assinatura e conteúdo exclusivo."""

    def __init__(self, **kwargs) -> None:
        super().__init__("membership", **kwargs)

    def recommend_tiers(
        self, niche: str, audience_size: int = 0
    ) -> list[dict[str, Any]]:
        """Recomenda planos de assinatura baseados no nicho."""
        recommendations = []
        for tier_id, tier in MEMBERSHIP_TIERS.items():
            if tier_id == "free":
                continue
            recommendations.append(
                {
                    "id": tier_id,
                    "name": tier["name"],
                    "price_monthly": tier["price_monthly"],
                    "price_yearly": round(
                        tier["price_monthly"] * 10, 2
                    ),  # 2 months free
                    "benefits": tier["benefits"],
                    "estimated_conversion_rate": self._estimate_conversion(
                        tier_id, niche
                    ),
                    "estimated_revenue_per_1000_visitors": round(
                        tier["price_monthly"]
                        * self._estimate_conversion(tier_id, niche)
                        * 1000
                    ),
                }
            )
        return recommendations

    def _estimate_conversion(self, tier: str, niche: str) -> float:
        """Estima taxa de conversão para cada tier."""
        rates = {
            "basic": {
                "default": 0.02,
                "financas": 0.03,
                "tecnologia": 0.015,
                "saude": 0.025,
                "carreira": 0.02,
            },
            "premium": {
                "default": 0.005,
                "financas": 0.008,
                "tecnologia": 0.004,
                "saude": 0.006,
                "carreira": 0.005,
            },
            "vip": {
                "default": 0.001,
                "financas": 0.002,
                "tecnologia": 0.001,
                "saude": 0.0015,
                "carreira": 0.001,
            },
        }
        niche_rates = rates.get(tier, {})
        return niche_rates.get(niche.lower(), niche_rates.get("default", 0.01))

    def generate_exclusive_content(
        self, tier: str, niche: str, keyword: str
    ) -> dict[str, Any]:
        """Gera descrição de conteúdo exclusivo para cada tier."""
        content_by_tier = {
            "basic": {
                "type": "artigo_aprofundado",
                "title": f"Análise Avançada: {keyword}",
                "description": f"Versão estendida do artigo sobre {keyword} com dados exclusivos.",
                "frequency": "semanal",
            },
            "premium": {
                "type": "video_aula",
                "title": f"Masterclass: {keyword} Passo a Passo",
                "description": f"Aula completa sobre {keyword} com material de apoio.",
                "frequency": "quinzenal",
            },
            "vip": {
                "type": "mentoria",
                "title": f"Mentoria Exclusiva: Estratégias de {keyword}",
                "description": f"Sessão ao vivo de 60 min sobre {keyword} com especialista.",
                "frequency": "mensal",
            },
        }
        return content_by_tier.get(tier, content_by_tier["basic"])

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        niche = str(campaign.get("niche", "tecnologia"))
        audience = int(campaign.get("estimated_audience", 0))

        recommended = self.recommend_tiers(niche, audience)
        total_monthly = sum(
            t["price_monthly"] * t["estimated_conversion_rate"] * max(audience, 1000)
            for t in recommended
        )

        # Generate exclusive content samples
        keyword = campaign.get("keyword", niche)
        content_samples = {}
        for tier in recommended:
            content_samples[tier["id"]] = self.generate_exclusive_content(
                tier["id"], niche, keyword
            )

        output = {
            "niche": niche,
            "audience": max(audience, 1000),
            "recommended_tiers": recommended,
            "content_samples": content_samples,
            "estimated_revenue": {
                "monthly_subscribers": {
                    t["name"]: round(
                        max(audience, 1000) * t["estimated_conversion_rate"]
                    )
                    for t in recommended
                },
                "total_monthly_mrr": round(total_monthly, 2),
                "total_yearly_arr": round(total_monthly * 12, 2),
            },
            "setup_steps": [
                "Criar landing page de assinatura",
                "Configurar gateway de pagamento (Stripe/Mercado Pago)",
                "Criar área de membros no site",
                "Produzir conteúdo exclusivo inicial (4 semanas)",
                "Configurar sequência de onboarding para novos membros",
            ],
            "recommendations": [
                "Começar com tier Básico (R$19,90) para testar o mercado",
                "Usar email marketing para promover a assinatura",
                "Oferecer primeiro mês grátis para atrair membros iniciais",
                "Criar conteúdo exclusivo de alto valor antes de lançar",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="membership",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Criou plano de assinatura para {niche}: R${total_monthly:.0f}/mês estimado"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _utcnow_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))
