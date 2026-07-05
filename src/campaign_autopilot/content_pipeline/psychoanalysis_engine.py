"""Psychoanalysis Engine — deep psychological triggers and Jungian concepts.

Based on:
- Jungian analytical psychology
- Lacanian psychoanalysis
- Archetypal marketing
- Depth psychology for persuasion
- The collective unconscious in branding

Provides frameworks for tapping into unconscious motivations.
"""

from __future__ import annotations

from enum import Enum


class DeepTrigger(Enum):
    """Deep psychoanalytic triggers for unconscious persuasion."""

    # Jungian concepts
    SHADOW = "shadow"  # The dark side, repressed desires
    PERSONA = "persona"  # Social mask, ideal self
    ANIMA_ANIMUS = "anima_animus"  # Inner feminine/masculine
    INDIVIDUATION = "individuation"  # Self-actualization journey
    COLLECTIVE_UNCONSCIOUS = "collective_unconscious"  # Shared memories

    # Core drives
    LUST = "lust"  # Sexual/sensual desire
    POWER = "power"  # Dominance, control, influence
    STATUS = "status"  # Social standing, respect
    IDENTITY = "identity"  # Who am I? Self-definition
    TRANSCENDENCE = "transcendence"  # Beyond self, meaning
    SECURITY = "security"  # Safety, protection, certainty
    NOVELTY = "novelty"  # New experiences, discovery

    # Lacanian concepts
    DESIRE = "desire"  # Lack that drives all action
    JOUISSANCE = "jouissance"  # Forbidden pleasure/excess
    THE_OTHER = "the_other"  # How we see ourselves through others
    THE_GAZE = "the_gaze"  # Being seen, validated, judged
    THE_VOID = "the_void"  # Existential emptiness we try to fill


class JungianConcept(Enum):
    """Jungian archetypal concepts applicable to marketing."""

    THE_HERO = "the_hero"
    THE_MOTHER = "the_mother"
    THE_FATHER = "the_father"
    THE_WISE_OLD_MAN = "the_wise_old_man"
    THE_TRICKSTER = "the_trickster"
    THE_SHADOW = "the_shadow"
    THE_SAGE = "the_sage"
    THE_INNOCENT = "the_innocent"
    THE_EXPLORER = "the_explorer"
    THE_OUTLAW = "the_outlaw"
    THE_MAGICIAN = "the_magician"
    THE_CREATOR = "the_creator"
    THE_RULER = "the_ruler"
    THE_CAREGIVER = "the_caregiver"
    THE_LOVER = "the_lover"
    THE_JESTER = "the_jester"
    THE_EVERYMAN = "the_everyman"


class DeepPersuasionProfile:
    """Deep psychological profile for ultra-persuasive content."""

    def __init__(self, niche: str, audience_segment: str):
        self.niche = niche
        self.audience = audience_segment
        self.triggers: list[DeepTrigger] = []
        self.archetypes: list[JungianConcept] = []
        self._build_profile()

    def _build_profile(self) -> None:
        """Build deep psychology profile."""
        # Default deep triggers
        self.triggers = [
            DeepTrigger.DESIRE,
            DeepTrigger.IDENTITY,
            DeepTrigger.SECURITY,
        ]
        # Default archetypes
        self.archetypes = [
            JungianConcept.THE_HERO,
            JungianConcept.THE_SAGE,
            JungianConcept.THE_EVERYMAN,
        ]

    def get_applications(self) -> list[dict[str, str]]:
        """Get practical content applications."""
        return [
            {
                "domain": "psychoanalysis",
                "trigger": t.value,
                "name": DEEP_TRIGGER_NAMES.get(t, t.value),
                "application": DEEP_TRIGGER_APPLICATIONS.get(t, ""),
                "copy_example": DEEP_TRIGGER_EXAMPLES.get(t, "").replace(
                    "[nicho]", self.niche
                ),
            }
            for t in self.triggers
        ] + [
            {
                "domain": "archetype",
                "archetype": a.value,
                "name": ARCHETYPE_NAMES.get(a, a.value),
                "application": ARCHETYPE_APPLICATIONS.get(a, ""),
                "brand_example": ARCHETYPE_BRANDS.get(a, ""),
            }
            for a in self.archetypes
        ]


DEEP_TRIGGER_NAMES = {
    DeepTrigger.SHADOW: "Sombra",
    DeepTrigger.PERSONA: "Persona (Máscara Social)",
    DeepTrigger.INDIVIDUATION: "Individuação",
    DeepTrigger.DESIRE: "Desejo Inconsciente",
    DeepTrigger.IDENTITY: "Identidade",
    DeepTrigger.TRANSCENDENCE: "Transcendência",
    DeepTrigger.THE_OTHER: "O Olhar do Outro",
    DeepTrigger.THE_VOID: "O Vazio Existencial",
    DeepTrigger.POWER: "Poder",
    DeepTrigger.SECURITY: "Segurança Profunda",
}

DEEP_TRIGGER_APPLICATIONS = {
    DeepTrigger.SHADOW: "Ative o desejo reprimido de mudança. Mostre o que o leitor não quer admitir sobre si mesmo.",
    DeepTrigger.PERSONA: "Apresente a versão ideal que o leitor quer ser. O 'eu perfeito' que ele projeta.",
    DeepTrigger.INDIVIDUATION: "Posicione o produto/serviço como parte da jornada de autodescoberta do leitor.",
    DeepTrigger.DESIRE: "O desejo nunca é pelo objeto em si, mas pelo que ele REPRESENTA (status, amor, poder).",
    DeepTrigger.IDENTITY: "Consumo é construção de identidade. 'Você é o que você compra.'",
    DeepTrigger.THE_OTHER: "Somos ansiosos por como somos percebidos. Produtos são extensões do self social.",
    DeepTrigger.THE_VOID: "Consumo como tentativa de preencher um vazio existencial. Marketing aspiracional.",
    DeepTrigger.POWER: "Desejo primal de controle sobre o ambiente. Produtos que dão poder ao consumidor.",
}

DEEP_TRIGGER_EXAMPLES = {
    DeepTrigger.SHADOW: "Você sabe que merece mais. Mas uma parte de você tem medo de mudar. Está na hora de enfrentar essa sombra.",
    DeepTrigger.PERSONA: "Imagine a versão de você que já domina [nicho]. Confiante, realizada, no controle. Essa pessoa está a um passo de distância.",
    DeepTrigger.INDIVIDUATION: "Esta não é apenas mais uma ferramenta. É um passo na sua jornada de se tornar a melhor versão de si mesmo.",
    DeepTrigger.DESIRE: "Não é sobre o curso. É sobre a liberdade que ele representa. A liberdade de trabalhar de onde quiser, quando quiser.",
    DeepTrigger.IDENTITY: "Pessoas que compram [produto] não estão apenas resolvendo um problema. Estão se definindo como profissionais sérios.",
    DeepTrigger.THE_OTHER: "O que as pessoas vão pensar quando virem seus resultados? Como você será visto? O respeito que você merece.",
}

ARCHETYPE_NAMES = {
    JungianConcept.THE_HERO: "O Herói",
    JungianConcept.THE_SAGE: "O Sábio",
    JungianConcept.THE_INNOCENT: "O Inocente",
    JungianConcept.THE_EXPLORER: "O Explorador",
    JungianConcept.THE_OUTLAW: "O Rebelde",
    JungianConcept.THE_MAGICIAN: "O Mago",
    JungianConcept.THE_CREATOR: "O Criador",
    JungianConcept.THE_RULER: "O Governante",
    JungianConcept.THE_CAREGIVER: "O Cuidador",
    JungianConcept.THE_LOVER: "O Amante",
    JungianConcept.THE_JESTER: "O Bobo da Corte",
    JungianConcept.THE_EVERYMAN: "O Cara Comum",
}

ARCHETYPE_APPLICATIONS = {
    JungianConcept.THE_HERO: "Jornada de superação. Mostre o desafio, a luta e a vitória. Use linguagem de batalha e conquista.",
    JungianConcept.THE_SAGE: "Conhecimento como poder. Posicione conteúdo como sabedoria exclusiva. 'Descubra os segredos.'",
    JungianConcept.THE_INNOCENT: "Simplicidade e pureza. 'Volte às origens.' Promessa de felicidade sem complicação.",
    JungianConcept.THE_EXPLORER: "Liberdade e descoberta. 'Vá além.' Conteúdo sobre novos horizontes, possibilidades.",
    JungianConcept.THE_OUTLAW: "Revolução. 'Quebre as regras.' Marketing de disrupção, para quem está cansado do sistema.",
    JungianConcept.THE_MAGICIAN: "Transformação. 'Transforme sua realidade.' Promessa de poder extraordinário.",
    JungianConcept.THE_RULER: "Controle e status. 'Tome o comando.' Conteúdo para quem quer liderança e autoridade.",
    JungianConcept.THE_EVERYMAN: "Identificação. 'Somos iguais.' Conteúdo próximo, acessível, 'gente como a gente.'",
}

ARCHETYPE_BRANDS = {
    JungianConcept.THE_HERO: "Nike ('Just Do It'), Gatorade",
    JungianConcept.THE_SAGE: "Google, TED, Harvard",
    JungianConcept.THE_INNOCENT: "Coca-Cola, McDonald's",
    JungianConcept.THE_EXPLORER: "Jeep, The North Face, Red Bull",
    JungianConcept.THE_OUTLAW: "Harley-Davidson, Diesel, Spotify",
    JungianConcept.THE_MAGICIAN: "Disney, Apple, Dyson",
    JungianConcept.THE_RULER: "Mercedes-Benz, Rolex, Microsoft",
    JungianConcept.THE_CAREGIVER: "Johnson & Johnson, Dove",
    JungianConcept.THE_LOVER: "Chanel, Victoria's Secret, Häagen-Dazs",
    JungianConcept.THE_JESTER: "Skittles, Old Spice, Doritos",
    JungianConcept.THE_EVERYMAN: "IKEA, Levi's, Volkswagen",
}


class PsychoanalysisEngine:
    """Engine for depth psychology in content creation."""

    @staticmethod
    def create_profile(niche: str, audience: str) -> DeepPersuasionProfile:
        return DeepPersuasionProfile(niche, audience)

    @staticmethod
    def interpret_desire(niche: str, product: str) -> list[dict[str, str]]:
        """Interpret the unconscious desire behind a product purchase."""
        return [
            {
                "manifest": product,
                "latent_desire": "Controle e autonomia sobre o próprio futuro",
                "depth_angle": f"{product} não é só sobre {niche}. É sobre a liberdade de decidir seu próprio caminho.",
            },
            {
                "manifest": product,
                "latent_desire": "Reconhecimento e validação social",
                "depth_angle": f"{product} é o símbolo visível do seu compromisso com a excelência em {niche}.",
            },
            {
                "manifest": product,
                "latent_desire": "Segurança contra o fracasso e a incerteza",
                "depth_angle": f"{product} é sua rede de proteção. A certeza de que você está no caminho certo em {niche}.",
            },
        ]

    @staticmethod
    def apply_shadow_marketing(niche: str, fear: str) -> dict[str, str]:
        """Apply shadow archetype to marketing content."""
        return {
            "technique": "Shadow Marketing",
            "description": f"Ative o medo inconsciente de {fear} em {niche} para motivar ação.",
            "copy_angle": f"O que você realmente teme é acordar daqui a 5 anos e perceber que você poderia ter {fear} se tivesse começado hoje. Esse medo não é seu inimigo. É seu guia.",
        }

    @staticmethod
    def apply_individuation_framework(
        niche: str, current_state: str, desired_state: str
    ) -> dict[str, list]:
        """Create content using the individuation (self-actualization) framework."""
        return {
            "framework": "Individuação em 3 Atos",
            "stages": [
                {
                    "act": 1,
                    "name": "A Queda da Persona",
                    "content": f"Mostre que a forma atual ({current_state}) não está funcionando. A máscara precisa cair.",
                    "emotion": "Desconforto construtivo",
                },
                {
                    "act": 2,
                    "name": "Encontro com a Sombra",
                    "content": f"Explore os medos e bloqueios que impedem chegar a {desired_state}. Enfrente a sombra.",
                    "emotion": "Coragem",
                },
                {
                    "act": 3,
                    "name": "A Nova Identidade",
                    "content": f"Apresente a nova identidade integrada: a pessoa que domina {niche} e vive {desired_state}.",
                    "emotion": "Realização",
                },
            ],
        }

    @staticmethod
    def get_all_triggers() -> list[dict[str, str]]:
        return [
            {
                "id": t.value,
                "name": DEEP_TRIGGER_NAMES.get(t, t.value),
                "application": DEEP_TRIGGER_APPLICATIONS.get(t, ""),
            }
            for t in DeepTrigger
        ]
