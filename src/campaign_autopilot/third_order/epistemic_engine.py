"""Epistemic Engine — Self-questioning and blind-spot detection.

Core third-order capability: the system questions what it knows,
detects its own blind spots, and generates alternative hypotheses
about its domain, its performance, and its own assumptions.

Based on epistemic logic, theory of mind, and critical rationalism.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any


class EpistemicStatus(Enum):
    """Epistemic classification of claims/knowledge."""

    VERIFIED = "verified"  # Confirmed through multiple sources
    INFERRED = "inferred"  # Derived from verified facts
    ASSUMED = "assumed"  # Taken as true without verification
    HYPOTHESIZED = "hypothesized"  # Proposed but untested
    UNKNOWN = "unknown"  # No epistemic position
    CONTRADICTED = "contradicted"  # Evidence against
    UNCERTAIN = "uncertain"  # Conflicting evidence


class BlindSpot:
    """A detected gap or blind spot in the system's knowledge."""

    def __init__(
        self,
        domain: str,
        description: str,
        impact: str,
        severity: str = "medium",
        hypothesis: str = "",
    ):
        self.domain = domain
        self.description = description
        self.impact = impact
        self.severity = severity  # low, medium, high, critical
        self.hypothesis = hypothesis

    def to_dict(self) -> dict[str, str]:
        return {
            "domain": self.domain,
            "description": self.description,
            "impact": self.impact,
            "severity": self.severity,
            "hypothesis": self.hypothesis,
        }


class Hypothesis:
    """An alternative hypothesis or explanation for a phenomenon."""

    def __init__(
        self,
        phenomenon: str,
        current_belief: str,
        alternative: str,
        evidence_for: str,
        confidence: float = 0.5,
    ):
        self.phenomenon = phenomenon
        self.current_belief = current_belief
        self.alternative = alternative
        self.evidence_for = evidence_for
        self.confidence = confidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "phenomenon": self.phenomenon,
            "current_belief": self.current_belief,
            "alternative": self.alternative,
            "evidence_for": self.evidence_for,
            "confidence": self.confidence,
        }


class KnowledgeMap:
    """A map of what the system knows, doesn't know, and assumes."""

    def __init__(self, niche: str):
        self.niche = niche
        self.verified_facts: list[dict] = []
        self.assumptions: list[dict] = []
        self.unknowns: list[dict] = []
        self.blind_spots: list[BlindSpot] = []
        self.hypotheses: list[Hypothesis] = []
        self._build_knowledge_map()

    def _build_knowledge_map(self) -> None:
        """Build initial knowledge map with domain-specific epistemic analysis."""
        # Verified facts about the niche
        self.verified_facts = [
            {
                "claim": f"O mercado de {self.niche} está crescendo",
                "evidence": "Múltiplas fontes de pesquisa de mercado, tendências Google",
            },
            {
                "claim": "Conteúdo orgânico de qualidade gera tráfego sustentável",
                "evidence": "Dados de SEO, Google Analytics, estudos de caso",
            },
            {
                "claim": "Marketing de afiliados requer disclosure",
                "evidence": "Regulamentações legais (LGPD, Código do Consumidor)",
            },
        ]

        # Hidden assumptions
        self.assumptions = [
            {
                "assumption": "O público-alvo prefere conteúdo gratuito a conteúdo pago inicialmente",
                "epistemic_status": "assumed",
                "challenge": "Talvez o público esteja disposto a pagar por curadoria de qualidade",
            },
            {
                "assumption": "SEO é o canal mais eficiente para tráfego orgânico",
                "epistemic_status": "assumed",
                "challenge": "Em nichos saturados, redes sociais podem ter melhor ROI de tempo",
            },
            {
                "assumption": "Conteúdo longo tem melhor performance para SEO",
                "epistemic_status": "assumed",
                "challenge": "Conteúdo curto e direto pode ter maior engajamento em algumas plataformas",
            },
        ]

        # What we don't know
        self.unknowns = [
            {
                "question": "Qual a taxa de conversão real por plataforma (YouTube vs Blog vs TikTok)?",
                "why_unknown": "Não há dados suficientes de conversão atribuída a cada canal",
            },
            {
                "question": "Qual o lifetime value médio de um lead capturado?",
                "why_unknown": "O sistema ainda não fez análise de cohort com dados temporais suficientes",
            },
            {
                "question": "Quais keywords têm melhor intenção de compra no nicho?",
                "why_unknown": "A classificação de intenção é baseada em heurística, não em dados de conversão reais",
            },
        ]

    def identify_blind_spots(
        self, recent_performance: dict | None = None
    ) -> list[BlindSpot]:
        """Detect blind spots based on performance data and epistemic gaps."""
        blind_spots = []

        # Epistemic blind spot 1: confirmation bias
        blind_spots.append(
            BlindSpot(
                domain="epistemology",
                description="Viés de confirmação: o sistema pode estar buscando apenas dados que confirmam suas crenças sobre canais de tráfego",
                impact="Pode superinvestir em canais ineficientes e ignorar oportunidades em canais não testados",
                severity="high",
                hypothesis="Talvez o canal mais eficiente não seja o que mais produzimos conteúdo, mas o que temos menos dados",
            )
        )

        # Epistemic blind spot 2: unknown unknowns
        blind_spots.append(
            BlindSpot(
                domain="market",
                description=f"Mudanças no mercado de {self.niche} que o sistema não antecipou",
                impact="Estratégia baseada em dados defasados pode perder oportunidades emergentes",
                severity="medium",
                hypothesis="O radar de tendências do sistema pode estar calibrado para o passado, não para o futuro",
            )
        )

        # Epistemic blind spot 3: observer effect
        blind_spots.append(
            BlindSpot(
                domain="measurement",
                description="O sistema não mede o impacto de sua própria medição nos resultados (efeito do observador)",
                impact="Métricas podem ser artefatos do próprio sistema de medição, não da realidade",
                severity="high",
                hypothesis="Ao medir performance, o sistema pode estar alterando o comportamento dos agentes de forma não intencional",
            )
        )

        # Performance-based blind spots
        if recent_performance:
            if recent_performance.get("revenue", 0) < recent_performance.get(
                "expected_revenue", 1
            ):
                blind_spots.append(
                    BlindSpot(
                        domain="revenue_model",
                        description="A receita está abaixo do esperado. Pode haver um gap entre conteúdo e conversão.",
                        impact="Continuar produzindo conteúdo sem ajustar conversão pode perpetuar baixa performance",
                        severity="critical",
                        hypothesis="Talvez o problema não seja quantidade de conteúdo, mas alinhamento entre intenção de busca e oferta",
                    )
                )

        self.blind_spots = blind_spots
        return blind_spots

    def generate_alternative_hypotheses(
        self, phenomenon: str, current_belief: str
    ) -> list[Hypothesis]:
        """Generate alternative explanations for a phenomenon."""
        alternatives = [
            Hypothesis(
                phenomenon=phenomenon,
                current_belief=current_belief,
                alternative=f"A causa pode ser o oposto: {_invert_belief(current_belief)}",
                evidence_for="Lógica dialética: toda tese contém sua antítese",
                confidence=0.3,
            ),
            Hypothesis(
                phenomenon=phenomenon,
                current_belief=current_belief,
                alternative="Pode haver uma causa oculta não considerada: fatores externos ao sistema",
                evidence_for="Análise de sistemas complexos frequentemente revela causas não óbvias",
                confidence=0.4,
            ),
            Hypothesis(
                phenomenon=phenomenon,
                current_belief=current_belief,
                alternative="O fenômeno pode ser um artefato da medição, não um fato real",
                evidence_for="Efeito do observador é bem documentado em sistemas de medição",
                confidence=0.35,
            ),
            Hypothesis(
                phenomenon=phenomenon,
                current_belief=current_belief,
                alternative="Pode ser uma combinação de múltiplos fatores agindo em conjunto, não uma causa única",
                evidence_for="Sistemas complexos raramente têm causas únicas",
                confidence=0.5,
            ),
        ]
        self.hypotheses = alternatives
        return alternatives

    def to_dict(self) -> dict[str, Any]:
        return {
            "niche": self.niche,
            "verified_facts": self.verified_facts,
            "assumptions": self.assumptions,
            "unknowns": self.unknowns,
            "blind_spots": [b.to_dict() for b in self.blind_spots],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
        }


def _invert_belief(belief: str) -> str:
    """Simple belief inversion for dialectic analysis."""
    invert_map = {
        "mais": "menos",
        "melhor": "pior",
        "aumenta": "diminui",
        "cresce": "decresce",
        "bom": "ruim",
        "eficiente": "ineficiente",
        "rápido": "devagar",
        "caro": "barato",
        "fácil": "difícil",
        "sempre": "nunca",
        "nunca": "sempre",
        "tudo": "nada",
    }
    words = belief.lower().split()
    inverted = []
    for w in words:
        inverted.append(invert_map.get(w, w))
    return " ".join(inverted)


class EpistemicEngine:
    """Core epistemic engine for third-order self-questioning.

    Capabilities:
    - Map what the system knows/doesn't know/assumes
    - Detect blind spots and cognitive biases
    - Generate alternative hypotheses for phenomena
    - Challenge core assumptions
    - Create epistemic risk assessments
    """

    @staticmethod
    def create_knowledge_map(niche: str) -> KnowledgeMap:
        """Create a knowledge map for a niche."""
        return KnowledgeMap(niche)

    @staticmethod
    def challenge_assumptions(knowledge_map: KnowledgeMap) -> list[dict[str, str]]:
        """Challenge each assumption and provide alternative perspectives."""
        challenges = []
        for assumption in knowledge_map.assumptions:
            challenges.append(
                {
                    "assumption": assumption["assumption"],
                    "current_status": assumption["epistemic_status"],
                    "challenge": assumption.get(
                        "challenge", "Questionar esta suposição"
                    ),
                    "experiment_suggestion": f"Testar a hipótese inversa por {random.choice(['7 dias', '14 dias', '30 dias'])} para coletar evidências",
                }
            )
        return challenges

    @staticmethod
    def generate_epistemic_report(knowledge_map: KnowledgeMap) -> dict[str, Any]:
        """Generate a comprehensive epistemic report."""
        return {
            "verified_facts_count": len(knowledge_map.verified_facts),
            "assumptions_count": len(knowledge_map.assumptions),
            "unknowns_count": len(knowledge_map.unknowns),
            "blind_spots_count": len(knowledge_map.blind_spots),
            "hypotheses_count": len(knowledge_map.hypotheses),
            "epistemic_health_score": _calculate_epistemic_health(knowledge_map),
            "critical_unknowns": [
                u
                for u in knowledge_map.unknowns
                if "conversão" in u["question"].lower()
                or "receita" in u["question"].lower()
            ],
            "high_severity_blind_spots": [
                b.to_dict()
                for b in knowledge_map.blind_spots
                if b.severity in ("high", "critical")
            ],
            "recommended_experiments": _generate_epistemic_experiments(knowledge_map),
        }

    @staticmethod
    def detect_cognitive_biases(recent_decisions: list[dict]) -> list[dict[str, str]]:
        """Detect potential cognitive biases in recent system decisions."""
        biases_detected = []

        # Check for recency bias
        if len(recent_decisions) >= 3:
            recent = recent_decisions[-3:]
            if all(d.get("channel") == recent[0].get("channel") for d in recent):
                biases_detected.append(
                    {
                        "bias": "Viés de Recência",
                        "evidence": "Últimas 3 decisões favorecem o mesmo canal",
                        "impact": "Pode estar ignorando canais igualmente ou mais eficientes",
                        "mitigation": "Forçar variação ou usar dados históricos mais longos para decisão",
                    }
                )

        # Check for anchoring
        if recent_decisions:
            first = recent_decisions[0]
            if any(
                d.get("metric") == first.get("metric") for d in recent_decisions[1:]
            ):
                biases_detected.append(
                    {
                        "bias": "Ancoragem",
                        "evidence": "Decisões subsequentes referenciam a mesma métrica da primeira decisão",
                        "impact": "Pode estar superestimando uma métrica em detrimento de outras",
                        "mitigation": "Usar média ponderada de múltiplas métricas para cada decisão",
                    }
                )

        return biases_detected

    @staticmethod
    def unknown_unknowns_scan(niche: str, recent_results: dict) -> list[dict[str, str]]:
        """Scan for 'unknown unknowns' — things the system doesn't know it doesn't know."""
        scans = [
            {
                "domain": "regulatory",
                "question": "Existem novas regulamentações que impactam o nicho e que o sistema desconhece?",
                "severity": "high",
                "action": "Verificar legislação atualizada de marketing de afiliados e LGPD",
            },
            {
                "domain": "competitive",
                "question": "Concorrentes estão usando estratégias que o sistema não considera?",
                "severity": "medium",
                "action": "Análise competitiva com foco em padrões não utilizados pelo sistema",
            },
            {
                "domain": "technological",
                "question": "Novas ferramentas/plataformas podem tornar a estratégia atual obsoleta?",
                "severity": "medium",
                "action": "Varredura de tendências tecnológicas em marketing digital",
            },
            {
                "domain": "behavioral",
                "question": "O comportamento do público-alvo mudou de formas que o sistema não detectou?",
                "severity": "high",
                "action": "Pesquisa qualitativa com amostra do público-alvo para validar suposições comportamentais",
            },
        ]
        return scans


def _calculate_epistemic_health(km: KnowledgeMap) -> float:
    """Calculate epistemic health score (0-100)."""
    score = 70.0  # Base score
    # Deductions for blind spots
    score -= len(km.blind_spots) * 5
    # Deductions for unknown unknowns
    score -= len(km.unknowns) * 3
    # Bonuses for explicit assumptions (awareness)
    score += min(len(km.assumptions) * 2, 10)
    return max(0, min(100, score))


def _generate_epistemic_experiments(km: KnowledgeMap) -> list[dict[str, str]]:
    """Generate experiments to reduce epistemic uncertainty."""
    experiments = []
    for unknown in km.unknowns[:3]:
        experiments.append(
            {
                "question": unknown["question"],
                "experiment": f"Coletar dados específicos para responder: {unknown['question']}",
                "duration": "30 dias",
                "success_criteria": "Redução da incerteza epistêmica sobre esta questão",
            }
        )
    for assumption in km.assumptions[:2]:
        experiments.append(
            {
                "question": f"Suposição: {assumption['assumption']}",
                "experiment": "Testar A/B: operar com e sem esta suposição por 14 dias",
                "duration": "14 dias",
                "success_criteria": "Evidência estatística para manter ou rejeitar a suposição",
            }
        )
    return experiments
