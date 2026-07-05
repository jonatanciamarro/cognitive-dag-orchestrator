"""UI Pricing Agent — Gera tabelas de preços de alta conversão estilo 21st.dev.

Gera pricing tables com múltiplos planos, destaque do plano recomendado,
comparação de features e CTA por plano.
Ponytail: stdlib-only.
"""

from __future__ import annotations

import time

from .base import AgentBase, AgentResult, CampaignContext, utc_now_iso


class UIPricingAgent(AgentBase):
    """Agent especializado em pricing tables."""

    def __init__(self, name: str = "ui_pricing"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign or {}
        niche = campaign.get("niche", "marketing digital")

        try:
            plans = self._generate_plans(niche)
            html, css = self._generate_pricing(niche, plans)

            output = {
                "status": "success",
                "pricing_id": f"pricing_{int(time.time())}",
                "html": html,
                "css": css,
                "plans": plans,
                "full_component": f"<style>{css}</style>\n{html}",
            }

            from pathlib import Path

            out_dir = Path("output") / "ui_design" / "pricing"
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / f"pricing_{int(time.time())}.html", "w") as f:
                f.write(output["full_component"])

        except Exception as e:
            output = {"status": "error", "error": str(e)}

        finished_at = utc_now_iso()
        return AgentResult(
            agent=self.name,
            status=output.get("status", "error"),
            output=output,
        )

    def _generate_plans(self, niche: str) -> list[dict]:
        return [
            {
                "name": "Básico",
                "price": "R$ 47",
                "period": "/mês",
                "featured": False,
                "features": [
                    "Acesso básico",
                    "1 nicho",
                    "Suporte email",
                    "7 dias garantia",
                ],
                "cta": "Começar Grátis",
            },
            {
                "name": "Profissional",
                "price": "R$ 97",
                "period": "/mês",
                "featured": True,
                "features": [
                    "Acesso completo",
                    "3 nichos",
                    "Suporte prioritário",
                    "Relatórios avançados",
                    "API",
                ],
                "cta": "Escolher Profissional",
            },
            {
                "name": "Enterprise",
                "price": "R$ 197",
                "period": "/mês",
                "featured": False,
                "features": [
                    "Tudo do Profissional",
                    "Nichos ilimitados",
                    "Suporte 24/7",
                    "Gerente dedicado",
                    "Customizações",
                ],
                "cta": "Falar com Vendas",
            },
        ]

    def _generate_pricing(self, niche: str, plans: list[dict]) -> tuple[str, str]:
        cards_html = ""
        for plan in plans:
            featured_class = " lyzer-pricing-featured" if plan.get("featured") else ""
            badge_html = (
                '<span class="lyzer-pricing-badge">Mais Popular</span>'
                if plan.get("featured")
                else ""
            )
            features_html = "".join(
                f'<li class="lyzer-pricing-feature"><span>✓</span> {f}</li>'
                for f in plan["features"]
            )
            cards_html += f"""
  <div class="lyzer-pricing-card{featured_class}">
    {badge_html}
    <h3 class="lyzer-pricing-name">{plan["name"]}</h3>
    <div class="lyzer-pricing-price">
      <span class="lyzer-pricing-amount">{plan["price"]}</span>
      <span class="lyzer-pricing-period">{plan["period"]}</span>
    </div>
    <ul class="lyzer-pricing-features">{features_html}</ul>
    <a href="#checkout" class="lyzer-pricing-cta">{plan["cta"]}</a>
  </div>"""

        html = f"""<section class="lyzer-pricing">
  <div class="lyzer-pricing-container">
    <h2 class="lyzer-pricing-title">Planos e Preços</h2>
    <p class="lyzer-pricing-subtitle">Escolha o plano ideal para seu negócio de {niche}</p>
    <div class="lyzer-pricing-grid">{cards_html}
    </div>
  </div>
</section>"""

        css = """.lyzer-pricing {
  padding: 6rem 2rem;
  background: #0a0a1a;
}
.lyzer-pricing-container { max-width: 1100px; margin: 0 auto; }
.lyzer-pricing-title {
  text-align: center; font-size: 2.5rem; font-weight: 800;
  color: #fff; margin: 0 0 1rem;
}
.lyzer-pricing-subtitle {
  text-align: center; color: #94a3b8;
  font-size: 1.1rem; margin: 0 0 4rem;
}
.lyzer-pricing-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem; align-items: start;
}
.lyzer-pricing-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px; padding: 2.5rem 2rem;
  position: relative; transition: transform 0.2s, border-color 0.2s;
}
.lyzer-pricing-card:hover { transform: translateY(-4px); }
.lyzer-pricing-featured {
  border-color: #6366f1;
  background: rgba(99,102,241,0.05);
  transform: scale(1.05);
}
.lyzer-pricing-badge {
  position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff; padding: 0.3rem 1rem; border-radius: 100px;
  font-size: 0.8rem; font-weight: 600; white-space: nowrap;
}
.lyzer-pricing-name { color: #fff; font-size: 1.3rem; margin: 0 0 1rem; }
.lyzer-pricing-price { margin-bottom: 1.5rem; }
.lyzer-pricing-amount { font-size: 2.5rem; font-weight: 800; color: #fff; }
.lyzer-pricing-period { color: #64748b; font-size: 0.9rem; }
.lyzer-pricing-features { list-style: none; padding: 0; margin: 0 0 2rem; }
.lyzer-pricing-feature {
  color: #94a3b8; padding: 0.5rem 0;
  font-size: 0.95rem;
}
.lyzer-pricing-feature span { color: #22c55e; margin-right: 0.5rem; }
.lyzer-pricing-cta {
  display: block; text-align: center; padding: 0.9rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; color: #e2e8f0;
  text-decoration: none; font-weight: 600;
  transition: background 0.2s;
}
.lyzer-pricing-featured .lyzer-pricing-cta {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
}
.lyzer-pricing-cta:hover { opacity: 0.9; }"""

        return html, css
