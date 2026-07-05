"""Neuromarketing Engine — brain-based marketing strategies.

Based on:
- Neuromarketing research (Lindstrom, Dooley, Morin)
- Brain's reward system (dopamine, oxytocin, serotonin)
- Emotional marketing (Limbic system)
- Sensory marketing
- Mirror neurons and empathy
- Cognitive fluency and processing

For optimizing content for the brain's natural responses.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class BrainPrinciple(Enum):
    """Neuromarketing principles based on brain research."""

    # Reward System
    DOPAMINE_ANTICIPATION = "dopamine_anticipation"  # Anticipation of reward
    OXYTOCIN_TRUST = "oxytocin_trust"  # Bonding and trust
    SEROTONIN_STATUS = "serotonin_status"  # Status and validation
    ENDORPHIN_PLEASURE = "endorphin_pleasure"  # Pleasure and relief

    # Cognitive Processing
    COGNITIVE_FLUENCY = "cognitive_fluency"  # Easy to process = feels true
    PRIMING = "priming"  # Prior exposure influences response
    MIRROR_NEURONS = "mirror_neurons"  # Empathy through observation
    ASSOCIATIVE_LEARNING = "associative_learning"  # Pavlovian conditioning

    # Emotional Brain (Limbic)
    EMOTIONAL_CONTAGION = "emotional_contagion"  # Emotions are contagious
    NOSTALGIA = "nostalgia"  # Past positive memories
    LOSS_AVERSION_NEURAL = "loss_aversion_neural"  # Loss > gain in the brain
    STATUS_SEEKING = "status_seeking"  # Social hierarchy drive

    # Attention
    RETICULAR_ACTIVATING = "reticular_activating"  # RAS - novelty detection
    ATTENTION_CASCADE = "attention_cascade"  # Visual attention patterns
    PATTERN_INTERRUPT = "pattern_interrupt"  # Breaking expectations


class SensoryTrigger(Enum):
    """Sensory triggers that activate emotional responses."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    GUSTATORY = "gustatory"  # taste
    OLFACTORY = "olfactory"  # smell
    TACTILE = "tactile"
    KINESTHETIC = "kinesthetic"  # movement
    PROXEMIC = "proxemic"  # space/distance


NEURO_PRINCIPLES_DB: dict[BrainPrinciple, dict[str, str]] = {
    BrainPrinciple.DOPAMINE_ANTICIPATION: {
        "name": "Antecipação de Dopamina",
        "description": "O cérebro libera mais dopamina na ANTECIPAÇÃO de uma recompensa do que ao recebê-la.",
        "content_application": "Crie expectativa. Use 'revelações', 'segredos', 'próximos passos'. Teasers.",
        "copy_example": "O segredo que vou revelar no próximo parágrafo vai mudar sua perspectiva sobre [tema].",
    },
    BrainPrinciple.OXYTOCIN_TRUST: {
        "name": "Ocitocina (Confiança)",
        "description": "Histórias pessoais e vulnerabilidade liberam ocitocina, criando confiança.",
        "content_application": "Use storytelling pessoal. Seja vulnerável. Crie conexão emocional.",
        "copy_example": "Vou ser honesto com você: eu também já fracassei em [tema] antes de descobrir o segredo.",
    },
    BrainPrinciple.COGNITIVE_FLUENCY: {
        "name": "Fluência Cognitiva",
        "description": "Informações fáceis de processar são percebidas como MAIS VERDADEIRAS.",
        "content_application": "Use linguagem simples, parágrafos curtos, imagens, analogias. Evite jargão.",
        "copy_example": "Simples assim: [explicação em 1 linha]. É por isso que funciona.",
    },
    BrainPrinciple.MIRROR_NEURONS: {
        "name": "Neurônios-Espelho",
        "description": "O cérebro 'simula' o que observa. Ver alguém fazendo ativa os mesmos circuitos.",
        "content_application": "Descreva ações de forma vívida. Mostre resultados visuais. Use linguagem sensorial.",
        "copy_example": "Imagine abrir seu computador e ver [resultado]. É exatamente assim que você vai se sentir.",
    },
    BrainPrinciple.EMOTIONAL_CONTAGION: {
        "name": "Contágio Emocional",
        "description": "Emoções são contagiosas. Seu estado emocional influencia o leitor.",
        "content_application": "Transmita entusiasmo genuíno. Use emoção positiva. Empolgação vende.",
        "copy_example": "Estou tão empolgado para compartilhar isso! Quando eu descobri [tema], minha vida mudou completamente.",
    },
    BrainPrinciple.PATTERN_INTERRUPT: {
        "name": "Interrupção de Padrão",
        "description": "O cérebro nota mudanças bruscas. Use para prender atenção.",
        "content_application": "Abra com algo inesperado. Use contraste. Quebre expectativas.",
        "copy_example": "Vou te contar algo que parece absurdo: [afirmação contraintuitiva].",
    },
    BrainPrinciple.NOSTALGIA: {
        "name": "Nostalgia",
        "description": "Memórias positivas do passado criam conexão emocional e confiança.",
        "content_application": "Referencie 'como era antes'. Conecte com memórias compartilhadas.",
        "copy_example": "Lembra quando [referência nostálgica]? Pois é, [tema] era assim. Não precisa mais ser.",
    },
    BrainPrinciple.STATUS_SEEKING: {
        "name": "Busca por Status",
        "description": "O cérebro tem um circuito dedicado a buscar status social.",
        "content_application": "Mostre como o produto/solução eleva o status do usuário.",
        "copy_example": "Pessoas que dominam [tema] são vistas como autoridades. É seu momento de brilhar.",
    },
    BrainPrinciple.PRIMING: {
        "name": "Priming",
        "description": "Exposição prévia influencia resposta subsequente.",
        "content_application": "Use palavras e imagens preparatórias antes do CTA.",
        "copy_example": "Use palavras como 'confiança', 'autoridade', 'sucesso' ANTES da oferta.",
    },
    BrainPrinciple.RETICULAR_ACTIVATING: {
        "name": "Sistema Reticular Ativador",
        "description": "O cérebro filtra o que não é relevante. Novidade quebra o filtro.",
        "content_application": "Use números, palavras novas, perguntas, afirmações surpreendentes.",
        "copy_example": "Número 1: [fato surpreendente]. Você sabia disso sobre [tema]?",
    },
    BrainPrinciple.LOSS_AVERSION_NEURAL: {
        "name": "Aversão à Perda Neural",
        "description": "A perda ativa áreas cerebrais 2x mais fortes que o ganho.",
        "content_application": "Sempre enquadre sua oferta como REDUÇÃO de perda, não apenas ganho.",
        "copy_example": "A cada dia que você espera, você perde [X benefícios]. Não espere mais.",
    },
    BrainPrinciple.ATTENTION_CASCADE: {
        "name": "Cascata de Atenção",
        "description": "Atenção segue padrões específicos (Z, F, N de leitura).",
        "content_application": "Coloque informações mais importantes no canto superior esquerdo. Use headings.",
        "copy_example": "[TÍTULO IMPACTANTE] → [Sub-título com benefício] → [CTA no final]",
    },
}


class NeuromarketingEngine:
    """Engine for brain-optimized content creation."""

    @staticmethod
    def get_principle(principle: BrainPrinciple) -> dict[str, str]:
        """Get detailed information about a neuromarketing principle."""
        return NEURO_PRINCIPLES_DB.get(principle, {})

    @staticmethod
    def get_all_principles() -> list[dict[str, str]]:
        return [
            {"id": p.value, **NEURO_PRINCIPLES_DB.get(p, {})} for p in BrainPrinciple
        ]

    @staticmethod
    def apply_principle_to_content(
        principle: BrainPrinciple,
        topic: str,
        niche: str,
    ) -> dict[str, str]:
        """Get concrete content application for a principle."""
        info = NEURO_PRINCIPLES_DB.get(principle, {})
        return {
            "principle": principle.value,
            "name": info.get("name", ""),
            "strategy": info.get("content_application", ""),
            "copy_example": info.get("copy_example", "")
            .replace("[tema]", topic)
            .replace("[nicho]", niche),
        }

    @staticmethod
    def select_best_principles(content_type: str, goal: str) -> list[BrainPrinciple]:
        """Select optimal neuromarketing principles for content type."""
        recommendations = {
            "blog_article": {
                "educate": [
                    BrainPrinciple.COGNITIVE_FLUENCY,
                    BrainPrinciple.MIRROR_NEURONS,
                ],
                "persuade": [
                    BrainPrinciple.OXYTOCIN_TRUST,
                    BrainPrinciple.EMOTIONAL_CONTAGION,
                ],
                "sell": [
                    BrainPrinciple.DOPAMINE_ANTICIPATION,
                    BrainPrinciple.LOSS_AVERSION_NEURAL,
                ],
            },
            "video_youtube": {
                "hook": [
                    BrainPrinciple.PATTERN_INTERRUPT,
                    BrainPrinciple.RETICULAR_ACTIVATING,
                ],
                "engage": [
                    BrainPrinciple.MIRROR_NEURONS,
                    BrainPrinciple.EMOTIONAL_CONTAGION,
                ],
                "convert": [
                    BrainPrinciple.DOPAMINE_ANTICIPATION,
                    BrainPrinciple.STATUS_SEEKING,
                ],
            },
            "video_tiktok": {
                "hook": [
                    BrainPrinciple.PATTERN_INTERRUPT,
                    BrainPrinciple.RETICULAR_ACTIVATING,
                ],
                "retain": [
                    BrainPrinciple.DOPAMINE_ANTICIPATION,
                    BrainPrinciple.MIRROR_NEURONS,
                ],
            },
            "email": {
                "open": [BrainPrinciple.PATTERN_INTERRUPT, BrainPrinciple.NOSTALGIA],
                "click": [
                    BrainPrinciple.DOPAMINE_ANTICIPATION,
                    BrainPrinciple.COGNITIVE_FLUENCY,
                ],
                "buy": [
                    BrainPrinciple.LOSS_AVERSION_NEURAL,
                    BrainPrinciple.STATUS_SEEKING,
                ],
            },
            "social_media": {
                "stop_scroll": [
                    BrainPrinciple.PATTERN_INTERRUPT,
                    BrainPrinciple.RETICULAR_ACTIVATING,
                ],
                "engage": [
                    BrainPrinciple.EMOTIONAL_CONTAGION,
                    BrainPrinciple.MIRROR_NEURONS,
                ],
                "convert": [
                    BrainPrinciple.DOPAMINE_ANTICIPATION,
                    BrainPrinciple.OXYTOCIN_TRUST,
                ],
            },
        }
        type_recs = recommendations.get(content_type, {})
        return type_recs.get(goal, [BrainPrinciple.COGNITIVE_FLUENCY])

    @staticmethod
    def optimize_for_brain(content_type: str, text: str) -> dict[str, Any]:
        """Analyze content and suggest brain-based optimizations."""
        principles = NeuromarketingEngine.select_best_principles(
            content_type, "persuade"
        )
        suggestions = []
        for p in principles:
            info = NEURO_PRINCIPLES_DB.get(p, {})
            suggestions.append(
                {
                    "principle": p.value,
                    "name": info.get("name", ""),
                    "suggestion": info.get("content_application", ""),
                }
            )
        return {
            "content_length": len(text),
            "suggested_principles": len(principles),
            "recommendations": suggestions,
            "fluency_score": NeuromarketingEngine._calculate_fluency(text),
        }

    @staticmethod
    def _calculate_fluency(text: str) -> float:
        """Calculate cognitive fluency score (0-100)."""
        words = text.split()
        if not words:
            return 50.0
        avg_word_len = sum(len(w) for w in words) / len(words)
        sentence_count = max(1, text.count(".") + text.count("!") + text.count("?"))
        avg_sentence_len = len(words) / sentence_count
        # Shorter words and sentences = more fluent
        fluency = 100 - (avg_word_len * 5 + avg_sentence_len * 0.5)
        return max(0, min(100, fluency))
