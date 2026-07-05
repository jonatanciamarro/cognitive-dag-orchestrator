"""OpportunityDetectorAgent — 2ª Ordem: Detecta novas oportunidades de receita automaticamente.

Monitora:
- Novos programas de afiliados no nicho
- Produtos digitais com alta demanda
- Nichos com baixa concorrência e alto CPC
- Tendências de busca emergentes
- Gaps de conteúdo que concorrentes não exploraram
"""

from __future__ import annotations

from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("opportunity_detector")


class OpportunityDetectorAgent(AgentBase):
    """Detecta novas oportunidades de receita automaticamente — 2ª Ordem."""

    def __init__(self, **kwargs) -> None:
        super().__init__("opportunity_detector", **kwargs)

    def scan_opportunities(
        self, current_niche: str, existing_sources: list[str]
    ) -> dict[str, Any]:
        """Escaneia o mercado em busca de novas oportunidades."""
        # Simulação — em produção: integrar com APIs de mercado
        niches = {
            "tecnologia": {
                "trending": [
                    "IA para pequenas empresas",
                    "Notebooks com IA integrada",
                    "Segurança digital 2026",
                ],
                "gaps": [
                    "Guias para idosos",
                    "Comparativos de assinaturas de software",
                    "Reviews de produtos little-known",
                ],
                "high_cpc_keywords": [
                    "seguro cibernético",
                    "software gestão empresarial",
                    "consultoria TI",
                ],
                "new_affiliate_programs": ["HubSpot", "Semrush", "Canva Pro", "Notion"],
                "product_ideas": [
                    "Curso de IA para iniciantes",
                    "Template de gestão de projetos",
                    "Ebook de segurança digital",
                ],
            },
            "financas": {
                "trending": [
                    "Criptomoedas 2026",
                    "Renda extra com IA",
                    "Investimentos automáticos",
                ],
                "gaps": [
                    "Educação financeira para crianças",
                    "Planejamento para autônomos",
                    "Finanças para casais",
                ],
                "high_cpc_keywords": [
                    "consórcio",
                    "seguro de vida",
                    "cartão black",
                    "investimento exterior",
                ],
                "new_affiliate_programs": [
                    "Inter",
                    "C6 Bank",
                    "XP Investimentos",
                    "Binance",
                ],
                "product_ideas": [
                    "Planilha de investimentos",
                    "Curso de educação financeira",
                    "Ebook sair das dívidas",
                ],
            },
            "saude": {
                "trending": [
                    "Saúde mental home office",
                    "Suplementos naturais",
                    "Exercícios 10 minutos",
                ],
                "gaps": [
                    "Saúde para gestantes",
                    "Exercícios para idosos",
                    "Nutrição infantil",
                ],
                "product_ideas": [
                    "Guia de alimentação saudável",
                    "Checklist de exames preventivos",
                    "Ebook de receitas fit",
                ],
            },
            "carreira": {
                "trending": [
                    "Trabalho remoto 2026",
                    "Carreira em IA",
                    "Freelance internacional",
                ],
                "gaps": [
                    "Transição de carreira para tech",
                    "LinkedIn para introvertidos",
                    "Entrevistas em inglês",
                ],
                "product_ideas": [
                    "Template de currículo moderno",
                    "Curso de LinkedIn",
                    "Guia de entrevista em inglês",
                ],
            },
        }

        niche_data = niches.get(current_niche.lower(), {})
        if not niche_data:
            # Cross-niche opportunity
            all_trending = []
            for n, data in niches.items():
                all_trending.extend(data.get("trending", []))
            return {
                "cross_niche": True,
                "suggested_niches": list(niches.keys()),
                "trending_across_all": all_trending[:5],
            }

        return {
            "current_niche": current_niche,
            "trending_topics": niche_data.get("trending", []),
            "content_gaps": niche_data.get("gaps", []),
            "high_cpc_keywords": niche_data.get("high_cpc_keywords", []),
            "new_affiliate_programs": niche_data.get("new_affiliate_programs", []),
            "product_ideas": niche_data.get("product_ideas", []),
            "opportunity_score": self._calculate_opportunity_score(niche_data),
            "recommended_actions": self._recommend_actions(
                niche_data, existing_sources
            ),
        }

    def _calculate_opportunity_score(self, niche_data: dict) -> float:
        """Calcula score de oportunidade para o nicho."""
        score = 0.0
        if niche_data.get("trending"):
            score += 0.3
        if niche_data.get("gaps"):
            score += 0.2
        if niche_data.get("high_cpc_keywords"):
            score += 0.3
        if niche_data.get("new_affiliate_programs"):
            score += 0.1
        if niche_data.get("product_ideas"):
            score += 0.1
        return round(min(score, 1.0), 2)

    def _recommend_actions(
        self, niche_data: dict, existing_sources: list[str]
    ) -> list[str]:
        """Recomenda ações específicas baseadas nas oportunidades."""
        actions = []
        if niche_data.get("high_cpc_keywords"):
            actions.append(
                f"💰 Alta prioridade: criar conteúdo para keywords de alto CPC: {niche_data['high_cpc_keywords'][0]}"
            )
        if niche_data.get("new_affiliate_programs"):
            new = [
                p
                for p in niche_data["new_affiliate_programs"]
                if p not in existing_sources
            ]
            if new:
                actions.append(
                    f"🤝 Novo programa de afiliados: {new[0]} — alta comissão"
                )
        if niche_data.get("product_ideas"):
            actions.append(
                f"📦 Oportunidade de produto digital: {niche_data['product_ideas'][0]}"
            )
        if niche_data.get("content_gaps"):
            actions.append(
                f"📝 Gap de conteúdo: {niche_data['content_gaps'][0]} — sem concorrência forte"
            )
        if niche_data.get("trending"):
            actions.append(
                f"📈 Tendência emergente: {niche_data['trending'][0]} — primeiro mover"
            )
        return actions

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        current_niche = str(campaign.get("niche", "tecnologia"))
        existing_sources = campaign.get("existing_revenue_sources", [])

        scan = self.scan_opportunities(current_niche, existing_sources)

        output = {
            "scan": scan,
            "opportunities_found": len(scan.get("recommended_actions", [])),
            "vypočet_opportunity_score": scan.get("opportunity_score", 0),
            "actions": scan.get("recommended_actions", []),
            "new_sources_suggested": [
                {
                    "source": "adicionar_adsense",
                    "priority": "alta",
                    "effort": "3-4 ciclos",
                    "projected_monthly": "R$ 200-500 com 10k visitas",
                },
                {
                    "source": "criar_produto_digital",
                    "priority": "alta",
                    "effort": "2 ciclos",
                    "projected_monthly": "R$ 500-2000",
                },
                {
                    "source": "programa_afiliados_novo",
                    "priority": "média",
                    "effort": "1 ciclo",
                    "projected_monthly": "R$ 100-500",
                },
                {
                    "source": "licenciar_conteudo",
                    "priority": "baixa",
                    "effort": "1 ciclo",
                    "projected_monthly": "R$ 50-300",
                },
            ],
            "recommendation": (
                "Foco em keywords de alto CPC + novo produto digital = maior impacto imediato."
            ),
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="opportunity_scan",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Escaneou oportunidades em {current_niche}, encontrou {len(scan.get('recommended_actions', []))} ações"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _utcnow_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        from datetime import datetime

        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))
