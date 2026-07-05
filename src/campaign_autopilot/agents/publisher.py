"""Agente de Publicação — planeja cronograma, sugere canais e formata conteúdo."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class PublisherAgent(AgentBase):
    """Planeja a publicação de conteúdo: cronograma, canais, formato."""

    def __init__(self, **kwargs) -> None:
        super().__init__("publisher", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        planning = context.step_results.get("content_planner", {})
        compliance = context.step_results.get("compliance", {})
        campaign = context.campaign

        planning_output = (
            planning.get("output", {}) if isinstance(planning, dict) else {}
        )
        compliance_output = (
            compliance.get("output", {}) if isinstance(compliance, dict) else {}
        )
        briefs = planning_output.get("briefs", [])

        # Se compliance bloqueou, não publicar
        blocked = compliance_output.get("status") == "block"

        channels = list(campaign.get("channels", ["seo", "community", "newsletter"]))
        now = datetime.now(timezone.utc)

        # Gerar cronograma de publicação
        schedule = []
        for i, brief in enumerate(briefs[:10]):
            pub_date = now + timedelta(days=i * 3)  # Publicar a cada 3 dias
            primary_channel = channels[i % len(channels)] if channels else "seo"
            schedule.append(
                {
                    "position": i + 1,
                    "keyword": brief.get("keyword", ""),
                    "content_type": brief.get("content_type", "article"),
                    "channel": primary_channel,
                    "scheduled_date": pub_date.isoformat(),
                    "status": "blocked" if blocked else "scheduled",
                    "offers": brief.get("offers", []),
                    "estimated_effort_hours": 4
                    if brief.get("content_type") == "article"
                    else 2,
                }
            )

        # Estimar resultados
        total_clicks = 0
        for brief in briefs:
            vol = brief.get("estimated_volume", 1000)
            diff = brief.get("difficulty", 0.5)
            # CTR orgânico estimado: 3-5% para primeira página
            estimated_clicks = int(vol * (1 - diff) * 0.04)
            total_clicks += estimated_clicks

        output = {
            "schedule": schedule,
            "total_scheduled": len(schedule),
            "estimated_monthly_clicks_organic": total_clicks,
            "blocked": blocked,
            "channels_used": channels,
            "publishing_plan": (
                f"Publicar {len(schedule)} conteúdos nos próximos {len(schedule) * 3} dias "
                f"nos canais: {', '.join(channels)}. "
                f"Estimativa de cliques orgânicos mensais: ~{total_clicks}."
            ),
        }

        # Registrar explicação
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="publishing_plan",
                input_state={
                    "briefs_count": len(briefs),
                    "channels": channels,
                    "blocked": blocked,
                },
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "total_scheduled": len(schedule),
                    "estimated_clicks": total_clicks,
                },
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="publisher",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Agendou {len(schedule)} conteúdos para {', '.join(channels)}"],
            metadata={
                "scheduled": len(schedule),
                "channels": channels,
                "blocked": blocked,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
