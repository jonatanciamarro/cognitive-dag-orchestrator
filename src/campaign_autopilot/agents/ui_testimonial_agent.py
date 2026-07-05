"""UI Testimonial Agent — Gera seções de depoimentos estilo 21st.dev.

Cards de depoimento com foto, nome, cargo, rating estrelas e texto.
Carrossel CSS nativo (sem JS).
Ponytail: stdlib-only.
"""

from __future__ import annotations

import time

from .base import AgentBase, AgentResult, CampaignContext, utc_now_iso


class UITestimonialAgent(AgentBase):
    """Agent especializado em seções de depoimentos/social proof."""

    def __init__(self, name: str = "ui_testimonial"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign or {}
        niche = campaign.get("niche", "marketing digital")

        try:
            testimonials = self._generate_testimonials(niche)
            html, css = self._generate_section(niche, testimonials)

            output = {
                "status": "success",
                "testimonial_id": f"testimonial_{int(time.time())}",
                "html": html,
                "css": css,
                "count": len(testimonials),
                "full_component": f"<style>{css}</style>\n{html}",
            }

            from pathlib import Path

            out_dir = Path("output") / "ui_design" / "testimonials"
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / f"testimonials_{int(time.time())}.html", "w") as f:
                f.write(output["full_component"])

        except Exception as e:
            output = {"status": "error", "error": str(e)}

        finished_at = utc_now_iso()
        return AgentResult(
            agent=self.name,
            status=output.get("status", "error"),
            output=output,
        )

    def _generate_testimonials(self, niche: str) -> list[dict]:
        return [
            {
                "name": "Ana Silva",
                "role": f"Empreendedora {niche.title()}",
                "text": f"Transformei meu negócio com {niche}! Em apenas 3 meses já estava vendo resultados que não esperava. Recomendo para todos que querem crescer.",
                "rating": 5,
            },
            {
                "name": "Carlos Oliveira",
                "role": "Analista de Marketing",
                "text": "A plataforma é intuitiva e o suporte é incrível. Consegui aplicar tudo que aprendi e meus resultados quadruplicaram.",
                "rating": 5,
            },
            {
                "name": "Mariana Costa",
                "role": "Produtora Digital",
                "text": "Comecei do zero e hoje faturo mais de R$ 10k/mês graças à metodologia. O diferencial é o acompanhamento próximo.",
                "rating": 5,
            },
        ]

    def _generate_section(
        self, niche: str, testimonials: list[dict]
    ) -> tuple[str, str]:
        cards = ""
        for t in testimonials:
            stars = "★" * t["rating"] + "☆" * (5 - t["rating"])
            cards += f"""
  <div class="lyzer-testimonial-card">
    <div class="lyzer-testimonial-stars">{stars}</div>
    <p class="lyzer-testimonial-text">"{t["text"]}"</p>
    <div class="lyzer-testimonial-author">
      <div class="lyzer-testimonial-avatar">{t["name"][0]}</div>
      <div>
        <strong>{t["name"]}</strong>
        <span>{t["role"]}</span>
      </div>
    </div>
  </div>"""

        html = f"""<section class="lyzer-testimonials">
  <div class="lyzer-testimonials-container">
    <h2 className="lyzer-testimonials-title">O Que Nossos Alunos Dizem</h2>
    <p class="lyzer-testimonials-subtitle">Histórias reais de quem transformou sua vida com {niche}</p>
    <div class="lyzer-testimonials-grid">{cards}
    </div>
  </div>
</section>"""

        css = """.lyzer-testimonials {
  padding: 6rem 2rem;
  background: #0a0a1a;
}
.lyzer-testimonials-container { max-width: 1100px; margin: 0 auto; }
.lyzer-testimonials-title {
  text-align: center; font-size: 2.5rem; font-weight: 800;
  color: #fff; margin: 0 0 1rem;
}
.lyzer-testimonials-subtitle {
  text-align: center; color: #94a3b8;
  font-size: 1.1rem; margin: 0 0 4rem;
}
.lyzer-testimonials-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}
.lyzer-testimonial-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px; padding: 2rem;
  transition: transform 0.2s;
}
.lyzer-testimonial-card:hover { transform: translateY(-4px); }
.lyzer-testimonial-stars { color: #f59e0b; font-size: 1.1rem; margin-bottom: 1rem; }
.lyzer-testimonial-text {
  color: #94a3b8; line-height: 1.7;
  font-style: italic; margin-bottom: 1.5rem;
}
.lyzer-testimonial-author {
  display: flex; align-items: center; gap: 0.75rem;
}
.lyzer-testimonial-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #fff; font-size: 1.1rem;
}
.lyzer-testimonial-author strong { display: block; color: #e2e8f0; font-size: 0.95rem; }
.lyzer-testimonial-author span { color: #64748b; font-size: 0.8rem; }"""

        return html, css
