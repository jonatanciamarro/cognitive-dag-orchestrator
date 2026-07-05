"""Psychology Engine — cognitive biases, persuasion principles, and psychological triggers.

Based on established psychological research:
- Cialdini's 6 Principles of Persuasion
- Kahneman's System 1/System 2
- Cognitive biases (100+ documented)
- Behavioral psychology (Fogg Behavior Model)
- Motivation and emotion psychology

For affiliate marketing content optimization.
"""

from __future__ import annotations

from enum import Enum


class CognitiveBias(Enum):
    """Cognitive biases relevant to marketing and persuasion."""

    # Social biases
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    LIKING = "liking"
    CONSENSUS = "consensus"

    # Decision biases
    LOSS_AVERSION = "loss_aversion"
    SCARCITY = "scarcity"
    ANCHORING = "anchoring"
    DRO = "dread_of_regret"  # Dread Of Regret / FOMO
    DECOY = "decoy_effect"

    # Cognitive biases
    CONFIRMATION = "confirmation_bias"
    AVAILABILITY = "availability_heuristic"
    RECENCY = "recency_bias"
    HALO = "halo_effect"
    ENDOWMENT = "endowment_effect"
    DUNNING_KRUGER = "dunning_kruger"

    # Commitment biases
    CONSISTENCY = "consistency"
    COMMITMENT = "commitment"
    FOOT_IN_DOOR = "foot_in_door"
    DOOR_IN_FACE = "door_in_face"

    # Framing biases
    FRAMING = "framing_effect"
    ZERO_RISK = "zero_risk_bias"
    SUNK_COST = "sunk_cost"
    OPTIMISM = "optimism_bias"


class PersuasionPrinciple(Enum):
    """Cialdini's 7 Principles of Persuasion."""

    RECIPROCITY = "reciprocity"
    SCARCITY = "scarcity"
    AUTHORITY = "authority"
    CONSISTENCY = "consistency"
    LIKING = "liking"
    SOCIAL_PROOF = "social_proof"
    UNITY = "unity"  # 7th principle (newest)


class PsychologicalTrigger(Enum):
    """Deep psychological triggers for content."""

    # Core emotions
    FEAR = "fear"
    GREED = "greed"
    VANITY = "vanity"
    GUILT = "guilt"
    SHAME = "shame"
    PRIDE = "pride"
    CURIOSITY = "curiosity"
    BELONGING = "belonging"
    CONTROL = "control"
    CERTAINTY = "certainty"
    SIGNIFICANCE = "significance"

    # Deep needs
    AUTONOMY = "autonomy"
    COMPETENCE = "competence"
    RELATEDNESS = "relatedness"
    MEANING = "meaning"
    MASTERY = "mastery"


class PersuasiveProfile:
    """Complete persuasion profile for a content piece."""

    def __init__(self, niche: str, audience: str):
        self.niche = niche
        self.audience = audience
        self.biases: list[CognitiveBias] = []
        self.principles: list[PersuasionPrinciple] = []
        self.triggers: list[PsychologicalTrigger] = []
        self._build_profile()

    def _build_profile(self) -> None:
        """Build persuasion profile based on audience and niche."""
        # Default biases that work for most audiences
        self.biases = [
            CognitiveBias.SOCIAL_PROOF,
            CognitiveBias.LOSS_AVERSION,
            CognitiveBias.AUTHORITY,
        ]

        # Default persuasion principles
        self.principles = [
            PersuasionPrinciple.RECIPROCITY,
            PersuasionPrinciple.SOCIAL_PROOF,
            PersuasionPrinciple.SCARCITY,
        ]

        # Default psychological triggers
        self.triggers = [
            PsychologicalTrigger.CURIOSITY,
            PsychologicalTrigger.SIGNIFICANCE,
            PsychologicalTrigger.CERTAINTY,
        ]

    def get_applications(self) -> list[dict[str, str]]:
        """Get practical applications of the persuasion profile for content."""
        applications = []
        for bias in self.biases:
            apps = BIAS_APPLICATIONS.get(bias, {})
            applications.append(
                {
                    "bias": bias.value,
                    "name": apps.get("name", bias.value),
                    "content_application": apps.get("content", ""),
                    "copy_example": apps.get("copy_example", ""),
                }
            )
        for principle in self.principles:
            apps = PRINCIPLE_APPLICATIONS.get(principle, {})
            applications.append(
                {
                    "principle": principle.value,
                    "name": apps.get("name", principle.value),
                    "content_application": apps.get("content", ""),
                    "copy_example": apps.get("copy_example", ""),
                }
            )
        for trigger in self.triggers:
            apps = TRIGGER_APPLICATIONS.get(trigger, {})
            applications.append(
                {
                    "trigger": trigger.value,
                    "name": apps.get("name", trigger.value),
                    "content_application": apps.get("content", ""),
                    "copy_example": apps.get("copy_example", ""),
                }
            )
        return applications


# ── Bias Applications Database ──────────────────────────────────

BIAS_APPLICATIONS: dict[CognitiveBias, dict[str, str]] = {
    CognitiveBias.SOCIAL_PROOF: {
        "name": "Prova Social",
        "content": "Inclua números de usuários, depoimentos, estudos de caso.",
        "copy_example": "Mais de 50.000 pessoas já transformaram seus resultados com este método.",
    },
    CognitiveBias.AUTHORITY: {
        "name": "Autoridade",
        "content": "Mostre credenciais, certificações, parcerias, prêmios.",
        "copy_example": "Recomendado pelos maiores especialistas em [nicho] do Brasil.",
    },
    CognitiveBias.LOSS_AVERSION: {
        "name": "Aversão à Perda",
        "content": "Destaque o que o leitor PERDE ao não agir (2x mais forte que ganho).",
        "copy_example": "Você está perdendo R$ X por mês ao não implementar esta estratégia.",
    },
    CognitiveBias.SCARCITY: {
        "name": "Escassez",
        "content": "Limite de tempo, vagas, ou quantidade. Crie urgência real.",
        "copy_example": "Apenas 7 vagas restantes para esta turma. Próxima só em 2027.",
    },
    CognitiveBias.ANCHORING: {
        "name": "Ancoragem",
        "content": "Apresente um valor alto primeiro para ancorar a percepção.",
        "copy_example": "Consultoria particular: R$ 5.000. Este guia completo: R$ 47.",
    },
    CognitiveBias.CONFIRMATION: {
        "name": "Viés de Confirmação",
        "content": "Reforce crenças existentes do leitor sobre o nicho.",
        "copy_example": "Você já sabia que [crença do nicho]. Agora veja como fazer certo.",
    },
    CognitiveBias.CONSENSUS: {
        "name": "Consenso",
        "content": "Mostre que a maioria das pessoas já adotou a solução.",
        "copy_example": "87% dos profissionais de [nicho] já usam esta abordagem.",
    },
    CognitiveBias.DRO: {
        "name": "Dread Of Regret (FOMO)",
        "content": "Medo de se arrepender por não ter agido quando teve chance.",
        "copy_example": "Daqui a 3 meses, você vai se perguntar por que não começou hoje.",
    },
}

PRINCIPLE_APPLICATIONS: dict[PersuasionPrinciple, dict[str, str]] = {
    PersuasionPrinciple.RECIPROCITY: {
        "name": "Reciprocidade",
        "content": "Ofereça valor GRÁTIS primeiro (guia, checklist, planilha).",
        "copy_example": "Baixe grátis: Checklist Completo de [tema]. Presente nosso!",
    },
    PersuasionPrinciple.SCARCITY: {
        "name": "Escassez",
        "content": "Oferta limitada no tempo ou quantidade exclusiva.",
        "copy_example": "Preço especial para os primeiros 100 compradores.",
    },
    PersuasionPrinciple.AUTHORITY: {
        "name": "Autoridade",
        "content": "Cite fontes, pesquisas, especialistas reconhecidos.",
        "copy_example": "Baseado em 15 anos de pesquisa em [nicho].",
    },
    PersuasionPrinciple.CONSISTENCY: {
        "name": "Consistência",
        "content": "Peça pequenos compromissos que levam ao grande.",
        "copy_example": "Você já deu o primeiro passo lendo até aqui. Continue!",
    },
    PersuasionPrinciple.LIKING: {
        "name": "Simpatia",
        "content": "Seja autêntico, use histórias pessoais, mostre vulnerabilidade.",
        "copy_example": "Eu também comecei do zero. Se eu consegui, você consegue.",
    },
    PersuasionPrinciple.SOCIAL_PROOF: {
        "name": "Prova Social",
        "content": "Depoimentos, avaliações, números de usuários satisfeitos.",
        "copy_example": "Veja o que alunos estão dizendo sobre o curso.",
    },
    PersuasionPrinciple.UNITY: {
        "name": "Unidade",
        "content": "Nós juntos. Crie senso de identidade compartilhada.",
        "copy_example": "Juntos, vamos transformar sua relação com [nicho].",
    },
}

TRIGGER_APPLICATIONS: dict[PsychologicalTrigger, dict[str, str]] = {
    PsychologicalTrigger.FEAR: {
        "name": "Medo",
        "content": "Medo de perder oportunidades, dinheiro, status ou tempo.",
        "copy_example": "Enquanto você espera, seus concorrentes estão avançando.",
    },
    PsychologicalTrigger.GREED: {
        "name": "Ganância",
        "content": "Desejo de mais dinheiro, resultados, reconhecimento.",
        "copy_example": "Imagine multiplicar seus resultados em [prazo curto].",
    },
    PsychologicalTrigger.VANITY: {
        "name": "Vaidade",
        "content": "Desejo de status, reconhecimento, parecer bem-sucedido.",
        "copy_example": "Seja visto como autoridade em [nicho]. Seja referência.",
    },
    PsychologicalTrigger.CURIOSITY: {
        "name": "Curiosidade",
        "content": "Gap de curiosidade. Informação incompleta que leva ao próximo passo.",
        "copy_example": "O segredo que ninguém conta sobre [tema] (revele no final).",
    },
    PsychologicalTrigger.BELONGING: {
        "name": "Pertencimento",
        "content": "Desejo de fazer parte de um grupo, comunidade, tribo.",
        "copy_example": "Faça parte do grupo seleto de profissionais que dominam [tema].",
    },
    PsychologicalTrigger.CONTROL: {
        "name": "Controle",
        "content": "Desejo de ter controle sobre a própria vida e resultados.",
        "copy_example": "Assuma o controle dos seus resultados em [nicho].",
    },
    PsychologicalTrigger.SIGNIFICANCE: {
        "name": "Significância",
        "content": "Desejo de se sentir importante, especial, único.",
        "copy_example": "Você merece resultados extraordinários em [nicho].",
    },
    PsychologicalTrigger.CERTAINTY: {
        "name": "Certeza",
        "content": "Desejo de previsibilidade, segurança, redução de riscos.",
        "copy_example": "Método testado e comprovado. Resultados garantidos ou seu dinheiro de volta.",
    },
}


class PsychologyEngine:
    """Core engine for psychologically-informed content creation."""

    @staticmethod
    def create_profile(niche: str, audience: str = "iniciantes") -> PersuasiveProfile:
        """Create a persuasion profile for content targeting."""
        return PersuasiveProfile(niche, audience)

    @staticmethod
    def select_best_biases(content_type: str, goal: str) -> list[CognitiveBias]:
        """Select optimal cognitive biases for content type and goal."""
        recommendations = {
            "blog_article": {
                "educate": [CognitiveBias.AUTHORITY, CognitiveBias.CONFIRMATION],
                "persuade": [CognitiveBias.SOCIAL_PROOF, CognitiveBias.LOSS_AVERSION],
                "sell": [
                    CognitiveBias.SCARCITY,
                    CognitiveBias.ANCHORING,
                    CognitiveBias.DRO,
                ],
            },
            "landing_page": {
                "convert": [
                    CognitiveBias.ANCHORING,
                    CognitiveBias.SCARCITY,
                    CognitiveBias.LOSS_AVERSION,
                ],
                "lead": [CognitiveBias.RECIPROCITY, CognitiveBias.AUTHORITY],
            },
            "email": {
                "open": [CognitiveBias.CURIOSITY, CognitiveBias.RECENCY],
                "click": [CognitiveBias.SCARCITY, CognitiveBias.DRO],
                "buy": [CognitiveBias.LOSS_AVERSION, CognitiveBias.SOCIAL_PROOF],
            },
            "video": {
                "hook": [CognitiveBias.CURIOSITY, CognitiveBias.FRAMING],
                "retain": [CognitiveBias.STORYTELLING, CognitiveBias.HALO],
                "convert": [CognitiveBias.SCARCITY, CognitiveBias.LOSS_AVERSION],
            },
        }
        type_recs = recommendations.get(content_type, {})
        return type_recs.get(goal, [CognitiveBias.SOCIAL_PROOF])

    @staticmethod
    def select_best_principles(
        content_type: str, goal: str
    ) -> list[PersuasionPrinciple]:
        """Select optimal persuasion principles."""
        recommendations = {
            "blog_article": {
                "educate": [
                    PersuasionPrinciple.AUTHORITY,
                    PersuasionPrinciple.RECIPROCITY,
                ],
                "persuade": [
                    PersuasionPrinciple.SOCIAL_PROOF,
                    PersuasionPrinciple.LIKING,
                ],
                "sell": [PersuasionPrinciple.SCARCITY, PersuasionPrinciple.RECIPROCITY],
            },
            "landing_page": {
                "convert": [
                    PersuasionPrinciple.SCARCITY,
                    PersuasionPrinciple.SOCIAL_PROOF,
                    PersuasionPrinciple.AUTHORITY,
                ],
                "lead": [
                    PersuasionPrinciple.RECIPROCITY,
                    PersuasionPrinciple.CONSISTENCY,
                ],
            },
            "email": {
                "sell": [
                    PersuasionPrinciple.SCARCITY,
                    PersuasionPrinciple.SOCIAL_PROOF,
                    PersuasionPrinciple.UNITY,
                ],
            },
        }
        type_recs = recommendations.get(content_type, {})
        return type_recs.get(goal, [PersuasionPrinciple.SOCIAL_PROOF])

    @staticmethod
    def select_best_triggers(
        content_type: str, goal: str
    ) -> list[PsychologicalTrigger]:
        """Select optimal psychological triggers."""
        recommendations = {
            "blog_article": {
                "educate": [
                    PsychologicalTrigger.CURIOSITY,
                    PsychologicalTrigger.CERTAINTY,
                ],
                "inspire": [
                    PsychologicalTrigger.SIGNIFICANCE,
                    PsychologicalTrigger.MEANING,
                ],
                "sell": [PsychologicalTrigger.FEAR, PsychologicalTrigger.GREED],
            },
            "landing_page": {
                "convert": [
                    PsychologicalTrigger.FEAR,
                    PsychologicalTrigger.GREED,
                    PsychologicalTrigger.CERTAINTY,
                ],
            },
            "email": {
                "open": [PsychologicalTrigger.CURIOSITY, PsychologicalTrigger.FEAR],
                "buy": [PsychologicalTrigger.GREED, PsychologicalTrigger.CERTAINTY],
            },
        }
        type_recs = recommendations.get(content_type, {})
        return type_recs.get(goal, [PsychologicalTrigger.CURIOSITY])

    @staticmethod
    def generate_persuasive_segment(
        bias: CognitiveBias,
        topic: str,
        niche: str,
    ) -> dict[str, str]:
        """Generate a persuasive content segment based on a specific bias."""
        app = BIAS_APPLICATIONS.get(bias, {})
        placements = {
            CognitiveBias.SOCIAL_PROOF: "Meio do artigo, seção de depoimentos",
            CognitiveBias.AUTHORITY: "Início (credentials) ou final (fontes)",
            CognitiveBias.LOSS_AVERSION: "Final, antes do CTA",
            CognitiveBias.SCARCITY: "Final, junto com o CTA",
            CognitiveBias.ANCHORING: "Início, na apresentação do valor",
            CognitiveBias.RECIPROCITY: "Ofereça algo grátis antes de pedir",
            CognitiveBias.CURIOSITY: "Título e primeiros parágrafos",
        }
        return {
            "bias": bias.value,
            "name": app.get("name", bias.value),
            "strategy": app.get("content", ""),
            "copy_example": app.get("copy_example", "")
            .replace("[nicho]", niche)
            .replace("[tema]", topic),
            "placement": placements.get(bias, "Distribuído naturalmente no conteúdo"),
        }

    @staticmethod
    def _suggest_placement(bias: CognitiveBias) -> str:
        placements = {
            CognitiveBias.SOCIAL_PROOF: "Meio do artigo, seção de depoimentos",
            CognitiveBias.AUTHORITY: "Início (credentials) ou final (fontes)",
            CognitiveBias.LOSS_AVERSION: "Final, antes do CTA",
            CognitiveBias.SCARCITY: "Final, junto com o CTA",
            CognitiveBias.ANCHORING: "Início, na apresentação do valor",
            CognitiveBias.RECIPROCITY: "Ofereça algo grátis antes de pedir",
            CognitiveBias.CURIOSITY: "Título e primeiros parágrafos",
        }
        return placements.get(bias, "Distribuído naturalmente no conteúdo")

    @staticmethod
    def _suggest_placement(bias):
        placements = {
            CognitiveBias.SOCIAL_PROOF: "Meio do artigo, seção de depoimentos",
            CognitiveBias.AUTHORITY: "Início (credentials) ou final (fontes)",
            CognitiveBias.LOSS_AVERSION: "Final, antes do CTA",
            CognitiveBias.SCARCITY: "Final, junto com o CTA",
            CognitiveBias.ANCHORING: "Início, na apresentação do valor",
            CognitiveBias.RECIPROCITY: "Ofereça algo grátis antes de pedir",
            CognitiveBias.CURIOSITY: "Título e primeiros parágrafos",
        }
        return placements.get(bias, "Distribuído naturalmente no conteúdo")

    @staticmethod
    def get_all_biases() -> list[dict[str, str]]:
        """Return all cognitive biases with descriptions."""
        return [
            {
                "id": b.value,
                "name": BIAS_APPLICATIONS.get(b, {}).get("name", b.value),
                "description": BIAS_APPLICATIONS.get(b, {}).get("content", ""),
            }
            for b in CognitiveBias
        ]

    @staticmethod
    def get_all_principles() -> list[dict[str, str]]:
        return [
            {
                "id": p.value,
                "name": PRINCIPLE_APPLICATIONS.get(p, {}).get("name", p.value),
                "description": PRINCIPLE_APPLICATIONS.get(p, {}).get("content", ""),
            }
            for p in PersuasionPrinciple
        ]
