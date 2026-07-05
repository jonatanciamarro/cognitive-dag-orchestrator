"""Tests for CreativeEngine (6th Order — Creative Intelligence)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.creative_engine import (
    CreativeEngine,
    MarketGapDetector,
    NicheGenesisAgent,
    NovelValueGenerator,
)
from campaign_autopilot.agents.base import CampaignContext


class TestMarketGapDetector(unittest.TestCase):
    def setUp(self):
        self.detector = MarketGapDetector()

    def test_scan_returns_opportunities(self):
        results = self.detector.scan()
        self.assertGreater(len(results), 5)
        self.assertIn("domain", results[0])
        self.assertIn("score", results[0])

    def test_opportunities_ranked(self):
        results = self.detector.scan()
        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_each_has_niche_name(self):
        results = self.detector.scan()
        for r in results:
            self.assertIn("suggested_niche_name", r)


class TestNicheGenesisAgent(unittest.TestCase):
    def setUp(self):
        self.agent = NicheGenesisAgent()

    def test_agent_name(self):
        self.assertEqual(self.agent.name, "niche_genesis")

    def test_generate_from_opportunity(self):
        ctx = CampaignContext(
            campaign={
                "opportunity": {
                    "domain": "educacao_online",
                    "description": "Cursos online",
                    "score": 0.85,
                }
            },
            run_id="test-genesis",
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("niche_config", result.output)
        self.assertIn("keywords", result.output)

    def test_viability_threshold(self):
        ctx = CampaignContext(
            campaign={
                "opportunity": {"domain": "test", "description": "Test", "score": 0.3}
            },
            run_id="test-low",
        )
        result = self.agent.run(ctx)
        self.assertFalse(result.output.get("ready_to_launch", True))


class TestNovelValueGenerator(unittest.TestCase):
    def setUp(self):
        self.agent = NovelValueGenerator()

    def test_generates_products(self):
        ctx = CampaignContext(
            campaign={"niche": "educacao_online", "domain": "educacao_online"},
            run_id="test-value",
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("product_ideas", result.output)
        self.assertGreater(len(result.output["product_ideas"]), 0)

    def test_generates_content_angles(self):
        ctx = CampaignContext(campaign={"niche": "saude_mental"}, run_id="test-angle")
        result = self.agent.run(ctx)
        self.assertGreater(len(result.output.get("content_angles", [])), 0)


class TestCreativeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CreativeEngine()

    def test_engine_name(self):
        self.assertEqual(self.engine.name, "creative_engine")

    def test_full_cycle(self):
        ctx = CampaignContext(campaign={}, run_id="test-creative")
        result = self.engine.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("synthesis", result.output)
        self.assertIn("opportunities", result.output)
        self.assertIn("new_niches", result.output)

    def test_synthesis_summary(self):
        ctx = CampaignContext(campaign={}, run_id="test-synth")
        result = self.engine.run(ctx)
        synth = result.output["synthesis"]
        self.assertIn("niches_ready_to_launch", synth)
        self.assertIn("recommendation", synth)


if __name__ == "__main__":
    unittest.main()
