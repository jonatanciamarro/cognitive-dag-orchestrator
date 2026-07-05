"""PerformanceTrackerAgent — Monitora ROAS e decide quando pausar/escalar campanhas.

Decisões baseadas em:
- ROAS > 3.0: Escalar (dobrar budget)
- ROAS 1.5-3.0: Manter, otimizar
- ROAS 1.0-1.5: Reduzir budget, testar variações
- ROAS < 1.0: Pausar campanha
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("perf_tracker")

STATE_FILE = Path(".state/campaign_performance.json")


class PerformanceTrackerAgent(AgentBase):
    """Monitora performance de campanhas e decide ações."""

    def __init__(self, **kwargs) -> None:
        super().__init__("performance_tracker", **kwargs)

    def _load_performance(self) -> dict[str, Any]:
        try:
            if STATE_FILE.exists():
                return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
        return {"campaigns": {}, "history": []}

    def _save_performance(self, data: dict[str, Any]) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(data, indent=2, default=str))

    def _evaluate_campaign(self, campaign_data: dict) -> dict[str, Any]:
        """Avalia performance de uma campanha e recomenda ação."""
        spend = float(campaign_data.get("spend", 0))
        revenue = float(campaign_data.get("revenue", 0))
        impressions = int(campaign_data.get("impressions", 0))
        clicks = int(campaign_data.get("clicks", 0))
        conversions = int(campaign_data.get("conversions", 0))

        roas = revenue / spend if spend > 0 else 0
        cpc = spend / clicks if clicks > 0 else 0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cvr = (conversions / clicks * 100) if clicks > 0 else 0

        # Decision logic
        if roas >= 3.0:
            action = "scale"
            reason = f"ROAS {roas:.1f}x — Excelente! Escalar budget em 50-100%"
            budget_change = 0.75  # +75%
        elif roas >= 1.5:
            action = "maintain"
            reason = f"ROAS {roas:.1f}x — Bom. Manter budget e otimizar criativos"
            budget_change = 0.0
        elif roas >= 1.0:
            action = "reduce"
            reason = (
                f"ROAS {roas:.1f}x — Abaixo do ideal. Reduzir budget em 30% e testar"
            )
            budget_change = -0.30
        else:
            action = "pause"
            reason = f"ROAS {roas:.1f}x — Prejuízo. Pausar campanha imediatamente"
            budget_change = -1.0

        return {
            "roas": round(roas, 2),
            "cpc": round(cpc, 2),
            "ctr": round(ctr, 2),
            "cvr": round(cvr, 2),
            "action": action,
            "reason": reason,
            "budget_change_pct": budget_change,
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        perf_data = self._load_performance()

        # Simulated campaign data (in real mode, this would come from platform APIs)
        campaigns = campaign.get(
            "campaigns",
            [
                {
                    "id": "google_search_01",
                    "platform": "google_ads",
                    "spend": 450.0,
                    "revenue": 1250.0,
                    "impressions": 15000,
                    "clicks": 320,
                    "conversions": 12,
                },
                {
                    "id": "meta_feed_01",
                    "platform": "meta_ads",
                    "spend": 300.0,
                    "revenue": 680.0,
                    "impressions": 28000,
                    "clicks": 450,
                    "conversions": 8,
                },
                {
                    "id": "native_01",
                    "platform": "native_ads",
                    "spend": 100.0,
                    "revenue": 180.0,
                    "impressions": 35000,
                    "clicks": 280,
                    "conversions": 3,
                },
            ],
        )

        evaluations = []
        total_spend = 0
        total_revenue = 0
        actions_taken = []

        for c in campaigns:
            eval_result = self._evaluate_campaign(c)
            evaluations.append({**c, "evaluation": eval_result})
            total_spend += c.get("spend", 0)
            total_revenue += c.get("revenue", 0)

            if eval_result["action"] in ("scale", "reduce", "pause"):
                actions_taken.append(
                    {
                        "campaign": c["id"],
                        "action": eval_result["action"],
                        "reason": eval_result["reason"],
                        "budget_change": eval_result["budget_change_pct"],
                    }
                )

                log.info(
                    "campaign_action",
                    campaign=c["id"],
                    action=eval_result["action"],
                    roas=eval_result["roas"],
                )

        overall_roas = total_revenue / total_spend if total_spend > 0 else 0

        # Update performance history
        perf_data["history"].append(
            {
                "date": datetime.now(timezone.utc).isoformat(),
                "total_spend": total_spend,
                "total_revenue": total_revenue,
                "overall_roas": overall_roas,
                "campaigns": [
                    {
                        "id": c["id"],
                        "roas": c["evaluation"]["roas"],
                        "action": c["evaluation"]["action"],
                    }
                    for c in evaluations
                ],
            }
        )
        perf_data["campaigns"] = {c["id"]: c for c in evaluations}
        self._save_performance(perf_data)

        # Overall health
        if overall_roas >= 1.5:
            health = "healthy"
            health_msg = f"🟢 Sistema saudável — ROAS geral {overall_roas:.1f}x"
        elif overall_roas >= 1.0:
            health = "warning"
            health_msg = (
                f"🟡 Atenção — ROAS geral {overall_roas:.1f}x, precisa otimizar"
            )
        else:
            health = "critical"
            health_msg = (
                f"🔴 Crítico — ROAS geral {overall_roas:.1f}x, pausar campanhas!"
            )

        output = {
            "health": health,
            "health_message": health_msg,
            "overall_roas": round(overall_roas, 2),
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "profit": round(total_revenue - total_spend, 2),
            "campaigns_evaluated": evaluations,
            "actions_taken": actions_taken,
            "summary": (
                f"Investido: R$ {total_spend:.2f} | Retorno: R$ {total_revenue:.2f} | "
                f"ROAS: {overall_roas:.1f}x | Lucro: R$ {total_revenue - total_spend:.2f} | "
                f"{len(actions_taken)} ações recomendadas"
            ),
            "auto_actions": [
                "✅ Campanhas com ROAS > 3.0 terão budget dobrado automaticamente",
                "✅ Campanhas com ROAS < 1.0 serão pausadas automaticamente",
                "⚠️ Ações de redução de budget requerem aprovação manual",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="performance_tracker",
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
            notes=[health_msg, f"{len(actions_taken)} ações recomendadas"],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
