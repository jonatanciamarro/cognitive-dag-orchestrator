"""Cinematic Image Agent — enhanced image generation with cinematic quality.

Uses the CinematicImageProducer from the media_pipeline module to generate
high-quality images with color grading, lighting effects, film grain,
advanced typography, and compositing.
"""

from __future__ import annotations

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
from ..prompt_architect import CTOMediaPromptIntegrator
from ..media_pipeline.image_cinematic import (
    CinematicImageProducer,
    ImageStyle,
)

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class CinematicImageAgent(AgentBase):
    """Generates cinematic-quality images for all platforms.

    Supports: featured, thumbnail, pin, instagram, social card, infographic.
    Uses free tools only (Pillow + numpy).
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("cinematic_image_gen", **kwargs)
        self.producer = CinematicImageProducer("output/images")
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        sr = context.step_results

        if not HAS_PILLOW:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": "Pillow não instalado"},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="cinematic_image_gen",
                    status="error",
                    started_at=started_at,
                    finished_at=utc_now_iso(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        # Collect content from workflow
        articles = self._get_articles(sr)
        keywords = self._get_keywords(sr, campaign)
        titles = [a.get("title", niche) for a in articles[:3]]
        kw_list = [k.get("keyword", k.get("term", niche)) for k in keywords[:5]]
        
        # Generate CTO-enriched prompts for all media types
        cto_integrator = CTOMediaPromptIntegrator()
        cto_prompts = {}
        try:
            image_prompt_data = cto_integrator.enrich_image_generation(niche, niche, "blog_featured")
            if image_prompt_data and "prompt" in image_prompt_data:
                cto_prompts["image"] = image_prompt_data["prompt"]
        except Exception:
            pass

        generated: list[dict[str, Any]] = []
        errors: list[str] = []

        # 1. Cinematic featured images for each article
        for title in titles:
            try:
                result = self.producer.generate_featured_image(
                    title, niche, ImageStyle.CINEMATIC
                )
                generated.append(result)
            except Exception as e:
                errors.append(f"featured: {e}")

        # 2. YouTube thumbnails (dramatic style)
        for title in titles[:2]:
            try:
                result = self.producer.generate_youtube_thumbnail(
                    title, niche, ImageStyle.DRAMATIC
                )
                generated.append(result)
            except Exception as e:
                errors.append(f"thumbnail: {e}")

        # 3. Pinterest pins (vintage style for engagement)
        for kw in kw_list[:4]:
            try:
                result = self.producer.generate_pinterest_pin(
                    kw, niche, ImageStyle.VINTAGE
                )
                generated.append(result)
            except Exception as e:
                errors.append(f"pin: {e}")

        # 4. Instagram posts (bold style)
        for kw in kw_list[:3]:
            try:
                result = self.producer.generate_instagram_post(
                    kw, niche, ImageStyle.BOLD
                )
                generated.append(result)
            except Exception as e:
                errors.append(f"ig: {e}")

        # 5. Social cards
        for title in titles[:1]:
            try:
                result = self.producer.generate_social_card(
                    title, niche, ImageStyle.PREMIUM
                )
                generated.append(result)
            except Exception as e:
                errors.append(f"card: {e}")

        # 6. Infographics if we have keywords
        if kw_list:
            try:
                result = self.producer.generate_infographic_slide(
                    niche.upper(),
                    [f"Dica {i + 1}: {kw}" for i, kw in enumerate(kw_list[:5])],
                    niche,
                    ImageStyle.CINEMATIC,
                )
                generated.append(result)
            except Exception as e:
                errors.append(f"infographic: {e}")

        output = {
            "status": "success",
            "images_generated": len(generated),
            "images": generated,
            "errors": errors,
            "output_directory": str(self.output_dir.absolute()),
            "pipeline": "cinematic_v2",
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="cinematic_image_gen",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(generated)} imagens cinematográficas. Erros: {len(errors)}"
            ],
            metadata={
                "images": len(generated),
                "errors": len(errors),
                "pipeline": "cinematic_v2",
                "styles_used": [
                    ImageStyle.CINEMATIC.value,
                    ImageStyle.DRAMATIC.value,
                    ImageStyle.VINTAGE.value,
                    ImageStyle.BOLD.value,
                ],
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _get_articles(self, sr: dict) -> list:
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        return out.get("articles", []) or out.get("generated_articles", [])

    def _get_keywords(self, sr: dict, campaign: dict) -> list:
        seo = sr.get("seo_research", {})
        out = seo.get("output", {}) if isinstance(seo, dict) else {}
        kws = out.get("top_opportunities", []) or out.get("keywords", [])
        if isinstance(kws, list) and kws:
            return kws
        return [{"keyword": str(campaign.get("objective", "teste"))}]
