"""Agente de Email Marketing — gera sequências de emails para captura de leads, nurture e recomendações de afiliados."""

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


# Templates de email
_EMAIL_TEMPLATES: dict[str, dict[str, Any]] = {
    "welcome_sequence": {
        "name": "Sequência de Boas-Vindas",
        "description": "Sequência de 3 emails para novos leads, construindo autoridade e introduzindo ofertas.",
        "emails": [
            {
                "subject": "Bem-vindo ao clube! 🎉 Aqui está seu presente de boas-vindas",
                "preheader": "O que você vai aprender nos próximos dias",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Que bom ter você aqui! 🎉\n\n"
                    "Nos próximos dias, vou compartilhar com você os melhores conteúdos sobre {niche} "
                    "que ajudaram centenas de pessoas a transformar seus resultados.\n\n"
                    "Para começar, quero te presentear com este conteúdo especial:\n"
                    "👉 [Link do conteúdo gratuito]\n\n"
                    "Fique de olho no seu email — amanhã vou enviar uma dica prática que você pode "
                    "aplicar hoje mesmo.\n\n"
                    "Um abraço,\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 0,
                "goal": "aquecimento",
            },
            {
                "subject": "A estratégia que mudou tudo 🔥",
                "preheader": "Como aplicar {keyword} na prática",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "No email de hoje, quero compartilhar uma estratégia simples mas poderosa "
                    "que muitos ignoram quando o assunto é {keyword}.\n\n"
                    "[Aqui vai o conteúdo educativo com dicas práticas]\n\n"
                    "Se você aplicar isso hoje, vai ver resultados em poucos dias. "
                    "Prometo que não é complicatedo!\n\n"
                    "E se quiser se aprofundar, separei algumas ferramentas que recomendo:\n"
                    "{ofertas_texto}\n\n"
                    "Continue assim e até amanhã!\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 1,
                "goal": "educação",
            },
            {
                "subject": "O segredo dos profissionais de {niche} 🤫",
                "preheader": "Ferramentas que profissionais usam para acelerar resultados",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Hoje vou revelar as ferramentas que os profissionais de {niche} usam "
                    "para obter resultados muito mais rápido.\n\n"
                    "A verdade é que tentar fazer tudo manualmente é perda de tempo. "
                    "Com as ferramentas certas, você faz em horas o que levaria dias.\n\n"
                    "{ofertas_texto}\n\n"
                    "Lembrando que alguns links são de afiliados — você não paga nada a mais "
                    "por isso, e me ajuda a continuar criando conteúdo gratuito.\n\n"
                    "Até o próximo email!\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 3,
                "goal": "conversão",
            },
        ],
    },
    "promo_sequence": {
        "name": "Sequência Promocional",
        "description": "Sequência de 2 emails focada em promover um produto específico de afiliado.",
        "emails": [
            {
                "subject": "Por que {product_name} está fazendo tanto sucesso? 🏆",
                "preheader": "Análise completa de {product_name}",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Você já ouviu falar de {product_name}?\n\n"
                    "Milhares de pessoas estão usando e os resultados são impressionantes. "
                    "Neste email, vou te mostrar exatamente por que este produto "
                    "se destaca no mercado de {niche}.\n\n"
                    "[Aqui vai uma análise honesta com prós, contras e diferenciais]\n\n"
                    "👉 {product_url}\n\n"
                    "Se você está buscando uma solução completa para {keyword}, "
                    "{product_name} pode ser exatamente o que você precisa.\n\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 0,
                "goal": "apresentação",
            },
            {
                "subject": "Última chance: oferta especial de {product_name} ⏰",
                "preheader": "Não perca esta oportunidade",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Se você está considerando {product_name}, agora é o momento.\n\n"
                    "A oferta atual inclui bônus exclusivos que podem não estar disponíveis "
                    "nos próximos dias.\n\n"
                    "👉 {product_url}\n\n"
                    "Qualquer dúvida, é só responder este email.\n\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 3,
                "goal": "urgência",
            },
        ],
    },
    "nurture_sequence": {
        "name": "Sequência de Nutrição",
        "description": "Sequência de 4 emails para manter engajamento e gerar confiança ao longo do tempo.",
        "emails": [
            {
                "subject": "3 erros que {keyword} iniciantes cometem 🚫",
                "preheader": "Evite estes erros comuns",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Depois de ajudar centenas de pessoas com {keyword}, percebi que "
                    "os mesmos 3 erros se repetem...\n\n"
                    "1️⃣ [Erro 1]\n2️⃣ [Erro 2]\n3️⃣ [Erro 3]\n\n"
                    "Evitando estes erros, você economiza semanas de tentativa e erro.\n\n"
                    "Na próxima semana, vou mostrar como corrigir cada um deles.\n\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 0,
                "goal": "engajamento",
            },
            {
                "subject": "Case de sucesso: de zero a resultado com {keyword} 📈",
                "preheader": "Inspire-se com esta história",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Quero compartilhar uma história inspiradora de alguém que começou "
                    "do zero e conseguiu resultados incríveis com {keyword}.\n\n"
                    "[História do case, desafios, estratégias e resultados]\n\n"
                    "O que mais me impressiona é que qualquer pessoa pode replicar "
                    "esta estratégia — inclusive você.\n\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 3,
                "goal": "inspiração",
            },
            {
                "subject": "As melhores ferramentas para {keyword} em {year} 🛠️",
                "preheader": "Ferramentas recomendadas para {keyword}",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Testei dezenas de ferramentas para {keyword} e separei as que "
                    "realmente valem a pena.\n\n"
                    "{ofertas_texto}\n\n"
                    "Cada uma delas tem seus pontos fortes. A melhor escolha depende "
                    "do seu objetivo específico.\n\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 7,
                "goal": "recomendação",
            },
            {
                "subject": "O que você faria se pudesse começar de novo? 🔄",
                "preheader": "Reflexão e próximos passos",
                "body_template": (
                    "Olá {{nome}},\n\n"
                    "Esta é uma pergunta que gosto de fazer: se pudesse começar de novo "
                    "sabendo o que sei hoje sobre {keyword}, o que eu faria diferente?\n\n"
                    "Minha resposta: focaria no essencial desde o início e ignoraria o ruído.\n\n"
                    "Espero que esta sequência de emails tenha te ajudado. Se tiver "
                    "qualquer dúvida, é só responder este email.\n\n"
                    "Continue firme e até a próxima!\n"
                    "{{nome_remetente}}"
                ),
                "delay_days": 14,
                "goal": "relacionamento",
            },
        ],
    },
}


def _build_offers_text(offers: list[dict[str, Any]]) -> str:
    """Build formatted offers text for emails."""
    if not offers:
        return ""
    text = ""
    for offer in offers[:3]:
        pname = offer.get("product_name", "Produto")
        purl = offer.get("product_url", "#")
        desc = offer.get("description", "")
        text += f"🔗 **{pname}** — {desc}\n👉 {purl}\n\n"
    return text


def _render_email_body(
    template: str,
    variables: dict[str, str],
    offers_text: str,
) -> str:
    """Render email body template with variables."""
    result = template.replace("{ofertas_texto}", offers_text)
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    return result


def _generate_sequences(
    keyword: str,
    niche: str,
    product_name: str,
    product_url: str,
    offers: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate all email sequences."""
    year = "2026"
    variables_base: dict[str, str] = {
        "keyword": keyword,
        "niche": niche,
        "product_name": product_name,
        "year": year,
    }
    offers_text = _build_offers_text(offers)

    sequences = []
    total_emails = 0
    for seq_key, seq_template in _EMAIL_TEMPLATES.items():
        if product_name and product_url:
            variables = dict(variables_base)
            variables["product_name"] = product_name
            variables["product_url"] = product_url
        else:
            variables = dict(variables_base)
            variables["product_name"] = niche  # fallback
            variables["product_url"] = "#"

        emails = []
        for email_tmpl in seq_template["emails"]:
            subject = email_tmpl["subject"]
            for key, val in variables.items():
                placeholder = "{" + key + "}"
                if placeholder in subject:
                    subject = subject.replace(placeholder, str(val))

            preheader = email_tmpl["preheader"]
            for key, val in variables.items():
                placeholder = "{" + key + "}"
                if placeholder in preheader:
                    preheader = preheader.replace(placeholder, str(val))

            body = _render_email_body(
                email_tmpl["body_template"], variables, offers_text
            )

            emails.append(
                {
                    "subject": subject,
                    "preheader": preheader,
                    "body": body,
                    "delay_days": email_tmpl["delay_days"],
                    "goal": email_tmpl["goal"],
                }
            )

        sequences.append(
            {
                "name": seq_template["name"],
                "description": seq_template["description"],
                "emails": emails,
                "total_emails": len(emails),
            }
        )
        total_emails += len(emails)

    return {
        "sequences": sequences,
        "total_sequences": len(sequences),
        "total_emails": total_emails,
    }


class EmailMarketingAgent(AgentBase):
    """Gera sequências de email marketing automatizadas com ofertas de afiliados."""

    def __init__(self, **kwargs) -> None:
        super().__init__("email_marketing", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get keyword from SEO or campaign
        seo = context.step_results.get("seo_research", {})
        seo_output = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_output.get("top_opportunities", [])
        keyword = (
            opportunities[0]["keyword"]
            if opportunities
            else str(campaign.get("objective", "marketing digital"))
        )

        # Get offers
        offers_step = context.step_results.get("offer_lookup", {})
        offers_output = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_output.get("available_offers", [])

        # Get or generate lead magnet suggestion
        lead_magnet = context.artifacts.get(
            "lead_magnet", f"Guia Completo de {keyword}"
        )

        # Extract product info from first offer
        product_name = (
            available_offers[0].get("product_name", "Produto Recomendado")
            if available_offers
            else niche
        )
        product_url = (
            available_offers[0].get("product_url", "#") if available_offers else "#"
        )

        # Generate email sequences
        result = _generate_sequences(
            keyword, niche, product_name, product_url, available_offers
        )

        output = {
            **result,
            "lead_magnet": lead_magnet,
            "niche": niche,
            "generation_method": "template_based",
            "recommendation": (
                f"Criar {result['total_emails']} emails em {result['total_sequences']} sequências. "
                f"Lead magnet: '{lead_magnet}'. "
                f"Primeiro email: '{result['sequences'][0]['emails'][0]['subject']}'."
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="email_marketing",
                input_state={
                    "niche": niche,
                    "keyword": keyword,
                    "sequences": result["total_sequences"],
                },
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "sequences": result["total_sequences"],
                    "emails": result["total_emails"],
                },
            )

        # Semantic memory
        if self.semantic_memory:
            email_concept_id = self.semantic_memory.register_concept(
                f"email_seq_{context.run_id[:8]}",
                "content",
                f"Sequência de {result['total_emails']} emails para {niche}",
            )
            niche_concept = self.semantic_memory.find_concept(niche, "niche")
            if niche_concept:
                self.semantic_memory.assert_claim(
                    subject=niche_concept["concept_id"],
                    predicate="has_email_sequence",
                    object=email_concept_id,
                    confidence=0.7,
                    evidence_type="DIRECT_OBSERVATION",
                    epistemic_status="INFERRED",
                    supporting_data={
                        "emails": result["total_emails"],
                        "sequences": result["total_sequences"],
                    },
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="email_marketing",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {result['total_emails']} emails em {result['total_sequences']} sequências para '{keyword}'"
            ],
            metadata={
                "sequences": result["total_sequences"],
                "emails": result["total_emails"],
                "niche": niche,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
