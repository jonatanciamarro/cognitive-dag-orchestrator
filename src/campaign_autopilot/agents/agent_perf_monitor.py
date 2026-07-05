"""AgentPerformanceMonitor — Monitora performance individual de cada agente.

Sistema de analytics de segunda ordem que:
- Rastreia taxa de sucesso, tempo médio, output value de cada agente
- Identifica agentes com baixa performance ou degradação
- Recomenda substituição, otimização ou remoção de agentes
- Gera ranking de agentes por contribuição
- Detecta regressão de performance ao longo do tempo
"""

from __future__ import annotations

import json
from pathlib import Path

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class AgentPerformanceMonitor(AgentBase):
    """Monitora e analisa a performance individual de cada agente.

    Permite que o sistema avalie seus próprios componentes e tome
    decisões sobre otimização, substituição ou remoção de agentes.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("agent_perf_monitor", **kwargs)
        self.db_file = Path(".state/agent_performance.json")
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_db()

    def _load_db(self) -> None:
        if self.db_file.exists():
            try:
                self.db = json.loads(self.db_file.read_text())
            except (json.JSONDecodeError, Exception):
                self.db = self._default_db()
        else:
            self.db = self._default_db()

    def _default_db(self) -> dict:
        return {"agents": {}, "cycle_logs": [], "anomalies": []}

    def _save_db(self) -> None:
        self.db_file.write_text(json.dumps(self.db, indent=2, default=str))

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        step_results = context.step_results

        # 1. Coletar métricas de cada agente neste ciclo
        cycle_metrics = self._collect_cycle_metrics(step_results, context.run_id)

        # 2. Atualizar base histórica
        self._update_agent_db(cycle_metrics)

        # 3. Detectar anomalias
        anomalies = self._detect_anomalies(cycle_metrics)

        # 4. Gerar ranking
        ranking = self._generate_ranking()

        # 5. Gerar recomendações
        recommendations = self._generate_recommendations(anomalies, ranking)

        self._save_db()

        output = {
            "status": "success",
            "cycle_id": context.run_id,
            "agents_monitored": len(cycle_metrics),
            "total_history_agents": len(self.db["agents"]),
            "cycle_metrics": cycle_metrics,
            "ranking": ranking[:10],  # Top 10
            "bottom_agents": ranking[-5:] if len(ranking) > 5 else [],
            "anomalies": anomalies,
            "recommendations": recommendations,
            "summary": self._generate_summary(cycle_metrics, anomalies),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="agent_performance_monitor",
                input_state={"agents_monitored": len(cycle_metrics)},
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={
                    "anomalies": len(anomalies),
                    "recommendations": len(recommendations),
                },
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="agent_perf_monitor",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Monitorou {len(cycle_metrics)} agentes neste ciclo. "
                f"{len(anomalies)} anomalias. {len(recommendations)} recomendações."
            ],
            metadata={
                "agents": len(cycle_metrics),
                "anomalies": len(anomalies),
                "recommendations": len(recommendations),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── 1. Coleta de Métricas ───────────────────────────────────

    def _collect_cycle_metrics(self, step_results: dict, cycle_id: str) -> list[dict]:
        """Coletar métricas de cada agente neste ciclo."""
        metrics = []

        for step_id, result in step_results.items():
            if not isinstance(result, dict):
                continue

            trace = result.get("trace", {}) or {}
            if isinstance(trace, dict):
                agent = trace.get("agent", result.get("agent", step_id))
            else:
                agent = result.get("agent", step_id)

            status = result.get("status", "unknown")
            duration = trace.get("duration_ms", 0) if isinstance(trace, dict) else 0
            error = trace.get("error", None) if isinstance(trace, dict) else None

            # Estimate output quality
            output = result.get("output", {})
            output_quality = 0
            if isinstance(output, dict):
                # Count output keys as a proxy for quality
                meaningful_keys = [
                    k for k in output.keys() if k not in ("status", "errors", "trace")
                ]
                output_quality = len(meaningful_keys)
                # Bonus for generating actual content
                for bonus_key in (
                    "images_generated",
                    "videos_generated",
                    "articles_published",
                    "total_recommendations",
                    "files_generated",
                ):
                    if bonus_key in output:
                        output_quality += output.get(bonus_key, 0)

            metrics.append(
                {
                    "cycle_id": cycle_id,
                    "agent": agent,
                    "step_id": step_id,
                    "status": status,
                    "duration_ms": duration,
                    "output_quality_score": output_quality,
                    "error": error,
                    "has_error": status != "success",
                }
            )

        return metrics

    # ── 2. Atualização de Banco ─────────────────────────────────

    def _update_agent_db(self, cycle_metrics: list[dict]) -> None:
        """Update historical database with cycle metrics."""
        for m in cycle_metrics:
            agent = m["agent"]
            if agent not in self.db["agents"]:
                self.db["agents"][agent] = {
                    "runs": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "total_output_score": 0,
                    "avg_output_score": 0,
                    "last_seen": "",
                    "performance_trend": [],  # last 10 scores
                    "first_seen": m["cycle_id"],
                }

            a = self.db["agents"][agent]
            a["runs"] += 1
            if m["status"] == "success":
                a["successes"] += 1
            else:
                a["failures"] += 1
            a["total_duration_ms"] += m["duration_ms"]
            a["avg_duration_ms"] = a["total_duration_ms"] // a["runs"]
            a["total_output_score"] += m["output_quality_score"]
            a["avg_output_score"] = a["total_output_score"] // max(a["runs"], 1)
            a["last_seen"] = m["cycle_id"]
            a["performance_trend"].append(m["output_quality_score"])
            if len(a["performance_trend"]) > 10:
                a["performance_trend"] = a["performance_trend"][-10:]

    # ── 3. Detecção de Anomalias ────────────────────────────────

    def _detect_anomalies(self, cycle_metrics: list[dict]) -> list[dict]:
        """Detect anomalous agent behavior."""
        anomalies = []

        for m in cycle_metrics:
            agent = m["agent"]
            a_data = self.db["agents"].get(agent, {})

            # High failure rate
            if a_data.get("runs", 0) >= 3:
                success_rate = a_data["successes"] / a_data["runs"]
                if success_rate < 0.5:
                    anomalies.append(
                        {
                            "agent": agent,
                            "type": "high_failure_rate",
                            "detail": f"Taxa de sucesso {success_rate:.0%} (<50%) em {a_data['runs']} execuções",
                            "severity": "critical",
                            "recommendation": f"Revisar agente '{agent}'. Possível bug ou problema de configuração.",
                        }
                    )

            # Performance degradation (trend going down)
            trend = a_data.get("performance_trend", [])
            if len(trend) >= 3:
                first_half = sum(trend[: len(trend) // 2]) / max(
                    len(trend[: len(trend) // 2]), 1
                )
                second_half = sum(trend[len(trend) // 2 :]) / max(
                    len(trend[len(trend) // 2 :]), 1
                )
                if second_half < first_half * 0.5 and first_half > 0:
                    anomalies.append(
                        {
                            "agent": agent,
                            "type": "performance_degradation",
                            "detail": f"Output score caiu de {first_half:.0f} para {second_half:.0f}",
                            "severity": "high",
                            "recommendation": f"Verificar agente '{agent}'. Pode precisar de revisão de parâmetros.",
                        }
                    )

            # Current failure
            if m["has_error"]:
                anomalies.append(
                    {
                        "agent": agent,
                        "type": "execution_error",
                        "detail": m.get("error", "Erro desconhecido")
                        or "Falha na execução",
                        "severity": "high"
                        if a_data.get("failures", 0) > 1
                        else "medium",
                        "recommendation": f"Investigar erro no agente '{agent}'.",
                    }
                )

        return anomalies

    # ── 4. Ranking ──────────────────────────────────────────────

    def _generate_ranking(self) -> list[dict]:
        """Generate agent ranking by performance score."""
        ranked = []
        for agent, data in self.db["agents"].items():
            if data["runs"] < 1:
                continue
            success_rate = data["successes"] / data["runs"]
            perf_score = (success_rate * 50) + min(data["avg_output_score"], 50)
            ranked.append(
                {
                    "agent": agent,
                    "runs": data["runs"],
                    "success_rate": round(success_rate, 2),
                    "avg_output_score": data["avg_output_score"],
                    "avg_duration_ms": data["avg_duration_ms"],
                    "performance_score": round(perf_score, 1),
                }
            )

        ranked.sort(key=lambda x: -x["performance_score"])
        return ranked

    # ── 5. Recomendações ────────────────────────────────────────

    def _generate_recommendations(
        self, anomalies: list[dict], ranking: list[dict]
    ) -> list[dict]:
        """Generate recommendations based on agent analytics."""
        recs = []

        # Critical anomalies first
        for a in anomalies:
            if a["severity"] == "critical":
                recs.append(
                    {
                        "type": "agent_issue",
                        "priority": "critical",
                        "agent": a["agent"],
                        "recommendation": a["recommendation"],
                    }
                )

        # Bottom performers
        if len(ranking) >= 3:
            bottom = ranking[-3:]
            for b in bottom:
                if b["runs"] >= 3 and b["success_rate"] < 0.7:
                    recs.append(
                        {
                            "type": "low_performer",
                            "priority": "medium",
                            "agent": b["agent"],
                            "recommendation": f"Agente '{b['agent']}' com score {b['performance_score']}. Considere revisão.",
                        }
                    )

        if not recs:
            recs.append(
                {
                    "type": "all_healthy",
                    "priority": "info",
                    "agent": "system",
                    "recommendation": "Todos os agentes operando dentro dos parâmetros esperados.",
                }
            )

        return recs

    # ── Sumário ─────────────────────────────────────────────────

    def _generate_summary(
        self, cycle_metrics: list[dict], anomalies: list[dict]
    ) -> str:
        total = len(cycle_metrics)
        successes = sum(1 for m in cycle_metrics if m["status"] == "success")
        errors = total - successes
        critical = sum(1 for a in anomalies if a["severity"] == "critical")

        return (
            f"📊 **Agent Performance Monitor**\n\n"
            f"Agentes no ciclo: {total} | Sucessos: {successes} | Erros: {errors}\n"
            f"Anomalias: {len(anomalies)} (críticas: {critical})\n\n"
            f"{'⚠️ Atenção: agentes com problemas detectados.' if anomalies else '✅ Todos os agentes operando normalmente.'}"
        )
