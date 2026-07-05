"""Tests for Hotmart Agent System."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.hotmart import (
    HotmartLinkManagerAgent,
    ProductMatcherAgent,
    AffiliateConfigUpdaterAgent,
    LinkValidatorAgent,
)
from campaign_autopilot.agents.hotmart.link_manager import HotmartLinkStore
from campaign_autopilot.agents.base import CampaignContext


class TestLinkStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()  # Libera lock no Windows
        self.db_path = self.tmp.name
        self.tmp.close()
        self.store = HotmartLinkStore(self.db_path)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_add_link(self):
        result = self.store.add_link(
            "tecnologia", "Curso Python", "https://hotm.art/python?aff=test"
        )
        self.assertTrue(result)

    def test_duplicate_url(self):
        self.store.add_link(
            "tecnologia", "Curso Python", "https://hotm.art/python?aff=test"
        )
        self.store.add_link(
            "financas", "Curso Python", "https://hotm.art/python?aff=test"
        )
        links = self.store.get_links()
        self.assertGreaterEqual(len(links), 1)

    def test_get_by_niche(self):
        self.store.add_link("tecnologia", "Curso A", "https://hotm.art/a?aff=t")
        self.store.add_link("financas", "Curso B", "https://hotm.art/b?aff=t")
        tech = self.store.get_links(niche="tecnologia")
        self.assertEqual(len(tech), 1)
        self.assertEqual(tech[0]["niche"], "tecnologia")

    def test_status(self):
        self.store.add_link("tecnologia", "Curso A", "https://hotm.art/a?aff=t")
        self.store.add_link("financas", "Curso B", "https://hotm.art/b?aff=t")
        status = self.store.get_status()
        self.assertEqual(len(status), 2)


class TestLinkManagerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = HotmartLinkManagerAgent()

    def test_agent_name(self):
        self.assertEqual(self.agent.name, "hotmart_link_manager")

    def test_add_link_via_context(self):
        ctx = CampaignContext(
            campaign={
                "niche": "tecnologia",
                "product_name": "Curso de IA",
                "product_url": "https://hotm.art/ia?aff=test123",
            },
            run_id="test-add",
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertTrue(result.output.get("added", False))


class TestProductMatcher(unittest.TestCase):
    def setUp(self):
        self.agent = ProductMatcherAgent()

    def test_detect_curso(self):
        ctx = CampaignContext(
            campaign={
                "product_name": "Curso Completo de Python",
                "niche": "tecnologia",
            },
            run_id="t1",
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["product_type"], "curso")
        self.assertGreater(len(result.output["suggested_keywords"]), 0)

    def test_detect_ebook(self):
        ctx = CampaignContext(
            campaign={"product_name": "Ebook Guia Financeiro", "niche": "financas"},
            run_id="t2",
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.output["product_type"], "ebook")
        self.assertGreater(result.output["suggested_commission"], 50)

    def test_empty_name(self):
        ctx = CampaignContext(campaign={"product_name": ""}, run_id="t3")
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")


class TestLinkValidator(unittest.TestCase):
    def setUp(self):
        self.agent = LinkValidatorAgent()

    def test_valid_hotmart(self):
        ctx = CampaignContext(
            campaign={
                "link": "https://hotm.art/curso?aff=abc123",
                "product_name": "Curso Teste",
            },
            run_id="v1",
        )
        result = self.agent.run(ctx)
        self.assertTrue(result.output.get("valid", False))

    def test_invalid_no_aff(self):
        ctx = CampaignContext(
            campaign={
                "link": "https://hotm.art/curso",
                "product_name": "Curso Teste",
            },
            run_id="v2",
        )
        result = self.agent.run(ctx)
        self.assertFalse(result.output.get("valid", True))

    def test_placeholder(self):
        ctx = CampaignContext(
            campaign={
                "link": "https://hotm.art/seulink_python",
                "product_name": "Curso Teste",
            },
            run_id="v3",
        )
        result = self.agent.run(ctx)
        self.assertFalse(result.output.get("valid", True))


class TestConfigUpdater(unittest.TestCase):
    def setUp(self):
        self.orig_config = None
        self.config_path = Path("configs/affiliate_offers.json")
        if self.config_path.exists():
            self.orig_config = self.config_path.read_text()

    def tearDown(self):
        if self.orig_config:
            self.config_path.write_text(self.orig_config)

    def test_updater_runs(self):
        agent = AffiliateConfigUpdaterAgent()
        ctx = CampaignContext(campaign={"niche": "test"}, run_id="cu1")
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
