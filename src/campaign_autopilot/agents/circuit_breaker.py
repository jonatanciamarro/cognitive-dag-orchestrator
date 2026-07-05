"""CircuitBreaker — Sistema de Preservação de Emergência.

Monitora a saúde geral do sistema e ativa modos de segurança:
1. GREEN — Operação normal
2. YELLOW — Degradação detectada, modo cauteloso
3. RED — Falha crítica, freeze + preservação de estado

DARPA-style: resiliência a nível de sistema, não apenas de componente.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


_CRITICAL_AGENTS = {
    "content_generator",
    "free_image_gen",
    "site_deploy",
    "analytics_feedback",
    "meta_orchestrator",
}

_MAX_CONSECUTIVE_FAILURES = 3


class CircuitBreaker(AgentBase):
    """Sistema de Preservação de Emergência.

    Três estados:
    - GREEN: Operação normal
    - YELLOW: Degradação detectada (ações cautelares)
    - RED: Falha crítica (freeze + snapshot + alerta)
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("circuit_breaker", **kwargs)
        self.state_file = Path(".state/circuit_state.json")
        self.snapshot_dir = Path(".state/emergency_snapshots")
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        if self.state_file.exists():
            try:
                self.state = json.loads(self.state_file.read_text())
            except (json.JSONDecodeError, Exception):
                self.state = self._default_state()
        else:
            self.state = self._default_state()

    def _default_state(self) -> dict:
        return {
            "status": "GREEN",
            "consecutive_failures": 0,
            "critical_agents_down": [],
            "last_snapshot": None,
            "activated_at": None,
            "history": [],
        }

    def _save_state(self) -> None:
        self.state_file.write_text(json.dumps(self.state, indent=2, default=str))

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        step_results = context.step_results

        # 1. Analisar saúde atual
        analysis = self._analyze_health(step_results)

        # 2. Determinar estado
        new_status = self._determine_status(analysis)
        status_changed = new_status != self.state["status"]
        self.state["status"] = new_status

        # 3. Executar ações baseadas no estado
        actions: list[dict[str, Any]] = []
        if new_status == "RED":
            if not self.state["activated_at"]:
                actions = self._emergency_freeze(step_results, context.run_id)
                self.state["activated_at"] = utc_now_iso()
        elif new_status == "YELLOW":
            actions = self._cautious_mode(analysis)
        else:  # GREEN
            self.state["consecutive_failures"] = 0
            self.state["critical_agents_down"] = []
            self.state["activated_at"] = None

        # 4. Registrar histórico
        self.state["history"].append(
            {
                "timestamp": utc_now_iso(),
                "status": new_status,
                "changed": status_changed,
                "total_failures": analysis["total_failures"],
                "total_agents": analysis["total_agents"],
            }
        )
        if len(self.state["history"]) > 50:
            self.state["history"] = self.state["history"][-50:]
        self._save_state()

        output = {
            "status": new_status,
            "status_changed": status_changed,
            "health_analysis": analysis,
            "actions_taken": actions,
            "consecutive_failures": self.state["consecutive_failures"],
            "critical_agents_down": self.state["critical_agents_down"],
            "recommendation": self._recommendation(new_status),
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="circuit_breaker",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Status: {new_status} | {analysis['total_failures']} falhas em {analysis['total_agents']} agentes"
            ],
            metadata={"status": new_status, "failures": analysis["total_failures"]},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── Análise de Saúde ───────────────────────────────────────

    def _analyze_health(self, step_results: dict) -> dict[str, Any]:
        """Analyze health of all agents in the cycle."""
        total = len(step_results)
        failures = 0
        critical_down = []

        for step_id, result in step_results.items():
            if not isinstance(result, dict):
                failures += 1
                continue
            status = result.get("status", "unknown")
            if status != "success":
                failures += 1
                if step_id in _CRITICAL_AGENTS:
                    critical_down.append(step_id)

        self.state["consecutive_failures"] = (
            self.state["consecutive_failures"] + 1 if failures > 0 else 0
        )
        self.state["critical_agents_down"] = critical_down

        return {
            "total_agents": total,
            "total_failures": failures,
            "critical_agents_down": critical_down,
            "success_rate": round((total - failures) / max(total, 1) * 100, 1),
        }

    # ── Determinação de Estado ─────────────────────────────────

    def _determine_status(self, analysis: dict) -> str:
        """Determine system status based on health analysis."""
        # RED: critical agent down OR consecutive failures > limit
        if analysis["critical_agents_down"]:
            return "RED"
        if self.state["consecutive_failures"] >= _MAX_CONSECUTIVE_FAILURES:
            return "RED"
        if analysis["total_failures"] > 0:
            return "YELLOW"
        return "GREEN"

    # ── Ações de Emergência (RED) ──────────────────────────────

    def _emergency_freeze(self, step_results: dict, cycle_id: str) -> list[dict]:
        """Emergency freeze: preserve state, create snapshot."""
        actions = []
        snapshot_id = f"emergency_{cycle_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        snap_path = self.snapshot_dir / snapshot_id
        snap_path.mkdir(parents=True, exist_ok=True)

        # 1. Save state snapshot
        try:
            (snap_path / "step_results.json").write_text(
                json.dumps(step_results, indent=2, default=str)
            )
            actions.append(
                {
                    "action": "state_snapshot",
                    "path": str(snap_path / "step_results.json"),
                    "status": "saved",
                }
            )
        except Exception as e:
            actions.append({"action": "state_snapshot", "status": f"error: {e}"})

        # 2. Backup workflow files
        for wf in Path("workflows").glob("*.json"):
            try:
                shutil.copy2(str(wf), str(snap_path / wf.name))
            except Exception:
                pass
        actions.append(
            {"action": "workflow_backup", "path": str(snap_path), "status": "saved"}
        )

        # 3. Backup DBs
        for db in list(Path(".state").glob("*.sqlite3")) + list(
            Path(".").glob("*.sqlite3")
        ):
            try:
                shutil.copy2(str(db), str(snap_path / db.name))
            except Exception:
                pass

        self.state["last_snapshot"] = snapshot_id
        actions.append(
            {
                "action": "emergency_freeze",
                "snapshot_id": snapshot_id,
                "status": "SYSTEM_FROZEN",
                "message": "Sistema congelado por segurança. Snapshot de emergência criado. "
                "Revise os agentes críticos antes de continuar.",
            }
        )
        return actions

    # ── Modo Cauteloso (YELLOW) ────────────────────────────────

    def _cautious_mode(self, analysis: dict) -> list[dict]:
        """Cautious mode: log warnings, suggest mitigations."""
        return [
            {
                "action": "cautious_mode",
                "failures": analysis["total_failures"],
                "status": "degraded",
                "message": f"{analysis['total_failures']} falhas detectadas. "
                "Operação continua mas recomenda-se revisão.",
            }
        ]

    @staticmethod
    def _recommendation(status: str) -> str:
        if status == "GREEN":
            return "✅ Sistema operando normalmente. Nenhuma ação necessária."
        elif status == "YELLOW":
            return "⚠️ Degradação detectada. Monitore os agentes com falha. Modo cautelar ativo."
        else:
            return "🔴 EMERGÊNCIA: Agentes críticos offline. Sistema congelado. Intervenção necessária."
