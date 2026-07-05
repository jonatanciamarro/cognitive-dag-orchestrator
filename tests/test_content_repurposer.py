"""Tests for ContentRepurposerAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.content_repurposer import ContentRepurposerAgent


class TestContentRepurposer(unittest.TestCase):
    def setUp(self):
        self.agent = ContentRepurposerAgent()

    def test_repurposes_articles(self):
        c = CampaignContext(
            campaign={"campaign_id": "rp_test", "niche": "marketing digital"}
        )
        c.run_id = "rp_run"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Guia de Afiliados",
                        "slug": "guia-afiliados",
                        "body": "Conteudo...",
                        "meta_description": "Guia completo",
                        "keyword": "afiliados",
                        "word_count": 500,
                    },
                ]
            }
        }
        c.step_results["seo_research"] = {
            "output": {"top_opportunities": [{"keyword": "marketing afiliados"}]}
        }
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output["total_articles_repurposed"], 0)
        self.assertGreater(result.output["total_formats_generated"], 0)

    def test_5_formats_per_article(self):
        c = CampaignContext(campaign={"campaign_id": "rp_test2", "niche": "marketing"})
        c.run_id = "rp_run2"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Teste",
                        "slug": "teste",
                        "body": "x",
                        "meta_description": "y",
                        "keyword": "z",
                        "word_count": 100,
                    },
                ]
            }
        }
        result = self.agent.run(c)
        content = result.output["repurposed_content"][0]
        self.assertIn("youtube", content)
        self.assertIn("pinterest", content)
        self.assertIn("whatsapp", content)
        self.assertIn("email", content)
        self.assertIn("social", content)

    def test_fallback_without_articles(self):
        c = CampaignContext(campaign={"campaign_id": "rp_test3", "niche": "marketing"})
        c.run_id = "rp_run3"
        c.step_results["content_planner"] = {
            "output": {
                "briefs": [
                    {"keyword": "teste", "topic": "Teste", "content_type": "article"}
                ]
            }
        }
        result = self.agent.run(c)
        self.assertGreaterEqual(result.output["total_articles_repurposed"], 1)


if __name__ == "__main__":
    unittest.main()
