"""Psychology Specialist Agent — applies cognitive biases and persuasion principles.

Focuses on psychological triggers, persuasion principles, and behavioral
economics to make content more persuasive and engaging.
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
from ..content_pipeline.psychology_engine import PsychologyEngine


class PsychologySpecialistAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("psychology_specialist", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        niche = str(context.campaign.get("niche", "marketing digital"))
        audience = str(context.campaign.get("target_audience", "iniciantes"))

        profile = PsychologyEngine.create_profile(niche, audience)
        apps = profile.get_applications()
        output = {
            "status": "success",
            "profile": {
                "biases": [b.value for b in profile.biases],
                "principles": [p.value for p in profile.principles],
                "triggers": [t.value for t in profile.triggers],
            },
            "applications": apps[:5],
            "all_biases": PsychologyEngine.get_all_biases(),
            "all_principles": PsychologyEngine.get_all_principles(),
        }
        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="psychology_specialist",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[f"Applied {len(apps)} persuasion elements"],
                metadata={"applications": len(apps)},
            ),
        )
