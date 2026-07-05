"""Agente de Marketing no Pinterest — gera pins, descrições SEO, boards e estratégia de tráfego orgânico."""

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


_PIN_TEMPLATES: dict[str, dict[str, Any]] = {
    "infographic": {
        "title_template": "{keyword} — Infográfico Completo [{year}]",
        "description_template": (
            "Aprenda tudo sobre {keyword} neste infográfico completo. "
            "Salve este pin para consultar depois e siga o board para mais conteúdos sobre {niche}! "
            "{hashtags}"
        ),
        "board": "{niche} Dicas e Tutoriais",
        "seo_keywords": ["infográfico", "guia visual", "passo a passo"],
    },
    "tutorial": {
        "title_template": "Como {keyword} — Tutorial Passo a Passo",
        "description_template": (
            "Quer aprender {keyword}? Este tutorial passo a passo vai te ajudar. "
            "Perfeito para iniciantes em {niche}. Salve para ver depois! "
            "{hashtags}"
        ),
        "board": "Tutoriais de {niche}",
        "seo_keywords": ["tutorial", "como fazer", "passo a passo", "iniciantes"],
    },
    "list": {
        "title_template": "Top {number} Dicas de {keyword} para {year}",
        "description_template": (
            "As melhores dicas de {keyword} para você aplicar hoje. "
            "Salve este pin para não perder nenhuma dica e siga o board! "
            "{hashtags}"
        ),
        "board": "Melhores de {niche}",
        "seo_keywords": ["melhores dicas", "top", "lista", "guia"],
    },
    "product": {
        "title_template": "{product_name} — Review e Opinião [{year}]",
        "description_template": (
            "Confira nosso review completo de {product_name}. "
            "Descubra se vale a pena e como pode ajudar você em {niche}. "
            "Salve para comparar opções! "
            "{hashtags}"
        ),
        "board": "Ferramentas de {niche}",
        "seo_keywords": ["review", "vale a pena", "opinião", "comparativo"],
    },
}


class PinterestMarketingAgent(AgentBase):
    """Gera pins, descrições SEO, boards e estratégia para Pinterest."""

    def __init__(self, **kwargs) -> None:
        super().__init__("pinterest_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get keywords from SEO
        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])

        # Get offers
        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_out.get("available_offers", [])

        # Fallback
        if not opportunities:
            opportunities = [
                {
                    "keyword": str(campaign.get("objective", "marketing digital")),
                    "volume": 1000,
                    "difficulty": 0.3,
                    "intent": "informational",
                }
            ]

        # Generate pins for each keyword
        pins = []
        boards_used = set()
        for i, opp in enumerate(opportunities[:5]):
            keyword = opp.get("keyword", str(campaign.get("objective", "")))
            intent = opp.get("intent", "informational")

            # Choose pin type based on intent
            if intent == "commercial" and available_offers:
                pin_type = "product"
            elif intent == "informational":
                pin_type = "infographic" if i % 2 == 0 else "tutorial"
            else:
                pin_type = "list"

            template = _PIN_TEMPLATES[pin_type]

            # Get matching product
            product_name = ""
            if pin_type == "product" and available_offers:
                product_name = available_offers[0].get("product_name", "")

            # Generate hashtags
            hashtags = self._generate_hashtags(keyword, niche)

            # Variables
            year = "2026"
            number = str(5 + (i % 11))  # 5-15
            vars_map = {
                "keyword": keyword,
                "niche": niche,
                "year": year,
                "number": number,
                "product_name": product_name,
                "hashtags": " ".join(hashtags[:8]),
            }

            # Build title
            title = template["title_template"]
            for k, v in vars_map.items():
                title = title.replace(f"{{{k}}}", str(v))

            # Build description
            desc = template["description_template"]
            for k, v in vars_map.items():
                desc = desc.replace(f"{{{k}}}", str(v))

            # Build board name
            board = template["board"]
            for k, v in vars_map.items():
                board = board.replace(f"{{{k}}}", str(v))
            boards_used.add(board)

            # Build SEO keywords list
            seo_kws = [keyword] + template["seo_keywords"] + [niche]

            # Create link to related content
            related_content_url = "#"
            if pin_type == "product" and available_offers:
                related_content_url = available_offers[0].get("product_url", "#")

            pins.append(
                {
                    "title": title,
                    "description": desc,
                    "board": board,
                    "pin_type": pin_type,
                    "seo_keywords": seo_kws[:10],
                    "hashtags": hashtags[:10],
                    "related_content_url": related_content_url,
                    "image_suggestion": self._suggest_image(keyword, pin_type),
                    "keyword": keyword,
                }
            )

        output = {
            "pins": pins,
            "total_pins": len(pins),
            "boards": list(boards_used),
            "total_boards": len(boards_used),
            "niche": niche,
            "generation_method": "template_based",
            "recommendation": (
                f"Criar {len(pins)} pins para Pinterest distribuídos em {len(boards_used)} boards. "
                f"Postar 1 pin por dia para crescimento orgânico consistente. "
                f"Pinterest é uma das melhores fontes de tráfego evergreen para afiliados."
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="pinterest_marketing",
                input_state={"opportunities": len(opportunities), "niche": niche},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"pins": len(pins), "boards": len(boards_used)},
            )

        # Semantic memory
        if self.semantic_memory:
            for pin in pins:
                pin_concept_id = self.semantic_memory.register_concept(
                    f"pin_{pin['keyword'][:15]}",
                    "content",
                    pin["title"][:100],
                )
                niche_concept = self.semantic_memory.find_concept(niche, "niche")
                if niche_concept:
                    self.semantic_memory.assert_claim(
                        subject=niche_concept["concept_id"],
                        predicate="has_pin",
                        object=pin_concept_id,
                        confidence=0.7,
                        evidence_type="DIRECT_OBSERVATION",
                        epistemic_status="INFERRED",
                        supporting_data={
                            "board": pin["board"],
                            "type": pin["pin_type"],
                        },
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="pinterest_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(pins)} pins para {len(boards_used)} boards no nicho '{niche}'"
            ],
            metadata={"pins": len(pins), "boards": len(boards_used), "niche": niche},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _generate_hashtags(keyword: str, niche: str) -> list[str]:
        """Generate SEO hashtags for Pinterest."""
        words = keyword.lower().split() + niche.lower().split()
        tags = set()
        for w in words:
            if len(w) > 2:
                tags.add(f"#{w}")
        additional = {
            "marketing": [
                "#marketingdigital",
                "#afiliados",
                "#marketingparainiciantes",
            ],
            "financas": ["#financaspessoais", "#educacaofinanceira", "#rendaextra"],
            "tecnologia": ["#tecnologia", "#ferramentasdigitais", "#produtividade"],
            "digital": ["#marketingdigital", "#cursogratuito", "#empreendedorismo"],
        }
        for key, extra_tags in additional.items():
            if key in keyword.lower() or key in niche.lower():
                tags.update(extra_tags)

        return list(tags)[:12]

    @staticmethod
    def _suggest_image(keyword: str, pin_type: str) -> str:
        """Suggest image description for the pin."""
        suggestions = {
            "infographic": f"Infográfico vertical com dicas sobre {keyword}. Fundo clean, cores vibrantes.",
            "tutorial": f"Capa de tutorial com passo a passo de {keyword}. Números grandes e chamativos.",
            "list": f"Lista com ícones e dicas de {keyword}. Design moderno e fácil de ler.",
            "product": "Mockup do produto com review. Avaliação em estrelas e destaque para o nome.",
        }
        return suggestions.get(pin_type, f"Imagem profissional sobre {keyword}")
