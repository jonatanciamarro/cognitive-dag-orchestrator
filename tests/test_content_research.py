"""Tests for ContentResearchAgent (news sub-package)."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.news.content_research import ContentResearchAgent


class TestContentResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ContentResearchAgent()

    def test_instantiation(self):
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "content_research")

    def test_run_with_known_niche(self):
        ctx = CampaignContext(campaign={"niche": "tecnologia"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("top_opportunities", result.output)
        self.assertGreater(len(result.output["top_opportunities"]), 0)

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("top_opportunities", result.output)


if __name__ == "__main__":
    unittest.main()
