"""Tests for RevenueOrchestratorAgent (sub-package)."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.revenue.orchestrator import RevenueOrchestratorAgent


class TestRevenueOrchestratorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RevenueOrchestratorAgent()

    def test_instantiation(self):
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "revenue_orchestrator")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("summary", result.output)
        self.assertIn("active_sources", result.output)

    def test_run_returns_source_breakdown(self):
        ctx = CampaignContext(campaign={"niche": "tecnologia"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("summary", result.output)
        self.assertGreater(result.output["summary"]["total_sources"], 0)


if __name__ == "__main__":
    unittest.main()
