"""CTO Media Prompt Architect — Geração de prompts de mídia comthinking CTO.

Aplica o meta-prompt do CTO Executive Director para construir prompts
estruturados de alta qualidade para geração de imagens, vídeos e áudio.

FLUXO:
  PHASE 0 — EXECUTIVE INPUT VALIDATION
  PHASE 0.5 — EPISTEMIC REVIEW (o que sabemos sobre o nicho/audiência)
  PHASE 1 — TECHNICAL CLASSIFICATION (tipo de mídia, formato, objetivo)
  PHASE 2 — DOMAIN MODELING (conceitos visuais/auditivos relevantes)
  PHASE 3 — ARCHITECTURAL DESIGN (elementos, composição, estilo)
  PHASE 4 — QUALITY CHECK (revisão epistemológica do prompt)
  PHASE 5 — PROMPT OUTPUT (prompt final otimizado por provider)

Ponytail: stdlib-only, sem dependências externas.
"""

from __future__ import annotations

import json
import time
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════
# PHASE 0 — EXECUTIVE INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MediaBrief:
    """Brief validado de mídia — o que vamos gerar e por quê."""
    niche: str
    media_type: str  # "image", "video", "audio"
    format_type: str  # "blog_featured", "youtube_thumbnail", "pinterest_pin",
                      # "instagram_post", "social_card", "slideshow",
                      # "voiceover", "podcast"
    target_audience: str = ""
    mood: str = ""  # "professional", "energetic", "calm", "luxury", etc.
    color_palette: str = ""  # "corporate_blue", "warm_sunset", "dark_premium"
    reference_keywords: list[str] = field(default_factory=list)
    brand_name: str = "Lyzer Labs"
    quality_threshold: float = 97.0
    resolution: tuple[int, int] = (1200, 630)
    duration_seconds: int = 30  # for video/audio
    language: str = "pt-BR"


# ═══════════════════════════════════════════════════════════════════
# PHASE 0.5 — EPISTEMIC REVIEW
# ═══════════════════════════════════════════════════════════════════

class EpistemicClass(Enum):
    """Classificação epistêmica de informações."""
    VERIFIED_FACT = "verified_fact"
    ASSUMPTION = "assumption"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"


@dataclass
class EpistemicStatement:
    """Uma declaração com classificação epistêmica."""
    statement: str
    classification: EpistemicClass
    source: str = ""


# ═══════════════════════════════════════════════════════════════════
# DOMAIN MODEL — Conceitos visuais/auditivos por nicho
# ═══════════════════════════════════════════════════════════════════

# Mapa de conceitos visuais por nicho — curadoria CTO
_NICHE_VISUAL_CONCEPTS: dict[str, dict[str, Any]] = {
    "marketing digital": {
        "visual_concepts": [
            "painel de dados e graficos animados",
            "setas de crescimento e conexoes de rede",
            "dashboard digital com metricas",
            "pessoas trabalhando em laptops com telas coloridas",
        ],
        "moods": ["profissional", "moderno", "dinamico", "tecnologico"],
        "color_palettes": ["corporate_blue", "dark_premium", "ocean_gradient"],
        "cinematic_elements": [
            "luz azul suave tipo neon", "efeito glassmorphism",
            "gradientes sutis", "profundidade de campo",
        ],
        "audio_style": "voz masculina ou feminina, tom profissional e caloroso, ritmo moderado",
        "audio_background": "musica eletronica suave, intensidade crescente, sem vocals",
        "video_transitions": "fade suave, zoom lento, cross dissolve",
    },
    "empreendedorismo": {
        "visual_concepts": [
            "pessoa de terno ou casual elegante em escritorio moderno",
            "grafico de crescimento com flecha ascendente",
            "apertos de mao e networking profissional",
            "ceu aberto ou horizonte simbolizando possibilidades",
        ],
        "moods": ["inspirador", "profissional", "ambicioso", "confiante"],
        "color_palettes": ["warm_premium", "corporate_blue", "gold_accent"],
        "cinematic_elements": [
            "iluminacao natural estilo golden hour",
            "lente grande angular", "pouca profundidade de campo",
            "cor quente e convidativa",
        ],
        "audio_style": "voz grave e confiante, tom inspirador, pausas estrategicas",
        "audio_background": "musica orquestral suave, cordas, building up",
        "video_transitions": "wipe suave, fade to black, zoom out",
    },
    "financas": {
        "visual_concepts": [
            "graficos de acoes e candles",
            "moedas e notas em composicao artistica",
            "calculadora e documentos sobre mesa",
            "escudo ou cofre simbolizando seguranca",
        ],
        "moods": ["serio", "confiavel", "sofisticado", "preciso"],
        "color_palettes": ["dark_green", "corporate_blue", "gold_black"],
        "cinematic_elements": [
            "iluminacao dramatica low-key",
            "texturas de papel e metal",
            "sombras profundas", "contrato alto",
        ],
        "audio_style": "voz seria e confiavel, tom institucional, dicacao clara",
        "audio_background": "musica instrumental suave, piano, ambiente corporativo",
        "video_transitions": "cut seco, fade rapido, slide",
    },
    "inteligencia artificial": {
        "visual_concepts": [
            "rede neural ou conexoes luminosas",
            "rosto holografico ou figura digital",
            "circuitos e dados fluindo",
            "interface futurista com dados 3D",
        ],
        "moods": ["futurista", "inovador", "tecnologico", "preciso"],
        "color_palettes": ["dark_premium", "cyberpunk", "ocean_gradient"],
        "cinematic_elements": [
            "luz neon azul e roxa", "efeito glitch sutil",
            "particulas flutuantes", "reflexos metalicos",
        ],
        "audio_style": "voz robotica suave ou humana com eco sutil, tom de descoberta",
        "audio_background": "musica electronica ambiente, sintetizadores, pads",
        "video_transitions": "glitch sutil, fade com ruido digital, morph",
    },
    "marketing digital afiliados": {
        "visual_concepts": [
            "funil de vendas digital com moedas caindo",
            "pessoa em home office com multiplas telas",
            "dashboard de afiliados com comissoes",
            "conexoes entre criador de conteudo e audiencia",
        ],
        "moods": ["profissional", "acessivel", "dinamico", "otimista"],
        "color_palettes": ["corporate_blue", "warm_premium", "dark_premium"],
        "cinematic_elements": [
            "iluminacao de escritorio moderno",
            "elementos flutuantes de dados",
            "graficos ascendentes",
            "atmosfera produtiva mas relaxada",
        ],
        "audio_style": "voz feminina ou masculina calorosa, tom de mentor, didatica",
        "audio_background": "musica lo-fi suave, instrumental, ritmo medio",
        "video_transitions": "fade suave, slide lateral, zoom in informativo",
    },
    "saude e bem-estar": {
        "visual_concepts": [
            "pessoa meditando em ambiente natural e sereno",
            "alimentos saudaveis em composicao colorida",
            "corpo humano em equilibrio com elementos da natureza",
            "spa ou ambiente de relaxamento com luz natural",
        ],
        "moods": ["calmo", "natural", "equilibrado", "vital"],
        "color_palettes": ["green_nature", "warm_earthy", "pastel_soft"],
        "cinematic_elements": [
            "luz natural suave estilo golden hour",
            "cores verdes e terrosas", "profundidade de campo suave",
            "elementos organicos e texturas naturais",
        ],
        "audio_style": "voz feminina suave e acolhedora, tom calmante, ritmo lento e pausado",
        "audio_background": "natureza ambiente, agua corrente, passaros, musica instrumental relaxante",
        "video_transitions": "fade suave, dissolve lento, crossfade natural",
    },
    "desenvolvimento pessoal": {
        "visual_concepts": [
            "pessoa caminhando em direcao ao horizonte ou luz",
            "livros abertos e conhecimento fluindo",
            "escada ou degraus subindo em direcao ao ceu",
            "mente humana com ideias borbulhando",
        ],
        "moods": ["inspirador", "reflexivo", "transformador", "esperancoso"],
        "color_palettes": ["warm_premium", "gold_accent", "ocean_gradient"],
        "cinematic_elements": [
            "luz frontal suave estilo amanhecer",
            "composicao com linhas guia ascendentes",
            "cores quentes e acolhedoras",
            "simbolos de transformacao como borboleta ou luz",
        ],
        "audio_style": "voz calma e reflexiva, tom de mentor, pausas para reflexao",
        "audio_background": "musica instrumental emotiva, piano suave, cordas leves",
        "video_transitions": "fade to white, dissolve suave, zoom lento",
    },
    "moda e beleza": {
        "visual_concepts": [
            "pessoa elegante em composicao fashion com cores vibrantes",
            "produtos de beleza em arranjo artistico minimalista",
            "texturas de tecidos e maquiagem em macro detalhe",
            "passarela ou estudio fotografico com luz dramatica",
        ],
        "moods": ["elegante", "sofisticado", "moderno", "ousado"],
        "color_palettes": ["dark_premium", "rose_gold", "monochrome_chic"],
        "cinematic_elements": [
            "luz dramatica high-key e low-key",
            "cores vibrantes ou preto e branco",
            "texturas luxuosas", "composicao minimalista",
            "reflexos e brilhos sutis",
        ],
        "audio_style": "voz feminina estilosa e confiante, tom trendy, ritmo moderno",
        "audio_background": "musica fashion upbeat, pop instrumental, batida moderna",
        "video_transitions": "cut rapido, slide estiloso, fade com brilho",
    },
    "viagens e turismo": {
        "visual_concepts": [
            "destinos paradisiacos com praia e natureza exuberante",
            "pessoa explorando cidade historica ou cultura local",
            "mapas e rotas com elementos de aventura",
            "malas e passaporte com destino ao fundo",
        ],
        "moods": ["aventureiro", "alegre", "livre", "exotico"],
        "color_palettes": ["warm_sunset", "ocean_vibrant", "tropical_bright"],
        "cinematic_elements": [
            "luz natural abundante",
            "cores quentes e saturadas",
            "grande angular para paisagens",
            "movimento e dinamismo",
        ],
        "audio_style": "voz animada e energetica, tom de descoberta, ritmo acelerado",
        "audio_background": "musica animada mundial, percussao, instrumentos locais",
        "video_transitions": "wipe criativo, slide, fade com transicao geografica",
    },
}


_NICHE_FALLBACK: dict[str, Any] = {
    "visual_concepts": [
        "pessoa focada em laptop com dados e graficos",
        "ambiente profissional moderno e iluminado",
        "elementos de tecnologia e inovacao",
        "crescimento e desenvolvimento pessoal",
    ],
    "moods": ["profissional", "moderno", "inspirador"],
    "color_palettes": ["corporate_blue", "dark_premium"],
    "cinematic_elements": [
        "iluminacao profissional studio",
        "composicao limpa e objetiva",
        "cores balanceadas",
    ],
    "audio_style": "voz profissional, tom claro e direto, ritmo moderado",
    "audio_background": "musica instrumental suave, ambiente profissional",
    "video_transitions": "fade suave, cross dissolve",
}


# ═══════════════════════════════════════════════════════════════════
# PHASE 2 — FORMAT ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════

_IMAGE_FORMATS: dict[str, dict[str, Any]] = {
    "blog_featured": {
        "resolution": (1200, 630),
        "aspect_ratio": "1.91:1",
        "style": "cinematografico profissional com composicao rica",
        "focus": "conceito abstrato do tema com elementos visuais chave",
        "composition": "regra dos tercos, ponto focal no centro, espaco para texto",
        "lighting": "iluminacao dramatica suave com destaque no elemento principal",
    },
    "youtube_thumbnail": {
        "resolution": (1280, 720),
        "aspect_ratio": "16:9",
        "style": "alto contraste, cores vibrantes, expressivo",
        "focus": "rosto ou elemento de destaque com contraste maximo",
        "composition": "close-up ou plano medio, texto grande visivel em miniatura",
        "lighting": "iluminacao frontal com destaque, sombras dramaticas",
    },
    "pinterest_pin": {
        "resolution": (1000, 1500),
        "aspect_ratio": "2:3",
        "style": "limpo, vertical, tipografia destacada",
        "focus": "conceito principal com sobreposicao de texto elegante",
        "composition": "centro vertical com gradiente para texto na parte inferior",
        "lighting": "iluminacao suave e uniforme, cores pastel ou vibrantes",
    },
    "instagram_post": {
        "resolution": (1080, 1080),
        "aspect_ratio": "1:1",
        "style": "moderno, feed-coeso, alto engajamento visual",
        "focus": "elemento central forte com composicao equilibrada",
        "composition": "centro-simetrico ou regra dos tercos",
        "lighting": "iluminacao de estúdio suave",
    },
    "social_card": {
        "resolution": (1200, 630),
        "aspect_ratio": "1.91:1",
        "style": "limpo, corporativo, compartilhavel",
        "focus": "titulo ou conceito principal com apoio visual",
        "composition": "gradiente como base, texto centralizado",
        "lighting": "iluminacao plana e uniforme",
    },
}

_VIDEO_FORMATS: dict[str, dict[str, Any]] = {
    "slideshow": {
        "style": "cinematografico com efeito Ken Burns",
        "default_duration": 30,
        "transitions": "cross dissolve, zoom lento, fade",
        "music_style": "instrumental, intensidade crescente",
    },
    "short": {
        "style": "dinamico, ritmo rapido, cortes precisos",
        "default_duration": 15,
        "transitions": "cut rapido, slide, zoom",
    },
    "tutorial": {
        "style": "didatico, passo-a-passo, elementos graficos",
        "default_duration": 60,
        "transitions": "fade suave, morph entre passos",
    },
}

_AUDIO_FORMATS: dict[str, dict[str, Any]] = {
    "voiceover": {
        "style": "voz profissional com entonacao natural",
        "default_duration": 30,
        "background": "musica instrumental suave em fade",
        "format": "MP3 192kbps",
    },
    "podcast": {
        "style": "conversacional, tom caloroso",
        "default_duration": 300,
        "background": "introducao musical com fade in/out",
        "format": "MP3 256kbps",
    },
}


# ═══════════════════════════════════════════════════════════════════
# PHASE 3-5 — CTO MEDIA PROMPT ARCHITECT
# ═══════════════════════════════════════════════════════════════════

class MediaPromptArchitect:
    """CTO-graded media prompt architect.

    Aplica o meta-prompt do CTO Executive Director para construir
    prompts de midia com qualidade cinematografica.

    Uso:
        architect = MediaPromptArchitect()
        
        # Image prompt
        prompt = architect.build_image_prompt(
            niche="marketing digital",
            format_type="blog_featured",
            keyword="funil de vendas automatizado",
        )
        
        # Video prompt
        prompt = architect.build_video_prompt(
            niche="empreendedorismo",
            format_type="slideshow",
            script_segments=["Introducao", "Desenvolvimento", "Conclusao"],
        )
        
        # Audio prompt  
        prompt = architect.build_audio_prompt(
            niche="financas",
            format_type="voiceover",
            script_text="O guia completo para sua independencia financeira...",
        )
    """

    def __init__(self):
        self._history: list[dict] = []

    # ── prompt builders publicos ──

    def build_image_prompt(
        self,
        niche: str,
        format_type: str = "blog_featured",
        keyword: str = "",
        mood: str | None = None,
        custom_elements: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build CTO-graded image generation prompt.

        Aplica PHASE 0-5 para construir um prompt de imagem
        cinematográfica com validação epistêmica.
        """
        brief = self._validate_brief(niche, "image", format_type)
        concepts = self._get_niche_concepts(niche)
        fmt = _IMAGE_FORMATS.get(format_type, _IMAGE_FORMATS["blog_featured"])
        elements = custom_elements or concepts["visual_concepts"][:3]
        chosen_mood = mood or concepts["moods"][0]

        prompt = self._build_cinematic_prompt(
            brief=brief,
            fmt=fmt,
            concepts=concepts,
            elements=elements,
            mood=chosen_mood,
            keyword=keyword,
            media_class="image",
        )

        return self._finalize("image", prompt, format_type, keyword)

    def build_video_prompt(
        self,
        niche: str,
        format_type: str = "slideshow",
        script_segments: list[str] | None = None,
        mood: str | None = None,
    ) -> dict[str, Any]:
        """Build CTO-graded video generation prompt."""
        brief = self._validate_brief(niche, "video", format_type)
        concepts = self._get_niche_concepts(niche)
        fmt = _VIDEO_FORMATS.get(format_type, _VIDEO_FORMATS["slideshow"])
        chosen_mood = mood or concepts["moods"][0]
        segments = script_segments or ["Introducao", "Conteudo principal", "Conclusao com CTA"]

        prompt = self._build_cinematic_prompt(
            brief=brief, fmt=fmt, concepts=concepts,
            elements=concepts["visual_concepts"][:2],
            mood=chosen_mood, keyword="",
            media_class="video",
            extra={
                "segments": segments,
                "transitions": concepts["video_transitions"],
                "duration": fmt["default_duration"],
            },
        )

        return self._finalize("video", prompt, format_type, niche)

    def build_audio_prompt(
        self,
        niche: str,
        format_type: str = "voiceover",
        script_text: str = "",
        mood: str | None = None,
    ) -> dict[str, Any]:
        """Build CTO-graded audio/TTS generation prompt."""
        brief = self._validate_brief(niche, "audio", format_type)
        concepts = self._get_niche_concepts(niche)
        fmt = _AUDIO_FORMATS.get(format_type, _AUDIO_FORMATS["voiceover"])
        chosen_mood = mood or concepts["moods"][0]

        prompt = self._build_audio_prompt_internal(
            brief=brief, fmt=fmt, concepts=concepts,
            mood=chosen_mood, script_text=script_text,
        )

        return self._finalize("audio", prompt, format_type, niche)

    def generate_all(
        self,
        niche: str,
        keyword: str = "",
        script_text: str = "",
    ) -> dict[str, dict[str, Any]]:
        """Generate prompts for all media types at once (image + video + audio)."""
        return {
            "image": self.build_image_prompt(niche=niche, keyword=keyword),
            "video": self.build_video_prompt(niche=niche),
            "audio": self.build_audio_prompt(niche=niche, script_text=script_text),
        }

    # ── metodos internos (CTO workflow) ──

    def _validate_brief(self, niche: str, media_type: str, fmt: str) -> MediaBrief:
        """PHASE 0 — Validacao de input executivo."""
        return MediaBrief(
            niche=niche,
            media_type=media_type,
            format_type=fmt,
        )

    def _get_niche_concepts(self, niche: str) -> dict[str, Any]:
        """PHASE 0.5-2 — Busca conceitos de dominio do nicho."""
        # Exact or partial match
        for key, concepts in _NICHE_VISUAL_CONCEPTS.items():
            if key in niche.lower() or niche.lower() in key:
                return concepts
        return _NICHE_FALLBACK.copy()

    def _build_cinematic_prompt(
        self,
        brief: MediaBrief,
        fmt: dict[str, Any],
        concepts: dict[str, Any],
        elements: list[str],
        mood: str,
        keyword: str,
        media_class: str,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """PHASE 3 — Architectural design do prompt cinematico."""
        extra = extra or {}
        kw = keyword or brief.niche
        cinematic_elements = concepts.get("cinematic_elements", [])
        palette = concepts.get("color_palettes", ["corporate_blue"])[0]

        prompt_lines = [f"PROMPT CINEMATICO CTO — {brief.niche.upper()}", ""]

        # Epistemic context
        prompt_lines.append(f"// DOMINIO: {brief.niche}")
        prompt_lines.append(f"// CLASSIFICACAO: {media_class}")
        prompt_lines.append(f"// FORMATO: {fmt.get('aspect_ratio', brief.media_type)}")
        prompt_lines.append(f"// RESOLUCAO: {fmt.get('resolution', brief.resolution)}")
        prompt_lines.append(f"// MOOD: {mood}")
        prompt_lines.append(f"// PALETA: {palette}")
        prompt_lines.append("")

        # Core visual/auditive description
        prompt_lines.append("--- CONCEITO CENTRAL ---")
        prompt_lines.append(f"Tema: {kw}")
        prompt_lines.append(f"Elementos principais: {', '.join(elements)}")
        prompt_lines.append(f"Estilo: {fmt.get('style', 'cinematografico profissional')}")
        prompt_lines.append(f"Iluminacao: {fmt.get('lighting', 'profissional suave')}")
        prompt_lines.append(f"Composicao: {fmt.get('composition', 'regra dos tercos')}")
        prompt_lines.append("")

        # Cinematic elements
        prompt_lines.append("--- ELEMENTOS CINEMATICOS ---")
        for ce in cinematic_elements:
            prompt_lines.append(f"- {ce}")
        prompt_lines.append("")

        # Extra elements for video
        if extra.get("segments"):
            prompt_lines.append("--- SEQUENCIA DE CENAS ---")
            for i, seg in enumerate(extra["segments"], 1):
                prompt_lines.append(f"  Cena {i}: {seg}")
            prompt_lines.append(f"Transicoes: {extra.get('transitions', 'fade suave')}")
            prompt_lines.append(f"Duracao: {extra.get('duration', 30)}s")
            prompt_lines.append("")

        # Focus
        prompt_lines.append(f"--- DIRECAO DE {media_class.upper()} ---")
        prompt_lines.append(f"Foco principal: {fmt.get('focus', 'conceito central')}")
        prompt_lines.append("Alta qualidade, cinematografico, profissional.")
        prompt_lines.append("Sem textos na imagem. Sem marcas d'agua.")
        prompt_lines.append("Proporcao e resolucao adequadas para o formato.")

        return "\n".join(prompt_lines)

    def _build_audio_prompt_internal(
        self,
        brief: MediaBrief,
        fmt: dict[str, Any],
        concepts: dict[str, Any],
        mood: str,
        script_text: str,
    ) -> str:
        """PHASE 3 — Audio/TTS prompt construction."""
        prompt_lines = [f"PROMPT DE AUDIO CTO — {brief.niche.upper()}", ""]
        prompt_lines.append(f"// DOMINIO: {brief.niche}")
        prompt_lines.append(f"// FORMATO: {fmt.get('style', 'voiceover')}")
        prompt_lines.append(f"// MOOD: {mood}")
        prompt_lines.append("")

        prompt_lines.append("--- DIRECAO VOCAL ---")
        prompt_lines.append(f"Estilo de voz: {concepts.get('audio_style', 'profissional')}")
        prompt_lines.append(f"Background: {concepts.get('audio_background', 'instrumental suave')}")
        prompt_lines.append("Idioma: pt-BR")
        prompt_lines.append("")

        if script_text:
            prompt_lines.append("--- ROTEIRO ---")
            prompt_lines.append(script_text)
            prompt_lines.append("")

        prompt_lines.append("--- ESPECIFICACOES TECNICAS ---")
        prompt_lines.append(f"Formato: {fmt.get('format', 'MP3')}")
        prompt_lines.append(f"Duracao: {fmt.get('default_duration', 30)}s")
        prompt_lines.append(f"Fade in/out: 2s cada")
        prompt_lines.append(f"Volume background: -15dB relativo a voz")
        prompt_lines.append("Qualidade: alta, sem ruido, compressao minima")

        return "\n".join(prompt_lines)

    def _finalize(
        self, media_type: str, prompt: str, fmt: str, context: str
    ) -> dict[str, Any]:
        """PHASE 8 — CTO Snapshot: prompt finalizado com metadados."""
        record = {
            "media_type": media_type,
            "format": fmt,
            "context": context,
            "prompt": prompt,
            "char_count": len(prompt),
            "word_count": len(prompt.split()),
            "epistemic_quality": self._estimate_quality(prompt),
            "timestamp": time.time(),
        }
        self._history.append(record)
        return record

    def _estimate_quality(self, prompt: str) -> float:
        """Estimate CTO prompt quality based on structure markers."""
        score = 85.0
        if "CONCEITO CENTRAL" in prompt:
            score += 3
        if "ELEMENTOS CINEMATICOS" in prompt:
            score += 3
        if "DIRECAO" in prompt:
            score += 2
        if "DOMINIO" in prompt:
            score += 2
        if "CLASSIFICACAO" in prompt:
            score += 2
        if "FORMATO" in prompt:
            score += 1
        if "RESOLUCAO" in prompt or "Duracao" in prompt:
            score += 1
        if "MOOD" in prompt:
            score += 1
        return min(100, score)

    def history(self, n: int = 5) -> list[dict]:
        return self._history[-n:]


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION: ImageAgent + VideoAgent + AudioAgent enhancers
# ═══════════════════════════════════════════════════════════════════

class CTOMediaPromptIntegrator:
    """Integrates CTO prompts into existing media agents.

    Fornece metodos para enriquecer os prompts dos agents
    cinematic_image_agent, cinematic_video_agent, audio_production_agent.
    """

    def __init__(self):
        self.architect = MediaPromptArchitect()

    def enrich_image_generation(
        self,
        niche: str,
        keyword: str = "",
        format_type: str = "blog_featured",
    ) -> dict[str, Any]:
        """Generate enriched prompt for image generation."""
        return self.architect.build_image_prompt(
            niche=niche, format_type=format_type, keyword=keyword,
        )

    def enrich_video_generation(
        self,
        niche: str,
        script_segments: list[str] | None = None,
        format_type: str = "slideshow",
    ) -> dict[str, Any]:
        """Generate enriched prompt for video generation."""
        return self.architect.build_video_prompt(
            niche=niche, format_type=format_type,
            script_segments=script_segments,
        )

    def enrich_audio_generation(
        self,
        niche: str,
        script_text: str = "",
        format_type: str = "voiceover",
    ) -> dict[str, Any]:
        """Generate enriched prompt for audio generation."""
        return self.architect.build_audio_prompt(
            niche=niche, format_type=format_type, script_text=script_text,
        )

    def get_niche_visual_guide(self, niche: str) -> dict[str, Any]:
        """Get the full visual/auditive guide for a niche."""
        return _NICHE_VISUAL_CONCEPTS.get(
            next((k for k in _NICHE_VISUAL_CONCEPTS if k in niche.lower()), ""),
            _NICHE_FALLBACK,
        )
