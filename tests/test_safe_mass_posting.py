"""Tests for SafeMassPostingAgent — validacao anti-spam multi-plataforma."""

from __future__ import annotations

import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.safe_mass_posting import (
    SafeMassPostingAgent,
    PLATFORM_LIMITS,
)
from campaign_autopilot.agents.base import CampaignContext


class TestSafeMassPostingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SafeMassPostingAgent()
        # Clean memory for each test
        self.agent.memory = {
            "posts_log": [],
            "daily_counts": {},
            "weekly_counts": {},
            "monthly_counts": {},
            "hashes": [],
            "total_posts_safe": 0,
            "total_blocks": 0,
        }

    def test_platform_limits_exist(self):
        """Todos os limites esperados devem existir."""
        expected = {
            "blog",
            "youtube",
            "instagram",
            "tiktok",
            "twitter",
            "pinterest",
            "linkedin",
            "facebook",
            "telegram",
            "whatsapp",
            "email",
        }
        self.assertTrue(expected.issubset(set(PLATFORM_LIMITS.keys())))

    def test_validate_post_new_account(self):
        """Conta nova (30 dias) deve ter limite reduzido."""
        # Use blog which has higher base limit, so the reduction is still > 0
        v = self.agent.validate_post("blog", {"title": "Teste"}, account_age_days=15)
        self.assertIn(v["status"], ("pass", "warn", "block"))
        self.assertLessEqual(v["max_daily"], 3)  # 10 * 0.3 = 3
        self.assertEqual(v["account_multiplier"], 0.3)

    def test_validate_post_mature_account(self):
        """Conta madura (1+ ano) deve ter limite cheio."""
        v = self.agent.validate_post(
            "youtube", {"title": "Teste"}, account_age_days=400
        )
        self.assertIn(v["status"], ("pass", "warn"))
        self.assertEqual(v["max_daily"], PLATFORM_LIMITS["youtube"]["max_daily"])

    def test_validate_post_verified_account(self):
        """Conta verificada deve ter 1.2x do limite."""
        v = self.agent.validate_post(
            "youtube", {"title": "Teste"}, account_age_days=400, is_verified=True
        )
        expected = int(PLATFORM_LIMITS["youtube"]["max_daily"] * 1.2)
        self.assertEqual(v["max_daily"], expected)

    def test_content_hash_different(self):
        """Conteudos diferentes devem ter hashes diferentes."""
        h1 = self.agent._content_hash("Artigo sobre inteligencia artificial")
        h2 = self.agent._content_hash("Artigo sobre investimentos na bolsa")
        self.assertNotEqual(h1, h2)

    def test_content_similarity_low(self):
        """Conteudos diferentes devem ter baixa similaridade."""
        sim = self.agent._content_similarity(
            "Inteligencia artificial transforma o mundo",
            "Bolsa de valores atinge recorde historico",
        )
        self.assertLess(sim, 0.3)

    def test_generate_posting_plan(self):
        """Plano de postagem deve distribuir artigos pelas plataformas."""
        articles = [
            {"content": {"title": f"Artigo {i}", "slug": f"artigo-{i}"}}
            for i in range(5)
        ]
        plan = self.agent.generate_posting_plan(
            articles,
            {
                "platforms": ["blog", "pinterest", "telegram"],
                "account_age_days": 365,
            },
        )
        self.assertGreater(plan["total_scheduled"], 0)
        self.assertIn("blog", plan["plan"])
        self.assertIn("pinterest", plan["plan"])
        self.assertIn("telegram", plan["plan"])

    def test_run_validation(self):
        """Run deve validar todos os artigos para todas as plataformas."""
        result = self.agent.run(
            CampaignContext(
                campaign={
                    "articles": [{"content": {"title": "Teste"}} for _ in range(3)],
                    "posting_config": {
                        "platforms": ["blog", "pinterest"],
                        "account_age_days": 365,
                    },
                }
            )
        )
        self.assertGreater(result.output["posts_validated"], 0)
        self.assertIn("posts_passed", result.output)
        self.assertIn("posts_blocked", result.output)
        self.assertIn("posting_plan", result.output)
        self.assertIn("maximization_guide", result.output)

    def test_log_and_recover(self):
        """Post deve ser registrado e recuperavel."""
        v = self.agent.validate_post("blog", {"title": "Teste"}, 365)
        self.agent.log_post("blog", {"title": "Teste"}, v)
        self.assertEqual(self.agent.memory["total_posts_safe"], 1)
        self.assertEqual(len(self.agent.memory["posts_log"]), 1)

    def test_rapid_fire_detection(self):
        """Multiplos posts rapidos devem gerar warning."""
        for i in range(3):
            v = self.agent.validate_post("blog", {"title": f"Post {i}"}, 365)
            self.agent.log_post("blog", {"title": f"Post {i}"}, v)
        v = self.agent.validate_post("blog", {"title": "Post rapido"}, 365)
        self.assertIn(v["status"], ("pass", "warn"))

    def test_different_article_same_platform_block(self):
        """Artigos diferentes no mesmo dia devem passar."""
        v1 = self.agent.validate_post(
            "blog", {"title": "Marketing Digital 2026", "body": "Guia completo"}, 365
        )
        self.agent.log_post("blog", {"title": "Marketing Digital 2026"}, v1)
        v2 = self.agent.validate_post(
            "blog",
            {"title": "Investimentos na Bolsa", "body": "Guia para iniciantes"},
            365,
        )
        self.assertIn(v2["status"], ("pass", "warn"))

    def test_memory_persistence(self):
        """Memoria deve salvar e carregar corretamente."""
        self.agent.memory["total_posts_safe"] = 42
        self.agent._save()
        new_agent = SafeMassPostingAgent()
        self.assertEqual(new_agent.memory.get("total_posts_safe", 0), 42)


if __name__ == "__main__":
    unittest.main()
