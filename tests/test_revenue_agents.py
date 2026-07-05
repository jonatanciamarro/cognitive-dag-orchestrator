"""Testes para Revenue Agents — GenericAffiliate, AdSense, CPA, Orchestrator, Memory."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.revenue import (
    RevenueOrchestratorAgent,
    GenericAffiliateNetworkAgent,
    AdSenseAgent,
    CPAAgent,
    RevenueMemory,
    RevenueProtocol,
)


class TestRevenueMemory(unittest.TestCase):
    """Testes para RevenueMemory — banco unificado de receitas."""

    def setUp(self):
        self.tmp = tempfile.mktemp(suffix=".db")
        self.memory = RevenueMemory(db_path=self.tmp)

    def tearDown(self):
        if Path(self.tmp).exists():
            Path(self.tmp).unlink()

    def test_init_creates_all_sources(self):
        status = self.memory.get_status()
        sources = {s["source"] for s in status}
        expected = {
            "hotmart",
            "monetizze",
            "kiwify",
            "eduzz",
            "mercadolivre",
            "shopee",
            "shein",
            "aliexpress",
            "adsense",
            "cpa",
            "digital_product",
            "membership",
            "email_marketing",
            "lead_capture",
            "traffic_recycling",
            "paid_traffic",
        }
        self.assertEqual(sources, expected)
        self.assertEqual(len(status), 16)

    def test_update_source_status(self):
        self.memory.update_source("hotmart", status="active")
        status = self.memory.get_status()
        hotmart = next(s for s in status if s["source"] == "hotmart")
        self.assertEqual(hotmart["status"], "active")

    def test_update_source_revenue(self):
        self.memory.update_source("mercadolivre", revenue=150.0)
        summary = self.memory.get_summary()
        self.assertEqual(summary["total_revenue"], 150.0)
        self.memory.update_source("mercadolivre", revenue=50.0)
        summary = self.memory.get_summary()
        self.assertEqual(summary["total_revenue"], 200.0)

    def test_record_and_get_events(self):
        self.memory.record_event(
            "hotmart", "sale", amount=97.0, description="Curso vendido"
        )
        self.memory.record_event(
            "hotmart", "sale", amount=47.0, description="E-book vendido"
        )
        events = self.memory.get_events(source="hotmart")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["amount"], 47.0)

    def test_get_summary(self):
        self.memory.update_source("hotmart", revenue=100.0)
        self.memory.update_source("adsense", revenue=50.0)
        self.memory.update_source("hotmart", status="active")
        self.memory.update_source("adsense", status="active")
        summary = self.memory.get_summary()
        self.assertEqual(summary["total_revenue"], 150.0)
        self.assertEqual(summary["active_sources"], 2)
        self.assertEqual(summary["total_sources"], 16)

    def test_save_and_get_protocol(self):
        protocol = {"steps": ["step1", "step2"], "current_phase": "setup"}
        self.memory.save_protocol("hotmart", protocol)
        loaded = self.memory.get_protocol("hotmart")
        self.assertEqual(loaded, protocol)


class TestGenericAffiliateNetworkAgent(unittest.TestCase):
    """Testes para GenericAffiliateNetworkAgent (Monetizze, Kiwify, Eduzz)."""

    def setUp(self):
        self.agent = GenericAffiliateNetworkAgent(network="monetizze")
        self.context = CampaignContext(
            campaign={"action": "protocol"},
        )

    def test_init_sets_network(self):
        self.assertEqual(self.agent.network, "monetizze")
        self.assertEqual(self.agent.name, "affiliate_monetizze")

    def test_run_protocol_action(self):
        result = self.agent.run(self.context)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["network"], "monetizze")

    def test_run_ads_txt_action(self):
        ctx = CampaignContext(
            campaign={"action": "generate_ads_txt", "publisher_id": "pub-123456789"}
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")

    def test_run_add_link_action(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"offers_by_niche": {"tecnologia": []}}, f)
            tmp_path = f.name

        with patch(
            "campaign_autopilot.agents.revenue.generic_affiliate.CONFIG_PATH",
            Path(tmp_path),
        ):
            ctx = CampaignContext(
                campaign={
                    "action": "add_link",
                    "product_name": "Curso Teste",
                    "product_url": "https://monetizze.com.br/curso?afiliado=test123",
                    "niche": "tecnologia",
                }
            )
            result = self.agent.run(ctx)
            self.assertEqual(result.status, "success")
            self.assertTrue(result.output["added"])

            data = json.loads(Path(tmp_path).read_text())
            self.assertEqual(len(data["offers_by_niche"]["tecnologia"]), 1)
            self.assertEqual(
                data["offers_by_niche"]["tecnologia"][0]["product_name"], "Curso Teste"
            )

        Path(tmp_path).unlink(missing_ok=True)

    def test_run_add_link_missing_fields(self):
        ctx = CampaignContext(
            campaign={
                "action": "add_link",
                "product_name": "",
                "product_url": "",
            }
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "error")

    def test_kiwify_agent(self):
        agent = GenericAffiliateNetworkAgent(network="kiwify")
        ctx = CampaignContext(campaign={"action": "protocol"})
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["network"], "kiwify")

    def test_eduzz_agent(self):
        agent = GenericAffiliateNetworkAgent(network="eduzz")
        ctx = CampaignContext(campaign={"action": "protocol"})
        result = agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["network"], "eduzz")


class TestAdSenseAgent(unittest.TestCase):
    """Testes para AdSenseAgent."""

    def setUp(self):
        self.agent = AdSenseAgent()
        self.context = CampaignContext(
            campaign={"action": "protocol"},
        )

    def test_run_protocol_action(self):
        result = self.agent.run(self.context)
        self.assertEqual(result.status, "success")

    def test_run_verify_action(self):
        ctx = CampaignContext(
            campaign={"action": "verify_site", "site_url": "https://example.com"}
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")

    def test_run_ads_txt_action(self):
        ctx = CampaignContext(
            campaign={"action": "generate_ads_txt", "publisher_id": "pub-123456789"}
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")

    def test_run_protocol_default_fallback(self):
        ctx = CampaignContext(campaign={"action": "optimize"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        # Falls back to protocol since 'optimize' is not an AdSense action


class TestCPAAgent(unittest.TestCase):
    """Testes para CPAAgent."""

    def setUp(self):
        self.agent = CPAAgent()
        self.context = CampaignContext(
            campaign={"action": "protocol"},
        )

    def test_run_protocol_action(self):
        result = self.agent.run(self.context)
        self.assertEqual(result.status, "success")

    def test_run_lead_form_action(self):
        ctx = CampaignContext(campaign={"action": "generate_lead_form"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")

    def test_run_lead_magnet_action(self):
        ctx = CampaignContext(campaign={"action": "generate_lead_magnet"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")

    def test_run_protocol_default_fallback(self):
        ctx = CampaignContext(campaign={"action": "status"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")


class TestRevenueOrchestratorAgent(unittest.TestCase):
    """Testes para RevenueOrchestratorAgent."""

    def setUp(self):
        self.agent = RevenueOrchestratorAgent()
        self.context = CampaignContext(
            campaign={"action": "dashboard"},
        )

    def test_run_dashboard_action(self):
        result = self.agent.run(self.context)
        self.assertEqual(result.status, "success")
        self.assertIn("summary", result.output)
        self.assertIn("active_sources", result.output)
        self.assertIn("pending_sources", result.output)

    def test_run_setup_all_action(self):
        ctx = CampaignContext(campaign={"action": "setup_all"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["total_sources"], 16)

    def test_run_next_steps_action(self):
        ctx = CampaignContext(campaign={"action": "next_steps"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("pending_sources", result.output)

    def test_run_invalid_action_falls_back_to_dashboard(self):
        ctx = CampaignContext(campaign={"action": "invalid"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("summary", result.output)


class TestRevenueProtocol(unittest.TestCase):
    """Testes para RevenueProtocol."""

    def test_protocol_creation(self):
        protocol = RevenueProtocol(name="Test Network", source_type="affiliate")
        self.assertEqual(protocol.name, "Test Network")
        self.assertEqual(protocol.source_type, "affiliate")

    def test_protocol_steps(self):
        protocol = RevenueProtocol(name="Test", source_type="affiliate")
        steps = protocol.get_protocol_steps()
        self.assertEqual(len(steps), 7)
        self.assertEqual(steps[0]["phase"], "SETUP")
        self.assertEqual(steps[4]["phase"], "ACTIVATE")
        self.assertEqual(steps[6]["phase"], "OPTIMIZE")

    def test_protocol_to_dict(self):
        protocol = RevenueProtocol(name="Test", source_type="cpa")
        d = protocol.to_dict()
        self.assertEqual(d["name"], "Test")
        self.assertEqual(d["type"], "cpa")
        self.assertEqual(len(d["steps"]), 7)


if __name__ == "__main__":
    unittest.main()
