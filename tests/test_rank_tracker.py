"""Tests for RankTrackerAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.rank_tracker import RankTrackerAgent


class TestRankTracker(unittest.TestCase):
    def setUp(self):
        self.agent = RankTrackerAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "rank_tracker")

    def test_estimate_traffic_share(self):
        self.assertAlmostEqual(self.agent._estimate_traffic_share(1), 0.32)
        self.assertAlmostEqual(self.agent._estimate_traffic_share(10), 0.01)
        self.assertEqual(self.agent._estimate_traffic_share(15), 0.0)

    def test_run_without_network(self):
        c = CampaignContext(campaign={"campaign_id": "rt_test", "niche": "marketing"})
        c.run_id = "rt_run"
        result = self.agent.run(c)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
