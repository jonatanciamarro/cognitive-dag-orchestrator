"""Agente de Captura de Leads — gera lead magnets, landing pages e formulários de opt-in."""

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


_LEAD_MAGNET_TEMPLATES: dict[str, dict[str, Any]] = {
    "ebook": {
        "title": "Guia Completo de {keyword} para Iniciantes",
        "subtitle": "Aprenda {keyword} do zero com este guia passo a passo",
        "format": "PDF",
        "benefits": [
            "Entenda os fundamentos de {keyword}",
            "Evite os 5 erros mais comuns de iniciantes",
            "Economize meses de tentativa e erro",
        ],
        "cta": "📥 Baixar Guia Grátis",
        "color_scheme": "blue",
    },
    "checklist": {
        "title": "Checklist Completo de {keyword}",
        "subtitle": "{number} passos essenciais para dominar {keyword}",
        "format": "PDF (1 página)",
        "benefits": [
            "Tenha um roteiro claro de {keyword}",
            "Não pule nenhuma etapa importante",
            "Acompanhe seu progresso",
        ],
        "cta": "📋 Quero o Checklist",
        "color_scheme": "green",
    },
    "template": {
        "title": "Template de {keyword} — Edite e Use",
        "subtitle": "Pronto para usar. Basta preencher com suas informações.",
        "format": "Planilha/Google Sheets",
        "benefits": [
            "Economize horas de trabalho",
            "Estrutura profissional validada",
            "Personalizável para seu nicho",
        ],
        "cta": "📊 Baixar Template Grátis",
        "color_scheme": "orange",
    },
    "video": {
        "title": "Mini-Curso Grátis: {keyword} em {number} Dias",
        "subtitle": "{number} vídeos direto ao ponto sobre {keyword}",
        "format": "Vídeos (YouTube)",
        "benefits": [
            "Aprenda no seu ritmo",
            "Conteúdo 100% prático",
            "Acesso vitalício",
        ],
        "cta": "🎬 Quero o Mini-Curso",
        "color_scheme": "purple",
    },
}

_LANDING_PAGE_SECTIONS: list[dict[str, Any]] = [
    {
        "section": "hero",
        "template": "Título grande + subtítulo + CTA principal + imagem de fundo",
    },
    {"section": "benefits", "template": "3-5 benefícios com ícones do lead magnet"},
    {
        "section": "social_proof",
        "template": "Depoimentos ou números (ex: 'Já ajudou 1000+ pessoas')",
    },
    {"section": "form", "template": "Formulário simples: Nome + Email + Botão de CTA"},
    {"section": "footer", "template": "Links, disclosure, garantia de privacidade"},
]

_EMAIL_CAPTURE_TEMPLATES: dict[str, str] = {
    "popup": (
        "🔓 *Conteúdo Exclusivo!*\n\n"
        "Deixe seu email para receber o {lead_magnet} gratuitamente.\n"
        "Prometemos não enviar spam. Descadastre-se quando quiser."
    ),
    "inline": (
        "📩 *Gostou do conteúdo?*\n"
        "Receba mais dicas como esta + {lead_magnet} gratuitamente:\n"
        "[Formulário de email]"
    ),
    "exit": (
        "⏰ *Espera! Não vá ainda!*\n\n"
        "Baixe grátis: {lead_magnet}\n"
        "[Email] → [Baixar Agora]"
    ),
}


class LeadCaptureAgent(AgentBase):
    """Gera estratégia completa de captura de leads: lead magnets, landing pages, formulários."""

    def __init__(self, **kwargs) -> None:
        super().__init__("lead_capture", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get keyword from SEO
        seo = context.step_results.get("seo_research", {})
        seo_out = seo.get("output", {}) if isinstance(seo, dict) else {}
        opportunities = seo_out.get("top_opportunities", [])
        keyword = (
            opportunities[0]["keyword"]
            if opportunities
            else str(campaign.get("objective", "marketing digital"))
        )

        # Get offers
        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        available_offers = offers_out.get("available_offers", [])

        # Generate lead magnets
        lead_magnets = []
        for i, (lm_type, template) in enumerate(_LEAD_MAGNET_TEMPLATES.items()):
            number = str(5 + (i * 2))  # 5, 7, 9, 11
            variables = {"keyword": keyword, "niche": niche, "number": number}

            title = template["title"]
            subtitle = template["subtitle"]
            for k, v in variables.items():
                title = title.replace("{" + k + "}", str(v))
                subtitle = subtitle.replace("{" + k + "}", str(v))

            benefits = []
            for b in template["benefits"]:
                for k, v in variables.items():
                    b = b.replace("{" + k + "}", str(v))
                benefits.append(b)

            lead_magnets.append(
                {
                    "type": lm_type,
                    "title": title,
                    "subtitle": subtitle,
                    "format": template["format"],
                    "benefits": benefits,
                    "cta": template["cta"],
                    "color_scheme": template["color_scheme"],
                }
            )

        # Generate landing page structure
        landing_page = {
            "sections": _LANDING_PAGE_SECTIONS,
            "primary_lead_magnet": lead_magnets[0]["title"]
            if lead_magnets
            else f"Guia de {keyword}",
            "form_fields": ["Nome", "Email"],
            "privacy_note": "Seus dados estão seguros. Você pode cancelar a qualquer momento.",
            "html_structure": self._generate_html_structure(
                lead_magnets[0] if lead_magnets else None, keyword, niche
            ),
        }

        # Generate email capture variants
        email_captures = {}
        for cap_type, template in _EMAIL_CAPTURE_TEMPLATES.items():
            body = template.replace(
                "{lead_magnet}",
                lead_magnets[0]["title"] if lead_magnets else f"Guia de {keyword}",
            )
            email_captures[cap_type] = body

        # Generate content upgrade suggestions
        articles = context.step_results.get("content_generator", {}).get("output", {})
        if isinstance(articles, dict):
            art_list = articles.get("articles", [])
        else:
            art_list = []
        content_upgrades = []
        for art in art_list[:3]:
            content_upgrades.append(
                {
                    "article_title": art.get("title", ""),
                    "suggested_lead_magnet": f"Checklist complementar: {art.get('keyword', keyword)}",
                    "placement": "meio do artigo + final do artigo",
                }
            )

        output = {
            "lead_magnets": lead_magnets,
            "total_lead_magnets": len(lead_magnets),
            "landing_page": landing_page,
            "email_capture_variants": email_captures,
            "content_upgrades": content_upgrades,
            "niche": niche,
            "keyword": keyword,
            "recommendation": (
                f"Criar landing page com lead magnet '{lead_magnets[0]['title'] if lead_magnets else keyword}'. "
                f"Incluir popup de captura nos artigos + formulário inline. "
                f"Oferecer {lead_magnets[1]['title'] if len(lead_magnets) > 1 else 'checklist'} como content upgrade."
            ),
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="lead_capture",
                input_state={"niche": niche, "keyword": keyword},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "lead_magnets": len(lead_magnets),
                    "content_upgrades": len(content_upgrades),
                },
            )

        # Semantic memory
        if self.semantic_memory:
            lc_concept = self.semantic_memory.register_concept(
                f"lc_{context.run_id[:8]}",
                "content",
                f"Lead capture: {len(lead_magnets)} magnets para {niche}",
            )
            niche_concept = self.semantic_memory.find_concept(niche, "niche")
            if niche_concept:
                self.semantic_memory.assert_claim(
                    subject=niche_concept["concept_id"],
                    predicate="has_lead_capture",
                    object=lc_concept,
                    confidence=0.7,
                    evidence_type="DIRECT_OBSERVATION",
                    epistemic_status="INFERRED",
                    supporting_data={
                        "lead_magnets": len(lead_magnets),
                        "landing_page": True,
                    },
                    source_cycle_id=context.run_id,
                    asserted_by=self.name,
                    observer_id=self.name,
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="lead_capture",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(lead_magnets)} lead magnets e landing page para '{niche}'"
            ],
            metadata={
                "lead_magnets": len(lead_magnets),
                "content_upgrades": len(content_upgrades),
                "niche": niche,
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _generate_html_structure(
        lead_magnet: dict | None, keyword: str, niche: str
    ) -> str:
        """Generate a simple HTML structure for the landing page."""
        if lead_magnet:
            title = lead_magnet["title"]
            subtitle = lead_magnet["subtitle"]
            cta = lead_magnet["cta"]
            benefits = "\n".join(
                f"    <li>✨ {b}</li>" for b in lead_magnet["benefits"]
            )
        else:
            title = f"Guia Completo de {keyword}"
            subtitle = f"Aprenda {keyword} do zero"
            cta = "Baixar Grátis"
            benefits = f"    <li>✨ Domine {keyword}</li>"

        return f"""<!-- Landing Page HTML Structure -->
<div class="landing-page">
  <section class="hero">
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <a href="#form" class="cta-button">{cta}</a>
  </section>
  <section class="benefits">
    <h2>Você vai receber:</h2>
    <ul>
{benefits}
    </ul>
  </section>
  <section class="form" id="form">
    <h2>Baixe agora — é grátis!</h2>
    <form>
      <input type="text" name="name" placeholder="Seu nome" required>
      <input type="email" name="email" placeholder="Seu melhor email" required>
      <button type="submit">{cta}</button>
    </form>
    <p class="privacy">🔒 Seus dados estão seguros. Sem spam.</p>
  </section>
</div>"""
