"""Neuromarketing Specialist Agent — brain-based content optimization.

Applies neuromarketing principles to optimize content for the brain's
natural response patterns: dopamine, oxytocin, cognitive fluency, etc.
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
from ..content_pipeline.neuromarketing_engine import NeuromarketingEngine


class NeuromarketingSpecialistAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("neuromarketing_specialist", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        niche = str(context.campaign.get("niche", "marketing digital"))
        items = self._get_items(context.step_results, context.campaign)
        topic = (
            items[0].get("title", items[0].get("keyword", niche)) if items else niche
        )

        principles = NeuromarketingEngine.select_best_principles(
            "blog_article", "persuade"
        )
        apps = [
            NeuromarketingEngine.apply_principle_to_content(p, topic, niche)
            for p in principles[:5]
        ]

        output = {
            "status": "success",
            "recommended_principles": [p.value for p in principles],
            "applications": apps,
            "all_principles": NeuromarketingEngine.get_all_principles(),
        }
        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="neuromarketing_specialist",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[f"Applied {len(apps)} neuromarketing principles"],
                metadata={"principles": len(apps)},
            ),
        )

    def _get_items(self, sr, campaign):
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        arts = out.get("articles", []) or out.get("generated_articles", [])
        if arts:
            return arts
        return [{"keyword": str(campaign.get("objective", "teste"))}]
