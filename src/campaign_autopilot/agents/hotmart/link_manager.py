"""HotmartLinkManagerAgent — Gerencia a colecao de links de afiliado Hotmart.

Armazena links em SQLite, organiza por nicho, evita duplicatas.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("hotmart_links")


class HotmartLinkStore:
    """SQLite store for Hotmart affiliate links."""

    def __init__(self, db_path: str | Path = ".state/hotmart_links.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS hotmart_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    product_url TEXT NOT NULL,
                    network TEXT DEFAULT 'hotmart',
                    commission_value REAL DEFAULT 50.0,
                    commission_type TEXT DEFAULT 'percentage',
                    keywords TEXT DEFAULT '[]',
                    cookie_days INTEGER DEFAULT 30,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_used TEXT,
                    clicks INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0.0,
                    UNIQUE(product_url, niche)
                );
            """)
            conn.commit()

    def add_link(
        self,
        niche: str,
        product_name: str,
        product_url: str,
        keywords: list[str] | None = None,
        commission: float = 50.0,
    ) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        kw_json = json.dumps(keywords or self._suggest_keywords(product_name))
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO hotmart_links
                       (niche, product_name, product_url, commission_value, keywords, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (niche, product_name, product_url, commission, kw_json, now, now),
                )
                conn.commit()
                return True
            except Exception as e:
                log.error("add_link_failed", error=str(e)[:100])
                return False

    def get_links(
        self, niche: str | None = None, active_only: bool = True
    ) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            if niche:
                rows = conn.execute(
                    "SELECT niche, product_name, product_url, commission_value, keywords, "
                    "clicks, conversions, revenue, created_at FROM hotmart_links "
                    "WHERE niche=? AND (is_active=? OR NOT ?) ORDER BY created_at DESC",
                    (niche, 1, active_only),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT niche, product_name, product_url, commission_value, keywords, "
                    "clicks, conversions, revenue, created_at FROM hotmart_links "
                    "WHERE is_active=? OR NOT ? ORDER BY niche, created_at DESC",
                    (1, active_only),
                ).fetchall()
            return [
                {
                    "niche": r[0],
                    "product_name": r[1],
                    "product_url": r[2],
                    "commission_value": r[3],
                    "keywords": json.loads(r[4]),
                    "clicks": r[5],
                    "conversions": r[6],
                    "revenue": r[7],
                    "created_at": r[8],
                }
                for r in rows
            ]

    def get_status(self) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            rows = conn.execute(
                "SELECT niche, COUNT(*) as count, SUM(clicks) as total_clicks, "
                "SUM(conversions) as total_conversions, SUM(revenue) as total_revenue "
                "FROM hotmart_links WHERE is_active=1 GROUP BY niche"
            ).fetchall()
            return [
                {
                    "niche": r[0],
                    "count": r[1],
                    "clicks": r[2] or 0,
                    "conversions": r[3] or 0,
                    "revenue": r[4] or 0.0,
                }
                for r in rows
            ]

    def mark_used(self, product_url: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "UPDATE hotmart_links SET last_used=?, clicks=clicks+1 WHERE product_url=?",
                (now, product_url),
            )
            conn.commit()

    def _suggest_keywords(self, product_name: str) -> list[str]:
        words = product_name.lower().replace(":", "").replace(",", "").split()
        return [w for w in words if len(w) > 2][:8]


class HotmartLinkManagerAgent(AgentBase):
    """Gerencia a colecao de links Hotmart: adicionar, listar, status."""

    def __init__(self, **kwargs) -> None:
        super().__init__("hotmart_link_manager", **kwargs)
        self.store = HotmartLinkStore()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "add")

            if action == "status":
                return self._handle_status(started_at)
            elif action == "list":
                return self._handle_list(campaign, started_at)
            else:
                return self._handle_add(campaign, started_at)

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            error_trace = AgentTrace(
                agent=self.name,
                step_id="manage",
                status="error",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                error=str(e)[:500],
            )
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=error_trace,
            )

    def _handle_add(self, campaign: dict, started_at: str) -> AgentResult:
        niche = campaign.get("niche", "")
        name = campaign.get("product_name", "")
        url = campaign.get("product_url", "")
        keywords = campaign.get("keywords", [])
        commission = campaign.get("commission_value", 50.0)

        if not name or not url:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": "product_name e product_url obrigatorios"},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="manage",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        success = self.store.add_link(niche, name, url, keywords, commission)
        statuses = self.store.get_status()

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="add_link",
            status="success" if success else "error",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[
                f"added: {name}",
                f"niche: {niche}",
                f"status: {'OK' if success else 'FAIL'}",
            ],
        )
        return AgentResult(
            agent=self.name,
            status="success" if success else "error",
            output={
                "added": success,
                "product_name": name,
                "niche": niche,
                "collection_status": statuses,
            },
            trace=trace,
        )

    def _handle_status(self, started_at: str) -> AgentResult:
        statuses = self.store.get_status()
        links = self.store.get_links()
        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="status",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"total: {len(links)} links"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={"collection_status": statuses, "total_links": len(links)},
            trace=trace,
        )

    def _handle_list(self, campaign: dict, started_at: str) -> AgentResult:
        niche = campaign.get("niche")
        links = self.store.get_links(niche)
        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="list",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(links)} links in {niche or 'all niches'}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={"links": links, "count": len(links)},
            trace=trace,
        )
