"""Economic Intelligence Layer — AG-Kit Evolution Phase 13.

Capital allocation engine: decides where to invest resources,
which channels to grow/abandon, and how to optimize for ROI.

Builds on Phase 11 (ConstraintGraph) and Phase 12 (WorldModel):
  ConstraintGraph → constraints on spending
  WorldModel → predicted outcomes of investments
  EconomicEngine → optimal allocation decisions

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only)
  - No ML — uses WorldModel predictions + simple optimization
  - Thread-safe, integrates with existing architecture
  - Useful even without full historical data
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field, asdict
from enum import Enum


# ── Types ─────────────────────────────────────────────────────


class InvestmentStrategy(Enum):
    AGGRESSIVE = "aggressive"  # High risk, high reward
    BALANCED = "balanced"  # Moderate risk, diversified
    CONSERVATIVE = "conservative"  # Low risk, proven channels
    OPPORTUNISTIC = "opportunistic"  # Follow best short-term ROI


# ── Domain Models ─────────────────────────────────────────────


@dataclass
class ChannelMetrics:
    """Performance metrics for a single channel."""

    channel: str
    revenue: float = 0.0
    cost: float = 0.0
    traffic: float = 0.0
    conversions: float = 0.0
    content_count: int = 0
    active_days: int = 0

    @property
    def roi(self) -> float:
        """Return on investment as a multiplier (e.g., 2.5 = 250% ROI)."""
        if self.cost <= 0:
            return 0.0
        return round((self.revenue - self.cost) / self.cost, 4)

    @property
    def profit(self) -> float:
        return round(self.revenue - self.cost, 2)

    @property
    def revenue_per_content(self) -> float:
        if self.content_count <= 0:
            return 0.0
        return round(self.revenue / self.content_count, 2)

    @property
    def conversion_rate(self) -> float:
        if self.traffic <= 0:
            return 0.0
        return round(self.conversions / self.traffic * 100, 2)

    def to_dict(self) -> dict:
        return {
            "channel": self.channel,
            "revenue": self.revenue,
            "cost": self.cost,
            "profit": self.profit,
            "roi": self.roi,
            "traffic": self.traffic,
            "conversions": self.conversions,
            "conversion_rate": self.conversion_rate,
            "content_count": self.content_count,
            "revenue_per_content": self.revenue_per_content,
            "active_days": self.active_days,
        }


@dataclass
class AllocationDecision:
    """A recommended allocation of resources."""

    channel: str
    recommended_budget: float
    recommended_actions: list[str]  # e.g., ["increase_content", "seo_update"]
    expected_revenue: float
    expected_roi: float
    confidence: str  # high, medium, low
    reasoning: str = ""
    risk_level: str = "medium"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PortfolioSummary:
    """Summary of the current channel portfolio."""

    total_revenue: float = 0.0
    total_cost: float = 0.0
    total_profit: float = 0.0
    overall_roi: float = 0.0
    active_channels: int = 0
    channels: dict[str, ChannelMetrics] = field(default_factory=dict)
    diversification_score: float = (
        0.0  # 0.0 (single channel) to 1.0 (perfectly diversified)
    )

    def update(self) -> None:
        """Recalculate summary from channel data."""
        self.total_revenue = sum(c.revenue for c in self.channels.values())
        self.total_cost = sum(c.cost for c in self.channels.values())
        self.total_profit = self.total_revenue - self.total_cost
        self.overall_roi = round(
            (self.total_profit / self.total_cost * 100) if self.total_cost > 0 else 0, 2
        )
        self.active_channels = len(self.channels)
        # Diversification: 1 - HHI (Herfindahl-Hirschman Index) normalized
        if self.total_revenue > 0:
            shares = [
                (c.revenue / self.total_revenue) ** 2 for c in self.channels.values()
            ]
            hhi = sum(shares)
            self.diversification_score = round(
                1
                - (hhi - 1 / max(len(self.channels), 1))
                / (1 - 1 / max(len(self.channels), 1)),
                4,
            )
        else:
            self.diversification_score = 0.0

    def to_dict(self) -> dict:
        self.update()
        return {
            "total_revenue": self.total_revenue,
            "total_cost": self.total_cost,
            "total_profit": self.total_profit,
            "overall_roi": self.overall_roi,
            "active_channels": self.active_channels,
            "diversification_score": self.diversification_score,
            "channels": {k: v.to_dict() for k, v in self.channels.items()},
        }


@dataclass
class Opportunity:
    """An untapped opportunity the system could pursue."""

    niche: str
    channel: str
    estimated_revenue: float
    estimated_cost: float
    difficulty: str  # easy, medium, hard
    time_to_revenue: str  # days, weeks, months
    confidence: str
    reasoning: str = ""

    @property
    def estimated_roi(self) -> float:
        if self.estimated_cost <= 0:
            return 0.0
        return round(
            (self.estimated_revenue - self.estimated_cost) / self.estimated_cost, 2
        )

    def to_dict(self) -> dict:
        return asdict(self)


# ── Channel ROI Model ─────────────────────────────────────────


class ChannelROIModel:
    """Predicts ROI for channels based on historical + simulated data.

    Can be seeded from WorldModel predictions or from direct observations.
    """

    def __init__(self) -> None:
        self._channels: dict[str, ChannelMetrics] = {}
        self._lock = threading.Lock()

    def register(self, channel: str, metrics: ChannelMetrics | None = None) -> None:
        with self._lock:
            if channel not in self._channels:
                self._channels[channel] = metrics or ChannelMetrics(channel=channel)
            elif metrics:
                self._channels[channel] = metrics

    def record(
        self,
        channel: str,
        revenue: float = 0.0,
        cost: float = 0.0,
        traffic: float = 0.0,
        conversions: float = 0.0,
    ) -> None:
        with self._lock:
            if channel not in self._channels:
                self._channels[channel] = ChannelMetrics(channel=channel)
            c = self._channels[channel]
            c.revenue += revenue
            c.cost += cost
            c.traffic += traffic
            c.conversions += conversions
            c.content_count += (
                1 if any(x > 0 for x in [revenue, traffic, conversions]) else 0
            )
            c.active_days += 1

    def get(self, channel: str) -> ChannelMetrics | None:
        return self._channels.get(channel)

    def all(self) -> list[ChannelMetrics]:
        return list(self._channels.values())

    def roi_ranking(self) -> list[ChannelMetrics]:
        """Return channels sorted by ROI descending."""
        return sorted(self._channels.values(), key=lambda c: -c.roi)

    def profit_ranking(self) -> list[ChannelMetrics]:
        """Return channels sorted by profit descending."""
        return sorted(self._channels.values(), key=lambda c: -c.profit)

    def predict_roi(self, channel: str, additional_investment: float = 0.0) -> dict:
        """Predict ROI for a channel with additional investment.

        Uses diminishing returns: each additional unit of investment
        yields less marginal return.
        """
        c = self._channels.get(channel)
        if c is None or c.cost <= 0:
            return {
                "predicted_roi": 0,
                "confidence": "insufficient",
                "marginal_roi": 0,
                "max_profitable_investment": 0,
            }

        base_roi = c.roi
        # Diminishing returns: marginal_roi = base_roi * 0.5^(investment / current_cost)
        marginal_factor = 0.5 ** (additional_investment / max(c.cost, 1))
        marginal_roi = base_roi * marginal_factor

        # Maximum profitable investment (where marginal_roi drops to risk-free rate ~5%)
        max_invest = 0
        for mult in range(1, 20):
            mf = 0.5 ** (mult)
            mr = base_roi * mf
            if mr < 0.05:  # risk-free rate equivalent
                break
            max_invest = mult

        return {
            "channel": channel,
            "current_roi": base_roi,
            "current_cost": c.cost,
            "current_revenue": c.revenue,
            "additional_investment": additional_investment,
            "predicted_marginal_roi": round(marginal_roi, 4),
            "predicted_total_roi": round(
                (c.revenue - c.cost + marginal_roi * additional_investment)
                / max(c.cost + additional_investment, 1),
                4,
            ),
            "max_profitable_investment_multiple": max_invest,
            "confidence": "high"
            if c.active_days >= 30
            else "medium"
            if c.active_days >= 7
            else "low",
        }

    def portfolio(self) -> PortfolioSummary:
        p = PortfolioSummary()
        p.channels = dict(self._channels)
        p.update()
        return p


# ── Capital Allocation Engine ─────────────────────────────────


class CapitalAllocationEngine:
    """Decides where to invest resources (time, budget, API calls).

    Uses ChannelROIModel for historical data and (optionally) WorldModel
    predictions for future scenarios. Strategy determines risk appetite.
    """

    def __init__(
        self,
        roi_model: ChannelROIModel | None = None,
        strategy: InvestmentStrategy = InvestmentStrategy.BALANCED,
    ) -> None:
        self.roi_model = roi_model or ChannelROIModel()
        self.strategy = strategy
        self._lock = threading.Lock()

    def set_strategy(self, strategy: InvestmentStrategy) -> None:
        self.strategy = strategy

    def allocate(
        self,
        total_budget: float,
        world_model_predictions: dict[str, dict] | None = None,
    ) -> list[AllocationDecision]:
        """Allocate a budget across channels. Returns prioritized decisions.

        Args:
            total_budget: Total resources to allocate (arbitrary units)
            world_model_predictions: Optional predicted outcomes per channel
                Format: {"channel": {"expected_revenue": float, "confidence": str}}
        """
        channels = self.roi_model.all()
        if not channels:
            return []

        decisions = []
        # Strategy-based adjustments
        risk_multipliers = {
            InvestmentStrategy.AGGRESSIVE: {"proven_weight": 0.6, "new_weight": 0.4},
            InvestmentStrategy.BALANCED: {"proven_weight": 0.8, "new_weight": 0.2},
            InvestmentStrategy.CONSERVATIVE: {
                "proven_weight": 0.95,
                "new_weight": 0.05,
            },
            InvestmentStrategy.OPPORTUNISTIC: {"proven_weight": 0.5, "new_weight": 0.5},
        }
        strat = risk_multipliers.get(
            self.strategy, risk_multipliers[InvestmentStrategy.BALANCED]
        )

        # Sort by ROI
        ranked = self.roi_model.roi_ranking()

        # Calculate allocation weights
        total_weight = 0.0
        weights = {}
        for c in ranked:
            w = max(c.roi, 0.1)  # base weight from ROI
            # Apply strategy weights
            if c.revenue == 0:  # new channel
                w *= strat["new_weight"]
            else:
                w *= strat["proven_weight"]
            # Apply prediction if available
            if world_model_predictions and c.channel in world_model_predictions:
                pred = world_model_predictions[c.channel]
                conf_mult = {
                    "high": 1.2,
                    "medium": 1.0,
                    "low": 0.8,
                    "insufficient": 0.5,
                }
                w *= conf_mult.get(pred.get("confidence", "medium"), 1.0)
            weights[c.channel] = w
            total_weight += w

        # Generate allocation decisions
        remaining = total_budget
        for i, c in enumerate(ranked):
            if remaining <= 0:
                break
            # Last channel gets remainder
            if i == len(ranked) - 1:
                alloc = remaining
            else:
                alloc = round(
                    total_budget * weights[c.channel] / max(total_weight, 1), 2
                )
                alloc = min(alloc, remaining)

            remaining -= alloc

            # Determine recommended actions
            actions = []
            if c.roi > 2.0:
                actions.append("increase_content_production")
                actions.append("scale_channel")
            elif c.roi > 1.0:
                actions.append("maintain_effort")
                actions.append("seo_optimization")
            elif c.roi > 0:
                actions.append("optimize_cost")
                actions.append("pause_if_no_improvement")
            else:
                actions.append("evaluate_abandon")

            # Expected revenue from this allocation
            expected_rev = (
                c.revenue * (1 + alloc / max(c.cost, 1) * c.roi * 0.3)
                if c.cost > 0
                else 0
            )

            decisions.append(
                AllocationDecision(
                    channel=c.channel,
                    recommended_budget=alloc,
                    recommended_actions=actions,
                    expected_revenue=round(expected_rev, 2),
                    expected_roi=round(expected_rev / max(alloc, 1), 2),
                    confidence="high"
                    if c.active_days >= 30
                    else "medium"
                    if c.active_days >= 7
                    else "low",
                    reasoning=self._reason(c, alloc, actions),
                    risk_level="low"
                    if c.roi > 1.5
                    else "medium"
                    if c.roi > 0.5
                    else "high",
                )
            )

        return sorted(decisions, key=lambda d: -d.expected_roi)

    def _reason(
        self, channel: ChannelMetrics, budget: float, actions: list[str]
    ) -> str:
        parts = [f"Canal {channel.channel}:"]
        if channel.roi > 2:
            parts.append(f"ROI excepcional de {channel.roi:.1f}x")
        elif channel.roi > 0:
            parts.append(f"ROI de {channel.roi:.1f}x")
        else:
            parts.append("sem retorno ainda")
        if actions:
            parts.append(f"ações: {', '.join(actions)}")
        parts.append(f"budget: ${budget:.0f}")
        return " | ".join(parts)

    def abandon_suggestions(self) -> list[ChannelMetrics]:
        """Channels that should be considered for abandonment."""
        return [
            c
            for c in self.roi_model.all()
            if c.roi <= 0 and c.cost > 0 and c.active_days >= 14
        ]


# ── Opportunity Cost Engine ───────────────────────────────────


class OpportunityCostEngine:
    """Calculates the cost of NOT pursuing an opportunity.

    Core insight: every opportunity not pursued has a real cost
    (the revenue it would have generated).
    """

    def __init__(self, roi_model: ChannelROIModel) -> None:
        self.roi_model = roi_model

    def evaluate(self, opportunity: Opportunity) -> dict:
        """Evaluate the cost of NOT pursuing this opportunity over time."""
        daily_revenue = opportunity.estimated_revenue / 365
        reasoning_parts = []

        # Cost of delaying 30, 60, 90 days
        costs = {}
        for days in [30, 60, 90]:
            loss = daily_revenue * days
            costs[f"{days}_days"] = round(loss, 2)

        # Compare with current worst-performing channel
        worst = self.roi_model.profit_ranking()
        if worst:
            worst_channel = worst[-1]
            reasoning_parts.append(
                f"Custo de oportunidade em 30 dias: ${costs['30_days']:.0f} "
                f"vs canal mais fraco (${worst_channel.channel}) "
                f"que custa ${worst_channel.cost:.0f} e gera ${worst_channel.revenue:.0f}"
            )
        else:
            reasoning_parts.append(
                f"Custo de oportunidade em 30 dias: ${costs['30_days']:.0f}"
            )

        return {
            "opportunity": opportunity.to_dict(),
            "opportunity_cost_30d": costs["30_days"],
            "opportunity_cost_60d": costs["60_days"],
            "opportunity_cost_90d": costs["90_days"],
            "estimated_monthly_cost": round(daily_revenue * 30.5, 2),
            "recommendation": "pursue" if opportunity.estimated_roi > 1.0 else "skip",
            "reasoning": " | ".join(reasoning_parts),
        }

    def prioritize(self, opportunities: list[Opportunity]) -> list[dict]:
        """Rank opportunities by cost of NOT pursuing them."""
        evaluated = [self.evaluate(opp) for opp in opportunities]
        return sorted(evaluated, key=lambda e: -e["opportunity_cost_30d"])


# ── Economic Engine (Orchestrator) ────────────────────────────


class EconomicEngine:
    """Main economic intelligence engine.

    Coordinates ChannelROIModel, CapitalAllocationEngine, and
    OpportunityCostEngine. Builds on WorldModel predictions.

    Usage:
        ee = EconomicEngine()
        ee.record_channel("blog", revenue=500, cost=100, traffic=10000)
        decisions = ee.allocate(total_budget=1000)
        opp_cost = ee.evaluate_opportunity(niche="ia", channel="blog", ...)
    """

    def __init__(self) -> None:
        self.roi_model = ChannelROIModel()
        self.allocation = CapitalAllocationEngine(self.roi_model)
        self.opportunity = OpportunityCostEngine(self.roi_model)
        self._lock = threading.Lock()

    def record_channel(
        self,
        channel: str,
        revenue: float = 0,
        cost: float = 0,
        traffic: float = 0,
        conversions: float = 0,
    ) -> None:
        self.roi_model.record(channel, revenue, cost, traffic, conversions)

    def set_strategy(self, strategy: InvestmentStrategy) -> None:
        self.allocation.strategy = strategy

    def allocate(
        self, total_budget: float, predictions: dict[str, dict] | None = None
    ) -> list[AllocationDecision]:
        return self.allocation.allocate(total_budget, predictions)

    def portfolio(self) -> PortfolioSummary:
        return self.roi_model.portfolio()

    def evaluate_opportunity(
        self,
        niche: str,
        channel: str,
        estimated_revenue: float,
        estimated_cost: float,
        difficulty: str = "medium",
    ) -> dict:
        opp = Opportunity(
            niche=niche,
            channel=channel,
            estimated_revenue=estimated_revenue,
            estimated_cost=estimated_cost,
            difficulty=difficulty,
            time_to_revenue="weeks",
            confidence="medium",
        )
        return self.opportunity.evaluate(opp)

    def abandon_suggestions(self) -> list[ChannelMetrics]:
        return self.allocation.abandon_suggestions()

    def snapshot(self) -> dict:
        return {
            "portfolio": self.roi_model.portfolio().to_dict(),
            "strategy": self.allocation.strategy.value,
            "abandon_candidates": [c.to_dict() for c in self.abandon_suggestions()],
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Run a demonstration of the Economic Intelligence Layer."""
    ee = EconomicEngine()

    # Seed historical data
    channels = {
        "blog": {"revenue": 3000, "cost": 500, "traffic": 50000, "conversions": 150},
        "youtube": {
            "revenue": 5000,
            "cost": 1200,
            "traffic": 80000,
            "conversions": 200,
        },
        "pinterest": {
            "revenue": 1500,
            "cost": 300,
            "traffic": 25000,
            "conversions": 80,
        },
        "email": {"revenue": 2000, "cost": 200, "traffic": 10000, "conversions": 300},
        "instagram": {"revenue": 500, "cost": 400, "traffic": 15000, "conversions": 40},
        "tiktok": {"revenue": 200, "cost": 300, "traffic": 20000, "conversions": 25},
    }
    for ch, data in channels.items():
        ee.record_channel(ch, **data)

    print("=== Economic Intelligence Layer — Demo ===")
    print()

    # Portfolio summary
    p = ee.portfolio()
    print(
        f"Portfolio: ${p.total_revenue:.0f} revenue, ${p.total_cost:.0f} cost, "
        f"${p.total_profit:.0f} profit, ROI {p.overall_roi}%"
    )
    print(
        f"Diversification: {p.diversification_score:.2f} (0=concentrated, 1=diversified)"
    )
    print(f"Active channels: {p.active_channels}")
    print()

    # ROI ranking
    print("ROI Ranking:")
    for c in ee.roi_model.roi_ranking():
        print(
            f"  {c.channel:12s} ROI {c.roi:6.1f}x  profit ${c.profit:6.0f}  "
            f"rev/content ${c.revenue_per_content:5.0f}  conv {c.conversion_rate:5.1f}%"
        )

    print()
    decisions = ee.allocate(total_budget=5000)
    print("Allocation Decisions (budget=$5000):")
    for d in decisions:
        print(
            f"  {d.channel:12s} ${d.recommended_budget:6.0f} → "
            f"${d.expected_revenue:6.0f} expected (ROI {d.expected_roi:.1f}x) "
            f"[{d.confidence}, risk={d.risk_level}]"
        )
        print(f"    Actions: {', '.join(d.recommended_actions)}")

    print()
    abandons = ee.abandon_suggestions()
    print(f"Channels to evaluate for abandonment: {len(abandons)}")
    for a in abandons:
        print(
            f"  ✗ {a.channel}: cost ${a.cost}, revenue ${a.revenue}, "
            f"ROI {a.roi}x ({a.active_days} days)"
        )

    print()
    result = ee.evaluate_opportunity(
        niche="inteligencia_artificial",
        channel="blog",
        estimated_revenue=8000,
        estimated_cost=1000,
        difficulty="medium",
    )
    print("Opportunity cost (new niche 'ia' on blog):")
    print(f"  Cost of 30d delay: ${result['opportunity_cost_30d']}")
    print(f"  Cost of 90d delay: ${result['opportunity_cost_90d']}")
    print(f"  Recommendation: {result['recommendation']}")


if __name__ == "__main__":
    demo()
