"""Archetype Engine — 12 Jungian brand archetypes for content strategy.

Based on:
- Carl Jung's archetypes
- Mark & Pearson's 'The Hero and the Outlaw'
- Archetypal branding methodology
- Brand personality frameworks

Each archetype has: core desire, goal, fear, strategy, and content approach.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any


class BrandArchetype(Enum):
    """The 12 Jungian brand archetypes."""

    INNOCENT = "innocent"
    SAGE = "sage"
    EXPLORER = "explorer"
    OUTLAW = "outlaw"
    MAGICIAN = "magician"
    HERO = "hero"
    LOVER = "lover"
    JESTER = "jester"
    EVERYMAN = "everyman"
    CAREGIVER = "caregiver"
    RULER = "ruler"
    CREATOR = "creator"


class ArchetypeExpression:
    """Complete expression of a brand archetype."""

    def __init__(self, archetype: BrandArchetype):
        self.archetype = archetype
        self.core = ARCHETYPE_CORE.get(archetype, {})
        self.content = ARCHETYPE_CONTENT.get(archetype, {})
        self.marketing = ARCHETYPE_MARKETING.get(archetype, {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "archetype": self.archetype.value,
            "name": self.core.get("name", ""),
            "motto": self.core.get("motto", ""),
            "core_desire": self.core.get("core_desire", ""),
            "goal": self.core.get("goal", ""),
            "fear": self.core.get("fear", ""),
            "strategy": self.core.get("strategy", ""),
            "content_style": self.content.get("style", ""),
            "content_types": self.content.get("content_types", []),
            "tone": self.content.get("tone", ""),
            "keywords": self.content.get("keywords", []),
            "brand_examples": self.marketing.get("brands", []),
            "copy_angle": self.marketing.get("copy_angle", ""),
        }

    def generate_headline(self, topic: str, niche: str) -> str:
        """Generate a headline in the archetype's voice."""
        headlines = ARCHETYPE_HEADLINES.get(self.archetype, [])
        template = (
            random.choice(headlines) if headlines else "Guia de {topic} para {niche}"
        )
        return template.replace("{topic}", topic).replace("{niche}", niche)

    def generate_content_segment(self, topic: str, niche: str) -> dict[str, str]:
        """Generate a content segment in the archetype's voice."""
        segments = ARCHETYPE_SEGMENTS.get(self.archetype, [])
        segment = (
            random.choice(segments) if segments else "Conteúdo sobre {topic} em {niche}"
        )
        return {
            "archetype": self.archetype.value,
            "content": segment.replace("{topic}", topic).replace("{niche}", niche),
        }


# ── Archetype Database ──────────────────────────────────────────

ARCHETYPE_CORE: dict[BrandArchetype, dict[str, str]] = {
    BrandArchetype.INNOCENT: {
        "name": "O Inocente",
        "motto": "Eu mereço ser feliz",
        "core_desire": "Experiência de paraíso, paz, felicidade",
        "goal": "Ser feliz, estar em segurança",
        "fear": "Ser punido por fazer algo errado",
        "strategy": "Fazer as coisas certas, manter otimismo",
    },
    BrandArchetype.SAGE: {
        "name": "O Sábio",
        "motto": "A verdade libertará",
        "core_desire": "Descoberta da verdade, conhecimento",
        "goal": "Usar inteligência para compreender o mundo",
        "fear": "Ser enganado, ignorância",
        "strategy": "Buscar informação, pensar antes de agir",
    },
    BrandArchetype.EXPLORER: {
        "name": "O Explorador",
        "motto": "Não me cerque",
        "core_desire": "Liberdade para descobrir quem é através da exploração",
        "goal": "Experenciar uma vida melhor, mais autêntica",
        "fear": "Ficar preso, conformidade",
        "strategy": "Viajar, buscar novidades, escapar do tédio",
    },
    BrandArchetype.OUTLAW: {
        "name": "O Rebelde",
        "motto": "Regras foram feitas para ser quebradas",
        "core_desire": "Vingança, revolução, mudança radical",
        "goal": "Destruir o que não funciona",
        "fear": "Ficar impotente, irrelevante",
        "strategy": "Chocar, quebrar regras, disruptura",
    },
    BrandArchetype.MAGICIAN: {
        "name": "O Mago",
        "motto": "Tudo é possível",
        "core_desire": "Compreensão das leis fundamentais do universo",
        "goal": "Transformar sonhos em realidade",
        "fear": "Consequências negativas imprevistas",
        "strategy": "Desenvolver visão, transformar",
    },
    BrandArchetype.HERO: {
        "name": "O Herói",
        "motto": "Onde há vontade, há um caminho",
        "core_desire": "Provar valor através de atos corajosos",
        "goal": "Usar maestria para melhorar o mundo",
        "fear": "Fraqueza, vulnerabilidade, fracassar",
        "strategy": "Treinar duro, superar obstáculos",
    },
    BrandArchetype.LOVER: {
        "name": "O Amante",
        "motto": "Você é tudo que preciso",
        "core_desire": "Intimidade, conexão profunda, beleza",
        "goal": "Estar em relacionamento com pessoas e paixões",
        "fear": "Ficar sozinho, ser rejeitado",
        "strategy": "Tornar-se mais atraente física e emocionalmente",
    },
    BrandArchetype.JESTER: {
        "name": "O Bobo da Corte",
        "motto": "Só se vive uma vez",
        "core_desire": "Viver o momento com alegria",
        "goal": "Se divertir, iluminar o dia dos outros",
        "fear": "Ficar entediado, ser chato",
        "strategy": "Brincar, fazer piadas, ser leve",
    },
    BrandArchetype.EVERYMAN: {
        "name": "O Cara Comum",
        "motto": "Todos somos iguais",
        "core_desire": "Conexão com os outros, pertencimento",
        "goal": "Se encaixar, ser aceito",
        "fear": "Ficar de fora, ser diferente",
        "strategy": "Ser genuíno, mostrar vulnerabilidade",
    },
    BrandArchetype.CAREGIVER: {
        "name": "O Cuidador",
        "motto": "Ame seu próximo como a si mesmo",
        "core_desire": "Proteger e cuidar dos outros",
        "goal": "Ajudar, servir, dar suporte",
        "fear": "Egoísmo, ingratidão",
        "strategy": "Fazer pelos outros o que gostaria que fizessem",
    },
    BrandArchetype.RULER: {
        "name": "O Governante",
        "motto": "O poder não é dado, é conquistado",
        "core_desire": "Controle, poder, status",
        "goal": "Criar prosperidade e ordem",
        "fear": "Caos, perder o controle",
        "strategy": "Liderar, assumir responsabilidade",
    },
    BrandArchetype.CREATOR: {
        "name": "O Criador",
        "motto": "A imaginação é mais importante que o conhecimento",
        "core_desire": "Criar algo de valor duradouro",
        "goal": "Dar forma à visão, expressar identidade",
        "fear": "Ter uma visão medíocre",
        "strategy": "Desenvolver habilidade artística, inovar",
    },
}

ARCHETYPE_CONTENT: dict[BrandArchetype, dict[str, Any]] = {
    BrandArchetype.INNOCENT: {
        "style": "Otimista, simples, acessível, puro",
        "content_types": [
            "guia para iniciantes",
            "benefícios",
            "histórias de sucesso simples",
        ],
        "tone": "Acalmador, esperançoso, amigável",
        "keywords": [
            "fácil",
            "simples",
            "comece",
            "grátis",
            "passo a passo",
            "para iniciantes",
        ],
    },
    BrandArchetype.SAGE: {
        "style": "Analítico, profundo, bem-pesquisado, intelectual",
        "content_types": ["guia completo", "pesquisa", "estudo de caso", "whitepaper"],
        "tone": "Autoritativo, educacional, preciso",
        "keywords": [
            "guia completo",
            "tudo sobre",
            "análise",
            "pesquisa",
            "estudo",
            "dados",
        ],
    },
    BrandArchetype.EXPLORER: {
        "style": "Aventureiro, independente, aspiracional, livre",
        "content_types": [
            "novas tendências",
            "possibilidades",
            "destinos",
            "descobertas",
        ],
        "tone": "Empolgante, livre, independente",
        "keywords": ["novo", "descubra", "explore", "liberdade", "além", "horizontes"],
    },
    BrandArchetype.OUTLAW: {
        "style": "Revolucionário, disruptivo, provocador, ousado",
        "content_types": ["revolução", "disruptura", "contra-ataque", "manifesto"],
        "tone": "Desafiador, rebelde, confiante",
        "keywords": [
            "revolução",
            "disruptivo",
            "quebre as regras",
            "rebelde",
            "ousado",
        ],
    },
    BrandArchetype.MAGICIAN: {
        "style": "Transformacional, místico, visionário, surpreendente",
        "content_types": ["transformação", "segredos revelados", "poder oculto"],
        "tone": "Misterioso, transformador, poderoso",
        "keywords": ["transforme", "descubra o segredo", "poder", "milagre", "mágico"],
    },
    BrandArchetype.HERO: {
        "style": "Corajoso, determinado, inspirador, de superação",
        "content_types": ["superação", "desafio", "conquista", "transformação"],
        "tone": "Motivacional, desafiador, vitorioso",
        "keywords": [
            "supere",
            "conquiste",
            "desafio",
            "vitória",
            "persistência",
            "força",
        ],
    },
    BrandArchetype.LOVER: {
        "style": "Sensual, apaixonado, íntimo, belo, emocional",
        "content_types": ["conexão", "paixão", "relacionamento", "beleza"],
        "tone": "Íntimo, sensual, emocional, caloroso",
        "keywords": ["paixão", "amor", "conexão", "intimidade", "emoção", "coração"],
    },
    BrandArchetype.JESTER: {
        "style": "Divertido, irreverente, leve, descontraído, engraçado",
        "content_types": ["humor", "entretenimento", "sátira", "memes"],
        "tone": "Engraçado, leve, irreverente",
        "keywords": [
            "diversão",
            "risada",
            "engraçado",
            "leve",
            "descontraído",
            "feliz",
        ],
    },
    BrandArchetype.EVERYMAN: {
        "style": "Acessível, realista, genuíno, próximo, humano",
        "content_types": ["história real", "pessoa como você", "comunidade"],
        "tone": "Amigável, acessível, genuíno, caloroso",
        "keywords": [
            "você",
            "real",
            "verdadeiro",
            "pessoal",
            "como eu",
            "gente como a gente",
        ],
    },
    BrandArchetype.RULER: {
        "style": "Poderoso, sofisticado, controlado, prestigioso",
        "content_types": ["liderança", "poder", "controle", "status", "excelência"],
        "tone": "Confiante, poderoso, controlado, autoritativo",
        "keywords": ["poder", "liderança", "controle", "domínio", "autoridade", "topo"],
    },
    BrandArchetype.CREATOR: {
        "style": "Inovador, criativo, original, expressivo, autêntico",
        "content_types": [
            "criação",
            "inovação",
            "design",
            "originalidade",
            "expressão",
        ],
        "tone": "Inspirador, visionário, autêntico, inovador",
        "keywords": ["crie", "inove", "original", "design", "expressão", "único"],
    },
}
ARCHETYPE_MARKETING: dict[BrandArchetype, dict[str, Any]] = {
    BrandArchetype.INNOCENT: {
        "brands": ["Coca-Cola", "McDonald's", "Dove"],
        "copy_angle": "Simplicidade que traz felicidade. Promessa de pureza.",
    },
    BrandArchetype.SAGE: {
        "brands": ["Google", "TED", "Harvard", "Coursera"],
        "copy_angle": "Conhecimento como poder. 'Descubra a verdade por trás de [tema]'.",
    },
    BrandArchetype.EXPLORER: {
        "brands": ["Jeep", "The North Face", "Airbnb", "Red Bull"],
        "copy_angle": "Liberdade e descoberta. 'Vá além do óbvio em [nicho]'.",
    },
    BrandArchetype.OUTLAW: {
        "brands": ["Harley-Davidson", "Diesel", "Spotify", "Uber"],
        "copy_angle": "Disrupção e rebeldia. 'Quebre as regras de [nicho]'.",
    },
    BrandArchetype.MAGICIAN: {
        "brands": ["Disney", "Apple", "Dyson", "Tesla"],
        "copy_angle": "Transformação extraordinária. 'Descubra o segredo que muda tudo'.",
    },
    BrandArchetype.HERO: {
        "brands": ["Nike", "Gatorade", "Adidas", "Under Armour"],
        "copy_angle": "Superação e vitória. 'Domine [nicho] e conquiste resultados'.",
    },
    BrandArchetype.LOVER: {
        "brands": ["Chanel", "Victoria's Secret", "Häagen-Dazs", "Godiva"],
        "copy_angle": "Paixão e conexão. 'Para quem busca excelência em [nicho]'.",
    },
    BrandArchetype.JESTER: {
        "brands": ["Skittles", "Old Spice", "Doritos", "M&M's"],
        "copy_angle": "Diversão e leveza. 'Por que [nicho] precisa ser tão sério?'.",
    },
    BrandArchetype.EVERYMAN: {
        "brands": ["IKEA", "Levi's", "Volkswagen", "Walmart"],
        "copy_angle": "Acessível e real. '[Nicho] para pessoas reais, como você'.",
    },
    BrandArchetype.CAREGIVER: {
        "brands": ["Johnson & Johnson", "Dove", "UNICEF"],
        "copy_angle": "Cuidado e proteção. 'O melhor para você e sua jornada em [nicho]'.",
    },
    BrandArchetype.RULER: {
        "brands": ["Mercedes-Benz", "Rolex", "Microsoft", "American Express"],
        "copy_angle": "Poder e controle. 'Excelência máxima em [nicho]'.",
    },
    BrandArchetype.CREATOR: {
        "brands": ["Apple", "LEGO", "Adobe", "Sony"],
        "copy_angle": "Inovação e originalidade. 'Crie algo extraordinário em [nicho]'.",
    },
}


ARCHETYPE_HEADLINES: dict[BrandArchetype, list[str]] = {
    BrandArchetype.SAGE: [
        "{topic}: Tudo Que Você Precisa Saber Sobre em {niche}",
        "O Guia Definitivo de {topic} Baseado em Dados",
        "{topic}: Análise Completa para Profissionais de {niche}",
    ],
    BrandArchetype.HERO: [
        "Domine {topic} e Conquiste Resultados Extraordinários em {niche}",
        "Supere os Desafios de {topic} no {niche}",
        "A Jornada do Herói: {topic} para Quem Busca Excelência em {niche}",
    ],
    BrandArchetype.EXPLORER: [
        "Descubra Novos Horizontes em {topic} no {niche}",
        "Explore {topic} Além do Óbvio no {niche}",
        "Sua Jornada de Descoberta em {topic} Começa Agora",
    ],
    BrandArchetype.OUTLAW: [
        "Por que {topic} em {niche} é Diferente do Que Você Pensa",
        "O Manifesto Rebelde de {topic} no {niche}",
        "Quebre as Regras: {topic} Não é Sobre o Que Ensinam",
    ],
    BrandArchetype.INNOCENT: [
        "Comece em {topic} de Forma Simples e Fácil em {niche}",
        "Guia para Iniciantes em {topic} no {niche}",
        "{topic} para Quem Está Começando do Zero em {niche}",
    ],
    BrandArchetype.MAGICIAN: [
        "Transforme Seus Resultados com {topic} em {niche}",
        "O Segredo de {topic} Revelado para {niche}",
        "A Fórmula Mágica de {topic} para {niche}",
    ],
    BrandArchetype.RULER: [
        "Domine {topic} e Tome o Controle em {niche}",
        "Excelência em {topic}: O Padrão dos Líderes em {niche}",
        "{topic} no Mais Alto Nível para Profissionais de {niche}",
    ],
}

ARCHETYPE_SEGMENTS: dict[BrandArchetype, list[str]] = [
    "Existe um jeito mais inteligente de {tema} em {nicho}. E eu vou te mostrar.",
]
ARCHETYPE_SEGMENTS = {
    BrandArchetype.SAGE: [
        "A verdade sobre {topic} em {niche} é baseada em dados, não em opiniões. Deixe-me mostrar o que a pesquisa realmente diz.",
    ],
    BrandArchetype.HERO: [
        "Você já enfrentou {problema} em {niche}? Pois é, eu também. Mas descobri que {topic} pode ser a virada de chave.",
    ],
    BrandArchetype.EXPLORER: [
        "Existe um mundo além do básico em {topic}. Um mundo onde profissionais de {niche} encontram resultados extraordinários.",
    ],
}


class ArchetypeEngine:
    """Engine for archetype-based content strategy."""

    @staticmethod
    def get_archetype(archetype: BrandArchetype) -> ArchetypeExpression:
        return ArchetypeExpression(archetype)

    @staticmethod
    def get_all_archetypes() -> list[dict[str, Any]]:
        return [ArchetypeExpression(a).to_dict() for a in BrandArchetype]

    @staticmethod
    def select_for_niche(niche: str, goal: str = "convert") -> list[BrandArchetype]:
        """Select best archetypes for a niche."""
        archetype_niches = {
            "financas": [
                BrandArchetype.RULER,
                BrandArchetype.SAGE,
                BrandArchetype.HERO,
            ],
            "saude": [
                BrandArchetype.CAREGIVER,
                BrandArchetype.INNOCENT,
                BrandArchetype.HERO,
            ],
            "tecnologia": [
                BrandArchetype.CREATOR,
                BrandArchetype.SAGE,
                BrandArchetype.EXPLORER,
            ],
            "marketing": [
                BrandArchetype.MAGICIAN,
                BrandArchetype.EXPLORER,
                BrandArchetype.SAGE,
            ],
            "empreendedorismo": [
                BrandArchetype.HERO,
                BrandArchetype.RULER,
                BrandArchetype.OUTLAW,
            ],
            "educacao": [
                BrandArchetype.SAGE,
                BrandArchetype.INNOCENT,
                BrandArchetype.CAREGIVER,
            ],
            "bem_estar": [
                BrandArchetype.CAREGIVER,
                BrandArchetype.LOVER,
                BrandArchetype.INNOCENT,
            ],
            "moda": [
                BrandArchetype.LOVER,
                BrandArchetype.CREATOR,
                BrandArchetype.EXPLORER,
            ],
            "games": [
                BrandArchetype.JESTER,
                BrandArchetype.HERO,
                BrandArchetype.EXPLORER,
            ],
        }
        niche_lower = niche.lower()
        for key, archetypes in archetype_niches.items():
            if key in niche_lower or niche_lower in key:
                return archetypes
        return [BrandArchetype.SAGE, BrandArchetype.HERO, BrandArchetype.EVERYMAN]

    @staticmethod
    def generate_brand_voice_guide(
        niche: str, primary: BrandArchetype, secondary: BrandArchetype
    ) -> dict[str, Any]:
        """Generate a complete brand voice guide combining two archetypes."""
        primary_exp = ArchetypeExpression(primary)
        secondary_exp = ArchetypeExpression(secondary)
        return {
            "primary_archetype": primary_exp.to_dict(),
            "secondary_archetype": secondary_exp.to_dict(),
            "voice_blend": f"Main {primary_exp.core.get('name')} energy with a touch of {secondary_exp.core.get('name')}",
            "tone_rules": [
                f"Speak with {primary_exp.content.get('tone', 'confidence')}",
                f"Add {secondary_exp.content.get('style', 'subtlety')} where appropriate",
                f"Use keywords from both: {primary_exp.content.get('keywords', [])[:3]} + {secondary_exp.content.get('keywords', [])[:3]}",
            ],
            "content_mix": [
                f"70% {primary.value} style content",
                f"30% {secondary.value} style content",
            ],
        }
