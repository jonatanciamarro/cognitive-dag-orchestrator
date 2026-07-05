"""Scheduler — editorial calendar, content scheduling, email drips.

Consolidado de: content_scheduler.py + email_sequences.py
"""

from __future__ import annotations
from datetime import datetime, timedelta


class EditorialCalendar:
    def __init__(self, niche: str):
        self.niche = niche
        self.items: list[dict] = []
        self.channels = [
            "blog", "youtube", "instagram", "tiktok", "pinterest", "twitter",
        ]

    def add_item(
        self, title: str, channel: str, scheduled_date: str,
        content_type: str, keyword: str = "",
    ):
        self.items.append({
            "title": title, "channel": channel,
            "scheduled_date": scheduled_date, "content_type": content_type,
            "keyword": keyword, "status": "scheduled",
            "created_at": datetime.now().isoformat(),
        })

    def get_week_schedule(self, start_date: str | None = None) -> list[dict]:
        return sorted(self.items, key=lambda x: x.get("scheduled_date", ""))[:14]

    def get_channel_distribution(self) -> dict:
        dist = {}
        for item in self.items:
            ch = item["channel"]
            dist[ch] = dist.get(ch, 0) + 1
        return dist

    def generate_weekly_plan(self, keywords: list[str], start_date: str) -> list[dict]:
        plan = []
        days = ["segunda", "terça", "quarta", "quinta", "sexta"]
        for i, day in enumerate(days):
            if i < len(keywords):
                plan.append({
                    "date": (datetime.fromisoformat(start_date) + timedelta(days=i)).date().isoformat(),
                    "day": day, "keyword": keywords[i],
                    "channel": self.channels[i % len(self.channels)],
                    "content_type": "article" if i % 3 == 0 else "video" if i % 3 == 1 else "social",
                })
        return plan


class ContentScheduler:
    @staticmethod
    def create_calendar(niche: str) -> EditorialCalendar:
        return EditorialCalendar(niche)

    @staticmethod
    def calculate_optimal_frequency(channel: str, niche: str) -> dict:
        frequencies = {
            "blog": {"min_per_week": 2, "ideal_per_week": 4, "max_per_week": 7},
            "youtube": {"min_per_week": 1, "ideal_per_week": 3, "max_per_week": 5},
            "instagram": {"min_per_week": 3, "ideal_per_week": 7, "max_per_week": 14},
            "tiktok": {"min_per_week": 3, "ideal_per_week": 7, "max_per_week": 14},
            "pinterest": {"min_per_week": 5, "ideal_per_week": 10, "max_per_week": 20},
            "twitter": {"min_per_week": 7, "ideal_per_week": 14, "max_per_week": 28},
        }
        return frequencies.get(channel, {"min_per_week": 1, "ideal_per_week": 3, "max_per_week": 7})

    @staticmethod
    def get_best_posting_time(channel: str, niche: str) -> dict:
        times = {
            "blog": "08:00", "youtube": "11:00", "instagram": "12:00",
            "tiktok": "19:00", "pinterest": "20:00", "twitter": "09:00", "email": "10:00",
        }
        return {
            "channel": channel, "recommended_time": times.get(channel, "10:00"),
            "timezone": "America/Sao_Paulo", "best_days": ["terça", "quinta", "sábado"],
        }


class DripCampaign:
    def __init__(self, name: str, niche: str):
        self.name = name
        self.niche = niche
        self.emails: list[dict] = []

    def add_email(self, subject: str, body_template: str, delay_days: int, goal: str = "nurture"):
        self.emails.append({
            "subject": subject, "body_template": body_template,
            "delay_days": delay_days, "goal": goal, "order": len(self.emails) + 1,
        })

    def get_sequence(self) -> list[dict]:
        return sorted(self.emails, key=lambda e: e["delay_days"])

    def to_dict(self) -> dict:
        return {
            "name": self.name, "niche": self.niche, "emails": self.emails,
            "total_emails": len(self.emails),
            "total_duration_days": sum(e["delay_days"] for e in self.emails),
        }


WELCOME_SEQUENCE = {
    "name": "boas_vindas",
    "emails": [
        {"subject": "Bem-vindo(a) ao {niche}! Aqui está seu presente", "delay_days": 0, "goal": "welcome"},
        {"subject": "O segredo que muda tudo em {niche}", "delay_days": 2, "goal": "engage"},
        {"subject": "3 erros que {niche} iniciantes cometem", "delay_days": 5, "goal": "educate"},
        {"subject": "Como {topic} pode transformar seus resultados", "delay_days": 8, "goal": "convert"},
    ],
}

AFFILIATE_SEQUENCE = {
    "name": "afiliados",
    "emails": [
        {"subject": "Você pediu, chegou: review de {product}", "delay_days": 0, "goal": "review"},
        {"subject": "{product} vs concorrência: qual ganha?", "delay_days": 2, "goal": "comparison"},
        {"subject": "Oferta especial {product} para assinantes", "delay_days": 5, "goal": "offer"},
        {"subject": "Último aviso: bônus exclusivo está acabando", "delay_days": 7, "goal": "urgency"},
    ],
}


class EmailSequenceEngine:
    @staticmethod
    def create_campaign(name: str, niche: str) -> DripCampaign:
        return DripCampaign(name, niche)

    @staticmethod
    def get_template(template_name: str, niche: str, topic: str = "", product: str = "") -> DripCampaign:
        templates = {"welcome": WELCOME_SEQUENCE, "affiliate": AFFILIATE_SEQUENCE}
        tpl = templates.get(template_name, WELCOME_SEQUENCE)
        campaign = DripCampaign(tpl["name"], niche)
        for email in tpl["emails"]:
            subject = email["subject"].replace("{niche}", niche).replace("{topic}", topic).replace("{product}", product)
            campaign.add_email(subject, email.get("body", subject), email["delay_days"], email["goal"])
        return campaign

    @staticmethod
    def generate_follow_up(campaign: DripCampaign, days_since_last: int = 3) -> dict:
        return {
            "subject": "Ainda estou pensando sobre sua jornada em " + campaign.niche,
            "delay_days": days_since_last, "goal": "follow_up",
            "body": "Só passando para ver se você teve chance de conferir o material...",
        }
