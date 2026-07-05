"""Recursive Observer Agent — Meta-meta-orchestration.

Observes the MetaOrchestrator itself, auditing governance quality
and suggesting improvements to the governance layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)
from ..third_order.recursive_observer import RecursiveObserver


class RecursiveObserverAgent(AgentBase):
    def __init__(self, **kwargs):
        super().__init__("recursive_observer", **kwargs)
        self.history_file = Path(".state/meta_history.json")

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        campaign = context.campaign

        # Load meta history if available
        meta_history = []
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    meta_history = json.load(f).get("cycles", [])
            except Exception:
                meta_history = []

        audit = RecursiveObserver.create_audit(meta_history)
        meta_insights = RecursiveObserver.generate_meta_insights(dict(campaign))
        collapse_check = RecursiveObserver.check_recursive_collapse(0, 3)
        governance_check = RecursiveObserver.should_evolve_governance(audit)

        output = {
            "status": "success",
            "governance_audit": audit.to_dict(),
            "improvement_plan": audit.generate_improvement_plan(),
            "meta_insights": [i.to_dict() for i in meta_insights],
            "recursive_safety": collapse_check,
            "governance_evolution_needed": governance_check,
        }

        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="recursive_observer",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[
                    f"Auditou governança: {audit.quality_scores.get('overall_governance_health', 0):.2f} de saúde"
                ],
                metadata={
                    "meta_insights": len(meta_insights),
                    "recommendations": len(audit.recommendations),
                },
            ),
        )
