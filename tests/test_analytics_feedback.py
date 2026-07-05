"""Tests for AnalyticsFeedbackAgent."""

from __future__ import annotations

import unittest

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.analytics_feedback import AnalyticsFeedbackAgent


class TestAnalyticsFeedbackAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AnalyticsFeedbackAgent()

    def _make_context(
        self, articles=0, videos=0, emails=0, pins=0, compliance="pass"
    ) -> CampaignContext:
        context = CampaignContext(
            campaign={"campaign_id": "test_fb_001", "niche": "marketing digital"},
        )
        context.run_id = "test_fb_run"
        context.step_results = {
            "seo_research": {
                "output": {"total_keywords_found": 20, "opportunities_count": 5}
            },
            "compliance": {"output": {"status": compliance}},
            "content_generator": {
                "output": {
                    "articles": [{"word_count": 400}] * articles,
                    "total_words": articles * 400,
                }
            },
            "youtube_marketing": {
                "output": {"videos": [{"title": f"v{i}"} for i in range(videos)]}
            },
            "email_marketing": {
                "output": {
                    "total_emails": emails,
                    "total_sequences": 3,
                    "sequences": [],
                }
            },
            "pinterest_marketing": {
                "output": {
                    "pins": [{"title": f"p{i}"} for i in range(pins)],
                    "total_pins": pins,
                }
            },
            "wp_publisher": {
                "output": {"publications": [{"word_count": 400}] * articles}
            },
        }
        return context

    def test_evaluates_cycle(self):
        """Should evaluate a cycle and produce metrics."""
        context = self._make_context(articles=3, videos=2, emails=9, pins=5)
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertIn("cycle_summary", output)
        self.assertIn("lessons", output)
        self.assertIn("suggestions", output)

        summary = output["cycle_summary"]
        self.assertEqual(summary["total_articles"], 3)
        self.assertEqual(summary["total_videos"], 2)
        self.assertEqual(summary["total_emails"], 9)
        self.assertEqual(summary["total_pins"], 5)

    def test_high_score_for_full_cycle(self):
        """Full multi-channel cycle should get high score."""
        context = self._make_context(articles=3, videos=3, emails=9, pins=5)
        result = self.agent.run(context)
        score = result.output["cycle_summary"]["cycle_quality_score"]
        self.assertGreaterEqual(score, 60)
        self.assertLessEqual(score, 100)

    def test_low_score_for_empty_cycle(self):
        """Empty cycle should get low score."""
        context = self._make_context(articles=0, videos=0, emails=0, pins=0)
        result = self.agent.run(context)
        score = result.output["cycle_summary"]["cycle_quality_score"]
        self.assertLess(score, 30)

    def test_compliance_penalty(self):
        """Blocked compliance should reduce score."""
        good = self._make_context(
            articles=3, videos=2, emails=5, pins=3, compliance="pass"
        )
        blocked = self._make_context(
            articles=3, videos=2, emails=5, pins=3, compliance="block"
        )

        good_score = self.agent.run(good).output["cycle_summary"]["cycle_quality_score"]
        blocked_score = self.agent.run(blocked).output["cycle_summary"][
            "cycle_quality_score"
        ]
        self.assertGreater(good_score, blocked_score)

    def test_lessons_generated(self):
        """Should generate lessons based on cycle content."""
        context = self._make_context(articles=3, videos=2, emails=9, pins=5)
        result = self.agent.run(context)
        self.assertGreater(len(result.output["lessons"]), 0)

    def test_suggestions_for_missing_channels(self):
        """Should suggest adding channels that are missing."""
        context = self._make_context(articles=3, videos=0, emails=0, pins=0)
        result = self.agent.run(context)
        suggestions = result.output["suggestions"]
        video_suggestions = [
            s for s in suggestions if "vídeo" in s.lower() or "YouTube" in s
        ]
        self.assertGreater(len(video_suggestions), 0)

    def test_trace_metadata(self):
        """Trace should contain feedback metadata."""
        context = self._make_context(articles=3, videos=1, emails=5, pins=3)
        result = self.agent.run(context)
        self.assertIsNotNone(result.trace)
        self.assertEqual(result.trace.agent, "analytics_feedback")
        self.assertIn("cycle_score", result.trace.metadata)
        self.assertIn("lessons", result.trace.metadata)


if __name__ == "__main__":
    unittest.main()
