"""Tests for StrategyEvolutionAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.strategy_evolution import StrategyEvolutionAgent


class TestStrategyEvolutionAgent(unittest.TestCase):
    def setUp(self):
        self.agent = StrategyEvolutionAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "strategy_evolution")

    def test_run(self):
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("applicable_strategies", result.output)

    def test_run_with_context(self):
        ctx = CampaignContext(
            campaign={"niche": "afiliados", "objective": "gerar receita"},
            step_results={
                "analytics": {"output": {"metrics": {"cpa_avg": 35.0}}},
                "memory_lookup": {
                    "output": {"learnings": ["Alta conversão em conteúdo tutorial"]}
                },
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("strategic_recommendations", result.output)


if __name__ == "__main__":
    unittest.main()
