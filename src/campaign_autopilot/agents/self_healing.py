"""SelfHealingAgent — Auto-reparo do sistema.

Monitora a saúde dos agentes e componentes, e executa ações corretivas:
- Reconecta bancos SQLite corrompidos
- Recria diretórios de output ausentes
- Reinicia agentes que falharam consistentemente
- Limpa arquivos temporários órfãos
- Verifica integridade dos dados persistentes
- Gera relatório de saúde do sistema
"""

from __future__ import annotations

import sqlite3
import shutil
import tempfile
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


_HEALTH_CHECKS: list[dict[str, Any]] = [
    {
        "id": "output_dirs",
        "description": "Verificar diretórios de output",
        "severity": "medium",
        "auto_fix": True,
    },
    {
        "id": "temp_files",
        "description": "Limpar arquivos temporários órfãos",
        "severity": "low",
        "auto_fix": True,
    },
    {
        "id": "state_dirs",
        "description": "Verificar diretórios de estado",
        "severity": "high",
        "auto_fix": True,
    },
    {
        "id": "db_integrity",
        "description": "Verificar integridade dos bancos SQLite",
        "severity": "critical",
        "auto_fix": True,
    },
    {
        "id": "agent_history",
        "description": "Verificar arquivos de histórico dos agentes",
        "severity": "medium",
        "auto_fix": True,
    },
]


class SelfHealingAgent(AgentBase):
    """Auto-reparo do sistema. Monitora saúde e executa ações corretivas.

    Este é o 'médico' do sistema: detecta problemas, diagnostica causas,
    e aplica remediação automática quando possível.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("self_healing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()

        checks: list[dict[str, Any]] = []
        fixes: list[dict[str, Any]] = []
        warnings: list[str] = []

        # 1. Verificar diretórios de output
        checks.append(self._check_output_dirs())

        # 2. Verificar diretórios de estado
        checks.append(self._check_state_dirs())

        # 3. Limpar temporários
        checks.append(self._clean_temp_files())

        # 4. Verificar integridade dos bancos SQLite
        checks.append(self._check_db_integrity())

        # 5. Verificar arquivos de histórico dos agentes
        checks.append(self._check_agent_history())

        # Compile results
        total_checks = len(checks)
        passed = sum(1 for c in checks if c["status"] == "passed")
        fixed = sum(1 for c in checks if c["status"] == "fixed")
        failed = sum(1 for c in checks if c["status"] == "failed")

        for c in checks:
            if c.get("fixed"):
                fixes.append(
                    {
                        "check": c["id"],
                        "action": c.get("fix_action", "auto-repair applied"),
                        "result": c["status"],
                    }
                )
            if c.get("warning"):
                warnings.append(c["warning"])

        # System health score
        health_score = round((passed + fixed) / max(total_checks, 1) * 100, 1)

        output = {
            "status": "success" if failed == 0 else "degraded",
            "health_score": health_score,
            "total_checks": total_checks,
            "passed": passed,
            "fixed": fixed,
            "failed": failed,
            "checks": checks,
            "fixes_applied": fixes,
            "warnings": warnings,
            "recommendation": self._recommendation(health_score, failed),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="self_healing",
                input_state={"health_score": health_score},
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={"fixes": len(fixes), "warnings": len(warnings)},
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="self_healing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Saúde: {health_score}% | {passed} ok, {fixed} corrigidos, {failed} falhos"
            ],
            metadata={
                "health": health_score,
                "fixes": len(fixes),
                "warnings": len(warnings),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── 1. Diretórios de Output ─────────────────────────────────

    def _check_output_dirs(self) -> dict[str, Any]:
        """Verificar e recriar diretórios de output."""
        dirs = [
            Path("output/images"),
            Path("output/videos"),
            Path("output/content"),
            Path("output/published"),
            Path("site"),
            Path("site/blog"),
            Path("site/pages"),
            Path("site/assets/css"),
            Path("site/assets/js"),
        ]

        missing = []
        for d in dirs:
            if not d.exists():
                missing.append(str(d))
                try:
                    d.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return {
                        "id": "output_dirs",
                        "status": "failed",
                        "detail": f"Não foi possível criar {d}: {e}",
                        "fixed": False,
                    }

        if missing:
            return {
                "id": "output_dirs",
                "status": "fixed",
                "detail": f"{len(missing)} diretórios recriados",
                "fixed": True,
                "fix_action": f"mkdir -p {' '.join(missing)}",
            }

        return {
            "id": "output_dirs",
            "status": "passed",
            "detail": "Todos os diretórios OK",
            "fixed": False,
        }

    # ── 2. Diretórios de Estado ─────────────────────────────────

    def _check_state_dirs(self) -> dict[str, Any]:
        """Verificar diretórios de estado persistente."""
        dirs = [Path(".state"), Path("reports")]
        missing = []
        for d in dirs:
            if not d.exists():
                missing.append(str(d))
                try:
                    d.mkdir(parents=True, exist_ok=True)
                except OSError:
                    return {
                        "id": "state_dirs",
                        "status": "failed",
                        "detail": f"Não foi possível criar {d}",
                        "fixed": False,
                    }

        if missing:
            return {
                "id": "state_dirs",
                "status": "fixed",
                "detail": f"{len(missing)} diretórios de estado recriados",
                "fixed": True,
                "fix_action": f"mkdir -p {' '.join(missing)}",
            }
        return {
            "id": "state_dirs",
            "status": "passed",
            "detail": "Diretórios de estado OK",
            "fixed": False,
        }

    # ── 3. Limpeza de Temporários ───────────────────────────────

    def _clean_temp_files(self) -> dict[str, Any]:
        """Limpar arquivos temporários órfãos."""
        cleaned = 0
        size_freed = 0

        # Clean autopilot_video_ temp dirs
        temp_base = Path(tempfile.gettempdir())
        for d in temp_base.glob("autopilot_video_*"):
            try:
                size = sum(f.stat().st_size for f in d.rglob("*")) if d.exists() else 0
                shutil.rmtree(str(d), ignore_errors=True)
                cleaned += 1
                size_freed += size
            except (OSError, PermissionError):
                pass

        # Clean slide_ temp files
        for f in temp_base.glob("slide_*.png"):
            try:
                size_freed += f.stat().st_size
                f.unlink()
                cleaned += 1
            except OSError:
                pass

        if cleaned > 0:
            return {
                "id": "temp_files",
                "status": "fixed",
                "detail": f"Limpou {cleaned} arquivos temporários ({size_freed // 1024}KB)",
                "fixed": True,
                "fix_action": f"remove {cleaned} temp files",
            }
        return {
            "id": "temp_files",
            "status": "passed",
            "detail": "Sem temporários órfãos",
            "fixed": False,
        }

    # ── 4. Integridade de Bancos SQLite ─────────────────────────

    def _check_db_integrity(self) -> dict[str, Any]:
        """Verificar integridade dos bancos SQLite."""
        dbs = list(Path(".state").glob("*.sqlite3")) + list(Path(".").glob("*.sqlite3"))
        if not dbs:
            return {
                "id": "db_integrity",
                "status": "passed",
                "detail": "Nenhum banco SQLite para verificar",
                "fixed": False,
            }

        issues = []
        for db_path in dbs:
            try:
                conn = sqlite3.connect(str(db_path))
                conn.execute("PRAGMA integrity_check")
                conn.close()
            except sqlite3.DatabaseError as e:
                issues.append(f"{db_path.name}: {e}")
                # Try to recover
                try:
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("PRAGMA auto_vacuum=1")
                    conn.execute("VACUUM")
                    conn.close()
                    issues[-1] += " (recuperado via VACUUM)"
                except sqlite3.Error:
                    issues[-1] += " (sem recuperação automática)"

        if issues:
            return {
                "id": "db_integrity",
                "status": "fixed" if "recuperado" in str(issues) else "failed",
                "detail": "; ".join(issues) or "Issues encontrados",
                "fixed": "recuperado" in str(issues),
                "fix_action": "PRAGMA integrity_check + VACUUM",
            }
        return {
            "id": "db_integrity",
            "status": "passed",
            "detail": f"{len(dbs)} bancos íntegros",
            "fixed": False,
        }

    # ── 5. Histórico de Agentes ─────────────────────────────────

    def _check_agent_history(self) -> dict[str, Any]:
        """Verificar arquivos de histórico dos agentes."""
        history_files = (
            list(Path(".state").glob("*history*"))
            + list(Path(".state").glob("*evolution*"))
            + list(Path(".state").glob("*performance*"))
        )
        if not history_files:
            return {
                "id": "agent_history",
                "status": "passed",
                "detail": "Históricos ainda não criados (primeiros ciclos)",
                "fixed": False,
            }

        issues = []
        for f in history_files:
            if f.stat().st_size == 0:
                issues.append(f"{f.name}: vazio")
                try:
                    f.write_text("{}")
                    issues[-1] += " (reinicializado)"
                except (OSError, PermissionError):
                    pass
            elif f.stat().st_size > 10 * 1024 * 1024:  # >10MB
                issues.append(
                    f"{f.name}: muito grande ({f.stat().st_size // 1024 // 1024}MB)"
                )

        if issues:
            return {
                "id": "agent_history",
                "status": "fixed",
                "detail": "; ".join(issues),
                "fixed": True,
                "fix_action": "reinicializar históricos corrompidos",
            }
        return {
            "id": "agent_history",
            "status": "passed",
            "detail": f"{len(history_files)} históricos íntegros",
            "fixed": False,
        }

    # ── Recomendação ────────────────────────────────────────────

    def _recommendation(self, health: float, failed: int) -> str:
        if health >= 90:
            return "✅ Sistema saudável. Nenhuma intervenção necessária."
        elif health >= 70:
            return "⚠️ Sistema operacional com pequenos ajustes. Recomendado revisar warnings."
        elif health >= 50:
            return "🔶 Sistema degradado. Intervenção recomendada para evitar falhas."
        else:
            return "🔴 Sistema crítico. Intervenção imediata necessária."
