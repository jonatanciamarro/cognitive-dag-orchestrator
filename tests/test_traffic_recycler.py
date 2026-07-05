"""Tests for TrafficRecyclerAgent — reciclagem de trafego em multiplas camadas."""

from __future__ import annotations

import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.traffic_recycler import (
    TrafficRecyclerAgent,
    CONVERSION_PATHS,
    INTENT_MAP,
    NICHE_MAP,
)
from campaign_autopilot.agents.base import CampaignContext


class TestTrafficRecyclerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = TrafficRecyclerAgent()
        # Clean memory
        self.agent.memory = {
            "paths": {
                k: {"rpv": v["rpv"], "times_used": 0, "conversions": 0}
                for k, v in CONVERSION_PATHS.items()
            },
            "total_recycled": 0.0,
            "total_conversions": 0,
            "cycle_count": 0,
        }

    def test_conversion_paths_exist(self):
        """Todos os caminhos de conversao esperados devem existir."""
        expected = {
            "email_lead_magnet",
            "exit_intent_popup",
            "interstitial",
            "cross_niche",
            "telegram",
            "whatsapp",
            "digital_product",
            "membership",
        }
        for pid in expected:
            self.assertIn(pid, CONVERSION_PATHS, f"{pid} faltando em CONVERSION_PATHS")

    def test_intent_map_coverage(self):
        """Todas as intencoes devem ter caminhos mapeados."""
        for intent in ["informational", "commercial", "transactional", "navigational"]:
            self.assertIn(intent, INTENT_MAP, f"{intent} faltando em INTENT_MAP")
            self.assertGreater(len(INTENT_MAP[intent]), 0, f"{intent} sem caminhos")

    def test_niche_map_coverage(self):
        """Todos os nichos devem ter caminhos mapeados."""
        for niche in ["tecnologia", "financas", "saude", "carreira"]:
            self.assertIn(niche, NICHE_MAP, f"{niche} faltando em NICHE_MAP")
            self.assertGreater(len(NICHE_MAP[niche]), 0, f"{niche} sem caminhos")

    def test_get_paths_returns_scored(self):
        """get_paths deve retornar caminhos ordenados por score."""
        paths = self.agent.get_paths(
            {"title": "Melhor SSD", "intent": "commercial"}, "tecnologia", 5000
        )
        self.assertGreater(len(paths), 0)
        for i in range(len(paths) - 1):
            self.assertGreaterEqual(paths[i]["score"], paths[i + 1]["score"])

    def test_get_paths_informational(self):
        """Artigos informacionais devem ter caminhos diferentes de comerciais."""
        info_paths = self.agent.get_paths(
            {"title": "O que e IA", "intent": "informational"}, "tecnologia", 1000
        )
        comm_paths = self.agent.get_paths(
            {"title": "Melhor notebook", "intent": "commercial"}, "tecnologia", 1000
        )
        info_ids = [p["path_id"] for p in info_paths[:3]]
        comm_ids = [p["path_id"] for p in comm_paths[:3]]
        self.assertNotEqual(info_ids, comm_ids)

    def test_estimate_returns_values(self):
        """Estimativa deve retornar valores numericos."""
        content = {"title": "Teste", "slug": "teste"}
        paths = self.agent.get_paths(content, "tecnologia", 5000)
        est = self.agent.estimate(content, paths, 5000)
        self.assertGreater(est["recycled"], 0)
        self.assertGreater(est["visits"], 0)
        self.assertGreater(len(est["path_breakdown"]), 0)

    def test_gen_html_lead_magnet(self):
        """Lead magnet HTML deve ser gerado."""
        html = self.agent.gen_html(
            "email_lead_magnet",
            {"content": {"title": "Teste", "slug": "teste", "section": "tecnologia"}},
        )
        self.assertIn("lead", html.lower())
        self.assertIn("email", html.lower())

    def test_gen_html_exit_intent(self):
        """Exit intent popup HTML deve conter script."""
        html = self.agent.gen_html(
            "exit_intent_popup",
            {"content": {"title": "Teste", "slug": "teste", "section": "tecnologia"}},
        )
        self.assertIn("exit", html.lower())
        self.assertIn("<script>", html)

    def test_gen_html_telegram(self):
        """Telegram CTA deve ser gerado."""
        html = self.agent.gen_html(
            "telegram",
            {"content": {"title": "Teste", "slug": "teste", "section": "tecnologia"}},
        )
        self.assertIn("telegram", html.lower())

    def test_run_analysis(self):
        """Run deve analisar artigos e retornar metricas."""
        result = self.agent.run(
            CampaignContext(
                campaign={
                    "articles": [
                        {
                            "content": {
                                "title": "Melhor SSD 2026",
                                "slug": "ssd",
                                "section": "tecnologia",
                                "intent": "commercial",
                            }
                        },
                        {
                            "content": {
                                "title": "Como economizar",
                                "slug": "economizar",
                                "section": "financas",
                                "intent": "informational",
                            }
                        },
                    ],
                    "visit_data": {"ssd": 5000, "economizar": 3000},
                    "current_revenue": 100,
                }
            )
        )
        self.assertGreater(result.output["articles_analyzed"], 0)
        self.assertGreater(result.output["total_additional_revenue_potential"], 0)
        self.assertGreater(len(result.output["top_paths"]), 0)
        self.assertIn("interstitial_elements", result.output)
        self.assertIn("funnel", result.output)
        self.assertIn("next_steps", result.output)

    def test_memory_persistence(self):
        """Memoria deve salvar e carregar estado."""
        self.agent.memory["total_recycled"] = 500.0
        self.agent._save()
        new_agent = TrafficRecyclerAgent()
        self.assertGreaterEqual(new_agent.memory.get("total_recycled", 0), 500.0)

    def test_all_html_types_generated(self):
        """Todos os tipos de HTML devem ser geraveis."""
        for pid in [
            "email_lead_magnet",
            "exit_intent_popup",
            "telegram",
            "whatsapp",
            "interstitial",
        ]:
            html = self.agent.gen_html(
                pid,
                {
                    "content": {
                        "title": "Teste",
                        "slug": "teste",
                        "section": "tecnologia",
                    }
                },
            )
            self.assertGreater(len(html), 50, f"{pid} gerou HTML curto demais")


if __name__ == "__main__":
    unittest.main()
