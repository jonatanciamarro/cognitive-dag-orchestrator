from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.orchestrator import CampaignOrchestrator
from campaign_autopilot.memory import MemoryStore
from campaign_autopilot.affiliate import OfferManager, AffiliateOffer


ROOT = Path(__file__).resolve().parents[1]
AFFILIATE_WORKFLOW = ROOT / "workflows" / "organic_affiliate_cycle.json"
AFFILIATE_CONTEXT = ROOT / "examples" / "affiliate_context.json"


class TestAffiliateIntegration(unittest.TestCase):
    """Testa o ciclo completo de afiliados orgânicos com cognitive stores."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._db_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._db_path.unlink(missing_ok=True)

    def test_full_affiliate_cycle(self) -> None:
        """Executa o workflow completo de afiliados e verifica todos os steps."""
        payload = json.loads(AFFILIATE_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            orchestrator = CampaignOrchestrator(
                workflow_path=AFFILIATE_WORKFLOW,
                memory_store=store,
            )
            result = orchestrator.run(CampaignContext.from_mapping(payload))

        self.assertEqual(result.status, "success")
        wr = result.output
        self.assertEqual(
            set(wr["step_results"].keys()),
            {
                "seo_research",
                "ui_design",
                "compliance",
                "memory_lookup",
                "offer_lookup",
                "content_planner",
                "publisher",
            },
        )

        # Verificar outputs de cada agente
        sr = wr["step_results"]
        self.assertGreater(sr["seo_research"]["output"]["total_keywords_found"], 0)
        self.assertGreater(sr["seo_research"]["output"]["opportunities_count"], 0)

        self.assertEqual(sr["compliance"]["output"]["status"], "pass")

        # Offers podem ser 0 ou mais (depende do match)
        self.assertGreaterEqual(sr["offer_lookup"]["output"]["total_offers_found"], 1)

        self.assertGreater(sr["content_planner"]["output"]["total_briefs"], 0)

        pub = sr["publisher"]["output"]
        self.assertGreater(pub["total_scheduled"], 0)
        self.assertFalse(pub["blocked"])
        self.assertGreater(pub["estimated_monthly_clicks_organic"], 0)

    def test_affiliate_cycle_with_offer_manager(self) -> None:
        """Verifica que o OfferManager pode coexistir com o workflow."""
        payload = json.loads(AFFILIATE_CONTEXT.read_text(encoding="utf-8"))
        with MemoryStore(self._db_path) as store:
            # Pré-registrar ofertas
            om = OfferManager(store._conn)
            om.register_offer(
                AffiliateOffer(
                    offer_id="int_test_001",
                    network="hotmart",
                    product_name="Curso Integração Teste",
                    product_url="https://hotmart.com/integration-test",
                    commission_type="percentage",
                    commission_value=60.0,
                    category="marketing digital",
                )
            )

            orchestrator = CampaignOrchestrator(
                workflow_path=AFFILIATE_WORKFLOW,
                memory_store=store,
            )
            result = orchestrator.run(CampaignContext.from_mapping(payload))
            self.assertEqual(result.status, "success")

        # Verify data persisted by OfferManager
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute("SELECT COUNT(*) AS c FROM affiliate_offers").fetchall()
            self.assertGreaterEqual(rows[0]["c"], 1)
            rows2 = conn.execute("SELECT COUNT(*) AS c FROM content_briefs").fetchall()
            self.assertGreaterEqual(rows2[0]["c"], 0)
        finally:
            conn.close()
