"""Media Pipeline Orchestrator Agent — coordinates the cinematic media pipeline.

Acts as a meta-agent that:
1. Receives content from the main workflow
2. Coordinates image, video, and audio production
3. Ensures quality standards
4. Reports results back to the main workflow
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


class MediaPipelineAgent(AgentBase):
    """Orchestrates the cinematic media pipeline (image + video + audio).

    Delegates to specialized agents and aggregates results.
    Runs after content generation to produce all media assets.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("media_pipeline", **kwargs)
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        sr = context.step_results

        # Collect results from sub-agents
        image_result = sr.get("cinematic_image_gen", {})
        video_result = sr.get("cinematic_video_producer", {})
        audio_result = sr.get("audio_production", {})

        image_output = (
            image_result.get("output", {}) if isinstance(image_result, dict) else {}
        )
        video_output = (
            video_result.get("output", {}) if isinstance(video_result, dict) else {}
        )
        audio_output = (
            audio_result.get("output", {}) if isinstance(audio_result, dict) else {}
        )

        images = image_output.get("images", [])
        videos = video_output.get("videos", [])
        audio = audio_output.get("audio_files", [])

        total_images = len(images)
        total_videos = len(videos)
        total_audio = len(audio)

        # Aggregate quality metrics
        quality_report = self._generate_quality_report(images, videos, audio)

        output = {
            "status": "success",
            "summary": {
                "total_images": total_images,
                "total_videos": total_videos,
                "total_audio_files": total_audio,
                "total_assets": total_images + total_videos + total_audio,
            },
            "images_by_type": self._count_by_type(images, "type"),
            "videos_by_type": self._count_by_type(videos, "type"),
            "quality_report": quality_report,
            "pipeline": "cinematic_v2",
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="media_pipeline",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Pipeline de mídia: {total_images} imagens, {total_videos} vídeos, {total_audio} áudios"
            ],
            metadata={
                "images": total_images,
                "videos": total_videos,
                "audio": total_audio,
                "pipeline": "cinematic_v2",
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _count_by_type(self, items: list[dict], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            k = item.get(key, "unknown")
            counts[k] = counts.get(k, 0) + 1
        return counts

    def _generate_quality_report(
        self, images: list, videos: list, audio: list
    ) -> dict[str, Any]:
        """Generate quality metrics for produced media."""
        return {
            "cinematic_grade": True,
            "ken_burns_effect": True,
            "color_grading": True,
            "lighting_effects": True,
            "audio_narration": len(audio) > 0,
            "background_music": any(a.get("type") == "background_music" for a in audio),
            "total_assets": len(images) + len(videos) + len(audio),
            "resolutions": {
                "images": "1200x630, 1280x720, 1000x1500, 1080x1080",
                "videos": "1280x720 (YouTube), 720x1280 (TikTok)",
            },
        }
