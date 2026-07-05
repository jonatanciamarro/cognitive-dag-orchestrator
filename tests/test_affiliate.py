from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.affiliate import (
    OfferManager,
    AffiliateOffer,
    AffiliateLink,
    ContentBrief,
    AmazonAssociates,
    Hotmart,
    GenericAffiliate,
)


class TestAffiliateModels(unittest.TestCase):
    def test_offer_roundtrip(self) -> None:
        offer = AffiliateOffer(
            offer_id="test_001",
            network="hotmart",
            product_name="Curso Teste",
            product_url="https://hotmart.com/product/test",
            commission_type="percentage",
            commission_value=50.0,
            category="marketing",
        )
        d = offer.to_dict()
        restored = AffiliateOffer.from_dict(d)
        self.assertEqual(restored.offer_id, "test_001")
        self.assertEqual(restored.commission_value, 50.0)

    def test_link_roundtrip(self) -> None:
        link = AffiliateLink(
            link_id="link_001",
            offer_id="offer_001",
            base_url="https://example.com/prod",
            tracked_url="https://example.com/prod?ref=test",
            source="blog",
            content_id="article_001",
        )
        d = link.to_dict()
        restored = AffiliateLink.from_dict(d)
        self.assertEqual(restored.link_id, "link_001")
        self.assertEqual(restored.clicks, 0)

    def test_content_brief_roundtrip(self) -> None:
        brief = ContentBrief(
            brief_id="brief_001",
            topic="Como ganhar dinheiro online",
            keyword="ganhar dinheiro online",
            content_type="article",
            offers=["offer_001"],
            outline=["Intro", "Passo 1", "Conclusão"],
        )
        d = brief.to_dict()
        restored = ContentBrief.from_dict(d)
        self.assertEqual(restored.brief_id, "brief_001")
        self.assertEqual(restored.status, "draft")


class TestAffiliateNetworks(unittest.TestCase):
    def test_amazon_link(self) -> None:
        amazon = AmazonAssociates(tracking_id="test-20")
        offer = AffiliateOffer(
            offer_id="amz_001",
            network="amazon",
            product_name="Livro Teste",
            product_url="https://www.amazon.com.br/dp/123456",
            commission_type="percentage",
            commission_value=10.0,
        )
        url = amazon.build_link(offer)
        self.assertIn("tag=test-20", url)

    def test_hotmart_link(self) -> None:
        hotmart = Hotmart(affiliate_id="ABC123")
        offer = AffiliateOffer(
            offer_id="hot_001",
            network="hotmart",
            product_name="Curso Teste",
            product_url="https://hotmart.com/product/test",
            commission_type="percentage",
            commission_value=50.0,
        )
        url = hotmart.build_link(offer)
        self.assertIn("aff=ABC123", url)

    def test_generic_link(self) -> None:
        generic = GenericAffiliate(name="testnet", param_name="ref")
        offer = AffiliateOffer(
            offer_id="gen_001",
            network="testnet",
            product_name="Produto Teste",
            product_url="https://example.com/prod",
            commission_type="fixed",
            commission_value=5.0,
        )
        url = generic.build_link(offer, ref="meu_id")
        self.assertIn("ref=meu_id", url)


class TestOfferManager(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.mgr = OfferManager(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_register_and_get_offer(self) -> None:
        offer = AffiliateOffer(
            offer_id="off_001",
            network="hotmart",
            product_name="Curso SEO",
            product_url="https://hotmart.com/seo",
            commission_type="percentage",
            commission_value=60.0,
        )
        self.mgr.register_offer(offer)
        retrieved = self.mgr.get_offer("off_001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.product_name, "Curso SEO")

    def test_register_offer_idempotent(self) -> None:
        offer = AffiliateOffer(
            offer_id="off_002",
            network="amazon",
            product_name="Produto",
            product_url="https://amazon.com/prod",
            commission_type="percentage",
            commission_value=5.0,
        )
        oid1 = self.mgr.register_offer(offer)
        oid2 = self.mgr.register_offer(offer)
        self.assertEqual(oid1, oid2)

    def test_list_offers_by_network(self) -> None:
        self.mgr.register_offer(
            AffiliateOffer(
                offer_id="a1",
                network="hotmart",
                product_name="H1",
                product_url="https://h.com/1",
                commission_type="percentage",
                commission_value=50,
            )
        )
        self.mgr.register_offer(
            AffiliateOffer(
                offer_id="a2",
                network="amazon",
                product_name="A1",
                product_url="https://a.com/1",
                commission_type="percentage",
                commission_value=3,
            )
        )
        hotmart_offers = self.mgr.list_offers(network="hotmart")
        self.assertEqual(len(hotmart_offers), 1)

    def test_create_and_track_link(self) -> None:
        offer = AffiliateOffer(
            offer_id="off_link",
            network="amazon",
            product_name="Test",
            product_url="https://amazon.com/test",
            commission_type="percentage",
            commission_value=5.0,
        )
        self.mgr.register_offer(offer)
        amazon = AmazonAssociates(tracking_id="test-20")
        link = self.mgr.create_link(
            offer,
            amazon,
            source="blog",
            content_id="art_001",
            campaign="test_camp",
            tag="test-20",
        )
        self.assertIn("tag=test-20", link.tracked_url)
        self.assertEqual(link.content_id, "art_001")

        # Track a click
        self.mgr.track_click(link.link_id, {"ip": "127.0.0.1"})
        links = self.mgr.get_links_for_content("art_001")
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].clicks, 1)

    def test_track_conversion(self) -> None:
        offer = AffiliateOffer(
            offer_id="off_conv",
            network="hotmart",
            product_name="Conv",
            product_url="https://h.com/conv",
            commission_type="percentage",
            commission_value=50.0,
        )
        self.mgr.register_offer(offer)
        hotmart = Hotmart(affiliate_id="ABC")
        link = self.mgr.create_link(offer, hotmart)
        self.mgr.track_conversion(link.link_id, revenue=50.0)
        links = self.mgr.get_links_for_content("")
        if links:
            self.assertEqual(links[0].conversions, 1)
            self.assertAlmostEqual(links[0].revenue, 50.0)

    def test_save_and_list_briefs(self) -> None:
        brief = ContentBrief(
            brief_id="brief_01",
            topic="SEO Basics",
            keyword="seo basics",
            content_type="article",
            offers=["off_001"],
            outline=["Intro", "Body", "End"],
        )
        self.mgr.save_brief(brief)
        briefs = self.mgr.list_briefs()
        self.assertEqual(len(briefs), 1)
        self.assertEqual(briefs[0].status, "draft")

    def test_affiliate_metrics(self) -> None:
        metrics = self.mgr.get_affiliate_metrics()
        self.assertIn("total_clicks", metrics)
        self.assertIn("total_revenue", metrics)
        self.assertIn("conversion_rate", metrics)

    def test_save_brief_updates_existing(self) -> None:
        brief = ContentBrief(
            brief_id="brief_upd",
            topic="Original",
            keyword="original",
            content_type="article",
        )
        self.mgr.save_brief(brief)
        brief.status = "approved"
        self.mgr.save_brief(brief)
        briefs = self.mgr.list_briefs(status="approved")
        self.assertEqual(len(briefs), 1)
