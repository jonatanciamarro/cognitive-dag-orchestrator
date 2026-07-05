"""Storyboard Agent — plans visual sequences for video and image production.

Creates structured storyboards for:
- YouTube videos (title, hook, content, CTA)
- TikTok/Reels (hook, tips, engagement)
- Image sequences (blog, social media, Pinterest)
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


class StoryboardAgent(AgentBase):
    """Plans visual sequences (storyboards) for media production.

    Generates structured scripts that the cinematic video/image producers
    use to create content with proper narrative flow.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("storyboard", **kwargs)
        self.output_dir = Path("output/storyboards")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        sr = context.step_results

        # Collect content
        articles = self._get_articles(sr)
        keywords = self._get_keywords(sr, campaign)

        storyboards: list[dict[str, Any]] = []
        errors: list[str] = []

        # YouTube storyboards from articles
        for article in articles[:2]:
            try:
                title = article.get("title", niche)
                content = article.get("content", article.get("body", ""))
                sb = self._create_youtube_storyboard(title, niche, content)
                storyboards.append(sb)
                # Save storyboard JSON
                slug = article.get("slug", title)[:20]
                sb_path = self.output_dir / f"storyboard_yt_{slug}.json"
                with open(sb_path, "w") as f:
                    json.dump(sb, f, indent=2)
                sb["path"] = str(sb_path)
            except Exception as e:
                errors.append(f"yt_storyboard: {e}")

        # TikTok storyboards
        for kw_info in keywords[:3]:
            try:
                kw = kw_info.get("keyword", kw_info.get("term", niche))
                sb = self._create_tiktok_storyboard(kw, niche)
                storyboards.append(sb)
                slug = kw[:15]
                sb_path = self.output_dir / f"storyboard_tt_{slug}.json"
                with open(sb_path, "w") as f:
                    json.dump(sb, f, indent=2)
                sb["path"] = str(sb_path)
            except Exception as e:
                errors.append(f"tt_storyboard: {e}")

        # Image sequence plan
        for article in articles[:1]:
            try:
                title = article.get("title", niche)
                sb = self._create_image_storyboard(title, niche, keywords)
                storyboards.append(sb)
            except Exception as e:
                errors.append(f"img_storyboard: {e}")

        output = {
            "status": "success",
            "storyboards": storyboards,
            "total": len(storyboards),
            "errors": errors,
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="storyboard",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Criou {len(storyboards)} storyboards"],
            metadata={"storyboards": len(storyboards), "errors": len(errors)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _create_youtube_storyboard(
        self, title: str, niche: str, content: str
    ) -> dict[str, Any]:
        """Create a YouTube video storyboard."""
        segments = [
            {"text": title.upper(), "subtitle": niche, "icon": "🎬", "type": "title"}
        ]

        # Content segments from article
        lines = [l for l in content.split("\n") if l.strip() and len(l.strip()) > 20]
        for i, line in enumerate(lines[:5]):
            segments.append(
                {
                    "text": line.strip()[:150],
                    "subtitle": f"Passo {i + 1}",
                    "icon": f"📌 {i + 1}",
                    "type": "content",
                }
            )

        # CTA
        segments.append(
            {
                "text": "Gostou? Inscreva-se para mais conteúdo! 🚀",
                "subtitle": f"Mais em {niche}",
                "icon": "🔔",
                "type": "cta",
            }
        )

        return {
            "type": "youtube",
            "title": title,
            "niche": niche,
            "format": "1280x720 (16:9)",
            "style": "cinematic",
            "segments": segments,
            "estimated_duration_sec": len(segments) * 4,
        }

    def _create_tiktok_storyboard(self, keyword: str, niche: str) -> dict[str, Any]:
        """Create a TikTok/Reels storyboard."""
        tips = [
            f"Foque em {niche} todos os dias",
            "Crie conteúdo que eduque",
            "Use gatilhos mentais",
            "Consistência é mais importante que perfeição",
            "Engaje nos comentários",
        ]

        segments = [
            {
                "text": f"⚠️ {keyword.upper()}",
                "subtitle": niche,
                "icon": "🔥",
                "type": "hook",
            },
        ]
        for i, tip in enumerate(tips[:4]):
            segments.append(
                {
                    "text": tip,
                    "subtitle": f"Dica {i + 1}/{min(4, len(tips))}",
                    "icon": f"✨ {i + 1}",
                    "type": "content",
                }
            )
        segments.append(
            {
                "text": "Segue para mais dicas! 🚀",
                "subtitle": f"#{niche.replace(' ', '')}",
                "icon": "🎯",
                "type": "cta",
            }
        )

        return {
            "type": "tiktok",
            "keyword": keyword,
            "niche": niche,
            "format": "720x1280 (9:16)",
            "style": "cinematic",
            "segments": segments,
            "estimated_duration_sec": len(segments) * 3,
        }

    def _create_image_storyboard(
        self, title: str, niche: str, keywords: list[dict]
    ) -> dict[str, Any]:
        """Create an image production plan."""
        kw_list = [k.get("keyword", k.get("term", niche)) for k in keywords[:5]]
        return {
            "type": "image_sequence",
            "title": title,
            "niche": niche,
            "formats": {
                "featured": {"count": 1, "style": "cinematic", "size": "1200x630"},
                "thumbnail": {"count": 1, "style": "dramatic", "size": "1280x720"},
                "pinterest_pins": {
                    "count": min(3, len(kw_list)),
                    "style": "vintage",
                    "size": "1000x1500",
                },
                "instagram_posts": {
                    "count": min(2, len(kw_list)),
                    "style": "bold",
                    "size": "1080x1080",
                },
                "social_card": {"count": 1, "style": "premium", "size": "1200x630"},
            },
            "keywords": kw_list,
        }

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
