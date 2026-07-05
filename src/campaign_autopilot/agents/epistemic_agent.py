"""Epistemic Agent — Third-order self-questioning.

Detects what the system knows, doesn't know, and doesn't know it doesn't know.
Generates alternative hypotheses and challenges core assumptions.
"""

from __future__ import annotations

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)
from ..third_order.epistemic_engine import EpistemicEngine


class EpistemicAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("epistemic", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        niche = str(context.campaign.get("niche", "marketing digital"))

        km = EpistemicEngine.create_knowledge_map(niche)
        blind_spots = km.identify_blind_spots()
        challenges = EpistemicEngine.challenge_assumptions(km)
        report = EpistemicEngine.generate_epistemic_report(km)
        unknown_scan = EpistemicEngine.unknown_unknowns_scan(niche, {})

        # Generate hypothesis for a key phenomenon
        hypotheses = km.generate_alternative_hypotheses(
            "baixa conversão de tráfego em receita",
            "mais conteúdo orgânico gera mais receita",
        )

        output = {
            "status": "success",
            "knowledge_map": km.to_dict(),
            "blind_spots": [b.to_dict() for b in blind_spots],
            "assumptions_challenged": challenges,
            "epistemic_report": report,
            "unknown_unknowns": unknown_scan,
            "alternative_hypotheses": [h.to_dict() for h in hypotheses],
        }

        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="epistemic",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[
                    f"Mapeou conhecimento: {len(km.verified_facts)} fatos, {len(blind_spots)} pontos cegos, {len(hypotheses)} hipóteses"
                ],
                metadata={
                    "blind_spots": len(blind_spots),
                    "hypotheses": len(hypotheses),
                },
            ),
        )
