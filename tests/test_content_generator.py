"""Tests for ContentGeneratorAgent."""

from __future__ import annotations

import unittest

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.content_generator import ContentGeneratorAgent


class TestContentGeneratorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ContentGeneratorAgent()

    def _make_context(self, briefs=None, offers=None) -> CampaignContext:
        context = CampaignContext(
            campaign={
                "campaign_id": "test_content_001",
                "objective": "gerar receita com marketing de afiliados",
                "niche": "marketing digital para iniciantes",
            },
        )
        context.run_id = "test_run_12345"
        if briefs is not None:
            context.step_results["content_planner"] = {"output": {"briefs": briefs}}
        if offers is not None:
            context.step_results["offer_lookup"] = {
                "output": {"available_offers": offers}
            }
        return context

    def test_generates_articles_from_briefs(self):
        """Should generate articles for each briefing."""
        briefs = [
            {
                "keyword": "marketing de afiliados para iniciantes",
                "content_type": "article",
                "offers": ["hotmart_001"],
                "volume": 5000,
                "difficulty": 0.3,
                "estimated_volume": 5000,
            },
            {
                "keyword": "melhores ferramentas de SEO",
                "content_type": "review",
                "offers": ["hotmart_002"],
                "volume": 3000,
                "difficulty": 0.4,
                "estimated_volume": 3000,
            },
        ]
        offers = [
            {
                "offer_id": "hotmart_001",
                "network": "hotmart",
                "product_name": "Curso Marketing Digital Completo",
                "product_url": "https://hotmart.com/product/mkt",
                "price": 197.00,
            },
            {
                "offer_id": "hotmart_002",
                "network": "hotmart",
                "product_name": "Ferramenta de SEO Automatizado",
                "product_url": "https://hotmart.com/product/seo",
                "price": 97.00,
            },
        ]

        context = self._make_context(briefs, offers)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.output)
        output = result.output
        self.assertEqual(output["total_articles"], 2)
        self.assertIn("articles", output)
        self.assertEqual(len(output["articles"]), 2)
        self.assertIn("total_words", output)

        # Check article structure
        article = output["articles"][0]
        self.assertIn("title", article)
        self.assertIn("body", article)
        self.assertIn("slug", article)
        self.assertIn("meta_description", article)
        self.assertIn("word_count", article)
        self.assertIn("estimated_reading_time", article)
        self.assertIn("keyword", article)
        self.assertIn("content_type", article)

        # Verify article content
        self.assertGreater(article["word_count"], 50)
        self.assertGreater(len(article["body"]), 200)

    def test_generated_content_has_affiliate_disclosure(self):
        """Generated articles should contain affiliate disclosure."""
        briefs = [
            {
                "keyword": "marketing digital",
                "content_type": "article",
                "offers": ["hotmart_001"],
            }
        ]
        offers = [
            {
                "offer_id": "hotmart_001",
                "network": "hotmart",
                "product_name": "Curso Marketing Digital Completo",
                "product_url": "https://hotmart.com/product/mkt",
                "price": 197.00,
            }
        ]
        context = self._make_context(briefs, offers)
        result = self.agent.run(context)
        article = result.output["articles"][0]
        body_lower = article["body"].lower()
        # The disclosure mentions "comissão" and "afiliados" in Portuguese
        self.assertTrue("afiliados" in body_lower or "comissão" in body_lower)

    def test_fallback_without_briefs(self):
        """Should create fallback article when no briefs available."""
        context = self._make_context(None, None)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertGreaterEqual(output["total_articles"], 1)

    def test_generates_article_without_offers(self):
        """Should work even without offers."""
        briefs = [
            {
                "keyword": "marketing digital",
                "content_type": "article",
                "offers": [],
            }
        ]
        context = self._make_context(briefs, None)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertEqual(output["total_articles"], 1)
        article = output["articles"][0]
        self.assertIn("title", article)
        self.assertIn("body", article)

    def test_generates_review_content(self):
        """Review type should include product-specific content."""
        briefs = [
            {
                "keyword": "ferramenta SEO",
                "content_type": "review",
                "offers": ["hotmart_002"],
            }
        ]
        offers = [
            {
                "offer_id": "hotmart_002",
                "network": "hotmart",
                "product_name": "Ferramenta de SEO Automatizado",
                "product_url": "https://hotmart.com/product/seo",
                "price": 97.00,
            }
        ]
        context = self._make_context(briefs, offers)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        article = result.output["articles"][0]
        self.assertIn("Review", article["title"])
        self.assertIn("Ferramenta de SEO", article["title"])

    def test_max_articles_limit(self):
        """Should generate no more than 3 articles per cycle."""
        briefs = [
            {"keyword": f"keyword_{i}", "content_type": "article", "offers": []}
            for i in range(10)
        ]
        context = self._make_context(briefs, None)
        result = self.agent.run(context)

        output = result.output
        self.assertLessEqual(output["total_articles"], 3)

    def test_trace_metadata(self):
        """Trace should contain generation metadata."""
        briefs = [{"keyword": "test", "content_type": "article", "offers": []}]
        context = self._make_context(briefs, None)
        result = self.agent.run(context)

        self.assertIsNotNone(result.trace)
        self.assertEqual(result.trace.agent, "content_generator")
        self.assertEqual(result.trace.step_id, "content_generator")
        self.assertEqual(result.trace.status, "success")
        self.assertIn("articles", result.trace.metadata)
        self.assertIn("total_words", result.trace.metadata)

    def test_generation_with_explanation_store(self):
        """Should work with ExplanationStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.explanation import ExplanationStore

        store = ExplanationStore(conn)
        agent = ContentGeneratorAgent(explanation_store=store)

        briefs = [{"keyword": "test", "content_type": "article", "offers": []}]
        context = self._make_context(briefs, None)
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        # Verify decision was recorded
        row = store._execute("SELECT COUNT(*) FROM explanation_decisions").fetchone()
        self.assertGreater(row[0], 0)

    def test_generation_with_semantic_memory(self):
        """Should work with SemanticMemoryStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.semantic_memory import SemanticMemoryStore

        sem = SemanticMemoryStore(conn)
        sem.register_observer(
            "content_generator", "AGENT", "content_generator_agent", 0.7
        )
        sem.register_concept(
            "marketing digital para iniciantes", "niche", "Nicho de teste"
        )

        agent = ContentGeneratorAgent(semantic_memory=sem)

        briefs = [{"keyword": "test keyword", "content_type": "article", "offers": []}]
        context = self._make_context(briefs, None)
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        # Verify semantic claims were created
        claims = sem.query_claims(limit=10)
        self.assertGreater(len(claims), 0)


if __name__ == "__main__":
    unittest.main()
