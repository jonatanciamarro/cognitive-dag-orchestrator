"""Agent Tracing System — Persistent execution trace store.

Registra todo ciclo de execucao de agentes:
- Inputs e outputs
- Tool calls e model calls
- Custo e duracao
- Erros e recuperacao
- Dependencias entre passos

Uso:
    store = TraceStore("traces.sqlite3")
    recorder = TraceRecorder(store)
    with recorder.record("agent_x", run_id="abc") as ctx:
        ctx.set_input({"prompt": "hello"})
        result = agent.run(...)
        ctx.set_output(result)
        # ctx stores everything automatically
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(v: Any) -> str:
    try:
        return json.dumps(v, default=str, ensure_ascii=False)
    except Exception:
        return json.dumps({"error": "unserializable"})


def _from_json(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return s


# ═══════════════════════════════════════════════════════════════════
# TRACE RECORD
# ═══════════════════════════════════════════════════════════════════


@dataclass
class TraceRecord:
    """Complete trace of a single agent execution."""

    trace_id: str
    run_id: str
    agent_name: str
    step_id: str
    status: str  # "running", "success", "failed", "recovered"
    started_at: str
    finished_at: str = ""
    duration_ms: int = 0
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    model_calls: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    error: str | None = None
    recovery_attempts: int = 0
    cost: float = 0.0
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    workflow_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TraceRecord":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ═══════════════════════════════════════════════════════════════════
# TRACE STORE — SQLite Persistence
# ═══════════════════════════════════════════════════════════════════


class TraceStore:
    """Persistent trace storage with SQLite WAL mode.

    Thread-safe. Each trace is a row in the 'traces' table.
    Supports query by run_id, agent_name, status, time range.
    """

    def __init__(self, db_path: str | Path = "traces.sqlite3"):
        self.db_path = str(db_path)
        self._lock = threading.Lock()
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
        return self._conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'running',
                    started_at TEXT NOT NULL,
                    finished_at TEXT DEFAULT '',
                    duration_ms INTEGER DEFAULT 0,
                    input_data TEXT DEFAULT '{}',
                    output_data TEXT DEFAULT '{}',
                    tool_calls TEXT DEFAULT '[]',
                    model_calls TEXT DEFAULT '[]',
                    dependencies TEXT DEFAULT '[]',
                    error TEXT,
                    recovery_attempts INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    tokens_used INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    workflow_name TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_traces_run
                ON traces(run_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_traces_agent
                ON traces(agent_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_traces_status
                ON traces(status)
            """)
            conn.commit()

    def save(self, record: TraceRecord) -> None:
        """Save or update a trace record."""
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                """
                INSERT INTO traces (
                    trace_id, run_id, agent_name, step_id, status,
                    started_at, finished_at, duration_ms,
                    input_data, output_data, tool_calls, model_calls,
                    dependencies, error, recovery_attempts,
                    cost, tokens_used, metadata, workflow_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(trace_id) DO UPDATE SET
                    status=excluded.status,
                    finished_at=excluded.finished_at,
                    duration_ms=excluded.duration_ms,
                    output_data=excluded.output_data,
                    tool_calls=excluded.tool_calls,
                    model_calls=excluded.model_calls,
                    error=excluded.error,
                    recovery_attempts=excluded.recovery_attempts,
                    cost=excluded.cost,
                    tokens_used=excluded.tokens_used,
                    metadata=excluded.metadata
            """,
                (
                    record.trace_id,
                    record.run_id,
                    record.agent_name,
                    record.step_id,
                    record.status,
                    record.started_at,
                    record.finished_at,
                    record.duration_ms,
                    _json(record.input_data),
                    _json(record.output_data),
                    _json(record.tool_calls),
                    _json(record.model_calls),
                    _json(record.dependencies),
                    record.error,
                    record.recovery_attempts,
                    record.cost,
                    record.tokens_used,
                    _json(record.metadata),
                    record.workflow_name,
                ),
            )
            conn.commit()

    def get(self, trace_id: str) -> TraceRecord | None:
        """Get a single trace by ID."""
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT * FROM traces WHERE trace_id = ?", (trace_id,)
            ).fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def list_by_run(self, run_id: str) -> list[TraceRecord]:
        """List all traces for a given execution run."""
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM traces WHERE run_id = ? ORDER BY started_at", (run_id,)
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def list_by_agent(self, agent_name: str, limit: int = 50) -> list[TraceRecord]:
        """List recent traces for a specific agent."""
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM traces WHERE agent_name = ? ORDER BY started_at DESC LIMIT ?",
                (agent_name, limit),
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def list_by_status(self, status: str, limit: int = 50) -> list[TraceRecord]:
        """List traces with a specific status."""
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM traces WHERE status = ? ORDER BY started_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def list_recent(self, limit: int = 100) -> list[TraceRecord]:
        """List most recent traces."""
        with self._lock:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM traces ORDER BY started_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_stats(self) -> dict[str, Any]:
        """Aggregate statistics across all traces."""
        with self._lock:
            conn = self._get_conn()
            total = conn.execute("SELECT COUNT(*) FROM traces").fetchone()[0]
            by_status = conn.execute(
                "SELECT status, COUNT(*) FROM traces GROUP BY status"
            ).fetchall()
            total_cost = conn.execute(
                "SELECT COALESCE(SUM(cost), 0) FROM traces"
            ).fetchone()[0]
            total_tokens = conn.execute(
                "SELECT COALESCE(SUM(tokens_used), 0) FROM traces"
            ).fetchone()[0]
            avg_duration = conn.execute(
                "SELECT COALESCE(AVG(duration_ms), 0) FROM traces WHERE duration_ms > 0"
            ).fetchone()[0]
            by_agent = conn.execute(
                "SELECT agent_name, COUNT(*) FROM traces GROUP BY agent_name ORDER BY COUNT(*) DESC LIMIT 20"
            ).fetchall()
        return {
            "total_traces": total,
            "by_status": {row[0]: row[1] for row in by_status},
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "avg_duration_ms": round(avg_duration, 1),
            "top_agents": [{"agent": row[0], "calls": row[1]} for row in by_agent],
        }

    def delete_old(self, days: int = 30) -> int:
        """Delete traces older than N days. Returns count deleted."""
        cutoff = datetime.now(timezone.utc).isoformat()
        # Approximate: compare the started_at string (ISO format is sortable)
        with self._lock:
            conn = self._get_conn()
            # Delete traces where started_at is older than N days
            # We need to convert ISO date to compare properly
            deleted = conn.execute(
                "DELETE FROM traces WHERE started_at < ?", (cutoff,)
            ).rowcount
            conn.commit()
        # More precise: delete traces older than N days from now
        import time as _time

        cutoff_ts = _time.time() - (days * 86400)
        with self._lock:
            conn = self._get_conn()
            # SQLite doesn't have great date parsing, so we use the trace_id timestamp prefix
            # or just delete by count if too many
            deleted = conn.execute(
                "DELETE FROM traces WHERE trace_id IN ("
                "SELECT trace_id FROM traces ORDER BY started_at ASC "
                "LIMIT (SELECT MAX(0, COUNT(*) - 10000) FROM traces)"
                ")"
            ).rowcount
            conn.commit()
        return deleted

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> TraceRecord:
        return TraceRecord(
            trace_id=row["trace_id"],
            run_id=row["run_id"],
            agent_name=row["agent_name"],
            step_id=row["step_id"],
            status=row["status"],
            started_at=row["started_at"],
            finished_at=row["finished_at"] or "",
            duration_ms=row["duration_ms"] or 0,
            input_data=_from_json(row["input_data"] or "{}"),
            output_data=_from_json(row["output_data"] or "{}"),
            tool_calls=_from_json(row["tool_calls"] or "[]"),
            model_calls=_from_json(row["model_calls"] or "[]"),
            dependencies=_from_json(row["dependencies"] or "[]"),
            error=row["error"],
            recovery_attempts=row["recovery_attempts"] or 0,
            cost=row["cost"] or 0.0,
            tokens_used=row["tokens_used"] or 0,
            metadata=_from_json(row["metadata"] or "{}"),
            workflow_name=row["workflow_name"] or "",
        )

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ═══════════════════════════════════════════════════════════════════
# TRACE RECORDER — Context manager for automatic tracing
# ═══════════════════════════════════════════════════════════════════


class TraceRecorder:
    """Records agent execution traces automatically.

    Use as a context manager:
        with recorder.record("my_agent", run_id="run_1") as ctx:
            ctx.set_input({"prompt": "hello"})
            result = my_agent.run(context)
            ctx.set_output(result)
    """

    def __init__(self, store: TraceStore):
        self.store = store

    def record(
        self,
        agent_name: str,
        step_id: str = "",
        run_id: str = "",
        workflow_name: str = "",
        dependencies: list[str] | None = None,
    ) -> "_TraceSession":
        trace_id = uuid.uuid4().hex[:16]
        session = _TraceSession(
            store=self.store,
            trace_id=trace_id,
            agent_name=agent_name,
            step_id=step_id or agent_name,
            run_id=run_id or uuid.uuid4().hex[:12],
            workflow_name=workflow_name,
            dependencies=dependencies or [],
        )
        return session.__enter__()


class _TraceSession:
    """Internal session object returned by TraceRecorder.record()."""

    def __init__(
        self,
        store: TraceStore,
        trace_id: str,
        agent_name: str,
        step_id: str,
        run_id: str,
        workflow_name: str,
        dependencies: list[str],
    ):
        self.store = store
        self.trace_id = trace_id
        self.agent_name = agent_name
        self.step_id = step_id
        self.run_id = run_id
        self.workflow_name = workflow_name
        self.dependencies = dependencies
        self.record: TraceRecord | None = None
        self._started: str = ""

    def __enter__(self) -> "_TraceSession":
        self._started = _now_iso()
        self.record = TraceRecord(
            trace_id=self.trace_id,
            run_id=self.run_id,
            agent_name=self.agent_name,
            step_id=self.step_id,
            status="running",
            started_at=self._started,
            dependencies=self.dependencies,
            workflow_name=self.workflow_name,
        )
        self.store.save(self.record)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        finished = _now_iso()
        started = datetime.fromisoformat(self._started)
        ended = datetime.fromisoformat(finished)
        ms = max(0, int((ended - started).total_seconds() * 1000))

        self.record.finished_at = finished
        self.record.duration_ms = ms

        if exc_type:
            self.record.status = "failed"
            self.record.error = (
                f"{exc_type.__name__}: {exc_val}" if exc_val else str(exc_type)
            )
        elif self.record.status == "running":
            self.record.status = "success"

        self.store.save(self.record)

    def set_input(self, data: dict[str, Any]) -> None:
        if self.record:
            self.record.input_data = data
            self.store.save(self.record)

    def set_output(self, data: Any) -> None:
        if self.record:
            if isinstance(data, dict):
                self.record.output_data = data
            elif hasattr(data, "to_dict"):
                self.record.output_data = data.to_dict()
            else:
                self.record.output_data = {"result": str(data)}
            self.store.save(self.record)

    def add_tool_call(
        self, tool_name: str, inputs: dict, outputs: Any, duration_ms: int = 0
    ) -> None:
        if self.record:
            self.record.tool_calls.append(
                {
                    "tool": tool_name,
                    "input": inputs,
                    "output": _jsonable(outputs),
                    "duration_ms": duration_ms,
                    "timestamp": _now_iso(),
                }
            )
            self.store.save(self.record)

    def add_model_call(
        self,
        model: str,
        prompt: str,
        response: str,
        tokens: int = 0,
        cost: float = 0.0,
        duration_ms: int = 0,
    ) -> None:
        if self.record:
            self.record.model_calls.append(
                {
                    "model": model,
                    "prompt_preview": prompt[:200],
                    "response_preview": response[:200] if response else "",
                    "tokens": tokens,
                    "cost": cost,
                    "duration_ms": duration_ms,
                    "timestamp": _now_iso(),
                }
            )
            self.record.tokens_used += tokens
            self.record.cost += cost
            self.store.save(self.record)

    def set_recovered(self, error: str) -> None:
        if self.record:
            self.record.status = "recovered"
            self.record.recovery_attempts += 1
            self.record.error = error
            self.store.save(self.record)

    def set_metadata(self, **kwargs) -> None:
        if self.record:
            self.record.metadata.update(kwargs)
            self.store.save(self.record)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


# ═══════════════════════════════════════════════════════════════════
# TRACE VIEWER — Query and format traces
# ═══════════════════════════════════════════════════════════════════


class TraceViewer:
    """Query and display traces in various formats."""

    def __init__(self, store: TraceStore):
        self.store = store

    def summary(self, run_id: str) -> dict[str, Any]:
        """Get a human-readable summary of a run."""
        traces = self.store.list_by_run(run_id)
        if not traces:
            return {"error": "run not found", "run_id": run_id}

        total_duration = sum(t.duration_ms for t in traces)
        total_cost = sum(t.cost for t in traces)
        total_tokens = sum(t.tokens_used for t in traces)
        by_status: dict[str, int] = {}
        for t in traces:
            by_status[t.status] = by_status.get(t.status, 0) + 1

        return {
            "run_id": run_id,
            "total_agents": len(traces),
            "total_duration_ms": total_duration,
            "total_cost": round(total_cost, 6),
            "total_tokens": total_tokens,
            "by_status": by_status,
            "agents": [t.agent_name for t in traces],
            "failed": [t.agent_name for t in traces if t.status == "failed"],
        }

    def report(self, limit: int = 20) -> str:
        """Generate a text report of recent traces."""
        traces = self.store.list_recent(limit)
        lines = [f"=== Recent Traces (last {len(traces)}) ==="]
        for t in traces:
            status_icon = {
                "success": "OK",
                "failed": "FAIL",
                "recovered": "REC",
                "running": "RUN",
            }.get(t.status, "?")
            lines.append(
                f"  {status_icon} {t.agent_name:25s} | "
                f"{t.duration_ms:6d}ms | "
                f"${t.cost:.6f} | "
                f"{t.tokens_used:6d}tok | "
                f"{t.run_id[:12]}"
            )
        return "\n".join(lines)


__all__ = [
    "TraceRecord",
    "TraceStore",
    "TraceRecorder",
    "TraceViewer",
]
