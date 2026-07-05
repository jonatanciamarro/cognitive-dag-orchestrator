from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.orchestrator import CampaignOrchestrator
from campaign_autopilot.memory import MemoryStore
from campaign_autopilot.goals import GoalRegistry


ROOT = Path(__file__).resolve().parents[1]
ORGANIC_WORKFLOW = ROOT / "workflows" / "organic_cycle.json"
ORGANIC_CONTEXT = ROOT / "examples" / "organic_context.json"


class TestMetaCognitiveLayer(unittest.TestCase):
    """Verify the Phase 2 meta-cognitive layer: observers, epistemic claims,
    goal registry, and ontology drift detection."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._db_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._db_path.unlink(missing_ok=True)

    def test_observers_registered(self) -> None:
        """All agents should be registered as semantic observers."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=ORGANIC_WORKFLOW,
                memory_store=store,
            )
            orchestrator.run(CampaignContext.from_mapping(payload))

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT * FROM semantic_observers ORDER BY name"
            ).fetchall()
            observer_ids = {r["observer_id"] for r in rows}
            for expected in (
                "analytics",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
                "ontology_steward",
                "orchestrator",
            ):
                self.assertIn(
                    expected, observer_ids, f"Observer {expected} not registered"
                )
        finally:
            conn.close()

    def test_claims_have_epistemic_status(self) -> None:
        """All semantic claims should have a valid epistemic_status."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=ORGANIC_WORKFLOW,
                memory_store=store,
            )
            orchestrator.run(CampaignContext.from_mapping(payload))

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT DISTINCT epistemic_status FROM semantic_claims"
            ).fetchall()
            statuses = {r["epistemic_status"] for r in rows}
            self.assertTrue(
                statuses.issubset({"VERIFIED", "INFERRED", "ASSUMED", "HYPOTHETICAL"}),
                f"Invalid epistemic statuses found: {statuses}",
            )
        finally:
            conn.close()

    def test_claims_have_observer_ids(self) -> None:
        """Claims should be traceable to observer agents."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=ORGANIC_WORKFLOW,
                memory_store=store,
            )
            orchestrator.run(CampaignContext.from_mapping(payload))

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT DISTINCT observer_id FROM semantic_claims WHERE observer_id IS NOT NULL"
            ).fetchall()
            observer_ids = {r["observer_id"] for r in rows}
            self.assertGreaterEqual(len(observer_ids), 1)
            self.assertIn("analytics", observer_ids)
        finally:
            conn.close()

    def test_goal_registry_initialized(self) -> None:
        """GoalRegistry should be createable and goals persistable."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            gr = GoalRegistry(conn)
            gid = gr.register_goal(
                objective="Test meta-cognitive goal",
                owner="test",
                success_criteria={"cpa": 25.0},
            )
            goal = gr.get_goal(gid)
            self.assertIsNotNone(goal)
            self.assertEqual(goal["objective"], "Test meta-cognitive goal")
            self.assertEqual(goal["achieved"], 0)
        finally:
            conn.close()

    def test_goal_evaluation_from_orchestrator(self) -> None:
        """Register a goal before running a workflow; verify it gets evaluated."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            # Pre-register a goal via the GoalRegistry
            gr = GoalRegistry(store._conn)
            gid = gr.register_goal(
                objective="Produce a ready plan",
                owner="meta_test",
                success_criteria={"status_achieved": 1.0},
            )
            orchestrator = CampaignOrchestrator(
                workflow_path=ORGANIC_WORKFLOW,
                memory_store=store,
            )
            orchestrator.run(CampaignContext.from_mapping(payload))

        # Goal should have been evaluated during the cycle
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            gr2 = GoalRegistry(conn)
            evals = gr2.get_goal_evaluations(gid)
            self.assertGreaterEqual(len(evals), 1)
            status = gr2.get_goal_status(gid)
            self.assertIsNotNone(status)
        finally:
            conn.close()

    def test_ontology_version_created(self) -> None:
        """Each cycle should produce an ontology snapshot."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=ORGANIC_WORKFLOW,
                memory_store=store,
            )
            orchestrator.run(CampaignContext.from_mapping(payload))

        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT COUNT(*) AS cnt FROM semantic_ontology_versions"
            ).fetchall()
            self.assertGreaterEqual(rows[0]["cnt"], 1)
        finally:
            conn.close()
