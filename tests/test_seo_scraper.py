"""Tests for SEOScraperAgent."""

from __future__ import annotations
import unittest
from unittest.mock import patch
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.seo_scraper import SEOScraperAgent


def _mock_search_result(query: str, num_results: int = 10) -> dict:
    """Returns a fake search result without making HTTP requests."""
    return {
        "organic_results": [
            {"url": f"https://example.com/{i}", "title": f"Result {i} for {query}"}
            for i in range(min(num_results, 3))
        ],
        "total_results_found": 0,
        "related_questions": [f"O que é {query}?", f"Como fazer {query}?"],
        "search_suggestions": [f"{query} para iniciantes", f"{query} passo a passo"],
        "query": query,
    }


class TestSEOScraperAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SEOScraperAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "seo_scraper")

    def test_estimate_difficulty(self):
        d = self.agent._estimate_difficulty("test", 0, 0)
        self.assertEqual(d["level"], "very_easy")
        d = self.agent._estimate_difficulty("test", 12, 8)
        self.assertEqual(d["level"], "very_hard")

    def test_estimate_volume(self):
        v = self.agent._estimate_volume("melhores ferramentas de marketing", 0.5)
        self.assertGreater(v, 0)

    def test_extract_domain(self):
        self.assertIsNotNone(self.agent)

    def test_estimate_volume_returns_int(self):
        v = self.agent._estimate_volume("keyword", 0.3)
        self.assertIsInstance(v, int)
        self.assertGreater(v, 0)
        v = self.agent._estimate_volume("keyword", 0.9)
        self.assertIsInstance(v, int)

    @patch.object(SEOScraperAgent, "_google_search")
    def test_run_without_network(self, mock_search):
        """Should handle simulated search gracefully."""
        mock_search.return_value = _mock_search_result("marketing digital")
        ctx = CampaignContext(
            campaign={"campaign_id": "seo_test", "niche": "marketing digital"}
        )
        ctx.run_id = "seo_run"
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("results", result.output)
        self.assertGreater(len(result.output["results"]), 0)

    @patch.object(SEOScraperAgent, "_google_search")
    def test_run_returns_recommendation(self, mock_search):
        mock_search.return_value = _mock_search_result("afiliados")
        ctx = CampaignContext(campaign={"niche": "afiliados"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("recommendation", result.output)
        self.assertIn("additional_keywords_from_serp", result.output)


if __name__ == "__main__":
    unittest.main()
