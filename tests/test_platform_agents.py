"""Testes para PlatformAffiliateAgent e AllPlatformsSetupAgent."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from campaign_autopilot.agents.base import CampaignContext
from unittest import mock
from campaign_autopilot.agents.revenue import (
    PlatformAffiliateAgent,
    AllPlatformsSetupAgent,
    get_products_by_niche,
    get_products_by_platform,
)


class TestProductDatabase(unittest.TestCase):
    """Testes para o banco de produtos curados."""

    def test_products_exist_for_all_platforms(self):
        """Todas as 4 plataformas tem produtos."""
        for platform in ["mercadolivre", "shopee", "shein", "aliexpress"]:
            products = get_products_by_platform(platform)
            self.assertGreater(len(products), 0, f"{platform} tem 0 produtos")

    def test_products_by_niche(self):
        """Cada nicho tem produtos de multiplas plataformas."""
        for niche in ["tecnologia", "financas", "saude", "carreira"]:
            products = get_products_by_niche(niche)
            self.assertGreater(len(products), 0, f"{niche} tem 0 produtos")

    def test_all_platforms_returns_list(self):
        """get_all_platforms retorna lista."""
        from campaign_autopilot.agents.revenue.platform_products import (
            get_all_platforms,
        )

        platforms = get_all_platforms()
        self.assertIn("mercadolivre", platforms)
        self.assertIn("shopee", platforms)

    def test_product_has_required_fields(self):
        """Produtos tem campos obrigatorios."""
        products = get_products_by_platform("mercadolivre")
        for p in products:
            self.assertTrue(p.product_name)
            self.assertTrue(p.product_id)
            self.assertTrue(p.niche)
            self.assertGreater(p.price_brl, 0)
            self.assertGreater(p.commission_pct, 0)

    def test_build_url_mercadolivre(self):
        """Constroi URL de afiliado do ML corretamente."""
        products = get_products_by_platform("mercadolivre")
        if products:
            url = products[0].build_url("TEST123")
            self.assertIn("TEST123", url)
            self.assertIn(products[0].product_id, url)


class TestPlatformAffiliateAgent(unittest.TestCase):
    """Testes para PlatformAffiliateAgent."""

    def setUp(self):
        self.tmp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        config = {
            "_instructions": "Config de teste",
            "affiliate_ids": {},
            "offers_by_niche": {
                "tecnologia": [],
                "financas": [],
                "saude": [],
                "carreira": [],
            },
        }
        json.dump(config, self.tmp_config)
        self.tmp_config.close()

        # Patch the CONFIG_PATH
        self.patcher = mock.patch(
            "campaign_autopilot.agents.revenue.platform_agent.CONFIG_PATH",
            Path(self.tmp_config.name),
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if Path(self.tmp_config.name).exists():
            Path(self.tmp_config.name).unlink()

    def test_mercadolivre_protocol(self):
        """Mostra protocolo do ML."""
        agent = PlatformAffiliateAgent(platform="mercadolivre")
        ctx = CampaignContext(campaign={"action": "protocol"})
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("signup_url", result.output)

    def test_autosetup_requires_code(self):
        """Autosetup requer codigo de afiliado."""
        agent = PlatformAffiliateAgent(platform="shopee")
        ctx = CampaignContext(campaign={"action": "autosetup"})
        result = agent.run(ctx)
        self.assertEqual(result.status, "error")
        self.assertIn("affiliate_code_required", result.output.get("error", ""))

    @mock.patch.dict(os.environ, {"MERCADOLIVRE_AFFILIATE_ID": "TEST123"})
    def test_autosetup_with_env_code(self):
        """Autosetup usa codigo do env."""
        agent = PlatformAffiliateAgent(platform="mercadolivre")
        ctx = CampaignContext(campaign={"action": "autosetup", "niche": "tecnologia"})
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output.get("registered", 0), 0)

    def test_autosetup_with_explicit_code(self):
        """Autosetup com codigo explicito."""
        agent = PlatformAffiliateAgent(platform="aliexpress")
        ctx = CampaignContext(
            campaign={
                "action": "autosetup",
                "affiliate_code": "ALI123",
                "niche": "tecnologia",
            }
        )
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output.get("registered", 0), 0)

    def test_list_products(self):
        """Lista produtos disponiveis."""
        agent = PlatformAffiliateAgent(platform="shein")
        ctx = CampaignContext(campaign={"action": "list_products"})
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertGreater(result.output.get("total", 0), 0)

    def test_autosetup_registers_in_config(self):
        """Autosetup registra no config JSON."""
        agent = PlatformAffiliateAgent(platform="mercadolivre")
        ctx = CampaignContext(
            campaign={
                "action": "autosetup",
                "affiliate_code": "MLTEST",
                "niche": "tecnologia",
                "max_per_niche": 2,
            }
        )
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")

        # Verify config file
        with open(self.tmp_config.name) as f:
            config = json.load(f)

        ml_offers = [
            o
            for o in config.get("offers_by_niche", {}).get("tecnologia", [])
            if o.get("network") == "mercadolivre"
        ]
        self.assertGreater(len(ml_offers), 0)
        for offer in ml_offers:
            self.assertIn("MLTEST", offer.get("product_url", ""))
            self.assertTrue(offer.get("auto_collected"))

    def test_trace_metadata(self):
        """Verifica metadados do trace."""
        agent = PlatformAffiliateAgent(platform="shopee")
        ctx = CampaignContext(campaign={"action": "protocol"})
        result = agent.run(ctx)
        self.assertEqual(result.trace.agent, "affiliate_shopee")
        self.assertEqual(result.trace.status, "success")


class TestAllPlatformsSetupAgent(unittest.TestCase):
    """Testes para AllPlatformsSetupAgent."""

    def test_setup_all_requires_codes(self):
        """Setup all sem codigos retorna todos skipped."""
        agent = AllPlatformsSetupAgent()
        ctx = CampaignContext(campaign={"affiliate_codes": {}})
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        for plat, res in result.output.get("results", {}).items():
            self.assertEqual(res.get("status"), "skipped")

    @mock.patch.dict(
        os.environ,
        {
            "MERCADOLIVRE_AFFILIATE_ID": "MLTEST",
            "SHOPEE_AFFILIATE_ID": "SHPTEST",
        },
    )
    def test_setup_all_with_env_codes(self):
        """Setup all com codigos do env."""
        agent = AllPlatformsSetupAgent()
        ctx = CampaignContext(
            campaign={
                "affiliate_codes": {
                    "shein": "SH123",
                    "aliexpress": "ALI123",
                }
            }
        )
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")


if __name__ == "__main__":
    unittest.main()
