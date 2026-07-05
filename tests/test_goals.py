from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.goals import GoalRegistry


class TestGoalRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.store = GoalRegistry(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_register_and_get_goal(self) -> None:
        gid = self.store.register_goal(
            objective="Reduce CPA to under 30",
            owner="media_buying",
            success_criteria={"cpa": 30.0},
        )
        goal = self.store.get_goal(gid)
        self.assertIsNotNone(goal)
        self.assertEqual(goal["objective"], "Reduce CPA to under 30")
        self.assertEqual(goal["owner"], "media_buying")

    def test_list_goals_by_owner(self) -> None:
        self.store.register_goal("Goal A", owner="team_a")
        self.store.register_goal("Goal B", owner="team_b")
        goals_a = self.store.list_goals(owner="team_a")
        self.assertEqual(len(goals_a), 1)
        self.assertEqual(goals_a[0]["objective"], "Goal A")

    def test_list_active_goals(self) -> None:
        gid = self.store.register_goal("Active goal", owner="test")
        self.store.register_goal("Complete goal", owner="test")
        self.store.update_goal_achievement(
            self.store.list_goals(owner="test")[1]["goal_id"], True
        )
        active = self.store.list_goals(only_active=True)
        for g in active:
            self.assertEqual(g["achieved"], 0)

    def test_evaluate_goal_achieved(self) -> None:
        gid = self.store.register_goal(
            objective="Reach 50 conversions",
            success_criteria={"conversions": 50},
        )
        result = self.store.evaluate_goal(
            goal_id=gid,
            cycle_id="cycle_1",
            measured_value=60,
            target_value=50,
            metric_name="conversions",
        )
        self.assertTrue(result["achieved"])
        goal = self.store.get_goal(gid)
        self.assertEqual(goal["achieved"], 1)

    def test_evaluate_goal_not_achieved(self) -> None:
        gid = self.store.register_goal(
            objective="Reach 50 conversions",
            success_criteria={"conversions": 50},
        )
        result = self.store.evaluate_goal(
            goal_id=gid,
            cycle_id="cycle_1",
            measured_value=30,
            target_value=50,
            metric_name="conversions",
        )
        self.assertFalse(result["achieved"])

    def test_get_goal_evaluations(self) -> None:
        gid = self.store.register_goal("Test goal", success_criteria={"ctr": 0.03})
        self.store.evaluate_goal(gid, "cycle_1", 0.025, 0.03, "ctr")
        self.store.evaluate_goal(gid, "cycle_2", 0.035, 0.03, "ctr")
        evals = self.store.get_goal_evaluations(gid)
        self.assertEqual(len(evals), 2)

    def test_get_goal_status_with_latest_evaluation(self) -> None:
        gid = self.store.register_goal("Status test", success_criteria={"cpa": 25.0})
        self.store.evaluate_goal(gid, "cycle_1", 30.0, 25.0, "cpa")
        status = self.store.get_goal_status(gid)
        self.assertIsNotNone(status)
        self.assertIsNotNone(status["latest_evaluation"])
        self.assertEqual(status["latest_evaluation"]["metric_name"], "cpa")

    def test_evaluate_from_outcome_matches_goal(self) -> None:
        gid = self.store.register_goal(
            objective="CPA under 40",
            success_criteria={"cpa": 40.0},
        )
        results = self.store.evaluate_from_outcome(
            cycle_id="cycle_1",
            outcome_data={"cpa": 35.0, "conversions": 10},
        )
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["achieved"])
        goal = self.store.get_goal(gid)
        self.assertEqual(goal["achieved"], 1)

    def test_evaluate_from_outcome_no_match(self) -> None:
        self.store.register_goal(
            objective="CTR over 3%",
            success_criteria={"ctr": 0.03},
        )
        results = self.store.evaluate_from_outcome(
            cycle_id="cycle_1",
            outcome_data={"cpa": 35.0},  # No ctr in outcome
        )
        self.assertEqual(len(results), 1)
        self.assertIn("No matching metric", results[0]["notes"])

    def test_multiple_active_goals_evaluated(self) -> None:
        self.store.register_goal("Goal 1", success_criteria={"cpa": 30.0})
        self.store.register_goal("Goal 2", success_criteria={"conversions": 50})
        results = self.store.evaluate_from_outcome(
            cycle_id="cycle_1",
            outcome_data={"cpa": 25.0, "conversions": 60},
        )
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["achieved"] for r in results))
