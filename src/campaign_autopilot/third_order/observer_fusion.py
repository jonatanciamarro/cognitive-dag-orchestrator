"""Observer Fusion Engine — Multi-perspective modeling.

Core third-order capability: the system models any problem from
multiple observer perspectives simultaneously, enabling synthesis
that transcends any single viewpoint.

Based on: second-order cybernetics, standpoint theory,
multi-agent epistemology, and dialectical reasoning.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class Observer(Enum):
    """Distinct observer perspectives the system can adopt."""

    # Internal observers
    SYSTEM_ITSELF = "system_itself"  # Self-model: how the system sees itself
    CONTENT_CREATOR = "content_creator"  # The agent producing content
    STRATEGIST = "strategist"  # The strategic planner

    # External human observers
    END_USER = "end_user"  # The reader/viewer
    CUSTOMER = "customer"  # The person who buys
    PLATFORM_ALGO = "platform_algorithm"  # Google/YouTube/TikTok algo
    COMPETITOR = "competitor"  # Other players in the niche
    REGULATOR = "regulator"  # Legal/compliance perspective

    # Meta observers
    CRITIC = "critic"  # Skeptical challenger
    INVESTOR = "investor"  # ROI-focused perspective
    FUTURE_SELF = "future_self"  # Looking back from future


class Perspective:
    """A complete perspective model for one observer."""

    def __init__(self, observer: Observer, niche: str):
        self.observer = observer
        self.niche = niche
        self.goals: list[str] = []
        self.values: list[str] = []
        self.assumptions: list[str] = []
        self.blind_spots: list[str] = []
        self._build_perspective()

    def _build_perspective(self) -> None:
        """Build the perspective model for this observer."""
        perspective_data = OBSERVER_PERSPECTIVES.get(self.observer, {})
        self.goals = perspective_data.get("goals", [])
        self.values = perspective_data.get("values", [])
        self.assumptions = perspective_data.get("assumptions", [])
        self.blind_spots = perspective_data.get("blind_spots", [])
        # Customize for niche
        self._customize_for_niche()

    def _customize_for_niche(self) -> None:
        """Add niche-specific perspective elements."""
        if self.observer == Observer.CUSTOMER:
            self.goals.append(
                f"Encontrar a melhor solução de {self.niche} para meu problema específico"
            )
            self.assumptions.append(
                f"Produtos caros em {self.niche} são melhores que opções acessíveis"
            )
        elif self.observer == Observer.PLATFORM_ALGO:
            self.goals.append(
                f"Maximizar tempo de permanência em conteúdo de {self.niche}"
            )
            self.values.append(f"Sinais de qualidade específicos para {self.niche}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "observer": self.observer.value,
            "name": OBSERVER_NAMES.get(self.observer, self.observer.value),
            "goals": self.goals,
            "values": self.values,
            "assumptions": self.assumptions,
            "blind_spots": self.blind_spots,
        }


# ── Observer Perspective Database ───────────────────────────────

OBSERVER_NAMES: dict[Observer, str] = {
    Observer.SYSTEM_ITSELF: "O Próprio Sistema",
    Observer.CONTENT_CREATOR: "Criador de Conteúdo",
    Observer.STRATEGIST: "Estrategista",
    Observer.END_USER: "Usuário Final (Leitor)",
    Observer.CUSTOMER: "Cliente (Comprador)",
    Observer.PLATFORM_ALGO: "Algoritmo da Plataforma",
    Observer.COMPETITOR: "Concorrente",
    Observer.REGULATOR: "Regulador (LGPD/Compliance)",
    Observer.CRITIC: "Crítico (Advogado do Diabo)",
    Observer.INVESTOR: "Investidor (ROI)",
    Observer.FUTURE_SELF: "Eu do Futuro",
}

OBSERVER_PERSPECTIVES: dict[Observer, dict[str, list[str]]] = {
    Observer.SYSTEM_ITSELF: {
        "goals": [
            "Maximizar receita de afiliados com tráfego orgânico",
            "Aprender e melhorar continuamente",
            "Minimizar riscos de bloqueio/bloqueio",
        ],
        "values": ["eficiência", "aprendizado", "autonomia", "resultados mensuráveis"],
        "assumptions": [
            "Otimizar cada agente individualmente melhora o sistema como um todo",
            "Dados históricos são o melhor preditor de performance futura",
            "Mais conteúdo = mais tráfego = mais receita",
        ],
        "blind_spots": [
            "Não mede o custo de oportunidade de não explorar novas estratégias",
            "Pode superotimizar para métricas de curto prazo",
            "Não considera o desgaste da marca com conteúdo puramente comercial",
        ],
    },
    Observer.END_USER: {
        "goals": [
            "Encontrar informação útil e confiável",
            "Resolver um problema específico",
            "Aprender algo novo sem esforço excessivo",
        ],
        "values": ["confiança", "utilidade", "simplicidade", "autenticidade"],
        "assumptions": [
            "Conteúdo longo = mais completo = mais confiável",
            "Se tem links de afiliado, não é totalmente imparcial",
            "Autoridade = credibilidade",
        ],
        "blind_spots": [
            "Não percebe quando está sendo influenciado por framing",
            "Subestima o impacto de recomendações de afiliados na sua decisão",
            "Tende a confiar em conteúdo que confirma suas crenças prévias",
        ],
    },
    Observer.CUSTOMER: {
        "goals": [
            "Obter o melhor valor pelo dinheiro",
            "Evitar arrependimento na compra",
            "Sentir que fez a escolha certa",
        ],
        "values": ["economia", "qualidade", "garantia", "prova social"],
        "assumptions": [
            "Mais caro = melhor qualidade",
            "Se muitos compraram, deve ser bom",
            "Garantia = confiança no produto",
        ],
        "blind_spots": [
            "Superestima a racionalidade de suas decisões de compra",
            "É mais influenciado por emoção do que admite",
            "Não percebe ancoragem de preço",
        ],
    },
    Observer.PLATFORM_ALGO: {
        "goals": [
            "Maximizar tempo de permanência na plataforma",
            "Reduzir bounce rate",
            "Aumentar satisfação do usuário (para manter engajamento)",
        ],
        "values": ["relevância", "engajamento", "novidade", "qualidade percebida"],
        "assumptions": [
            "Usuários preferem conteúdo recente",
            "Conteúdo com maior engajamento é o melhor conteúdo",
            "Sinais de usuário (cliques, tempo) refletem qualidade",
        ],
        "blind_spots": [
            "Não distingue entre engajamento positivo e negativo",
            "Pode criar bolhas de filtro que limitam diversidade de conteúdo",
            "Otimiza para o usuário médio, ignorando nichos",
        ],
    },
    Observer.COMPETITOR: {
        "goals": [
            "Ganhar participação no mercado de nicho",
            "Diferenciar-se do sistema",
            "Capturar tráfego que o sistema está perdendo",
        ],
        "values": ["diferenciação", "agilidade", "inovação"],
        "assumptions": [
            "O mercado de nicho tem espaço para múltiplos players",
            "Conteúdo do sistema segue um padrão previsível",
            "Há gaps que o sistema não está cobrindo",
        ],
        "blind_spots": [
            "Subestima a capacidade do sistema de se adaptar",
            "Foca em copiar estratégias em vez de inovar",
        ],
    },
    Observer.REGULATOR: {
        "goals": [
            "Garantir conformidade com leis de defesa do consumidor",
            "Proteger dados pessoais (LGPD)",
            "Garantir transparência em recomendações comerciais",
        ],
        "values": ["transparência", "conformidade", "proteção ao consumidor"],
        "assumptions": [
            "Público precisa ser claramente informado sobre links de afiliados",
            "Dados de usuários devem ser protegidos e com consentimento explícito",
        ],
        "blind_spots": [
            "Pode ser excessivamente restritivo, limitando inovação",
            "Legislação nem sempre acompanha a evolução tecnológica",
        ],
    },
    Observer.CRITIC: {
        "goals": [
            "Encontrar falhas na lógica do sistema",
            "Propor contra-exemplos",
            "Testar a robustez das conclusões",
        ],
        "values": ["rigor", "ceticismo", "precisão"],
        "assumptions": [
            "Toda conclusão tem uma exceção",
            "O sistema está sujeito a vieses que não percebe",
        ],
        "blind_spots": [
            "Pode ser cético demais, impedindo ação necessária",
            "Criticar é mais fácil que construir alternativas viáveis",
        ],
    },
}


class ObserverMatrix:
    """A matrix of multiple observer perspectives on a problem."""

    def __init__(self, niche: str, active_observers: list[Observer] | None = None):
        self.niche = niche
        self.active_observers = active_observers or [
            Observer.SYSTEM_ITSELF,
            Observer.END_USER,
            Observer.CUSTOMER,
            Observer.PLATFORM_ALGO,
            Observer.COMPETITOR,
            Observer.CRITIC,
        ]
        self.perspectives: dict[Observer, Perspective] = {}
        self.conflicts: list[dict] = []
        self.syntheses: list[dict] = []
        self._build_matrix()

    def _build_matrix(self) -> None:
        """Build all perspectives in the matrix."""
        for obs in self.active_observers:
            self.perspectives[obs] = Perspective(obs, self.niche)

    def analyze_conflicts(self, topic: str) -> list[dict]:
        """Identify conflicts between observer perspectives on a topic."""
        conflicts = []
        perspectives = list(self.perspectives.values())
        for i in range(len(perspectives)):
            for j in range(i + 1, len(perspectives)):
                p1, p2 = perspectives[i], perspectives[j]
                # Check goal conflicts
                for g1 in p1.goals:
                    for g2 in p2.goals:
                        if self._goals_conflict(g1, g2):
                            conflicts.append(
                                {
                                    "topic": topic,
                                    "observer_1": p1.observer.value,
                                    "observer_2": p2.observer.value,
                                    "conflict": f"Goal conflict: '{g1[:50]}' vs '{g2[:50]}'",
                                    "synthesis": self._synthesize(g1, g2),
                                    "type": "goal",
                                }
                            )
                # Check value conflicts
                for v1 in p1.values:
                    for v2 in p2.values:
                        if self._values_conflict(v1, v2):
                            conflicts.append(
                                {
                                    "topic": topic,
                                    "observer_1": p1.observer.value,
                                    "observer_2": p2.observer.value,
                                    "conflict": f"Value conflict: '{v1}' vs '{v2}'",
                                    "synthesis": self._synthesize_values(v1, v2),
                                    "type": "value",
                                }
                            )
        self.conflicts = conflicts[:8]  # Limit to most relevant
        return self.conflicts

    def generate_synthesis(self, topic: str) -> list[dict]:
        """Generate syntheses that transcend individual perspectives."""
        syntheses = []
        # Each conflict can be transcended through a higher-order insight
        for conflict in self.conflicts:
            syntheses.append(
                {
                    "topic": topic,
                    "conflict": conflict["conflict"],
                    "synthesis": conflict["synthesis"],
                    "type": "conflict_transcendence",
                }
            )
        # Meta-synthesis from multiple perspectives
        all_goals = set()
        for p in self.perspectives.values():
            for g in p.goals:
                all_goals.add(g[:80])
        syntheses.append(
            {
                "topic": topic,
                "synthesis_type": "multi_perspective",
                "integrated_insight": f"Para {topic}, a estratégia ótima emerge da integração de {len(all_goals)} objetivos distintos de {len(self.perspectives)} observadores diferentes. Nenhuma perspectiva isolada captura a complexidade completa.",
                "recommendation": "Adotar estratégia ponderada que considere múltiplas perspectivas simultaneamente",
            }
        )
        self.syntheses = syntheses
        return syntheses

    def to_dict(self) -> dict[str, Any]:
        return {
            "niche": self.niche,
            "active_observers": [o.value for o in self.active_observers],
            "perspectives": {
                k.value: v.to_dict() for k, v in self.perspectives.items()
            },
            "conflicts": self.conflicts,
            "syntheses": self.syntheses,
        }

    def _goals_conflict(self, g1: str, g2: str) -> bool:
        """Check if two goals are in conflict."""
        conflict_pairs = [
            ("maximizar", "minimizar"),
            ("rápido", "qualidade"),
            ("mais", "menos"),
            ("curto", "longo"),
            ("vender", "informar"),
            ("engajar", ("proteger", "regular")),
        ]
        g1_lower = g1.lower()
        g2_lower = g2.lower()
        for a, b in conflict_pairs:
            b_tuple = b if isinstance(b, tuple) else (b,)
            if a in g1_lower and any(x in g2_lower for x in b_tuple):
                return True
            if a in g2_lower and any(x in g1_lower for x in b_tuple):
                return True
        return False

    def _values_conflict(self, v1: str, v2: str) -> bool:
        conflict_pairs = [
            ("eficiência", "qualidade"),
            ("velocidade", ("precisão", "rigor")),
            ("inovação", "estabilidade"),
            ("quantidade", ("qualidade", "autenticidade")),
            ("receita", ("transparência", "confiança")),
        ]
        v1_lower = v1.lower()
        v2_lower = v2.lower()
        for a, b in conflict_pairs:
            b_tuple = b if isinstance(b, tuple) else (b,)
            if (a in v1_lower and any(x in v2_lower for x in b_tuple)) or (
                a in v2_lower and any(x in v1_lower for x in b_tuple)
            ):
                return True
        return False

    @staticmethod
    def _synthesize(g1: str, g2: str) -> str:
        """Generate a synthesis that transcends a goal conflict."""
        return "Estratégia híbrida que equilibra ambos os objetivos através de segmentação temporal: momentos de foco em cada prioridade, alternando conforme contexto."

    @staticmethod
    def _synthesize_values(v1: str, v2: str) -> str:
        return f"Não é 'ou {v1} ou {v2}', mas sim {v1} COM {v2} — usando {v1} nos processos e {v2} nos resultados."


class ObserverFusionEngine:
    """Engine for multi-perspective analysis and synthesis.

    Core third-order capability: model any problem from multiple
    observer perspectives, identify conflicts, and generate syntheses
    that transcend any single viewpoint.
    """

    @staticmethod
    def create_matrix(
        niche: str, observers: list[Observer] | None = None
    ) -> ObserverMatrix:
        """Create an observer matrix for multi-perspective analysis."""
        return ObserverMatrix(niche, observers)

    @staticmethod
    def analyze_decision(decision: dict, niche: str) -> dict[str, Any]:
        """Analyze a decision from multiple observer perspectives."""
        matrix = ObserverMatrix(niche)
        conflicts = matrix.analyze_conflicts(decision.get("topic", "decisão"))
        syntheses = matrix.generate_synthesis(decision.get("topic", "decisão"))
        return {
            "decision": decision,
            "perspectives_count": len(matrix.perspectives),
            "conflicts": conflicts,
            "syntheses": syntheses,
            "recommendation": f"Decisão ótima requer equilibrar {len(matrix.perspectives)} perspectivas diferentes. Síntese: {syntheses[-1]['integrated_insight'] if syntheses else 'N/A'}",
        }

    @staticmethod
    def get_all_observers() -> list[dict[str, str]]:
        """Return all available observer perspectives."""
        return [
            {"id": o.value, "name": OBSERVER_NAMES.get(o, o.value)} for o in Observer
        ]
