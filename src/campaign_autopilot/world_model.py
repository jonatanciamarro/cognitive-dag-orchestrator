"""World Model Engine — AG-Kit Evolution Phase 12.

Predictive model of the environment. Given current state + action,
predicts next state. Runs scenario simulations and counterfactuals.

Builds on Phase 11 (ConstraintGraph) and existing data stores
(MemoryStore, TraceStore, OutcomeStore) to model state transitions.

Design Principles (Ponytail):
  - Zero new dependencies (stdlib only — math, statistics, itertools)
  - No ML libraries (no numpy, no scipy)
  - Statistical prediction via moving averages, trends, confidence intervals
  - Thread-safe, integrates with existing architecture
  - Useful even without historical data (uses reasonable defaults)
"""

from __future__ import annotations

import json
import statistics
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Types ─────────────────────────────────────────────────────


class TrendDirection(Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    UNKNOWN = "unknown"


class ModelConfidence(Enum):
    HIGH = "high"  # lots of data, low variance
    MEDIUM = "medium"  # some data, moderate variance
    LOW = "low"  # little data or high variance
    INSUFFICIENT = "insufficient"  # not enough data to model


# ── Domain Models ─────────────────────────────────────────────


@dataclass
class MetricHistory:
    """Historical data points for a single metric."""

    metric_name: str
    data_points: list[dict] = field(default_factory=list)
    # Each data point: {"timestamp": float, "value": float, "source": str}

    def add(
        self, value: float, timestamp: float | None = None, source: str = ""
    ) -> None:
        self.data_points.append(
            {
                "timestamp": timestamp or time.time(),
                "value": value,
                "source": source,
            }
        )

    def sorted(self) -> list[dict]:
        return sorted(self.data_points, key=lambda d: d["timestamp"])

    def recent(self, n: int = 10) -> list[dict]:
        return self.sorted()[-n:]

    def values(self, n: int | None = None) -> list[float]:
        vals = [d["value"] for d in self.sorted()]
        return vals[-n:] if n else vals

    def count(self) -> int:
        return len(self.data_points)

    def mean(self) -> float | None:
        vals = self.values()
        return sum(vals) / len(vals) if vals else None

    def stdev(self) -> float | None:
        vals = self.values()
        if len(vals) < 2:
            return None
        return statistics.stdev(vals)

    def trend(self, n: int | None = None) -> TrendDirection:
        """Estimate trend direction from recent data points."""
        vals = self.values(n)
        if len(vals) < 3:
            return TrendDirection.UNKNOWN
        # Simple linear regression slope via least squares
        xs = list(range(len(vals)))
        n_pts = len(xs)
        sx = sum(xs)
        sy = sum(vals)
        sxx = sum(x * x for x in xs)
        sxy = sum(x * y for x, y in zip(xs, vals))
        try:
            slope = (n_pts * sxy - sx * sy) / (n_pts * sxx - sx * sx)
        except ZeroDivisionError:
            return TrendDirection.UNKNOWN
        # Normalize slope by mean value
        mean_v = sum(vals) / n_pts
        if mean_v == 0:
            return TrendDirection.UNKNOWN
        rel_slope = slope / mean_v
        if rel_slope > 0.05:
            return TrendDirection.UP
        elif rel_slope < -0.05:
            return TrendDirection.DOWN
        return TrendDirection.STABLE

    def predict_next(self, steps: int = 1) -> dict:
        """Predict the next value based on trend."""
        vals = self.values()
        if len(vals) < 3:
            return {
                "predicted": None,
                "confidence": ModelConfidence.INSUFFICIENT,
                "lower_bound": None,
                "upper_bound": None,
            }
        # Linear regression
        xs = list(range(len(vals)))
        n = len(xs)
        sx = sum(xs)
        sy = sum(vals)
        sxx = sum(x * x for x in xs)
        sxy = sum(x * y for x, y in zip(xs, vals))
        try:
            slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
            intercept = (sy - slope * sx) / n
        except ZeroDivisionError:
            return {
                "predicted": None,
                "confidence": ModelConfidence.INSUFFICIENT,
                "lower_bound": None,
                "upper_bound": None,
            }
        next_x = len(vals) + steps - 1
        predicted = slope * next_x + intercept
        # Confidence based on R²-like measure
        residuals = [v - (slope * x + intercept) for x, v in zip(xs, vals)]
        std_err = (
            statistics.stdev(residuals) if len(residuals) > 1 else abs(predicted) * 0.5
        )
        n_pts = len(vals)
        conf = (
            ModelConfidence.HIGH
            if n_pts >= 20 and std_err / max(abs(predicted), 0.01) < 0.3
            else ModelConfidence.MEDIUM
            if n_pts >= 10
            else ModelConfidence.LOW
            if n_pts >= 5
            else ModelConfidence.INSUFFICIENT
        )
        return {
            "predicted": round(predicted, 4),
            "confidence": conf.value,
            "lower_bound": round(predicted - 1.96 * std_err, 4),
            "upper_bound": round(predicted + 1.96 * std_err, 4),
            "trend": self.trend().value,
            "data_points": n_pts,
        }

    def to_dict(self) -> dict:
        return {
            "metric": self.metric_name,
            "data_points": len(self.data_points),
            "mean": self.mean(),
            "stdev": self.stdev(),
            "trend": self.trend().value,
        }


@dataclass
class WorldState:
    """Snapshot of the current system state at a point in time."""

    timestamp: float
    metrics: dict[str, float] = field(default_factory=dict)
    constraints: dict[str, bool | float] = field(default_factory=dict)
    active_channels: list[str] = field(default_factory=list)
    budget_remaining: dict[str, float] = field(default_factory=dict)
    revenue_by_channel: dict[str, float] = field(default_factory=dict)
    agent_results: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "metrics": dict(self.metrics),
            "constraints": dict(self.constraints),
            "active_channels": list(self.active_channels),
            "budget": dict(self.budget_remaining),
            "revenue": dict(self.revenue_by_channel),
        }


# ── Action Model ──────────────────────────────────────────────


@dataclass
class Action:
    """An action the system can take, which transitions state."""

    action_type: (
        str  # "publish_content", "increase_budget", "pause_channel", "seo_update"
    )
    target: str  # which channel, agent, or campaign
    params: dict = field(default_factory=dict)

    def signature(self) -> str:
        """Unique signature for this action (for counterfactual matching)."""
        return f"{self.action_type}:{self.target}"


# ── State Predictor ───────────────────────────────────────────


class StatePredictor:
    """Predicts next state given current state + action.

    Uses historical trends from MetricHistory objects.
    Falls back to reasonable defaults when no history exists.
    """

    def __init__(self) -> None:
        self._history: dict[str, MetricHistory] = {}
        self._lock = threading.Lock()

    def record(
        self,
        metric: str,
        value: float,
        timestamp: float | None = None,
        source: str = "",
    ) -> None:
        """Record a historical data point."""
        with self._lock:
            if metric not in self._history:
                self._history[metric] = MetricHistory(metric)
            self._history[metric].add(value, timestamp, source)

    def get_history(self, metric: str) -> MetricHistory | None:
        return self._history.get(metric)

    def all_metrics(self) -> list[str]:
        return list(self._history.keys())

    def predict(self, metric: str, steps: int = 1) -> dict:
        """Predict future value of a metric."""
        h = self._history.get(metric)
        if h is None:
            return {"predicted": None, "confidence": ModelConfidence.INSUFFICIENT.value}
        return h.predict_next(steps)

    def predict_many(self, metrics: list[str], steps: int = 1) -> dict[str, dict]:
        """Predict multiple metrics at once."""
        return {m: self.predict(m, steps) for m in metrics}

    def predict_state(
        self, current: WorldState, action: Action | None = None, steps: int = 1
    ) -> WorldState:
        """Predict next world state from current state and optional action.

        Uses statistical models for each metric independently.
        Action modifies the prediction (e.g., publish_content → traffic +20%).
        """
        next_state = WorldState(timestamp=time.time() + (steps * 3600))
        next_state.active_channels = list(current.active_channels)
        next_state.budget_remaining = dict(current.budget_remaining)

        # Predict each metric
        for metric, current_value in current.metrics.items():
            pred = self.predict(metric, steps)
            if pred["predicted"] is not None:
                # Blend prediction with current value (weighted by confidence)
                conf_weights = {
                    "high": 0.8,
                    "medium": 0.6,
                    "low": 0.3,
                    "insufficient": 0.0,
                }
                w = conf_weights.get(pred["confidence"], 0.5)
                next_state.metrics[metric] = round(
                    current_value * (1 - w) + pred["predicted"] * w, 4
                )
            else:
                # No data: simple decay or growth based on action
                next_state.metrics[metric] = current_value

        # Apply action effects
        if action:
            self._apply_action_effect(next_state, action)

        # Propagate constraints
        for cid, val in current.constraints.items():
            # If metric exists, check threshold
            metric_name = cid.replace("_min", "").replace("_max", "")
            if metric_name in next_state.metrics:
                next_state.constraints[cid] = (
                    False  # will be re-evaluated by constraint layer
                )
            else:
                next_state.constraints[cid] = val

        return next_state

    def _apply_action_effect(self, state: WorldState, action: Action) -> None:
        """Apply estimated effect of an action on the predicted state."""
        effects = {
            "publish_content": {"traffic": 1.15, "content_count": 1.0},
            "seo_update": {"traffic": 1.08, "seo_score": 0.05},
            "increase_budget": {"ad_spend": 1.3, "paid_traffic": 1.25},
            "decrease_budget": {"ad_spend": 0.7, "paid_traffic": 0.75},
            "pause_channel": {"traffic": 0.85, "cost": 0.9},
            "activate_channel": {"traffic": 1.10, "cost": 1.05},
            "email_campaign": {"email_traffic": 1.5, "conversions": 1.2},
            "social_posting": {"social_traffic": 1.3, "engagement": 1.2},
        }
        eff = effects.get(action.action_type, {})
        for metric, multiplier in eff.items():
            if metric in state.metrics:
                state.metrics[metric] = round(state.metrics[metric] * multiplier, 4)

    def report(self) -> dict:
        """Report on all tracked metrics."""
        metrics = {}
        for name, hist in self._history.items():
            metrics[name] = hist.to_dict()
            metrics[name]["predict_next"] = hist.predict_next()
        return {
            "tracked_metrics": len(metrics),
            "total_data_points": sum(h.count() for h in self._history.values()),
            "metrics": metrics,
        }


# ── Scenario Simulator ────────────────────────────────────────


class ScenarioSimulator:
    """Runs "what-if" simulations: sequences of actions → predicted outcomes.

    Example:
        sim = ScenarioSimulator(predictor)
        result = sim.run([
            Action("publish_content", "blog", {"count": 5}),
            Action("seo_update", "blog", {}),
            Action("social_posting", "pinterest", {"pins": 10}),
        ], current_state)
        # Returns: [state1, state2, state3] — predicted trajectory
    """

    def __init__(self, predictor: StatePredictor) -> None:
        self.predictor = predictor

    def run(
        self,
        actions: list[Action],
        initial_state: WorldState,
        steps_per_action: int = 3,
    ) -> list[WorldState]:
        """Simulate a sequence of actions. Returns trajectory of states."""
        trajectory = []
        current = initial_state
        trajectory.append(current)
        for action in actions:
            for _step in range(steps_per_action):
                current = self.predictor.predict_state(current, action, steps=1)
                trajectory.append(current)
        return trajectory

    def compare(
        self, scenarios: dict[str, list[Action]], initial_state: WorldState
    ) -> dict[str, list[WorldState]]:
        """Compare multiple scenarios side by side.

        Example:
            scenarios = {
                "otimista": [Action("publish_content", "blog")],
                "conservador": [Action("seo_update", "blog")],
                "minimo": [],
            }
            results = sim.compare(scenarios, current_state)
        """
        return {
            name: self.run(actions, initial_state)
            for name, actions in scenarios.items()
        }

    def best_action(
        self,
        state: WorldState,
        action_candidates: list[Action],
        objective_metric: str = "revenue",
        horizon_steps: int = 5,
    ) -> Action | None:
        """Find the single best action to maximize an objective metric."""
        if not action_candidates:
            return None
        results = []
        for action in action_candidates:
            trajectory = self.run([action], state, steps_per_action=horizon_steps)
            final_metric = trajectory[-1].metrics.get(objective_metric, 0)
            results.append((final_metric, action))
        results.sort(key=lambda x: -x[0])
        return results[0][1] if results else None


# ── Counterfactual Engine ─────────────────────────────────────


class CounterfactualEngine:
    """Re-plays history with modified actions.

    Answers: "What would have happened if we had chosen differently?"
    """

    def __init__(self, predictor: StatePredictor) -> None:
        self.predictor = predictor
        self._history_log: list[dict] = []

    def log_state(self, state: WorldState, action_taken: Action | None = None) -> None:
        """Record a historical state transition."""
        self._history_log.append(
            {
                "timestamp": state.timestamp,
                "state": state,
                "action": action_taken,
            }
        )

    def counterfactual(self, from_step: int, new_action: Action) -> list[WorldState]:
        """Replay from a specific step with a different action.

        Args:
            from_step: Index in history log to branch from
            new_action: The action to take instead

        Returns:
            Predicted trajectory from the branch point
        """
        if from_step >= len(self._history_log):
            return []
        branch_state = self._history_log[from_step]["state"]
        # Run simulation from branch point
        sim = ScenarioSimulator(self.predictor)
        remaining = len(self._history_log) - from_step
        return sim.run([new_action], branch_state, steps_per_action=remaining)

    def what_if(self, action_to_replace: str, new_action: Action) -> list[dict]:
        """Find all historical occurrences of an action and replace them.

        Args:
            action_to_replace: Action type signature to find
            new_action: Replacement action

        Returns:
            List of counterfactual outcomes
        """
        results = []
        for i, entry in enumerate(self._history_log):
            act = entry.get("action")
            if act and act.signature() == action_to_replace:
                cf = self.counterfactual(i, new_action)
                if cf:
                    results.append(
                        {
                            "replaced_at": entry["timestamp"],
                            "original_action": act.signature(),
                            "new_action": new_action.signature(),
                            "predicted_trajectory": [s.snapshot() for s in cf],
                        }
                    )
        return results


# ── World Model (Orchestrator) ────────────────────────────────


class WorldModel:
    """Main world model. Coordinates prediction, simulation, and counterfactuals.

    Usage:
        wm = WorldModel()
        wm.learn_from_history(memory_store, trace_store, outcome_store)
        sim = wm.simulate([
            Action("publish_content", "blog", {"count": 5}),
        ], wm.current_state())
        best = wm.best_action(candidates)
    """

    def __init__(self) -> None:
        self.predictor = StatePredictor()
        self.simulator = ScenarioSimulator(self.predictor)
        self.counterfactual = CounterfactualEngine(self.predictor)
        self._lock = threading.Lock()
        self._current_state: WorldState | None = None

    def learn(self, metric: str, value: float, source: str = "") -> None:
        """Record a single observation."""
        self.predictor.record(metric, value, source=source)

    def learn_batch(self, data: dict[str, list[float]]) -> None:
        """Record batch observations (e.g., from memory store)."""
        for metric, values in data.items():
            for v in values:
                self.predictor.record(metric, v)

    def set_current_state(self, state: WorldState) -> None:
        self._current_state = state

    def current_state(self) -> WorldState | None:
        return self._current_state

    def predict(self, metric: str, steps: int = 1) -> dict:
        return self.predictor.predict(metric, steps)

    def predict_many(self, metrics: list[str], steps: int = 1) -> dict[str, dict]:
        return self.predictor.predict_many(metrics, steps)

    def simulate(
        self,
        actions: list[Action],
        initial_state: WorldState | None = None,
        steps_per_action: int = 3,
    ) -> list[WorldState]:
        """Run a scenario simulation."""
        state = initial_state or self._current_state
        if state is None:
            raise ValueError("No initial state provided or stored")
        return self.simulator.run(actions, state, steps_per_action)

    def compare_scenarios(
        self, scenarios: dict[str, list[Action]]
    ) -> dict[str, list[WorldState]]:
        """Compare multiple scenarios."""
        state = self._current_state
        if state is None:
            raise ValueError("No current state set")
        return self.simulator.compare(scenarios, state)

    def best_action(
        self, candidates: list[Action], objective: str = "revenue", horizon: int = 5
    ) -> Action | None:
        """Find best action to maximize objective."""
        state = self._current_state
        if state is None:
            return None
        return self.simulator.best_action(state, candidates, objective, horizon)

    def report(self) -> dict:
        return self.predictor.report()

    def snapshot(self) -> dict:
        state = self._current_state
        return {
            "current_state": state.snapshot() if state else None,
            "model": self.report(),
        }


# ── Quick Diagnostic ──────────────────────────────────────────


def demo() -> None:
    """Run a demonstration of the World Model Engine."""
    wm = WorldModel()

    # Feed historical data (simulated)
    import random

    random.seed(42)
    base_traffic = 1000
    for day in range(60):
        wm.learn("traffic", base_traffic + random.gauss(0, 100), source="demo")
        wm.learn("revenue", base_traffic * 0.05 + random.gauss(0, 20), source="demo")
        wm.learn("conversions", base_traffic * 0.03 + random.gauss(0, 5), source="demo")
        base_traffic += random.gauss(10, 20)  # slow growth trend

    # Current state
    state = WorldState(
        timestamp=time.time(),
        metrics={"traffic": 1500, "revenue": 80, "conversions": 45, "cost": 30},
        active_channels=["blog", "youtube", "pinterest"],
        budget_remaining={"total": 500, "ads": 100},
    )
    wm.set_current_state(state)

    print("=== World Model Engine — Demo ===")
    print()
    print("Predicted next values:")
    for metric in ["traffic", "revenue", "conversions"]:
        pred = wm.predict(metric)
        print(
            f"  {metric}: {pred['predicted']:.1f} "
            f"(conf: {pred['confidence']}, trend: {pred['trend']})"
        )

    print()
    print("Scenario comparison:")
    scenarios = {
        "do_nothing": [],
        "publish_blog": [Action("publish_content", "blog")],
        "publish_blog+seo": [
            Action("publish_content", "blog"),
            Action("seo_update", "blog"),
        ],
        "email_campaign": [Action("email_campaign", "all")],
    }
    results = wm.compare_scenarios(scenarios)
    for name, trajectory in results.items():
        final = trajectory[-1] if trajectory else state
        print(
            f"  {name}: traffic={final.metrics.get('traffic', 0):.0f}, "
            f"revenue={final.metrics.get('revenue', 0):.1f}"
        )

    print()
    best = wm.best_action(
        [
            Action("publish_content", "blog"),
            Action("seo_update", "blog"),
            Action("email_campaign", "all"),
            Action("social_posting", "pinterest"),
        ],
        objective="revenue",
        horizon=10,
    )
    print(f"Best action for revenue: {best.signature() if best else 'N/A'}")

    print()
    print("Model stats:", json.dumps(wm.report(), indent=2))


if __name__ == "__main__":
    demo()
