"""Value Evolution Agent — Evolves the system's success criteria.

Examines and evolves the value system: what the system optimizes for,
detecting conflicts between values, and suggesting evolution.
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
from ..third_order.value_system import ValueSystemEngine


class ValueEvolutionAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("value_evolution", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        campaign = context.campaign

        profile = ValueSystemEngine.create_profile()
        conflicts = ValueSystemEngine.analyze_value_conflicts(profile)

        performance = {
            "revenue": campaign.get("revenue", 0.5),
            "target_revenue": campaign.get("target_revenue", 1.0),
            "traffic_growth": campaign.get("traffic_growth", 0.1),
            "cycles": campaign.get("cycles", 1),
        }
        evolution = ValueSystemEngine.suggest_evolution(profile, performance)
        ethics = ValueSystemEngine.generate_value_ethics_report(profile)

        output = {
            "status": "success",
            "current_values": profile.to_dict(),
            "top_values": profile.get_top_values(5),
            "conflicts": [c.to_dict() for c in conflicts],
            "suggested_evolution": evolution,
            "ethics_report": ethics,
            "all_dimensions": ValueSystemEngine.get_all_dimensions(),
        }

        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="value_evolution",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[
                    f"Sistema de valores: {len(profile.dimensions)} dimensões, {len(conflicts)} conflitos"
                ],
                metadata={
                    "values": len(profile.dimensions),
                    "conflicts": len(conflicts),
                },
            ),
        )
