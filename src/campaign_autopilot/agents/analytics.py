from __future__ import annotations

from statistics import mean
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


def _as_number_series(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        series: list[float] = []
        for item in value:
            if isinstance(item, (int, float)):
                series.append(float(item))
        return series
    if isinstance(value, (int, float)):
        return [float(value)]
    return []


class AnalyticsAgent(AgentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__("analytics", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        signals = context.signals

        spend_series = _as_number_series(signals.get("daily_spend", []))
        conversion_series = _as_number_series(signals.get("daily_conversions", []))
        ctr_series = _as_number_series(signals.get("ctr", []))
        cpa_series = _as_number_series(signals.get("cpa", []))

        spend_avg = mean(spend_series) if spend_series else None
        conversions_avg = mean(conversion_series) if conversion_series else None
        ctr_avg = mean(ctr_series) if ctr_series else None
        cpa_avg = mean(cpa_series) if cpa_series else None

        objective = str(campaign.get("objective", "growth"))
        channels = [str(channel) for channel in campaign.get("channels", [])]
        recent_trend = "stable"
        if len(spend_series) >= 2 and spend_series[-1] > spend_series[0] * 1.1:
            recent_trend = "increasing spend"
        elif (
            len(conversion_series) >= 2
            and conversion_series[-1] >= conversion_series[0] * 1.1
        ):
            recent_trend = "improving conversion"

        opportunities = []
        if ctr_avg is not None and ctr_avg < 2.0:
            opportunities.append(
                "Improve click-through with stronger creative variation."
            )
        if cpa_avg is not None and cpa_avg > float(campaign.get("target_cpa", cpa_avg)):
            opportunities.append(
                "Reallocate budget to lower-CPA channels and tighten bidding."
            )
        if not opportunities:
            opportunities.append(
                "Maintain current pacing and keep testing incremental creative variants."
            )

        risks = []
        if (
            spend_avg is not None
            and float(campaign.get("budget", spend_avg)) <= spend_avg
        ):
            risks.append("Budget utilization is near the campaign cap.")
        if conversion_series and conversion_series[-1] == 0:
            risks.append("Recent conversions stalled.")

        # Compute thresholds before building output or recording explanations
        thresholds_passed = True
        if ctr_avg is not None and ctr_avg < 2.0:
            thresholds_passed = False
        if spend_avg is not None and float(campaign.get("budget", spend_avg or 0)) <= (
            spend_avg or 0
        ):
            thresholds_passed = False

        output = {
            "objective": objective,
            "channels": channels,
            "metrics": {
                "daily_spend_avg": spend_avg,
                "daily_conversions_avg": conversions_avg,
                "ctr_avg": ctr_avg,
                "cpa_avg": cpa_avg,
            },
            "trend": recent_trend,
            "opportunities": opportunities,
            "risks": risks,
            "confidence": 0.6 if spend_series or conversion_series else 0.3,
        }

        # Record explanation if store is available
        if self.explanation_store:
            _cycle_id = context.run_id
            _decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=_cycle_id,
                decision_type="metrics_gate",
                input_state={
                    "objective": objective,
                    "channels": channels,
                    "spend_avg": spend_avg,
                    "ctr_avg": ctr_avg,
                    "cpa_avg": cpa_avg,
                    "trend": recent_trend,
                },
            )
            # Record metrics threshold checks as rule applications
            if ctr_avg is not None and ctr_avg < 2.0:
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="metrics.ctr_minimum",
                    rule_value=">= 2.0",
                    actual_value=ctr_avg,
                    comparison_result=False,
                    rule_order=1,
                )
            if spend_avg is not None and float(
                campaign.get("budget", spend_avg or 0)
            ) <= (spend_avg or 0):
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="metrics.budget_utilization",
                    rule_value="spend < budget",
                    actual_value=f"spend={spend_avg}, budget={campaign.get('budget', 0)}",
                    comparison_result=False,
                    rule_order=2,
                )
            if thresholds_passed:
                self.explanation_store.record_rule_application(
                    decision_id=_decision_id,
                    rule_source="metrics.all_thresholds",
                    rule_value="pass",
                    actual_value="pass",
                    comparison_result=True,
                    rule_order=1,
                )
            self.explanation_store.update_decision_output(
                decision_id=_decision_id,
                output_decision={
                    "status": "pass" if thresholds_passed else "review",
                    "metrics": output.get("metrics", {}),
                },
            )

        # Extract semantic knowledge if memory store is available
        if self.semantic_memory and channels and ctr_avg is not None:
            _channel_str = channels[0] if channels else "unknown"
            self.semantic_memory.extract_cycle_knowledge(
                cycle_id=context.run_id,
                channel=_channel_str,
                metric_data={
                    "ctr": ctr_avg,
                    "cpa": cpa_avg,
                    "spend": spend_avg,
                    "conversions": conversions_avg,
                },
                all_metrics_passed=thresholds_passed,
                asserted_by=self.name,
                observer_id=self.name,
            )
        finished_at = utc_now_iso()
        duration_ms = iso_duration_ms(started_at, finished_at)
        trace = AgentTrace(
            agent=self.name,
            step_id="analytics",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            thread_name="main",
            notes=["Derived baseline performance signals from campaign input."],
            metadata={"channels_seen": len(channels)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
