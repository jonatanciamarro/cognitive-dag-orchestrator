"""Communication Engine — message framing, tone, voice, and rhetoric.

Based on:
- Framing theory (Tversky & Kahneman)
- Rhetoric (Aristotle: Ethos, Pathos, Logos)
- Transactional Analysis (Berne)
- Non-Violent Communication (Rosenberg)
- Persuasive communication models
- Copywriting frameworks
"""

from __future__ import annotations

import random
from enum import Enum


class MessageFrame(Enum):
    """Message framing strategies for different psychological effects."""

    # Gain vs Loss
    GAIN_FRAME = "gain_frameFocus on benefits"
    LOSS_FRAME = "loss_frame"  # Focus on costs of inaction

    # Temporal frames
    PRESENT_FRAME = "present_frame"  # Focus on now
    FUTURE_FRAME = "future_frame"  # Focus on future state

    # Attribution frames
    INTERNAL_FRAME = "internal_frame"  # "You can do it"
    EXTERNAL_FRAME = "external_frame"  # "The market demands it"

    # Value frames
    ECONOMIC_FRAME = "economic_frame"  # Focus on money
    SOCIAL_FRAME = "social_frame"  # Focus on belonging
    ETHICAL_FRAME = "ethical_frame"  # Focus on doing right
    ACHIEVEMENT_FRAME = "achievement_frame"  # Focus on success


class ToneOfVoice(Enum):
    """Tone of voice options for content."""

    AUTHORITATIVE = "authoritative"  # Expert, confident, decisive
    CONVERSATIONAL = "conversational"  # Friendly, approachable, natural
    URGENT = "urgent"  # Pressing, time-sensitive
    INSPIRATIONAL = "inspirational"  # Uplifting, motivational
    EDUCATIONAL = "educational"  # Clear, instructive, patient
    EMPATHETIC = "empathetic"  # Understanding, supportive
    PROVOCATIVE = "provocative"  # Challenging, thought-provoking
    HUMOROUS = "humorous"  # Witty, fun, engaging
    FORMAL = "formal"  # Professional, structured
    CASUAL = "casual"  # Relaxed, informal


class RhetoricalDevice(Enum):
    """Classical rhetorical devices for persuasive writing."""

    # Ethos (credibility)
    CREDENTIAL = "credential"
    TESTIMONIAL = "testimonial"
    AUTHORITY_CITE = "authority_cite"

    # Pathos (emotion)
    FEAR_APPEAL = "fear_appeal"
    HOPE_APPEAL = "hope_appeal"
    VANITY_APPEAL = "vanity_appeal"
    ANECDOTE = "anecdote"
    CONTRAST = "contrast"
    METAPHOR = "metaphor"
    STORY = "story"

    # Logos (logic)
    STATISTIC = "statistic"
    CAUSE_EFFECT = "cause_effect"
    COMPARISON = "comparison"
    BEFORE_AFTER = "before_after"

    # Style
    REPETITION = "repetition"
    RHETORICAL_QUESTION = "rhetorical_question"
    TRICOLON = "tricolon"  # Rule of three
    HYPERBOLE = "hyperbole"


class CommunicationProfile:
    """Complete communication profile for content."""

    def __init__(self, niche: str, audience: str, brand_type: str = "authority"):
        self.niche = niche
        self.audience = audience
        self.brand_type = brand_type
        self.primary_tone = ToneOfVoice.AUTHORITATIVE
        self.secondary_tone = ToneOfVoice.EDUCATIONAL
        self.frames: list[MessageFrame] = []
        self.devices: list[RhetoricalDevice] = []
        self._build_profile()

    def _build_profile(self) -> None:
        """Build communication profile."""
        if self.brand_type == "authority":
            self.primary_tone = ToneOfVoice.AUTHORITATIVE
            self.secondary_tone = ToneOfVoice.EDUCATIONAL
            self.frames = [MessageFrame.GAIN_FRAME, MessageFrame.ACHIEVEMENT_FRAME]
        elif self.brand_type == "friend":
            self.primary_tone = ToneOfVoice.CONVERSATIONAL
            self.secondary_tone = ToneOfVoice.EMPATHETIC
            self.frames = [MessageFrame.SOCIAL_FRAME, MessageFrame.PRESENT_FRAME]
        elif self.brand_type == "provocateur":
            self.primary_tone = ToneOfVoice.PROVOCATIVE
            self.secondary_tone = ToneOfVoice.URGENT
            self.frames = [MessageFrame.LOSS_FRAME, MessageFrame.FUTURE_FRAME]
        elif self.brand_type == "educator":
            self.primary_tone = ToneOfVoice.EDUCATIONAL
            self.secondary_tone = ToneOfVoice.INSPIRATIONAL
            self.frames = [MessageFrame.GAIN_FRAME, MessageFrame.ETHICAL_FRAME]

        self.devices = [
            RhetoricalDevice.CONTRAST,
            RhetoricalDevice.BEFORE_AFTER,
            RhetoricalDevice.RHETORICAL_QUESTION,
        ]

    def get_tone_guide(self) -> dict[str, list[str]]:
        """Get tone of voice guidelines."""
        guides = {
            ToneOfVoice.AUTHORITATIVE: {
                "do": [
                    "Use dados",
                    "Seja direto",
                    "Mostre expertise",
                    "Use linguagem técnica quando relevante",
                ],
                "avoid": [
                    "Hesitação",
                    "Excesso de humildade",
                    "Opiniões não fundamentadas",
                ],
                "phrases": [
                    "Com base em...",
                    "A pesquisa mostra...",
                    "O que você precisa saber é...",
                ],
            },
            ToneOfVoice.CONVERSATIONAL: {
                "do": ["Fale como amigo", "Use contrações", "Pergunte", "Seja natural"],
                "avoid": ["Jargão técnico", "Formalidade excessiva", "Tom professoral"],
                "phrases": ["Saca só...", "Vamos ser sinceros...", "A real é que..."],
            },
            ToneOfVoice.URGENT: {
                "do": ["Prazos claros", "Linguagem de ação", "Contraste", "Escassez"],
                "avoid": ["Parecer desesperado", "Falsas urgências", "Exageros"],
                "phrases": [
                    "Não espere mais...",
                    "Última chance...",
                    "Agora ou nunca...",
                ],
            },
            ToneOfVoice.INSPIRATIONAL: {
                "do": [
                    "Histórias de superação",
                    "Linguagem aspiracional",
                    "Visão de futuro",
                ],
                "avoid": ["Parecer irreal", "Promessas vazias", "Clichês"],
                "phrases": ["Imagine...", "Você merece...", "Seu potencial é..."],
            },
            ToneOfVoice.EDUCATIONAL: {
                "do": ["Passo a passo", "Explicações claras", "Analogias", "Exemplos"],
                "avoid": [
                    "Presumir conhecimento",
                    "Pular etapas",
                    "Tom condescendente",
                ],
                "phrases": ["Basicamente...", "Pense como...", "O que isso significa?"],
            },
            ToneOfVoice.EMPATHETIC: {
                "do": [
                    "Validar sentimentos",
                    "Mostrar compreensão",
                    "Compartilhar vulnerabilidade",
                ],
                "avoid": [
                    "Parecer paternalista",
                    "Falsas promessas",
                    "Superficialidade",
                ],
                "phrases": [
                    "Eu entendo como...",
                    "É normal sentir...",
                    "Você não está sozinho...",
                ],
            },
            ToneOfVoice.PROVOCATIVE: {
                "do": ["Perguntas desafiadoras", "Afirmações ousadas", "Quebrar tabus"],
                "avoid": [
                    "Ser ofensivo",
                    "Provocar sem propósito",
                    "Parecer agressivo",
                ],
                "phrases": [
                    "E se tudo que você sabe estiver errado?",
                    "O problema não é...",
                    "Você está errado sobre...",
                ],
            },
        }
        return guides.get(self.primary_tone, guides[ToneOfVoice.AUTHORITATIVE])

    def get_writing_rules(self) -> list[str]:
        """Get writing rules based on communication profile."""
        rules = [
            "Use parágrafos de 2-3 frases no máximo",
            "Uma ideia por parágrafo",
            "Prefira voz ativa: 'Você consegue' vs 'É possível'",
            "Comece com o benefício, depois o como",
            "Use palavras sensoriais que ativam o cérebro",
            "Evite advérbios desnecessários ('muito', 'realmente')",
            "Substitua 'se' por 'quando' (mais certeza)",
            "Use 'você' 2x mais que 'nós' ou 'eu'",
        ]
        if self.primary_tone in (ToneOfVoice.AUTHORITATIVE, ToneOfVoice.EDUCATIONAL):
            rules.extend(
                [
                    "Inclua dados específicos (números, porcentagens)",
                    "Cite fontes confiáveis",
                    "Estruture com sub-títulos claros",
                ]
            )
        return rules


class CommunicationEngine:
    """Engine for strategic communication in content."""

    @staticmethod
    def create_profile(
        niche: str, audience: str, brand_type: str = "authority"
    ) -> CommunicationProfile:
        return CommunicationProfile(niche, audience, brand_type)

    @staticmethod
    def generate_headline(
        niche: str,
        topic: str,
        frame: MessageFrame = MessageFrame.GAIN_FRAME,
    ) -> str:
        """Generate a framed headline for maximum impact."""
        gain_headlines = [
            f"Como {topic} Pode Transformar Seus Resultados em {niche}",
            f"Domine {topic} e Alcance [Resultado] em {niche}",
            f"O Guia Completo de {topic} para Profissionais de {niche}",
        ]
        loss_headlines = [
            f"Por que Ignorar {topic} Está te Custando Resultados em {niche}",
            f"O Erro de {topic} que 97% dos Profissionais de {niche} Cometem",
            f"Pare de Perder Oportunidades: Domine {topic} em {niche} Agora",
        ]
        if frame == MessageFrame.LOSS_FRAME:
            return random.choice(loss_headlines)
        return random.choice(gain_headlines)

    @staticmethod
    def get_all_tones() -> list[dict[str, str]]:
        return [
            {
                "id": t.value,
                "name": t.value.capitalize(),
                "description": TONE_DESCRIPTIONS.get(t, ""),
            }
            for t in ToneOfVoice
        ]

    @staticmethod
    def get_all_frames() -> list[dict[str, str]]:
        return [
            {
                "id": f.value,
                "name": f.value.replace("_", " ").title(),
                "description": FRAME_DESCRIPTIONS.get(f, ""),
            }
            for f in MessageFrame
        ]

    @staticmethod
    def apply_device_to_copy(
        device: RhetoricalDevice,
        topic: str,
        niche: str,
    ) -> dict[str, str]:
        """Apply a rhetorical device to generate copy."""
        generators = {
            RhetoricalDevice.BEFORE_AFTER: {
                "name": "Antes e Depois",
                "copy": f"Antes de dominar {topic}: frustração, tentativa e erro, resultados inconsistentes. Depois: clareza, método comprovado, resultados previsíveis em {niche}.",
            },
            RhetoricalDevice.CONTRAST: {
                "name": "Contraste",
                "copy": f"Enquanto a maioria das pessoas em {niche} ainda está [erro comum], você pode [ação correta] com {topic}.",
            },
            RhetoricalDevice.RHETORICAL_QUESTION: {
                "name": "Pergunta Retórica",
                "copy": "E se você pudesse [benefício] em [prazo] sem [dor]? Parece bom demais para ser verdade?",
            },
            RhetoricalDevice.TRICOLON: {
                "name": "Regra de Três",
                "copy": f"{topic} é simples: aprenda, pratique, repita. Três passos. Resultados reais em {niche}.",
            },
            RhetoricalDevice.STATISTIC: {
                "name": "Estatística",
                "copy": f"Estudos mostram que 94% das pessoas que dominam {topic} têm [resultado] em {niche}.",
            },
            RhetoricalDevice.ANECDOTE: {
                "name": "Anedota",
                "copy": f"Deixe-me contar a história de um aluno que, depois de aprender {topic}, triplicou seus resultados em {niche} em apenas 30 dias.",
            },
        }
        return generators.get(
            device,
            {"name": "Personalizado", "copy": f"Destaque sobre {topic} em {niche}"},
        )


TONE_DESCRIPTIONS = {
    ToneOfVoice.AUTHORITATIVE: "Tom de especialista. Confiante, baseado em dados, direto.",
    ToneOfVoice.CONVERSATIONAL: "Tom de amigo. Natural, próximo, humano.",
    ToneOfVoice.URGENT: "Tom de emergência. Ação imediata, escassez, tempo limitado.",
    ToneOfVoice.INSPIRATIONAL: "Tom de mentor. Elevador, motivacional, aspiracional.",
    ToneOfVoice.EDUCATIONAL: "Tom de professor. Claro, paciente, estruturado.",
    ToneOfVoice.EMPATHETIC: "Tom de acolhimento. Compreensivo, paciente, humano.",
    ToneOfVoice.PROVOCATIVE: "Tom de provocador. Desafia crenças, disruptivo, marcante.",
    ToneOfVoice.HUMOROUS: "Tom bem-humorado. Leve, divertido, memorável.",
}

FRAME_DESCRIPTIONS = {
    MessageFrame.GAIN_FRAME: "Foco no que o leitor GANHA. Benefícios, resultados, conquistas.",
    MessageFrame.LOSS_FRAME: "Foco no que o leitor PERDE se não agir. 2x mais poderoso que gain frame.",
    MessageFrame.FUTURE_FRAME: "Foco no futuro desejado. Aspiração, possibilidade, potencial.",
    MessageFrame.PRESENT_FRAME: "Foco no agora. Ação imediata, momento presente, urgência.",
    MessageFrame.ECONOMIC_FRAME: "Foco em dinheiro e valor financeiro. ROI, economia, lucro.",
    MessageFrame.SOCIAL_FRAME: "Foco em pertencimento. Comunidade, tribo, status social.",
    MessageFrame.ACHIEVEMENT_FRAME: "Foco em realização. Sucesso, conquista, meta atingida.",
}
