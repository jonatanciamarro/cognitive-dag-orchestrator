"""Tests for SelfHealingAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.self_healing import SelfHealingAgent


class TestSelfHealingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SelfHealingAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "self_healing")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("health_score", result.output)

    def test_health_report_structure(self):
        ctx = CampaignContext(campaign={"niche": "test"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("total_checks", result.output)
        self.assertIn("passed", result.output)
        self.assertIn("failed", result.output)

    def test_run_with_errors_in_context(self):
        ctx = CampaignContext(
            step_results={
                "content_generator": {"status": "error", "error": "Generation failed"},
            }
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("checks", result.output)


if __name__ == "__main__":
    unittest.main()
