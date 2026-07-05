"""LandingPageAgent — Cria landing pages otimizadas para campanhas de tráfego pago.

Gera páginas de conversão focadas em:
- Oferta de afiliado
- Captura de email (lead magnet)
- Venda direta de produto digital
- Assinatura de membros
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("landing_page")

LANDING_TEMPLATES = {
    "affiliate": {
        "name": "Review + Link de Afiliado",
        "sections": [
            "hero",
            "problema",
            "solucao",
            "beneficios",
            "cta",
            "faq",
            "disclosure",
        ],
    },
    "lead_capture": {
        "name": "Captura de Email (Lead Magnet)",
        "sections": [
            "hero",
            "oferta_gratis",
            "beneficios",
            "formulario",
            "prova_social",
        ],
    },
    "digital_product": {
        "name": "Venda de Produto Digital",
        "sections": [
            "hero",
            "dor",
            "solucao",
            "conteudo",
            "depoimentos",
            "garantia",
            "cta",
        ],
    },
    "membership": {
        "name": "Assinatura de Membros",
        "sections": ["hero", "beneficios", "planos", "comparacao", "cta", "faq"],
    },
}


class LandingPageAgent(AgentBase):
    """Gera landing pages otimizadas para conversão."""

    def __init__(self, **kwargs) -> None:
        super().__init__("landing_page", **kwargs)

    def _generate_landing_html(self, article: dict, lp_type: str, niche: str) -> str:
        """Generate a complete landing page HTML."""
        content = article.get("content", article)
        title = content.get("title", "Oferta Especial")
        intro = content.get("introduction", "")
        meta = content.get("meta_description", "Oferta exclusiva para você")

        has_affiliate = bool(content.get("_meta", {}).get("affiliate_links"))
        affiliate_links = content.get("_meta", {}).get("affiliate_links", [])
        disclosure = content.get("_meta", {}).get("affiliate_disclosure", "")

        # Build CTA link
        cta_link = "/"
        cta_text = "Saiba Mais"
        if affiliate_links:
            cta_link = affiliate_links[0].get("url", "/")
            cta_text = f"Comprar {affiliate_links[0].get('product', 'Agora')}"

        sections_html = ""
        template = LANDING_TEMPLATES.get(lp_type, LANDING_TEMPLATES["affiliate"])

        for section in template["sections"]:
            if section == "hero":
                sections_html += f"""
                <section class="hero">
                    <h1>{title}</h1>
                    <p class="subtitle">{meta}</p>
                    <a href="{cta_link}" class="cta-button">{cta_text}</a>
                </section>"""
            elif section == "problema":
                sections_html += """
                <section class="problema">
                    <h2>Você já se sentiu assim?</h2>
                    <p>Muitas pessoas enfrentam dificuldades quando o assunto é encontrar a melhor opção. Informações contraditórias, preços confusos, medo de fazer a escolha errada.</p>
                    <p>Mas não se preocupe — estamos aqui para ajudar.</p>
                </section>"""
            elif section == "solucao":
                sections_html += f"""
                <section class="solucao">
                    <h2>A Solução Que Você Procura</h2>
                    <p>{intro[:300]}</p>
                </section>"""
            elif section == "beneficios":
                sections_html += """
                <section class="beneficios">
                    <h2>Por Que Escolher Esta Opção?</h2>
                    <ul>
                        <li>✅ Qualidade comprovada por milhares de usuários</li>
                        <li>✅ Suporte especializado e dedicado</li>
                        <li>✅ Garantia de satisfação ou seu dinheiro de volta</li>
                        <li>✅ Entrega imediata e segura</li>
                    </ul>
                </section>"""
            elif section == "cta":
                sections_html += f"""
                <section class="cta-section">
                    <h2>Não Perca Esta Oportunidade!</h2>
                    <p>Clique no botão abaixo e garanta a melhor opção para você.</p>
                    <a href="{cta_link}" class="cta-button big">{cta_text} →</a>
                    <p class="urgency">⚠️ Oferta por tempo limitado</p>
                </section>"""
            elif section == "faq":
                sections_html += """
                <section class="faq">
                    <h2>Perguntas Frequentes</h2>
                    <div class="faq-item"><strong>Vale a pena?</strong><p>Sim, milhares de pessoas já se beneficiaram desta escolha.</p></div>
                    <div class="faq-item"><strong>Tem garantia?</strong><p>Sim, você tem garantia de satisfação ou seu dinheiro de volta.</p></div>
                    <div class="faq-item"><strong>Como funciona?</strong><p>Simples: clique no link, escolha a melhor opção e aproveite.</p></div>
                </section>"""
            elif section == "disclosure" and disclosure:
                sections_html += (
                    f'<section class="disclosure"><p>{disclosure}</p></section>'
                )
            elif section == "oferta_gratis":
                sections_html += """
                <section class="oferta-gratis">
                    <h2>Receba Conteúdo Exclusivo Grátis!</h2>
                    <p>Inscreva-se e receba dicas valiosas diretamente no seu email.</p>
                </section>"""
            elif section == "formulario":
                sections_html += """
                <section class="form-section">
                    <form class="lead-form" action="#" method="POST">
                        <input type="text" name="nome" placeholder="Seu nome" required>
                        <input type="email" name="email" placeholder="Seu melhor email" required>
                        <button type="submit" class="cta-button">Quero Receber Grátis!</button>
                    </form>
                </section>"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Landing Page</title>
    <meta name="description" content="{meta}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #1a1a2e; }}
        .hero {{ background: linear-gradient(135deg, #1a365d, #2b6cb0); color: white; padding: 80px 20px; text-align: center; }}
        .hero h1 {{ font-size: 2.5rem; margin-bottom: 20px; max-width: 800px; margin: 0 auto 20px; }}
        .subtitle {{ font-size: 1.2rem; opacity: 0.9; max-width: 600px; margin: 0 auto 30px; }}
        .cta-button {{ display: inline-block; background: #48bb78; color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-size: 1.1rem; font-weight: bold; margin-top: 20px; transition: transform 0.2s; }}
        .cta-button:hover {{ transform: scale(1.05); }}
        section {{ padding: 60px 20px; max-width: 800px; margin: 0 auto; }}
        section h2 {{ font-size: 1.8rem; margin-bottom: 20px; color: #1a365d; }}
        ul {{ list-style: none; }}
        ul li {{ padding: 8px 0; font-size: 1.1rem; }}
        .cta-section {{ text-align: center; background: #f7fafc; border-radius: 12px; margin: 40px auto; }}
        .big {{ padding: 20px 60px; font-size: 1.3rem; }}
        .urgency {{ color: #e53e3e; margin-top: 15px; font-weight: bold; }}
        .faq-item {{ padding: 15px 0; border-bottom: 1px solid #e2e8f0; }}
        .faq-item strong {{ color: #2b6cb0; }}
        .lead-form {{ display: flex; flex-direction: column; gap: 15px; max-width: 400px; margin: 0 auto; }}
        .lead-form input {{ padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; }}
        .lead-form button {{ cursor: pointer; border: none; }}
        .disclosure {{ font-size: 0.8rem; color: #718096; text-align: center; padding: 30px 20px; }}
        @media (max-width: 600px) {{ .hero h1 {{ font-size: 1.8rem; }} section {{ padding: 40px 15px; }} }}
    </style>
</head>
<body>
    {sections_html}
</body>
</html>"""
        return html

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        niche = campaign.get("niche", "tecnologia")
        lp_type = campaign.get("landing_page_type", "affiliate")
        output_dir = campaign.get("output_dir", "site/landing")

        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        landing_pages = []
        for article in articles:
            content = article.get("content", article)
            slug = content.get("slug", f"lp-{len(landing_pages)}")

            html = self._generate_landing_html(article, lp_type, niche)
            file_path = output_path / f"{slug}.html"
            file_path.write_text(html, encoding="utf-8")

            landing_pages.append(
                {
                    "title": content.get("title", "Untitled"),
                    "slug": slug,
                    "file": str(file_path),
                    "url": f"/landing/{slug}.html",
                    "type": lp_type,
                }
            )

        output = {
            "landing_pages": landing_pages,
            "total": len(landing_pages),
            "output_directory": str(output_path),
            "type": LANDING_TEMPLATES.get(lp_type, {}).get("name", lp_type),
            "next_steps": [
                "Vincule as landing pages às campanhas de anúncio",
                "Configure pixel de conversão (Google Ads, Meta Pixel)",
                "Teste A/B diferentes versões da landing page",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="landing_page",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=int(
                (
                    datetime.fromisoformat(finished_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
                * 1000
            ),
            thread_name="main",
            notes=[f"{len(landing_pages)} landing pages criadas para {niche}"],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
