from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from campaign_autopilot.memory import MemoryStore
from campaign_autopilot.models import Campaign, Event


class TestMemoryStore(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._db_path = Path(self._tmp.name)
        self.store = MemoryStore(self._db_path)

    def tearDown(self) -> None:
        self.store.close()
        self._db_path.unlink(missing_ok=True)

    def test_upsert_and_get_campaign(self) -> None:
        c = Campaign(campaign_id="cmp_test", name="Test", budget=100.0, opt_in=True)
        self.store.upsert_campaign(c)
        retrieved = self.store.get_campaign("cmp_test")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.campaign_id, "cmp_test")
        self.assertEqual(retrieved.name, "Test")
        self.assertEqual(retrieved.budget, 100.0)
        self.assertTrue(retrieved.opt_in)

    def test_get_campaign_nonexistent(self) -> None:
        retrieved = self.store.get_campaign("nonexistent")
        self.assertIsNone(retrieved)

    def test_upsert_campaign_updates_existing(self) -> None:
        c1 = Campaign(campaign_id="cmp_upd", name="Original", budget=50.0)
        self.store.upsert_campaign(c1)
        c2 = Campaign(campaign_id="cmp_upd", name="Updated", budget=200.0)
        self.store.upsert_campaign(c2)

        retrieved = self.store.get_campaign("cmp_upd")
        self.assertEqual(retrieved.name, "Updated")
        self.assertEqual(retrieved.budget, 200.0)

    def test_list_campaigns(self) -> None:
        c1 = Campaign(campaign_id="cmp_a", name="A")
        c2 = Campaign(campaign_id="cmp_b", name="B")
        self.store.upsert_campaign(c1)
        self.store.upsert_campaign(c2)

        campaigns = self.store.list_campaigns()
        self.assertEqual(len(campaigns), 2)
        self.assertEqual(campaigns[0].campaign_id, "cmp_a")
        self.assertEqual(campaigns[1].campaign_id, "cmp_b")

    def test_record_and_list_events(self) -> None:
        now = datetime.now(timezone.utc)
        events = [
            Event(
                event_id="evt_1",
                campaign_id="cmp_evt",
                kind="impression",
                occurred_at=now,
                value=10.0,
                count=100,
            ),
            Event(
                event_id="evt_2",
                campaign_id="cmp_evt",
                kind="click",
                occurred_at=now,
                value=5.0,
                count=20,
            ),
        ]
        self.store.record_events(events)

        stored = self.store.list_events("cmp_evt")
        self.assertEqual(len(stored), 2)
        self.assertEqual(stored[0].kind, "impression")
        self.assertEqual(stored[1].kind, "click")

    def test_list_events_by_campaign(self) -> None:
        now = datetime.now(timezone.utc)
        events_a = [
            Event(
                event_id="evt_a1",
                campaign_id="cmp_a",
                kind="impression",
                occurred_at=now,
            ),
            Event(
                event_id="evt_a2", campaign_id="cmp_a", kind="click", occurred_at=now
            ),
        ]
        events_b = [
            Event(
                event_id="evt_b1",
                campaign_id="cmp_b",
                kind="conversion",
                occurred_at=now,
            ),
        ]
        self.store.record_events(events_a)
        self.store.record_events(events_b)

        stored_a = self.store.list_events("cmp_a")
        self.assertEqual(len(stored_a), 2)
        stored_b = self.store.list_events("cmp_b")
        self.assertEqual(len(stored_b), 1)

    def test_list_all_events(self) -> None:
        now = datetime.now(timezone.utc)
        events = [
            Event(
                event_id="evt_all1",
                campaign_id="cmp_x",
                kind="impression",
                occurred_at=now,
            ),
            Event(
                event_id="evt_all2", campaign_id="cmp_y", kind="click", occurred_at=now
            ),
        ]
        self.store.record_events(events)

        all_events = self.store.list_events()
        self.assertGreaterEqual(len(all_events), 2)

    def test_record_events_updates_existing(self) -> None:
        now = datetime.now(timezone.utc)
        e1 = Event(
            event_id="evt_upd",
            campaign_id="cmp_upd",
            kind="impression",
            occurred_at=now,
            count=100,
        )
        self.store.record_events([e1])

        e2 = Event(
            event_id="evt_upd",
            campaign_id="cmp_upd",
            kind="impression",
            occurred_at=now,
            count=200,
        )
        self.store.record_events([e2])

        stored = self.store.list_events("cmp_upd")
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].count, 200)

    def test_stable_event_id_consistency(self) -> None:
        payload = {"campaign_id": "cmp_1", "kind": "click", "value": 5.0, "count": 10}
        id1 = MemoryStore.stable_event_id(payload)
        id2 = MemoryStore.stable_event_id(payload)
        self.assertEqual(id1, id2)

    def test_stable_event_id_differentiates(self) -> None:
        payload_a = {"campaign_id": "cmp_1", "kind": "click", "value": 5.0}
        payload_b = {"campaign_id": "cmp_1", "kind": "impression", "value": 5.0}
        id_a = MemoryStore.stable_event_id(payload_a)
        id_b = MemoryStore.stable_event_id(payload_b)
        self.assertNotEqual(id_a, id_b)

    def test_context_manager(self) -> None:
        """MemoryStore should work as a context manager."""
        with MemoryStore(self._db_path) as store:
            c = Campaign(campaign_id="cmp_ctx", name="Context test")
            store.upsert_campaign(c)
            retrieved = store.get_campaign("cmp_ctx")
            self.assertIsNotNone(retrieved)

        # After exiting context, store should be closed
        with self.assertRaises(Exception):
            store.get_campaign("cmp_ctx")

    def test_empty_campaign_list(self) -> None:
        campaigns = self.store.list_campaigns()
        self.assertEqual(campaigns, [])
