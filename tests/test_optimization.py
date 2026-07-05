"""Tests for OptimizationAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.optimization import OptimizationAgent


class TestOptimizationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = OptimizationAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "optimization")

    def test_run_with_analytics(self):
        ctx = CampaignContext(
            campaign={"campaign_id": "test-001", "channels": ["blog", "email"]},
            step_results={
                "analytics": {
                    "output": {
                        "metrics": {"cpa_avg": 35.0, "ctr_avg": 0.025},
                        "risks": ["baixo volume de conversões"],
                    }
                },
                "compliance": {
                    "output": {"status": "pass", "guardrails": ["revisar disclosure"]}
                },
                "memory_lookup": {
                    "output": {"learnings": ["campanha anterior teve alto engajamento"]}
                },
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("actions", result.output)

    def test_run_with_compliance_block(self):
        ctx = CampaignContext(
            campaign={"campaign_id": "test-002"},
            step_results={
                "analytics": {"output": {"metrics": {}}},
                "compliance": {"output": {"status": "block", "guardrails": []}},
                "memory_lookup": {"output": {"learnings": []}},
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        actions = result.output.get("actions", [])
        self.assertGreater(len(actions), 0)

    def test_run_empty_context(self):
        ctx = CampaignContext()
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("actions", result.output)

    def test_run_with_channels(self):
        ctx = CampaignContext(
            campaign={
                "campaign_id": "test-003",
                "channels": ["blog", "youtube", "pinterest"],
            },
            step_results={
                "analytics": {
                    "output": {"metrics": {"cpa_avg": 50.0, "ctr_avg": 0.015}}
                },
                "compliance": {"output": {"status": "pass", "guardrails": []}},
                "memory_lookup": {"output": {"learnings": []}},
            },
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("actions", result.output)


if __name__ == "__main__":
    unittest.main()
