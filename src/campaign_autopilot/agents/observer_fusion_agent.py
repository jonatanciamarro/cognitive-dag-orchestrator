"""Observer Fusion Agent — Multi-perspective analysis.

Models any problem from multiple observer perspectives,
identifies conflicts, and generates transcendent syntheses.
"""

from __future__ import annotations

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)
from ..third_order.observer_fusion import ObserverFusionEngine


class ObserverFusionAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("observer_fusion", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        niche = str(context.campaign.get("niche", "marketing digital"))

        matrix = ObserverFusionEngine.create_matrix(niche)
        conflicts = matrix.analyze_conflicts(f"estratégia de conteúdo para {niche}")
        syntheses = matrix.generate_synthesis(f"{niche}")

        output = {
            "status": "success",
            "matrix": matrix.to_dict(),
            "perspectives_count": len(matrix.perspectives),
            "conflicts": conflicts,
            "syntheses": syntheses,
            "all_observers": ObserverFusionEngine.get_all_observers(),
        }

        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="observer_fusion",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[
                    f"Modelou {len(matrix.perspectives)} perspectivas, {len(conflicts)} conflitos, {len(syntheses)} sínteses"
                ],
                metadata={
                    "perspectives": len(matrix.perspectives),
                    "conflicts": len(conflicts),
                },
            ),
        )
