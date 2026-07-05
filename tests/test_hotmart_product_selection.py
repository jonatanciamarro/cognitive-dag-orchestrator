"""Testes para HotmartProductResearcherAgent e HotmartAffiliateSelectorAgent."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.hotmart import (
    HotmartProductResearcherAgent,
    HotmartAffiliateSelectorAgent,
)


class TestHotmartProductResearcherAgent(unittest.TestCase):
    """Testes para o pesquisador de produtos Hotmart."""

    def setUp(self):
        self.agent = HotmartProductResearcherAgent()

    def test_research_all_niches(self):
        """Pesquisa todos os nichos e retorna produtos."""
        ctx = CampaignContext(campaign={"niche": "all", "max_results": 3})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("results", result.output)
        self.assertEqual(len(result.output["results"]), 4)  # 4 nichos

    def test_research_specific_niche(self):
        """Pesquisa nicho especifico e retorna produtos ranqueados."""
        ctx = CampaignContext(campaign={"niche": "financas", "max_results": 5})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["niche"], "financas")
        products = result.output["results"]
        self.assertGreater(len(products), 0)
        self.assertLessEqual(len(products), 5)
        # Verificar se estao ordenados por velocity_score
        scores = [p["velocity_score"] for p in products]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_research_tecnologia(self):
        """Pesquisa tecnologia e verifica produtos."""
        ctx = CampaignContext(campaign={"niche": "tecnologia", "max_results": 10})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        products = result.output["results"]
        self.assertGreater(len(products), 0)
        for p in products:
            self.assertIn("product_name", p)
            self.assertIn("velocity_score", p)
            self.assertIn("earnings_per_sale", p)

    def test_research_min_velocity_filter(self):
        """Filtro de velocidade minima funciona."""
        ctx = CampaignContext(
            campaign={"niche": "carreira", "max_results": 10, "min_velocity": 50.0}
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        for p in result.output["results"]:
            self.assertGreaterEqual(p["velocity_score"], 50.0)

    def test_trace_metadata(self):
        """Verifica metadados do trace."""
        ctx = CampaignContext(campaign={"niche": "saude"})
        result = self.agent.run(ctx)
        self.assertEqual(result.trace.status, "success")
        self.assertEqual(result.trace.agent, "hotmart_product_researcher")


class TestHotmartAffiliateSelectorAgent(unittest.TestCase):
    """Testes para o seletor de afiliados Hotmart."""

    def setUp(self):
        self.agent = HotmartAffiliateSelectorAgent()

    def test_select_without_products(self):
        """Seleciona sem receber produtos — pesquisa internamente."""
        ctx = CampaignContext(campaign={"niche": "all", "budget_tier": "rapido"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("selected", result.output)
        self.assertGreaterEqual(len(result.output["selected"]), 1)
        self.assertIn("hunt_list", result.output)

    def test_select_rapido_tier(self):
        """Seleciona com tier 'rapido' — prioriza velocidade."""
        ctx = CampaignContext(campaign={"niche": "tecnologia", "budget_tier": "rapido"})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        selected = result.output["selected"]
        self.assertGreaterEqual(len(selected), 1)
        self.assertLessEqual(len(selected), 3)

    def test_select_equilibrio_tier(self):
        """Seleciona com tier 'equilibrio'."""
        ctx = CampaignContext(
            campaign={"niche": "financas", "budget_tier": "equilibrio"}
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["budget_tier"], "equilibrio")

    def test_select_ticket_alto_tier(self):
        """Seleciona com tier 'ticket_alto' — prioriza maior ganho por venda."""
        ctx = CampaignContext(
            campaign={"niche": "carreira", "budget_tier": "ticket_alto"}
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("selection_criteria", result.output)

    def test_hunt_list_generated(self):
        """Gera lista de caca legivel."""
        ctx = CampaignContext(campaign={"niche": "saude", "budget_tier": "rapido"})
        result = self.agent.run(ctx)
        self.assertIn("hunt_list", result.output)
        self.assertIn("LISTA DE PRODUTOS", result.output["hunt_list"])

    def test_trace_metadata(self):
        """Verifica metadados do trace."""
        ctx = CampaignContext(campaign={"niche": "tecnologia"})
        result = self.agent.run(ctx)
        self.assertEqual(result.trace.agent, "hotmart_affiliate_selector")
        self.assertEqual(result.trace.status, "success")


if __name__ == "__main__":
    unittest.main()
