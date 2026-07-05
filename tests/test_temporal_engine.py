"""Tests for TemporalEngineAgent (5th Order — Temporal Intelligence)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.temporal_engine import (
    TemporalEngineAgent,
    TemporalStore,
    SEASONAL_EVENTS,
)
from campaign_autopilot.agents.base import CampaignContext


class TestTemporalStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()  # Libera lock no Windows
        self.db_path = self.tmp.name
        self.tmp.close()
        self.store = TemporalStore(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_initial_state(self):
        s = self.store.get_summary()
        self.assertEqual(s["timeline_events"], 0)
        self.assertEqual(s["narrative_dimensions"], 0)

    def test_record_event(self):
        self.store.record_cycle_event(
            "c1", "tecnologia", "cycle_complete", {"articles": 2}
        )
        timeline = self.store.get_timeline()
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]["cycle_id"], "c1")

    def test_timeline_filter_by_niche(self):
        self.store.record_cycle_event("c1", "tecnologia", "cycle_complete", {})
        self.store.record_cycle_event("c2", "financas", "cycle_complete", {})
        t = self.store.get_timeline(niche="tecnologia")
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["niche"], "tecnologia")

    def test_narrative_self(self):
        self.store.update_narrative_self("global", "Sou um sistema novo.")
        narratives = self.store.get_narrative_self()
        self.assertIn("global", narratives)

    def test_seasonal_events_configured(self):
        self.assertGreater(len(SEASONAL_EVENTS), 5)


class TestTemporalEngineAgent(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()  # Libera lock no Windows
        self.db_path = self.tmp.name
        self.tmp.close()
        self.agent = TemporalEngineAgent(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_agent_creation(self):
        self.assertEqual(self.agent.name, "temporal_engine")

    def test_run_empty(self):
        ctx = CampaignContext(campaign={"niche": "test"}, run_id="test-001")
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("narrative", result.output)
        self.assertIn("foresight", result.output)
        self.assertIn("seasonal_events", result.output)

    def test_run_with_history(self):
        # First cycle
        ctx1 = CampaignContext(
            campaign={
                "niche": "tecnologia",
                "cycle_id": "c1",
                "articles": 2,
                "revenue": 100.0,
            },
            run_id="r1",
        )
        r1 = self.agent.run(ctx1)
        self.assertEqual(r1.status, "success")

        # Second cycle
        ctx2 = CampaignContext(
            campaign={
                "niche": "tecnologia",
                "cycle_id": "c2",
                "articles": 3,
                "revenue": 150.0,
            },
            run_id="r2",
        )
        r2 = self.agent.run(ctx2)
        self.assertEqual(r2.status, "success")
        self.assertGreater(len(r2.output.get("timeline", r2.output["narrative"])), 0)


if __name__ == "__main__":
    unittest.main()
