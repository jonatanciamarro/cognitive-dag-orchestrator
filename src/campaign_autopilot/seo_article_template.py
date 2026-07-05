"""SEO Article Template — Motor de scoring para artigos otimizados para múltiplos buscadores.

Cada artigo é modelado como um vetor de 20 sinais que Google, Bing e Yahoo avaliam.
O template valida e pontua cada seção do artigo antes da publicação.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


# ── Schema de Pontuação ─────────────────────────────────────────

SCORE_WEIGHTS = {
    "title": 10,
    "meta_description": 8,
    "introduction": 10,
    "headings": 10,
    "content_depth": 15,
    "readability": 8,
    "multimedia": 8,
    "internal_links": 6,
    "external_links": 6,
    "schema_markup": 8,
    "freshness": 4,
    "keyword_usage": 7,
    "total": 100,
}

REQUIREMENTS = {
    "title": {
        "max_chars": 60,
        "keyword_in_first_60_chars": True,
        "no_clickbait": True,
        "has_emotional_or_numerical_hook": True,
    },
    "meta_description": {
        "min_chars": 120,
        "max_chars": 158,
        "keyword_natural": True,
    },
    "introduction": {
        "max_chars": 200,
        "keyword_in_first_100_chars": True,
        "answers_what_who_why": True,
    },
    "headings": {
        "min_h2": 4,
        "has_h3": True,
        "keyword_in_headings": True,
    },
    "content_depth": {
        "min_words": 500,
        "optimal_words": 1500,
        "covers_topic_completely": True,
    },
    "readability": {
        "max_paragraph_length": 300,  # characters
        "has_bullets_or_lists": True,
        "simple_language": True,
    },
    "multimedia": {
        "min_images": 1,
        "images_have_alt_text": True,
        "has_optimized_images": True,
    },
    "internal_links": {
        "min_links": 3,
        "links_relevant": True,
    },
    "external_links": {
        "min_links": 2,
        "links_to_authoritative_sources": True,
    },
    "schema_markup": {
        "has_article_schema": True,
        "has_faq_schema_if_applicable": True,
        "has_breadcrumb_schema": True,
    },
    "freshness": {
        "has_publish_date": True,
        "has_update_date": True,
        "date_is_visible": True,
    },
    "keyword_usage": {
        "keyword_in_title": True,
        "keyword_in_first_paragraph": True,
        "keyword_in_headings": True,
        "keyword_density_ideal": True,
        "lsis_present": True,
    },
}


@dataclass
class ArticleScore:
    """Pontuação de um artigo por seção."""

    title: float = 0.0
    meta_description: float = 0.0
    introduction: float = 0.0
    headings: float = 0.0
    content_depth: float = 0.0
    readability: float = 0.0
    multimedia: float = 0.0
    internal_links: float = 0.0
    external_links: float = 0.0
    schema_markup: float = 0.0
    freshness: float = 0.0
    keyword_usage: float = 0.0

    @property
    def total(self) -> float:
        return (
            (
                self.title * SCORE_WEIGHTS["title"]
                + self.meta_description * SCORE_WEIGHTS["meta_description"]
                + self.introduction * SCORE_WEIGHTS["introduction"]
                + self.headings * SCORE_WEIGHTS["headings"]
                + self.content_depth * SCORE_WEIGHTS["content_depth"]
                + self.readability * SCORE_WEIGHTS["readability"]
                + self.multimedia * SCORE_WEIGHTS["multimedia"]
                + self.internal_links * SCORE_WEIGHTS["internal_links"]
                + self.external_links * SCORE_WEIGHTS["external_links"]
                + self.schema_markup * SCORE_WEIGHTS["schema_markup"]
                + self.freshness * SCORE_WEIGHTS["freshness"]
                + self.keyword_usage * SCORE_WEIGHTS["keyword_usage"]
            )
            / 100
            * 100
        )

    @property
    def passed(self) -> bool:
        return self.total >= 70.0

    @property
    def grade(self) -> str:
        if self.total >= 90:
            return "A"
        elif self.total >= 80:
            return "B"
        elif self.total >= 70:
            return "C"
        elif self.total >= 60:
            return "D"
        else:
            return "F"

    def to_dict(self) -> dict[str, Any]:
        return {
            "scores": {
                "title": round(self.title, 2),
                "meta_description": round(self.meta_description, 2),
                "introduction": round(self.introduction, 2),
                "headings": round(self.headings, 2),
                "content_depth": round(self.content_depth, 2),
                "readability": round(self.readability, 2),
                "multimedia": round(self.multimedia, 2),
                "internal_links": round(self.internal_links, 2),
                "external_links": round(self.external_links, 2),
                "schema_markup": round(self.schema_markup, 2),
                "freshness": round(self.freshness, 2),
                "keyword_usage": round(self.keyword_usage, 2),
            },
            "total": round(self.total, 1),
            "grade": self.grade,
            "passed": self.passed,
        }


# ── Template de Artigo ──────────────────────────────────────────


@dataclass
class ArticleSection:
    heading: str
    content: str
    score: float = 0.0
    feedback: list[str] = field(default_factory=list)


@dataclass
class SEOArticle:
    """Artigo completo com metadados SEO."""

    # Metadados
    keyword: str
    intent: str  # informational, commercial, transactional, navigational
    niche: str
    word_count_target: int = 1500

    # Conteúdo
    title: str = ""
    meta_description: str = ""
    slug: str = ""
    introduction: str = ""
    sections: list[ArticleSection] = field(default_factory=list)
    conclusion: str = ""

    # Mídia
    image_prompt: str = ""
    image_alt_text: str = ""

    # Schema
    schema_type: str = "Article"

    # Autor
    author_name: str = ""
    author_bio: str = ""

    # Links
    internal_links: list[dict[str, str]] = field(default_factory=list)
    external_links: list[dict[str, str]] = field(default_factory=list)

    # FAQ
    faq_items: list[dict[str, str]] = field(default_factory=list)

    # Pontuação
    score: ArticleScore = field(default_factory=ArticleScore)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": {
                "keyword": self.keyword,
                "intent": self.intent,
                "niche": self.niche,
                "word_count_target": self.word_count_target,
            },
            "content": {
                "title": self.title,
                "meta_description": self.meta_description,
                "slug": self.slug,
                "introduction": self.introduction,
                "sections": [
                    {"heading": s.heading, "content": s.content[:100] + "..."}
                    for s in self.sections
                ],
                "conclusion": self.conclusion,
            },
            "multimedia": {
                "image_prompt": self.image_prompt,
                "image_alt_text": self.image_alt_text,
            },
            "schema": {
                "type": self.schema_type,
                "faq_count": len(self.faq_items),
            },
            "author": {
                "name": self.author_name,
                "bio": self.author_bio[:50] + "..." if self.author_bio else "",
            },
            "links": {
                "internal": len(self.internal_links),
                "external": len(self.external_links),
            },
            "score": self.score.to_dict(),
        }

    def to_markdown(self) -> str:
        """Gera o artigo completo em markdown para publicação."""
        lines = []
        lines.append(f"# {self.title}")
        lines.append("")
        lines.append(f"*{self.meta_description}*")
        lines.append("")
        lines.append(f"![{self.image_alt_text}]({self.slug}-hero.jpg)")
        lines.append("")
        lines.append(self.introduction)
        lines.append("")
        for section in self.sections:
            lines.append(f"## {section.heading}")
            lines.append("")
            lines.append(section.content)
            lines.append("")
        lines.append("## Conclusão")
        lines.append("")
        lines.append(self.conclusion)
        lines.append("")
        if self.faq_items:
            lines.append("## Perguntas Frequentes")
            lines.append("")
            for faq in self.faq_items:
                lines.append(f"### {faq['question']}")
                lines.append("")
                lines.append(faq["answer"])
                lines.append("")
        if self.internal_links:
            lines.append("## Leia também")
            lines.append("")
            for link in self.internal_links:
                lines.append(f"- [{link['title']}]({link['url']})")
            lines.append("")
        return "\n".join(lines)


# ── Motor de Scoring ────────────────────────────────────────────


class SEOArticleScorer:
    """Avalia um artigo contra os critérios dos buscadores."""

    def score(self, article: SEOArticle) -> ArticleScore:
        score = ArticleScore()

        # Title
        score.title = self._score_title(article.title, article.keyword)

        # Meta Description
        score.meta_description = self._score_meta_description(
            article.meta_description, article.keyword
        )

        # Introduction
        score.introduction = self._score_introduction(
            article.introduction, article.keyword
        )

        # Headings
        all_headings = [s.heading for s in article.sections]
        score.headings = self._score_headings(all_headings, article.keyword)

        # Content Depth
        full_text = (
            article.introduction
            + " "
            + " ".join(s.content for s in article.sections)
            + " "
            + article.conclusion
        )
        word_count = len(full_text.split())
        score.content_depth = self._score_content_depth(
            word_count, article.word_count_target
        )

        # Readability
        score.readability = self._score_readability(full_text)

        # Multimedia
        score.multimedia = self._score_multimedia(
            article.image_alt_text, bool(article.image_prompt)
        )

        # Internal Links
        score.internal_links = self._score_links(article.internal_links, min_req=3)

        # External Links
        score.external_links = self._score_links(article.external_links, min_req=2)

        # Schema
        score.schema_markup = self._score_schema(
            article.schema_type, len(article.faq_items)
        )

        # Freshness
        score.freshness = 1.0  # Always fresh, generated today

        # Keyword Usage
        score.keyword_usage = self._score_keyword_usage(
            article.title,
            article.introduction,
            all_headings,
            full_text,
            article.keyword,
        )

        return score

    def _score_title(self, title: str, keyword: str) -> float:
        if not title:
            return 0.0
        s = 0.0
        if len(title) <= 60:
            s += 0.3
        else:
            s += 0.1
        if keyword.lower() in title.lower():
            s += 0.4
        if any(c.isdigit() for c in title):
            s += 0.15
        if any(
            w in title.lower() for w in ["como", "melhor", "guia", "dicas", "passo"]
        ):
            s += 0.15
        return min(s, 1.0)

    def _score_meta_description(self, desc: str, keyword: str) -> float:
        if not desc:
            return 0.0
        s = 0.0
        length = len(desc)
        if 120 <= length <= 158:
            s += 0.5
        elif 100 <= length <= 180:
            s += 0.3
        else:
            s += 0.1
        if keyword.lower() in desc.lower():
            s += 0.5
        return min(s, 1.0)

    def _score_introduction(self, intro: str, keyword: str) -> float:
        if not intro:
            return 0.0
        s = 0.0
        if len(intro) <= 200:
            s += 0.2
        if keyword.lower() in intro[:100].lower():
            s += 0.4
        # Check if it answers what/who/why
        intro_lower = intro.lower()
        questions_answered = sum(
            1 for q in ["o que", "como", "por que", "qual", "quem"] if q in intro_lower
        )
        s += min(questions_answered * 0.1, 0.4)
        return min(s, 1.0)

    def _score_headings(self, headings: list[str], keyword: str) -> float:
        if not headings:
            return 0.0
        s = 0.0
        if len(headings) >= 4:
            s += 0.4
        elif len(headings) >= 2:
            s += 0.2
        keyword_in_headings = sum(1 for h in headings if keyword.lower() in h.lower())
        if keyword_in_headings >= 2:
            s += 0.3
        elif keyword_in_headings >= 1:
            s += 0.15
        # Has H3
        has_subheadings = any(len(h) > 40 for h in headings)  # rough proxy
        if has_subheadings:
            s += 0.3
        return min(s, 1.0)

    def _score_content_depth(self, word_count: int, target: int) -> float:
        if word_count >= 2000:
            return 1.0
        if word_count >= 1200:
            return 0.8
        if word_count >= 800:
            return 0.6
        if word_count >= 500:
            return 0.4
        if word_count >= 300:
            return 0.2
        return 0.1

    def _score_readability(self, text: str) -> float:
        if not text:
            return 0.0
        s = 0.5  # base
        paragraphs = text.split("\n\n")
        avg_para_len = sum(len(p) for p in paragraphs) / max(len(paragraphs), 1)
        if avg_para_len <= 150:
            s += 0.2
        if "•" in text or "- " in text:
            s += 0.15
        if any(c.isdigit() for c in text):
            s += 0.15
        return min(s, 1.0)

    def _score_multimedia(self, alt_text: str, has_image: bool) -> float:
        s = 0.0
        if has_image:
            s += 0.5
        if alt_text:
            s += 0.5
        return min(s, 1.0)

    def _score_links(self, links: list, min_req: int) -> float:
        if not links:
            return 0.0
        count = len(links)
        if count >= min_req + 2:
            return 1.0
        if count >= min_req:
            return 0.7
        if count >= 1:
            return 0.3
        return 0.0

    def _score_schema(self, schema_type: str, faq_count: int) -> float:
        s = 0.3
        if schema_type in ("Article", "NewsArticle"):
            s += 0.3
        if faq_count >= 3:
            s += 0.4
        elif faq_count >= 1:
            s += 0.2
        return min(s, 1.0)

    def _score_keyword_usage(
        self, title: str, intro: str, headings: list[str], text: str, keyword: str
    ) -> float:
        kw = keyword.lower()
        s = 0.0
        if kw in title.lower():
            s += 0.25
        if kw in intro.lower()[:100]:
            s += 0.25
        if any(kw in h.lower() for h in headings):
            s += 0.2

        # Keyword density (ideal: 0.5-2%)
        words = text.split()
        kw_count = text.lower().count(kw)
        density = kw_count / max(len(words), 1) * 100
        if 0.3 <= density <= 3.0:
            s += 0.15
        else:
            s += 0.05

        # LSI keywords presence
        lsi_keywords = self._extract_lsi(keyword)
        lsi_found = sum(1 for lsi in lsi_keywords if lsi.lower() in text.lower())
        s += min(lsi_found * 0.03, 0.15)

        return min(s, 1.0)

    @staticmethod
    def _extract_lsi(keyword: str) -> list[str]:
        """Extrai LSI keywords genéricas baseadas no termo principal."""
        # LSI simuladas — em produção, usar API de NLP
        base_lsi = {
            "como": ["guia", "passo a passo", "tutorial", "aprender", "fazer"],
            "melhor": ["review", "comparação", "top", "qual", "avaliação"],
            "o que": ["significado", "definição", "conceito", "entender"],
            "dicas": ["ideias", "sugestões", "estratégias", "técnicas"],
        }
        for trigger, words in base_lsi.items():
            if trigger in keyword.lower():
                return words
        return ["guia", "dicas", "como", "benefícios", "vantagens"]


# ── Prompt Builder ──────────────────────────────────────────────


class SEOArticlePromptBuilder:
    """Constrói prompts para o SEOContentWriterAgent."""

    @staticmethod
    def build_article_prompt(
        keyword: str,
        intent: str,
        niche: str,
        word_count: int,
        target_audience: str = "",
        competitors: list[str] | None = None,
    ) -> str:
        """Gera prompt completo para criar artigo SEO-otimizado."""
        intent_instructions = {
            "informational": (
                "Foco em educar o leitor. Explique conceitos, responda perguntas, "
                "forneça informações completas e precisas. Tom didático e acessível."
            ),
            "commercial": (
                "Foco em ajudar o leitor a tomar uma decisão de compra. "
                "Compare opções, destaque prós e contras, mencione preços. "
                "Tom analítico e objetivo."
            ),
            "transactional": (
                "Foco na ação de compra. Inclua links de afiliado naturalmente, "
                "destaque ofertas, descontos e benefícios. Tom persuasivo mas ético."
            ),
            "navigational": (
                "Foco em direcionar o leitor para recursos específicos. "
                "Seja direto e útil, evitando rodeios."
            ),
        }

        instruction = intent_instructions.get(
            intent, intent_instructions["informational"]
        )
        audience = target_audience or "iniciantes interessados no tema"
        comp_text = ""
        if competitors:
            comp_text = "Concorrentes a superar:\n" + "\n".join(
                f"- {c}" for c in competitors[:3]
            )

        return f"""Você é um redator SEO especializado em conteúdo para Google, Bing e Yahoo.

TÓPICO PRINCIPAL: {keyword}
INTENÇÃO DE BUSCA: {intent}
NICHO: {niche}
PÚBLICO-ALVO: {audience}
EXTENSÃO: {word_count} palavras

{instruction}

{comp_text}

REGRAS OBRIGATÓRIAS:
1. Responda COMPLETAMENTE à intenção de busca — o leitor não precisa ler outro artigo
2. Use a palavra-chave no título, na introdução e em pelo menos 2 headings
3. Estrutura com H2 e H3 hierárquicos
4. Parágrafos de no máximo 150 caracteres
5. Inclua lista com bullets ou numerada quando relevante
6. Tom: informativo, útil, sem sensacionalismo
7. Português brasileiro natural
8. Mínimo de 4 seções com H2
9. Ao final, inclua seção de Perguntas Frequentes (3-5 perguntas)
10. NÃO use linguagem promocional excessiva — seja útil primeiro

FORMATO DE SAÍDA (JSON):
{{
    "title": "Manchete SEO (máx 60 caracteres)",
    "meta_description": "Meta description (120-158 caracteres)",
    "slug": "url-amigavel-com-keyword",
    "introduction": "Introdução de até 200 caracteres respondendo O quê, Para quem, Por que ler",
    "sections": [
        {{"heading": "H2 - Primeira seção", "content": "Conteúdo completo da seção"}},
        {{"heading": "H2 - Segunda seção", "content": "..."}}
    ],
    "conclusion": "Conclusão com recapitulação e CTA sutil",
    "faq_items": [
        {{"question": "Pergunta frequente?", "answer": "Resposta direta e útil"}}
    ],
    "image_prompt": "Descrição para gerar imagem sobre o tema",
    "image_alt_text": "Texto alternativo SEO para a imagem",
    "author_notes": "Observações sobre diferenciação do conteúdo"
}}"""

    @staticmethod
    def build_fix_prompt(article_json: dict, score_report: dict) -> str:
        """Gera prompt para corrigir um artigo com base no score."""
        low_scores = [
            f"- {k}: {v['total']}/100"
            for k, v in score_report.get("scores", {}).items()
            if isinstance(v, dict) and v.get("total", 100) < 70
        ]

        return f"""REVISÃO SEO — O artigo abaixo precisa de melhorias.

PONTOS A MELHORAR:
{chr(10).join(low_scores) if low_scores else "Nenhum — apenas refinamento"}

ARTIGO ATUAL:
{json.dumps(article_json, ensure_ascii=False, indent=2)}

Gere uma versão melhorada, corrigindo todos os pontos acima.
Mantenha o mesmo formato JSON.
Mantenha o tom informativo e útil.
Não perca a essência do conteúdo original."""
