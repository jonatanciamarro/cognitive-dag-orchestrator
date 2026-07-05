"""Tests for ContentOptimizerAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.content_optimizer import ContentOptimizerAgent


class TestContentOptimizer(unittest.TestCase):
    def setUp(self):
        self.agent = ContentOptimizerAgent()

    def test_empty_still_works(self):
        c = CampaignContext(campaign={"campaign_id": "co_test", "niche": "mkt"})
        c.run_id = "co_run"
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")

    def test_analyzes_articles(self):
        c = CampaignContext(campaign={"campaign_id": "co_test2", "niche": "mkt"})
        c.run_id = "co_run2"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Guia de Marketing Digital para Iniciantes",
                        "body": "Marketing digital é essencial. Aprenda marketing digital neste guia completo. "
                        * 50,
                        "meta_description": "Guia completo de marketing digital para iniciantes.",
                        "word_count": 300,
                        "keyword": "marketing digital",
                        "content_type": "article",
                    }
                ]
            }
        }
        result = self.agent.run(c)
        self.assertGreater(result.output["articles_analyzed"], 0)

    def test_generates_score(self):
        c = CampaignContext(campaign={"campaign_id": "co_test3", "niche": "mkt"})
        c.run_id = "co_run3"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Test",
                        "body": "x " * 400,
                        "meta_description": "Test desc.",
                        "word_count": 400,
                        "keyword": "test",
                        "content_type": "article",
                    }
                ]
            }
        }
        result = self.agent.run(c)
        self.assertGreaterEqual(result.output["average_seo_score"], 0)


if __name__ == "__main__":
    unittest.main()
