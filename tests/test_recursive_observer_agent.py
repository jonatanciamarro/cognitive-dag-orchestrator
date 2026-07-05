"""Tests for RecursiveObserverAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.recursive_observer_agent import RecursiveObserverAgent


class TestRecursiveObserverAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RecursiveObserverAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "recursive_observer")

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("governance_audit", result.output)

    def test_run_with_context(self):
        ctx = CampaignContext(campaign={"niche": "test"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
