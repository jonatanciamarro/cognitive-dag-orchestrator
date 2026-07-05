from __future__ import annotations

from typing import Any, Iterable

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).lower()


def _contains_any(text: str, needles: Iterable[str]) -> list[str]:
    hits = []
    for needle in needles:
        needle_l = needle.lower()
        if needle_l and needle_l in text:
            hits.append(needle)
    return hits


class ComplianceAgent(AgentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__("compliance", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        policy = context.policy
        content_text = " ".join(
            _normalize_text(campaign.get(field))
            for field in ("headline", "description", "copy", "cta")
        )
        restricted_terms = list(policy.get("restricted_terms", []))
        required_disclosures = list(policy.get("required_disclosures", []))
        banned_hits = _contains_any(content_text, restricted_terms)
        disclosure_hits = [
            term for term in required_disclosures if term.lower() in content_text
        ]

        violations = []
        if banned_hits:
            violations.append(f"Restricted terms present: {', '.join(banned_hits)}")
        if required_disclosures and len(disclosure_hits) < len(required_disclosures):
            violations.append("Missing one or more required disclosures.")
        if float(campaign.get("budget", 0) or 0) <= 0:
            violations.append("Campaign budget must be positive.")

        guardrails = list(policy.get("guardrails", []))
        if not guardrails:
            guardrails = [
                "Review new copy before launch.",
                "Preserve opt-out and disclosure requirements.",
            ]

        status = "block" if violations else "pass"

        # Record explanation if store is available
        if self.explanation_store:
            _cycle_id = context.run_id
            _input_state = {
                "banned_hits": banned_hits,
                "disclosure_hits": disclosure_hits,
                "budget": campaign.get("budget", 0),
                "restricted_terms": restricted_terms,
                "required_disclosures": required_disclosures,
            }
            _decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=_cycle_id,
                decision_type="compliance_gate",
                input_state=_input_state,
            )
            if banned_hits:
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="policy.restricted_terms",
                    rule_value=restricted_terms,
                    actual_value=banned_hits,
                    comparison_result=False,
                    rule_order=1,
                )
                self.explanation_store.record_counterfactual(
                    decision_id=_decision_id,
                    changed_field="banned_hits",
                    changed_from=banned_hits,
                    changed_to=[],
                    predicted_outcome="pass",
                )
            if required_disclosures and len(disclosure_hits) < len(
                required_disclosures
            ):
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="policy.required_disclosures",
                    rule_value=required_disclosures,
                    actual_value=disclosure_hits,
                    comparison_result=False,
                    rule_order=2,
                )
                self.explanation_store.record_counterfactual(
                    decision_id=_decision_id,
                    changed_field="disclosure_hits",
                    changed_from=disclosure_hits,
                    changed_to=required_disclosures,
                    predicted_outcome="pass",
                )
            if float(campaign.get("budget", 0) or 0) <= 0:
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="policy.budget_positive",
                    rule_value=">0",
                    actual_value=campaign.get("budget", 0),
                    comparison_result=False,
                    rule_order=3,
                )
            if not violations:
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="comprehensive_check",
                    rule_value="no_violations",
                    actual_value="no_violations",
                    comparison_result=True,
                    rule_order=1,
                )
            self.explanation_store.update_decision_output(
                decision_id=_decision_id,
                output_decision={"status": status, "violations": violations},
            )

        output = {
            "status": status,
            "violations": violations,
            "guardrails": guardrails,
            "required_disclosures_seen": disclosure_hits,
            "review_required": bool(violations),
        }
        finished_at = utc_now_iso()
        duration_ms = iso_duration_ms(started_at, finished_at)
        trace = AgentTrace(
            agent=self.name,
            step_id="compliance",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            thread_name="main",
            notes=["Validated campaign content against configured policy."],
            metadata={"violations_count": len(violations)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
