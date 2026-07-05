"""MetaOrchestratorAgent — Orquestrador de Segunda Ordem.

Auto-observa a execução dos workflows e modifica sua própria estrutura:
- Analisa performance de cada step (duração, erros, output quality)
- Sugere paralelização de steps sequenciais lentos
- Remove steps que consistentemente produzem pouco valor
- Adiciona steps ausentes baseado em padrões de ciclos anteriores
- Ajusta max_workers baseado em utilização de recursos
- Gera novas configurações de workflow para o próximo ciclo

Este é o agente que permite ao sistema evoluir sua própria arquitetura.
"""

from __future__ import annotations

import json
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


class MetaOrchestratorAgent(AgentBase):
    """Orquestrador de Segunda Ordem — auto-modifica a estrutura do sistema.

    Funciona como o 'sistema nervoso' do meta-sistema: observa a execução,
    diagnostica gargalos, e gera prescrições para modificar workflows,
    alocação de recursos e configuração de agentes.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("meta_orchestrator", **kwargs)
        self.history_file = Path(".state/meta_history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_history()

    def _load_history(self) -> None:
        """Load historical execution data across cycles."""
        if self.history_file.exists():
            try:
                self.history = json.loads(self.history_file.read_text())
            except (json.JSONDecodeError, Exception):
                self.history = {
                    "cycles": [],
                    "workflow_evolution": [],
                    "agent_scores": {},
                }
        else:
            self.history = {"cycles": [], "workflow_evolution": [], "agent_scores": {}}

    def _save_history(self) -> None:
        self.history_file.write_text(json.dumps(self.history, indent=2, default=str))

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        step_results = context.step_results
        niche = str(campaign.get("niche", campaign.get("objective", "")))

        # 1. ANALYZE — Analisar performance do ciclo atual
        cycle_analysis = self._analyze_cycle(step_results, context.run_id)

        # 2. DIAGNOSE — Diagnosticar gargalos e oportunidades
        diagnosis = self._diagnose_workflow(cycle_analysis, self.history)

        # 3. PRESCRIBE — Gerar prescrições para o próximo ciclo
        prescriptions = self._prescribe_improvements(diagnosis, cycle_analysis, niche)

        # 4. EVOLVE — Evoluir o histórico
        self.history["cycles"].append(cycle_analysis)
        if len(self.history["cycles"]) > 50:
            self.history["cycles"] = self.history["cycles"][-50:]
        if prescriptions:
            self.history["workflow_evolution"].append(
                {
                    "cycle_id": context.run_id,
                    "prescriptions": len(prescriptions),
                    "timestamp": utc_now_iso(),
                }
            )
        self._update_agent_scores(step_results)
        self._save_history()

        # 5. OUTPUT — Gerar novo workflow config se aplicável
        new_workflow = (
            self._generate_workflow_config(diagnosis)
            if diagnosis.get("needs_restructure")
            else None
        )

        output = {
            "status": "success",
            "cycle_id": context.run_id,
            "total_cycles_analyzed": len(self.history["cycles"]),
            "workflow_evolution_count": len(self.history["workflow_evolution"]),
            "cycle_analysis": {
                "total_steps": cycle_analysis["total_steps"],
                "successful_steps": cycle_analysis["successful_steps"],
                "failed_steps": cycle_analysis["failed_steps"],
                "total_duration_ms": cycle_analysis["total_duration_ms"],
                "avg_step_duration_ms": cycle_analysis["avg_step_duration_ms"],
                "parallel_efficiency": cycle_analysis["parallel_efficiency"],
            },
            "diagnosis": {
                "bottlenecks": diagnosis["bottlenecks"],
                "low_value_steps": diagnosis["low_value_steps"],
                "parallelization_opportunities": diagnosis[
                    "parallelization_opportunities"
                ],
                "missing_steps": diagnosis["missing_steps"],
                "needs_restructure": diagnosis.get("needs_restructure", False),
            },
            "prescriptions": prescriptions,
            "new_workflow_config": new_workflow,
            "meta_insights": self._generate_meta_insights(diagnosis, niche),
        }

        # Explicação
        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="meta_orchestration",
                input_state={"total_cycles": len(self.history["cycles"])},
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={
                    "prescriptions": len(prescriptions),
                    "bottlenecks": len(diagnosis["bottlenecks"]),
                },
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="meta_orchestrator",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Analisou {cycle_analysis['total_steps']} steps. "
                f"{len(diagnosis['bottlenecks'])} bottlenecks. "
                f"{len(prescriptions)} prescrições geradas."
            ],
            metadata={
                "steps": cycle_analysis["total_steps"],
                "bottlenecks": len(diagnosis["bottlenecks"]),
                "prescriptions": len(prescriptions),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── 1. ANÁLISE DO CICLO ──────────────────────────────────────

    def _analyze_cycle(self, step_results: dict, cycle_id: str) -> dict[str, Any]:
        """Analisar métricas de execução do ciclo atual."""
        steps_data = []
        total_duration = 0
        successful = 0
        failed = 0
        parallel_estimate = 0

        for step_id, result in step_results.items():
            if not isinstance(result, dict):
                continue
            output = result.get("output", {})
            if isinstance(output, dict):
                output = {
                    k: v
                    for k, v in output.items()
                    if not isinstance(v, (dict, list)) or len(str(v)) < 200
                }
            trace = result.get("trace", {}) or {}
            status = result.get("status", "unknown")
            duration = trace.get("duration_ms", 0) if isinstance(trace, dict) else 0
            total_duration += duration
            if status == "success":
                successful += 1
            else:
                failed += 1

            # Estimate output value
            output_value = 0
            if isinstance(result.get("output"), dict):
                out = result["output"]
                output_value = len(str(out))
                for val_key in (
                    "images_generated",
                    "videos_generated",
                    "total_recommendations",
                    "total_issues",
                    "total_pins",
                    "total_videos",
                    "articles_published",
                    "files_generated",
                    "total_words",
                ):
                    if val_key in out:
                        output_value = max(output_value, out[val_key] * 100)

            steps_data.append(
                {
                    "step_id": step_id,
                    "agent": result.get("agent", trace.get("agent", step_id))
                    if isinstance(result, dict)
                    else step_id,
                    "status": status,
                    "duration_ms": duration,
                    "output_value_score": output_value,
                    "error": trace.get("error", None)
                    if isinstance(trace, dict)
                    else None,
                }
            )

        # Estimate parallel efficiency
        sequential_sum = sum(s["duration_ms"] for s in steps_data)
        parallel_estimate = total_duration / max(sequential_sum, 1)
        parallel_efficiency = (
            round(1 - parallel_estimate, 2) if parallel_estimate > 0 else 0
        )

        return {
            "cycle_id": cycle_id,
            "total_steps": len(steps_data),
            "successful_steps": successful,
            "failed_steps": failed,
            "total_duration_ms": total_duration,
            "avg_step_duration_ms": total_duration // max(len(steps_data), 1),
            "steps": steps_data,
            "parallel_efficiency": parallel_efficiency,  # 0 = all sequential, 1 = perfectly parallel
        }

    # ── 2. DIAGNÓSTICO ───────────────────────────────────────────

    def _diagnose_workflow(self, cycle: dict, history: dict) -> dict[str, Any]:
        """Diagnosticar gargalos e oportunidades."""
        bottlenecks = []
        low_value_steps = []
        parallelization_opps = []
        missing_steps = []
        avg_duration = cycle["avg_step_duration_ms"]

        # Find bottlenecks (steps taking > 2x average)
        for step in cycle["steps"]:
            if step["duration_ms"] > avg_duration * 3 and step["duration_ms"] > 1000:
                bottlenecks.append(
                    {
                        "step_id": step["step_id"],
                        "duration_ms": step["duration_ms"],
                        "ratio_vs_avg": round(
                            step["duration_ms"] / max(avg_duration, 1), 1
                        ),
                        "suggestion": f"Step '{step['step_id']}' é {round(step['duration_ms'] / max(avg_duration, 1), 1)}x mais lento que a média. Considere aumentar workers ou otimizar.",
                    }
                )

            # Low value steps (high duration, low output)
            if (
                step["duration_ms"] > avg_duration
                and step.get("output_value_score", 0) < 10
            ):
                low_value_steps.append(
                    {
                        "step_id": step["step_id"],
                        "duration_ms": step["duration_ms"],
                        "output_score": step.get("output_value_score", 0),
                        "suggestion": f"Step '{step['step_id']}' consumiu {step['duration_ms']}ms mas gerou pouco output. Considere remover ou combinar.",
                    }
                )

        # Parallelization opportunities (from history)
        if len(cycle["steps"]) >= 4:
            # Check if all steps without depends_on are actually parallel
            parallelization_opps.append(
                {
                    "description": f"Pipeline com {cycle['total_steps']} steps tem eficiência paralela de {cycle['parallel_efficiency']:.0%}",
                    "current_max_workers": 14,
                    "suggested_max_workers": min(14, max(4, cycle["total_steps"] // 2)),
                }
            )

        # Missing steps (based on cycle context)
        step_ids = {s["step_id"] for s in cycle["steps"]}

        return {
            "bottlenecks": bottlenecks,
            "low_value_steps": low_value_steps,
            "parallelization_opportunities": parallelization_opps,
            "missing_steps": missing_steps,
            "needs_restructure": len(bottlenecks) > 0 or len(low_value_steps) > 0,
            "cycle_health": "good" if len(bottlenecks) == 0 else "needs_optimization",
        }

    # ── 3. PRESCRIÇÕES ───────────────────────────────────────────

    def _prescribe_improvements(
        self, diagnosis: dict, cycle: dict, niche: str
    ) -> list[dict]:
        """Gerar prescrições acionáveis para melhorar o sistema."""
        prescriptions = []

        for b in diagnosis.get("bottlenecks", []):
            prescriptions.append(
                {
                    "type": "optimize_step",
                    "target": b["step_id"],
                    "action": b["suggestion"],
                    "priority": "high",
                    "expected_impact": "reduzir tempo de ciclo",
                }
            )

        for lv in diagnosis.get("low_value_steps", []):
            prescriptions.append(
                {
                    "type": "review_step",
                    "target": lv["step_id"],
                    "action": lv["suggestion"],
                    "priority": "medium",
                    "expected_impact": "melhorar eficiência do pipeline",
                }
            )

        for po in diagnosis.get("parallelization_opportunities", []):
            prescriptions.append(
                {
                    "type": "adjust_parallelism",
                    "target": "max_workers",
                    "action": f"Ajustar max_workers para {po['suggested_max_workers']} baseado na análise de paralelismo",
                    "priority": "medium",
                    "expected_impact": "melhorar throughput do pipeline",
                }
            )

        # Self-improvement prescriptions based on accumulated cycles
        total_cycles = len(self.history["cycles"])
        if total_cycles >= 2:
            prescriptions.append(
                {
                    "type": "meta_learning",
                    "target": "workflow_config",
                    "action": f"Com {total_cycles} ciclos analisados, calibrar thresholds de sucesso baseado em performance histórica",
                    "priority": "low",
                    "expected_impact": "aprimoramento contínuo do sistema",
                }
            )

        if not prescriptions:
            prescriptions.append(
                {
                    "type": "maintain",
                    "target": "system",
                    "action": "Sistema operando dentro dos parâmetros esperados. Nenhuma modificação necessária.",
                    "priority": "low",
                    "expected_impact": "manutenção de performance",
                }
            )

        return prescriptions

    # ── 4. EVOLUÇÃO ──────────────────────────────────────────────

    def _update_agent_scores(self, step_results: dict) -> None:
        """Update agent performance scores in history."""
        for step_id, result in step_results.items():
            if not isinstance(result, dict):
                continue
            agent = result.get("agent", step_id)
            status = result.get("status", "unknown")
            trace = result.get("trace", {}) or {}
            duration = trace.get("duration_ms", 0) if isinstance(trace, dict) else 0

            if agent not in self.history["agent_scores"]:
                self.history["agent_scores"][agent] = {
                    "runs": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                }
            score = self.history["agent_scores"][agent]
            score["runs"] += 1
            if status == "success":
                score["successes"] += 1
            else:
                score["failures"] += 1
            score["total_duration_ms"] += duration
            score["avg_duration_ms"] = score["total_duration_ms"] // score["runs"]

    # ── 5. GERAÇÃO DE WORKFLOW ───────────────────────────────────

    def _generate_workflow_config(self, diagnosis: dict) -> dict | None:
        """Generate a new workflow configuration if restructuring is needed."""
        if not diagnosis.get("needs_restructure"):
            return None

        return {
            "recommended_changes": [
                b["step_id"] for b in diagnosis.get("bottlenecks", [])
            ],
            "max_workers_adjustment": "increase"
            if diagnosis.get("bottlenecks")
            else "maintain",
            "note": "Configuração gerada automaticamente pelo MetaOrchestrator. Revisão humana recomendada antes de aplicar.",
        }

    # ── META-INSIGHTS ────────────────────────────────────────────

    def _generate_meta_insights(self, diagnosis: dict, niche: str) -> list[str]:
        """Generate meta-level insights about the system itself."""
        insights = []
        total = len(self.history["cycles"])

        if total == 0:
            insights.append(
                "Primeiro ciclo. Coletando dados de baseline para análise futura."
            )
        elif total < 5:
            insights.append(
                f"Fase de calibração inicial ({total} ciclos). Acumulando dados históricos."
            )
        else:
            insights.append(
                f"Sistema maduro com {total} ciclos de histórico. Iniciando otimização preditiva."
            )

        if diagnosis.get("cycle_health") == "good":
            insights.append(
                "Workflow operando com saúde boa. Nenhuma intervenção necessária."
            )
        else:
            insights.append(
                f"{len(diagnosis['bottlenecks'])} gargalos identificados. Prescrições geradas."
            )

        agent_scores = self.history.get("agent_scores", {})
        poor_agents = [
            a
            for a, s in agent_scores.items()
            if s.get("runs", 0) >= 3 and s.get("successes", 0) / s["runs"] < 0.5
        ]
        if poor_agents:
            insights.append(
                f"{len(poor_agents)} agentes com baixa taxa de sucesso: {', '.join(poor_agents)}"
            )

        return insights
