"""PortfolioOptimizerAgent — 2ª Ordem: Otimiza alocação entre múltiplas fontes de renda.

Analisa o portfólio completo de receitas e decide:
- Onde alocar o próximo ciclo de produção
- Quais fontes estão com baixo ROI (matar)
- Quais fontes merecem mais investimento (escalar)
- Balanceamento de risco entre fontes
"""

from __future__ import annotations

from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("portfolio_optimizer")


REVENUE_SOURCES = [
    {
        "id": "affiliate_hotmart",
        "name": "Hotmart",
        "type": "direct",
        "risk": 0.4,
        "passive": 0.3,
        "setup_days": 1,
    },
    {
        "id": "affiliate_amazon",
        "name": "Amazon Associates",
        "type": "direct",
        "risk": 0.3,
        "passive": 0.4,
        "setup_days": 1,
    },
    {
        "id": "adsense",
        "name": "Google AdSense",
        "type": "passive",
        "risk": 0.5,
        "passive": 1.0,
        "setup_days": 30,
    },
    {
        "id": "digital_product",
        "name": "Produtos Digitais",
        "type": "direct",
        "risk": 0.5,
        "passive": 0.6,
        "setup_days": 3,
    },
    {
        "id": "membership",
        "name": "Assinaturas",
        "type": "recurring",
        "risk": 0.3,
        "passive": 0.8,
        "setup_days": 7,
    },
    {
        "id": "email",
        "name": "Email Marketing",
        "type": "direct",
        "risk": 0.2,
        "passive": 0.5,
        "setup_days": 2,
    },
    {
        "id": "sponsorship",
        "name": "Patrocínio",
        "type": "direct",
        "risk": 0.6,
        "passive": 0.2,
        "setup_days": 14,
    },
    {
        "id": "licensing",
        "name": "Licenciamento",
        "type": "residual",
        "risk": 0.7,
        "passive": 0.9,
        "setup_days": 5,
    },
]


class PortfolioOptimizerAgent(AgentBase):
    """Otimiza portfólio de fontes de renda — 2ª Ordem."""

    def __init__(self, **kwargs) -> None:
        super().__init__("portfolio_optimizer", **kwargs)

    def analyze_portfolio(
        self, revenue_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analisa o portfólio completo e gera recomendações."""
        # Em produção: receber dados reais de revenue_monitor
        if revenue_data:
            sources = revenue_data
        else:
            sources = {
                s["id"]: {
                    "revenue": s.get("revenue", 0),
                    "effort": s.get("effort", 5),
                    "trend": s.get("trend", "stable"),
                }
                for s in REVENUE_SOURCES
            }

        analysis = []
        for src in REVENUE_SOURCES:
            src_id = src["id"]
            perf = sources.get(src_id, {})
            revenue = perf.get("revenue", 0)
            effort = perf.get("effort", 5)
            trend = perf.get("trend", "stable")

            roi = revenue / max(effort, 1)
            risk_adjusted_roi = roi * (1 - src["risk"])
            passivity_score = src["passive"]

            analysis.append(
                {
                    "source_id": src_id,
                    "name": src["name"],
                    "type": src["type"],
                    "current_revenue": revenue,
                    "effort_score": effort,
                    "roi": round(roi, 2),
                    "risk_adjusted_roi": round(risk_adjusted_roi, 2),
                    "risk": src["risk"],
                    "passivity": passivity_score,
                    "trend": trend,
                    "recommendation": self._recommend_action(
                        roi, risk_adjusted_roi, passivity_score, trend
                    ),
                }
            )

        # Sort by risk-adjusted ROI
        analysis.sort(key=lambda x: -x["risk_adjusted_roi"])

        # Calculate portfolio diversity
        types = {}
        for a in analysis:
            types[a["type"]] = types.get(a["type"], 0) + 1
        diversity_score = min(len(types) / 4, 1.0)
        concentration_risk = 1.0
        for a in analysis[:2]:
            concentration_risk -= 0.2  # Top 2 sources concentration risk

        return {
            "sources": analysis,
            "diversity": {
                "score": round(diversity_score, 2),
                "concentration_risk": round(max(0, concentration_risk), 2),
                "types_breakdown": types,
            },
            "recommendations": self._generate_portfolio_recs(analysis),
            "optimal_allocation": self._calculate_allocation(analysis),
        }

    def _recommend_action(
        self, roi: float, risk_roi: float, passivity: float, trend: str
    ) -> str:
        """Recomenda ação para uma fonte de renda."""
        if roi < 0.1:
            return "ELIMINAR" if trend == "down" else "REAVALIAR"
        if risk_roi > 2.0 and passivity > 0.7:
            return "ESCALAR (prioridade máxima)"
        if risk_roi > 1.0:
            return "MANTER E OTIMIZAR"
        if trend == "up":
            return "INVESTIR MAIS"
        return "MANTER"

    def _generate_portfolio_recs(self, analysis: list[dict]) -> list[str]:
        """Gera recomendações estratégicas."""
        recs = []
        high_roi = [a for a in analysis if "ESCALAR" in a.get("recommendation", "")]
        low_roi = [a for a in analysis if "ELIMINAR" in a.get("recommendation", "")]
        risky = [
            a for a in analysis if "risk" in str(a.get("recommendation", "")).lower()
        ]

        if high_roi:
            recs.append(
                f"🔥 Escalar {high_roi[0]['name']}: melhor ROI ajustado ao risco"
            )
        if low_roi:
            recs.append(f"🗑️ Eliminar {low_roi[0]['name']}: abaixo do threshold de ROI")
        recs.append(
            "📊 Diversificar: adicionar fontes de renda passiva para balancear risco"
        )
        recs.append(
            "🔄 Ciclo de reinvestimento: receita de fontes diretas → financiar fontes passivas"
        )
        recs.append(
            "📈 Meta: 60% receita passiva/residual, 40% receita direta para equilíbrio"
        )
        return recs

    def _calculate_allocation(self, analysis: list[dict]) -> dict[str, float]:
        """Calcula alocação ótima de esforço entre fontes."""
        total_score = sum(max(a["risk_adjusted_roi"], 0) for a in analysis)
        if total_score == 0:
            return {a["source_id"]: 1.0 / max(len(analysis), 1) for a in analysis}
        return {
            a["source_id"]: round(max(a["risk_adjusted_roi"], 0) / total_score, 3)
            for a in analysis
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        revenue_data = campaign.get("revenue_data", {})
        analysis = self.analyze_portfolio(revenue_data)

        output = {
            "portfolio_analysis": analysis,
            "executive_summary": {
                "diversity_score": analysis["diversity"]["score"],
                "concentration_risk": analysis["diversity"]["concentration_risk"],
                "top_source": analysis["sources"][0]["name"]
                if analysis["sources"]
                else "N/A",
                "sources_to_eliminate": len(
                    [
                        a
                        for a in analysis["sources"]
                        if "ELIMINAR" in a.get("recommendation", "")
                    ]
                ),
                "sources_to_scale": len(
                    [
                        a
                        for a in analysis["sources"]
                        if "ESCALAR" in a.get("recommendation", "")
                    ]
                ),
            },
            "cycle_priority": analysis.get("recommendations", [])[:2],
            "optimal_allocation": analysis.get("optimal_allocation", {}),
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="portfolio_optimization",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Otimizou portfólio de {len(analysis['sources'])} fontes de renda"],
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
