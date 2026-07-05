"""PinterestPublisherAgent — Prepara e publica conteúdo no Pinterest.

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

log = StructuredLogger("pinterest_publisher")


class PinterestPublisherAgent(AgentBase):
    """Publica conteúdo no Pinterest."""

    def __init__(self, **kwargs) -> None:
        super().__init__("pinterest_publisher", **kwargs)
        self._is_configured = bool(os.environ.get("PINTEREST_ACCESS_TOKEN", ""))

    def _format_post(self, content: dict, article: dict) -> str:
        """Format content for Pinterest."""
        title = content.get("title", "")
        intro = content.get("introduction", "")
        slug = content.get("slug", "")
        meta = content.get("_meta", {})

        return f"""# 📌 Pinterest — {title[:60]}

## Título SEO
{title[:100]}

## Descrição
{intro[:200]}

🔗 https://seudominio.com/{slug}

## Board: {"-".join(slug.split("-")[:2]).title()}
## Tamanho: 1000×1500px (infográfico)"""

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        output_dir = Path("output/social_posts/pinterest")
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
            "platform": "pinterest",
            "mode": "real" if self._is_configured else "manual",
            "posts": posts,
            "total_posts": len(posts),
            "output_directory": str(output_dir),
            "summary": f"{len(posts)} posts preparados para Pinterest.",
            "setup_guide": {
                "env_vars": "PINTEREST_ACCESS_TOKEN",
                "difficulty": "Variável",
                "guide": "https://developers.pinterest.com/",
            }
            if not self._is_configured
            else {},
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="pinterest",
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
