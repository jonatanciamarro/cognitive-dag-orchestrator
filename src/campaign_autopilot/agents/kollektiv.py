"""KollektivAgent — 4a Ordem: Inteligencia Coletiva Cross-Nicho.

Conecta todos os nichos em um barramento de conhecimento:
- Cada ciclo coleta resultados de TODOS os nichos
- Detecta padroes que funcionam em multiplos nichos
- Distribui estrategias vencedoras automaticamente
- Mantem um vault compartilhado de ontologias, ofertas e aprendizados

Sem este agente, cada nicho e uma ilha.
Com ele, o sistema e UM organismo que aprende em compounding.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ..logging_utils import StructuredLogger

log = StructuredLogger("kollektiv")


class CrossNicheVault:
    """Vault persistente de conhecimento cross-nicho."""

    def __init__(self, db_path: str | Path = ".state/kollektiv.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS niche_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche TEXT NOT NULL,
                    cycle_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    articles_generated INTEGER DEFAULT 0,
                    posts_generated INTEGER DEFAULT 0,
                    offers_used INTEGER DEFAULT 0,
                    revenue_estimated REAL DEFAULT 0,
                    seo_keywords_found INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    UNIQUE(niche, cycle_id)
                );
                CREATE TABLE IF NOT EXISTS winning_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche TEXT NOT NULL,
                    strategy_type TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    description TEXT,
                    success_score REAL DEFAULT 0,
                    times_tested INTEGER DEFAULT 0,
                    times_won INTEGER DEFAULT 0,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS cross_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    description TEXT,
                    source_niches TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    first_detected TEXT NOT NULL,
                    last_detected TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    UNIQUE(pattern_type, pattern_name)
                );
                CREATE TABLE IF NOT EXISTS shared_ontology (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    description TEXT,
                    related_concepts TEXT DEFAULT '[]',
                    applicable_niches TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.commit()

    def record_cycle(self, niche: str, cycle_id: str, data: dict) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                """INSERT OR REPLACE INTO niche_cycles
                   (niche, cycle_id, started_at, articles_generated, posts_generated,
                    offers_used, revenue_estimated, seo_keywords_found, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    niche,
                    cycle_id,
                    data.get("started_at", datetime.now(timezone.utc).isoformat()),
                    data.get("articles", 0),
                    data.get("posts", 0),
                    data.get("offers_used", 0),
                    data.get("revenue", 0),
                    data.get("seo_keywords", 0),
                    json.dumps(data.get("metadata", {})),
                ),
            )
            conn.commit()

    def detect_cross_patterns(self) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            rows = conn.execute(
                """SELECT strategy_type, strategy_name, COUNT(DISTINCT niche) as niche_count,
                          AVG(success_score) as avg_score, SUM(times_tested) as total_tested
                   FROM winning_strategies
                   WHERE times_tested > 0
                   GROUP BY strategy_type, strategy_name
                   HAVING niche_count > 1
                   ORDER BY avg_score DESC, total_tested DESC
                   LIMIT 20"""
            ).fetchall()
            return [
                {
                    "strategy_type": r[0],
                    "strategy_name": r[1],
                    "niche_count": r[2],
                    "avg_score": round(r[3], 3),
                    "total_tested": r[4],
                }
                for r in rows
            ]

    def get_cross_niche_recommendations(self, for_niche: str) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            rows = conn.execute(
                """SELECT ws.strategy_type, ws.strategy_name, ws.description,
                          ws.success_score, ws.niche as source_niche
                   FROM winning_strategies ws
                   WHERE ws.niche != ?
                     AND ws.success_score > 0.6
                     AND ws.times_tested >= 2
                     AND ws.strategy_type || ':' || ws.strategy_name NOT IN (
                         SELECT strategy_type || ':' || strategy_name
                         FROM winning_strategies
                         WHERE niche = ?
                     )
                   ORDER BY ws.success_score DESC
                   LIMIT 10""",
                (for_niche, for_niche),
            ).fetchall()
            return [
                {
                    "type": r[0],
                    "name": r[1],
                    "description": r[2],
                    "proven_score": round(r[3], 3),
                    "source_niche": r[4],
                }
                for r in rows
            ]

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            niches = (
                conn.execute(
                    "SELECT COUNT(DISTINCT niche) FROM niche_cycles"
                ).fetchone()[0]
                or 0
            )
            cycles = (
                conn.execute("SELECT COUNT(*) FROM niche_cycles").fetchone()[0] or 0
            )
            strategies = (
                conn.execute("SELECT COUNT(*) FROM winning_strategies").fetchone()[0]
                or 0
            )
            patterns = (
                conn.execute("SELECT COUNT(*) FROM cross_patterns").fetchone()[0] or 0
            )
            return {
                "niches_tracked": niches,
                "total_cycles": cycles,
                "winning_strategies": strategies,
                "cross_patterns": patterns,
            }


class KollektivAgent(AgentBase):
    """4a Ordem: Inteligencia Coletiva Cross-Nicho."""

    def __init__(
        self, vault_path: str | Path = ".state/kollektiv.db", **kwargs
    ) -> None:
        super().__init__("kollektiv", **kwargs)
        self.vault = CrossNicheVault(vault_path)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            # Step 1: Collect results from all niches
            niches_data = self._collect_niches_data(context)

            # Step 2: Record each niche's results
            for niche_name, data in niches_data.items():
                self.vault.record_cycle(
                    niche_name, data.get("cycle_id", "unknown"), data
                )

            # Step 3: Detect cross-niche patterns
            cross_patterns = self.vault.detect_cross_patterns()

            # Step 4: Generate recommendations for each niche
            recommendations = {}
            for niche_name in niches_data:
                recs = self.vault.get_cross_niche_recommendations(niche_name)
                if recs:
                    recommendations[niche_name] = recs

            # Step 5: Generate report
            vault_summary = self.vault.get_summary()
            synthesis = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_niches": len(niches_data),
                "vault_health": vault_summary,
                "intelligence_quote": (
                    f"{len(cross_patterns)} padroes cross-nicho. "
                    f"{sum(len(v) for v in recommendations.values())} recomendacoes."
                ),
            }

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="kollektiv",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"niches: {list(niches_data.keys())}",
                    f"patterns: {len(cross_patterns)}",
                    f"recs: {sum(len(v) for v in recommendations.values())}",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "synthesis": synthesis,
                    "vault_summary": vault_summary,
                    "cross_patterns": cross_patterns,
                    "recommendations": recommendations,
                },
                trace=trace,
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            log.error("kollektiv_failed", error=str(e)[:200])
            error_trace = AgentTrace(
                agent=self.name,
                step_id="kollektiv",
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

    def _collect_niches_data(self, context: CampaignContext) -> dict[str, dict]:
        # Try step_results first
        sr = context.step_results if hasattr(context, "step_results") else {}
        niches = {}
        for step_id, step_result in sr.items():
            if isinstance(step_result, dict):
                out = step_result.get("output", {})
                if isinstance(out, dict):
                    n = out.get("niche", "")
                    if n:
                        niches.setdefault(
                            n,
                            {
                                "cycle_id": "unknown",
                                "articles": 0,
                                "posts": 0,
                                "offers_used": 0,
                                "revenue": 0,
                                "seo_keywords": 0,
                                "started_at": datetime.now(timezone.utc).isoformat(),
                                "metadata": {},
                            },
                        )
                        d = niches[n]
                        d["articles"] = max(
                            d["articles"],
                            out.get("articles", out.get("articles_generated", 0)),
                        )
                        d["posts"] = max(
                            d["posts"], out.get("posts", out.get("posts_generated", 0))
                        )
                        d["revenue"] = max(
                            d["revenue"],
                            out.get("revenue", out.get("revenue_estimated", 0)),
                        )

        # Fallback: check campaign context for all_niches_results
        campaign = context.campaign if hasattr(context, "campaign") else {}
        all_results = campaign.get("all_niches_results", {})
        if isinstance(all_results, dict):
            for n, data in all_results.items():
                if isinstance(data, dict) and not n.startswith("_"):
                    niches.setdefault(n, {})
                    niches[n]["articles"] = max(
                        niches[n].get("articles", 0), len(data.get("articles", []))
                    )
                    niches[n]["cycle_id"] = niches[n].get("cycle_id") or data.get(
                        "cycle_id", "unknown"
                    )
                    niches[n]["revenue"] = max(
                        niches[n].get("revenue", 0),
                        data.get("revenue", {}).get("total", 0),
                    )
                    niches[n]["started_at"] = (
                        niches[n].get("started_at")
                        or datetime.now(timezone.utc).isoformat()
                    )

        # Last resort: check for "niches" in campaign
        if not niches:
            configured = campaign.get(
                "niches", ["tecnologia", "financas", "saude", "carreira"]
            )
            for n in configured:
                if isinstance(n, str) and n not in niches:
                    niches[n] = {
                        "cycle_id": "unknown",
                        "articles": 0,
                        "posts": 0,
                        "offers_used": 0,
                        "revenue": 0,
                        "seo_keywords": 0,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "metadata": {"inferred": True},
                    }

        return niches
