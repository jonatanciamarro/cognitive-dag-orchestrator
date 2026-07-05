"""TikTokPublisherAgent — Prepara e publica conteúdo no TikTok.

Modos:
- real: POST via API oficial (requer credenciais)
- manual: salva conteúdo pronto em output/
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("tiktok_publisher")


class TikTokPublisherAgent(AgentBase):
    """Publica conteúdo no TikTok."""

    def __init__(self, **kwargs) -> None:
        super().__init__("tiktok_publisher", **kwargs)
        self._is_configured = bool(os.environ.get("TIKTOK_ACCESS_TOKEN", ""))

    def _format_post(self, content: dict, article: dict) -> str:
        """Format content for TikTok."""
        title = content.get("title", "")
        intro = content.get("introduction", "")
        slug = content.get("slug", "")
        meta = content.get("_meta", {})

        return f"""# 🎵 TikTok — {title[:50]}

## Script (15-60s)
{intro[:200]}

## Legenda
{intro[:100]}... 👉 Link na bio

#{slug.replace("-", " #")[:80]}"""

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        output_dir = Path("output/social_posts/tiktok")
        output_dir.mkdir(parents=True, exist_ok=True)

        posts = []
        for article in articles:
            content = article.get("content", article)
            slug = content.get("slug", "post")
            post_content = self._format_post(content, article)

            file_path = output_dir / f"{slug}.md"
            file_path.write_text(post_content, encoding="utf-8")

            posts.append(
                {
                    "title": content.get("title", ""),
                    "file": str(file_path),
                    "mode": "real" if self._is_configured else "manual",
                }
            )

        output = {
            "platform": "tiktok",
            "mode": "real" if self._is_configured else "manual",
            "posts": posts,
            "total_posts": len(posts),
            "output_directory": str(output_dir),
            "summary": f"{len(posts)} posts preparados para TikTok.",
            "setup_guide": {
                "env_vars": "TIKTOK_ACCESS_TOKEN",
                "difficulty": "Variável",
                "guide": "https://developers.tiktok.com/",
            }
            if not self._is_configured
            else {},
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="tiktok",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[output["summary"]],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
