"""Tests for CircuitBreaker."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.circuit_breaker import CircuitBreaker, _CRITICAL_AGENTS


class TestCircuitBreaker(unittest.TestCase):
    def setUp(self):
        self.breaker = CircuitBreaker()

    def test_instantiation(self):
        self.assertEqual(self.breaker.name, "circuit_breaker")

    def test_initial_state_green(self):
        ctx = CampaignContext()
        result = self.breaker.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["status"], "GREEN")

    def test_critical_agents_defined(self):
        self.assertIn("content_generator", _CRITICAL_AGENTS)
        self.assertIn("meta_orchestrator", _CRITICAL_AGENTS)

    def test_run_with_step_results(self):
        ctx = CampaignContext(
            step_results={
                "analytics": {"output": {"metrics": {}}},
                "content_generator": {"output": {"status": "success"}},
            }
        )
        result = self.breaker.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("status", result.output)

    def test_run_with_failures(self):
        ctx = CampaignContext(
            step_results={
                "content_generator": {"error": "Failed", "status": "error"},
                "free_image_gen": {"error": "Failed", "status": "error"},
            }
        )
        result = self.breaker.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("consecutive_failures", result.output)


if __name__ == "__main__":
    unittest.main()
