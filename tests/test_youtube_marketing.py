"""Tests for YouTubeMarketingAgent."""

from __future__ import annotations

import unittest

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.youtube_marketing import YouTubeMarketingAgent


class TestYouTubeMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = YouTubeMarketingAgent()

    def _make_context(self, opportunities=None, offers=None) -> CampaignContext:
        context = CampaignContext(
            campaign={
                "campaign_id": "test_yt_001",
                "objective": "gerar trafego organico",
                "niche": "marketing digital",
            },
        )
        context.run_id = "test_yt_run_001"
        if opportunities is not None:
            context.step_results["seo_research"] = {
                "output": {"top_opportunities": opportunities}
            }
        if offers is not None:
            context.step_results["offer_lookup"] = {
                "output": {"available_offers": offers}
            }
        return context

    def test_generates_video_materials(self):
        """Should generate complete video materials."""
        opportunities = [
            {
                "keyword": "marketing de afiliados",
                "volume": 5000,
                "difficulty": 0.3,
                "intent": "informational",
            },
        ]
        context = self._make_context(opportunities)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertEqual(output["total_videos"], 1)
        self.assertIn("videos", output)
        video = output["videos"][0]

        self.assertIn("title", video)
        self.assertIn("description", video)
        self.assertIn("tags", video)
        self.assertIn("script_sections", video)
        self.assertIn("hook", video)
        self.assertIn("outro", video)
        self.assertIn("estimated_duration_minutes", video)

    def test_description_has_timestamps(self):
        """Description should contain timestamps for each section."""
        opportunities = [
            {
                "keyword": "SEO para iniciantes",
                "volume": 3000,
                "difficulty": 0.4,
                "intent": "commercial",
            },
        ]
        context = self._make_context(opportunities)
        result = self.agent.run(context)
        desc = result.output["videos"][0]["description"]
        self.assertIn("0:00", desc)
        self.assertIn("TIMESTAMPS", desc)

    def test_description_has_disclosure(self):
        """Description should contain affiliate disclosure."""
        opportunities = [
            {
                "keyword": "marketing digital",
                "volume": 1000,
                "difficulty": 0.3,
                "intent": "informational",
            },
        ]
        offers = [
            {
                "offer_id": "hotmart_001",
                "network": "hotmart",
                "product_name": "Curso Completo",
                "product_url": "https://hotmart.com/curso",
                "price": 197.00,
                "category": "marketing",
            }
        ]
        context = self._make_context(opportunities, offers)
        result = self.agent.run(context)
        desc = result.output["videos"][0]["description"]
        self.assertIn("DISCLOSURE", desc.upper())
        self.assertIn("afiliados", desc.lower())

    def test_description_has_affiliate_links(self):
        """Description should contain affiliate product links when offers available."""
        opportunities = [
            {
                "keyword": "ferramentas SEO",
                "volume": 2000,
                "difficulty": 0.4,
                "intent": "commercial",
            },
        ]
        offers = [
            {
                "offer_id": "hotmart_002",
                "network": "hotmart",
                "product_name": "Ferramenta SEO Pro",
                "product_url": "https://hotmart.com/seo-pro",
                "price": 97.00,
                "category": "tecnologia",
            }
        ]
        context = self._make_context(opportunities, offers)
        result = self.agent.run(context)
        desc = result.output["videos"][0]["description"]
        self.assertIn("hotmart.com/seo-pro", desc)

    def test_tags_generated(self):
        """Tags should be generated from niche."""
        opportunities = [
            {
                "keyword": "financas pessoais",
                "volume": 8000,
                "difficulty": 0.2,
                "intent": "informational",
            },
        ]
        context = CampaignContext(
            campaign={"campaign_id": "test_yt_002", "niche": "financas"},
        )
        context.run_id = "test_yt_run_002"
        context.step_results["seo_research"] = {
            "output": {"top_opportunities": opportunities}
        }
        result = self.agent.run(context)

        tags = result.output["videos"][0]["tags"]
        self.assertIn("financas pessoais", tags)
        self.assertIn("finanças pessoais", tags)

    def test_fallback_without_opportunities(self):
        """Should fall back to campaign objective when no SEO opportunities."""
        context = CampaignContext(
            campaign={
                "campaign_id": "test_yt_003",
                "objective": "marketing digital para iniciantes",
                "niche": "marketing digital",
            },
        )
        context.run_id = "test_yt_run_003"
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        self.assertGreaterEqual(result.output["total_videos"], 1)

    def test_max_videos_limit(self):
        """Should generate no more than 3 videos per cycle."""
        opportunities = [
            {
                "keyword": f"keyword_{i}",
                "volume": 1000,
                "difficulty": 0.3,
                "intent": "informational",
            }
            for i in range(10)
        ]
        context = self._make_context(opportunities)
        result = self.agent.run(context)
        self.assertLessEqual(result.output["total_videos"], 3)

    def test_trace_metadata(self):
        """Trace should contain video metadata."""
        opportunities = [
            {
                "keyword": "test",
                "volume": 1000,
                "difficulty": 0.3,
                "intent": "informational",
            }
        ]
        context = self._make_context(opportunities)
        result = self.agent.run(context)

        self.assertIsNotNone(result.trace)
        self.assertEqual(result.trace.agent, "youtube_marketing")
        self.assertEqual(result.trace.status, "success")
        self.assertIn("videos", result.trace.metadata)
        self.assertIn("niche", result.trace.metadata)

    def test_with_explanation_store(self):
        """Should work with ExplanationStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.explanation import ExplanationStore

        store = ExplanationStore(conn)
        agent = YouTubeMarketingAgent(explanation_store=store)

        context = self._make_context(
            [
                {
                    "keyword": "test",
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]
        )
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        row = store._execute("SELECT COUNT(*) FROM explanation_decisions").fetchone()
        self.assertGreater(row[0], 0)

    def test_with_semantic_memory(self):
        """Should work with SemanticMemoryStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.semantic_memory import SemanticMemoryStore

        sem = SemanticMemoryStore(conn)
        sem.register_observer(
            "youtube_marketing", "AGENT", "youtube_marketing_agent", 0.7
        )
        sem.register_concept("marketing digital", "niche", "Nicho de teste")

        agent = YouTubeMarketingAgent(semantic_memory=sem)
        context = self._make_context(
            [
                {
                    "keyword": "marketing de afiliados",
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]
        )
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        claims = sem.query_claims(limit=10)
        self.assertGreater(len(claims), 0)


if __name__ == "__main__":
    unittest.main()
