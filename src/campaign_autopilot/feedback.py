from __future__ import annotations

import threading

import json
import uuid
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


class OutcomeStore:
    """Captures the outcome of approved executions and feeds them back as learning signals.

    Each cycle records:
    - Expected outcome (from the execution plan)
    - Actual outcome (measured after execution)
    - Delta between expected and actual
    - Lessons extracted from the delta
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
            """CREATE TABLE IF NOT EXISTS feedback_outcomes (
                outcome_id TEXT PRIMARY KEY,
                cycle_id TEXT NOT NULL,
                expected_outcome TEXT NOT NULL DEFAULT '{}',
                actual_outcome TEXT NOT NULL DEFAULT '{}',
                delta TEXT NOT NULL DEFAULT '{}',
                success_flag INTEGER NOT NULL DEFAULT 0,
                lessons TEXT NOT NULL DEFAULT '[]',
                source_step_id TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )"""
        )
        self._execute(
            "CREATE INDEX IF NOT EXISTS idx_feedback_cycle ON feedback_outcomes(cycle_id)"
        )

    def record_expected(
        self,
        cycle_id: str,
        expected_outcome: dict[str, Any],
        source_step_id: str = "",
    ) -> str:
        """Record the expected outcome before execution."""
        outcome_id = _new_id()
        self._execute(
            """INSERT INTO feedback_outcomes
               (outcome_id, cycle_id, expected_outcome, created_at, source_step_id)
               VALUES (?, ?, ?, ?, ?)""",
            (
                outcome_id,
                cycle_id,
                json.dumps(expected_outcome),
                _utc_now(),
                source_step_id,
            ),
        )
        return outcome_id

    def record_actual(
        self,
        outcome_id: str,
        actual_outcome: dict[str, Any],
    ) -> dict[str, Any]:
        """Record actual outcome and compute delta. Returns the outcome record."""
        row = self._execute(
            "SELECT * FROM feedback_outcomes WHERE outcome_id = ?",
            (outcome_id,),
        ).fetchone()
        if row is None:
            return {"error": f"Outcome {outcome_id} not found"}

        expected = json.loads(row["expected_outcome"])
        actual = actual_outcome

        # Compute delta
        delta: dict[str, Any] = {}
        for key in set(list(expected.keys()) + list(actual.keys())):
            if key in expected and key in actual:
                if isinstance(expected[key], (int, float)) and isinstance(
                    actual[key], (int, float)
                ):
                    delta[key] = round(actual[key] - expected[key], 6)
                else:
                    delta[key] = {"expected": expected[key], "actual": actual[key]}
            elif key in expected:
                delta[key] = {"expected": expected[key], "actual": None}
            else:
                delta[key] = {"expected": None, "actual": actual[key]}

        # Determine success
        success_flag = self._evaluate_success(expected, actual, delta)

        # Extract lessons
        lessons = self._extract_lessons(expected, actual, delta, success_flag)

        self._execute(
            """UPDATE feedback_outcomes
               SET actual_outcome = ?, delta = ?, success_flag = ?, lessons = ?
               WHERE outcome_id = ?""",
            (
                json.dumps(actual),
                json.dumps(delta),
                int(success_flag),
                json.dumps(lessons),
                outcome_id,
            ),
        )

        return {
            "outcome_id": outcome_id,
            "cycle_id": row["cycle_id"],
            "expected": expected,
            "actual": actual,
            "delta": delta,
            "success": success_flag,
            "lessons": lessons,
        }

    def _evaluate_success(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
        delta: dict[str, Any],
    ) -> bool:
        """Determine if the outcome was successful based on the delta."""
        # If CPA was expected and actual is lower, that's success
        if (
            "cpa" in delta
            and actual.get("cpa") is not None
            and expected.get("cpa") is not None
        ):
            return actual["cpa"] <= expected["cpa"]
        # If conversions were expected and actual is higher, that's success
        if (
            "conversions" in delta
            and actual.get("conversions") is not None
            and expected.get("conversions") is not None
        ):
            return actual["conversions"] >= expected["conversions"]
        # If CTR was expected and actual is higher, that's success
        if (
            "ctr" in delta
            and actual.get("ctr") is not None
            and expected.get("ctr") is not None
        ):
            return actual["ctr"] >= expected["ctr"]
        # Default: no data to judge
        return True

    @staticmethod
    def _is_inverse_metric(key: str) -> bool:
        """Returns True if lower values are better (e.g., CPA, CPC)."""
        return key.lower() in (
            "cpa",
            "cpc",
            "cost_per_click",
            "cost_per_acquisition",
            "spend",
        )

    def _extract_lessons(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
        delta: dict[str, Any],
        success: bool,
    ) -> list[str]:
        """Extract human-readable lessons from the outcome delta."""
        lessons: list[str] = []
        for key, val in delta.items():
            if isinstance(val, dict) and "expected" in val:
                continue  # Non-numeric deltas aren't easily summarized
            if isinstance(val, (int, float)):
                is_inverse = self._is_inverse_metric(key)
                # For inverse metrics (CPA), negative delta = improvement
                # For normal metrics (conversions), positive delta = improvement
                improved = (val < 0 and is_inverse) or (val > 0 and not is_inverse)
                direction = "improved" if improved else "declined"
                lessons.append(
                    f"Metric '{key}' {direction} by {abs(val)} (expected: {expected.get(key)}, actual: {actual.get(key)})"
                )
        if not lessons:
            lessons.append(
                f"Cycle {'succeeded' if success else 'completed'} with no measurable metric delta."
            )
        return lessons

    def get_feedback(self, outcome_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM feedback_outcomes WHERE outcome_id = ?",
            (outcome_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_cycle_feedback(self, cycle_id: str) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM feedback_outcomes WHERE cycle_id = ? ORDER BY created_at DESC",
            (cycle_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def feed_lessons_to_semantic_memory(
        self,
        outcome_id: str,
        semantic_memory: Any,
        cycle_id: str = "",
    ) -> list[str]:
        """Feed outcome lessons into semantic memory as knowledge claims."""
        result = self.get_feedback(outcome_id)
        if result is None:
            return []

        lessons = json.loads(result["lessons"])
        claim_ids: list[str] = []

        lessons_concept = semantic_memory.find_concept("feedback_lessons", "knowledge")
        if not lessons_concept:
            lessons_concept_id = semantic_memory.register_concept(
                "feedback_lessons",
                "knowledge",
                "Lessons extracted from outcome feedback",
            )
        else:
            lessons_concept_id = lessons_concept["concept_id"]

        for i, lesson in enumerate(lessons):
            lesson_concept_id = semantic_memory.register_concept(
                f"feedback_lesson_{outcome_id}_{i}",
                "knowledge",
                lesson[:200],
            )
            cid = semantic_memory.assert_claim(
                subject=lessons_concept_id,
                predicate="includes",
                object=lesson_concept_id,
                confidence=0.7 if result.get("success_flag") else 0.4,
                evidence_type="DIRECT_OBSERVATION",
                supporting_data={
                    "outcome_id": outcome_id,
                    "cycle_id": cycle_id or result.get("cycle_id", ""),
                    "lesson_text": lesson,
                },
                source_cycle_id=cycle_id or result.get("cycle_id", ""),
                asserted_by="outcome_store",
            )
            claim_ids.append(cid)

        return claim_ids
