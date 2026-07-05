"""Tests for PinterestMarketingAgent."""

from __future__ import annotations

import unittest

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.pinterest_marketing import PinterestMarketingAgent


class TestPinterestMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = PinterestMarketingAgent()

    def _make_context(self, opportunities=None, offers=None) -> CampaignContext:
        context = CampaignContext(
            campaign={"campaign_id": "test_pin_001", "niche": "marketing digital"},
        )
        context.run_id = "test_pin_run"
        if opportunities is not None:
            context.step_results["seo_research"] = {
                "output": {"top_opportunities": opportunities}
            }
        if offers is not None:
            context.step_results["offer_lookup"] = {
                "output": {"available_offers": offers}
            }
        return context

    def test_generates_pins(self):
        """Should generate pins from SEO opportunities."""
        opps = [
            {
                "keyword": "marketing de afiliados",
                "volume": 5000,
                "difficulty": 0.3,
                "intent": "informational",
            }
        ]
        context = self._make_context(opps)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        self.assertGreater(result.output["total_pins"], 0)
        self.assertIn("pins", result.output)
        self.assertIn("boards", result.output)

    def test_pin_has_all_fields(self):
        """Each pin should have complete metadata."""
        opps = [
            {
                "keyword": "SEO",
                "volume": 1000,
                "difficulty": 0.3,
                "intent": "informational",
            }
        ]
        context = self._make_context(opps)
        pin = self.agent.run(context).output["pins"][0]

        self.assertIn("title", pin)
        self.assertIn("description", pin)
        self.assertIn("board", pin)
        self.assertIn("pin_type", pin)
        self.assertIn("hashtags", pin)
        self.assertIn("seo_keywords", pin)
        self.assertIn("image_suggestion", pin)
        self.assertIn("keyword", pin)

    def test_hashtags_generated(self):
        """Should generate relevant hashtags."""
        opps = [
            {
                "keyword": "financas pessoais",
                "volume": 8000,
                "difficulty": 0.2,
                "intent": "informational",
            }
        ]
        context = CampaignContext(campaign={"campaign_id": "t2", "niche": "financas"})
        context.run_id = "t2run"
        context.step_results["seo_research"] = {"output": {"top_opportunities": opps}}
        result = self.agent.run(context)

        hashtags = result.output["pins"][0]["hashtags"]
        self.assertGreater(len(hashtags), 0)
        self.assertTrue(all(h.startswith("#") for h in hashtags))

    def test_max_pins_limit(self):
        """Should generate no more than 5 pins."""
        opps = [
            {
                "keyword": f"k{i}",
                "volume": 1000,
                "difficulty": 0.3,
                "intent": "informational",
            }
            for i in range(20)
        ]
        context = self._make_context(opps)
        result = self.agent.run(context)
        self.assertLessEqual(result.output["total_pins"], 5)

    def test_fallback_without_opportunities(self):
        """Should work with no SEO data."""
        context = CampaignContext(campaign={"campaign_id": "t3", "niche": "marketing"})
        context.run_id = "t3run"
        result = self.agent.run(context)
        self.assertGreaterEqual(result.output["total_pins"], 1)

    def test_trace_metadata(self):
        """Trace should contain pin metadata."""
        context = self._make_context(
            [
                {
                    "keyword": "test",
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]
        )
        result = self.agent.run(context)
        self.assertIsNotNone(result.trace)
        self.assertEqual(result.trace.agent, "pinterest_marketing")
        self.assertIn("pins", result.trace.metadata)
        self.assertIn("boards", result.trace.metadata)


if __name__ == "__main__":
    unittest.main()
