"""Tests for CompetitorAnalysisAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.competitor_analysis import CompetitorAnalysisAgent


class TestCompetitorAnalysis(unittest.TestCase):
    def setUp(self):
        self.agent = CompetitorAnalysisAgent()

    def test_empty_context_still_works(self):
        c = CampaignContext(
            campaign={"campaign_id": "comp_test", "niche": "marketing digital"}
        )
        c.run_id = "comp_run"
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")
        self.assertIn("competitors_found", result.output)
        self.assertIn("content_gaps", result.output)

    def test_with_simulated_seo_data(self):
        c = CampaignContext(
            campaign={"campaign_id": "comp_test2", "niche": "marketing"}
        )
        c.run_id = "comp_run2"
        c.step_results["seo_research"] = {
            "output": {
                "top_opportunities": [
                    {
                        "keyword": "marketing de afiliados",
                        "volume": 5000,
                        "difficulty": 0.3,
                    },
                    {
                        "keyword": "como ganhar dinheiro online",
                        "volume": 8000,
                        "difficulty": 0.5,
                    },
                    {"keyword": "SEO para blogs", "volume": 3000, "difficulty": 0.4},
                ]
            }
        }
        result = self.agent.run(c)
        self.assertGreaterEqual(result.output["competitors_found"], 0)

    def test_extract_domain(self):
        d = self.agent._extract_domain("https://www.exemplo.com/pagina")
        self.assertEqual(d, "exemplo.com")

    def test_trace_metadata(self):
        c = CampaignContext(campaign={"campaign_id": "comp_test3", "niche": "mkt"})
        c.run_id = "comp_run3"
        result = self.agent.run(c)
        self.assertEqual(result.trace.agent, "competitor_analysis")
        self.assertIn("competitors", result.trace.metadata)


if __name__ == "__main__":
    unittest.main()
