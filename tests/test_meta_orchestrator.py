"""Tests for MetaOrchestratorAgent."""

from __future__ import annotations
import unittest
import json
import tempfile
from pathlib import Path
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.meta_orchestrator import MetaOrchestratorAgent


class TestMetaOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.orig_state = Path(".state")
        self.test_state = Path(tempfile.mkdtemp()) / ".state"
        self.test_state.mkdir(parents=True, exist_ok=True)
        # Patch the history file location by creating agent with custom path
        self.agent = MetaOrchestratorAgent()
        self.agent.history_file = self.test_state / "meta_history.json"

    def tearDown(self):
        import shutil

        shutil.rmtree(self.test_state.parent, ignore_errors=True)

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "meta_orchestrator")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("cycle_analysis", result.output)

    def test_run_with_step_results(self):
        ctx = CampaignContext(
            campaign={"niche": "marketing digital"},
            step_results={
                "analytics": {"status": "success", "output": {"metrics": {}}},
                "compliance": {"status": "success", "output": {"status": "pass"}},
                "optimization": {"status": "success", "output": {"actions": []}},
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("prescriptions", result.output)

    def test_run_with_failing_steps(self):
        ctx = CampaignContext(
            campaign={"niche": "test"},
            step_results={
                "analytics": {"status": "error", "error": "Failed to analyze"},
                "content_generator": {"status": "error", "error": "Generation timeout"},
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("diagnosis", result.output)

    def test_history_persistence(self):
        ctx = CampaignContext(campaign={"niche": "test"})
        self.agent.run(ctx)
        # History should be saved
        self.assertTrue(self.agent.history_file.exists())
        data = json.loads(self.agent.history_file.read_text())
        self.assertIn("cycles", data)
        self.assertGreater(len(data["cycles"]), 0)


if __name__ == "__main__":
    unittest.main()
