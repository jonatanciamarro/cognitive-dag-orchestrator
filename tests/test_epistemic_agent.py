"""Tests for EpistemicAgent (third-order)."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.epistemic_agent import EpistemicAgent


class TestEpistemicAgent(unittest.TestCase):
    def setUp(self):
        self.agent = EpistemicAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "epistemic")

    def test_run(self):
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("knowledge_map", result.output)

    def test_run_finds_blind_spots(self):
        ctx = CampaignContext(campaign={"niche": "afiliados"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("blind_spots", result.output)

    def test_run_generates_hypotheses(self):
        ctx = CampaignContext(campaign={"niche": "produtividade"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        # Hypotheses can be at top level or inside knowledge_map
        has_hypotheses = (
            "alternative_hypotheses" in result.output
            or "hypotheses" in result.output.get("knowledge_map", {})
        )
        self.assertTrue(has_hypotheses)

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        # Should handle empty context gracefully
        self.assertEqual(result.status, "success")
        self.assertIn("knowledge_map", result.output)


if __name__ == "__main__":
    unittest.main()
