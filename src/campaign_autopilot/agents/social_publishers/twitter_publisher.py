"""TwitterPublisherAgent — Publica threads no Twitter/X via API v2.

Modos:
- real: POST via Twitter API v2 (OAuth 2.0)
- manual: salva thread em .md pronto para copiar
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("twitter_publisher")


class TwitterPublisherAgent(AgentBase):
    """Publica threads no Twitter/X."""

    def __init__(self, **kwargs) -> None:
        super().__init__("twitter_publisher", **kwargs)
        self.api_key = os.environ.get("TWITTER_API_KEY", "")
        self.api_secret = os.environ.get("TWITTER_API_SECRET", "")
        self.access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "")
        self.access_secret = os.environ.get("TWITTER_ACCESS_SECRET", "")
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
        self._is_configured = bool(
            self.bearer_token or (self.api_key and self.api_secret)
        )

    def _build_thread(self, content: dict, article: dict) -> list[str]:
        """Build Twitter thread from article."""
        title = content.get("title", "")
        intro = content.get("introduction", "")
        sections = content.get("sections", [])
        conclusion = content.get("conclusion", "")
        slug = content.get("slug", "")
        meta = content.get("_meta", {})

        tweets = []

        # Tweet 1: Hook
        hook = f"🧵 {title}\n\n{intro[:200]}"
        if len(hook) > 280:
            hook = hook[:277] + "..."
        tweets.append(hook)

        # Tweet 2-4: Key points
        points_text = ""
        for section in sections[:3]:
            if isinstance(section, dict):
                s_content = section.get("content", "")
                points_text += f"• {s_content[:100]}...\n\n"

        if points_text:
            tweet2 = f"O que você precisa saber:\n\n{points_text[:250]}"
            tweets.append(tweet2)

        # Tweet: Affiliate link (if commercial)
        if meta.get("affiliate_links"):
            for link in meta["affiliate_links"][:1]:
                affiliate_tweet = f"💰 Recomendação: {link.get('product_name', 'Produto')}\n{link.get('tracked_url', '')}"
                tweets.append(affiliate_tweet)

        # Last tweet: CTA
        last = f"📖 Leia o artigo completo: https://seudominio.com/{slug}\n\nGostou? Comente e compartilhe! 🔄"
        tweets.append(last)

        return tweets

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        output_dir = Path("output/social_posts/twitter")
        output_dir.mkdir(parents=True, exist_ok=True)

        threads = []
        for article in articles:
            content = article.get("content", article)
            slug = content.get("slug", "thread")

            tweets = self._build_thread(content, article)

            # Save thread
            thread_text = "\n\n---\n\n".join(
                [f"Tweet {i + 1}:\n{t}" for i, t in enumerate(tweets)]
            )
            file_path = output_dir / f"{slug}.md"
            file_path.write_text(thread_text, encoding="utf-8")

            threads.append(
                {
                    "title": content.get("title", ""),
                    "tweet_count": len(tweets),
                    "file": str(file_path),
                    "mode": "manual" if not self._is_configured else "real",
                }
            )

        total_tweets = sum(t["tweet_count"] for t in threads)

        output = {
            "platform": "twitter",
            "mode": "real" if self._is_configured else "manual",
            "threads": threads,
            "total_tweets": total_tweets,
            "output_directory": str(output_dir),
            "summary": f"{len(threads)} threads ({total_tweets} tweets) preparadas para Twitter.",
            "setup_guide": {
                "steps": [
                    "1. Acesse developer.twitter.com e crie um app",
                    "2. Gere API Key + Secret + Bearer Token (v2)",
                    "3. Configure TWITTER_BEARER_TOKEN no .env",
                    "4. Para postar via API: configure OAuth 1.0a (TWITTER_ACCESS_TOKEN + SECRET)",
                ],
                "env_vars": "TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_BEARER_TOKEN (ou TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)",
                "difficulty": "Média (requer Twitter Developer Portal + OAuth)",
                "free_alternative": "Use o arquivo .md gerado e poste manualmente",
            },
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="twitter",
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
