from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


class GoalRegistry:
    """Persistent goal tracking and evaluation.

    Goals represent strategic objectives that persist across cycles.
    Each cycle can evaluate one or more goals against actual outcomes.
    """

    def __init__(self, conn: Any):
        self._conn = conn
        self._lock = threading.Lock()
        self._ensure_schema()

    def _execute(self, sql: str, params=None):
        with self._lock:
            if params is not None:
                return self._conn.execute(sql, params)
            return self._conn.execute(sql)

    def _ensure_schema(self) -> None:
        self._execute(
            """CREATE TABLE IF NOT EXISTS goals (
                goal_id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                owner TEXT NOT NULL DEFAULT '',
                success_criteria TEXT NOT NULL DEFAULT '{}',
                achieved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )"""
        )
        self._execute("CREATE INDEX IF NOT EXISTS idx_goals_owner ON goals(owner)")
        self._execute(
            """CREATE TABLE IF NOT EXISTS goal_evaluations (
                evaluation_id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL REFERENCES goals(goal_id),
                cycle_id TEXT NOT NULL,
                achieved INTEGER NOT NULL DEFAULT 0,
                measured_value REAL,
                target_value REAL,
                metric_name TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                evaluated_at TEXT NOT NULL
            )"""
        )
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_eval_goal ON goal_evaluations(goal_id)"
        )
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_eval_cycle ON goal_evaluations(cycle_id)"
        )

    # -- Goal CRUD --

    def register_goal(
        self,
        objective: str,
        owner: str = "",
        success_criteria: dict[str, Any] | None = None,
        goal_id: str | None = None,
    ) -> str:
        """Register a new strategic goal."""
        gid = goal_id or _new_id()
        self._execute(
            """INSERT INTO goals (goal_id, objective, owner, success_criteria, achieved, created_at)
               VALUES (?, ?, ?, ?, 0, ?)""",
            (gid, objective, owner, json.dumps(success_criteria or {}), _utc_now()),
        )
        self._conn.commit()
        return gid

    def get_goal(self, goal_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM goals WHERE goal_id = ?",
            (goal_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def list_goals(
        self,
        owner: str | None = None,
        only_active: bool = False,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if owner is not None:
            clauses.append("owner = ?")
            params.append(owner)
        if only_active:
            clauses.append("achieved = 0")
        where = " AND ".join(clauses) if clauses else "1=1"
        rows = self._execute(
            f"SELECT * FROM goals WHERE {where} ORDER BY created_at DESC",
            params,
        ).fetchall()
        return [dict(r) for r in rows]

    def update_goal_achievement(
        self, goal_id: str, achieved: bool
    ) -> dict[str, Any] | None:
        self._execute(
            "UPDATE goals SET achieved = ? WHERE goal_id = ?",
            (int(achieved), goal_id),
        )
        self._conn.commit()
        return self.get_goal(goal_id)

    # -- Goal Evaluation --

    @staticmethod
    def _is_inverse_metric(metric_name: str) -> bool:
        """Returns True if lower values are better (e.g., CPA, CPC, spend)."""
        return metric_name.lower() in (
            "cpa",
            "cpc",
            "cost_per_click",
            "cost_per_acquisition",
            "spend",
        )

    def evaluate_goal(
        self,
        goal_id: str,
        cycle_id: str,
        measured_value: float | None = None,
        target_value: float | None = None,
        metric_name: str = "",
        notes: str = "",
    ) -> dict[str, Any]:
        """Evaluate a goal against a measured outcome.

        If measured_value meets or exceeds target_value (for normal metrics)
        or measured_value is less than or equal to target_value (for inverse metrics
        like CPA, CPC, spend), the goal is marked achieved.
        """
        eval_id = _new_id()
        achieved = False
        if measured_value is not None and target_value is not None:
            if self._is_inverse_metric(metric_name):
                achieved = measured_value <= target_value
            else:
                achieved = measured_value >= target_value

        self._execute(
            """INSERT INTO goal_evaluations
               (evaluation_id, goal_id, cycle_id, achieved, measured_value,
                target_value, metric_name, notes, evaluated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                eval_id,
                goal_id,
                cycle_id,
                int(achieved),
                measured_value,
                target_value,
                metric_name,
                notes,
                _utc_now(),
            ),
        )
        self._conn.commit()

        # Update goal achievement status
        if achieved and measured_value is not None and target_value is not None:
            self.update_goal_achievement(goal_id, True)

        return {
            "evaluation_id": eval_id,
            "goal_id": goal_id,
            "cycle_id": cycle_id,
            "achieved": achieved,
            "measured_value": measured_value,
            "target_value": target_value,
            "metric_name": metric_name,
            "notes": notes,
        }

    def get_goal_evaluations(
        self,
        goal_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM goal_evaluations WHERE goal_id = ? ORDER BY evaluated_at DESC LIMIT ?",
            (goal_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_goal_status(self, goal_id: str) -> dict[str, Any] | None:
        """Get goal with its latest evaluation."""
        goal = self.get_goal(goal_id)
        if goal is None:
            return None
        evals = self.get_goal_evaluations(goal_id, limit=1)
        goal["latest_evaluation"] = evals[0] if evals else None
        row = self._execute(
            "SELECT COUNT(*) AS cnt FROM goal_evaluations WHERE goal_id = ?",
            (goal_id,),
        ).fetchone()
        goal["evaluation_count"] = row["cnt"] if row else 0
        return goal

    def evaluate_from_outcome(
        self,
        cycle_id: str,
        outcome_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Evaluate all active goals against a cycle's outcome data.

        Scans outcome keys (cpa, conversions, ctr, spend) and matches
        against goal success_criteria.
        """
        results: list[dict[str, Any]] = []
        active_goals = self.list_goals(only_active=True)

        for goal in active_goals:
            criteria = json.loads(goal["success_criteria"])
            matched = False
            for metric_name, target_value in criteria.items():
                if (
                    metric_name in outcome_data
                    and outcome_data[metric_name] is not None
                ):
                    measured = outcome_data[metric_name]
                    result = self.evaluate_goal(
                        goal_id=goal["goal_id"],
                        cycle_id=cycle_id,
                        measured_value=float(measured),
                        target_value=float(target_value),
                        metric_name=metric_name,
                        notes=f"Auto-evaluated from cycle {cycle_id} outcome data",
                    )
                    results.append(result)
                    matched = True
                    break
            if not matched:
                results.append(
                    {
                        "goal_id": goal["goal_id"],
                        "cycle_id": cycle_id,
                        "achieved": False,
                        "notes": "No matching metric in outcome data for auto-evaluation",
                    }
                )

        return results
