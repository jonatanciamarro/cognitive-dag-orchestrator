"""UI Design Memory — Rastreia componentes UI gerados e seu desempenho.

Armazena histórico de designs, variantes, scores de qualidade
e metadados para aprendizado e reuso.
Ponytail: stdlib-only, SQLite WAL.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class UIDesignRecord:
    """A recorded UI design artifact."""

    design_id: str
    design_type: str  # hero, pricing, faq, testimonial, full_page
    niche: str
    component_name: str
    variant: str
    quality_score: float
    html_size_chars: int
    css_size_chars: int
    js_size_chars: int
    sections_count: int
    approved: bool
    timestamp: float
    metadata: str = ""  # JSON string

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class UIDesignMemory:
    """Persistent store for UI design artifacts and their quality scores.

    Usa SQLite WAL para operações thread-safe.
    Permite consultar designs por tipo, nicho, score mínimo.
    """

    def __init__(self, db_path: str | Path = ".state/ui_design_memory.db"):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ui_designs (
                    design_id TEXT PRIMARY KEY,
                    design_type TEXT NOT NULL,
                    niche TEXT NOT NULL,
                    component_name TEXT NOT NULL,
                    variant TEXT DEFAULT 'default',
                    quality_score REAL DEFAULT 0.0,
                    html_size_chars INTEGER DEFAULT 0,
                    css_size_chars INTEGER DEFAULT 0,
                    js_size_chars INTEGER DEFAULT 0,
                    sections_count INTEGER DEFAULT 0,
                    approved INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ui_designs_type
                ON ui_designs(design_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ui_designs_niche
                ON ui_designs(niche)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ui_designs_score
                ON ui_designs(quality_score)
            """)
            conn.commit()
            conn.close()

    def record(self, design: UIDesignRecord) -> None:
        """Record a UI design artifact."""
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conn.execute(
                """INSERT OR REPLACE INTO ui_designs
                   (design_id, design_type, niche, component_name, variant,
                    quality_score, html_size_chars, css_size_chars, js_size_chars,
                    sections_count, approved, timestamp, metadata)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    design.design_id,
                    design.design_type,
                    design.niche,
                    design.component_name,
                    design.variant,
                    design.quality_score,
                    design.html_size_chars,
                    design.css_size_chars,
                    design.js_size_chars,
                    design.sections_count,
                    1 if design.approved else 0,
                    design.timestamp,
                    design.metadata,
                ),
            )
            conn.commit()
            conn.close()

    def query(
        self,
        design_type: str | None = None,
        niche: str | None = None,
        min_score: float = 0.0,
        approved_only: bool = False,
        limit: int = 20,
    ) -> list[UIDesignRecord]:
        """Query design records with filters."""
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            conditions = []
            params = []
            if design_type:
                conditions.append("design_type = ?")
                params.append(design_type)
            if niche:
                conditions.append("niche = ?")
                params.append(niche)
            if min_score > 0:
                conditions.append("quality_score >= ?")
                params.append(min_score)
            if approved_only:
                conditions.append("approved = 1")

            where = " AND ".join(conditions) if conditions else "1=1"
            rows = conn.execute(
                f"SELECT * FROM ui_designs WHERE {where} ORDER BY timestamp DESC LIMIT ?",
                params + [limit],
            ).fetchall()
            conn.close()

            return [
                UIDesignRecord(
                    design_id=r[0],
                    design_type=r[1],
                    niche=r[2],
                    component_name=r[3],
                    variant=r[4],
                    quality_score=r[5],
                    html_size_chars=r[6],
                    css_size_chars=r[7],
                    js_size_chars=r[8],
                    sections_count=r[9],
                    approved=bool(r[10]),
                    timestamp=r[11],
                    metadata=r[12],
                )
                for r in rows
            ]

    def best_designs(
        self, design_type: str, niche: str, top_n: int = 3
    ) -> list[UIDesignRecord]:
        """Get top-scoring approved designs for a type and niche."""
        return self.query(
            design_type=design_type,
            niche=niche,
            min_score=85.0,
            approved_only=True,
            limit=top_n,
        )

    def stats(self) -> dict[str, Any]:
        """Get aggregate statistics."""
        with self._lock:
            conn = sqlite3.connect(str(self._db_path))
            total = conn.execute("SELECT COUNT(*) FROM ui_designs").fetchone()[0]
            approved = conn.execute(
                "SELECT COUNT(*) FROM ui_designs WHERE approved=1"
            ).fetchone()[0]
            avg_score = (
                conn.execute("SELECT AVG(quality_score) FROM ui_designs").fetchone()[0]
                or 0.0
            )
            by_type = dict(
                conn.execute(
                    "SELECT design_type, COUNT(*) FROM ui_designs GROUP BY design_type"
                ).fetchall()
            )
            conn.close()
            return {
                "total_designs": total,
                "approved_designs": approved,
                "avg_quality_score": round(avg_score, 1),
                "by_type": by_type,
            }
