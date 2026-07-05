from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.orchestrator import CampaignOrchestrator
from campaign_autopilot.memory import MemoryStore


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflows" / "campaign_cycle.json"
CONTEXT = ROOT / "examples" / "orchestrator_context.json"


class TestCampaignIntegration(unittest.TestCase):
    """End-to-end integration test for the campaign (CPA) cycle with cognitive stores."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._db_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._db_path.unlink(missing_ok=True)

    def test_campaign_cycle_with_memory_produces_ready_plan(self) -> None:
        """Run the full campaign workflow with a real SQLite store and verify
        cognitive stores recorded data."""
        payload = json.loads(CONTEXT.read_text(encoding="utf-8"))

        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=WORKFLOW,
                memory_store=store,
            )
            result = orchestrator.run(CampaignContext.from_mapping(payload))

        # Workflow-level assertions
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["output"]["status"], "ready")

        # Cognitive store assertions
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Ontology snapshot recorded
            version_rows = conn.execute(
                "SELECT * FROM semantic_ontology_versions ORDER BY released_at DESC"
            ).fetchall()
            self.assertGreaterEqual(len(version_rows), 1)

            # All agents recorded explanation decisions
            decision_rows = conn.execute(
                "SELECT DISTINCT agent_id FROM explanation_decisions"
            ).fetchall()
            agent_ids = {row["agent_id"] for row in decision_rows}
            for expected in (
                "analytics",
                "compliance",
                "memory_lookup",
                "optimization",
            ):
                self.assertIn(
                    expected, agent_ids, f"Agent {expected} did not record a decision"
                )

            # Expected outcome recorded
            outcome_rows = conn.execute(
                "SELECT * FROM feedback_outcomes ORDER BY created_at DESC"
            ).fetchall()
            self.assertGreaterEqual(len(outcome_rows), 1)

            # Semantic claims recorded
            claim_rows = conn.execute(
                "SELECT * FROM semantic_claims LIMIT 10"
            ).fetchall()
            self.assertGreaterEqual(len(claim_rows), 1)

        finally:
            conn.close()

    def test_campaign_cycle_with_memory_handles_compliance_block(self) -> None:
        """Compliance failure should still record decisions but block the plan."""
        payload = json.loads(CONTEXT.read_text(encoding="utf-8"))
        payload["campaign"]["headline"] = "Guaranteed income now"
        payload["policy"]["restricted_terms"] = ["guaranteed income"]

        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=WORKFLOW,
                memory_store=store,
            )
            result = orchestrator.run(CampaignContext.from_mapping(payload))

        self.assertEqual(
            result.output["step_results"]["compliance"]["output"]["status"], "block"
        )
        self.assertEqual(result.output["output"]["status"], "blocked")

        # Even when blocked, explanation decisions should be recorded
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            decision_rows = conn.execute(
                "SELECT DISTINCT agent_id FROM explanation_decisions"
            ).fetchall()
            agent_ids = {row["agent_id"] for row in decision_rows}
            self.assertIn("compliance", agent_ids)
        finally:
            conn.close()
