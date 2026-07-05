"""Tests for BulkPublisherAgent."""

from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.bulk_publisher import BulkPublisherAgent


class TestBulkPublisher(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.agent = BulkPublisherAgent(output_dir=str(self.tmpdir))

    def test_schedules_all_content(self):
        c = CampaignContext(campaign={"campaign_id": "bp_test", "niche": "mkt"})
        c.run_id = "bp_run"
        c.step_results["content_generator"] = {
            "output": {
                "articles": [
                    {
                        "title": "Artigo 1",
                        "slug": "artigo-1",
                        "keyword": "mkt",
                        "content_type": "article",
                        "word_count": 300,
                    },
                    {
                        "title": "Artigo 2",
                        "slug": "artigo-2",
                        "keyword": "seo",
                        "content_type": "article",
                        "word_count": 400,
                    },
                ]
            }
        }
        c.step_results["youtube_marketing"] = {
            "output": {
                "videos": [{"title": "Video 1", "estimated_duration_minutes": 10}]
            }
        }
        c.step_results["pinterest_marketing"] = {
            "output": {"pins": [{"title": "Pin 1", "board": "MKT"}]}
        }
        result = self.agent.run(c)
        self.assertGreater(result.output["total_items_scheduled"], 0)
        self.assertIn("schedule", result.output)
        self.assertIn("calendar", result.output)

    def test_empty_still_works(self):
        c = CampaignContext(campaign={"campaign_id": "bp_test2", "niche": "mkt"})
        c.run_id = "bp_run2"
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
