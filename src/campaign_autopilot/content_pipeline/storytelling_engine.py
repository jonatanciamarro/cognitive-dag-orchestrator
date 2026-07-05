"""Storytelling Engine — narrative structures for persuasive content.

Provides story arcs, beats, and narrative frameworks for creating
engaging, emotionally-resonant content. Based on proven storytelling
methodologies: Hero's Journey, 3-Act Structure, Pixar Story Spine,
and marketing-specific frameworks.

All using Python stdlib and templates (zero external dependencies).
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any


class NarrativeStructure(Enum):
    """Proven narrative frameworks for content."""

    HERO_JOURNEY = "hero_journey"  # Campbell's monomyth
    THREE_ACT = "three_act"  # Classic 3-act structure
    STORY_SPINE = "story_spine"  # Pixar story spine
    PROBLEM_SOLUTION = "problem_solution"  # Before/after transformation
    AIDA = "aida"  # Attention-Interest-Desire-Action
    PAS = "pas"  # Problem-Agonize-Solution
    FEAR_GREED_URGENCY = "fear_greed_urgency"  # FGU framework
    FOUR_PS = "four_ps"  # Promise-Picture-Proof-Push
    BEFORE_AFTER_BRIDGE = "before_after_bridge"  # BAB framework
    HOOK_STORY_OFFER = "hook_story_offer"  # HSO for video/reels


class StoryBeat(Enum):
    """Individual story beats within a narrative structure."""

    # Universal beats
    HOOK = "hook"
    CONTEXT = "context"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    TRANSFORMATION = "transformation"

    # Marketing-specific beats
    PAIN_POINT = "pain_point"
    AGONY = "agony"
    REVELATION = "revelation"
    SOLUTION = "solution"
    OBJECTION_HANDLING = "objection_handling"
    SOCIAL_PROOF = "social_proof"
    URGENCY = "urgency"
    CALL_TO_ACTION = "call_to_action"


class StoryArc:
    """A complete narrative arc with structured beats."""

    def __init__(self, structure: NarrativeStructure):
        self.structure = structure
        self.beats: list[dict[str, Any]] = []
        self._build_arc()

    def _build_arc(self) -> None:
        """Build the story arc based on the chosen structure."""
        builders = {
            NarrativeStructure.HERO_JOURNEY: self._build_hero_journey,
            NarrativeStructure.THREE_ACT: self._build_three_act,
            NarrativeStructure.STORY_SPINE: self._build_story_spine,
            NarrativeStructure.PROBLEM_SOLUTION: self._build_problem_solution,
            NarrativeStructure.AIDA: self._build_aida,
            NarrativeStructure.PAS: self._build_pas,
            NarrativeStructure.BEFORE_AFTER_BRIDGE: self._build_bab,
            NarrativeStructure.HOOK_STORY_OFFER: self._build_hso,
        }
        builder = builders.get(self.structure, self._build_aida)
        builder()

    def _build_hero_journey(self) -> None:
        """Build Campbell's Hero's Journey for content."""
        self.beats = [
            {
                "beat": StoryBeat.CONTEXT,
                "title": "O Mundo Comum",
                "description": "Apresente o leitor no estado atual dele",
                "emotion": "familiaridade",
            },
            {
                "beat": StoryBeat.INCITING_INCIDENT,
                "title": "O Chamado à Aventura",
                "description": "Mostre o problema ou oportunidade que surge",
                "emotion": "curiosidade",
            },
            {
                "beat": StoryBeat.RISING_ACTION,
                "title": "A Jornada",
                "description": "Os passos e desafios para resolver",
                "emotion": "tensão crescente",
            },
            {
                "beat": StoryBeat.CLIMAX,
                "title": "O Momento de Virada",
                "description": "A descoberta ou decisão crucial",
                "emotion": "revelação",
            },
            {
                "beat": StoryBeat.RESOLUTION,
                "title": "O Retorno com o Elixir",
                "description": "O resultado positivo e o aprendizado",
                "emotion": "satisfação",
            },
            {
                "beat": StoryBeat.TRANSFORMATION,
                "title": "A Transformação",
                "description": "Como o leitor pode aplicar e mudar",
                "emotion": "inspiração",
            },
        ]

    def _build_three_act(self) -> None:
        self.beats = [
            {
                "beat": StoryBeat.HOOK,
                "title": "Setup",
                "description": "Apresente o cenário e o protagonista",
                "emotion": "interesse",
            },
            {
                "beat": StoryBeat.INCITING_INCIDENT,
                "title": "Confrontation",
                "description": "O problema ou conflito aparece",
                "emotion": "tensão",
            },
            {
                "beat": StoryBeat.RISING_ACTION,
                "title": "Rising Action",
                "description": "Tentativas e obstáculos",
                "emotion": "expectativa",
            },
            {
                "beat": StoryBeat.CLIMAX,
                "title": "Clímax",
                "description": "O momento decisivo",
                "emotion": "catarse",
            },
            {
                "beat": StoryBeat.RESOLUTION,
                "title": "Resolução",
                "description": "O desfecho e aprendizado",
                "emotion": "alívio",
            },
        ]

    def _build_story_spine(self) -> None:
        """Pixar-style story spine for emotional content."""
        self.beats = [
            {
                "beat": StoryBeat.CONTEXT,
                "title": "Era uma vez...",
                "description": "Contexto do leitor antes da solução",
                "emotion": "identificação",
            },
            {
                "beat": StoryBeat.INCITING_INCIDENT,
                "title": "Todos os dias...",
                "description": "O problema recorrente",
                "emotion": "frustração",
            },
            {
                "beat": StoryBeat.RISING_ACTION,
                "title": "Até que um dia...",
                "description": "A descoberta de algo novo",
                "emotion": "esperança",
            },
            {
                "beat": StoryBeat.CLIMAX,
                "title": "Por causa disso...",
                "description": "A mudança que aconteceu",
                "emotion": "entusiasmo",
            },
            {
                "beat": StoryBeat.RESOLUTION,
                "title": "Até que finalmente...",
                "description": "O resultado final",
                "emotion": "realização",
            },
            {
                "beat": StoryBeat.TRANSFORMATION,
                "title": "E desde então...",
                "description": "Como a vida mudou",
                "emotion": "gratidão",
            },
        ]

    def _build_problem_solution(self) -> None:
        self.beats = [
            {
                "beat": StoryBeat.PAIN_POINT,
                "title": "A Dor",
                "description": "Descreva o problema que o leitor enfrenta",
                "emotion": "reconhecimento",
            },
            {
                "beat": StoryBeat.AGONY,
                "title": "A Agonia",
                "description": "Aprofunde a dor e suas consequências",
                "emotion": "desconforto",
            },
            {
                "beat": StoryBeat.REVELATION,
                "title": "A Revelação",
                "description": "Mostre que existe uma solução",
                "emotion": "esperança",
            },
            {
                "beat": StoryBeat.SOLUTION,
                "title": "A Solução",
                "description": "Apresente sua solução específica",
                "emotion": "alívio",
            },
            {
                "beat": StoryBeat.SOCIAL_PROOF,
                "title": "A Prova",
                "description": "Depoimentos e resultados",
                "emotion": "confiança",
            },
            {
                "beat": StoryBeat.CALL_TO_ACTION,
                "title": "O Próximo Passo",
                "description": "Chamada para ação clara",
                "emotion": "urgência",
            },
        ]

    def _build_aida(self) -> None:
        self.beats = [
            {
                "beat": StoryBeat.HOOK,
                "title": "Atenção",
                "description": "Chame a atenção com um gancho forte",
                "emotion": "surpresa",
            },
            {
                "beat": StoryBeat.RISING_ACTION,
                "title": "Interesse",
                "description": "Mantenha o interesse com informações relevantes",
                "emotion": "curiosidade",
            },
            {
                "beat": StoryBeat.CLIMAX,
                "title": "Desejo",
                "description": "Crie desejo pela solução",
                "emotion": "desejo",
            },
            {
                "beat": StoryBeat.CALL_TO_ACTION,
                "title": "Ação",
                "description": "Peça a ação de forma direta",
                "emotion": "urgência",
            },
        ]

    def _build_pas(self) -> None:
        self.beats = [
            {
                "beat": StoryBeat.PAIN_POINT,
                "title": "Problema",
                "description": "Identifique o problema específico",
                "emotion": "identificação",
            },
            {
                "beat": StoryBeat.AGONY,
                "title": "Agonize",
                "description": "Faça o leitor sentir a dor do problema",
                "emotion": "desconforto",
            },
            {
                "beat": StoryBeat.SOLUTION,
                "title": "Solução",
                "description": "Apresente a solução de forma irresistível",
                "emotion": "alívio",
            },
        ]

    def _build_bab(self) -> None:
        self.beats = [
            {
                "beat": StoryBeat.CONTEXT,
                "title": "Antes",
                "description": "Como era antes (situação atual)",
                "emotion": "reconhecimento",
            },
            {
                "beat": StoryBeat.TRANSFORMATION,
                "title": "Depois",
                "description": "Como pode ser depois (situação desejada)",
                "emotion": "desejo",
            },
            {
                "beat": StoryBeat.SOLUTION,
                "title": "Ponte",
                "description": "A ponte que leva do antes ao depois",
                "emotion": "esperança",
            },
        ]

    def _build_hso(self) -> None:
        """Hook-Story-Offer structure for short-form video."""
        self.beats = [
            {
                "beat": StoryBeat.HOOK,
                "title": "Hook (3s)",
                "description": "Gancho que prende a atenção nos primeiros 3 segundos",
                "emotion": "curiosidade",
            },
            {
                "beat": StoryBeat.RISING_ACTION,
                "title": "Story (15-30s)",
                "description": "História curta com contexto e transformação",
                "emotion": "conexão",
            },
            {
                "beat": StoryBeat.CALL_TO_ACTION,
                "title": "Offer (10s)",
                "description": "Oferta clara com chamada para ação",
                "emotion": "urgência",
            },
        ]

    def render_outline(self, topic: str, niche: str) -> list[dict[str, str]]:
        """Render the arc as a concrete content outline for a topic."""
        outline = []
        for i, beat in enumerate(self.beats):
            outline.append(
                {
                    "section": f"{i + 1}. {beat['title']}",
                    "beat": beat["beat"].value,
                    "description": beat["description"],
                    "emotion": beat["emotion"],
                    "writing_prompt": self._generate_prompt(beat, topic, niche),
                }
            )
        return outline

    def _generate_prompt(self, beat: dict, topic: str, niche: str) -> str:
        """Generate a writing prompt for this beat."""
        prompts = {
            StoryBeat.HOOK: f"Abra com um fato surpreendente ou pergunta provocativa sobre {topic} em {niche}",
            StoryBeat.CONTEXT: f"Descreva a situação atual de quem está começando em {niche} sem conhecer {topic}",
            StoryBeat.PAIN_POINT: f"Descreva a frustração específica de quem tenta {topic} sem sucesso em {niche}",
            StoryBeat.AGONY: f"Aprofunde as consequências negativas de ignorar {topic} em {niche}",
            StoryBeat.REVELATION: f"Apresente a{'descoberta'} que muda tudo sobre {topic}",
            StoryBeat.SOLUTION: f"Explique como {topic} resolve o problema de forma prática em {niche}",
            StoryBeat.SOCIAL_PROOF: f"Inclua exemplos reais de pessoas que tiveram sucesso com {topic}",
            StoryBeat.URGENCY: f"Crie um senso de urgência sobre começar {topic} agora",
            StoryBeat.CALL_TO_ACTION: f"Chamada clara: o que o leitor deve fazer agora sobre {topic}",
        }
        return prompts.get(
            beat["beat"], f"Desenvolva conteúdo sobre {topic} para {niche}"
        )


class StorytellingEngine:
    """Core engine for narrative-driven content creation."""

    @staticmethod
    def create_arc(structure: NarrativeStructure) -> StoryArc:
        """Create a story arc with the given structure."""
        return StoryArc(structure)

    @staticmethod
    def select_structure(content_type: str, goal: str) -> NarrativeStructure:
        """Select the best narrative structure for content type and goal."""
        recommendations = {
            "blog_article": {
                "educate": NarrativeStructure.PROBLEM_SOLUTION,
                "persuade": NarrativeStructure.PAS,
                "inspire": NarrativeStructure.HERO_JOURNEY,
                "sell": NarrativeStructure.BEFORE_AFTER_BRIDGE,
            },
            "video_youtube": {
                "educate": NarrativeStructure.THREE_ACT,
                "persuade": NarrativeStructure.STORY_SPINE,
                "entertain": NarrativeStructure.HERO_JOURNEY,
            },
            "video_tiktok": {
                "hook": NarrativeStructure.HOOK_STORY_OFFER,
                "educate": NarrativeStructure.PAS,
                "sell": NarrativeStructure.AIDA,
            },
            "email": {
                "educate": NarrativeStructure.AIDA,
                "sell": NarrativeStructure.PAS,
                "engage": NarrativeStructure.STORY_SPINE,
            },
            "social": {
                "engage": NarrativeStructure.HOOK_STORY_OFFER,
                "educate": NarrativeStructure.PAS,
                "sell": NarrativeStructure.AIDA,
            },
        }
        type_recs = recommendations.get(content_type, {})
        return type_recs.get(goal, NarrativeStructure.PROBLEM_SOLUTION)

    @staticmethod
    def generate_hook(niche: str, topic: str, hook_type: str = "question") -> str:
        """Generate a powerful hook for any content."""
        hooks = {
            "question": [
                f"Você sabia que 97% das pessoas que começam em {niche} desistem nos primeiros 3 meses?",
                f"Qual é o maior erro que iniciantes cometem em {topic}?",
                f"E se eu te dissesse que {topic} não é tão complicado quanto parece?",
                f"Por que algumas pessoas prosperam em {niche} enquanto outras fracassam?",
            ],
            "statistic": [
                f"Estudos mostram que pessoas que dominam {topic} ganham 3x mais em {niche}.",
                f"90% dos profissionais de {niche} concordam: {topic} é a habilidade mais importante.",
                f"O mercado de {topic} cresceu 340% nos últimos 2 anos em {niche}.",
            ],
            "story": [
                f"Era uma vez um iniciante em {niche} que não sabia nada sobre {topic}...",
                f"Deixa eu te contar como {topic} transformou completamente meus resultados em {niche}.",
                f"Eu estava exatamente onde você está agora, sem saber por onde começar em {topic}.",
            ],
            "provocation": [
                f"Se você ainda não domina {topic}, você está perdendo dinheiro em {niche}.",
                f"Parabéns! Se você está buscando {topic}, você já está à frente de 90% das pessoas.",
                f"O segredo que ninguém conta sobre {topic} em {niche}.",
            ],
            "curiosity_gap": [
                f"O que {topic} tem a ver com {niche}? Mais do que você imagina.",
                f"As 5 palavras que mudam TUDO em {topic} para profissionais de {niche}.",
                f"O método de {topic} que os experts de {niche} não querem que você conheça.",
            ],
        }
        pool = hooks.get(hook_type, hooks["question"])
        return random.choice(pool)

    @staticmethod
    def generate_title(niche: str, topic: str, format_type: str = "guide") -> str:
        """Generate an optimized content title using proven formulas."""
        templates = {
            "guide": [
                f"{topic}: O Guia Completo para Iniciantes em {niche}",
                f"Guia Definitivo de {topic} para Quem Está Começando em {niche}",
                f"{topic}: Do Zero ao Avançado em {niche}",
            ],
            "list": [
                f"7 Estratégias Comprovadas de {topic} para {niche}",
                f"10 Segredos de {topic} que Profissionais de {niche} Usam",
                f"5 Erros de {topic} que Estão te Custando Resultados em {niche}",
            ],
            "review": [
                f"Review Completo: A Melhor Ferramenta de {topic} para {niche}",
                f"{topic} Vale a Pena? Análise Honesta para Profissionais de {niche}",
            ],
            "comparison": [
                f"{topic} vs Alternativas: Qual é a Melhor para {niche}?",
                f"As Melhores Opções de {topic} para {niche} em 2026",
            ],
            "tutorial": [
                f"Como Dominar {topic} em {niche} em 7 Dias",
                f"Passo a Passo de {topic} para Iniciantes em {niche}",
                f"Tutorial Completo de {topic} para {niche}",
            ],
        }
        pool = templates.get(format_type, templates["guide"])
        return random.choice(pool)

    @staticmethod
    def generate_cta(niche: str, cta_type: str = "soft") -> str:
        """Generate persuasive call-to-action."""
        ctas = {
            "soft": [
                f"Quer saber mais sobre {niche}? Deixe seu comentário abaixo!",
                "O que você achou? Compartilhe sua experiência nos comentários.",
                "Salve este post para consultar depois!",
            ],
            "medium": [
                f"Compartilhe este conteúdo com alguém que está começando em {niche}.",
                f"Siga nosso perfil para mais dicas de {niche} todos os dias.",
                f"Inscreva-se no canal para não perder nenhum conteúdo sobre {niche}.",
            ],
            "hard": [
                f"Clique aqui para acessar o guia completo de {niche}.",
                f"Garanta seu acesso à ferramenta que vai transformar seus resultados em {niche}.",
                f"Comece agora: baixe o material exclusivo sobre {niche}.",
            ],
        }
        pool = ctas.get(cta_type, ctas["soft"])
        return random.choice(pool)

    @staticmethod
    def get_all_structures() -> list[dict[str, Any]]:
        """Return all available narrative structures with descriptions."""
        return [
            {
                "id": "hero_journey",
                "name": "Jornada do Herói",
                "description": "Clássica estrutura de transformação. Ideal para conteúdos inspiradores.",
                "best_for": "Artigos de transformação, cases de sucesso, storytelling de marca",
            },
            {
                "id": "three_act",
                "name": "3 Atos",
                "description": "Estrutura universal. Setup, confronto, resolução.",
                "best_for": "Tutoriais, vídeos educacionais, webinars",
            },
            {
                "id": "problem_solution",
                "name": "Problema-Solução",
                "description": "Mostre a dor e a solução. Alto poder de conversão.",
                "best_for": "Artigos de afiliados, páginas de venda, reviews",
            },
            {
                "id": "pas",
                "name": "PAS (Problema-Agonize-Solução)",
                "description": "Framework de copywriting mais poderoso para conversão.",
                "best_for": "Emails de vendas, landing pages, anúncios",
            },
            {
                "id": "aida",
                "name": "AIDA",
                "description": "Atenção-Interesse-Desejo-Ação. Clássico do marketing.",
                "best_for": "Funil de vendas completo, posts de blog",
            },
            {
                "id": "hook_story_offer",
                "name": "Hook-Story-Offer",
                "description": "Perfeito para vídeos curtos. Prende atenção imediata.",
                "best_for": "TikTok, Reels, Shorts, stories",
            },
            {
                "id": "before_after_bridge",
                "name": "Antes-Depois-Ponte",
                "description": "Mostre a transformação. Poderoso para aspiracional.",
                "best_for": "Antes/depois, depoimentos, resultados",
            },
            {
                "id": "story_spine",
                "name": "Story Spine (Pixar)",
                "description": "Estrutura narrativa emocional. Cria conexão profunda.",
                "best_for": "Brand storytelling, conteúdo emocional, histórias pessoais",
            },
        ]
