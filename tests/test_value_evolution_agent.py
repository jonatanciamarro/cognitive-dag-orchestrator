"""Tests for ValueEvolutionAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.value_evolution_agent import ValueEvolutionAgent


class TestValueEvolutionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ValueEvolutionAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "value_evolution")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("current_values", result.output)

    def test_run_with_niche(self):
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("suggested_evolution", result.output)


if __name__ == "__main__":
    unittest.main()
