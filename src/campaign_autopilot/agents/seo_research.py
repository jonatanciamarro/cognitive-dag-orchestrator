"""Agente de pesquisa SEO — palavras-chave, tópicos, volume, dificuldade."""

from __future__ import annotations

from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


# Simulação de dados de SEO para demonstração.
# Em produção, integrar com: Ahrefs API, Semrush API, Google Keyword Planner, etc.
_SIMULATED_KEYWORDS: dict[str, list[dict[str, Any]]] = {
    "marketing digital": [
        {
            "keyword": "marketing digital para iniciantes",
            "volume": 5400,
            "difficulty": 0.35,
            "intent": "informational",
        },
        {
            "keyword": "ferramentas marketing digital gratuitas",
            "volume": 3200,
            "difficulty": 0.28,
            "intent": "commercial",
        },
        {
            "keyword": "curso marketing digital online",
            "volume": 8900,
            "difficulty": 0.72,
            "intent": "transactional",
        },
        {
            "keyword": "marketing digital para pequenas empresas",
            "volume": 2800,
            "difficulty": 0.30,
            "intent": "informational",
        },
        {
            "keyword": "estratégia marketing digital 2026",
            "volume": 4100,
            "difficulty": 0.45,
            "intent": "informational",
        },
        {
            "keyword": "o que é marketing digital",
            "volume": 12000,
            "difficulty": 0.55,
            "intent": "informational",
        },
    ],
    "afiliados": [
        {
            "keyword": "ganhar dinheiro como afiliado",
            "volume": 9800,
            "difficulty": 0.65,
            "intent": "commercial",
        },
        {
            "keyword": "programa de afiliados para iniciantes",
            "volume": 6200,
            "difficulty": 0.40,
            "intent": "commercial",
        },
        {
            "keyword": "melhores programas de afiliados 2026",
            "volume": 4800,
            "difficulty": 0.38,
            "intent": "commercial",
        },
        {
            "keyword": "como ser afiliado do zero",
            "volume": 7200,
            "difficulty": 0.42,
            "intent": "informational",
        },
        {
            "keyword": "afiliado amazon brasil",
            "volume": 3600,
            "difficulty": 0.25,
            "intent": "commercial",
        },
        {
            "keyword": "comissão afiliado hotmart",
            "volume": 2900,
            "difficulty": 0.22,
            "intent": "commercial",
        },
    ],
    "produtividade": [
        {
            "keyword": "aumentar produtividade no trabalho",
            "volume": 4500,
            "difficulty": 0.30,
            "intent": "informational",
        },
        {
            "keyword": "ferramentas de produtividade",
            "volume": 3800,
            "difficulty": 0.25,
            "intent": "commercial",
        },
        {
            "keyword": "metodo pomodoro",
            "volume": 8200,
            "difficulty": 0.15,
            "intent": "informational",
        },
        {
            "keyword": "organização pessoal e produtividade",
            "volume": 2100,
            "difficulty": 0.20,
            "intent": "informational",
        },
    ],
    "financas": [
        {
            "keyword": "como economizar dinheiro",
            "volume": 15000,
            "difficulty": 0.50,
            "intent": "informational",
        },
        {
            "keyword": "melhores investimentos 2026",
            "volume": 8800,
            "difficulty": 0.60,
            "intent": "commercial",
        },
        {
            "keyword": "planilha de orçamento pessoal",
            "volume": 4200,
            "difficulty": 0.18,
            "intent": "commercial",
        },
        {
            "keyword": "renda extra online",
            "volume": 12000,
            "difficulty": 0.55,
            "intent": "commercial",
        },
        {
            "keyword": "curso educação financeira",
            "volume": 5600,
            "difficulty": 0.48,
            "intent": "transactional",
        },
    ],
    "tecnologia": [
        {
            "keyword": "melhores notebooks 2026",
            "volume": 9200,
            "difficulty": 0.58,
            "intent": "commercial",
        },
        {
            "keyword": "smartphones custo beneficio",
            "volume": 11000,
            "difficulty": 0.52,
            "intent": "commercial",
        },
        {
            "keyword": "inteligencia artificial o que é",
            "volume": 18000,
            "difficulty": 0.42,
            "intent": "informational",
        },
        {
            "keyword": "cursos de programacao online",
            "volume": 7500,
            "difficulty": 0.48,
            "intent": "transactional",
        },
    ],
    "saude": [
        {
            "keyword": "emagrecer rapido",
            "volume": 22000,
            "difficulty": 0.70,
            "intent": "commercial",
        },
        {
            "keyword": "alimentacao saudavel",
            "volume": 9800,
            "difficulty": 0.35,
            "intent": "informational",
        },
        {
            "keyword": "melhores suplementos alimentares",
            "volume": 6200,
            "difficulty": 0.42,
            "intent": "commercial",
        },
        {
            "keyword": "exercicios em casa",
            "volume": 15000,
            "difficulty": 0.25,
            "intent": "informational",
        },
    ],
}


class SEOResearchAgent(AgentBase):
    """Pesquisa palavras-chave, analisa volume e dificuldade, sugere tópicos."""

    def __init__(self, **kwargs) -> None:
        super().__init__("seo_research", **kwargs)

    def _search_keywords(self, topic: str) -> list[dict[str, Any]]:
        """Busca keywords simuladas para um tópico."""
        topic_lower = topic.lower()
        results = []
        for seed, kws in _SIMULATED_KEYWORDS.items():
            if seed in topic_lower or topic_lower in seed:
                results.extend(kws)
        if not results:
            results = _SIMULATED_KEYWORDS.get("marketing digital", [])
        return results

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        channels = list(campaign.get("channels", ["seo"]))

        # Pesquisar keywords
        keywords = self._search_keywords(niche)

        # Filtrar por dificuldade baixa/média (oportunidades rápidas)
        opportunities = [kw for kw in keywords if kw["difficulty"] < 0.50]
        opportunities.sort(key=lambda x: -x["volume"])

        # Sugerir tópicos baseados nas keywords
        topics = []
        for kw in opportunities[:8]:
            topics.append(
                {
                    "keyword": kw["keyword"],
                    "volume": kw["volume"],
                    "difficulty": kw["difficulty"],
                    "intent": kw["intent"],
                    "suggested_type": "article"
                    if kw["intent"] == "informational"
                    else "review"
                    if kw["intent"] == "commercial"
                    else "tutorial",
                    "estimated_monthly_traffic": round(
                        kw["volume"] * (1 - kw["difficulty"])
                    ),
                }
            )

        # Análise por canal
        channel_analysis = {}
        for ch in channels:
            channel_keywords = [kw for kw in keywords if ch in str(kw)]
            channel_analysis[ch] = {
                "total_keywords": len(keywords),
                "opportunities": len(opportunities),
                "avg_difficulty": round(
                    sum(kw["difficulty"] for kw in keywords) / len(keywords), 2
                )
                if keywords
                else 0,
            }

        output = {
            "niche": niche,
            "channels_analyzed": channels,
            "total_keywords_found": len(keywords),
            "opportunities_count": len(opportunities),
            "top_opportunities": topics[:5],
            "channel_analysis": channel_analysis,
            "recommendation": (
                "Focar em keywords com dificuldade < 0.40 para resultados rápidos. "
                "Produzir conteúdo informacional primeiro (alto volume, baixa dificuldade), "
                "depois artigos comerciais com links de afiliado."
            ),
        }

        # Registrar explicação
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="seo_research",
                input_state={"niche": niche, "channels": channels},
            )
            for i, kw in enumerate(opportunities[:5]):
                self.explanation_store.record_rule_application(
                    decision_id=decision_id,
                    rule_source=f"seo.opportunity_{i}",
                    rule_value="difficulty < 0.50",
                    actual_value=kw["difficulty"],
                    comparison_result=True,
                    rule_order=i + 1,
                )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "opportunities": len(opportunities),
                    "top_keyword": opportunities[0]["keyword"] if opportunities else "",
                },
            )

        # Extrair conhecimento semântico
        if self.semantic_memory and opportunities:
            niche_concept_id = self.semantic_memory.register_concept(
                niche, "niche", f"Nicho de mercado: {niche}"
            )
            for kw in opportunities[:3]:
                kw_concept_id = self.semantic_memory.register_concept(
                    f"kw_{kw['keyword'][:30]}",
                    "keyword",
                    f"Volume: {kw['volume']}, Dificuldade: {kw['difficulty']}",
                )
                self.semantic_memory.assert_claim(
                    subject=niche_concept_id,
                    predicate="has_keyword",
                    object=kw_concept_id,
                    confidence=1.0 - kw["difficulty"],
                    evidence_type="STATISTICAL_INFERENCE",
                    epistemic_status="INFERRED",
                    supporting_data=kw,
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="seo_research",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Pesquisou {len(keywords)} keywords no nicho '{niche}', encontrou {len(opportunities)} oportunidades"
            ],
            metadata={
                "niche": niche,
                "keywords_found": len(keywords),
                "opportunities": len(opportunities),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
