"""Agente de Planejamento de Conteúdo — combina pesquisa SEO com ofertas de afiliados."""

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


class ContentPlannerAgent(AgentBase):
    """Recebe pesquisa SEO + ofertas de afiliados e produz briefings de conteúdo."""

    def __init__(self, **kwargs) -> None:
        super().__init__("content_planner", **kwargs)
        self._offer_manager = None

    @property
    def offer_manager(self) -> Any:
        return self._offer_manager

    @offer_manager.setter
    def offer_manager(self, value: Any) -> None:
        self._offer_manager = value

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        seo = context.step_results.get("seo_research", {})
        offers_step = context.step_results.get("offer_lookup", {})
        memory = context.step_results.get("memory_lookup", {})

        seo_output = seo.get("output", {}) if isinstance(seo, dict) else {}
        offers_output = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        memory_output = memory.get("output", {}) if isinstance(memory, dict) else {}

        # Obter oportunidades de SEO
        opportunities = seo_output.get("top_opportunities", [])
        if not opportunities:
            # Fallback: usar do contexto
            opportunities = [
                {
                    "keyword": str(
                        context.campaign.get("objective", "marketing digital")
                    ),
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                    "suggested_type": "article",
                }
            ]

        # Obter ofertas disponíveis
        available_offers = offers_output.get("available_offers", [])
        learnings = memory_output.get("learnings", [])

        # Combinar keywords com ofertas
        briefs = []
        for kw in opportunities[:5]:
            matched_offers = []
            matched_ids = []
            kw_lower = kw["keyword"].lower()

            # Match simples: oferta cujo produto aparece na keyword
            for offer in available_offers:
                offer_name = str(offer.get("product_name", "")).lower()
                offer_cat = str(offer.get("category", "")).lower()
                if any(term in kw_lower for term in (offer_name[:10], offer_cat[:10])):
                    matched_offers.append(offer)
                    matched_ids.append(offer.get("offer_id", ""))

            # Se não achou match, pegar a primeira oferta disponível como sugestão
            if not matched_offers and available_offers:
                matched_offers.append(available_offers[0])
                matched_ids.append(available_offers[0].get("offer_id", ""))

            # Gerar outline baseado na intenção
            intent = kw.get("intent", "informational")
            if intent == "informational":
                outline = [
                    f"O que é {kw['keyword']}?",
                    f"Por que {kw['keyword']} é importante?",
                    f"Principais benefícios de {kw['keyword']}",
                    "Dicas práticas para começar",
                    "Perguntas frequentes",
                ]
            elif intent == "commercial":
                outline = [
                    f"Por que você precisa de {kw['keyword']}",
                    "Comparação das melhores opções",
                    f"Review: {matched_offers[0].get('product_name', 'Produto')}"
                    if matched_offers
                    else "",
                    "Prós e contras",
                    "Recomendação final",
                ]
            else:  # transactional
                outline = [
                    "O que considerar antes de comprar",
                    "Passo a passo para escolher",
                    f"Ofertas recomendadas: {matched_offers[0].get('product_name', 'Produto')}"
                    if matched_offers
                    else "",
                    "Depoimentos e resultados",
                    "Conclusão",
                ]

            outline = [item for item in outline if item]  # Remove vazios

            content_type = kw.get("suggested_type", "article")
            if content_type == "review":
                content_type = "article"

            briefs.append(
                {
                    "topic": kw["keyword"],
                    "keyword": kw["keyword"],
                    "content_type": content_type,
                    "search_intent": intent,
                    "offers": matched_ids,
                    "outline": outline,
                    "estimated_volume": kw.get("volume", 1000),
                    "difficulty": kw.get("difficulty", 0.5),
                    "affiliate_links_needed": len(matched_ids),
                }
            )

        # Aplicar aprendizados do memory
        applied_lessons = []
        for lesson in learnings:
            applied_lessons.append(str(lesson))

        output = {
            "briefs": briefs,
            "total_briefs": len(briefs),
            "applied_lessons": applied_lessons,
            "content_strategy": (
                f"Produzir {len(briefs)} conteúdos no nicho. "
                f"Prioridade: keywords com difficulty < 0.40 e intent informacional. "
                f"Inserir links de afiliado nos artigos comerciais."
            ),
        }

        # Registrar explicação
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="content_planning",
                input_state={
                    "opportunities_count": len(opportunities),
                    "offers_count": len(available_offers),
                    "briefs_generated": len(briefs),
                },
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "strategy": output["content_strategy"],
                    "briefs": len(briefs),
                },
            )

        # Armazenar briefs no semantic memory
        if self.semantic_memory:
            for brief in briefs[:3]:
                brief_concept = self.semantic_memory.register_concept(
                    f"brief_{brief['keyword'][:25]}",
                    "content_brief",
                    f"Type: {brief['content_type']}, Volume: {brief['estimated_volume']}",
                )
                self.semantic_memory.assert_claim(
                    subject=brief_concept,
                    predicate="targets_keyword",
                    object=brief_concept,  # self-reference for tracking
                    confidence=1.0 - brief["difficulty"],
                    evidence_type="INFERRED",
                    epistemic_status="INFERRED",
                    supporting_data={
                        "keyword": brief["keyword"],
                        "outline_count": len(brief["outline"]),
                    },
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="content_planner",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(briefs)} briefings de conteúdo baseados em {len(opportunities)} keywords e {len(available_offers)} ofertas"
            ],
            metadata={"briefs": len(briefs), "keywords_used": len(opportunities)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
