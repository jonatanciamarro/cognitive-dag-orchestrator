"""Tests for SEOResearchAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.seo_research import SEOResearchAgent


class TestSEOResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SEOResearchAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "seo_research")

    def test_run_with_known_niche(self):
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("top_opportunities", result.output)
        self.assertGreater(len(result.output["top_opportunities"]), 0)

    def test_run_with_unknown_niche(self):
        ctx = CampaignContext(campaign={"niche": "niche_inexistente_xyz"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        # Should still return results or empty list
        self.assertIn("top_opportunities", result.output)

    def test_run_with_objective_fallback(self):
        ctx = CampaignContext(campaign={"objective": "afiliados"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertGreater(len(result.output["top_opportunities"]), 0)

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("top_opportunities", result.output)


if __name__ == "__main__":
    unittest.main()
