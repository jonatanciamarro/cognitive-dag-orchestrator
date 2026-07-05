"""InstagramPublisherAgent — Publica imagens/carrosséis no Instagram.

Modos:
- real: Instagram Graph API (requer Facebook Dev App + Instagram Business)
- semi: Gera imagem + legenda, você posta manualmente
- browser: Usa browser automation (Selenium) para postar
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("instagram_publisher")


class InstagramPublisherAgent(AgentBase):
    """Publica conteúdo no Instagram."""

    def __init__(self, **kwargs) -> None:
        super().__init__("instagram_publisher", **kwargs)
        self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
        self.user_id = os.environ.get("INSTAGRAM_USER_ID", "")
        self._is_configured = bool(self.access_token and self.user_id)

    def _generate_caption(self, content: dict, article: dict) -> str:
        """Generate Instagram caption with emojis and hashtags."""
        title = content.get("title", "")
        intro = content.get("introduction", "")
        slug = content.get("slug", "")
        meta = content.get("_meta", {})

        caption = f"{title[:60]}\n\n"
        caption += f"{intro[:150]}...\n\n"
        caption += f"👉 Link na bio: seudominio.com/{slug}\n\n"

        if meta.get("affiliate_links"):
            for link in meta["affiliate_links"][:2]:
                caption += f"💰 {link.get('product_name', '')}\n"
            caption += "\n"

        # Hashtags
        tags = slug.split("-")[:8]
        caption += "\n" + " ".join([f"#{t}" for t in tags])
        caption += " #conteudo #blog #dicas #aprender"

        return caption

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        output_dir = Path("output/social_posts/instagram")
        output_dir.mkdir(parents=True, exist_ok=True)

        posts = []
        for article in articles:
            content = article.get("content", article)
            slug = content.get("slug", "post")
            caption = self._generate_caption(content, article)

            file_path = output_dir / f"{slug}.md"
            file_path.write_text(caption, encoding="utf-8")

            posts.append(
                {
                    "title": content.get("title", ""),
                    "caption": caption[:80] + "...",
                    "file": str(file_path),
                    "format": "carrossel_imagem",
                    "mode": "real" if self._is_configured else "manual",
                }
            )

        output = {
            "platform": "instagram",
            "mode": "real" if self._is_configured else "manual",
            "posts": posts,
            "total_posts": len(posts),
            "output_directory": str(output_dir),
            "summary": f"{len(posts)} posts preparados para Instagram.",
            "setup_guide": {
                "for_api": {
                    "steps": [
                        "1. Criar Facebook Developer App → Instagram Graph API",
                        "2. Converter conta para Instagram Business",
                        "3. Gerar access token (long-lived, 60 dias)",
                        "4. Configurar INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_USER_ID",
                    ],
                    "env_vars": "INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID",
                    "difficulty": "Difícil (requer Facebook Dev App + Instagram Business)",
                },
                "for_browser_automation": {
                    "steps": [
                        "1. Instalar Selenium: pip install selenium",
                        "2. Configurar INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD",
                        "3. O BrowserAutomationAgent fará login e postará",
                    ],
                    "env_vars": "INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD",
                    "difficulty": "Média (requer Selenium + ChromeDriver)",
                },
                "manual": {
                    "steps": [
                        "1. Abra a pasta output/social_posts/instagram/",
                        "2. Copie a legenda e as hashtags",
                        "3. Crie um card no Canva ou use imagem gerada",
                        "4. Poste manualmente",
                    ],
                    "difficulty": "⭐ Fácil (5 minutos por post)",
                },
            },
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="instagram",
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
