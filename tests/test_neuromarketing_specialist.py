"""Tests for NeuromarketingSpecialistAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.neuromarketing_specialist import (
    NeuromarketingSpecialistAgent,
)


class TestNeuromarketingSpecialistAgent(unittest.TestCase):
    def setUp(self):
        self.agent = NeuromarketingSpecialistAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "neuromarketing_specialist")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("recommended_principles", result.output)

    def test_run_with_niche(self):
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
