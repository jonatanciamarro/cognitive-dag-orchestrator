"""TemporalEngine — 5a Ordem: Inteligência Temporal.

NarrativeSelf + StrategicForesight:
- Quem o sistema foi, onde esta e para onde vai
- Deteccao de padroes sazonais no mercado BR
- Timing estrategico de conteudo e trafego pago
- Projecoes de trajetoria por nicho

Conecta passado → presente → futuro em uma narrativa coerente.
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

log = StructuredLogger("temporal_engine")

# Calendario sazonal BR — datas comerciais e culturais
SEASONAL_EVENTS: list[dict[str, Any]] = [
    {
        "name": "Volta as Aulas",
        "month": 1,
        "day": 15,
        "window_days": 30,
        "niches": ["educacao", "tecnologia", "financas"],
    },
    {
        "name": "Carnaval",
        "month": 2,
        "day": 15,
        "window_days": 14,
        "niches": ["turismo", "saude", "beleza"],
    },
    {
        "name": "Dia do Consumidor",
        "month": 3,
        "day": 15,
        "window_days": 20,
        "niches": ["tecnologia", "financas", "todas"],
    },
    {
        "name": "Dia das Maes",
        "month": 5,
        "day": 12,
        "window_days": 30,
        "niches": ["presentes", "beleza", "saude"],
    },
    {
        "name": "Dia dos Namorados",
        "month": 6,
        "day": 12,
        "window_days": 25,
        "niches": ["presentes", "viagens", "gastronomia"],
    },
    {
        "name": "Dia dos Pais",
        "month": 8,
        "day": 11,
        "window_days": 30,
        "niches": ["tecnologia", "presentes", "ferramentas"],
    },
    {
        "name": "Dia das Criancas",
        "month": 10,
        "day": 12,
        "window_days": 20,
        "niches": ["educacao", "brinquedos", "tecnologia"],
    },
    {
        "name": "Black Friday",
        "month": 11,
        "day": 28,
        "window_days": 35,
        "niches": ["todas"],
    },
    {"name": "Natal", "month": 12, "day": 25, "window_days": 45, "niches": ["todas"]},
    {
        "name": "Reveillon",
        "month": 12,
        "day": 31,
        "window_days": 15,
        "niches": ["todas"],
    },
]


class TemporalStore:
    """Timeline persistente — armazena o self historico do sistema."""

    def __init__(self, db_path: str | Path = ".state/temporal.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    niche TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    UNIQUE(cycle_id, niche, event_type)
                );
                CREATE TABLE IF NOT EXISTS narrative_self (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dimension TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS projections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche TEXT NOT NULL,
                    projection_date TEXT NOT NULL,
                    projection_type TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    UNIQUE(niche, projection_date, projection_type)
                );
            """)
            conn.commit()

    def record_cycle_event(
        self, cycle_id: str, niche: str, event_type: str, data: dict
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT OR REPLACE INTO timeline (cycle_id, niche, event_type, timestamp, data) VALUES (?, ?, ?, ?, ?)",
                (cycle_id, niche, event_type, now, json.dumps(data)),
            )
            conn.commit()

    def get_timeline(
        self, niche: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            if niche:
                rows = conn.execute(
                    "SELECT cycle_id, niche, event_type, timestamp, data FROM timeline "
                    "WHERE niche=? ORDER BY timestamp DESC LIMIT ?",
                    (niche, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT cycle_id, niche, event_type, timestamp, data FROM timeline "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [
                {
                    "cycle_id": r[0],
                    "niche": r[1],
                    "event_type": r[2],
                    "timestamp": r[3],
                    "data": json.loads(r[4]),
                }
                for r in rows
            ]

    def update_narrative_self(self, dimension: str, content: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT OR REPLACE INTO narrative_self (dimension, content, updated_at) VALUES (?, ?, ?)",
                (dimension, content, now),
            )
            conn.commit()

    def get_narrative_self(self, dimension: str | None = None) -> dict[str, str]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            if dimension:
                row = conn.execute(
                    "SELECT dimension, content, updated_at FROM narrative_self WHERE dimension=?",
                    (dimension,),
                ).fetchone()
                return {row[0]: row[1]} if row else {}
            else:
                rows = conn.execute(
                    "SELECT dimension, content, updated_at FROM narrative_self"
                ).fetchall()
                return {r[0]: r[1] for r in rows}

    def save_projection(
        self,
        niche: str,
        projection_date: str,
        projection_type: str,
        metrics: dict,
        confidence: float,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.execute(
                "INSERT OR REPLACE INTO projections (niche, projection_date, projection_type, metrics, confidence, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    niche,
                    projection_date,
                    projection_type,
                    json.dumps(metrics),
                    confidence,
                    now,
                ),
            )
            conn.commit()

    def get_projections(
        self, niche: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            if niche:
                rows = conn.execute(
                    "SELECT niche, projection_date, projection_type, metrics, confidence, created_at "
                    "FROM projections WHERE niche=? ORDER BY projection_date DESC LIMIT ?",
                    (niche, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT niche, projection_date, projection_type, metrics, confidence, created_at "
                    "FROM projections ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [
                {
                    "niche": r[0],
                    "projection_date": r[1],
                    "type": r[2],
                    "metrics": json.loads(r[3]),
                    "confidence": r[4],
                    "created_at": r[5],
                }
                for r in rows
            ]

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            events = conn.execute("SELECT COUNT(*) FROM timeline").fetchone()[0] or 0
            projections = (
                conn.execute("SELECT COUNT(*) FROM projections").fetchone()[0] or 0
            )
            narratives = (
                conn.execute("SELECT COUNT(*) FROM narrative_self").fetchone()[0] or 0
            )
            niches = (
                conn.execute("SELECT COUNT(DISTINCT niche) FROM timeline").fetchone()[0]
                or 0
            )
            return {
                "timeline_events": events,
                "projections": projections,
                "narrative_dimensions": narratives,
                "niches_tracked": niches,
            }


class TemporalEngineAgent(AgentBase):
    """5a Ordem: Engine de Inteligencia Temporal.

    Conecta passado (NarrativeSelf), presente (analise atual) e
    futuro (StrategicForesight) em uma narrativa coerente.
    """

    def __init__(self, db_path: str | Path = ".state/temporal.db", **kwargs) -> None:
        super().__init__("temporal_engine", **kwargs)
        self.store = TemporalStore(db_path)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            cycle_id = campaign.get("cycle_id", campaign.get("run_id", "unknown"))
            niche = campaign.get("niche", "")

            # Step 1: Record this cycle in the timeline
            self._record_current_cycle(cycle_id, niche, campaign)

            # Step 2: Build NarrativeSelf
            narrative = self._build_narrative(niche)

            # Step 3: Run Strategic Foresight
            foresight = self._strategic_foresight(niche)

            # Step 4: Detect upcoming seasonal events
            seasonal = self._detect_seasonal_events()

            # Step 5: Generate temporal recommendations
            recommendations = self._generate_temporal_recommendations(
                niche, foresight, seasonal
            )

            # Step 6: Update NarrativeSelf
            if narrative:
                self.store.update_narrative_self(
                    f"narrative_{niche or 'global'}",
                    json.dumps(narrative, ensure_ascii=False),
                )

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="temporal",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"timeline: {narrative.get('timeline_length', 0)} events",
                    f"seasonal: {len(seasonal)} upcoming events",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "narrative": narrative,
                    "foresight": foresight,
                    "seasonal_events": seasonal,
                    "recommendations": recommendations,
                    "store_summary": self.store.get_summary(),
                },
                trace=trace,
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            log.error("temporal_failed", error=str(e)[:200])
            error_trace = AgentTrace(
                agent=self.name,
                step_id="temporal",
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

    def _record_current_cycle(self, cycle_id: str, niche: str, campaign: dict) -> None:
        data = {
            "articles": campaign.get("articles", 0),
            "revenue": campaign.get("revenue_estimated", campaign.get("revenue", 0)),
            "works_completed": True,
        }
        if cycle_id != "unknown":
            self.store.record_cycle_event(
                cycle_id, niche or "global", "cycle_complete", data
            )

    def _build_narrative(self, niche: str) -> dict[str, Any]:
        timeline = self.store.get_timeline(niche, limit=100)
        if not timeline:
            return {
                "timeline_length": 0,
                "historical_self": "Sistema novo. Ainda construindo historico.",
                "story_so_far": "Jornada comecou agora.",
            }

        total_cycles = len(timeline)
        first_event = (
            timeline[-1]["timestamp"] if len(timeline) > 1 else timeline[0]["timestamp"]
        )
        last_event = timeline[0]["timestamp"]

        # Calculate trajectory
        try:
            first_dt = datetime.fromisoformat(first_event)
            last_dt = datetime.fromisoformat(last_event)
            active_days = (last_dt - first_dt).days or 1
            cycles_per_day = total_cycles / active_days
        except Exception:
            active_days = 0
            cycles_per_day = 0

        return {
            "timeline_length": total_cycles,
            "historical_self": f"Completei {total_cycles} ciclos em {active_days} dias (media: {cycles_per_day:.1f}/dia)",
            "active_days": active_days,
            "cycles_per_day": round(cycles_per_day, 2),
            "first_recorded": first_event,
            "last_recorded": last_event,
            "story_so_far": (
                f"Ha {active_days} dias, este sistema comecou a operar. "
                f"Desde entao, completei {total_cycles} ciclos de conteudo, "
                f"aprendendo e evoluindo a cada iteracao."
            ),
        }

    def _strategic_foresight(self, niche: str) -> dict[str, Any]:
        timeline = self.store.get_timeline(niche, limit=50)
        if len(timeline) < 3:
            return {
                "projections": [],
                "confidence": 0.0,
                "note": "Historico insuficiente para projecoes (minimo 3 ciclos)",
            }

        # Simple trend projection based on recent trajectory
        recent = timeline[: min(10, len(timeline))]
        total_revenue = 0
        total_articles = 0
        for event in recent:
            d = event.get("data", {})
            total_revenue += d.get("revenue", 0)
            total_articles += d.get("articles", 0)

        avg_revenue = total_revenue / max(len(recent), 1)
        avg_articles = total_articles / max(len(recent), 1)

        # Project 30/60/90 days forward
        projections = []
        for days in [30, 60, 90]:
            projected_revenue = avg_revenue * days * 0.8  # 80% confidence decay
            projections.append(
                {
                    "horizon_days": days,
                    "projected_revenue": round(projected_revenue, 2),
                    "projected_articles": round(avg_articles * days),
                    "confidence": round(max(0.3, 0.8 - (days * 0.005)), 2),
                }
            )

        return {
            "projections": projections,
            "avg_revenue_per_cycle": round(avg_revenue, 2),
            "avg_articles_per_cycle": round(avg_articles, 1),
            "confidence": 0.7 if len(timeline) >= 10 else 0.5,
            "trend": "crescente" if avg_revenue > 0 else "estavel",
        }

    def _detect_seasonal_events(self) -> list[dict[str, Any]]:
        """Detecta eventos sazonais BR proximos."""
        now = datetime.now(timezone.utc)
        current_year = now.year
        upcoming = []

        for event in SEASONAL_EVENTS:
            event_date = datetime(
                current_year, event["month"], event["day"], tzinfo=timezone.utc
            )
            if event_date < now:
                event_date = datetime(
                    current_year + 1, event["month"], event["day"], tzinfo=timezone.utc
                )

            days_until = (event_date - now).days
            window = event["window_days"]

            if days_until <= window:
                upcoming.append(
                    {
                        "name": event["name"],
                        "date": event_date.isoformat(),
                        "days_until": days_until,
                        "window_days": window,
                        "niches": event["niches"],
                        "urgency": "alta"
                        if days_until <= 7
                        else "media"
                        if days_until <= 14
                        else "baixa",
                        "recommendation": self._seasonal_recommendation(
                            event["name"], event["niches"]
                        ),
                    }
                )

        return sorted(upcoming, key=lambda x: x["days_until"])

    def _seasonal_recommendation(self, event_name: str, niches: list[str]) -> str:
        recs = {
            "Black Friday": "Preparar conteudo comparativo (melhores produtos) e ofertas de afiliado com descontos reais.",
            "Natal": "Conteudo sobre presentes, guias de compras, ofertas especiais de fim de ano.",
            "Dia das Maes": "Conteudo emocional, guias de presente, historias de mae e familia.",
            "Dia dos Pais": "Conteudo sobre tecnologia, ferramentas, presentes utilitarios.",
            "Dia das Criancas": "Conteudo sobre educacao, brinquedos educativos, tecnologia infantil.",
            "Volta as Aulas": "Conteudo sobre materiais escolares, cursos online, organizacao de estudos.",
            "Dia do Consumidor": "Conteudo sobre direitos do consumidor, melhores ofertas, comparativos.",
            "Carnaval": "Conteudo sobre viagens, saude, beleza, cuidados durante a folia.",
            "Dia dos Namorados": "Conteudo sobre presentes românticos, jantares, viagem a dois.",
            "Reveillon": "Conteudo sobre metas, financas para o novo ano, resolucoes.",
        }
        return recs.get(event_name, f"Preparar conteudo sazonal para {event_name}.")

    def _generate_temporal_recommendations(
        self, niche: str, foresight: dict, seasonal: list
    ) -> list[dict[str, Any]]:
        recs = []
        if seasonal:
            for event in seasonal[:3]:
                if "todas" in event["niches"] or niche in event["niches"]:
                    recs.append(
                        {
                            "type": "seasonal_content",
                            "priority": event["urgency"],
                            "action": event["recommendation"],
                            "deadline": event["date"],
                            "days_remaining": event["days_until"],
                        }
                    )

        projections = foresight.get("projections", [])
        if projections:
            nearest = projections[0]
            if nearest.get("projected_revenue", 0) > 0:
                recs.append(
                    {
                        "type": "strategic_target",
                        "priority": "media",
                        "action": f"Meta: R$ {nearest['projected_revenue']:.2f} nos proximos {nearest['horizon_days']} dias",
                    }
                )

        return recs
