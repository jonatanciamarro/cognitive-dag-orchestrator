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
ORGANIC_WORKFLOW = ROOT / "workflows" / "organic_cycle.json"
ORGANIC_CONTEXT = ROOT / "examples" / "organic_context.json"


class TestOrganicIntegration(unittest.TestCase):
    """End-to-end integration test for the organic cycle with cognitive stores."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._db_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._db_path.unlink(missing_ok=True)

    def test_organic_cycle_produces_ready_plan_with_memory(self) -> None:
        """Run the full organic workflow with a real SQLite store and verify all
        cognitive stores recorded data."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))

        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=ORGANIC_WORKFLOW,
                memory_store=store,
            )
            result = orchestrator.run(CampaignContext.from_mapping(payload))

        # Workflow-level assertions
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["output"]["status"], "ready")
        self.assertEqual(
            set(result.output["step_results"].keys()),
            {
                "research",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
            },
        )

        # Semantic memory recorded ontology snapshot
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            version_rows = conn.execute(
                "SELECT * FROM semantic_ontology_versions ORDER BY released_at DESC"
            ).fetchall()
            self.assertGreaterEqual(len(version_rows), 1)
            version = dict(version_rows[0])
            self.assertIn("organic_cycle", version["version_id"])
            concepts = json.loads(version["concepts_snapshot"])
            self.assertGreater(len(concepts), 0)

            # Explanation store has decisions from all agents that record them
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

            # Outcome store recorded expected outcome
            outcome_rows = conn.execute(
                "SELECT * FROM feedback_outcomes ORDER BY created_at DESC"
            ).fetchall()
            self.assertGreaterEqual(len(outcome_rows), 1)
            outcome = dict(outcome_rows[0])
            expected = json.loads(outcome["expected_outcome"])
            self.assertIn("status", expected)
            self.assertIn("objective", expected)

            # Semantic knowledge was extracted (analytics extracts cycle knowledge)
            claim_rows = conn.execute(
                "SELECT * FROM semantic_claims LIMIT 10"
            ).fetchall()
            self.assertGreaterEqual(len(claim_rows), 1)

        finally:
            conn.close()

    def test_organic_cycle_without_memory_falls_back_gracefully(self) -> None:
        """Orchestrator without a memory_store should still produce a valid plan."""
        payload = json.loads(ORGANIC_CONTEXT.read_text(encoding="utf-8"))
        orchestrator = CampaignOrchestrator(workflow_path=ORGANIC_WORKFLOW)
        result = orchestrator.run(CampaignContext.from_mapping(payload))

        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["output"]["status"], "ready")
        self.assertEqual(
            set(result.output["step_results"].keys()),
            {
                "research",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
            },
        )
