"""Agente de Marketing no YouTube — gera scripts de vídeo, títulos SEO, descrições com links de afiliado e tags."""

from __future__ import annotations

from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


# Templates de roteiro de vídeo
_VIDEO_TEMPLATES: dict[str, dict[str, Any]] = {
    "tutorial": {
        "title_template": "Como {keyword} — Passo a Passo Completo para Iniciantes",
        "hook_template": (
            "Você sabia que {keyword} pode transformar seus resultados em {niche}? "
            "No vídeo de hoje, vou mostrar exatamente como você pode começar hoje mesmo."
        ),
        "outro_template": (
            "E aí, curtiu o passo a passo? Se inscreva no canal para mais conteúdos sobre {niche}, "
            "e não esqueça de conferir os links da descrição com ferramentas recomendadas. "
            "Até o próximo vídeo!"
        ),
        "sections": [
            {
                "time": "0:00",
                "title": "Introdução",
                "description": "Apresentar o tema e o que será ensinado.",
            },
            {
                "time": "1:00",
                "title": "O que você precisa saber",
                "description": "Pré-requisitos e conceitos básicos sobre {keyword}.",
            },
            {
                "time": "3:00",
                "title": "Passo a passo",
                "description": "Explicar detalhadamente como fazer {keyword}.",
            },
            {
                "time": "7:00",
                "title": "Dicas importantes",
                "description": "Erros comuns e como evitá-los ao fazer {keyword}.",
            },
            {
                "time": "9:00",
                "title": "Ferramentas recomendadas",
                "description": "Mostrar produtos/ferramentas que ajudam com {keyword}.",
            },
            {
                "time": "10:30",
                "title": "Conclusão",
                "description": "Resumo e call to action.",
            },
        ],
    },
    "review": {
        "title_template": "{product_name}: Vale a Pena? Review Completo",
        "hook_template": (
            "Hoje vou responder se {product_name} realmente funciona ou é só mais um produto que promete "
            "e não entrega. Fique até o final para minha opinião honesta."
        ),
        "outro_template": (
            "Espero que este review tenha ajudado você a decidir. Se gostou, dá aquele like "
            "e compartilhe com quem também está interessado em {product_name}. "
            "Links na descrição para mais informações."
        ),
        "sections": [
            {
                "time": "0:00",
                "title": "Introdução",
                "description": "Apresentar o produto e contexto.",
            },
            {
                "time": "1:30",
                "title": "O que é {product_name}?",
                "description": "Explicar o produto e para que serve.",
            },
            {
                "time": "3:00",
                "title": "Principais funcionalidades",
                "description": "Mostrar cada funcionalidade na prática.",
            },
            {
                "time": "5:00",
                "title": "Prós e Contras",
                "description": "Listar vantagens e desvantagens.",
            },
            {
                "time": "7:00",
                "title": "Preço e vale a pena?",
                "description": "Analisar custo-benefício.",
            },
            {
                "time": "8:30",
                "title": "Conclusão",
                "description": "Recomendação final e CTA.",
            },
        ],
    },
    "educational": {
        "title_template": "{keyword} em {year}: Tudo que Você Precisa Saber",
        "hook_template": (
            "O cenário de {niche} mudou muito em {year}, e {keyword} continua sendo um dos tópicos "
            "mais importantes para quem quer resultados. Vou te mostrar o que mudou e como se adaptar."
        ),
        "outro_template": (
            "Gostou do conteúdo? Inscreva-se e ative o sininho para não perder os próximos vídeos "
            "sobre {niche}. Deixe nos comentários qual tema você quer ver por aqui!"
        ),
        "sections": [
            {
                "time": "0:00",
                "title": "Introdução",
                "description": "Contexto do tema e o que será abordado.",
            },
            {
                "time": "1:30",
                "title": "O cenário atual de {keyword}",
                "description": "Dados e tendências sobre {keyword} em {year}.",
            },
            {
                "time": "4:00",
                "title": "Estratégias que funcionam",
                "description": "O que está funcionando agora para {keyword}.",
            },
            {
                "time": "7:00",
                "title": "Ferramentas essenciais",
                "description": "Ferramentas recomendadas para {keyword}.",
            },
            {
                "time": "9:00",
                "title": "Próximos passos",
                "description": "O que fazer depois de dominar {keyword}.",
            },
        ],
    },
}

_TAGS_BY_NICHE: dict[str, list[str]] = {
    "marketing digital": [
        "marketing digital",
        "marketing de afiliados",
        "ganhar dinheiro online",
        "trabalhar em casa",
        "renda extra",
        "marketing para iniciantes",
        "marketing digital para iniciantes",
    ],
    "financas": [
        "finanças pessoais",
        "investir dinheiro",
        "educação financeira",
        "como economizar dinheiro",
        "renda passiva",
        "independência financeira",
    ],
    "tecnologia": [
        "tecnologia",
        "apps úteis",
        "ferramentas digitais",
        "produtividade",
        "inteligência artificial",
        "software gratuito",
    ],
    "produtividade": [
        "produtividade",
        "gestão de tempo",
        "organização pessoal",
        "como ser mais produtivo",
        "metas e objetivos",
        "hábitos matinais",
    ],
    "default": [
        "tutorial",
        "guia completo",
        "passo a passo",
        "dicas úteis",
        "aprender online",
        "iniciantes",
    ],
}


def _generate_video_materials(
    keyword: str,
    niche: str,
    content_type: str,
    offers: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate complete video materials from templates."""
    year = "2026"
    product_name = offers[0].get("product_name", "") if offers else ""

    variables: dict[str, str] = {
        "keyword": keyword,
        "niche": niche,
        "product_name": product_name,
        "year": year,
    }

    # Choose template
    template = _VIDEO_TEMPLATES.get(
        content_type if content_type in _VIDEO_TEMPLATES else "educational"
    )

    # Build title
    title = template["title_template"]
    for key, val in variables.items():
        placeholder = "{" + key + "}"
        if placeholder in title:
            title = title.replace(placeholder, str(val))

    # Build description with affiliate links
    description = template["hook_template"]
    for key, val in variables.items():
        placeholder = "{" + key + "}"
        if placeholder in description:
            description = description.replace(placeholder, str(val))

    description += "\n\n📌 **LINKS E RECURSOS MENCIONADOS**\n\n"

    if offers:
        for i, offer in enumerate(offers[:3], 1):
            pname = offer.get("product_name", "Produto")
            purl = offer.get("product_url", "#")
            description += f"{i}. 🔗 **{pname}**: {purl}\n"

    description += "\n📌 **TIMESTAMPS**\n\n"
    for sec in template["sections"]:
        sec_title = sec["title"]
        for key, val in variables.items():
            placeholder = "{" + key + "}"
            if placeholder in sec_title:
                sec_title = sec_title.replace(placeholder, str(val))
        description += f"{sec['time']} — {sec_title}\n"

    description += "\n📌 **INSCREVA-SE**\n"
    description += (
        "Se este conteúdo foi útil, inscreva-se no canal e ative o sininho! 🔔\n"
    )

    description += "\n🔻 **DISCLOSURE** 🔻\n"
    description += (
        "Alguns links na descrição são de afiliados. Se você comprar através deles, "
    )
    description += "eu posso ganhar uma comissão sem custo adicional para você.\n"

    # Generate tags
    niche_tags = _TAGS_BY_NICHE.get(niche.lower(), _TAGS_BY_NICHE["default"])
    tags = [keyword] + niche_tags[:6]
    # Add product-specific tags
    if product_name:
        tags.append(product_name)
    tags = list(dict.fromkeys(tags))  # deduplicate preserving order

    # Generate script sections
    script_sections = []
    for sec in template["sections"]:
        sec_title = sec["title"]
        sec_desc = sec["description"]
        for key, val in variables.items():
            placeholder = "{" + key + "}"
            if placeholder in sec_title:
                sec_title = sec_title.replace(placeholder, str(val))
            if placeholder in sec_desc:
                sec_desc = sec_desc.replace(placeholder, str(val))
        script_sections.append(
            {
                "timestamp": sec["time"],
                "title": sec_title,
                "description": sec_desc,
            }
        )

    # Build outro
    outro = template["outro_template"]
    for key, val in variables.items():
        placeholder = "{" + key + "}"
        if placeholder in outro:
            outro = outro.replace(placeholder, str(val))

    total_duration_min = (
        int(
            sum(
                int(s["time"].split(":")[0]) * 60 + int(s["time"].split(":")[1])
                for s in template["sections"]
            )
            / 60
        )
        if template["sections"]
        else 10
    )

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "script_sections": script_sections,
        "hook": template["hook_template"],
        "outro": outro,
        "estimated_duration_minutes": total_duration_min,
        "content_type": content_type,
        "keyword": keyword,
    }


class YouTubeMarketingAgent(AgentBase):
    """Gera materiais completos para vídeos no YouTube: título, descrição, roteiro, tags."""

    def __init__(self, **kwargs) -> None:
        super().__init__("youtube_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get keywords from SEO research
        seo = context.step_results.get("seo_research", {})
        seo_output = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_output.get("top_opportunities", [])

        # Get offers
        offers_step = context.step_results.get("offer_lookup", {})
        offers_output = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_output.get("available_offers", [])

        # Fallback keywords if none from SEO
        if not opportunities:
            opportunities = [
                {
                    "keyword": str(campaign.get("objective", "marketing digital")),
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]

        # Determine video types based on search intent
        intent_to_video_type = {
            "informational": "educational",
            "commercial": "review",
            "transactional": "review",
            "navigational": "tutorial",
        }

        # Generate video materials for each keyword
        videos = []
        for opp in opportunities[:3]:  # Max 3 videos per cycle
            keyword = opp.get("keyword", opp.get("topic", ""))
            intent = opp.get("intent", "informational")
            video_type = intent_to_video_type.get(intent, "educational")

            # Match offers to keyword
            matched_offers = []
            for offer in available_offers:
                kw_lower = keyword.lower()
                if (
                    offer.get("category", "").lower() in kw_lower
                    or kw_lower in offer.get("category", "").lower()
                ):
                    matched_offers.append(offer)
            if not matched_offers and available_offers:
                matched_offers = [available_offers[0]]

            video = _generate_video_materials(
                keyword, niche, video_type, matched_offers
            )
            video["volume"] = opp.get("volume", 1000)
            video["difficulty"] = opp.get("difficulty", 0.5)
            videos.append(video)

        output = {
            "videos": videos,
            "total_videos": len(videos),
            "niche": niche,
            "generation_method": "template_based",
            "note": "Conteúdo gerado por template. Para produção real, configurar OPENAI_API_KEY para gerar roteiros com IA.",
            "recommendation": (
                f"Produzir {len(videos)} vídeos nos próximos dias. "
                f"Primeiro vídeo: '{videos[0]['title']}' (~{videos[0]['estimated_duration_minutes']}min). "
                f"Publicar no YouTube com links de afiliado na descrição."
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="youtube_marketing",
                input_state={"opportunities": len(opportunities), "niche": niche},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"videos": len(videos)},
            )

        # Semantic memory
        if self.semantic_memory:
            for video in videos:
                video_concept_id = self.semantic_memory.register_concept(
                    f"yt_{video['keyword'][:20]}",
                    "content",
                    video["title"][:100],
                )
                niche_concept = self.semantic_memory.find_concept(niche, "niche")
                if niche_concept:
                    self.semantic_memory.assert_claim(
                        subject=niche_concept["concept_id"],
                        predicate="has_video",
                        object=video_concept_id,
                        confidence=0.7,
                        evidence_type="DIRECT_OBSERVATION",
                        epistemic_status="INFERRED",
                        supporting_data={
                            "title": video["title"],
                            "duration": video["estimated_duration_minutes"],
                        },
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="youtube_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(videos)} materiais de vídeo para YouTube no nicho '{niche}'"
            ],
            metadata={"videos": len(videos), "niche": niche},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
