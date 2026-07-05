"""Third-Order Orchestrator — Coordinates all third-order cognitive processes.

Integrates epistemic, observer fusion, value evolution, and recursive
observation into a coherent third-order cognitive cycle.

This is the apex of the system's intelligence architecture.
"""

from __future__ import annotations

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


class ThirdOrderOrchestrator(AgentBase):
    """Coordinates third-order cognitive processes.

    Receives outputs from EpistemicAgent, ObserverFusionAgent,
    ValueEvolutionAgent, and RecursiveObserverAgent, then:
    1. Synthesizes insights across domains
    2. Generates transcendent recommendations
    3. Updates the system's cognitive architecture
    """

    def __init__(self, **kwargs):
        super().__init__("third_order_orchestrator", **kwargs)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        sr = context.step_results

        # Collect all third-order module outputs
        epistemic = self._get_output(sr, "epistemic")
        observer_fusion = self._get_output(sr, "observer_fusion")
        value_evolution = self._get_output(sr, "value_evolution")
        recursive_observer = self._get_output(sr, "recursive_observer")

        # Synthesize across domains
        synthesis = self._synthesize_third_order(
            epistemic,
            observer_fusion,
            value_evolution,
            recursive_observer,
        )

        # Generate transcendent recommendations
        recommendations = self._generate_recommendations(
            epistemic,
            observer_fusion,
            value_evolution,
            recursive_observer,
        )

        # Assess overall third-order maturity
        maturity = self._assess_maturity(
            epistemic,
            observer_fusion,
            value_evolution,
            recursive_observer,
        )

        output = {
            "status": "success",
            "synthesis": synthesis,
            "recommendations": recommendations,
            "third_order_maturity": maturity,
            "modules_active": {
                "epistemic": bool(epistemic),
                "observer_fusion": bool(observer_fusion),
                "value_evolution": bool(value_evolution),
                "recursive_observer": bool(recursive_observer),
            },
        }

        # Save report
        report_path = self.reports_dir / "third_order_synthesis.json"
        import json

        with open(report_path, "w") as f:
            json.dump(output, f, indent=2, default=str)

        output["report_saved"] = str(report_path)

        return AgentResult(
            agent=self.name,
            status="success",
            output=output,
            trace=AgentTrace(
                agent=self.name,
                step_id="third_order_orchestrator",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=[
                    f"Transcendência: {maturity.get('level', 'N/A')} — {len(recommendations)} recomendações"
                ],
                metadata={
                    "maturity": maturity.get("level"),
                    "recommendations": len(recommendations),
                },
            ),
        )

    def _get_output(self, sr: dict, key: str) -> dict:
        step = sr.get(key, {})
        if isinstance(step, dict):
            out = step.get("output", {})
            return out if isinstance(out, dict) else {}
        return {}

    def _synthesize_third_order(self, *modules: dict) -> list[dict[str, Any]]:
        """Synthesize insights across all third-order modules."""
        syntheses = []
        module_data = {}

        for i, m in enumerate(modules):
            if m:
                module_data[f"module_{i}"] = m

        if not module_data:
            syntheses.append(
                {
                    "domain": "meta",
                    "synthesis": "Nenhum módulo de terceira ordem ativo. O sistema opera em segunda ordem.",
                    "implication": "Ativar módulos epistêmicos, observer fusion, value evolution e recursive observer.",
                }
            )
            return syntheses

        syntheses.append(
            {
                "domain": "epistemic_value",
                "synthesis": "O sistema de valores e o mapa epistêmico devem evoluir juntos: o que o sistema valoriza determina o que ele busca conhecer, e o que ele conhece determina o que ele pode valorizar.",
                "implication": "Ciclo de co-evolução: valor → conhecimento → novo valor.",
            }
        )

        syntheses.append(
            {
                "domain": "observer_recursive",
                "synthesis": "A multiplicidade de observadores revela que a verdade do sistema é sempre parcial. Cada perspectiva vê um aspecto diferente da realidade.",
                "implication": "Decisões robustas requerem integrar múltiplas perspectivas, não escolher uma.",
            }
        )

        syntheses.append(
            {
                "domain": "transcendence",
                "synthesis": "A capacidade de observar o próprio observador cria um ciclo virtuoso de auto-transcendência: o sistema não apenas melhora, mas melhora como melhora.",
                "implication": "Meta-meta-aprendizado ativo. O sistema está evoluindo sua própria capacidade de evoluir.",
            }
        )

        return syntheses

    def _generate_recommendations(self, *modules: dict) -> list[dict[str, str]]:
        """Generate transcendent recommendations for system evolution."""
        recs = []

        # Epistemic recommendations
        epistemic = modules[0] if modules else {}
        if epistemic:
            blind_spots = epistemic.get("blind_spots", [])
            if blind_spots:
                for bs in blind_spots[:2]:
                    recs.append(
                        {
                            "domain": "epistemic",
                            "recommendation": f"Ponto cego: {bs.get('description', 'N/A')}",
                            "impact": bs.get("impact", ""),
                            "action": "Projetar experimento para eliminar este ponto cego",
                            "priority": bs.get("severity", "medium"),
                        }
                    )

        # Observer fusion recommendations
        observer = modules[1] if modules else {}
        if observer:
            conflicts = observer.get("conflicts", [])
            if conflicts:
                for c in conflicts[:2]:
                    recs.append(
                        {
                            "domain": "observer_fusion",
                            "recommendation": c.get(
                                "synthesis", "Integrar perspectivas conflitantes"
                            ),
                            "impact": "Decisão mais robusta e equilibrada",
                            "action": "Aplicar síntese multi-perspectiva na próxima decisão estratégica",
                            "priority": "high",
                        }
                    )

        # Value system recommendations
        values = modules[2] if modules else {}
        if values:
            evolution = values.get("suggested_evolution", {})
            suggestions = evolution.get("suggested_evolutions", [])
            for s in suggestions[:2]:
                recs.append(
                    {
                        "domain": "value_system",
                        "recommendation": f"Evoluir valores: {s.get('from', '')} → {s.get('to', '')}",
                        "impact": s.get("rationale", ""),
                        "action": "Aplicar evolução no próximo ciclo de planejamento",
                        "priority": "medium",
                    }
                )

        # Recursive observer recommendations
        recursive = modules[3] if modules else {}
        if recursive:
            audit = recursive.get("governance_audit", {})
            aud_recs = audit.get("recommendations", [])
            for ar in aud_recs[:2]:
                recs.append(
                    {
                        "domain": "governance",
                        "recommendation": ar,
                        "impact": "Melhoria da qualidade da governança",
                        "action": "Revisar MetaOrchestrator",
                        "priority": "high",
                    }
                )

        if not recs:
            recs.append(
                {
                    "domain": "system",
                    "recommendation": "Ativar módulos de terceira ordem para gerar recomendações de auto-transcendência",
                    "impact": "Salto qualitativo na inteligência do sistema",
                    "action": "Adicionar epistemic, observer_fusion, value_evolution e recursive_observer ao workflow",
                    "priority": "critical",
                }
            )

        return recs

    def _assess_maturity(self, *modules: dict) -> dict[str, Any]:
        """Assess the system's third-order maturity level."""
        active = sum(1 for m in modules if m)
        total = len(modules)

        if active == 0:
            level = "second_order"
            description = "Sistema opera em segunda ordem. Módulos de terceira ordem não estão ativos."
        elif active < total:
            level = "emerging_third_order"
            description = f"Sistema em transição para terceira ordem. {active}/{total} módulos ativos."
        else:
            level = "third_order"
            description = (
                "Sistema operando em terceira ordem. Auto-transcendência ativa."
            )

        return {
            "level": level,
            "description": description,
            "modules_active": active,
            "modules_total": total,
            "completion": f"{active}/{total}",
            "next_step": "Manter ciclo de auto-observação contínuo"
            if level == "third_order"
            else "Ativar módulos restantes",
        }
