"""SafeMassPostingAgent — Publicacao segura em massa sem ser considerado spam.

Maximiza a quantidade de conteudo postado por plataforma respeitando:
- Limites de frequencia de cada plataforma
- Variacao minima de conteudo (anti-duplicacao)
- Regras de compliance por plataforma
- Timing ideal de postagem
- Volume maximo seguro antes de trigger de spam
"""

from __future__ import annotations

import hashlib
import json
import random
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ..logging_utils import StructuredLogger

log = StructuredLogger("safe_mass_posting")
MEMORY_FILE = Path(".state/safe_posting_memory.json")

# ── Limites maximos seguros por plataforma (dados empiricos 2024-2026) ──
# Fonte: Documentacao oficial + reports de creators + experiencia pratica
# Valores: "max_daily" = maximo seguro POR CONTA antes de flag de spam
#          "min_interval_min" = intervalo minimo entre posts
#          "max_weekly" = maximo semanal seguro
#          "variation_threshold" = % minima de diferenca entre posts consecutivos

PLATFORM_LIMITS = {
    "blog": {
        "name": "Blog/Site",
        "max_daily": 10,
        "max_weekly": 50,
        "max_monthly": 200,
        "min_interval_min": 30,
        "variation_threshold": 0.30,
        "best_hours": [6, 7, 8, 9, 10, 11, 12, 17, 18, 19, 20],
        "best_days": [0, 1, 2, 3, 4, 5, 6],  # todos os dias
        "notes": "Conteudo original e de qualidade. Evitar copia exata.",
        "max_identical_keywords": 3,
    },
    "youtube": {
        "name": "YouTube",
        "max_daily": 2,
        "max_weekly": 7,
        "max_monthly": 30,
        "min_interval_min": 240,  # 4h entre videos
        "variation_threshold": 0.40,
        "best_hours": [11, 12, 13, 14, 15, 16, 17, 18, 19],
        "best_days": [1, 2, 3, 4, 5],  # ter-sex
        "notes": "Nao publicar mais de 3 videos em 24h. Canal novo: max 1/dia.",
        "max_shorts_daily": 3,
        "longform_min_interval_hours": 24,
    },
    "instagram": {
        "name": "Instagram",
        "max_daily": 3,
        "max_weekly": 15,
        "max_monthly": 60,
        "min_interval_min": 180,  # 3h entre posts
        "variation_threshold": 0.35,
        "best_hours": [8, 9, 10, 11, 12, 17, 18, 19, 20, 21],
        "best_days": [0, 1, 2, 3, 4, 5, 6],
        "notes": "Feed: max 2-3/dia. Stories: max 10/dia. Reels: max 3/dia.",
        "max_stories_daily": 10,
        "max_reels_daily": 3,
        "max_carousels_daily": 2,
    },
    "tiktok": {
        "name": "TikTok",
        "max_daily": 5,
        "max_weekly": 20,
        "max_monthly": 80,
        "min_interval_min": 60,
        "variation_threshold": 0.40,
        "best_hours": [7, 8, 9, 12, 13, 14, 18, 19, 20, 21, 22],
        "best_days": [1, 2, 3, 4, 5, 6],
        "notes": "Conta nova: 1-2/dia nas primeiras 2 semanas. Max 5/dia para contas estabelecidas.",
        "max_duet_daily": 3,
    },
    "twitter": {
        "name": "Twitter/X",
        "max_daily": 15,
        "max_weekly": 80,
        "max_monthly": 300,
        "min_interval_min": 15,
        "variation_threshold": 0.25,
        "best_hours": [7, 8, 9, 10, 11, 12, 17, 18, 19, 20],
        "best_days": [0, 1, 2, 3, 4, 5, 6],
        "notes": "Max 50 posts/dia para evitar shadowban. Threads contam como 1 post.",
        "max_threads_daily": 3,
        "max_media_daily": 15,
    },
    "pinterest": {
        "name": "Pinterest",
        "max_daily": 25,
        "max_weekly": 100,
        "max_monthly": 400,
        "min_interval_min": 10,
        "variation_threshold": 0.20,
        "best_hours": [8, 9, 10, 11, 12, 19, 20, 21, 22],
        "best_days": [0, 1, 2, 3, 4, 5, 6],
        "notes": "Pinterest permite volume alto. Ideal: 10-15 pins/dia. Max 25/dia.",
        "max_boards": 50,
        "pins_per_board_max_daily": 5,
    },
    "linkedin": {
        "name": "LinkedIn",
        "max_daily": 2,
        "max_weekly": 10,
        "max_monthly": 40,
        "min_interval_min": 240,
        "variation_threshold": 0.40,
        "best_hours": [7, 8, 9, 10, 11, 12, 17, 18],
        "best_days": [1, 2, 3, 4],  # ter-sex
        "notes": "Max 1 post/dia e 1 artigo/semana para perfil pessoal. Paginas: max 5/dia.",
        "max_articles_weekly": 1,
    },
    "facebook": {
        "name": "Facebook",
        "max_daily": 5,
        "max_weekly": 25,
        "max_monthly": 100,
        "min_interval_min": 120,
        "variation_threshold": 0.30,
        "best_hours": [8, 9, 10, 11, 12, 17, 18, 19, 20],
        "best_days": [0, 1, 2, 3, 4, 5, 6],
        "notes": "Pagina: max 5/dia. Grupo: max 3/dia. Stories: max 10/dia.",
        "max_group_posts_daily": 3,
    },
    "telegram": {
        "name": "Telegram",
        "max_daily": 20,
        "max_weekly": 100,
        "max_monthly": 400,
        "min_interval_min": 5,
        "variation_threshold": 0.15,
        "best_hours": [7, 8, 9, 10, 11, 12, 17, 18, 19, 20, 21, 22],
        "best_days": [0, 1, 2, 3, 4, 5, 6],
        "notes": "Canal: max 20 posts/dia. Grupo: max 10 posts/dia para evitar spam.",
        "max_media_per_post": 10,
    },
    "whatsapp": {
        "name": "WhatsApp",
        "max_daily": 3,
        "max_weekly": 15,
        "max_monthly": 60,
        "min_interval_min": 60,
        "variation_threshold": 0.30,
        "best_hours": [9, 10, 11, 14, 15, 16, 17, 18],
        "best_days": [1, 2, 3, 4, 5],
        "notes": "Broadcast: max 3/dia. Grupo: max 5/dia. Horario comercial recomendado.",
        "max_broadcast_daily": 3,
    },
    "email": {
        "name": "Email Marketing",
        "max_daily": 1,
        "max_weekly": 5,
        "max_monthly": 20,
        "min_interval_min": 1440,  # 24h
        "variation_threshold": 0.40,
        "best_hours": [8, 9, 10, 11, 12],
        "best_days": [1, 2, 3, 4],
        "notes": "Lei CAN-SPAM/LGPD. Opt-out obrigatorio. Max 1 email/dia por lista.",
        "max_emails_per_campaign": 1,
    },
}

# Fatores de seguranca por tipo de conta
ACCOUNT_MATURITY_MULTIPLIERS = {
    "new": 0.3,  # < 30 dias
    "growing": 0.5,  # 30-90 dias
    "established": 0.7,  # 3-12 meses
    "mature": 1.0,  # 1+ ano
    "verified": 1.2,  # verificado
}

# Limites de seguranca para evitar flag de bot
SECURITY_PATTERNS = {
    "identical_titles": {"max": 3, "window_days": 7},
    "identical_images": {"max": 2, "window_days": 30},
    "same_link_multiple_platforms": {"max": 5, "window_hours": 24},
    "rapid_fire": {"max_posts_per_hour": 5, "cooldown_minutes": 30},
    "hashtag_reuse": {"max_same_hashtags": 10, "window_posts": 20},
}


class SafeMassPostingAgent(AgentBase):
    """Agente de publicacao segura em massa.

    Maximiza volume de conteudo postado sem ativar flags de spam.
    Respeita limites por plataforma, variacao de conteudo,
    timing ideal e maturidade da conta.
    """

    def __init__(self, **kwargs):
        super().__init__("safe_mass_posting", **kwargs)
        self._lock = threading.RLock()
        self.memory = self._load()

    def _load(self):
        try:
            if MEMORY_FILE.exists():
                return json.loads(MEMORY_FILE.read_text())
        except Exception:
            pass
        return {
            "posts_log": [],
            "daily_counts": {},
            "weekly_counts": {},
            "monthly_counts": {},
            "hashes": [],
            "total_posts_safe": 0,
            "total_blocks": 0,
        }

    def _save(self):
        with self._lock:
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.memory["updated_at"] = datetime.now(timezone.utc).isoformat()
            # Keep only last 90 days of logs
            cutoff = datetime.now(timezone.utc) - timedelta(days=90)
            self.memory["posts_log"] = [
                p
                for p in self.memory.get("posts_log", [])
                if p.get("timestamp", "") >= cutoff.isoformat()
            ]
            MEMORY_FILE.write_text(json.dumps(self.memory, indent=2, default=str))

    def _content_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    def _content_similarity(self, text1: str, text2: str) -> float:
        """Jaccard similarity of word sets."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)

    def _get_platform_limit(self, platform: str) -> dict:
        return PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["blog"])

    def _get_account_multiplier(
        self, account_age_days: int, is_verified: bool = False
    ) -> float:
        if is_verified:
            return 1.2
        if account_age_days < 30:
            return 0.3
        if account_age_days < 90:
            return 0.5
        if account_age_days < 365:
            return 0.7
        return 1.0

    def _count_posts_in_window(self, platform: str, window_hours: int) -> int:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=window_hours)
        return sum(
            1
            for p in self.memory.get("posts_log", [])
            if p.get("platform") == platform
            and p.get("timestamp", "") >= cutoff.isoformat()
        )

    def _count_posts_today(self, platform: str) -> int:
        today = datetime.now(timezone.utc).date().isoformat()
        return sum(
            1
            for p in self.memory.get("posts_log", [])
            if p.get("platform") == platform
            and p.get("timestamp", "").startswith(today)
        )

    def _count_posts_this_week(self, platform: str) -> int:
        now = datetime.now(timezone.utc)
        start_of_week = (now - timedelta(days=now.weekday())).date().isoformat()
        return sum(
            1
            for p in self.memory.get("posts_log", [])
            if p.get("platform") == platform
            and p.get("timestamp", "").startswith(start_of_week)
        )

    def validate_post(
        self,
        platform: str,
        content: dict,
        account_age_days: int = 365,
        is_verified: bool = False,
    ) -> dict:
        """Valida se um post pode ser publicado com seguranca."""
        limits = self._get_platform_limit(platform)
        multiplier = self._get_account_multiplier(account_age_days, is_verified)
        max_daily = int(limits["max_daily"] * multiplier)
        max_weekly = int(limits["max_weekly"] * multiplier)

        issues = []
        warnings = []

        # 1. Limite diario
        today_count = self._count_posts_today(platform)
        if today_count >= max_daily:
            issues.append(f"Limite diario atingido ({today_count}/{max_daily})")

        # 2. Limite semanal
        week_count = self._count_posts_this_week(platform)
        if week_count >= max_weekly:
            warnings.append(
                f"Limite semanal quase atingido ({week_count}/{max_weekly})"
            )

        # 3. Intervalo minimo
        last_post_time = None
        for p in reversed(self.memory.get("posts_log", [])):
            if p.get("platform") == platform:
                last_post_time = p.get("timestamp")
                break
        if last_post_time:
            last_dt = datetime.fromisoformat(last_post_time)
            elapsed_min = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
            if elapsed_min < limits["min_interval_min"]:
                wait_min = int(limits["min_interval_min"] - elapsed_min)
                warnings.append(
                    f"Intervalo minimo: aguardar {wait_min}min entre posts no {platform} (min: {limits['min_interval_min']}min). O scheduler ajustara automaticamente."
                )

        # 4. Variacao de conteudo (anti-spam)
        title = content.get("title", "")
        body = content.get("body", "") or content.get("description", "")
        text_to_check = title + " " + body
        content_hash = self._content_hash(text_to_check)

        recent_hashes = self.memory.get("hashes", [])[:50]
        similarity_found = False
        for h in recent_hashes:
            sim = self._content_similarity(text_to_check, h["text"])
            if sim > limits["variation_threshold"] and h.get("platform") == platform:
                warnings.append(
                    f"Conteudo similar ({sim:.0%}) no {platform}. Variacao minima: {limits['variation_threshold']:.0%}"
                )
                similarity_found = True
                break
            elif sim > 0.80 and h.get("platform") != platform:
                warnings.append(
                    f"Cross-platform similar content ({sim:.0%}) - OK, mas varie quando possivel"
                )
                break

        # 5. Horario ideal (melhor engajamento, menor chance de spam)
        current_hour = datetime.now(timezone.utc).hour
        if current_hour not in limits.get("best_hours", list(range(24))):
            warnings.append(
                f"Horario nao ideal para {platform}. Melhores: {limits['best_hours']}"
            )

        # 6. Rapid fire check
        posts_last_hour = self._count_posts_in_window(platform, 1)
        if posts_last_hour >= SECURITY_PATTERNS["rapid_fire"]["max_posts_per_hour"]:
            issues.append(
                f"Rapid fire detectado: {posts_last_hour} posts na ultima hora"
            )

        # 7. Links repetidos entre plataformas
        links_in_content = []
        if "links" in content:
            links_in_content = content["links"]
        link_matches = 0
        for p in self.memory.get("posts_log", [])[:50]:
            for link in links_in_content:
                if link in p.get("links", []):
                    link_matches += 1
        if link_matches >= SECURITY_PATTERNS["same_link_multiple_platforms"]["max"]:
            warnings.append(f"Link repetido em multiplas plataformas ({link_matches}x)")

        # 8. Content hash check on same platform only
        for h in recent_hashes:
            if h["hash"] == content_hash and h.get("platform") == platform:
                # Same hash on same platform = real duplicate
                if self._count_posts_today(platform) > 0:
                    issues.append(f"Conteudo identico ja publicado no {platform} hoje")
                break

        # 9. Check de hashtags repetidas
        hashtags = content.get("hashtags", [])
        recent_hashtag_usage = 0
        for p in self.memory.get("posts_log", [])[:20]:
            for tag in hashtags:
                if tag in p.get("hashtags", []):
                    recent_hashtag_usage += 1
        if (
            recent_hashtag_usage
            > SECURITY_PATTERNS["hashtag_reuse"]["max_same_hashtags"]
        ):
            warnings.append(f"Hashtags repetidas em excesso ({recent_hashtag_usage}x)")

        status = "block" if issues else "pass"
        if warnings and not issues:
            status = "warn"

        return {
            "status": status,
            "platform": platform,
            "max_daily": max_daily,
            "max_weekly": max_weekly,
            "today_count": today_count,
            "week_count": week_count,
            "issues": issues,
            "warnings": warnings,
            "content_hash": content_hash,
            "account_multiplier": multiplier,
            "remaining_today": max(0, max_daily - today_count),
            "remaining_week": max(0, max_weekly - week_count),
        }

    def log_post(self, platform: str, content: dict, validation: dict):
        """Registra um post publicado."""
        with self._lock:
            entry = {
                "platform": platform,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "title": content.get("title", ""),
                "content_type": content.get("content_type", "article"),
                "links": content.get("links", []),
                "hashtags": content.get("hashtags", []),
                "hash": validation.get("content_hash", ""),
                "status": validation.get("status", "unknown"),
                "post_id": content.get("post_id", ""),
            }
            self.memory["posts_log"].append(entry)
            self.memory["hashes"].append(
                {
                    "hash": validation.get("content_hash", ""),
                    "text": (
                        content.get("title", "") + " " + content.get("body", "")
                    ).strip(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            self.memory["total_posts_safe"] = self.memory.get("total_posts_safe", 0) + 1

            # Auto-cleanup of old hashes
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            self.memory["hashes"] = [
                h
                for h in self.memory.get("hashes", [])
                if h.get("timestamp", "") >= cutoff.isoformat()
            ]
            self._save()

    def generate_posting_plan(
        self, articles: list[dict], config: dict | None = None
    ) -> dict:
        """Gera um plano de postagem segura maximizada para multiplas plataformas."""
        config = config or {}
        account_age = config.get("account_age_days", 365)
        is_verified = config.get("is_verified", False)
        target_platforms = config.get("platforms", list(PLATFORM_LIMITS.keys()))

        plan = {}
        total_posts = 0

        for platform in target_platforms:
            limits = self._get_platform_limit(platform)
            multiplier = self._get_account_multiplier(account_age, is_verified)
            max_daily = int(limits["max_daily"] * multiplier)
            max_weekly = int(limits["max_weekly"] * multiplier)
            min_interval = limits["min_interval_min"]
            best_hours = limits.get("best_hours", list(range(24)))

            remaining_today = max(0, max_daily - self._count_posts_today(platform))
            remaining_week = max(0, max_weekly - self._count_posts_this_week(platform))

            daily_posts = min(len(articles), remaining_today, remaining_week)
            daily_posts = min(daily_posts, max_daily)

            posts_scheduled = []
            for i in range(min(daily_posts, len(articles))):
                art = articles[i % len(articles)]
                hour = best_hours[i % len(best_hours)]
                scheduled_time = datetime.now(timezone.utc).replace(
                    hour=hour, minute=random.randint(0, 59)
                ) + timedelta(minutes=i * min_interval)
                posts_scheduled.append(
                    {
                        "article": art.get("content", art).get("title", ""),
                        "slug": art.get("content", art).get("slug", ""),
                        "platform": platform,
                        "scheduled_time": scheduled_time.isoformat(),
                        "content_type": art.get("content_type", "article"),
                    }
                )

            plan[platform] = {
                "max_daily_safe": max_daily,
                "max_weekly_safe": max_weekly,
                "remaining_today": remaining_today,
                "remaining_week": remaining_week,
                "scheduled_count": len(posts_scheduled),
                "scheduled": posts_scheduled,
                "min_interval_min": min_interval,
                "best_hours": best_hours,
                "account_multiplier": multiplier,
            }
            total_posts += len(posts_scheduled)

        return {
            "plan": plan,
            "total_scheduled": total_posts,
            "articles_available": len(articles),
            "platforms_configured": len(target_platforms),
            "account_age_days": account_age,
            "is_verified": is_verified,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        camp = context.campaign if hasattr(context, "campaign") else {}
        articles = camp.get("articles", [])
        config = camp.get("posting_config", {})

        # Validate each article for each platform
        validations = {}
        blocked = 0
        posted = 0

        for art in articles:
            content = art.get("content", art)
            title = content.get("title", "")

            for platform in config.get("platforms", ["blog"]):
                validation = self.validate_post(
                    platform=platform,
                    content={
                        "title": title,
                        "body": content.get("body", ""),
                        "hashtags": content.get("hashtags", []),
                        "links": content.get("links", []),
                    },
                    account_age_days=config.get("account_age_days", 365),
                    is_verified=config.get("is_verified", False),
                )

                if platform not in validations:
                    validations[platform] = []
                validations[platform].append(
                    {
                        "article": title,
                        "validation": validation,
                    }
                )

                if validation["status"] == "block":
                    blocked += 1
                    with self._lock:
                        self.memory["total_blocks"] = (
                            self.memory.get("total_blocks", 0) + 1
                        )
                else:
                    # Log the post (simulated)
                    self.log_post(platform, content, validation)
                    posted += 1

        self._save()

        # Generate posting plan
        posting_plan = self.generate_posting_plan(articles, config)

        # Aggregated report
        platform_summary = {}
        for platform, vals in validations.items():
            fails = sum(1 for v in vals if v["validation"]["status"] == "block")
            warns = sum(1 for v in vals if v["validation"]["status"] == "warn")
            passes = sum(1 for v in vals if v["validation"]["status"] == "pass")
            platform_summary[platform] = {
                "total": len(vals),
                "pass": passes,
                "warn": warns,
                "block": fails,
                "remaining_today": vals[0]["validation"]["remaining_today"]
                if vals
                else 0,
                "max_daily": vals[0]["validation"]["max_daily"] if vals else 0,
            }

        output = {
            "articles_analyzed": len(articles),
            "posts_validated": len(validations),
            "posts_passed": posted,
            "posts_blocked": blocked,
            "block_rate": round(blocked / max(posted + blocked, 1) * 100, 1),
            "platform_summary": platform_summary,
            "posting_plan": posting_plan,
            "total_posts_safe_history": self.memory.get("total_posts_safe", 0),
            "total_blocks_history": self.memory.get("total_blocks", 0),
            "memory_path": str(MEMORY_FILE),
            "maximization_guide": {
                "resumo": "Para maximizar postagens sem spam, siga a ordem de prioridade:",
                "plataformas_alto_volume": ["pinterest", "telegram", "twitter", "blog"],
                "plataformas_medio_volume": ["tiktok", "instagram", "facebook"],
                "plataformas_baixo_volume": [
                    "youtube",
                    "linkedin",
                    "email",
                    "whatsapp",
                ],
                "dicas": [
                    "Pinterest permite maior volume (25 pins/dia) - use como principal canal de trafego",
                    "Telegram canais permitem 20 posts/dia sem restricao",
                    "Blog aceita ate 10 artigos/dia se forem originais",
                    "Varie titulos em pelo menos 30% entre posts",
                    "Nunca poste o mesmo link em mais de 5 plataformas em 24h",
                    "Use horarios de pico para maior engajamento e menor chance de spam",
                    "Aumente volume gradualmente ao longo de semanas (warm up)",
                    "Intercale tipos de conteudo (texto, imagem, video)",
                ],
                "warm_up_schedule_dias": {
                    "1-7": "30% do maximo",
                    "8-14": "50% do maximo",
                    "15-30": "70% do maximo",
                    "31+": "100% do maximo (se sem restricoes)",
                },
            },
        }

        trace = AgentTrace(
            agent=self.name,
            step_id="safe_mass_posting",
            status="success",
            started_at=started_at,
            finished_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=0,
            thread_name="main",
            notes=[
                f"{posted} posts validados",
                f"{blocked} bloqueados",
                f"{len(articles)} artigos",
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
