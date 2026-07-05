"""SEOContentWriterAgent — Escreve artigos otimizados para Google, Bing e Yahoo.

Usa os 13 provedores LLM gratuitos com failover automático.
Gera artigos com scoring SEO em 20 sinais.
"""

from __future__ import annotations

import json
import random
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger
from ...seo_article_template import (
    SEOArticle,
    ArticleSection,
    SEOArticleScorer,
    SEOArticlePromptBuilder,
)

log = StructuredLogger("seo_content_writer")

# Article templates for when LLM is unavailable
_ARTICLE_TEMPLATES: dict[str, dict[str, Any]] = {
    "guia_completo": {
        "sections": 6,
        "word_count": 2000,
        "has_faq": True,
        "has_comparison_table": True,
        "description": "Guia completo e aprofundado sobre o tópico",
    },
    "review": {
        "sections": 5,
        "word_count": 1500,
        "has_faq": True,
        "has_pros_cons": True,
        "description": "Análise detalhada com prós, contras e recomendação",
    },
    "artigo_informativo": {
        "sections": 4,
        "word_count": 1200,
        "has_faq": True,
        "has_examples": True,
        "description": "Artigo informativo com exemplos práticos",
    },
    "tutorial": {
        "sections": 5,
        "word_count": 1500,
        "has_faq": False,
        "has_step_by_step": True,
        "description": "Tutorial passo a passo com instruções claras",
    },
    "comparacao": {
        "sections": 6,
        "word_count": 2000,
        "has_faq": True,
        "has_comparison_table": True,
        "has_pros_cons": True,
        "description": "Comparação detalhada entre opções concorrentes",
    },
}


class SEOContentWriterAgent(AgentBase):
    """Escreve artigos SEO-otimizados usando LLMs gratuitos com failover."""

    def __init__(self, **kwargs) -> None:
        super().__init__("seo_content_writer", **kwargs)
        self.scorer = SEOArticleScorer()

    def _generate_article_via_llm(
        self, keyword: str, intent: str, niche: str, word_count: int, content_type: str
    ) -> dict[str, Any] | None:
        """Tenta gerar artigo via LLM. Retorna None se falhar."""
        try:
            from ...free_llm_providers import generate_text

            prompt = SEOArticlePromptBuilder.build_article_prompt(
                keyword=keyword,
                intent=intent,
                niche=niche,
                word_count=word_count,
            )

            result = generate_text(prompt, max_tokens=max(word_count * 4, 3000))
            if not result:
                return None

            # Extract JSON from response
            return self._parse_json_response(result)
        except Exception as e:
            log.warning("llm_generation_failed", keyword=keyword, error=str(e)[:80])
            return None

    def _parse_json_response(self, text: str) -> dict[str, Any] | None:
        """Extrai JSON da resposta do LLM."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block
        import re

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Try markdown code block
        code_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if code_match:
            try:
                return json.loads(code_match.group(1))
            except json.JSONDecodeError:
                pass

        return None

    def _generate_article_stdlib(
        self, keyword: str, intent: str, niche: str, content_type: str
    ) -> dict[str, Any]:
        """Gera artigo usando template interno (stdlib fallback)."""
        template = _ARTICLE_TEMPLATES.get(
            content_type, _ARTICLE_TEMPLATES["artigo_informativo"]
        )
        num_sections = template["sections"]

        section_templates = {
            "o que é": f"O que é {keyword}?",
            "como funciona": f"Como funciona {keyword}?",
            "beneficios": f"Principais benefícios de {keyword}",
            "dicas": f"Dicas práticas para aplicar {keyword}",
            "comparacao": f"{keyword} vs Alternativas",
            "cuidados": f"Cuidados ao escolher {keyword}",
            "perguntas": "Perguntas Frequentes",
        }

        section_headings = list(section_templates.values())
        random.shuffle(section_headings)
        selected = section_headings[:num_sections]

        sections = []
        for i, heading in enumerate(selected):
            sections.append(
                ArticleSection(
                    heading=heading,
                    content=self._generate_section_text(
                        keyword, heading, niche, intent
                    ),
                    score=0.7,
                )
            )

        # Build FAQ
        faq_items = []
        if template.get("has_faq"):
            faq_items = [
                {
                    "question": f"O que é {keyword}?",
                    "answer": f"{keyword} é uma ferramenta/técnica que ajuda pessoas a alcançarem seus objetivos na área de {niche}.",
                },
                {
                    "question": f"Quanto custa {keyword}?",
                    "answer": f"Os preços de {keyword} variam bastante dependendo da qualidade e recursos. É importante pesquisar antes de comprar.",
                },
                {
                    "question": f"Vale a pena investir em {keyword}?",
                    "answer": f"Para a maioria das pessoas, sim. {keyword} oferece benefícios significativos que justificam o investimento.",
                },
                {
                    "question": f"Qual a melhor alternativa para {keyword}?",
                    "answer": "Existem várias alternativas no mercado. O ideal é comparar features e preços antes de decidir.",
                },
            ]

        return {
            "title": f"{keyword}: Guia Completo para {self._format_niche(niche)}",
            "meta_description": f"Descubra tudo sobre {keyword}. Guia completo com dicas, benefícios, comparações e perguntas frequentes. Atualizado 2026.",
            "slug": keyword.lower().replace(" ", "-")[:50],
            "introduction": f"Se você está buscando informações completas sobre {keyword}, chegou ao lugar certo. Neste guia, vamos explorar todos os aspectos importantes, desde conceitos básicos até dicas avançadas, para ajudar você a tomar a melhor decisão.",
            "sections": [
                {"heading": s.heading, "content": s.content} for s in sections
            ],
            "conclusion": f"Esperamos que este guia sobre {keyword} tenha sido útil. O mais importante é avaliar suas necessidades específicas antes de tomar uma decisão. Continue acompanhando nosso site para mais conteúdos como este.",
            "faq_items": faq_items,
            "image_prompt": f"Professional illustration about {keyword} in {niche}, modern style, blue and white colors",
            "image_alt_text": f"Guia completo sobre {keyword} - tudo que você precisa saber",
        }

    def _generate_section_text(
        self, keyword: str, heading: str, niche: str, intent: str
    ) -> str:
        """Gera texto para uma seção usando templates."""
        templates = [
            f"Quando falamos sobre {keyword}, é importante entender primeiro os conceitos fundamentais. {keyword} tem se tornado cada vez mais relevante no mundo de {niche}, e saber como aproveitar seus benefícios pode fazer toda a diferença nos seus resultados.",
            f"Um dos aspectos mais importantes de {keyword} é sua aplicação prática no dia a dia. Muitas pessoas já estão utilizando {keyword} para melhorar seus resultados em {niche}, e os números comprovam sua eficácia.",
            f"Para aproveitar ao máximo {keyword}, é recomendável seguir algumas boas práticas. Especialistas da área recomendam começar com o básico e ir evoluindo gradualmente, sempre testando e ajustando conforme necessário.",
            f"Existem diversas opções disponíveis quando o assunto é {keyword}. Cada uma com suas vantagens e desvantagens, e a escolha ideal depende das suas necessidades específicas em {niche}.",
            f"Os resultados de quem utiliza {keyword} corretamente são impressionantes. Estudos mostram que pessoas que dominam {keyword} conseguem resultados até 3x melhores em {niche} comparado com quem não utiliza.",
            f"É importante ficar atento às tendências em {keyword}. O mercado de {niche} está em constante evolução, e novas ferramentas e técnicas surgem regularmente. Manter-se atualizado é essencial.",
        ]
        return random.choice(templates)

    def _format_niche(self, niche: str) -> str:
        """Formata o nicho para uso em títulos."""
        mapping = {
            "tecnologia": "Tecnologia",
            "financas": "Finanças Pessoais",
            "saude": "Saúde e Bem-estar",
            "carreira": "Carreira e Desenvolvimento",
        }
        return mapping.get(niche.lower(), niche.capitalize())

    def _generate_article(
        self, keyword: str, intent: str, niche: str, word_count: int, content_type: str
    ) -> SEOArticle:
        """Gera um artigo completo, tentando LLM primeiro, fallback para stdlib."""
        log.info("generating_article", keyword=keyword, type=content_type)

        # Try LLM first
        llm_result = self._generate_article_via_llm(
            keyword, intent, niche, word_count, content_type
        )

        if llm_result:
            # Build SEOArticle from LLM result
            article = SEOArticle(
                keyword=keyword,
                intent=intent,
                niche=niche,
                word_count_target=word_count,
                title=llm_result.get("title", f"Guia sobre {keyword}"),
                meta_description=llm_result.get(
                    "meta_description", f"Guia completo sobre {keyword}"
                ),
                slug=llm_result.get("slug", keyword.lower().replace(" ", "-")),
                introduction=llm_result.get(
                    "introduction", f"Guia completo sobre {keyword}"
                ),
                sections=[
                    ArticleSection(heading=s["heading"], content=s["content"])
                    for s in llm_result.get("sections", [])
                ],
                conclusion=llm_result.get("conclusion", f"Conclusão sobre {keyword}"),
                image_prompt=llm_result.get("image_prompt", f"Image about {keyword}"),
                image_alt_text=llm_result.get("image_alt_text", f"Image: {keyword}"),
                faq_items=llm_result.get("faq_items", []),
            )
        else:
            # Fallback to stdlib
            data = self._generate_article_stdlib(keyword, intent, niche, content_type)
            article = SEOArticle(
                keyword=keyword,
                intent=intent,
                niche=niche,
                word_count_target=word_count,
                title=data["title"],
                meta_description=data["meta_description"],
                slug=data["slug"],
                introduction=data["introduction"],
                sections=[
                    ArticleSection(heading=s["heading"], content=s["content"])
                    for s in data["sections"]
                ],
                conclusion=data["conclusion"],
                image_prompt=data["image_prompt"],
                image_alt_text=data["image_alt_text"],
                faq_items=data.get("faq_items", []),
            )
            log.info("used_stdlib_fallback", keyword=keyword)

        # Score the article
        article.score = self.scorer.score(article)

        return article

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        # Get parameters from campaign or use defaults
        opportunities = campaign.get("opportunities", campaign.get("keywords", []))
        if isinstance(opportunities, dict):
            opportunities = [opportunities]

        niche = str(campaign.get("niche", "tecnologia"))
        default_word_count = int(campaign.get("default_word_count", 1500))

        articles_generated = []
        total_score = 0.0

        for opp in opportunities:
            keyword = opp.get("keyword", opp.get("topic", "assunto"))
            intent = opp.get("intent", "informational")
            word_count = opp.get("target_word_count", default_word_count)
            content_type = opp.get("suggested_content_type", "artigo_informativo")

            article = self._generate_article(
                keyword, intent, niche, word_count, content_type
            )
            total_score += article.score.total

            articles_generated.append(article.to_dict())

        avg_score = total_score / max(len(articles_generated), 1)

        output = {
            "niche": niche,
            "articles_generated": len(articles_generated),
            "average_seo_score": round(avg_score, 1),
            "articles": articles_generated,
            "recommendations": self._generate_recommendations(articles_generated),
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="seo_content_writing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(articles_generated)} artigos SEO-otimizados. Score médio: {avg_score:.1f}/100"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _generate_recommendations(self, articles: list[dict]) -> list[str]:
        """Gera recomendações baseadas nos scores dos artigos."""
        recs = []
        low_score_articles = [
            a for a in articles if a.get("score", {}).get("total", 100) < 70
        ]
        if low_score_articles:
            recs.append(
                f"{len(low_score_articles)} artigo(s) precisam de revisão (score < 70)"
            )

        recs.append("Revisar schema markup para garantir Article + FAQ")
        recs.append("Verificar se todas as imagens têm alt text descritivo")
        recs.append("Submeter novos artigos ao Search Console imediatamente")

        return recs

    @staticmethod
    def _utcnow_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        from datetime import datetime

        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))
