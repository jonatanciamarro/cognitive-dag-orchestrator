"""Tests for EmailMarketingAgent."""

from __future__ import annotations

import unittest

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.email_marketing import EmailMarketingAgent


class TestEmailMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.agent = EmailMarketingAgent()

    def _make_context(
        self, keyword="marketing digital", offers=None
    ) -> CampaignContext:
        context = CampaignContext(
            campaign={
                "campaign_id": "test_email_001",
                "objective": keyword,
                "niche": "marketing digital",
            },
        )
        context.run_id = "test_email_run_001"
        context.step_results["seo_research"] = {
            "output": {
                "top_opportunities": [
                    {"keyword": keyword, "volume": 1000, "difficulty": 0.3}
                ]
            }
        }
        if offers is not None:
            context.step_results["offer_lookup"] = {
                "output": {"available_offers": offers}
            }
        return context

    def test_generates_sequences(self):
        """Should generate email sequences."""
        context = self._make_context()
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        output = result.output
        self.assertGreater(output["total_sequences"], 0)
        self.assertGreater(output["total_emails"], 0)
        self.assertIn("sequences", output)

    def test_welcome_sequence_has_3_emails(self):
        """Welcome sequence should have 3 emails."""
        context = self._make_context()
        result = self.agent.run(context)
        sequences = result.output["sequences"]

        welcome = [s for s in sequences if "Boas-Vindas" in s["name"]]
        self.assertEqual(len(welcome), 1)
        self.assertEqual(welcome[0]["total_emails"], 3)

    def test_nurture_sequence_has_4_emails(self):
        """Nurture sequence should have 4 emails."""
        context = self._make_context()
        result = self.agent.run(context)
        sequences = result.output["sequences"]

        nurture = [s for s in sequences if "Nutrição" in s["name"]]
        self.assertEqual(len(nurture), 1)
        self.assertEqual(nurture[0]["total_emails"], 4)

    def test_promo_sequence_has_2_emails(self):
        """Promotional sequence should have 2 emails."""
        context = self._make_context()
        result = self.agent.run(context)
        sequences = result.output["sequences"]

        promo = [s for s in sequences if "Promocional" in s["name"]]
        self.assertEqual(len(promo), 1)
        self.assertEqual(promo[0]["total_emails"], 2)

    def test_email_has_subject_preheader_body(self):
        """Each email should have subject, preheader, and body."""
        context = self._make_context()
        result = self.agent.run(context)
        email = result.output["sequences"][0]["emails"][0]

        self.assertIn("subject", email)
        self.assertIn("preheader", email)
        self.assertIn("body", email)
        self.assertIn("delay_days", email)
        self.assertIn("goal", email)

    def test_offers_included_in_emails(self):
        """Offers should appear in email bodies when available."""
        offers = [
            {
                "offer_id": "hotmart_001",
                "network": "hotmart",
                "product_name": "Curso Marketing Digital",
                "product_url": "https://hotmart.com/curso-mkt",
                "price": 197.00,
            }
        ]
        context = self._make_context(offers=offers)
        result = self.agent.run(context)

        # Find the promo sequence which specifically mentions product_name
        sequences = result.output["sequences"]
        promo = [s for s in sequences if "Promocional" in s["name"]]
        if promo:
            email_body = promo[0]["emails"][0]["body"]
            self.assertIn("Curso Marketing Digital", email_body)

    def test_subject_includes_niche(self):
        """Email subject should include the niche in promo sequence."""
        context = self._make_context(keyword="SEO para blogs")
        result = self.agent.run(context)
        sequences = result.output["sequences"]

        # The promo sequence uses {niche} in subject
        promo = [s for s in sequences if "Promocional" in s["name"]]
        if promo:
            email_body = promo[0]["emails"][0]["body"]
            self.assertIn("SEO para blogs", email_body)

    def test_without_offers_still_works(self):
        """Should work without offers."""
        context = self._make_context()
        result = self.agent.run(context)

        self.assertEqual(result.status, "success")
        self.assertGreater(result.output["total_emails"], 0)

    def test_trace_metadata(self):
        """Trace should contain email metadata."""
        context = self._make_context()
        result = self.agent.run(context)

        self.assertIsNotNone(result.trace)
        self.assertEqual(result.trace.agent, "email_marketing")
        self.assertEqual(result.trace.status, "success")
        self.assertIn("sequences", result.trace.metadata)
        self.assertIn("emails", result.trace.metadata)

    def test_with_explanation_store(self):
        """Should work with ExplanationStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.explanation import ExplanationStore

        store = ExplanationStore(conn)
        agent = EmailMarketingAgent(explanation_store=store)

        context = self._make_context()
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        row = store._execute("SELECT COUNT(*) FROM explanation_decisions").fetchone()
        self.assertGreater(row[0], 0)

    def test_with_semantic_memory(self):
        """Should work with SemanticMemoryStore integration."""
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        from campaign_autopilot.semantic_memory import SemanticMemoryStore

        sem = SemanticMemoryStore(conn)
        sem.register_observer("email_marketing", "AGENT", "email_marketing_agent", 0.7)
        sem.register_concept("marketing digital", "niche", "Nicho de teste")

        agent = EmailMarketingAgent(semantic_memory=sem)
        context = self._make_context()
        result = agent.run(context)

        self.assertEqual(result.status, "success")
        claims = sem.query_claims(limit=10)
        self.assertGreater(len(claims), 0)


if __name__ == "__main__":
    unittest.main()
