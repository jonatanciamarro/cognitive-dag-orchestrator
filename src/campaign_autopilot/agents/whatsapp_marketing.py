"""Agente de Marketing no WhatsApp — gera mensagens, broadcasts, grupos e sequências para WhatsApp."""

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


_WHATSAPP_TEMPLATES: dict[str, dict[str, Any]] = {
    "welcome": {
        "name": "Mensagem de Boas-Vindas",
        "body_template": (
            "Olá {{nome}}! 👋\n\n"
            "Que bom ter você aqui! Sou o {nome_canal} e vou compartilhar dicas exclusivas "
            "sobre {niche} diretamente no seu WhatsApp.\n\n"
            "📌 *O que você vai receber:*\n"
            "✅ Dicas práticas de {keyword}\n"
            "✅ Ferramentas recomendadas\n"
            "✅ Ofertas exclusivas para assinantes\n\n"
            "Para começar, separei um conteúdo especial pra você:\n"
            "{link_presente}\n\n"
            "Fique à vontade para responder este número com dúvidas! 🚀"
        ),
        "media_type": "text",
        "schedule": "immediate",
    },
    "tip": {
        "name": "Dica Rápida",
        "body_template": (
            "💡 *Dica Rápida de {keyword}*\n\n"
            "{dica}\n\n"
            "Quer se aprofundar? 👇\n"
            "{link_artigo}\n\n"
            "Gostou? Encaminhe para um amigo! 🤝"
        ),
        "media_type": "text",
        "schedule": "segunda, quarta, sexta",
    },
    "offer": {
        "name": "Oferta Exclusiva",
        "body_template": (
            "🏆 *Oferta Exclusiva para Assinantes*\n\n"
            "{product_name} — {descricao_oferta}\n\n"
            "👉 {product_url}\n\n"
            "{disclosure}\n\n"
            "Corre que pode ser por tempo limitado! ⏰"
        ),
        "media_type": "text",
        "schedule": "quinta",
    },
    "engagement": {
        "name": "Pergunta de Engajamento",
        "body_template": (
            "📢 *Vamos conversar?*\n\n"
            "{pergunta}\n\n"
            "Responda aqui mesmo! Sua opinião é muito importante 💬"
        ),
        "media_type": "text",
        "schedule": "sabado",
    },
    "weekly_digest": {
        "name": "Resumo Semanal",
        "body_template": (
            "📋 *Resumo da Semana — {semana}*\n\n"
            "O que você perdeu:\n"
            "{topicos_semana}\n\n"
            "📌 *Dica do momento:*\n"
            "{dica_momento}\n\n"
            "👉 {link_destaque}\n\n"
            "Ótimo final de semana! 🎉"
        ),
        "media_type": "text",
        "schedule": "domingo",
    },
}


class WhatsAppMarketingAgent(AgentBase):
    """Gera estratégia completa de marketing no WhatsApp: mensagens, broadcasts, agendamento."""

    def __init__(self, **kwargs) -> None:
        super().__init__("whatsapp_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get keyword and offers
        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])
        keyword = (
            opportunities[0]["keyword"]
            if opportunities
            else str(campaign.get("objective", "marketing digital"))
        )

        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_out.get("available_offers", [])

        # Get articles
        gen_step = context.step_results.get("content_generator", {})
        gen_out = gen_step.get("output", {}) if isinstance(gen_step, dict) else {}
        articles = gen_out.get("articles", [])

        # Build messages from templates
        messages = []
        total_weekly = 0

        for msg_type, template in _WHATSAPP_TEMPLATES.items():
            body = template["body_template"]
            variables = {
                "nome_canal": niche.title(),
                "niche": niche,
                "keyword": keyword,
                "link_presente": articles[0].get("slug", "#") if articles else "#",
                "link_artigo": articles[0].get("slug", "#") if articles else "#",
                "dica": f"Comece com {keyword} focando no básico. Domine um canal de cada vez.",
                "product_name": available_offers[0].get(
                    "product_name", "Produto Recomendado"
                )
                if available_offers
                else "Produto Recomendado",
                "product_url": available_offers[0].get("product_url", "#")
                if available_offers
                else "#",
                "descricao_oferta": f"Acesse {keyword} com condição especial para nossa lista VIP.",
                "disclosure": "*Alguns links podem ser de afiliados. Você não paga nada a mais por isso.*",
                "pergunta": f"Qual sua maior dificuldade com {keyword} atualmente?",
                "semana": "atual",
                "topicos_semana": f"• Artigo: {articles[0]['title'][:50] if articles else keyword}\n• Dica: {keyword} na prática\n• Oferta especial",
                "dica_momento": f"Consistência é mais importante que perfeição em {keyword}.",
                "link_destaque": articles[0].get("slug", "#") if articles else "#",
            }

            for k, v in variables.items():
                placeholder = "{" + k + "}"
                if placeholder in body:
                    body = body.replace(placeholder, str(v))

            messages.append(
                {
                    "type": msg_type,
                    "name": template["name"],
                    "body": body,
                    "media_type": template["media_type"],
                    "schedule": template["schedule"],
                }
            )

            # Count weekly messages
            if template["schedule"] != "immediate":
                total_weekly += 1

        output = {
            "messages": messages,
            "total_messages": len(messages),
            "weekly_messages": total_weekly,
            "niche": niche,
            "strategy": (
                f"Estratégia WhatsApp: {len(messages)} tipos de mensagem, "
                f"~{total_weekly} mensagens por semana. "
                f"Capturar leads via link de convite → sequência de boas-vindas → "
                f"dicas 3x/semana → ofertas 1x/semana → engajamento semanal."
            ),
            "recommended_tools": [
                "WhatsApp Business API (para automação real)",
                "WATI / Z-API / Evolution API (integração brasileira)",
                "Link de convite: https://wa.me/5511999999999?text=Quero{niche}",
            ],
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="whatsapp_marketing",
                input_state={"niche": niche, "keyword": keyword},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={"messages": len(messages), "weekly": total_weekly},
            )

        # Semantic memory
        if self.semantic_memory:
            wa_concept = self.semantic_memory.register_concept(
                f"wa_{context.run_id[:8]}",
                "content",
                f"Estratégia WhatsApp: {total_weekly} msg/semana para {niche}",
            )
            niche_concept = self.semantic_memory.find_concept(niche, "niche")
            if niche_concept:
                self.semantic_memory.assert_claim(
                    subject=niche_concept["concept_id"],
                    predicate="has_whatsapp_strategy",
                    object=wa_concept,
                    confidence=0.7,
                    evidence_type="DIRECT_OBSERVATION",
                    epistemic_status="INFERRED",
                    supporting_data={"messages": len(messages), "weekly": total_weekly},
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="whatsapp_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(messages)} templates de WhatsApp para '{niche}' (~{total_weekly} msg/semana)"
            ],
            metadata={
                "messages": len(messages),
                "weekly": total_weekly,
                "niche": niche,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
