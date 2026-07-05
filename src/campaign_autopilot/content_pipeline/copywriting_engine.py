"""Copywriting Engine — high-conversion copy frameworks.

Based on proven copywriting frameworks:
- Direct response copywriting
- Storyselling (story-driven sales)
- Features-Advantages-Benefits (FAB)
- AIDA, PAS, BAB frameworks
- Objection handling
- Social proof integration
- Urgency and scarcity tactics

All in Python stdlib (zero external dependencies).
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any


class CopyFramework(Enum):
    """Proven copywriting frameworks for different contexts."""

    AIDA = "aida"  # Attention-Interest-Desire-Action
    PAS = "pas"  # Problem-Agonize-Solution
    BAB = "bab"  # Before-After-Bridge
    FAB = "fab"  # Features-Advantages-Benefits
    QUEST = "quest"  # Quality story framework
    SLAP = "slap"  # Stop-Look-Act-Purchase
    FOUR_PS = "four_ps"  # Promise-Picture-Proof-Push
    ACCA = "acca"  # Awareness-Comprehension-Conviction-Action
    SSS = "sss"  # Star-Story-Solution


class PersuasiveElement(Enum):
    """Building blocks of persuasive copy."""

    # Openers
    HOOK = "hook"
    QUESTION = "question"
    STATISTIC = "statistic"
    STORY_OPENER = "story_opener"

    # Body
    PAINT_PAIN = "paint_pain"
    AGITATE = "agitate"
    PRESENT_SOLUTION = "present_solution"
    FEATURES = "features"
    BENEFITS = "benefits"
    PROOF = "proof"
    TESTIMONIAL = "testimonial"
    GUARANTEE = "guarantee"
    OBJECTIONS = "objections"

    # Closers
    SCARCITY = "scarcity"
    BONUS = "bonus"
    CTA = "cta"
    PSS = "postscript"  # P.S. — most read part


# ── Framework Definitions ───────────────────────────────────────

FRAMEWORKS: dict[CopyFramework, dict[str, Any]] = {
    CopyFramework.AIDA: {
        "name": "AIDA",
        "description": "Attention → Interest → Desire → Action. Clássico universal.",
        "best_for": "Landing pages, emails, anúncios",
        "template": {
            "attention": "Hook forte que prende a atenção (título impactante, pergunta, fato inesperado)",
            "interest": "Mantenha o interesse com informações relevantes para o leitor",
            "desire": "Crie desejo profundo mostrando benefícios e transformação",
            "action": "Call to action claro, específico e urgente",
        },
    },
    CopyFramework.PAS: {
        "name": "PAS (Problem-Agonize-Solution)",
        "description": "Problem → Agonize → Solution. Taxa de conversão mais alta comprovada.",
        "best_for": "Emails de venda, landing pages, copy curta",
        "template": {
            "problem": "Identifique o problema específico que o leitor enfrenta",
            "agonize": "Aprofunde a dor. Faça o leitor SENTIR o desconforto de não resolver",
            "solution": "Apresente sua solução como o alívio natural e inevitável",
        },
    },
    CopyFramework.BAB: {
        "name": "BAB (Before-After-Bridge)",
        "description": "Before → After → Bridge. Foco na transformação.",
        "best_for": "Vídeos, landing pages, copy aspiracional",
        "template": {
            "before": "Descreva o estado atual negativo do leitor",
            "after": "Pinte o quadro do estado desejado após a solução",
            "bridge": "Apresente sua solução como a ponte entre os dois estados",
        },
    },
    CopyFramework.FAB: {
        "name": "FAB (Features-Advantages-Benefits)",
        "description": "Features → Advantages → Benefits. Traduz características em valor.",
        "best_for": "Páginas de produto, reviews, comparações",
        "template": {
            "features": "Liste as características do que você oferece",
            "advantages": "Explique qual vantagem cada característica traz",
            "benefits": "Traduza em benefício emocional para o leitor",
        },
    },
    CopyFramework.SSS: {
        "name": "SSS (Star-Story-Solution)",
        "description": "Star → Story → Solution. Storyselling poderoso.",
        "best_for": "Brand storytelling, cases de sucesso, conteúdo longo",
        "template": {
            "star": "Apresente o protagonista (pode ser o leitor ou um case)",
            "story": "Conte a jornada com desafios, descobertas e transformação",
            "solution": "Mostre como a solução foi o catalisador da transformação",
        },
    },
}

# ── Copy Blocks Database ────────────────────────────────────────


class CopyBlocks:
    """Pre-built copy blocks for quick content assembly."""

    # Hooks
    HOOKS: dict[str, list[str]] = {
        "question": [
            "Você sabia que a maioria das pessoas comete esse erro em {nicho}?",
            "Qual foi a última vez que você tentou {tema} e não deu certo?",
            "E se eu te dissesse que {tema} pode ser mais simples do que parece?",
        ],
        "statistic": [
            "Estudos mostram que 97% das pessoas desistem de {nicho} nos primeiros 3 meses.",
            "Segundo dados do mercado, quem domina {tema} ganha 3x mais em {nicho}.",
            "O mercado de {tema} cresceu 340% em {nicho} nos últimos 2 anos.",
        ],
        "story": [
            "Deixe eu te contar uma história que vai mudar sua perspectiva sobre {tema} em {nicho}.",
            "Eu estava exatamente onde você está agora: perdido, sem saber por onde começar em {tema}.",
        ],
        "provocation": [
            "O maior erro que você pode cometer em {nicho} é ignorar {tema}.",
            "Enquanto você espera, seus concorrentes estão dominando {tema}.",
        ],
    }

    # Pain agitations
    PAIN: list[str] = [
        "É frustrante, não é? Você tenta, erra, tenta de novo, e os resultados não vêm.",
        "Essa dor que você sente toda vez que pensa em {tema} não é sua culpa. Ninguém te ensinou o caminho certo.",
        "Sabe o que é mais irritante? Ver outras pessoas tendo sucesso em {nicho} enquanto você ainda está lutando.",
    ]

    # Benefits
    BENEFITS: list[str] = [
        "Imagine acordar e sentir que você finalmente domina {tema}. A confiança de saber exatamente o que fazer.",
        "Pense na liberdade de ter um método que funciona. Resultados previsíveis. Sem adivinhação.",
        "O que você faria com {resultado} extra todo mês? Como sua vida mudaria?",
    ]

    # Social proof
    PROOF: list[str] = [
        "Mais de {X} pessoas já transformaram seus resultados em {nicho} com {tema}.",
        "Veja o que {testemunha} disse depois de aplicar {tema}: '{depoimento}'.",
        "{X}% dos profissionais que adotaram {tema} viram resultados em até {prazo}.",
    ]

    # CTAs
    CTAS: dict[str, list[str]] = {
        "soft": [
            "Quer saber mais? Deixe seu comentário abaixo.",
            "Compartilhe este conteúdo com quem precisa saber disso.",
            "Salve este post para consultar depois.",
        ],
        "medium": [
            "Clique no link para acessar o guia completo.",
            "Inscreva-se gratuitamente para receber mais conteúdos como este.",
            "Baixe agora o material complementar sobre {tema}.",
        ],
        "hard": [
            "Não espere mais. Clique aqui e comece sua transformação hoje.",
            "Garanta sua vaga agora. Vagas limitadas.",
            "Comece agora. Seu futuro em {nicho} agradece.",
        ],
    }

    # Urgency/Scarcity
    URGENCY: list[str] = [
        "Esta oportunidade não vai durar para sempre.",
        "Daqui a {prazo}, você vai se perguntar por que não começou hoje.",
        "As pessoas que agem agora estão à frente. As que esperam, ficam para trás.",
    ]


class CopywritingEngine:
    """Engine for persuasive copywriting."""

    @staticmethod
    def get_framework(framework: CopyFramework) -> dict[str, Any]:
        return dict(FRAMEWORKS.get(framework, {}))

    @staticmethod
    def get_all_frameworks() -> list[dict[str, Any]]:
        return [{"id": f.value, **FRAMEWORKS.get(f, {})} for f in CopyFramework]

    @staticmethod
    def select_best_framework(content_type: str, goal: str) -> CopyFramework:
        recommendations = {
            "landing_page": {
                "convert": CopyFramework.AIDA,
                "lead": CopyFramework.PAS,
            },
            "email": {
                "sell": CopyFramework.PAS,
                "engage": CopyFramework.SSS,
                "welcome": CopyFramework.BAB,
            },
            "blog_article": {
                "educate": CopyFramework.FAB,
                "persuade": CopyFramework.SSS,
                "sell": CopyFramework.AIDA,
            },
            "video": {
                "convert": CopyFramework.BAB,
                "educate": CopyFramework.SSS,
                "hook": CopyFramework.PAS,
            },
            "social_media": {
                "convert": CopyFramework.PAS,
                "engage": CopyFramework.SSS,
            },
        }
        type_recs = recommendations.get(content_type, {})
        return type_recs.get(goal, CopyFramework.AIDA)

    @staticmethod
    def generate_copy_outline(
        framework: CopyFramework, topic: str, niche: str
    ) -> dict[str, Any]:
        """Generate a complete copy outline using a framework."""
        fw = FRAMEWORKS.get(framework, {})
        template = fw.get("template", {})
        outline = []
        for section, instruction in template.items():
            prompt = CopywritingEngine._generate_section_prompt(section, topic, niche)
            outline.append(
                {
                    "section": section,
                    "instruction": instruction,
                    "writing_prompt": prompt,
                }
            )
        return {
            "framework": framework.value,
            "name": fw.get("name", ""),
            "description": fw.get("description", ""),
            "outline": outline,
        }

    @staticmethod
    def _generate_section_prompt(section: str, topic: str, niche: str) -> str:
        prompts = {
            "hook": f"Escreva um gancho de 1 frase sobre {topic} em {niche} que seja surpreendente ou contraintuitivo.",
            "problem": f"Descreva o problema principal de quem não domina {topic} em {niche}.",
            "agonize": f"Aprofunde a frustração: o que o leitor perde financeira e emocionalmente sem {topic}.",
            "solution": f"Apresente {topic} como a solução. Como resolve o problema de forma prática?",
            "before": f"Pinte o quadro do 'antes': como é a vida do leitor SEM {topic} em {niche}.",
            "after": f"Pinte o quadro do 'depois': como é a vida do leitor COM {topic} em {niche}.",
            "bridge": f"Faça a ponte: como {topic} leva do antes ao depois de forma específica.",
            "features": f"Liste 3 características principais de {topic} para {niche}.",
            "benefits": "Traduza cada característica em benefício emocional para o leitor.",
        }
        return prompts.get(section, f"Desenvolva {section} sobre {topic} em {niche}.")

    @staticmethod
    def generate_hook(niche: str, topic: str, style: str = "question") -> str:
        """Generate a powerful copy hook."""
        pool = CopyBlocks.HOOKS.get(style, CopyBlocks.HOOKS["question"])
        return random.choice(pool).replace("{nicho}", niche).replace("{tema}", topic)

    @staticmethod
    def generate_cta(niche: str, intensity: str = "medium") -> str:
        """Generate a call-to-action."""
        pool = CopyBlocks.CTAS.get(intensity, CopyBlocks.CTAS["medium"])
        return random.choice(pool).replace("{nicho}", niche)

    @staticmethod
    def generate_benefit(topic: str, niche: str) -> str:
        """Generate a benefit statement."""
        return (
            random.choice(CopyBlocks.BENEFITS)
            .replace("{tema}", topic)
            .replace("{nicho}", niche)
        )

    @staticmethod
    def generate_urgency() -> str:
        return random.choice(CopyBlocks.URGENCY)

    @staticmethod
    def assemble_short_copy(framework: CopyFramework, topic: str, niche: str) -> str:
        """Assemble a short persuasive copy using the framework."""
        outline = CopywritingEngine.generate_copy_outline(framework, topic, niche)
        parts = []
        for item in outline.get("outline", []):
            prompt = item.get("writing_prompt", "")
            parts.append(prompt)
        return "\n\n".join(parts)

    @staticmethod
    def objection_handler(niche: str, objections: list[str]) -> list[dict[str, str]]:
        common_objections = {
            "preco": f"{objections[0] if objections else 'É caro'} - Na verdade, o custo de {niche} é menor que o custo de NÃO agir. Pense no ROI.",
            "tempo": "Nunca tenho tempo - O método foi criado justamente para quem tem pouco tempo. Resultados com 30 minutos por dia.",
            "iniciante": "Sou muito novo nisso - Todo expert já foi iniciante. O segredo é começar com o método certo.",
            "resultado": "Não sei se funciona - Mais de [X] pessoas já tiveram resultados comprovados. A ciência por trás é sólida.",
        }
        return [
            {
                "objection": obj,
                "response": common_objections.get(
                    obj[:5],
                    f"Entendo sua preocupação com {obj}. Aqui está o que você precisa saber...",
                ),
            }
            for obj in objections[:5]
        ]
