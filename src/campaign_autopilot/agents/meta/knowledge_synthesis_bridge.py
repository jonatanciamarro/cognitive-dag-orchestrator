"""KnowledgeSynthesisBridge — 3ª Ordem: Síntese de conhecimento entre todos os domínios.

Conecta:
- MemoryStore (dados operacionais)
- SemanticMemory (grafo de conceitos)
- SynthesisEngine (aprendizado entre ciclos)
- RevenueMonitor (dados financeiros)
- SEO Analytics (dados de tráfego)

Gera insights que nenhum domínio conseguiria gerar sozinho.
"""

from __future__ import annotations

from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("knowledge_synthesis")


class KnowledgeSynthesisBridge(AgentBase):
    """Sintetiza conhecimento entre todos os domínios — 3ª Ordem."""

    def __init__(self, **kwargs) -> None:
        super().__init__("knowledge_synthesis", **kwargs)

    def synthesize(self, context: CampaignContext) -> dict[str, Any]:
        """Sintetiza conhecimento de todos os domínios em insights acionáveis."""
        sr = context.step_results if hasattr(context, "step_results") else {}
        campaign = context.campaign if hasattr(context, "campaign") else {}

        # Collect insights from each domain
        seo_insights = self._collect_seo_insights(sr)
        revenue_insights = self._collect_revenue_insights(sr, campaign)
        content_insights = self._collect_content_insights(sr)
        meta_insights = self._collect_meta_insights(sr)

        # Generate cross-domain insights
        cross_insights = self._generate_cross_insights(
            seo_insights, revenue_insights, content_insights, meta_insights
        )

        # Build knowledge graph
        knowledge_graph = self._build_knowledge_graph(
            seo_insights, revenue_insights, content_insights, cross_insights
        )

        return {
            "seo_domain": seo_insights,
            "revenue_domain": revenue_insights,
            "content_domain": content_insights,
            "meta_domain": meta_insights,
            "cross_domain_insights": cross_insights,
            "knowledge_graph": knowledge_graph,
            "synthesis_quality": self._evaluate_synthesis(cross_insights),
        }

    def _collect_seo_insights(self, sr: dict) -> dict:
        """Coleta insights do domínio SEO."""
        seo = self._get_output(sr, "seo_technical", {})
        rank = self._get_output(sr, "rank_tracker", {})
        return {
            "articles_with_schema": seo.get("articles_processed", 0)
            if isinstance(seo, dict)
            else 0,
            "ranking_data_available": bool(rank) if isinstance(rank, dict) else False,
        }

    def _collect_revenue_insights(self, sr: dict, campaign: dict) -> dict:
        """Coleta insights do domínio de receita."""
        portfolio = self._get_output(sr, "portfolio_analysis", {})
        products = self._get_output(sr, "digital_product", {})
        compounding = self._get_output(sr, "compounding", {})
        revenue_data = campaign.get("revenue_data", {})

        return {
            "revenue_sources": len(revenue_data)
            if isinstance(revenue_data, dict)
            else 0,
            "total_revenue": sum(revenue_data.values())
            if isinstance(revenue_data, dict)
            else 0,
            "has_portfolio_analysis": bool(portfolio),
            "has_digital_products": bool(products),
            "has_compounding_plan": bool(compounding),
        }

    def _collect_content_insights(self, sr: dict) -> dict:
        """Coleta insights do domínio de conteúdo."""
        content = self._get_output(sr, "seo_content_writing", {})
        eeat = self._get_output(sr, "eeat_validation", {})
        research = self._get_output(sr, "keyword_research", {})

        return {
            "articles_generated": content.get("articles_generated", 0)
            if isinstance(content, dict)
            else 0,
            "avg_seo_score": content.get("average_seo_score", 0)
            if isinstance(content, dict)
            else 0,
            "avg_eeat_score": eeat.get("average_eeat_score", 0)
            if isinstance(eeat, dict)
            else 0,
            "opportunities_found": research.get("opportunities_found", 0)
            if isinstance(research, dict)
            else 0,
        }

    def _collect_meta_insights(self, sr: dict) -> dict:
        """Coleta insights do domínio meta."""
        cross = self._get_output(sr, "cross_pollination", {})
        factory = self._get_output(sr, "agent_factory", {})
        orchestrator = self._get_output(sr, "meta_orchestrator", {})

        return {
            "cross_pollination_active": len(cross.get("activations", []))
            if isinstance(cross, dict)
            else 0,
            "agent_needs_detected": factory.get("needs_detected", 0)
            if isinstance(factory, dict)
            else 0,
            "orchestrator_cycles": orchestrator.get("total_cycles_analyzed", 0)
            if isinstance(orchestrator, dict)
            else 0,
        }

    def _generate_cross_insights(
        self, seo: dict, revenue: dict, content: dict, meta: dict
    ) -> list[dict]:
        """Gera insights que cruzam domínios."""
        insights = []

        # SEO → Revenue
        if content.get("avg_seo_score", 0) > 70 and revenue.get("total_revenue", 0) > 0:
            insights.append(
                {
                    "type": "seo_to_revenue",
                    "insight": "Conteúdo com alto score SEO está gerando receita. Escalar produção.",
                    "confidence": 0.8,
                    "action": "Aumentar produção de conteúdo comercial",
                }
            )

        # Revenue → Content
        if (
            revenue.get("total_revenue", 0) > 0
            and content.get("articles_generated", 0) > 0
        ):
            rpm = revenue["total_revenue"] / max(content["articles_generated"], 1)
            insights.append(
                {
                    "type": "revenue_per_article",
                    "insight": f"R$ {rpm:.2f} por artigo gerado",
                    "confidence": 0.7,
                    "action": "Focar em tipos de artigo com maior RPM",
                }
            )

        # E-E-A-T → Revenue
        if content.get("avg_eeat_score", 0) > 70:
            insights.append(
                {
                    "type": "eeat_monetization",
                    "insight": "Conteúdo com alto E-E-A-T está pronto para monetização premium",
                    "confidence": 0.75,
                    "action": "Adicionar links de afiliado em artigos com E-E-A-T > 70",
                }
            )

        # Meta → Everything
        if meta.get("cross_pollination_active", 0) > 3:
            insights.append(
                {
                    "type": "ecosystem_maturity",
                    "insight": "Ecossistema maduro com múltiplos loops de cross-pollination ativos",
                    "confidence": 0.85,
                    "action": "Sistema entrando em modo autônomo. Reduzir supervisão.",
                }
            )

        if not insights:
            insights.append(
                {
                    "type": "initial",
                    "insight": "Coletando dados de baseline para síntese cross-domínio",
                    "confidence": 0.3,
                    "action": "Continuar ciclos para acumular dados",
                }
            )

        return insights

    def _build_knowledge_graph(
        self, seo: dict, revenue: dict, content: dict, cross: list
    ) -> dict:
        """Constrói grafo de conhecimento conectando todos os domínios."""
        nodes = [
            {"id": "seo", "label": "SEO", "metrics": seo},
            {"id": "revenue", "label": "Receita", "metrics": revenue},
            {"id": "content", "label": "Conteúdo", "metrics": content},
        ]
        edges = [
            {"source": "content", "target": "seo", "type": "alimenta"},
            {"source": "seo", "target": "revenue", "type": "gera"},
            {"source": "revenue", "target": "content", "type": "financia"},
        ]
        return {"nodes": nodes, "edges": edges, "cross_insights": len(cross)}

    def _evaluate_synthesis(self, cross: list) -> dict:
        """Avalia qualidade da síntese."""
        high_conf = sum(1 for c in cross if c.get("confidence", 0) > 0.7)
        return {
            "total_insights": len(cross),
            "high_confidence_insights": high_conf,
            "synthesis_quality": "Alta"
            if high_conf >= 2
            else "Média"
            if high_conf >= 1
            else "Inicial",
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        synthesis = self.synthesize(context)

        output = {
            "synthesis": synthesis,
            "executive_summary": {
                "domains_synthesized": 4,
                "cross_insights": len(synthesis["cross_domain_insights"]),
                "quality": synthesis["synthesis_quality"]["synthesis_quality"],
                "knowledge_graph_nodes": len(synthesis["knowledge_graph"]["nodes"]),
            },
            "top_insights": [
                i
                for i in synthesis["cross_domain_insights"]
                if i.get("confidence", 0) > 0.7
            ][:3],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="knowledge_synthesis",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Sintetizou 4 domínios: {len(synthesis['cross_domain_insights'])} insights cross-domínio"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _get_output(sr: dict, step_id: str, default: Any = None) -> Any:
        step = sr.get(step_id, {})
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
