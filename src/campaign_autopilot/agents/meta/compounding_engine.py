"""CompoundingEngine — 2ª Ordem: Ciclo de reinvestimento automático entre fontes de renda.

Princípio: receita de fontes "diretas" (maior esforço) financia fontes "passivas" (menor esforço).
Com o tempo, o sistema migra de ativo → passivo → residual, aumentando a renda sem aumentar trabalho.

Fluxo:
  Fase 1: Afiliados (ativo) → gera receita
  Fase 2: Receita → financia conteúdo para AdSense + Produtos Digitais
  Fase 3: AdSense (passivo) + Produtos (recorrente) → escala sem esforço extra
  Fase 4: Receita residual → reinveste em novas fontes (expansão)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("compounding_engine")


COMPOUNDING_STRATEGY = [
    {
        "phase": 1,
        "name": "Ativação",
        "description": "Foco em afiliados e conteúdo direto",
        "source_type": "direct",
        "reinvest_rate": 0.3,  # 30% da receita reinvestida
        "target": "construir base de conteúdo e audiência",
        "metrics": ["artigos publicados", "tráfego orgânico", "comissões"],
    },
    {
        "phase": 2,
        "name": "Diversificação",
        "description": "Adicionar AdSense e produtos digitais",
        "source_type": "direct_passive",
        "reinvest_rate": 0.4,
        "target": "múltiplas fontes de renda operacionais",
        "metrics": ["fontes ativas", "receita total", "ROI por fonte"],
    },
    {
        "phase": 3,
        "name": "Passivação",
        "description": "Receita direta financia crescimento passivo",
        "source_type": "passive_first",
        "reinvest_rate": 0.5,
        "target": "mínimo 60% receita passiva",
        "metrics": ["receita passiva %", "trabalho por R$", "margem"],
    },
    {
        "phase": 4,
        "name": "Residual",
        "description": "Sistema autossustentável, renda composta",
        "source_type": "residual",
        "reinvest_rate": 0.6,
        "target": "crescimento exponencial sem trabalho extra",
        "metrics": ["crescimento m/m", "novas fontes automáticas", "liberdade"],
    },
]


class CompoundingEngine(AgentBase):
    """Gerencia o ciclo de reinvestimento entre fontes de renda — 2ª Ordem."""

    def __init__(self, **kwargs) -> None:
        super().__init__("compounding_engine", **kwargs)

    def calculate_phase(self, revenue_data: dict[str, float]) -> dict[str, Any]:
        """Determina em qual fase de compounding o sistema está."""
        total = sum(revenue_data.values()) or 1
        direct = revenue_data.get("affiliate_hotmart", 0) + revenue_data.get(
            "affiliate_amazon", 0
        )
        passive = revenue_data.get("adsense", 0) + revenue_data.get(
            "digital_product", 0
        )
        recurring = revenue_data.get("membership", 0)
        residual = revenue_data.get("licensing", 0) + revenue_data.get("sponsorship", 0)

        passive_ratio = (passive + recurring + residual) / total

        if passive_ratio < 0.3:
            return {**COMPOUNDING_STRATEGY[0], "phase_found": True}
        elif passive_ratio < 0.5:
            return {**COMPOUNDING_STRATEGY[1], "phase_found": True}
        elif passive_ratio < 0.7:
            return {**COMPOUNDING_STRATEGY[2], "phase_found": True}
        else:
            return {**COMPOUNDING_STRATEGY[3], "phase_found": True}

    def plan_reinvestment(self, revenue_data: dict[str, float]) -> dict[str, Any]:
        """Planeja como reinvestir a receita do próximo ciclo."""
        phase = self.calculate_phase(revenue_data)
        reinvest_rate = phase["reinvest_rate"]
        total_revenue = sum(revenue_data.values())
        reinvestment_budget = total_revenue * reinvest_rate

        # Em produção: alocação inteligente baseada em ROI histórico
        allocation = {
            "content_production": reinvestment_budget
            * 0.4,  # Mais conteúdo = mais tráfego
            "new_agents_development": reinvestment_budget * 0.15,
            "membership_content": reinvestment_budget * 0.15,
            "tools_and_infrastructure": reinvestment_budget * 0.1,
            "experimental_new_sources": reinvestment_budget * 0.2,
        }

        return {
            "current_phase": phase["name"],
            "phase_description": phase["description"],
            "total_revenue": round(total_revenue, 2),
            "reinvestment_rate": reinvest_rate,
            "reinvestment_budget": round(reinvestment_budget, 2),
            "allocation": {k: round(v, 2) for k, v in allocation.items()},
            "projected_growth": self._project_growth(
                phase, reinvestment_budget, total_revenue
            ),
            "actions": self._generate_actions(phase, allocation),
        }

    def _project_growth(
        self, phase: dict, reinvestment: float, current_revenue: float
    ) -> dict[str, Any]:
        """Projeta crescimento baseado no compounding."""
        # Simplified projection model
        monthly_growth = reinvestment / max(current_revenue, 1) * 0.3
        return {
            "estimated_monthly_growth": round(monthly_growth * 100, 1),
            "projected_revenue_3_months": round(
                current_revenue * (1 + monthly_growth) ** 3, 2
            ),
            "projected_revenue_6_months": round(
                current_revenue * (1 + monthly_growth) ** 6, 2
            ),
            "projected_revenue_12_months": round(
                current_revenue * (1 + monthly_growth) ** 12, 2
            ),
            "note": "Projeção baseada em modelo de compounding. Resultados reais podem variar.",
        }

    def _generate_actions(self, phase: dict, allocation: dict) -> list[str]:
        """Gera ações específicas para a fase atual."""
        actions = [
            f"Reinvestir R$ {allocation.get('content_production', 0):.0f} em produção de conteúdo",
            f"Alocar R$ {allocation.get('experimental_new_sources', 0):.0f} para testar novas fontes de renda",
        ]
        if phase["source_type"] == "direct":
            actions.append(
                "Foco em aumentar receita direta para financiar fases seguintes"
            )
        elif phase["source_type"] == "passive_first":
            actions.append(
                "Migrar receita direta para financiar canais passivos (AdSense, produtos)"
            )
        elif phase["source_type"] == "residual":
            actions.append(
                "Sistema autossustentável: reinvestir em experimentação e escala"
            )
        return actions

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        revenue_data = campaign.get(
            "revenue_data",
            {
                "affiliate_hotmart": campaign.get("revenue_hotmart", 0),
                "affiliate_amazon": campaign.get("revenue_amazon", 0),
                "adsense": campaign.get("revenue_adsense", 0),
                "digital_product": campaign.get("revenue_products", 0),
                "membership": campaign.get("revenue_membership", 0),
                "sponsorship": campaign.get("revenue_sponsorship", 0),
                "licensing": campaign.get("revenue_licensing", 0),
            },
        )
        # Remove zeros
        revenue_data = {k: v for k, v in revenue_data.items() if v}

        compounding_plan = self.plan_reinvestment(revenue_data)

        output = {
            "compounding": compounding_plan,
            "executive_summary": {
                "current_phase": compounding_plan["current_phase"],
                "reinvestment": f"R$ {compounding_plan['reinvestment_budget']:.2f} neste ciclo",
                "projected_12m": f"R$ {compounding_plan['projected_growth']['projected_revenue_12_months']:.2f}",
                "growth_rate": f"{compounding_plan['projected_growth']['estimated_monthly_growth']}%/mês",
            },
            "transformation_roadmap": [
                "Fase 1 → 2: Quando receita passiva > 30% do total",
                "Fase 2 → 3: Quando receita passiva > 50% do total",
                "Fase 3 → 4: Quando receita passiva > 70% do total (liberdade)",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="compounding",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Plano de compounding: {compounding_plan['reinvestment_budget']:.0f} para reinvestir em {compounding_plan['current_phase']}"
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
