from __future__ import annotations

import unittest
from datetime import datetime, timezone

from campaign_autopilot.models import Campaign, Event, Metrics, Decision, Policy


class TestCampaign(unittest.TestCase):
    def test_default_construction(self) -> None:
        c = Campaign(campaign_id="cmp_1")
        self.assertEqual(c.campaign_id, "cmp_1")
        self.assertEqual(c.name, "")
        self.assertEqual(c.status, "active")
        self.assertFalse(c.opt_in)
        self.assertTrue(c.compliance_ok)
        self.assertEqual(c.budget, 0.0)

    def test_to_dict_roundtrip(self) -> None:
        c = Campaign(
            campaign_id="cmp_2",
            name="Test Campaign",
            status="paused",
            budget=500.0,
            spend=120.0,
            revenue=300.0,
            target_cpa=25.0,
            target_roas=2.0,
            opt_in=True,
            compliance_ok=True,
            compliance_notes="Reviewed and approved",
        )
        d = c.to_dict()
        self.assertIn("campaign_id", d)
        self.assertIn("updated_at", d)
        self.assertIsInstance(d["updated_at"], str)

        restored = Campaign.from_dict(d)
        self.assertEqual(restored.campaign_id, "cmp_2")
        self.assertEqual(restored.name, "Test Campaign")
        self.assertEqual(restored.status, "paused")
        self.assertEqual(restored.budget, 500.0)
        self.assertEqual(restored.spend, 120.0)
        self.assertEqual(restored.target_cpa, 25.0)
        self.assertTrue(restored.opt_in)

    def test_from_dict_filters_unknown_fields(self) -> None:
        payload = {
            "campaign_id": "cmp_3",
            "name": "Filtered",
            "unknown_field": "should be ignored",
            "budget": "not a float but still set",
        }
        c = Campaign.from_dict(payload)
        self.assertEqual(c.campaign_id, "cmp_3")
        # unknown_field should be filtered out
        self.assertFalse(hasattr(c, "unknown_field"))

    def test_to_dict_includes_updated_at(self) -> None:
        c = Campaign(campaign_id="cmp_4")
        d = c.to_dict()
        self.assertIn("updated_at", d)
        # Should be ISO format
        parsed = datetime.fromisoformat(d["updated_at"])
        self.assertIsNotNone(parsed)

    def test_from_dict_parses_updated_at(self) -> None:
        now = datetime.now(timezone.utc)
        payload = {"campaign_id": "cmp_5", "updated_at": now.isoformat()}
        c = Campaign.from_dict(payload)
        self.assertEqual(c.updated_at.isoformat(), now.isoformat())


class TestEvent(unittest.TestCase):
    def test_default_construction(self) -> None:
        now = datetime.now(timezone.utc)
        e = Event(
            event_id="evt_1",
            campaign_id="cmp_1",
            kind="impression",
            occurred_at=now,
        )
        self.assertEqual(e.value, 0.0)
        self.assertEqual(e.count, 1)
        self.assertEqual(e.metadata, {})

    def test_to_dict_roundtrip(self) -> None:
        now = datetime.now(timezone.utc)
        e = Event(
            event_id="evt_2",
            campaign_id="cmp_1",
            kind="conversion",
            occurred_at=now,
            value=100.0,
            count=5,
            metadata={"spend": 25.0, "source": "email"},
        )
        d = e.to_dict()
        self.assertEqual(d["event_id"], "evt_2")
        self.assertEqual(d["value"], 100.0)
        self.assertEqual(d["count"], 5)
        self.assertIn("occurred_at", d)

        restored = Event.from_dict(d)
        self.assertEqual(restored.event_id, "evt_2")
        self.assertEqual(restored.value, 100.0)
        self.assertEqual(restored.count, 5)
        self.assertEqual(restored.metadata, {"spend": 25.0, "source": "email"})

    def test_from_dict_defaults(self) -> None:
        payload = {
            "event_id": "evt_3",
            "campaign_id": "cmp_1",
            "kind": "click",
            "occurred_at": "2026-06-19T00:00:00Z",
        }
        e = Event.from_dict(payload)
        self.assertEqual(e.value, 0.0)
        self.assertEqual(e.count, 1)
        self.assertEqual(e.metadata, {})

    def test_occurred_at_timezone_handling(self) -> None:
        """Events with and without timezone should both parse correctly."""
        payload_with_tz = {
            "event_id": "evt_4",
            "campaign_id": "cmp_1",
            "kind": "impression",
            "occurred_at": "2026-06-19T12:00:00+00:00",
        }
        payload_z = {
            "event_id": "evt_5",
            "campaign_id": "cmp_1",
            "kind": "impression",
            "occurred_at": "2026-06-19T12:00:00Z",
        }
        e1 = Event.from_dict(payload_with_tz)
        e2 = Event.from_dict(payload_z)
        self.assertEqual(e1.occurred_at.isoformat(), e2.occurred_at.isoformat())


class TestMetrics(unittest.TestCase):
    def test_default_construction(self) -> None:
        m = Metrics()
        self.assertEqual(m.impressions, 0)
        self.assertEqual(m.clicks, 0)
        self.assertEqual(m.conversions, 0)
        self.assertEqual(m.spend, 0.0)
        self.assertEqual(m.anomaly_flags, [])
        self.assertIsNone(m.cpa)
        self.assertIsNone(m.roas)

    def test_to_dict_roundtrip(self) -> None:
        m = Metrics(
            impressions=1000,
            clicks=50,
            conversions=5,
            spend=250.0,
            revenue=750.0,
            ctr=0.05,
            cvr=0.10,
            cpa=50.0,
            roas=3.0,
            anomaly_flags=["low_ctr"],
        )
        d = m.to_dict()
        self.assertEqual(d["impressions"], 1000)
        self.assertEqual(d["clicks"], 50)
        self.assertEqual(d["cpa"], 50.0)
        self.assertEqual(d["anomaly_flags"], ["low_ctr"])

    def test_to_dict_rounds_floats(self) -> None:
        m = Metrics(spend=1.23456789, revenue=9.87654321)
        d = m.to_dict()
        self.assertEqual(d["spend"], 1.234568)
        self.assertEqual(d["revenue"], 9.876543)


class TestDecision(unittest.TestCase):
    def test_construction(self) -> None:
        d = Decision(
            action="scale_budget",
            campaign_id="cmp_1",
            reason="All thresholds met",
            parameters={"new_budget": 1150},
            confidence=0.82,
            requires_review=False,
        )
        self.assertEqual(d.action, "scale_budget")
        self.assertEqual(d.confidence, 0.82)

    def test_to_dict(self) -> None:
        d = Decision(
            action="pause",
            campaign_id="cmp_1",
            reason="High CPA",
            confidence=0.9,
            requires_review=True,
        )
        result = d.to_dict()
        self.assertEqual(result["action"], "pause")
        self.assertTrue(result["requires_review"])
        self.assertIn("parameters", result)


class TestPolicy(unittest.TestCase):
    def test_default_construction(self) -> None:
        p = Policy()
        self.assertTrue(p.opt_in_required)
        self.assertEqual(p.name, "default")
        self.assertEqual(p.min_impressions, 100)

    def test_to_dict(self) -> None:
        p = Policy()
        d = p.to_dict()
        self.assertIn("opt_in_required", d)
        self.assertIn("min_impressions", d)

    def test_from_dict_roundtrip(self) -> None:
        payload = {
            "name": "strict",
            "opt_in_required": True,
            "min_impressions": 500,
            "min_clicks": 50,
            "pause_cpa_multiplier": 2.0,
        }
        p = Policy.from_dict(payload)
        self.assertEqual(p.name, "strict")
        self.assertEqual(p.min_impressions, 500)
        self.assertEqual(p.pause_cpa_multiplier, 2.0)
        # Unset fields keep defaults
        self.assertEqual(p.min_conversions, 3)

    def test_from_dict_filters_unknown(self) -> None:
        payload = {"name": "test", "unknown_field": "should be ignored"}
        p = Policy.from_dict(payload)
        self.assertEqual(p.name, "test")
        self.assertFalse(hasattr(p, "unknown_field"))
