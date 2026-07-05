"""CrossPollinationHub — 3ª Ordem: Conecta todos os domínios em ciclo virtuoso.

O hub que faz o sistema inteiro se alimentar:
- Conteúdo SEO (Onda 1) → gera tráfego → monetiza (Onda 2) → financia mais conteúdo
- Oportunidades detectadas → novos conteúdos → novos produtos
- Dados de receita → alimentam estratégia de conteúdo
- Métricas de engajamento → otimizam produtos digitais

Sem este hub, cada onda opera em silo. Com ele, o sistema é UM organismo.
"""

from __future__ import annotations

from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("cross_pollination")


CROSS_POLLINATION_STRATEGIES = [
    {
        "id": "content_to_product",
        "name": "Artigo → Produto Digital",
        "description": "Artigos com alto engajamento viram ebooks/cursos",
        "trigger": "article_engagement > 0.7",
        "action": "DigitalProductAgent criar produto baseado no artigo",
    },
    {
        "id": "content_to_affiliate",
        "name": "Artigo → Afiliado Inteligente",
        "description": "Artigos comerciais recebem links de afiliado automáticos",
        "trigger": "article_intent == 'commercial'",
        "action": "OfferLookupAgent + InternalLinkerAgent inserir links",
    },
    {
        "id": "opportunity_to_content",
        "name": "Oportunidade → Conteúdo Novo",
        "description": "Oportunidades detectadas viram pautas de conteúdo",
        "trigger": "opportunity_score > 0.7",
        "action": "SEOContentWriterAgent criar artigo sobre o tópico",
    },
    {
        "id": "product_to_email",
        "name": "Produto → Sequência de Email",
        "description": "Novos produtos digitais geram sequência de vendas",
        "trigger": "new_product_created",
        "action": "EmailMarketingAgent criar sequência de lançamento",
    },
    {
        "id": "revenue_to_content",
        "name": "Receita → Mais Conteúdo",
        "description": "Receita de afiliados financia mais produção de conteúdo",
        "trigger": "compounding_plan_approved",
        "action": "Mais artigos no próximo ciclo (reinvestimento)",
    },
    {
        "id": "trend_to_news",
        "name": "Tendência → Notícia Rápida",
        "description": "Tendências detectadas viram conteúdo de trending",
        "trigger": "trending_topic_detected",
        "action": "SEOContentWriterAgent criar artigo rápido (modo trending)",
    },
    {
        "id": "eeat_to_trust",
        "name": "E-E-A-T → Conversão",
        "description": "Conteúdo com alto E-E-A-T vende mais produtos",
        "trigger": "eeat_score > 0.8",
        "action": "Adicionar links de afiliado em artigos de alta confiança",
    },
    {
        "id": "membership_to_content",
        "name": "Assinantes → Conteúdo Exclusivo",
        "description": "Membros premium geram demanda por conteúdo específico",
        "trigger": "member_feedback_collected",
        "action": "Criar conteúdo baseado em pedidos dos assinantes",
    },
]


class CrossPollinationHub(AgentBase):
    """Conecta todos os domínios do sistema em ciclo virtuoso — 3ª Ordem."""

    def __init__(self, **kwargs) -> None:
        super().__init__("cross_pollination", **kwargs)

    def analyze_cross_pollination(self, context: CampaignContext) -> dict[str, Any]:
        """Analisa oportunidades de cross-pollination entre domínios."""
        sr = context.step_results if hasattr(context, "step_results") else {}
        campaign = context.campaign if hasattr(context, "campaign") else {}

        # Collect signals from all domains
        signals = self._collect_signals(sr, campaign)

        # Match signals to strategies
        activations = []
        for strategy in CROSS_POLLINATION_STRATEGIES:
            should_activate = self._evaluate_trigger(strategy["trigger"], signals)
            if should_activate:
                activations.append(
                    {
                        "strategy_id": strategy["id"],
                        "name": strategy["name"],
                        "trigger_met": strategy["trigger"],
                        "action": strategy["action"],
                        "priority": self._calculate_priority(strategy["id"], signals),
                        "expected_impact": self._estimate_impact(
                            strategy["id"], signals
                        ),
                    }
                )

        # Prioritize by impact
        activations.sort(key=lambda x: -x["priority"])

        # Generate cross-pollination graph
        graph = self._build_pollination_graph(activations)

        return {
            "total_strategies": len(CROSS_POLLINATION_STRATEGIES),
            "activations": activations,
            "active_strategies": len(activations),
            "pollination_graph": graph,
            "ecosystem_health": self._calculate_ecosystem_health(activations, signals),
            "synergy_score": self._calculate_synergy(activations),
            "recommendations": self._generate_recommendations(activations),
        }

    def _collect_signals(self, step_results: dict, campaign: dict) -> dict[str, Any]:
        """Coleta sinais de todos os domínios para avaliação."""
        signals = {}

        # From SEO content (Onda 1)
        seo_out = self._get_step_output(step_results, "seo_content_writing", {})
        if isinstance(seo_out, dict):
            signals["article_count"] = len(seo_out.get("articles", []))
            signals["avg_seo_score"] = seo_out.get("average_seo_score", 0)
            signals["article_intents"] = [
                a.get("metadata", {}).get("intent", "")
                for a in seo_out.get("articles", [])
                if isinstance(a, dict)
            ]

        # From research
        research_out = self._get_step_output(step_results, "keyword_research", {})
        if isinstance(research_out, dict):
            signals["opportunities"] = research_out.get("opportunities_found", 0)
            signals["top_opportunities"] = research_out.get("top_opportunities", [])

        # From EEAT
        eeat_out = self._get_step_output(step_results, "eeat_validation", {})
        if isinstance(eeat_out, dict):
            signals["avg_eeat_score"] = eeat_out.get("average_eeat_score", 0)

        # From revenue (Onda 2)
        signals["revenue_sources"] = campaign.get("revenue_data", {})

        # From portfolio
        portfolio_out = self._get_step_output(step_results, "portfolio_analysis", {})
        if isinstance(portfolio_out, dict):
            signals["portfolio"] = portfolio_out.get("portfolio_analysis", {})

        # From digital products
        product_out = self._get_step_output(step_results, "digital_product", {})
        if isinstance(product_out, dict):
            signals["new_product"] = bool(product_out.get("top_product"))

        # From compounding
        compound_out = self._get_step_output(step_results, "compounding", {})
        if isinstance(compound_out, dict):
            signals["compounding_plan"] = compound_out.get("compounding", {})

        return signals

    def _evaluate_trigger(self, trigger: str, signals: dict) -> bool:
        """Avalia se um trigger de cross-pollination foi ativado."""
        try:
            if "article_engagement > 0.7" in trigger:
                return signals.get("avg_seo_score", 0) > 70
            if "article_intent == 'commercial'" in trigger:
                return "commercial" in signals.get("article_intents", [])
            if (
                "opportunity_score > 0.7" in trigger
                and signals.get("opportunities", 0) > 0
            ):
                return True
            if "new_product_created" in trigger:
                return signals.get("new_product", False)
            if "compounding_plan_approved" in trigger:
                return bool(signals.get("compounding_plan", {}))
            if "eeat_score > 0.8" in trigger:
                return signals.get("avg_eeat_score", 0) > 80
            if "trending_topic_detected" in trigger:
                return signals.get("opportunities", 0) > 3
            return False
        except Exception:
            return False

    def _calculate_priority(self, strategy_id: str, signals: dict) -> float:
        """Calcula prioridade (0-1) para uma estratégia de cross-pollination."""
        priorities = {
            "content_to_affiliate": 0.9
            if "commercial" in signals.get("article_intents", [])
            else 0.5,
            "content_to_product": 0.8 if signals.get("avg_seo_score", 0) > 70 else 0.4,
            "opportunity_to_content": 0.85
            if signals.get("opportunities", 0) > 3
            else 0.5,
            "product_to_email": 0.75 if signals.get("new_product", False) else 0.3,
            "revenue_to_content": 0.9 if signals.get("compounding_plan", {}) else 0.4,
            "trend_to_news": 0.7,
            "eeat_to_trust": 0.6 if signals.get("avg_eeat_score", 0) > 70 else 0.3,
            "membership_to_content": 0.5,
        }
        return priorities.get(strategy_id, 0.5)

    def _estimate_impact(self, strategy_id: str, signals: dict) -> str:
        """Estima impacto de cada estratégia."""
        impacts = {
            "content_to_affiliate": "Médio: aumento de 10-30% em comissões",
            "content_to_product": "Alto: nova fonte de receita recorrente",
            "opportunity_to_content": "Alto: captura de tráfego novo",
            "product_to_email": "Alto: conversão de leads em vendas",
            "revenue_to_content": "Muito alto: ciclo de compounding",
            "trend_to_news": "Médio: tráfego de pico temporário",
            "eeat_to_trust": "Médio: aumento de conversão",
            "membership_to_content": "Médio: retenção de assinantes",
        }
        return impacts.get(strategy_id, "Desconhecido")

    def _build_pollination_graph(self, activations: list) -> dict:
        """Constrói grafo de como os domínios se alimentam."""
        active_ids = {a["strategy_id"] for a in activations}
        nodes = []
        edges = []

        # Define all domain nodes
        domains = {
            "content": "Conteúdo SEO",
            "products": "Produtos Digitais",
            "affiliates": "Afiliados",
            "email": "Email Marketing",
            "membership": "Assinaturas",
            "adsense": "AdSense",
            "trends": "Tendências",
            "eeat": "E-E-A-T",
        }

        for d_id, d_name in domains.items():
            nodes.append({"id": d_id, "name": d_name, "active": True})

        # Define edges for active strategies
        edge_map = {
            "content_to_product": ("content", "products"),
            "content_to_affiliate": ("content", "affiliates"),
            "opportunity_to_content": ("trends", "content"),
            "product_to_email": ("products", "email"),
            "revenue_to_content": ("affiliates", "content"),
            "trend_to_news": ("trends", "content"),
            "eeat_to_trust": ("eeat", "affiliates"),
            "membership_to_content": ("membership", "content"),
        }

        for sid in active_ids:
            if sid in edge_map:
                src, tgt = edge_map[sid]
                edges.append({"source": src, "target": tgt, "strategy": sid})

        return {"nodes": nodes, "edges": edges}

    def _calculate_ecosystem_health(self, activations: list, signals: dict) -> dict:
        """Calcula saúde geral do ecossistema."""
        active_ratio = len(activations) / max(len(CROSS_POLLINATION_STRATEGIES), 1)
        return {
            "score": round(active_ratio * 100, 1),
            "status": "Excelente"
            if active_ratio > 0.7
            else "Bom"
            if active_ratio > 0.4
            else "Emergente",
            "active_loops": len(activations),
            "total_possible_loops": len(CROSS_POLLINATION_STRATEGIES),
        }

    def _calculate_synergy(self, activations: list) -> float:
        """Calcula sinergia entre ativações."""
        if not activations:
            return 0.0
        return min(len(activations) / len(CROSS_POLLINATION_STRATEGIES) * 1.5, 1.0)

    def _generate_recommendations(self, activations: list) -> list[str]:
        """Gera recomendações baseadas nas ativações."""
        recs = []
        active_ids = {a["strategy_id"] for a in activations}

        if "content_to_product" in active_ids and "product_to_email" not in active_ids:
            recs.append("Criar sequência de email para o novo produto digital")
        if "opportunity_to_content" not in active_ids:
            recs.append(
                "Ativar detector de oportunidades para alimentar pipeline de conteúdo"
            )
        if "revenue_to_content" in active_ids:
            recs.append("Reinvestimento ativo: receita financiando mais conteúdo")
        if "eeat_to_trust" in active_ids:
            recs.append(
                "Artigos com alto E-E-A-T prontos para monetização com afiliados"
            )
        if not recs:
            recs.append(
                "Sistema em operação padrão. Cross-pollination aumentará com mais dados."
            )
        return recs

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        analysis = self.analyze_cross_pollination(context)

        output = {
            "cross_pollination": analysis,
            "executive_summary": {
                "active_loops": analysis["active_strategies"],
                "ecosystem_health": analysis["ecosystem_health"]["status"],
                "synergy": f"{analysis['synergy_score'] * 100:.0f}%",
                "top_priority": analysis["activations"][0]["name"]
                if analysis["activations"]
                else "Nenhuma",
            },
            "pollination_graph": analysis["pollination_graph"],
            "recommendations": analysis["recommendations"],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="cross_pollination",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"{analysis['active_strategies']} estratégias de cross-pollination ativas | Saúde: {analysis['ecosystem_health']['status']}"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _get_step_output(step_results: dict, step_id: str, default: Any = None) -> Any:
        """Extrai output de um step específico."""
        step = step_results.get(step_id, {})
        if isinstance(step, dict):
            return step.get("output", step)
        return default

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
