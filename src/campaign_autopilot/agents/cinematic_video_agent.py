"""Cinematic Video Agent — enhanced video production with cinematic effects.

Uses the CinematicVideoProducer from media_pipeline to generate videos with:
- Ken Burns motion effects
- Professional transitions
- Cinematic color grading
- Optional audio narration sync
- YouTube and TikTok formats
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
from ..media_pipeline.video_cinematic import (
    CinematicVideoProducer,
    TransitionType,
    KenBurnsEffect,
)

try:
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class CinematicVideoAgent(AgentBase):
    """Produces cinematic-quality videos using free tools (MoviePy + Pillow)."""

    def __init__(self, **kwargs) -> None:
        super().__init__("cinematic_video_producer", **kwargs)
        self.producer = CinematicVideoProducer("output/videos")
        self.output_dir = Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        sr = context.step_results
        
        # Generate CTO-enriched video style prompt
        cto_video_style = None
        try:
            cto = CTOMediaPromptIntegrator()
            vp = cto.enrich_video_generation(niche, niche, "slideshow")
            if vp and "prompt" in vp:
                cto_video_style = vp["prompt"]
        except Exception:
            pass

        # Collect content
        articles = self._get_articles(sr)
        keywords = self._get_keywords(sr, campaign)
        audio_path = self._find_audio(sr)

        videos: list[dict[str, Any]] = []
        errors: list[str] = []

        # YouTube videos (from articles)
        for article in articles[:1]:
            try:
                title = article.get("title", niche)
                # Build script segments from article sections
                content = article.get("content", article.get("body", ""))
                lines = content.split("\n") if content else [title]
                segments = []
                for i, line in enumerate(lines[:6]):
                    line = line.strip()
                    if line and len(line) > 10 and not line.startswith("#"):
                        segments.append(
                            {
                                "text": line[:120],
                                "subtitle": f"Parte {len(segments) + 1}",
                                "icon": f"📌 {len(segments) + 1}",
                            }
                        )

                if not segments:
                    segments = [{"text": title, "subtitle": niche, "icon": "🎬"}]

                result = self.producer.produce_youtube_video(
                    title=title,
                    niche=niche,
                    script_segments=segments,
                    transition=TransitionType.CROSSFADE,
                    ken_burns=KenBurnsEffect.ZOOM_IN_SLOW,
                    audio_path=audio_path,
                )
                videos.append(result)
            except Exception as e:
                errors.append(f"yt: {e}")

        # TikTok / Short videos (using MoneyPrinterTurbo engine)
        for kw_info in keywords[:2]:
            try:
                kw = kw_info.get("keyword", kw_info.get("term", niche))
                tips = [
                    f"Dica 1: Comece focado em {kw}.",
                    "Dica 2: Crie conteúdo com consistência e qualidade.",
                    "Dica 3: Use as melhores palavras-chave no seu SEO.",
                    "Dica 4: Engaje e interaja sempre com a sua audiência.",
                ]
                script_text = f"Aqui estão quatro dicas rápidas para crescer em {kw}! " + " ".join(tips) + " Curtiu? Siga para mais dicas!"
                
                from ..media_pipeline.money_printer import TurboVideoProducer
                turbo_producer = TurboVideoProducer("output/videos")
                
                result = turbo_producer.produce_viral_short(
                    script_text=script_text,
                    niche=niche,
                    keyword=kw,
                )
                videos.append(result)
            except Exception as e:
                errors.append(f"tt: {e}")

        output = {
            "status": "success",
            "videos_generated": len(videos),
            "videos": videos,
            "errors": errors,
            "pipeline": "turbo_money_printer_v1",
            "features": ["edge_tts", "pexels_broll", "burned_subtitles", "ken_burns"],
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="cinematic_video_producer",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Produziu {len(videos)} vídeos cinematográficos. Erros: {len(errors)}"
            ],
            metadata={
                "videos": len(videos),
                "errors": len(errors),
                "pipeline": "cinematic_v2",
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

    def _find_audio(self, sr: dict) -> str | None:
        """Find audio narration from previous step."""
        audio = sr.get("audio_production", {})
        if isinstance(audio, dict):
            out = audio.get("output", {}) if "output" in audio else audio
            if isinstance(out, dict):
                narration = out.get("narration", {})
                if isinstance(narration, dict) and narration.get("status") == "success":
                    return narration.get("path")
                if out.get("status") == "success":
                    return out.get("path")
        return None
