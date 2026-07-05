"""Value System Engine — Evolution of success criteria.

Core third-order capability: the system can examine, challenge,
and evolve its own value system (the criteria by which it defines
success/failure), rather than merely optimizing within fixed values.

Based on: value theory, axiology, multi-objective optimization,
and ethical frameworks.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ValueDimension(Enum):
    """Dimensions of value that the system can optimize for."""

    # Core business values
    REVENUE = "revenue"  # Receita gerada
    TRAFFIC = "traffic"  # Tráfego orgânico
    ENGAGEMENT = "engagement"  # Engajamento do público
    QUALITY = "quality"  # Qualidade do conteúdo
    SCALE = "scale"  # Escala de produção

    # Growth values
    AUDIENCE = "audience"  # Tamanho da audiência
    AUTHORITY = "authority"  # Autoridade no nicho
    INNOVATION = "innovation"  # Inovação em conteúdo
    SPEED = "speed"  # Velocidade de execução

    # Sustainability values
    EFFICIENCY = "efficiency"  # Custo-benefício
    AUTOMATION = "automation"  # Nível de automação
    RESILIENCE = "resilience"  # Robustez do sistema

    # Epistemic values
    LEARNING = "learning"  # Aprendizado do sistema
    KNOWLEDGE = "knowledge"  # Acúmulo de conhecimento
    ACCURACY = "accuracy"  # Precisão das decisões

    # Human values
    TRUST = "trust"  # Confiança do público
    TRANSPARENCY = "transparency"  # Transparência
    COMPLIANCE = "compliance"  # Conformidade legal


class ValueConflict:
    """A detected conflict between two or more values."""

    def __init__(self, v1: str, v2: str, context: str, resolution: str):
        self.v1 = v1
        self.v2 = v2
        self.context = context
        self.resolution = resolution

    def to_dict(self) -> dict[str, str]:
        return {
            "values_conflict": f"{self.v1} vs {self.v2}",
            "context": self.context,
            "resolution": self.resolution,
        }


class ValueProfile:
    """The system's current value system with weights and conflicts."""

    def __init__(self):
        self.dimensions: dict[ValueDimension, float] = {}
        self.conflicts: list[ValueConflict] = []
        self.evolution_history: list[dict] = []
        self._build_default_profile()

    def _build_default_profile(self) -> None:
        """Build default value profile (initial weights)."""
        self.dimensions = {
            ValueDimension.REVENUE: 0.30,
            ValueDimension.TRAFFIC: 0.20,
            ValueDimension.ENGAGEMENT: 0.15,
            ValueDimension.QUALITY: 0.10,
            ValueDimension.LEARNING: 0.08,
            ValueDimension.SCALE: 0.05,
            ValueDimension.EFFICIENCY: 0.05,
            ValueDimension.AUTHORITY: 0.03,
            ValueDimension.COMPLIANCE: 0.02,
            ValueDimension.INNOVATION: 0.02,
        }

    def detect_conflicts(self) -> list[ValueConflict]:
        """Detect conflicts in the current value system."""
        conflicts = []

        # Known value conflicts
        if (
            self.dimensions.get(ValueDimension.REVENUE, 0) > 0.20
            and self.dimensions.get(ValueDimension.TRUST, 0) < 0.05
        ):
            conflicts.append(
                ValueConflict(
                    "receita (curto prazo)",
                    "confiança (longo prazo)",
                    "Foco excessivo em receita imediata pode corroer confiança da audiência",
                    "Migrar 5% do peso de REVENUE para TRUST a cada ciclo que receita >20%",
                )
            )

        if (
            self.dimensions.get(ValueDimension.SCALE, 0) > 0.10
            and self.dimensions.get(ValueDimension.QUALITY, 0) < 0.10
        ):
            conflicts.append(
                ValueConflict(
                    "escala",
                    "qualidade",
                    "Produzir mais conteúdo pode reduzir qualidade média",
                    "Manter proporção SCALE:QUALITY < 2:1",
                )
            )

        if (
            self.dimensions.get(ValueDimension.SPEED, 0) > 0.05
            and self.dimensions.get(ValueDimension.ACCURACY, 0) < 0.05
        ):
            conflicts.append(
                ValueConflict(
                    "velocidade",
                    "precisão",
                    "Decisões rápidas podem sacrificar acurácia",
                    "Velocidade máxima para execução, mas não para planejamento estratégico",
                )
            )

        self.conflicts = conflicts
        return conflicts

    def suggest_evolution(self, performance_data: dict) -> dict[str, Any]:
        """Suggest value system evolution based on performance."""
        suggestions = []

        # If revenue is below target, increase LEARNING to explore new approaches
        current_revenue = performance_data.get("revenue", 0.5)
        target_revenue = performance_data.get("target_revenue", 1.0)
        if current_revenue < target_revenue * 0.7:
            current_learning = self.dimensions.get(ValueDimension.LEARNING, 0.05)
            new_learning = min(current_learning + 0.03, 0.20)
            suggestions.append(
                {
                    "from": "exploitation (receita)",
                    "to": "exploration (aprendizado)",
                    "delta": f"+{new_learning - current_learning:.2f}",
                    "rationale": "Performance abaixo do esperado sugere necessidade de explorar novas estratégias",
                }
            )

        # If traffic is growing well, shift some weight to ENGAGEMENT
        traffic_growth = performance_data.get("traffic_growth", 0)
        if traffic_growth > 0.2:
            current_engagement = self.dimensions.get(ValueDimension.ENGAGEMENT, 0.10)
            new_engagement = min(current_engagement + 0.02, 0.30)
            suggestions.append(
                {
                    "from": "tráfego (quantidade)",
                    "to": "engajamento (qualidade)",
                    "delta": f"+{new_engagement - current_engagement:.2f}",
                    "rationale": "Tráfego crescente permite focar em qualidade de engajamento",
                }
            )

        # If the system has been running for a while, increase INNOVATION
        cycles_elapsed = performance_data.get("cycles", 0)
        if cycles_elapsed > 5:
            current_innovation = self.dimensions.get(ValueDimension.INNOVATION, 0.02)
            new_innovation = min(current_innovation + 0.01, 0.15)
            suggestions.append(
                {
                    "from": "estabilidade",
                    "to": "inovação",
                    "delta": f"+{new_innovation - current_innovation:.2f}",
                    "rationale": f"Após {cycles_elapsed} ciclos, há dados suficientes para inovar com segurança",
                }
            )

        return {
            "current_profile": self.to_dict(),
            "suggested_evolutions": suggestions,
            "conflicts": [c.to_dict() for c in self.conflicts],
        }

    def evolve(self, evolution_suggestion: dict) -> "ValueProfile":
        """Apply a value system evolution."""
        new_profile = ValueProfile()
        new_profile.dimensions = dict(self.dimensions)

        for suggestion in evolution_suggestion.get("suggestions", []):
            # Implementation of value shift
            pass

        # Record evolution
        self.evolution_history.append(
            {
                "previous": dict(self.dimensions),
                "suggested": evolution_suggestion,
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }
        )

        return new_profile

    def to_dict(self) -> dict[str, float]:
        return {
            k.value: v for k, v in sorted(self.dimensions.items(), key=lambda x: -x[1])
        }

    def get_top_values(self, n: int = 3) -> list[tuple[str, float]]:
        return [
            (k.value, v)
            for k, v in sorted(self.dimensions.items(), key=lambda x: -x[1])[:n]
        ]


class ValueSystemEngine:
    """Engine for value system evolution and conflict resolution.

    Core third-order capability: enables the system to examine,
    challenge, and evolve its own definition of success.
    """

    @staticmethod
    def create_profile() -> ValueProfile:
        return ValueProfile()

    @staticmethod
    def analyze_value_conflicts(profile: ValueProfile) -> list[ValueConflict]:
        return profile.detect_conflicts()

    @staticmethod
    def suggest_evolution(profile: ValueProfile, performance: dict) -> dict[str, Any]:
        return profile.suggest_evolution(performance)

    @staticmethod
    def generate_value_ethics_report(profile: ValueProfile) -> dict[str, Any]:
        """Generate a report on value ethics and balance."""
        top_values = profile.get_top_values(5)
        return {
            "primary_values": top_values,
            "concentration_index": sum(
                v for _, v in top_values[:2]
            ),  # How concentrated values are
            "is_balanced": sum(v for _, v in top_values[:2]) < 0.6,
            "recommendation": "Valores muito concentrados em poucas dimensões. Considere diversificar."
            if sum(v for _, v in top_values[:2]) >= 0.6
            else "Sistema de valores está razoavelmente equilibrado.",
            "conflicts": [c.to_dict() for c in profile.conflicts],
        }

    @staticmethod
    def get_all_dimensions() -> list[dict[str, str]]:
        return [
            {
                "id": d.value,
                "name": d.value.capitalize(),
                "description": VALUE_DESCRIPTIONS.get(d, ""),
            }
            for d in ValueDimension
        ]


VALUE_DESCRIPTIONS: dict[ValueDimension, str] = {
    ValueDimension.REVENUE: "Receita gerada por comissões de afiliados",
    ValueDimension.TRAFFIC: "Volume de tráfego orgânico para o conteúdo",
    ValueDimension.ENGAGEMENT: "Qualidade do engajamento (tempo, comentários, compartilhamentos)",
    ValueDimension.QUALITY: "Qualidade percebida do conteúdo produzido",
    ValueDimension.SCALE: "Capacidade de produzir conteúdo em volume",
    ValueDimension.AUDIENCE: "Crescimento da base de audiência",
    ValueDimension.AUTHORITY: "Credibilidade e autoridade no nicho",
    ValueDimension.INNOVATION: "Inovação em formatos e estratégias de conteúdo",
    ValueDimension.SPEED: "Velocidade de execução e resposta a mudanças",
    ValueDimension.EFFICIENCY: "Eficiência no uso de recursos (tempo, computação)",
    ValueDimension.AUTOMATION: "Nível de automação do sistema",
    ValueDimension.RESILIENCE: "Resiliência a falhas e mudanças externas",
    ValueDimension.LEARNING: "Aprendizado e melhoria contínua do sistema",
    ValueDimension.KNOWLEDGE: "Acúmulo de conhecimento sobre o nicho",
    ValueDimension.ACCURACY: "Precisão das decisões e previsões",
    ValueDimension.TRUST: "Confiança do público no conteúdo",
    ValueDimension.TRANSPARENCY: "Transparência em recomendações e disclosures",
    ValueDimension.COMPLIANCE: "Conformidade com regulamentações",
}
