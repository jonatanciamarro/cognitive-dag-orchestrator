"""Agente de Publicação em Lote — publica todo conteúdo gerado com agendamento inteligente."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
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


class BulkPublisherAgent(AgentBase):
    """Publica TODO o conteúdo gerado no ciclo de forma coordenada.

    Estratégia de agendamento:
    - Artigos blog: 1 a cada 2 dias
    - Vídeos YouTube: 1 por semana
    - Pins Pinterest: 1 por dia
    - WhatsApp: conforme cronograma semanal
    - Emails: conforme sequência (0, 1, 3, 7, 14 dias)
    """

    def __init__(self, output_dir: str = "output/published", **kwargs) -> None:
        super().__init__("bulk_publisher", **kwargs)
        self.output_dir = Path(output_dir)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc)
        schedule: list[dict[str, Any]] = []
        total_items = 0

        # 1. Blog articles → 1 cada 2 dias
        gen = context.step_results.get("content_generator", {})
        gen_out = gen.get("output", {}) if isinstance(gen, dict) else {}
        articles = gen_out.get("articles", [])
        for i, art in enumerate(articles):
            day = i * 2
            pub_date = now + timedelta(days=day)
            schedule.append(
                {
                    "channel": "blog",
                    "type": art.get("content_type", "article"),
                    "title": art.get("title", ""),
                    "scheduled_date": pub_date.isoformat(),
                    "day_offset": day,
                    "word_count": art.get("word_count", 0),
                    "file": self._save_asset("blog", art),
                }
            )
            total_items += 1

        # 2. YouTube videos → 1 por semana
        yt = context.step_results.get("youtube_marketing", {})
        yt_out = yt.get("output", {}) if isinstance(yt, dict) else {}
        videos = yt_out.get("videos", [])
        for i, vid in enumerate(videos):
            day = i * 7
            pub_date = now + timedelta(days=day)
            schedule.append(
                {
                    "channel": "youtube",
                    "type": "video",
                    "title": vid.get("title", ""),
                    "scheduled_date": pub_date.isoformat(),
                    "day_offset": day,
                    "duration_min": vid.get("estimated_duration_minutes", 10),
                    "file": self._save_asset("youtube", vid),
                }
            )
            total_items += 1

        # 3. Pinterest pins → 1 por dia
        pin = context.step_results.get("pinterest_marketing", {})
        pin_out = pin.get("output", {}) if isinstance(pin, dict) else {}
        pins = pin_out.get("pins", [])
        for i, p in enumerate(pins):
            pub_date = now + timedelta(days=i)
            schedule.append(
                {
                    "channel": "pinterest",
                    "type": "pin",
                    "title": p.get("title", ""),
                    "scheduled_date": pub_date.isoformat(),
                    "day_offset": i,
                    "board": p.get("board", ""),
                    "file": self._save_asset("pinterest", p),
                }
            )
            total_items += 1

        # 4. WhatsApp messages → conforme cronograma semanal
        wa = context.step_results.get("whatsapp_marketing", {})
        wa_out = wa.get("output", {}) if isinstance(wa, dict) else {}
        messages = wa_out.get("messages", [])
        day_map = {
            "immediate": 0,
            "segunda": 1,
            "terca": 2,
            "quarta": 3,
            "quinta": 4,
            "sexta": 5,
            "sabado": 6,
            "domingo": 7,
        }
        for msg in messages:
            sched = msg.get("schedule", "immediate")
            offset = (
                day_map.get(sched.split(",")[0].strip().lower(), 0)
                if isinstance(sched, str)
                else 0
            )
            pub_date = now + timedelta(days=offset) if offset > 0 else now
            schedule.append(
                {
                    "channel": "whatsapp",
                    "type": msg.get("type", "message"),
                    "title": msg.get("name", "Mensagem"),
                    "scheduled_date": pub_date.isoformat(),
                    "day_offset": offset,
                    "message_snippet": msg.get("body", "")[:80] + "...",
                }
            )
            total_items += 1

        # 5. Email sequences → delays configurados
        em = context.step_results.get("email_marketing", {})
        em_out = em.get("output", {}) if isinstance(em, dict) else {}
        sequences = em_out.get("sequences", [])
        for seq in sequences:
            for email in seq.get("emails", []):
                delay = email.get("delay_days", 0)
                pub_date = now + timedelta(days=delay)
                schedule.append(
                    {
                        "channel": "email",
                        "type": "email",
                        "title": f"{seq.get('name', 'Sequência')}: {email.get('subject', '')}",
                        "scheduled_date": pub_date.isoformat(),
                        "day_offset": delay,
                        "subject": email.get("subject", ""),
                        "goal": email.get("goal", ""),
                    }
                )
                total_items += 1

        # Sort by scheduled date
        schedule.sort(key=lambda x: x["day_offset"])

        # Generate publishing calendar
        calendar = self._generate_calendar(schedule, now)
        estimated_months = max(1, (schedule[-1]["day_offset"] if schedule else 0) / 30)

        output = {
            "niche": niche,
            "total_items_scheduled": total_items,
            "publishing_span_days": schedule[-1]["day_offset"] if schedule else 0,
            "estimated_months": round(estimated_months, 1),
            "schedule": schedule,
            "calendar": calendar,
            "output_directory": str(self.output_dir.absolute()),
            "recommendation": self._generate_recommendation(
                total_items, schedule, calendar
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="bulk_publishing",
                input_state={
                    "items": total_items,
                    "span_days": output["publishing_span_days"],
                },
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "scheduled": total_items,
                    "days": output["publishing_span_days"],
                },
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="bulk_publisher",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Agendou {total_items} itens em {output['publishing_span_days']} dias"
            ],
            metadata={
                "scheduled": total_items,
                "span_days": output["publishing_span_days"],
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _save_asset(self, subdir: str, data: dict) -> str:
        """Save content asset to output directory."""
        asset_dir = self.output_dir / subdir
        asset_dir.mkdir(parents=True, exist_ok=True)
        slug = data.get("slug", data.get("keyword", "asset"))[:30]
        filepath = asset_dir / f"{slug}.json"
        filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        return str(filepath)

    @staticmethod
    def _generate_calendar(
        schedule: list[dict], start: datetime
    ) -> list[dict[str, Any]]:
        """Generate weekly calendar view."""
        if not schedule:
            return []
        calendar = []
        current_week = 1
        week_items = []
        week_start = start

        for item in schedule:
            item_date = start + timedelta(days=item["day_offset"])
            if item_date > week_start + timedelta(days=7):
                if week_items:
                    calendar.append(
                        {
                            "week": current_week,
                            "start": week_start.isoformat(),
                            "items": week_items,
                        }
                    )
                    current_week += 1
                    week_start = week_start + timedelta(days=7)
                    week_items = []
            week_items.append(
                {
                    "day": item["day_offset"],
                    "channel": item["channel"],
                    "title": item["title"][:60],
                }
            )

        if week_items:
            calendar.append(
                {
                    "week": current_week,
                    "start": week_start.isoformat(),
                    "items": week_items,
                }
            )
        return calendar

    @staticmethod
    def _generate_recommendation(total: int, schedule: list, calendar: list) -> str:
        days = schedule[-1]["day_offset"] if schedule else 0
        per_week = round(total / max(1, days / 7), 1) if days > 0 else total
        busiest = max(calendar, key=lambda c: len(c["items"])) if calendar else None

        return (
            f"Publicar {total} itens ao longo de {days} dias "
            f"({per_week}/semana). "
            + (
                f" Semana mais intensa: {len(busiest['items'])} publicações."
                if busiest
                else ""
            )
            + " Estratégia: blog e Pinterest para tráfego contínuo, "
            "YouTube e WhatsApp para engajamento, email para conversão."
        )
