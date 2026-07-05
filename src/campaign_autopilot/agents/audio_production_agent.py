"""Audio Production Agent — narration and background music generation.

Uses the CinematicAudioProducer from media_pipeline to generate:
- TTS narration via gTTS (free)
- Algorithmic background music (free)
- Audio mixing and mastering
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
from ..media_pipeline.audio_cinematic import (
    CinematicAudioProducer,
    BackgroundMusic,
)


class AudioProductionAgent(AgentBase):
    """Produces audio content: narration, background music, and mixed tracks."""

    def __init__(self, **kwargs) -> None:
        super().__init__("audio_production", **kwargs)
        self.producer = CinematicAudioProducer("output/audio")
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        sr = context.step_results

        # Collect content to narrate
        articles = self._get_articles(sr)
        keywords = self._get_keywords(sr, campaign)
        
        # Generate CTO-enriched audio style prompt
        cto_audio_style = None
        try:
            cto = CTOMediaPromptIntegrator()
            ap = cto.enrich_audio_generation(niche, niche)
            if ap and "prompt" in ap:
                cto_audio_style = ap["prompt"]
        except Exception:
            pass

        audio_results: list[dict[str, Any]] = []
        errors: list[str] = []

        # 1. Narration for YouTube videos (from articles)
        for article in articles[:1]:
            try:
                title = article.get("title", niche)
                content = article.get("content", article.get("body", title))
                # Use first 500 chars for narration
                narration_text = content[:800] if len(content) > 100 else title

                # Smart narration: intro + key points
                intro = f"Olá! Hoje vamos falar sobre {title}. "
                body = narration_text[:700]
                full_text = intro + body

                result = self.producer.produce_full_audio_track(
                    script_text=full_text,
                    niche=niche,
                    bg_style=BackgroundMusic.AMBIENT,
                    narration_lang="pt-BR",
                    bg_volume_db=-10.0,
                )
                audio_results.append(
                    {
                        "type": "youtube_narration",
                        "title": title,
                        **result,
                    }
                )
            except Exception as e:
                errors.append(f"narration_yt: {e}")

        # 2. TikTok-style short narrations
        for kw_info in keywords[:2]:
            try:
                kw = kw_info.get("keyword", kw_info.get("term", niche))
                short_text = (
                    f"Você sabia? {kw}. Isso é essencial para quem quer {niche}. "
                )
                short_text += "Curta e compartilhe se gostou dessa dica!"

                result = self.producer.produce_full_audio_track(
                    script_text=short_text,
                    niche=niche,
                    bg_style=BackgroundMusic.LO_FI,
                    narration_lang="pt-BR",
                    bg_volume_db=-8.0,
                )
                audio_results.append(
                    {
                        "type": "tiktok_narration",
                        "keyword": kw,
                        **result,
                    }
                )
            except Exception as e:
                errors.append(f"narration_tt: {e}")

        # 3. Generate background music only (for videos without narration)
        try:
            music = self.producer.generate_background_music(
                duration_sec=60,
                style=BackgroundMusic.AMBIENT,
            )
            audio_results.append(
                {
                    "type": "background_music",
                    "style": "ambient",
                    **music,
                }
            )
        except Exception as e:
            errors.append(f"bg_music: {e}")

        output = {
            "status": "success",
            "audio_produced": len(audio_results),
            "audio_files": audio_results,
            "errors": errors,
            "pipeline": "cinematic_v2",
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="audio_production",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Produziu {len(audio_results)} faixas de áudio. Erros: {len(errors)}"
            ],
            metadata={"audio": len(audio_results), "errors": len(errors)},
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
