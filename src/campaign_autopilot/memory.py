from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import Campaign, Event


class MemoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(
            self.path, check_same_thread=False, isolation_level=None
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._ensure_schema()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "MemoryStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def _ensure_schema(self) -> None:
        # Schema creation uses individual execute calls with autocommit
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                campaign_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                kind TEXT NOT NULL,
                value REAL NOT NULL,
                count INTEGER NOT NULL,
                metadata TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_campaign_time ON events(campaign_id, occurred_at)"
        )

    def upsert_campaign(self, campaign: Campaign) -> None:
        payload = json.dumps(campaign.to_dict(), sort_keys=True)
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO campaigns (campaign_id, payload)
                VALUES (?, ?)
                ON CONFLICT(campaign_id) DO UPDATE SET payload = excluded.payload
                """,
                (campaign.campaign_id, payload),
            )

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        row = self._conn.execute(
            "SELECT payload FROM campaigns WHERE campaign_id = ?",
            (campaign_id,),
        ).fetchone()
        if row is None:
            return None
        return Campaign.from_dict(json.loads(row["payload"]))

    def list_campaigns(self) -> list[Campaign]:
        rows = self._conn.execute(
            "SELECT payload FROM campaigns ORDER BY campaign_id"
        ).fetchall()
        return [Campaign.from_dict(json.loads(row["payload"])) for row in rows]

    def record_events(self, events: list[Event]) -> None:
        with self.transaction() as conn:
            for event in events:
                payload = json.dumps(event.to_dict(), sort_keys=True)
                conn.execute(
                    """
                    INSERT INTO events (
                        event_id, campaign_id, occurred_at, kind, value, count, metadata, payload
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(event_id) DO UPDATE SET
                        campaign_id = excluded.campaign_id,
                        occurred_at = excluded.occurred_at,
                        kind = excluded.kind,
                        value = excluded.value,
                        count = excluded.count,
                        metadata = excluded.metadata,
                        payload = excluded.payload
                    """,
                    (
                        event.event_id,
                        event.campaign_id,
                        event.occurred_at.isoformat(),
                        event.kind,
                        event.value,
                        event.count,
                        json.dumps(event.metadata, sort_keys=True),
                        payload,
                    ),
                )

    def list_events(self, campaign_id: str | None = None) -> list[Event]:
        if campaign_id is None:
            rows = self._conn.execute(
                "SELECT payload FROM events ORDER BY occurred_at, event_id"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT payload FROM events WHERE campaign_id = ? ORDER BY occurred_at, event_id",
                (campaign_id,),
            ).fetchall()
        return [Event.from_dict(json.loads(row["payload"])) for row in rows]

    @staticmethod
    def stable_event_id(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
