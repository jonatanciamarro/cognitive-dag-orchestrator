"""Tests for ObserverFusionAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.observer_fusion_agent import ObserverFusionAgent


class TestObserverFusionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ObserverFusionAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "observer_fusion")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("matrix", result.output)

    def test_run_with_step_results(self):
        ctx = CampaignContext(
            campaign={"niche": "marketing digital"},
            step_results={
                "analytics": {"output": {"metrics": {"ctr": 0.03}}},
                "compliance": {"output": {"status": "pass"}},
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("syntheses", result.output)


if __name__ == "__main__":
    unittest.main()
