"""Agente de Repurposing de Conteúdo — pega artigos do blog e gera automaticamente versões para todos os outros canais."""

from __future__ import annotations


from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class ContentRepurposerAgent(AgentBase):
    """Multiplica conteúdo: 1 artigo do blog → YouTube + Pinterest + WhatsApp + Email + Twitter.

    Este agente elimina trabalho duplicado: em vez de criar conteúdo único para cada canal,
    ele pega o que já foi gerado para o blog e adapta para todos os outros formatos.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("content_repurposer", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get articles from content_generator
        gen = context.step_results.get("content_generator", {})
        gen_out = gen.get("output", {}) if isinstance(gen, dict) else {}
        articles = gen_out.get("articles", [])

        # Get offers
        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        offers = offers_out.get("available_offers", [])

        # Get keywords
        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])

        if not articles:
            # Fallback from briefs
            planner = context.step_results.get("content_planner", {})
            planner_out = planner.get("output", {}) if isinstance(planner, dict) else {}
            briefs = planner_out.get("briefs", [])
            if briefs:
                articles = [
                    {
                        "title": b.get("topic", b.get("keyword", "")),
                        "slug": b.get("keyword", "post").lower().replace(" ", "-"),
                        "keyword": b.get("keyword", ""),
                        "content_type": b.get("content_type", "article"),
                        "body": f"Conteúdo sobre {b.get('topic', '')}",
                        "meta_description": f"Guia sobre {b.get('topic', '')}",
                        "word_count": 200,
                    }
                    for b in briefs[:3]
                ]

        keyword = (
            opportunities[0]["keyword"]
            if opportunities
            else str(campaign.get("objective", "marketing digital"))
        )

        # Repurpose each article to all channels
        repurposed = []
        for article in articles[:3]:
            title = article.get("title", keyword)
            slug = article.get("slug", keyword.lower().replace(" ", "-"))
            body = article.get("body", "")
            meta_desc = article.get("meta_description", f"Guia sobre {keyword}")

            # → YouTube Script
            youtube = {
                "title": title.replace("Guia Completo", "Vídeo Completo"),
                "description": f"{meta_desc}\n\n📌 LINKS:\n"
                + "\n".join(
                    f"🔗 {o.get('product_name', 'Produto')}: {o.get('product_url', '#')}"
                    for o in offers[:3]
                )
                + "\n\n🔔 Inscreva-se para mais conteúdos!",
                "tags": [keyword, niche, "tutorial", "passo a passo"],
                "estimated_duration": "8-12 minutos",
                "source_article": slug,
            }

            # → Pinterest Pin
            pinterest = {
                "title": title,
                "description": f"{meta_desc[:100]}... Salve este pin para ver depois! 🎯\n\n#{keyword.replace(' ', '')} #{niche.replace(' ', '')}",
                "board": f"{niche.title()} Dicas",
                "source_article": slug,
            }

            # → WhatsApp Message
            whatsapp = (
                f"📢 *{title}*\n\n"
                f"{meta_desc[:150]}...\n\n"
                f"👉 Leia o artigo completo e descubra as melhores estratégias!\n\n"
                f"{' | '.join(o.get('product_name', '') for o in offers[:2])}"
            )

            # → Email teaser
            email = {
                "subject": f"📖 {title}",
                "preview": meta_desc[:120],
                "body_preview": body[:200] + "...",
                "cta": "Ler Artigo Completo",
                "source_article": slug,
            }

            # → Social post (Twitter/LinkedIn)
            social = (
                f"📌 {title}\n\n"
                f"{meta_desc[:200]}...\n\n"
                f"👉 Leia mais: #{keyword.replace(' ', '')}\n"
                f"#{' #'.join(niche.split()[:3])}"
            )

            repurposed.append(
                {
                    "source_article": {
                        "title": title,
                        "slug": slug,
                        "word_count": article.get("word_count", 0),
                    },
                    "youtube": youtube,
                    "pinterest": pinterest,
                    "whatsapp": whatsapp,
                    "email": email,
                    "social": social,
                    "channels_count": 5,
                }
            )

        total_formats = len(repurposed) * 5  # 5 formats per article
        output = {
            "repurposed_content": repurposed,
            "total_articles_repurposed": len(repurposed),
            "total_formats_generated": total_formats,
            "niche": niche,
            "efficiency_ratio": "1 artigo → 5 formatos (multiplicador 5x)",
            "recommendation": (
                f"Distribuir {total_formats} peças de conteúdo em 5 canais diferentes "
                f"a partir de {len(repurposed)} artigos. "
                f"Publicação escalonada ao longo da semana para máximo alcance orgânico."
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="content_repurposing",
                input_state={"articles": len(articles), "formats": 5},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "repurposed": len(repurposed),
                    "formats": total_formats,
                },
            )

        # Semantic memory
        if self.semantic_memory:
            rp_concept = self.semantic_memory.register_concept(
                f"repurpose_{context.run_id[:8]}",
                "content",
                f"Repurposing: {total_formats} peças de {len(repurposed)} artigos",
            )
            niche_concept = self.semantic_memory.find_concept(niche, "niche")
            if niche_concept:
                self.semantic_memory.assert_claim(
                    subject=niche_concept["concept_id"],
                    predicate="has_repurposing",
                    object=rp_concept,
                    confidence=0.85,
                    evidence_type="DIRECT_OBSERVATION",
                    epistemic_status="VERIFIED",
                    supporting_data={
                        "articles": len(repurposed),
                        "formats": total_formats,
                    },
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="content_repurposer",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Repurposou {len(repurposed)} artigos em {total_formats} formatos para 5 canais"
            ],
            metadata={"articles": len(repurposed), "formats": total_formats},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
