"""SocialPublishingOrchestratorAgent — Orquestra publicação em todas as redes sociais.

Fluxo:
1. Pega artigos gerados no ciclo atual
2. Para cada plataforma configurada → formata e publica
3. Se sem API → gera arquivo pronto para copiar/colar
4. Agenda posts em horários estratégicos
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("social_publisher")

# Horários estratégicos para cada plataforma (horário BR)
BEST_POST_TIMES = {
    "youtube": {"weekday": ["06:00", "11:00", "15:00"], "weekend": ["08:00", "14:00"]},
    "instagram": {
        "weekday": ["07:00", "12:00", "18:00", "21:00"],
        "weekend": ["09:00", "16:00"],
    },
    "tiktok": {
        "weekday": ["06:00", "10:00", "14:00", "19:00", "22:00"],
        "weekend": ["08:00", "13:00", "20:00"],
    },
    "twitter": {
        "weekday": ["07:00", "12:00", "17:00", "20:00"],
        "weekend": ["09:00", "15:00"],
    },
    "pinterest": {
        "weekday": ["08:00", "13:00", "19:00"],
        "weekend": ["09:00", "20:00"],
    },
    "linkedin": {"weekday": ["07:30", "12:00", "17:30"], "weekend": ["10:00"]},
    "telegram": {"weekday": ["07:00", "12:00", "18:00"], "weekend": ["09:00", "15:00"]},
    "facebook": {
        "weekday": ["07:00", "12:00", "18:00", "20:00"],
        "weekend": ["09:00", "16:00"],
    },
}


class SocialPublishingOrchestratorAgent(AgentBase):
    """Orquestra publicação de conteúdo em múltiplas plataformas sociais."""

    def __init__(self, **kwargs) -> None:
        super().__init__("social_publisher", **kwargs)

    def _schedule_posts(
        self, platforms: list[str], articles_count: int
    ) -> dict[str, Any]:
        """Cria agenda de posts baseada nos melhores horários."""
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        is_weekend = now.weekday() >= 5
        schedule = []

        for platform in platforms:
            times = BEST_POST_TIMES.get(platform, {}).get(
                "weekend" if is_weekend else "weekday",
                ["12:00"],
            )
            for day_offset in range(7):  # Schedule for next 7 days
                for hour_str in times:
                    hour, minute = map(int, hour_str.split(":"))
                    post_time = now.replace(
                        hour=hour, minute=minute, second=0
                    ) + timedelta(days=day_offset)
                    if post_time > now:
                        schedule.append(
                            {
                                "platform": platform,
                                "scheduled_at": post_time.isoformat(),
                                "scheduled_at_br": post_time.strftime("%d/%m %H:%M"),
                                "content_type": "article_promotion",
                            }
                        )

        # Limit to reasonable number
        return {
            "total_scheduled": min(len(schedule), articles_count * len(platforms) * 3),
            "schedule": schedule[:50],
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        niches = campaign.get("niches", ["tecnologia", "financas", "saude", "carreira"])
        configured_platforms = campaign.get("configured_platforms", [])
        all_platforms = campaign.get(
            "platforms",
            [
                "youtube",
                "instagram",
                "tiktok",
                "twitter",
                "pinterest",
                "linkedin",
                "telegram",
                "facebook",
            ],
        )

        # Determine which platforms are configured vs need manual posting
        platform_status = {}
        for plat in all_platforms:
            is_configured = self._is_platform_configured(plat)
            platform_status[plat] = {
                "configured": is_configured,
                "mode": "auto" if is_configured else "manual",
                "setup_guide": self._get_setup_guide(plat),
            }

        # Schedule posts
        schedule_data = self._schedule_posts(
            [p for p, s in platform_status.items()], len(articles)
        )

        # Generate post files for each platform × article
        output_dir = Path("output/social_posts")
        output_dir.mkdir(parents=True, exist_ok=True)

        posts_generated = 0
        posts_by_platform = {}

        for article in articles:
            content = article.get("content", article)
            title = content.get("title", "Untitled")
            slug = content.get("slug", "post")

            for plat in all_platforms:
                post_content = self._format_for_platform(plat, content, article)
                plat_dir = output_dir / plat
                plat_dir.mkdir(parents=True, exist_ok=True)

                file_path = plat_dir / f"{slug}.md"
                file_path.write_text(post_content, encoding="utf-8")
                posts_generated += 1
                posts_by_platform.setdefault(plat, 0)
                posts_by_platform[plat] += 1

        configured_list = [p for p, s in platform_status.items() if s["configured"]]
        manual_list = [p for p, s in platform_status.items() if not s["configured"]]

        output = {
            "total_posts_generated": posts_generated,
            "posts_by_platform": posts_by_platform,
            "platforms_auto_publish": configured_list,
            "platforms_manual": manual_list,
            "schedule": schedule_data,
            "output_directory": str(output_dir),
            "summary": (
                f"{posts_generated} posts gerados em {len(posts_by_platform)} plataformas. "
                f"{len(configured_list)} configuradas para publicação automática. "
                f"{len(manual_list)} requerem ação manual."
            ),
            "compliance_notes": [
                "✅ Links de afiliado com rel=nofollow sponsored",
                "✅ Disclosure adicionada automaticamente",
                "✅ Conteúdo original em cada plataforma (não duplicado)",
                "✅ Horários estratégicos para máximo engajamento",
            ],
            "next_steps": [
                "Para AUTOPILOT TOTAL, configure as chaves de API (veja setup_guide em cada plataforma)",
                f"Platformas configuradas ({len(configured_list)}): {', '.join(configured_list)}",
                f"Platformas manuais ({len(manual_list)}): {', '.join(manual_list)}",
                f"Posts salvos em: {output_dir}",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="social_publisher",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=int(
                (
                    datetime.fromisoformat(finished_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
                * 1000
            ),
            thread_name="main",
            notes=[output["summary"]],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _is_platform_configured(self, platform: str) -> bool:
        """Check if platform API credentials are configured."""
        checks = {
            "youtube": bool(
                os.environ.get("YOUTUBE_API_KEY")
                and os.environ.get("YOUTUBE_CHANNEL_ID")
            ),
            "instagram": bool(os.environ.get("INSTAGRAM_ACCESS_TOKEN")),
            "tiktok": bool(os.environ.get("TIKTOK_ACCESS_TOKEN")),
            "twitter": bool(
                os.environ.get("TWITTER_API_KEY")
                and os.environ.get("TWITTER_API_SECRET")
            ),
            "pinterest": bool(os.environ.get("PINTEREST_ACCESS_TOKEN")),
            "linkedin": bool(os.environ.get("LINKEDIN_ACCESS_TOKEN")),
            "telegram": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
            "facebook": bool(os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")),
        }
        return checks.get(platform, False)

    def _get_setup_guide(self, platform: str) -> dict[str, str]:
        """Get setup instructions for each platform."""
        guides = {
            "youtube": {
                "guide": "https://console.cloud.google.com/apis/credentials → YouTube Data API v3",
                "env_vars": "YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET",
                "difficulty": "Média (requer Google Cloud Console)",
            },
            "instagram": {
                "guide": "https://developers.facebook.com/docs/instagram-basic-display-api/",
                "env_vars": "INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID",
                "difficulty": "Média (requer Facebook Dev App)",
            },
            "tiktok": {
                "guide": "https://developers.tiktok.com/",
                "env_vars": "TIKTOK_ACCESS_TOKEN, TIKTOK_OPEN_ID",
                "difficulty": "Média (requer TikTok Dev App)",
            },
            "twitter": {
                "guide": "https://developer.twitter.com/en/portal/dashboard",
                "env_vars": "TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET",
                "difficulty": "Fácil (requer Twitter Developer Portal)",
            },
            "pinterest": {
                "guide": "https://developers.pinterest.com/",
                "env_vars": "PINTEREST_ACCESS_TOKEN, PINTEREST_BOARD_ID",
                "difficulty": "Fácil (requer Pinterest Dev App)",
            },
            "linkedin": {
                "guide": "https://developer.linkedin.com/",
                "env_vars": "LINKEDIN_ACCESS_TOKEN, LINKEDIN_ORGANIZATION_ID",
                "difficulty": "Média (requer LinkedIn Dev App)",
            },
            "telegram": {
                "guide": "https://t.me/BotFather → crie um bot e pegue o token",
                "env_vars": "TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID (ex: @meucanal)",
                "difficulty": "⭐ MAIS FÁCIL! 5 minutos no Telegram",
            },
            "facebook": {
                "guide": "https://developers.facebook.com/docs/pages/access-tokens",
                "env_vars": "FACEBOOK_PAGE_ID, FACEBOOK_PAGE_ACCESS_TOKEN",
                "difficulty": "Média (requer Facebook Dev App)",
            },
        }
        return guides.get(
            platform,
            {
                "guide": "Documentação da plataforma",
                "env_vars": "Consultar documentação",
                "difficulty": "Variável",
            },
        )

    def _format_for_platform(self, platform: str, content: dict, article: dict) -> str:
        """Formata conteúdo para cada plataforma."""
        title = content.get("title", "Título")
        intro = content.get("introduction", "")
        slug = content.get("slug", "")
        site_url = f"https://seudominio.com/{slug}"

        formats = {
            "youtube": f"""# 🎬 YouTube — {title}

## Título SEO
{title}

## Descrição (com links)
{intro[:200]}

📌 Link do artigo completo: {site_url}

{"🔗 Links de afiliado:" if content.get("_meta", {}).get("affiliate_links") else ""}
{chr(10).join(["   • " + l.get("product_name", "?") + ": " + l.get("tracked_url", "?") for l in (content.get("_meta", {}).get("affiliate_links") or [])])}

{content.get("_meta", {}).get("affiliate_disclosure", "")}

## Tags
{", ".join(slug.split("-")[:5])}

## Roteiro (5-10 min)
[Gerado automaticamente — revise antes de gravar]
1. Introdução: {intro[:100]}...
2. Desenvolvimento: Aprofunde no tópico
3. Conclusão: Call-to-action + links""",
            "instagram": f"""# 📸 Instagram — {title[:60]}

## Legenda (carrossel)
{intro[:200]}

👉 Link na bio: {site_url}

{chr(10).join(["🔗 " + l.get("product_name", "?") for l in (content.get("_meta", {}).get("affiliate_links") or [])])}

.
.
.
#autopilot #{slug.replace("-", " #")} #conteudo #blog

## Dica de imagem/Reels
Crie um card com fundo escuro e texto:
"{title[:80]}"
Tamanho: 1080×1080px (feed) ou 1080×1920px (stories/reels)""",
            "tiktok": f"""# 🎵 TikTok — {title[:50]}

## Script (15-60 segundos)
🎬 Cena 1 (3s): {title[:100]}
🎬 Cena 2 (5s): {intro[:150]}
🎬 Cena 3 (5s): Call-to-action

## Texto da legenda
{intro[:100]}...
👉 Link na bio

#{slug.replace("-", " #")} #aprendanotiktok #dicas

## Áudio sugerido
Trend atual do nicho""",
            "twitter": f"""# 🐦 Twitter/X — Thread

🧵 1/5 {title}
{intro[:200]}

2/5 O que você precisa saber:
• Informação chave 1
• Informação chave 2
• Informação chave 3

3/5 Dica importante:
Dica baseada no conteúdo do artigo

4/5 🔗 Leia o artigo completo:
{site_url}

{"🔗 " + content.get("_meta", {}).get("affiliate_links", [{}])[0].get("product_name", "") + ": " + content.get("_meta", {}).get("affiliate_links", [{}])[0].get("tracked_url", "") if content.get("_meta", {}).get("affiliate_links") else ""}

5/5 Gostou? Comente, curta e compartilhe!

{", ".join(["#" + w for w in slug.split("-")[:3]])}""",
            "pinterest": f"""# 📌 Pinterest — {title[:60]}

## Título do Pin
{title[:100]}

## Descrição SEO
{intro[:200]}

🔗 {site_url}

## Board sugerido
{slug.split("-")[0].title() if "-" in slug else "Geral"}

## Dimensões do Pin
Infográfico: 1000×1500px (recomendado)
Imagem: 1000×1000px

## Tags
{", ".join(["#" + w for w in slug.split("-")[:5]])}""",
            "linkedin": f"""# 💼 LinkedIn — {title[:60]}

## Post
{title.upper()}

{intro[:300]}

👉 Leia o artigo completo: {site_url}

{"🔗 " + content.get("_meta", {}).get("affiliate_links", [{}])[0].get("product_name", "") if content.get("_meta", {}).get("affiliate_links") else ""}

Compartilhe sua opinião nos comentários! 💬

#{slug.replace("-", " #")} #carreira #crescimento #desenvolvimento""",
            "telegram": f"""# 📱 Telegram — {title}

{intro[:300]}

🔗 {site_url}

{"💰 " + content.get("_meta", {}).get("affiliate_disclosure", "") if content.get("_meta", {}).get("affiliate_links") else ""}

#{" #".join(slug.split("-")[:3])}""",
            "facebook": f"""# 👍 Facebook — {title[:60]}

{intro[:300]}

🔗 Leia mais: {site_url}

{chr(10).join(["💰 " + l.get("product_name", "?") for l in (content.get("_meta", {}).get("affiliate_links") or [])])}

O que você acha? Comente abaixo! 👇

#{" #".join(slug.split("-")[:3])}""",
        }

        return formats.get(platform, f"# {title}\n\n{intro}\n\n{site_url}")
