"""Tests for KollektivAgent (4th Order — Collective Intelligence)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.kollektiv import KollektivAgent, CrossNicheVault
from campaign_autopilot.agents.base import CampaignContext


class TestCrossNicheVault(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()  # Libera lock no Windows
        self.db_path = self.tmp.name
        self.tmp.close()
        self.vault = CrossNicheVault(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_initial_state(self):
        summary = self.vault.get_summary()
        self.assertEqual(summary["niches_tracked"], 0)
        self.assertEqual(summary["total_cycles"], 0)
        self.assertEqual(summary["winning_strategies"], 0)

    def test_record_cycle(self):
        self.vault.record_cycle(
            "tecnologia",
            "cycle-001",
            {
                "articles": 2,
                "posts": 5,
                "revenue": 100.0,
                "seo_keywords": 10,
            },
        )
        summary = self.vault.get_summary()
        self.assertEqual(summary["niches_tracked"], 1)
        self.assertEqual(summary["total_cycles"], 1)

    def test_multiple_niches(self):
        for niche in ["tecnologia", "financas", "saude"]:
            self.vault.record_cycle(
                niche,
                f"cycle-{niche}",
                {
                    "articles": 1,
                    "posts": 3,
                    "revenue": 50.0,
                },
            )
        summary = self.vault.get_summary()
        self.assertEqual(summary["niches_tracked"], 3)
        self.assertEqual(summary["total_cycles"], 3)

    def test_cross_niche_recommendations_empty(self):
        recs = self.vault.get_cross_niche_recommendations("tecnologia")
        self.assertEqual(recs, [])

    def test_no_cross_patterns_initially(self):
        patterns = self.vault.detect_cross_patterns()
        self.assertEqual(patterns, [])


class TestKollektivAgent(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()  # Libera lock no Windows
        self.db_path = self.tmp.name
        self.tmp.close()
        self.agent = KollektivAgent(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_agent_creation(self):
        self.assertEqual(self.agent.name, "kollektiv")

    def test_run_with_empty_context(self):
        ctx = CampaignContext(campaign={"niche": "test"}, run_id="test-001")
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("synthesis", result.output)
        self.assertIn("vault_summary", result.output)

    def test_run_with_all_niches(self):
        ctx = CampaignContext(
            campaign={
                "all_niches_results": {
                    "tecnologia": {"articles": [{"title": "A"}], "cycle_id": "c1"},
                    "financas": {"articles": [{"title": "B"}], "cycle_id": "c2"},
                    "saude": {
                        "articles": [{"title": "C"}, {"title": "D"}],
                        "cycle_id": "c3",
                    },
                },
                "niches": ["tecnologia", "financas", "saude"],
            },
            run_id="test-002",
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        vault = result.output["vault_summary"]
        self.assertGreaterEqual(vault["niches_tracked"], 1)
        self.assertIn("cross_patterns", result.output)
        self.assertIn("recommendations", result.output)


if __name__ == "__main__":
    unittest.main()
