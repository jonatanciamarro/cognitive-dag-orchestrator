"""BudgetOptimizerAgent — Aloca orçamento de tráfego pago entre plataformas e campanhas.

Regras de alocação:
- 60% Google Ads (maior intenção de compra)
- 30% Meta Ads (remarketing + cold audience)
- 10% Native Ads (Taboola/Outbrain — reconhecimento)
- Ajusta baseado em ROAS histórico de cada plataforma
- Reserva 20% para teste de novos criativos
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("budget_optimizer")

DEFAULT_ALLOCATION = {
    "google_ads": 0.60,
    "meta_ads": 0.30,
    "native_ads": 0.10,
}

MIN_DAILY_BUDGET_PER_PLATFORM = 10.0  # Mínimo de R$ 10/dia por plataforma


class BudgetOptimizerAgent(AgentBase):
    """Otimiza alocação de orçamento entre plataformas de tráfego pago."""

    def __init__(self, **kwargs) -> None:
        super().__init__("budget_optimizer", **kwargs)

    def _get_platform_roas(self, history: list[dict]) -> dict[str, float]:
        """Calcula ROAS por plataforma baseado em histórico."""
        platform_metrics: dict[str, dict] = {}
        for entry in history:
            plat = entry.get("platform", "unknown")
            if plat not in platform_metrics:
                platform_metrics[plat] = {"spend": 0.0, "revenue": 0.0}
            platform_metrics[plat]["spend"] += entry.get("spend", 0)
            platform_metrics[plat]["revenue"] += entry.get("revenue", 0)

        return {
            plat: (metrics["revenue"] / metrics["spend"])
            if metrics["spend"] > 0
            else 1.0
            for plat, metrics in platform_metrics.items()
        }

    def _calculate_allocation(
        self,
        total_daily_budget: float,
        platform_roas: dict[str, float],
        active_platforms: list[str],
    ) -> dict[str, dict]:
        """Calcula alocação por plataforma com ajuste por ROAS."""
        # Start with default allocation
        allocation = dict(DEFAULT_ALLOCATION)

        # Adjust based on ROAS (better ROAS = more budget)
        if platform_roas:
            total_roas = sum(platform_roas.values())
            if total_roas > 0:
                for plat in allocation:
                    if plat in platform_roas:
                        # Weight: 60% default + 40% ROAS-based
                        roas_weight = platform_roas[plat] / total_roas
                        allocation[plat] = 0.6 * allocation[plat] + 0.4 * roas_weight

        # Normalize
        total = sum(allocation.values())
        if total > 0:
            for plat in allocation:
                allocation[plat] /= total

        # Calculate budgets
        result = {}
        testing_budget = total_daily_budget * 0.20  # 20% for testing
        main_budget = total_daily_budget - testing_budget

        for plat in active_platforms:
            plat_budget = main_budget * allocation.get(plat, 0)
            if plat_budget < MIN_DAILY_BUDGET_PER_PLATFORM and plat in active_platforms:
                # If platform is active but budget too low, give minimum
                plat_budget = MIN_DAILY_BUDGET_PER_PLATFORM

            result[plat] = {
                "daily_budget": round(plat_budget, 2),
                "allocation_pct": round(allocation.get(plat, 0) * 100, 1),
                "monthly_budget": round(plat_budget * 30, 2),
                "roas": round(platform_roas.get(plat, 1.0), 2),
                "status": "active",
            }

        result["testing"] = {
            "daily_budget": round(testing_budget, 2),
            "allocation_pct": 20.0,
            "monthly_budget": round(testing_budget * 30, 2),
            "purpose": "Testar novos criativos e públicos",
            "status": "active",
        }

        return result

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        total_budget = float(campaign.get("total_daily_budget", 0))
        active_platforms = campaign.get("active_platforms", ["google_ads", "meta_ads"])
        campaign_history = campaign.get("campaign_history", [])

        platform_roas = self._get_platform_roas(campaign_history)
        allocation = self._calculate_allocation(
            total_budget, platform_roas, active_platforms
        )

        total_allocated = sum(
            v["daily_budget"] for v in allocation.values() if isinstance(v, dict)
        )

        output = {
            "total_daily_budget": total_budget,
            "total_monthly_budget": round(total_budget * 30, 2),
            "total_allocated": round(total_allocated, 2),
            "allocation": allocation,
            "platform_roas": platform_roas,
            "summary": (
                f"Budget de R$ {total_budget:.2f}/dia alocado em {len(active_platforms)} plataformas. "
                f"ROAS médio estimado: {sum(platform_roas.values()) / max(len(platform_roas), 1):.2f}"
            ),
            "recommendations": [
                "Monitore ROAS semanalmente para ajustar alocação",
                "Se ROAS < 1.5 por 2 semanas, pause campanha e analise",
                "Teste novos criativos toda semana com 20% do orçamento",
                "Escale o que funciona: dobre budget se ROAS > 3.0",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="budget_optimizer",
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
            notes=[output["summary"]],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
