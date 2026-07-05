"""Tests for PsychologySpecialistAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.psychology_specialist import PsychologySpecialistAgent


class TestPsychologySpecialistAgent(unittest.TestCase):
    def setUp(self):
        self.agent = PsychologySpecialistAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "psychology_specialist")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("profile", result.output)

    def test_run_with_niche(self):
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
