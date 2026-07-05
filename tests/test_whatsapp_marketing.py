"""Tests for WhatsAppMarketingAgent."""

from __future__ import annotations

import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.whatsapp_marketing import WhatsAppMarketingAgent


class TestWhatsAppMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WhatsAppMarketingAgent()

    def _make_context(self) -> CampaignContext:
        c = CampaignContext(
            campaign={"campaign_id": "wa_test", "niche": "marketing digital"}
        )
        c.run_id = "wa_run"
        c.step_results["seo_research"] = {
            "output": {"top_opportunities": [{"keyword": "marketing de afiliados"}]}
        }
        c.step_results["content_generator"] = {
            "output": {
                "articles": [{"title": "Guia de Afiliados", "slug": "guia-afiliados"}]
            }
        }
        return c

    def test_generates_messages(self):
        result = self.agent.run(self._make_context())
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output["total_messages"], 0)
        self.assertIn("messages", result.output)
        self.assertIn("strategy", result.output)
        self.assertIn("recommended_tools", result.output)

    def test_has_5_message_types(self):
        result = self.agent.run(self._make_context())
        self.assertEqual(result.output["total_messages"], 5)

    def test_messages_have_body(self):
        result = self.agent.run(self._make_context())
        for msg in result.output["messages"]:
            self.assertIn("body", msg)
            self.assertIn("type", msg)
            self.assertIn("schedule", msg)
            self.assertGreater(len(msg["body"]), 20)

    def test_weekly_count(self):
        result = self.agent.run(self._make_context())
        self.assertGreater(result.output["weekly_messages"], 0)

    def test_trace_metadata(self):
        result = self.agent.run(self._make_context())
        self.assertEqual(result.trace.agent, "whatsapp_marketing")
        self.assertIn("messages", result.trace.metadata)


if __name__ == "__main__":
    unittest.main()
