"""Tests for ContentPlannerAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.content_planner import ContentPlannerAgent


class TestContentPlannerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ContentPlannerAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "content_planner")

    def test_run_with_seo_and_offers(self):
        ctx = CampaignContext(
            campaign={"objective": "marketing digital"},
            step_results={
                "seo_research": {
                    "output": {
                        "top_opportunities": [
                            {
                                "keyword": "marketing digital para iniciantes",
                                "volume": 5400,
                                "difficulty": 0.35,
                            },
                            {
                                "keyword": "ferramentas marketing digital",
                                "volume": 3200,
                                "difficulty": 0.28,
                            },
                        ]
                    }
                },
                "offer_lookup": {
                    "output": {
                        "offers": [
                            {
                                "offer_id": "off_001",
                                "product_name": "Curso de Marketing",
                                "network": "hotmart",
                            },
                        ]
                    }
                },
                "memory_lookup": {
                    "output": {"learnings": ["Alta taxa de conversão em tutoriais"]}
                },
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("briefs", result.output)
        self.assertIn("content_strategy", result.output)

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("briefs", result.output)

    def test_run_without_offers(self):
        ctx = CampaignContext(
            campaign={"objective": "marketing digital"},
            step_results={
                "seo_research": {"output": {"top_opportunities": []}},
                "offer_lookup": {"output": {"offers": []}},
                "memory_lookup": {"output": {}},
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("briefs", result.output)


if __name__ == "__main__":
    unittest.main()
