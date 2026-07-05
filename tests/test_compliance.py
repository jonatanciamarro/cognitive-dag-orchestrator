"""Tests for ComplianceAgent."""

from __future__ import annotations
import unittest
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.compliance import ComplianceAgent


class TestComplianceAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ComplianceAgent()

    def test_instantiation(self):
        self.assertEqual(self.agent.name, "compliance")

    def test_run_clean_content(self):
        ctx = CampaignContext(
            campaign={
                "headline": "Curso de Marketing Digital",
                "description": "Aprenda marketing digital do zero",
                "budget": 100,
            }
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["status"], "pass")

    def test_run_blocked_content(self):
        ctx = CampaignContext(
            campaign={
                "headline": "Ganhe dinheiro rápido",
                "copy": "Resultados garantidos",
                "budget": 100,
            },
            policy={"restricted_terms": ["garantido", "dinheiro rápido"]},
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["status"], "block")
        self.assertGreater(len(result.output.get("violations", [])), 0)

    def test_run_warn_content(self):
        ctx = CampaignContext(
            campaign={"headline": "Curso incrível de marketing", "budget": 100},
            policy={"restricted_terms": ["incrível"]},
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn(result.output["status"], ("warn", "block"))

    def test_run_missing_disclosure(self):
        ctx = CampaignContext(
            campaign={"headline": "Melhor curso de afiliados", "budget": 100},
            policy={"required_disclosures": ["publicidade", "afiliado"]},
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertIn("violations", result.output)

    def test_run_with_disclosure_present(self):
        ctx = CampaignContext(
            campaign={
                "headline": "Curso de afiliados",
                "copy": "Este conteúdo contém links de afiliado",
                "budget": 100,
            },
            policy={"required_disclosures": ["afiliado"]},
        )
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["status"], "pass")

    def test_run_zero_budget_blocks(self):
        ctx = CampaignContext(campaign={"headline": "Curso", "budget": 0})
        result = self.agent.run(ctx)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["status"], "block")


if __name__ == "__main__":
    unittest.main()
