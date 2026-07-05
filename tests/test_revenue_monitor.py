"""Tests for RevenueMonitorAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.revenue_monitor import RevenueMonitorAgent


class TestRevenueMonitor(unittest.TestCase):
    def setUp(self):
        self.agent = RevenueMonitorAgent()

    def test_generates_projections(self):
        c = CampaignContext(
            campaign={"campaign_id": "rev_test", "niche": "marketing digital"}
        )
        c.run_id = "rev_run"
        c.step_results["offer_lookup"] = {
            "output": {
                "available_offers": [
                    {
                        "offer_id": "h1",
                        "network": "hotmart",
                        "product_name": "Curso MKT",
                        "commission_value": 60,
                        "price": 197,
                        "cookie_days": 30,
                        "category": "marketing",
                    }
                ]
            }
        }
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {"title": "A", "slug": "a", "body": "x", "word_count": 100}
                ]
            }
        }
        c.step_results["youtube_marketing"] = {"output": {"videos": [{"title": "V"}]}}
        c.step_results["email_marketing"] = {"output": {"total_emails": 5}}
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")
        self.assertIn("estimated_monthly_revenue", result.output["current_cycle"])
        self.assertIn("estimated_monthly_clicks", result.output["current_cycle"])
        self.assertIn("top_offers", result.output["current_cycle"])
        self.assertIn("recommendation", result.output)

    def test_empty_offers_still_works(self):
        c = CampaignContext(campaign={"campaign_id": "rev_test2", "niche": "mkt"})
        c.run_id = "rev_run2"
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["current_cycle"]["offers_available"], 0)


if __name__ == "__main__":
    unittest.main()
