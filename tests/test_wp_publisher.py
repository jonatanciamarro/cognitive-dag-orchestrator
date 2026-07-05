"""Tests for WordPressPublisherAgent."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.wp_publisher import WordPressPublisherAgent


class TestWordPressPublisherAgent(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.agent = WordPressPublisherAgent(
            publish_mode="file", output_dir=str(self.tmpdir)
        )

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_context(
        self,
        articles=None,
        blocked=False,
        channels=None,
    ) -> CampaignContext:
        context = CampaignContext(
            campaign={
                "campaign_id": "test_pub_001",
                "objective": "test publishing",
                "niche": "marketing digital",
                "channels": channels or ["seo"],
            },
        )
        if articles is not None:
            context.step_results["content_generator"] = {
                "output": {"articles": articles}
            }
        context.step_results["compliance"] = {
            "output": {"status": "block" if blocked else "pass"}
        }
        return context

    def _make_article(
        self, keyword="marketing digital", content_type="article"
    ) -> dict:
        return {
            "title": f"Guia Completo de {keyword.title()}",
            "slug": keyword.lower().replace(" ", "-"),
            "body": f"Conteúdo completo sobre {keyword}. " * 50,
            "meta_description": f"Guia sobre {keyword} para iniciantes.",
            "word_count": 200,
            "estimated_reading_time": 2,
            "content_type": content_type,
            "keyword": keyword,
        }

    def test_publishes_articles_as_files(self):
        """Should save articles as .md files."""
        articles = [self._make_article()]
        context = self._make_context(articles)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertEqual(output["total_published"], 1)
        self.assertEqual(output["mode_used"], "file")
        self.assertEqual(output["file_count"], 1)

        # Verify file was created
        expected_file = self.tmpdir / "marketing-digital.md"
        self.assertTrue(expected_file.exists())
        content = expected_file.read_text(encoding="utf-8")
        self.assertIn("Guia Completo de Marketing Digital", content)
        self.assertIn("---", content)  # Frontmatter

    def test_publishes_multiple_articles(self):
        """Should publish multiple articles."""
        articles = [
            self._make_article("marketing digital"),
            self._make_article("seo para iniciantes"),
        ]
        context = self._make_context(articles)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["total_published"], 2)

    def test_dry_run_mode(self):
        """Dry run should not create files."""
        agent = WordPressPublisherAgent(
            publish_mode="dry_run", output_dir=str(self.tmpdir)
        )
        articles = [self._make_article()]
        context = self._make_context(articles)
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertEqual(output["total_published"], 1)
        self.assertEqual(output["mode_used"], "dry_run")
        # No files should be created in dry_run mode
        self.assertFalse(list(self.tmpdir.iterdir()))

    def test_fallback_from_briefs(self):
        """Should create publications from briefs when no articles."""
        context = CampaignContext(
            campaign={
                "campaign_id": "test_pub_002",
                "niche": "marketing",
                "channels": ["seo"],
            },
        )
        context.step_results["content_planner"] = {
            "output": {
                "briefs": [
                    {
                        "keyword": "marketing digital",
                        "topic": "Marketing Digital",
                        "content_type": "article",
                    },
                    {
                        "keyword": "ferramentas seo",
                        "topic": "Ferramentas SEO",
                        "content_type": "review",
                    },
                ]
            }
        }
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        self.assertGreaterEqual(result.output["total_published"], 1)

    def test_publication_metadata(self):
        """Each publication should have proper metadata."""
        articles = [self._make_article()]
        context = self._make_context(articles)
        result = self.agent.run(context)

        pub = result.output["publications"][0]
        self.assertIn("title", pub)
        self.assertIn("filename", pub)
        self.assertIn("path", pub)
        self.assertIn("status", pub)
        self.assertIn("mode", pub)
        self.assertIn("scheduled_date", pub)
        self.assertIn("word_count", pub)

    def test_with_explanation_store(self):
        """Should work with ExplanationStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.explanation import ExplanationStore

        store = ExplanationStore(conn)
        agent = WordPressPublisherAgent(
            publish_mode="file",
            output_dir=str(self.tmpdir),
            explanation_store=store,
        )

        articles = [self._make_article()]
        context = self._make_context(articles)
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        decisions = store._execute(
            "SELECT COUNT(*) AS cnt FROM explanation_decisions"
        ).fetchone()
        self.assertGreater(decisions[0], 0)

    def test_with_semantic_memory(self):
        """Should work with SemanticMemoryStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.semantic_memory import SemanticMemoryStore

        sem = SemanticMemoryStore(conn)
        sem.register_observer("wp_publisher", "AGENT", "wp_publisher_agent", 0.7)

        agent = WordPressPublisherAgent(
            publish_mode="file",
            output_dir=str(self.tmpdir),
            semantic_memory=sem,
        )

        # Pre-register article concept so the publisher can find it
        sem.register_concept(
            "article_marketing digital", "content", "Guia Completo de Marketing Digital"
        )
        sem.register_concept("publish_cycle_test", "publishing", "Ciclo de teste")

        articles = [self._make_article()]
        context = self._make_context(articles)
        context.run_id = "test_run_wp_001"
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        claims = sem.query_claims(limit=10)
        self.assertGreater(len(claims), 0)

    def test_trace_metadata(self):
        """Trace should contain publishing metadata."""
        articles = [self._make_article()]
        context = self._make_context(articles)
        result = self.agent.run(context)

        self.assertIsNotNone(result.trace)
        self.assertEqual(result.trace.agent, "wp_publisher")
        self.assertEqual(result.trace.status, "success")
        self.assertIn("publications", result.trace.metadata)
        self.assertIn("mode", result.trace.metadata)

    def test_custom_output_dir(self):
        """Should respect custom output directory."""
        custom_dir = Path(tempfile.mkdtemp())
        try:
            agent = WordPressPublisherAgent(
                publish_mode="file", output_dir=str(custom_dir)
            )
            articles = [self._make_article()]
            context = self._make_context(articles)
            result = agent.run(context)

            self.assertEqual(result.status, "success")
            self.assertTrue((custom_dir / "marketing-digital.md").exists())
        finally:
            import shutil

            shutil.rmtree(custom_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
