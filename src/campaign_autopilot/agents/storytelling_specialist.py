"""Storytelling Specialist Agent — selects and applies narrative structures.

Focuses on narrative architecture: story arcs, beats, hooks, and emotional
sequencing for maximum engagement and persuasion.
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
from ..content_pipeline.storytelling_engine import StorytellingEngine


class StorytellingSpecialistAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("storytelling_specialist", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        niche = str(context.campaign.get("niche", "marketing digital"))
        items = self._get_items(context.step_results, context.campaign)

        arcs = []
        for item in items[:2]:
            topic = item.get("title", item.get("keyword", niche))
            structure = StorytellingEngine.select_structure("blog_article", "persuade")
            arc = StorytellingEngine.create_arc(structure)
            hook = StorytellingEngine.generate_hook(niche, topic, "curiosity_gap")
            title = StorytellingEngine.generate_title(niche, topic, "guide")
            cta = StorytellingEngine.generate_cta(niche, "medium")
            outline = arc.render_outline(topic, niche)
            arcs.append(
                {
                    "title": title,
                    "hook": hook,
                    "cta": cta,
                    "structure": structure.value,
                    "outline": outline,
                }
            )

        output = {
            "status": "success",
            "arcs_created": len(arcs),
            "arcs": arcs,
            "available_structures": StorytellingEngine.get_all_structures(),
        }
        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="storytelling_specialist",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[f"Created {len(arcs)} story arcs"],
                metadata={"arcs": len(arcs)},
            ),
        )

    def _get_items(self, sr, campaign):
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        articles = out.get("articles", []) or out.get("generated_articles", [])
        if articles:
            return articles
        seo = sr.get("seo_research", {})
        out2 = seo.get("output", {}) if isinstance(seo, dict) else {}
        kws = out2.get("top_opportunities", []) or out2.get("keywords", [])
        if kws:
            return kws
        return [{"keyword": str(campaign.get("objective", "teste"))}]
