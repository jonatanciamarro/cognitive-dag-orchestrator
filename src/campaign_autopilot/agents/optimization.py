from __future__ import annotations

from typing import Any, Dict, List

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class OptimizationAgent(AgentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__("optimization", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        analytics = context.step_results.get("analytics", {})
        compliance = context.step_results.get("compliance", {})
        memory = context.step_results.get("memory_lookup", {})
        campaign = context.campaign

        analytics_output = (
            analytics.get("output", {}) if isinstance(analytics, dict) else {}
        )
        compliance_output = (
            compliance.get("output", {}) if isinstance(compliance, dict) else {}
        )
        memory_output = memory.get("output", {}) if isinstance(memory, dict) else {}
        channels = list(campaign.get("channels", []))

        actions: List[Dict[str, Any]] = []
        risks: List[str] = list(analytics_output.get("risks", []))
        guardrails: List[str] = list(compliance_output.get("guardrails", []))
        learnings: List[str] = list(memory_output.get("learnings", []))

        # Query semantic memory for prior knowledge if store is available
        semantic_insights: list[str] = []
        if self.semantic_memory:
            for ch in channels:
                channel_concept = self.semantic_memory.find_concept(ch, "channel")
                if channel_concept:
                    claims = self.semantic_memory.query_claims(
                        subject=channel_concept["concept_id"],
                        min_confidence=0.3,
                        limit=5,
                    )
                    for claim in claims:
                        insight = f"{claim.get('subject_name', '?')} {claim['predicate']} {claim.get('object_name', '?')} (confidence: {claim['confidence']:.1f})"
                        semantic_insights.append(insight)
            if semantic_insights:
                learnings.extend(semantic_insights[:2])

        cpa_avg = analytics_output.get("metrics", {}).get("cpa_avg")
        ctr_avg = analytics_output.get("metrics", {}).get("ctr_avg")

        if compliance_output.get("status") == "block":
            actions.append(
                {
                    "id": "pause_launch",
                    "title": "Hold unsafe launch changes",
                    "owner": "compliance",
                    "channel": "all",
                    "change": "Do not ship new copy until all policy gaps are cleared.",
                    "priority": "high",
                    "rationale": "Compliance output includes blocking issues.",
                    "success_metric": "Zero open compliance violations.",
                    "guardrails": guardrails,
                }
            )
        else:
            budget_target = campaign.get("budget", 0)
            if isinstance(cpa_avg, (int, float)) and cpa_avg:
                action_change = (
                    "Shift 10-20% of spend toward best-performing channel segments."
                )
                if ctr_avg is not None and ctr_avg < 2.0:
                    action_change = "Prioritize creative testing on highest-impression channels before scaling spend."
                actions.append(
                    {
                        "id": "reallocate_budget",
                        "title": "Reallocate budget toward efficient segments",
                        "owner": "media",
                        "channel": ", ".join(channels) if channels else "primary",
                        "change": action_change,
                        "priority": "high",
                        "rationale": f"Observed CPA average of {cpa_avg:.2f} suggests tightening allocation.",
                        "success_metric": "Reduce CPA while protecting conversion volume.",
                        "guardrails": guardrails,
                    }
                )
            else:
                actions.append(
                    {
                        "id": "stabilize",
                        "title": "Stabilize pacing and gather more signal",
                        "owner": "media",
                        "channel": ", ".join(channels) if channels else "primary",
                        "change": "Maintain current spend, then run a controlled creative test.",
                        "priority": "medium",
                        "rationale": "Insufficient performance history to justify aggressive changes.",
                        "success_metric": "Collect enough data for a reliable next optimization pass.",
                        "guardrails": guardrails,
                    }
                )

        if learnings:
            actions.append(
                {
                    "id": "apply_memory",
                    "title": "Apply historical learnings",
                    "owner": "strategy",
                    "channel": "cross-channel",
                    "change": learnings[0],
                    "priority": "medium",
                    "rationale": "Prior campaign memory provides reusable patterns.",
                    "success_metric": "Mirror the highest-value historical pattern without repeating failures.",
                    "guardrails": guardrails,
                }
            )

        # Record explanation if store is available
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="optimization_proposal",
                input_state={
                    "cpa_avg": cpa_avg,
                    "ctr_avg": ctr_avg,
                    "channels": channels,
                    "compliance_blocked": compliance_output.get("status") == "block",
                    "semantic_insights_count": len(semantic_insights),
                },
            )
            for action in actions:
                self.explanation_store.record_rule_application(
                    decision_id=decision_id,
                    rule_source=f"optimization.{action['id']}",
                    rule_value=action["rationale"],
                    actual_value=action["change"],
                    comparison_result=True,
                    rule_order=actions.index(action) + 1,
                )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "proposal": actions[0]["id"] if actions else "none",
                    "action_count": len(actions),
                },
            )

        output = {
            "actions": actions,
            "risks": risks,
            "guardrails": guardrails,
            "semantic_insights": semantic_insights,
            "source_signals": {
                "analytics": analytics_output,
                "compliance": compliance_output,
                "memory": memory_output,
            },
        }
        finished_at = utc_now_iso()
        duration_ms = iso_duration_ms(started_at, finished_at)
        trace = AgentTrace(
            agent=self.name,
            step_id="optimization",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            thread_name="main",
            notes=["Synthesized optimization actions from upstream agent outputs."],
            metadata={"action_count": len(actions)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
