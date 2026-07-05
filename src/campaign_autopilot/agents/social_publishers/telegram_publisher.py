"""TelegramPublisherAgent — Publica conteúdo no Telegram via Bot API.

⚡ MAIS FÁCIL DE CONFIGURAR! 5 minutos:
1. Fale com @BotFather no Telegram → /newbot → pegue o token
2. Adicione o bot ao seu canal como admin
3. Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHANNEL_ID no .env

Modos:
- real: POST via API do Telegram
- manual: salva arquivo .md pronto para copiar
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("telegram_publisher")


def _http_post(url: str, data: dict, timeout: int = 30) -> tuple[int, Any]:
    import urllib.request
    import urllib.error

    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 0, {"error": str(e)}


class TelegramPublisherAgent(AgentBase):
    """Publica conteúdo no Telegram automaticamente."""

    def __init__(self, **kwargs) -> None:
        super().__init__("telegram_publisher", **kwargs)
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.channel_id = os.environ.get("TELEGRAM_CHANNEL_ID", "")
        self._is_configured = bool(self.bot_token and self.channel_id)

    def _publish_to_telegram(
        self, text: str, parse_mode: str = "HTML"
    ) -> dict[str, Any]:
        """Send message to Telegram channel via Bot API."""
        if not self._is_configured:
            return {
                "mode": "manual",
                "error": "Bot token ou channel ID não configurados",
            }

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }

        status, response = _http_post(url, data)
        if status == 200:
            result = response.get("result", {})
            return {
                "mode": "real",
                "message_id": result.get("message_id"),
                "date": result.get("date"),
                "chat": result.get("chat", {}).get("title", self.channel_id),
            }
        else:
            return {
                "mode": "failed",
                "error": response.get("description", str(response))[:200],
            }

    def _format_message(self, article: dict) -> str:
        """Format article as Telegram HTML message."""
        content = article.get("content", article)
        title = content.get("title", "Novo artigo")
        intro = content.get("introduction", "")
        slug = content.get("slug", "")
        site_url = f"https://seudominio.com/{slug}"

        msg = f"<b>📝 {title}</b>\n\n"
        msg += f"{intro[:400]}\n\n"
        msg += f"🔗 <a href='{site_url}'>Leia o artigo completo</a>\n"

        # Add affiliate links if present
        meta = content.get("_meta", {})
        if meta.get("affiliate_links"):
            msg += "\n💰 <i>Links recomendados:</i>\n"
            for link in meta["affiliate_links"][:2]:
                msg += f"• <a href='{link.get('tracked_url', link.get('url', ''))}'>{link.get('product_name', 'Produto')}</a>\n"

        if meta.get("affiliate_disclosure"):
            msg += f"\n<i>{meta['affiliate_disclosure']}</i>"

        msg += f"\n\n#{' #'.join(slug.split('-')[:3])}"
        return msg

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        niche = campaign.get("niche", "geral")
        output_dir = Path("output/social_posts/telegram")
        output_dir.mkdir(parents=True, exist_ok=True)

        published = []
        for article in articles:
            message = self._format_message(article)

            if self._is_configured:
                result = self._publish_to_telegram(message)
                published.append(
                    {
                        "title": article.get("content", article).get(
                            "title", "Untitled"
                        ),
                        "status": result.get("mode", "manual"),
                        "message_id": result.get("message_id"),
                        "error": result.get("error"),
                    }
                )
                log.info(
                    "telegram_publish",
                    title=article.get("content", {}).get("title", "")[:40],
                    status=result.get("mode"),
                )

                # Rate limit: max 20 messages per minute
                import time

                time.sleep(3)
            else:
                # Save to file
                slug = article.get("content", article).get("slug", "post")
                file_path = output_dir / f"{slug}.html"
                file_path.write_text(message, encoding="utf-8")
                published.append(
                    {
                        "title": article.get("content", article).get(
                            "title", "Untitled"
                        ),
                        "status": "manual",
                        "file": str(file_path),
                    }
                )

        auto_count = sum(1 for p in published if p.get("status") == "real")
        manual_count = sum(1 for p in published if p.get("status") == "manual")
        failed_count = sum(1 for p in published if p.get("status") == "failed")

        output = {
            "platform": "telegram",
            "mode": "real" if self._is_configured else "manual",
            "published": published,
            "auto_published": auto_count,
            "manual_saved": manual_count,
            "failed": failed_count,
            "channel": self.channel_id or "Não configurado",
            "summary": (
                f"Telegram: {auto_count} publicados automaticamente"
                if self._is_configured
                else f"Telegram: {manual_count} posts salvos em {output_dir}"
            ),
            "setup_guide": {
                "steps": [
                    "1. Abra o Telegram e procure @BotFather",
                    "2. Envie /newbot e siga as instruções",
                    "3. Copie o token do bot",
                    "4. Adicione o bot como admin do seu canal",
                    "5. Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHANNEL_ID no .env",
                ],
                "env_vars": "TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID (ex: @meucanal ou -1001234567890)",
                "difficulty": "⭐ Muito Fácil (5 minutos)",
            },
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="telegram",
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
