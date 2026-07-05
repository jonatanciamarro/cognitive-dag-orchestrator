"""Content Excellence Agent — orchestrates all content quality improvements.

This is the main content excellence orchestrator that coordinates:
- Storytelling (narrative structure selection)
- Psychology (cognitive biases, persuasion)
- Psychoanalysis (deep triggers, archetypes)
- Neuromarketing (brain-based optimization)
- Communication (framing, tone, rhetoric)
- Archetypes (brand voice, personality)
- Copywriting (conversion frameworks)

Integrates with the existing content generator pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)

from ..content_pipeline.storytelling_engine import (
    StorytellingEngine,
)
from ..content_pipeline.psychology_engine import (
    PsychologyEngine,
)
from ..content_pipeline.psychoanalysis_engine import (
    PsychoanalysisEngine,
)
from ..content_pipeline.neuromarketing_engine import (
    NeuromarketingEngine,
)
from ..content_pipeline.communication_engine import (
    CommunicationEngine,
    MessageFrame,
)
from ..content_pipeline.archetype_engine import (
    ArchetypeEngine,
)
from ..content_pipeline.copywriting_engine import (
    CopywritingEngine,
)


class ContentExcellenceAgent(AgentBase):
    """Orchestrates content quality improvements using psychology, storytelling, etc.

    Analyzes content briefs and enhances them with:
    - Optimal narrative structure selection
    - Persuasion principle integration
    - Neuromarketing brain-based optimizations
    - Archetype-aligned brand voice
    - Communication framing strategy
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("content_excellence", **kwargs)
        self.output_dir = Path("output/content")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", "marketing digital"))
        audience = str(campaign.get("target_audience", "iniciantes"))
        sr = context.step_results

        # Collect content briefs/articles
        articles = self._get_articles(sr)
        briefs = self._get_briefs(sr)
        content_items = articles if articles else briefs
        keywords = self._get_keywords(sr, campaign)

        enhancements: list[dict[str, Any]] = []
        errors: list[str] = []

        for item in content_items[:3]:
            try:
                title = item.get("title", item.get("keyword", niche))
                topic = title

                # 1. Select best narrative structure
                structure = StorytellingEngine.select_structure(
                    "blog_article", "persuade"
                )
                arc = StorytellingEngine.create_arc(structure)
                outline = arc.render_outline(topic, niche)

                # 2. Create persuasion profile
                profile = PsychologyEngine.create_profile(niche, audience)
                psychology_apps = profile.get_applications()

                # 3. Select neuromarketing principles
                neuro_principles = NeuromarketingEngine.select_best_principles(
                    "blog_article", "persuade"
                )
                neuro_apps = [
                    NeuromarketingEngine.apply_principle_to_content(p, topic, niche)
                    for p in neuro_principles[:3]
                ]

                # 4. Create communication profile
                comm_profile = CommunicationEngine.create_profile(
                    niche, audience, "authority"
                )
                tone_guide = comm_profile.get_tone_guide()

                # 5. Select brand archetype
                archetypes = ArchetypeEngine.select_for_niche(niche, "convert")
                if archetypes:
                    archetype_exp = ArchetypeEngine.get_archetype(archetypes[0])

                # 6. Generate headline
                headline = CommunicationEngine.generate_headline(
                    niche,
                    topic,
                    MessageFrame.GAIN_FRAME,
                )

                # 7. Deep psychoanalysis
                deep_analysis = PsychoanalysisEngine.interpret_desire(niche, topic)
                shadow = PsychoanalysisEngine.apply_shadow_marketing(
                    niche, f"perder oportunidades em {niche}"
                )

                # 8. Generate hook
                hook = StorytellingEngine.generate_hook(niche, topic, "curiosity_gap")

                # 9. Generate CTA
                cta = StorytellingEngine.generate_cta(niche, "medium")

                # 10. Copywriting framework
                copy_fw = CopywritingEngine.select_best_framework(
                    "blog_article", "persuade"
                )
                copy_outline = CopywritingEngine.generate_copy_outline(
                    copy_fw, topic, niche
                )

                enhancement = {
                    "title": title,
                    "storytelling": {
                        "structure": structure.value,
                        "arc_name": arc.structure.value,
                        "outline": outline,
                        "hook": hook,
                        "cta": cta,
                        "headline": headline,
                    },
                    "psychology": {
                        "biases": [b.value for b in profile.biases],
                        "principles": [p.value for p in profile.principles],
                        "applications": psychology_apps[:3],
                    },
                    "psychoanalysis": {
                        "deep_desires": deep_analysis,
                        "shadow_marketing": shadow,
                    },
                    "neuromarketing": {
                        "brain_principles": [n["principle"] for n in neuro_apps],
                        "applications": neuro_apps,
                    },
                    "communication": {
                        "primary_tone": comm_profile.primary_tone.value,
                        "tone_guide": tone_guide,
                        "writing_rules": comm_profile.get_writing_rules(),
                    },
                    "archetype": {
                        "selected": archetypes[0].value if archetypes else "sage",
                        "profile": archetype_exp.to_dict() if archetypes else {},
                    },
                    "copywriting": {
                        "framework": copy_fw.value,
                        "outline": copy_outline,
                    },
                }
                enhancements.append(enhancement)

                # Save individual enhancement
                slug = item.get("slug", topic)[:30]
                enh_path = self.output_dir / f"enhancement_{slug}.json"
                with open(enh_path, "w") as f:
                    json.dump(enhancement, f, indent=2, default=str)
                enhancement["saved_path"] = str(enh_path)

            except Exception as e:
                errors.append(f"{item.get('title', 'unknown')}: {e}")

        output = {
            "status": "success",
            "content_enhanced": len(enhancements),
            "enhancements": enhancements,
            "errors": errors,
            "summary": {
                "total_items": len(content_items),
                "enhanced": len(enhancements),
                "storytelling_structures_used": list(
                    set(e["storytelling"]["structure"] for e in enhancements)
                ),
                "psychology_biases_deployed": list(
                    set(b for e in enhancements for b in e["psychology"]["biases"])
                ),
                "neuromarketing_principles": list(
                    set(
                        n
                        for e in enhancements
                        for n in e["neuromarketing"]["brain_principles"]
                    )
                ),
                "archetypes_used": list(
                    set(
                        e["archetype"]["selected"]
                        for e in enhancements
                        if e["archetype"]["selected"]
                    )
                ),
            },
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="content_excellence",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Aprimorou {len(enhancements)} conteúdos com storytelling, psicologia, neuromarketing"
            ],
            metadata={"enhanced": len(enhancements), "errors": len(errors)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _get_articles(self, sr: dict) -> list:
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        return out.get("articles", []) or out.get("generated_articles", [])

    def _get_briefs(self, sr: dict) -> list:
        cp = sr.get("content_planner", {})
        out = cp.get("output", {}) if isinstance(cp, dict) else {}
        return out.get("briefs", []) or out.get("content_briefs", [])

    def _get_keywords(self, sr: dict, campaign: dict) -> list:
        seo = sr.get("seo_research", {})
        out = seo.get("output", {}) if isinstance(seo, dict) else {}
        kws = out.get("top_opportunities", []) or out.get("keywords", [])
        if isinstance(kws, list) and kws:
            return kws
        return [{"keyword": str(campaign.get("objective", "teste"))}]
