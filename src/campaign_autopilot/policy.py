from __future__ import annotations

from dataclasses import dataclass

from .metrics import apply_anomaly_flags
from .models import Campaign, Decision, Metrics, Policy


@dataclass(slots=True)
class DecisionPlan:
    campaign_id: str
    policy: Policy
    metrics: Metrics
    decisions: list[Decision]

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "policy": self.policy.to_dict(),
            "metrics": self.metrics.to_dict(),
            "decisions": [decision.to_dict() for decision in self.decisions],
        }


class PolicyEngine:
    def __init__(self, policy: Policy | None = None):
        self.policy = policy or Policy()

    def evaluate(self, campaign: Campaign, metrics: Metrics) -> DecisionPlan:
        metrics = apply_anomaly_flags(
            metrics,
            min_impressions=self.policy.min_impressions,
            min_clicks=self.policy.min_clicks,
            min_ctr=self.policy.scale_min_ctr,
            min_cvr=self.policy.scale_min_cvr,
            max_cpa=(campaign.target_cpa * self.policy.pause_cpa_multiplier)
            if campaign.target_cpa
            else None,
            min_roas=(campaign.target_roas / self.policy.scale_roas_multiplier)
            if campaign.target_roas
            else None,
        )

        decisions: list[Decision] = []

        if self.policy.opt_in_required and not campaign.opt_in:
            decisions.append(
                Decision(
                    action="request_review",
                    campaign_id=campaign.campaign_id,
                    reason="Campaign is not opted in for automated optimization.",
                    confidence=1.0,
                    requires_review=True,
                )
            )
            return DecisionPlan(
                campaign_id=campaign.campaign_id,
                policy=self.policy,
                metrics=metrics,
                decisions=decisions,
            )

        if not campaign.compliance_ok:
            decisions.append(
                Decision(
                    action="request_review",
                    campaign_id=campaign.campaign_id,
                    reason="Campaign compliance status is not approved for automation.",
                    confidence=1.0,
                    requires_review=True,
                )
            )
            return DecisionPlan(
                campaign_id=campaign.campaign_id,
                policy=self.policy,
                metrics=metrics,
                decisions=decisions,
            )

        severe_risk = False
        if (
            "no_conversions" in metrics.anomaly_flags
            and metrics.clicks >= self.policy.min_clicks
        ):
            severe_risk = True
        if "high_cpa" in metrics.anomaly_flags or "low_roas" in metrics.anomaly_flags:
            severe_risk = True

        if severe_risk:
            decisions.append(
                Decision(
                    action="pause",
                    campaign_id=campaign.campaign_id,
                    reason="Performance risk exceeded policy thresholds.",
                    parameters={
                        "current_spend": round(metrics.spend, 6),
                        "current_cpa": None
                        if metrics.cpa is None
                        else round(metrics.cpa, 6),
                        "current_roas": None
                        if metrics.roas is None
                        else round(metrics.roas, 6),
                    },
                    confidence=0.9,
                    requires_review=True,
                )
            )
            decisions.append(
                Decision(
                    action="request_review",
                    campaign_id=campaign.campaign_id,
                    reason="Automation paused the campaign and requested human review.",
                    confidence=1.0,
                    requires_review=True,
                )
            )
            return DecisionPlan(
                campaign_id=campaign.campaign_id,
                policy=self.policy,
                metrics=metrics,
                decisions=decisions,
            )

        can_scale = (
            metrics.impressions >= self.policy.min_impressions
            and metrics.clicks >= self.policy.min_clicks
            and metrics.conversions >= self.policy.min_conversions
            and metrics.ctr >= self.policy.scale_min_ctr
            and metrics.cvr >= self.policy.scale_min_cvr
            and (
                metrics.roas is not None
                and campaign.target_roas
                and metrics.roas
                >= campaign.target_roas * self.policy.scale_roas_multiplier
            )
            and (
                metrics.cpa is not None
                and campaign.target_cpa
                and metrics.cpa
                <= campaign.target_cpa * self.policy.scale_cpa_multiplier
            )
        )

        if can_scale:
            decisions.append(
                Decision(
                    action="scale_budget",
                    campaign_id=campaign.campaign_id,
                    reason="Campaign cleared scale thresholds with compliant opt-in traffic.",
                    parameters={
                        "budget_fraction": self.policy.scale_budget_fraction,
                        "new_budget": round(
                            campaign.budget * (1.0 + self.policy.scale_budget_fraction),
                            6,
                        ),
                    },
                    confidence=0.82,
                    requires_review=False,
                )
            )
            return DecisionPlan(
                campaign_id=campaign.campaign_id,
                policy=self.policy,
                metrics=metrics,
                decisions=decisions,
            )

        can_test = (
            metrics.clicks >= self.policy.create_test_min_clicks
            and metrics.conversions <= self.policy.create_test_max_conversions
            and "low_sample_impressions" not in metrics.anomaly_flags
        )

        if can_test:
            decisions.append(
                Decision(
                    action="create_test",
                    campaign_id=campaign.campaign_id,
                    reason="Traffic exists but conversion volume is too low for a scale decision.",
                    parameters={
                        "variant_count": self.policy.test_variant_count,
                        "focus": "creative_or_offer",
                    },
                    confidence=0.72,
                    requires_review=False,
                )
            )
            return DecisionPlan(
                campaign_id=campaign.campaign_id,
                policy=self.policy,
                metrics=metrics,
                decisions=decisions,
            )

        decisions.append(
            Decision(
                action="request_review",
                campaign_id=campaign.campaign_id,
                reason="Insufficient signal for automation, so the campaign is left for review.",
                confidence=1.0,
                requires_review=True,
            )
        )
        return DecisionPlan(
            campaign_id=campaign.campaign_id,
            policy=self.policy,
            metrics=metrics,
            decisions=decisions,
        )
