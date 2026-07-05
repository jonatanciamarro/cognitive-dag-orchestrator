"""Tests for OfferLookupAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.offer_lookup import OfferLookupAgent


class TestOfferLookupAgent(unittest.TestCase):
    def setUp(self):
        self.agent = OfferLookupAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "offer_lookup")

    def test_run_with_category(self):
        ctx = CampaignContext(campaign={"category": "tecnologia"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("available_offers", result.output)

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("available_offers", result.output)

    def test_run_with_marketing_category(self):
        ctx = CampaignContext(campaign={"category": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        offers = result.output.get("available_offers", [])
        self.assertGreater(len(offers), 0)


if __name__ == "__main__":
    unittest.main()
