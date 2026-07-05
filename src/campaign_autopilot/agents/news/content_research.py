"""ContentResearchAgent — Pesquisa palavras-chave, intenção, concorrência e gaps.

Baseado em ADR-002: modelo algoritmo-centrado para múltiplos buscadores.
"""

from __future__ import annotations

from typing import Any
import random

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("content_research")

# Simulated keyword database for demo
# In production: integrate with Google Keyword Planner, Ahrefs, Semrush APIs
_KEYWORD_DATA: dict[str, list[dict[str, Any]]] = {
    "tecnologia": [
        {
            "keyword": "melhores notebooks 2026",
            "volume": 9200,
            "difficulty": 0.58,
            "intent": "commercial",
            "cpc": 2.5,
        },
        {
            "keyword": "smartphones custo beneficio",
            "volume": 11000,
            "difficulty": 0.52,
            "intent": "commercial",
            "cpc": 1.8,
        },
        {
            "keyword": "inteligencia artificial o que é",
            "volume": 18000,
            "difficulty": 0.42,
            "intent": "informational",
            "cpc": 0.9,
        },
        {
            "keyword": "como escolher um notebook",
            "volume": 5400,
            "difficulty": 0.35,
            "intent": "informational",
            "cpc": 1.2,
        },
        {
            "keyword": "melhores celulares para fotos",
            "volume": 6800,
            "difficulty": 0.45,
            "intent": "commercial",
            "cpc": 2.1,
        },
        {
            "keyword": "hd externo recomendado",
            "volume": 3200,
            "difficulty": 0.28,
            "intent": "commercial",
            "cpc": 1.5,
        },
        {
            "keyword": "monitor para programador",
            "volume": 4100,
            "difficulty": 0.32,
            "intent": "commercial",
            "cpc": 1.9,
        },
        {
            "keyword": "teclado mecanico barato",
            "volume": 5800,
            "difficulty": 0.38,
            "intent": "commercial",
            "cpc": 1.4,
        },
        {
            "keyword": "roteador wifi potente",
            "volume": 4600,
            "difficulty": 0.30,
            "intent": "commercial",
            "cpc": 1.6,
        },
        {
            "keyword": "fone de ouvido sem fio",
            "volume": 7200,
            "difficulty": 0.48,
            "intent": "commercial",
            "cpc": 1.3,
        },
    ],
    "financas": [
        {
            "keyword": "como economizar dinheiro",
            "volume": 15000,
            "difficulty": 0.50,
            "intent": "informational",
            "cpc": 3.2,
        },
        {
            "keyword": "melhores investimentos 2026",
            "volume": 8800,
            "difficulty": 0.60,
            "intent": "commercial",
            "cpc": 4.5,
        },
        {
            "keyword": "renda extra online",
            "volume": 12000,
            "difficulty": 0.55,
            "intent": "commercial",
            "cpc": 5.0,
        },
        {
            "keyword": "como sair das dividas",
            "volume": 9800,
            "difficulty": 0.40,
            "intent": "informational",
            "cpc": 2.8,
        },
        {
            "keyword": "cartao de credito sem anuidade",
            "volume": 8200,
            "difficulty": 0.35,
            "intent": "commercial",
            "cpc": 6.0,
        },
        {
            "keyword": "investir com pouco dinheiro",
            "volume": 11000,
            "difficulty": 0.42,
            "intent": "informational",
            "cpc": 3.5,
        },
        {
            "keyword": "consorcio vale a pena",
            "volume": 6400,
            "difficulty": 0.38,
            "intent": "commercial",
            "cpc": 4.2,
        },
        {
            "keyword": "melhor conta digital",
            "volume": 7800,
            "difficulty": 0.30,
            "intent": "commercial",
            "cpc": 5.5,
        },
        {
            "keyword": "seguro de vida vale a pena",
            "volume": 5200,
            "difficulty": 0.45,
            "intent": "informational",
            "cpc": 7.0,
        },
        {
            "keyword": "financiamento imobiliario",
            "volume": 9500,
            "difficulty": 0.55,
            "intent": "commercial",
            "cpc": 4.8,
        },
    ],
    "saude": [
        {
            "keyword": "emagrecer rapido",
            "volume": 22000,
            "difficulty": 0.70,
            "intent": "commercial",
            "cpc": 1.8,
        },
        {
            "keyword": "alimentacao saudavel",
            "volume": 9800,
            "difficulty": 0.35,
            "intent": "informational",
            "cpc": 1.2,
        },
        {
            "keyword": "melhores suplementos",
            "volume": 6200,
            "difficulty": 0.42,
            "intent": "commercial",
            "cpc": 2.5,
        },
        {
            "keyword": "exercicios em casa",
            "volume": 15000,
            "difficulty": 0.25,
            "intent": "informational",
            "cpc": 0.8,
        },
        {
            "keyword": "ansiedade sintomas",
            "volume": 12000,
            "difficulty": 0.30,
            "intent": "informational",
            "cpc": 1.0,
        },
        {
            "keyword": "meditar para iniciantes",
            "volume": 5400,
            "difficulty": 0.20,
            "intent": "informational",
            "cpc": 0.6,
        },
        {
            "keyword": "sono reparador dicas",
            "volume": 4800,
            "difficulty": 0.22,
            "intent": "informational",
            "cpc": 0.9,
        },
        {
            "keyword": "vitamina d beneficios",
            "volume": 7200,
            "difficulty": 0.28,
            "intent": "informational",
            "cpc": 1.5,
        },
    ],
    "carreira": [
        {
            "keyword": "como fazer curriculo",
            "volume": 14000,
            "difficulty": 0.20,
            "intent": "informational",
            "cpc": 0.5,
        },
        {
            "keyword": "entrevista de emprego dicas",
            "volume": 8800,
            "difficulty": 0.25,
            "intent": "informational",
            "cpc": 0.7,
        },
        {
            "keyword": "cursos online gratuitos",
            "volume": 18000,
            "difficulty": 0.30,
            "intent": "commercial",
            "cpc": 1.5,
        },
        {
            "keyword": "linkedin otimizar perfil",
            "volume": 6200,
            "difficulty": 0.22,
            "intent": "informational",
            "cpc": 1.0,
        },
        {
            "keyword": "programacao para iniciantes",
            "volume": 9500,
            "difficulty": 0.35,
            "intent": "informational",
            "cpc": 1.2,
        },
        {
            "keyword": "mudar de carreira aos 30",
            "volume": 7200,
            "difficulty": 0.28,
            "intent": "informational",
            "cpc": 1.8,
        },
    ],
}

_NICHOS = ["tecnologia", "financas", "saude", "carreira"]


class ContentResearchAgent(AgentBase):
    """Pesquisa palavras-chave, analisa intenção, identifica gaps de conteúdo."""

    def __init__(self, **kwargs) -> None:
        super().__init__("content_research", **kwargs)

    def _find_keywords(self, niche: str) -> list[dict[str, Any]]:
        niche_lower = niche.lower()
        results = []
        for key, kws in _KEYWORD_DATA.items():
            if key in niche_lower or niche_lower in key:
                results.extend(kws)
        # If no match, return first niche
        if not results and _KEYWORD_DATA:
            results = _KEYWORD_DATA.get(
                niche_lower, _KEYWORD_DATA.get("tecnologia", [])
            )
        return results

    def _analyze_competition(self, keyword: str) -> dict[str, Any]:
        """Simula análise de concorrência para uma keyword."""
        return {
            "competitors_found": random.randint(3, 12),
            "avg_article_length": random.randint(800, 2500),
            "top_result_domain_authority": random.randint(20, 70),
            "content_gaps": [
                "poucos artigos com FAQ section",
                "falta de schema markup",
                "imagens sem alt text",
            ],
            "opportunity_score": random.uniform(0.3, 0.9),
        }

    def _estimate_traffic(self, keyword: dict[str, Any]) -> int:
        """Estima tráfego potencial baseado em volume e dificuldade."""
        volume = keyword.get("volume", 1000)
        difficulty = keyword.get("difficulty", 0.5)
        # Top 3 results get ~60% of clicks
        # Position 1 gets ~30% of clicks
        return int(volume * 0.30 * (1 - difficulty))

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", "tecnologia"))
        max_keywords = int(campaign.get("max_keywords_per_cycle", 10))
        preferred_intents = campaign.get(
            "preferred_intents", ["informational", "commercial"]
        )

        all_keywords = self._find_keywords(niche)

        # Filter by preferred intent
        filtered = [kw for kw in all_keywords if kw.get("intent") in preferred_intents]

        # Score each keyword (higher = better opportunity)
        for kw in filtered:
            difficulty = kw.get("difficulty", 0.5)
            volume = kw.get("volume", 100)
            intent = kw.get("intent", "informational")
            # Commercial + low difficulty + high volume = best opportunity
            intent_bonus = 1.2 if intent == "commercial" else 1.0
            kw["opportunity_score"] = round(
                volume * (1 - difficulty) * intent_bonus / 1000, 2
            )

        # Sort by opportunity
        filtered.sort(key=lambda x: -x.get("opportunity_score", 0))

        # Select top keywords
        top_keywords = filtered[:max_keywords]

        # Build detailed opportunities
        opportunities = []
        for kw in top_keywords:
            comp = self._analyze_competition(kw["keyword"])
            traffic_est = self._estimate_traffic(kw)
            opportunities.append(
                {
                    "keyword": kw["keyword"],
                    "volume": kw["volume"],
                    "difficulty": kw["difficulty"],
                    "intent": kw["intent"],
                    "cpc": kw.get("cpc", 0),
                    "opportunity_score": kw["opportunity_score"],
                    "estimated_monthly_traffic": traffic_est,
                    "competition": comp,
                    "suggested_content_type": (
                        "guia_completo"
                        if kw["intent"] == "informational" and kw["volume"] > 5000
                        else "review"
                        if kw["intent"] == "commercial"
                        else "tutorial"
                        if kw["difficulty"] < 0.3
                        else "artigo_informativo"
                    ),
                    "recommendation": (
                        "Prioridade máxima"
                        if kw["opportunity_score"] > 5
                        else "Alta prioridade"
                        if kw["opportunity_score"] > 3
                        else "Prioridade média"
                    ),
                }
            )

        # Generate content strategy
        strategy = self._generate_strategy(niche, opportunities)

        output = {
            "niche": niche,
            "cycle": context.run_id,
            "total_keywords_analyzed": len(all_keywords),
            "opportunities_found": len(opportunities),
            "top_opportunities": opportunities[:5],
            "content_strategy": strategy,
            "recommended_focus": (
                f"Produzir conteúdo {opportunities[0]['intent']} sobre "
                f"'{opportunities[0]['keyword']}' primeiro - "
                f"{opportunities[0]['estimated_monthly_traffic']} visitas/mês estimadas"
            )
            if opportunities
            else "Nenhuma oportunidade encontrada",
        }

        # Register in explanation store
        if self.explanation_store and opportunities:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="keyword_research",
                input_state={"niche": niche, "preferred_intents": preferred_intents},
            )
            self.explanation_store.record_rule_application(
                decision_id=decision_id,
                rule_source="adr002.content_research",
                rule_value="opportunity_score = volume * (1-difficulty) * intent_bonus",
                actual_value=opportunities[0]["opportunity_score"],
                comparison_result=True,
                rule_order=1,
            )

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="keyword_research",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Analisou {len(all_keywords)} keywords, encontrou {len(opportunities)} oportunidades no nicho '{niche}'"
            ],
            metadata={
                "niche": niche,
                "keywords_found": len(all_keywords),
                "opportunities": len(opportunities),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _generate_strategy(self, niche: str, opportunities: list) -> dict[str, Any]:
        """Gera estratégia de conteúdo baseada nos dados."""
        if not opportunities:
            return {"plan": [], "total_articles_suggested": 0}

        # Group by intent
        by_intent: dict[str, list] = {}
        for opp in opportunities:
            by_intent.setdefault(opp["intent"], []).append(opp)

        plan = []
        for intent, items in by_intent.items():
            plan.append(
                {
                    "intent": intent,
                    "count": len(items),
                    "avg_opportunity": round(
                        sum(i["opportunity_score"] for i in items) / len(items), 2
                    ),
                    "suggested_order": 1 if intent == "commercial" else 2,
                }
            )

        plan.sort(key=lambda x: x["suggested_order"])

        return {
            "plan": plan,
            "total_articles_suggested": len(opportunities),
            "estimated_monthly_traffic_total": sum(
                o["estimated_monthly_traffic"] for o in opportunities
            ),
            "estimated_monthly_cpc_avg": round(
                sum(o.get("cpc", 0) for o in opportunities)
                / max(len(opportunities), 1),
                2,
            ),
        }

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
