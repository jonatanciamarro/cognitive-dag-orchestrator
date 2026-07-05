"""RevenueMemory — Unificado: armazena estado de TODAS as fontes de renda."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...logging_utils import StructuredLogger

log = StructuredLogger("revenue_memory")

REVENUE_SOURCES = [
    "hotmart",
    "monetizze",
    "kiwify",
    "eduzz",
    "mercadolivre",
    "shopee",
    "shein",
    "aliexpress",
    "adsense",
    "cpa",
    "digital_product",
    "membership",
    "email_marketing",
    "lead_capture",
    "traffic_recycling",
    "paid_traffic",
]


class RevenueMemory:
    """Memoria unificada de todas as fontes de renda."""

    def __init__(self, db_path: str | Path = ".state/revenue.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS revenue_sources (
                    source TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    config TEXT DEFAULT '{}',
                    total_revenue REAL DEFAULT 0.0,
                    total_clicks INTEGER DEFAULT 0,
                    total_conversions INTEGER DEFAULT 0,
                    last_active TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS revenue_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    amount REAL DEFAULT 0.0,
                    description TEXT,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS revenue_protocols (
                    source TEXT PRIMARY KEY,
                    protocol TEXT NOT NULL,
                    current_phase TEXT DEFAULT 'setup',
                    steps_completed TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.commit()
            self._ensure_sources()

    def _ensure_sources(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            for source in REVENUE_SOURCES:
                conn.execute(
                    "INSERT OR IGNORE INTO revenue_sources (source, status, created_at, updated_at) VALUES (?, 'pending', ?, ?)",
                    (source, now, now),
                )
            conn.commit()

    def get_status(self) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            rows = conn.execute(
                "SELECT source, status, total_revenue, total_clicks, total_conversions, last_active "
                "FROM revenue_sources ORDER BY source"
            ).fetchall()
            return [
                {
                    "source": r[0],
                    "status": r[1],
                    "revenue": r[2],
                    "clicks": r[3],
                    "conversions": r[4],
                    "last_active": r[5],
                }
                for r in rows
            ]

    def update_source(
        self,
        source: str,
        status: str | None = None,
        revenue: float | None = None,
        clicks: int | None = None,
        conversions: int | None = None,
        config: dict | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            updates = ["updated_at=?"]
            params = [now]
            if status:
                updates.append("status=?")
                params.append(status)
            if revenue is not None:
                updates.append("total_revenue=total_revenue+?")
                params.append(revenue)
            if clicks is not None:
                updates.append("total_clicks=total_clicks+?")
                params.append(clicks)
            if conversions is not None:
                updates.append("total_conversions=total_conversions+?")
                params.append(conversions)
            if config:
                updates.append("config=?")
                params.append(json.dumps(config))
            conn.execute(
                f"UPDATE revenue_sources SET {', '.join(updates)}, last_active=? WHERE source=?",
                params + [now, source],
            )
            conn.commit()

    def record_event(
        self,
        source: str,
        event_type: str,
        amount: float = 0.0,
        description: str = "",
        metadata: dict | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT INTO revenue_events (source, event_type, amount, description, metadata, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    source,
                    event_type,
                    amount,
                    description,
                    json.dumps(metadata or {}),
                    now,
                ),
            )
            conn.commit()

    def get_events(
        self, source: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            if source:
                rows = conn.execute(
                    "SELECT source, event_type, amount, description, created_at FROM revenue_events "
                    "WHERE source=? ORDER BY created_at DESC LIMIT ?",
                    (source, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT source, event_type, amount, description, created_at FROM revenue_events "
                    "ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [
                {
                    "source": r[0],
                    "type": r[1],
                    "amount": r[2],
                    "description": r[3],
                    "created_at": r[4],
                }
                for r in rows
            ]

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            total = (
                conn.execute(
                    "SELECT SUM(total_revenue) FROM revenue_sources"
                ).fetchone()[0]
                or 0
            )
            active = conn.execute(
                "SELECT COUNT(*) FROM revenue_sources WHERE status='active'"
            ).fetchone()[0]
            events = conn.execute("SELECT COUNT(*) FROM revenue_events").fetchone()[0]
            return {
                "total_revenue": round(total, 2),
                "active_sources": active,
                "total_sources": len(REVENUE_SOURCES),
                "total_events": events,
            }

    def save_protocol(self, source: str, protocol: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT OR REPLACE INTO revenue_protocols (source, protocol, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (source, json.dumps(protocol), now, now),
            )
            conn.commit()

    def get_protocol(self, source: str) -> dict | None:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            row = conn.execute(
                "SELECT protocol FROM revenue_protocols WHERE source=?", (source,)
            ).fetchone()
            return json.loads(row[0]) if row else None
