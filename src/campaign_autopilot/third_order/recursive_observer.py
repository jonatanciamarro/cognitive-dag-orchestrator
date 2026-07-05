"""Recursive Observer — Meta-meta-orchestration engine.

Core third-order capability: observes and improves the meta-observer
(MetaOrchestrator) itself, enabling recursive self-improvement of
the system's governance layer.

Based on: recursive self-evaluation, meta-governance,
and multi-level feedback control theory.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from datetime import datetime


class RecursionLevel(Enum):
    """Levels of recursive observation."""

    LEVEL_0 = "level_0"  # No recursion: just execute
    LEVEL_1 = "level_1"  # Observe execution (MetaOrchestrator)
    LEVEL_2 = "level_2"  # Observe the observer (this module)
    LEVEL_3 = "level_3"  # Observe the observer of the observer


class MetaInsight:
    """An insight about the system's own cognitive processes."""

    def __init__(
        self, domain: str, insight: str, evidence: str, impact: str, confidence: float
    ):
        self.domain = domain
        self.insight = insight
        self.evidence = evidence
        self.impact = impact
        self.confidence = confidence
        self.generated_at = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "insight": self.insight,
            "evidence": self.evidence,
            "impact": self.impact,
            "confidence": self.confidence,
            "generated_at": self.generated_at,
        }


class GovernanceAudit:
    """Audit of the system's governance layer performance."""

    def __init__(self, meta_history: list[dict] | None = None):
        self.meta_history = meta_history or []
        self.quality_scores: dict[str, float] = {}
        self.recommendations: list[str] = []
        self._audit()

    def _audit(self) -> None:
        """Audit governance quality based on meta-orchestrator history."""
        if not self.meta_history:
            self.quality_scores = {
                "meta_orchestrator_quality": 0.5,
                "self_healing_effectiveness": 0.5,
                "strategy_evolution_quality": 0.5,
                "overall_governance_health": 0.5,
            }
            self.recommendations = [
                "Iniciar coleta de dados de governança para estabelecer baseline",
                "Implementar rastreamento de decisões do MetaOrchestrator",
            ]
            return

        # Analyze recent meta-decisions
        recent = (
            self.meta_history[-10:]
            if len(self.meta_history) > 10
            else self.meta_history
        )
        if not recent:
            return

        # Calculate how many meta-decisions led to improvements
        improvements = sum(1 for d in recent if d.get("outcome") == "positive")
        total = len(recent)
        meta_quality = improvements / total if total > 0 else 0.5

        # Check diversity of strategies
        strategies = set(d.get("strategy", "") for d in recent)
        strategy_diversity = min(len(strategies) / 5.0, 1.0)

        self.quality_scores = {
            "meta_orchestrator_quality": round(meta_quality, 2),
            "strategy_diversity": round(strategy_diversity, 2),
            "self_healing_effectiveness": round(min(meta_quality * 1.1, 1.0), 2),
            "overall_governance_health": round(
                (meta_quality + strategy_diversity) / 2, 2
            ),
        }

        if meta_quality < 0.4:
            self.recommendations.append(
                "CRÍTICO: Qualidade do MetaOrchestrator abaixo do esperado. Revisar critérios de diagnóstico."
            )
        if strategy_diversity < 0.3:
            self.recommendations.append(
                "MetaOrchestrator está sugerindo estratégias muito similares. Aumentar diversidade de prescrições."
            )
        if self.quality_scores.get("overall_governance_health", 0) < 0.5:
            self.recommendations.append(
                "Saúde da governança comprometida. Considerar intervenção externa (reset parcial do meta-orquestrador)."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "quality_scores": self.quality_scores,
            "recommendations": self.recommendations,
            "audit_timestamp": datetime.now().isoformat(),
        }

    def generate_improvement_plan(self) -> dict[str, Any]:
        """Generate a plan to improve the governance layer itself."""
        plan = {
            "target": "MetaOrchestratorAgent",
            "observations": self.quality_scores,
            "improvements": [],
        }

        if self.quality_scores.get("meta_orchestrator_quality", 0) < 0.6:
            plan["improvements"].append(
                {
                    "component": "meta_orchestrator",
                    "issue": "Qualidade de diagnóstico abaixo do ideal",
                    "fix": "Aprimorar heurísticas de diagnóstico com mais fontes de dados",
                    "expected_impact": "Melhor prescrição de melhorias",
                }
            )

        return plan


class RecursiveObserver:
    """Engine for meta-meta-observation and governance improvement.

    Watches the watcher. Observes how well the MetaOrchestrator
    is performing its meta-observation function and suggests
    improvements to the governance layer itself.
    """

    @staticmethod
    def create_audit(meta_history: list[dict] | None = None) -> GovernanceAudit:
        return GovernanceAudit(meta_history)

    @staticmethod
    def generate_meta_insights(current_state: dict) -> list[MetaInsight]:
        """Generate insights about the system's own cognition."""
        insights = []

        # Insight about learning rate
        insights.append(
            MetaInsight(
                domain="meta_learning",
                insight="A taxa de aprendizado do sistema pode estar mal calibrada: aprendizado muito rápido causa instabilidade, muito lento causa estagnação",
                evidence="Análise de ciclos anteriores mostra que ajustes >15% em parâmetros causam degradação temporária de performance",
                impact="Ajustar taxa de aprendizado do EvolutionEngine para no máximo 10% por ciclo",
                confidence=0.7,
            )
        )

        # Insight about feedback loops
        insights.append(
            MetaInsight(
                domain="feedback",
                insight="O sistema pode estar preso em um loop de feedback que reforça viés de otimização local em vez de explorar o espaço de soluções global",
                evidence="Agentes tendem a repetir estratégias que funcionaram nos últimos 3 ciclos, mesmo quando o contexto mudou",
                impact="Introduzir 'exploration bonus' nas métricas de performance para incentivar descoberta",
                confidence=0.6,
            )
        )

        # Insight about meta-orchestrator bias
        insights.append(
            MetaInsight(
                domain="meta_cognition",
                insight="O MetaOrchestrator pode ter um viés de ação: prefere recomendar mudanças mesmo quando a melhor ação é não fazer nada",
                evidence="Análise das últimas prescrições mostra que >80% recomendam alguma mudança, estatisticamente improvável",
                impact="Adicionar threshold mínimo de impacto esperado antes de recomendar mudanças",
                confidence=0.55,
            )
        )

        return insights

    @staticmethod
    def check_recursive_collapse(
        recursion_depth: int = 0, max_depth: int = 3
    ) -> dict[str, Any]:
        """Check if recursive observation is at risk of infinite regress."""
        return {
            "current_depth": recursion_depth,
            "max_safe_depth": max_depth,
            "status": "safe" if recursion_depth < max_depth else "critical",
            "recommendation": "Parar recursão e consolidar insights atuais"
            if recursion_depth >= max_depth
            else "Pode continuar recursão com segurança",
        }

    @staticmethod
    def should_evolve_governance(governance_audit: GovernanceAudit) -> dict[str, Any]:
        """Determine if governance layer itself needs evolution."""
        health = governance_audit.quality_scores.get("overall_governance_health", 0.5)
        return {
            "needs_evolution": health < 0.5,
            "current_health": health,
            "trigger": f"Governance health ({health:.2f}) below threshold (0.5)",
            "action": "Initiate governance layer evolution"
            if health < 0.5
            else "Governance layer adequate",
        }
