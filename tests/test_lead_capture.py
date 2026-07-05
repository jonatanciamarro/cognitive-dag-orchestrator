"""Tests for LeadCaptureAgent."""

from __future__ import annotations

import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.lead_capture import LeadCaptureAgent


class TestLeadCaptureAgent(unittest.TestCase):
    def setUp(self):
        self.agent = LeadCaptureAgent()

    def _make_context(self) -> CampaignContext:
        c = CampaignContext(
            campaign={"campaign_id": "lc_test", "niche": "marketing digital"}
        )
        c.run_id = "lc_run"
        c.step_results["seo_research"] = {
            "output": {"top_opportunities": [{"keyword": "marketing de afiliados"}]}
        }
        c.step_results["content_generator"] = {
            "output": {
                "articles": [{"title": "Guia de Afiliados", "keyword": "afiliados"}]
            }
        }
        return c

    def test_generates_lead_magnets(self):
        result = self.agent.run(self._make_context())
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output["total_lead_magnets"], 0)
        self.assertIn("lead_magnets", result.output)

    def test_has_4_magnet_types(self):
        result = self.agent.run(self._make_context())
        self.assertEqual(result.output["total_lead_magnets"], 4)

    def test_landing_page_generated(self):
        result = self.agent.run(self._make_context())
        self.assertIn("landing_page", result.output)
        self.assertIn("html_structure", result.output["landing_page"])

    def test_email_capture_variants(self):
        result = self.agent.run(self._make_context())
        self.assertIn("email_capture_variants", result.output)
        self.assertIn("popup", result.output["email_capture_variants"])
        self.assertIn("inline", result.output["email_capture_variants"])

    def test_content_upgrades(self):
        result = self.agent.run(self._make_context())
        self.assertIn("content_upgrades", result.output)

    def test_trace_metadata(self):
        result = self.agent.run(self._make_context())
        self.assertEqual(result.trace.agent, "lead_capture")
        self.assertIn("lead_magnets", result.trace.metadata)


if __name__ == "__main__":
    unittest.main()
