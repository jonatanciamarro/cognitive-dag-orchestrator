"""Agente de Marketing no Instagram — gera posts, stories, reels e estratégia de tráfego orgânico."""

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


_POST_TEMPLATES: dict[str, dict[str, Any]] = {
    "carrossel": {
        "title_template": "{keyword} — Guia Completo [{year}]",
        "caption_template": (
            "📌 Salve este post para consultar depois!\n\n"
            "{keyword} explicado em {number} slides. Perfeito para quem está começando em {niche}.\n\n"
            "🔹 O que você vai aprender:\n"
            "{bullet_points}\n\n"
            "Já salvou? Então compartilha com alguém que precisa saber disso!\n\n"
            "{hashtags}"
        ),
        "slides": [
            "Slide 1: Capa atrativa com o tema",
            "Slide 2: O que é {keyword}?",
            "Slide 3: Por que é importante para {niche}",
            "Slide 4: Passo a passo para começar",
            "Slide 5: Dicas e melhores práticas",
            "Slide 6: Ferramentas recomendadas (link na bio)",
            "Slide 7: Conclusão e CTA",
            "Slide 8: Resumo e call to action",
        ],
    },
    "reel_script": {
        "title_template": "{keyword} em 30 Segundos",
        "caption_template": (
            "🎬 {keyword} — o resumo em 30 segundos!\n\n"
            "Se você quer {objective}, esse vídeo é para você.\n\n"
            "Gostou? Segue para mais conteúdo sobre {niche}! 🚀\n\n"
            "{hashtags}"
        ),
        "script": (
            "[Cena 1: You talking to camera]\n"
            '"Você sabia que {keyword} pode mudar seus resultados em {niche}?"\n\n'
            "[Cena 2: Text overlay showing key stat]\n"
            '"A verdade é que muitas pessoas ignoram isso, mas é essencial."\n\n'
            "[Cena 3: Quick cuts showing the process]\n"
            '"O segredo está em {tip}. Simples, mas poderoso."\n\n'
            "[Cena 4: You talking, text: 'Salva pra ver depois']\n"
            '"Salva esse vídeo para não esquecer e compartilha com quem precisa!"\n\n'
            "[Cena 5: Link in bio call]\n"
            '"E claro, link na bio com as ferramentas que recomendo!"'
        ),
    },
    "story_series": {
        "title_template": "Série: {keyword}",
        "caption_template": (
            "📚 Série completa sobre {keyword}\n\n"
            "São {number} posts explicando tudo que você precisa saber sobre {keyword} em {niche}.\n\n"
            "Parte {part}: {part_title}\n\n"
            "Ative as notificações para não perder nenhum post da série!\n\n"
            "{hashtags}"
        ),
    },
}


class InstagramMarketingAgent(AgentBase):
    """Gera posts, carrosséis, reels scripts e estratégia para Instagram."""

    def __init__(self, **kwargs) -> None:
        super().__init__("instagram_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        objective = str(campaign.get("objective", "gerar receita"))
        tip = "consistência e conteúdo de valor"

        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])

        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_out.get("available_offers", [])

        if not opportunities:
            opportunities = [
                {
                    "keyword": str(campaign.get("objective", "marketing digital")),
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]

        posts = []
        for i, opp in enumerate(opportunities[:4]):
            keyword = opp.get("keyword", str(campaign.get("objective", "")))
            intent = opp.get("intent", "informational")

            if intent == "commercial" and available_offers:
                post_type = "carrossel"
            elif i == 0:
                post_type = "reel_script"
            else:
                post_type = "story_series"

            template = _POST_TEMPLATES[post_type]
            year = "2026"
            number = str(7 + (i % 5))

            bullet_points = "\n".join(
                f"✅ {item}"
                for item in [
                    "O que é e como funciona",
                    "Por que é importante",
                    "Como aplicar no seu dia a dia",
                    "Ferramentas que recomendo",
                    "Erros comuns para evitar",
                ]
            )

            vars_map = {
                "keyword": keyword,
                "niche": niche,
                "objective": objective,
                "year": year,
                "number": number,
                "part": "1",
                "part_title": "Introdução",
                "bullet_points": bullet_points,
                "tip": tip,
            }

            title = template["title_template"]
            for k, v in vars_map.items():
                title = title.replace(f"{{{k}}}", str(v))

            caption = template["caption_template"]
            for k, v in vars_map.items():
                caption = caption.replace(f"{{{k}}}", str(v))

            hashtags = self._generate_hashtags(keyword, niche)

            post = {
                "title": title,
                "caption": caption,
                "post_type": post_type,
                "hashtags": hashtags[:15],
                "keyword": keyword,
                "best_time_to_post": "18:00-21:00 (horário de pico no Brasil)",
                "strategy_note": "Posts educativos geram mais salvamentos, que alimentam o algoritmo.",
            }

            if post_type == "carrossel":
                slides = [
                    s.replace(f"{{{k}}}", str(v))
                    for s in template.get("slides", [])
                    for k, v in vars_map.items()
                ]
                post["slides"] = slides
                product = available_offers[0] if available_offers else None
                if product:
                    post["cta"] = (
                        f"Link na bio para: {product.get('product_name', 'ferramenta recomendada')}"
                    )

            if post_type == "reel_script":
                script = template.get("script", "")
                for k, v in vars_map.items():
                    script = script.replace(f"{{{k}}}", str(v))
                post["script"] = script
                post["duration_seconds"] = 30
                post["audio_suggestion"] = "Música trending + voz over"

            posts.append(post)

        output = {
            "posts": posts,
            "total_posts": len(posts),
            "niche": niche,
            "recommendation": (
                f"Criar {len(posts)} posts para Instagram. "
                f"3 posts por semana (1 carrossel, 1 reel, 1 post educativo). "
                f"Link na bio para lead capture ou afiliado. "
                f"Instagram é excelente para construir autoridade e capturar leads."
            ),
        }

        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="instagram_marketing",
                input_state={"opportunities": len(opportunities), "niche": niche},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"posts": len(posts)},
            )

        if self.semantic_memory:
            for post in posts:
                post_cid = self.semantic_memory.register_concept(
                    f"ig_{post['keyword'][:15]}",
                    "content",
                    post["title"][:100],
                )
                niche_c = self.semantic_memory.find_concept(niche, "niche")
                if niche_c:
                    self.semantic_memory.assert_claim(
                        subject=niche_c["concept_id"],
                        predicate="has_instagram_post",
                        object=post_cid,
                        confidence=0.7,
                        evidence_type="DIRECT_OBSERVATION",
                        epistemic_status="INFERRED",
                        supporting_data={"type": post["post_type"]},
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="instagram_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Gerou {len(posts)} posts para Instagram no nicho '{niche}'"],
            metadata={"posts": len(posts), "niche": niche},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _generate_hashtags(keyword: str, niche: str) -> list[str]:
        tags = set()
        words = keyword.lower().split() + niche.lower().split()
        for w in words:
            if len(w) > 2:
                tags.add(f"#{w.replace(' ', '')}")
        extra = {
            "marketing": ["#marketingdigital", "#afiliados", "#empreendedorismo"],
            "financas": ["#financaspessoais", "#rendaextra", "#educacaofinanceira"],
            "digital": ["#marketingdigital", "#cursogratuito", "#dicas"],
        }
        for key, ext in extra.items():
            if key in keyword.lower() or key in niche.lower():
                tags.update(ext)
        return list(tags)[:15]
