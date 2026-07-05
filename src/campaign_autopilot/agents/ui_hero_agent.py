"""UI Hero Section Agent — Gera hero sections de alta conversão estilo 21st.dev.

Produz HTML/CSS responsivo com design tokens, animações e CTA otimizado.
Ponytail: stdlib-only, sem dependências externas.
"""

from __future__ import annotations

import time

from .base import AgentBase, AgentResult, CampaignContext, utc_now_iso


class UIHeroAgent(AgentBase):
    """Agent especializado em hero sections de landing pages.

    Gera hero sections com:
    - Título de impacto
    - Subtítulo persuasivo
    - CTA principal + secundário
    - Badge de confiança/social proof
    - Animações CSS sutis
    """

    def __init__(self, name: str = "ui_hero"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign or {}
        niche = campaign.get("niche", "marketing digital")
        offer = campaign.get("offer", {})
        goal = campaign.get("goal", "conversao")

        try:
            html, css = self._generate_hero(niche, offer, goal)
            hero_id = f"hero_{int(time.time())}"

            output = {
                "status": "success",
                "hero_id": hero_id,
                "html": html,
                "css": css,
                "full_component": f"<style>{css}</style>\n{html}",
                "niche": niche,
                "goal": goal,
            }

            # Salvar em output/ui_design/
            from pathlib import Path

            out_dir = Path("output") / "ui_design" / "hero"
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / f"{hero_id}.html", "w") as f:
                f.write(output["full_component"])

        except Exception as e:
            output = {"status": "error", "error": str(e)}

        finished_at = utc_now_iso()
        return AgentResult(
            agent=self.name,
            status=output.get("status", "error"),
            output=output,
        )

    def _generate_hero(self, niche: str, offer: dict, goal: str) -> tuple[str, str]:
        """Generate a high-converting hero section with 21st.dev-style design."""
        title = offer.get("title", f"Domine {niche.title()} em 2026")
        subtitle = offer.get(
            "subtitle",
            f"A plataforma completa para transformar seus resultados em {niche}",
        )
        cta = offer.get("cta", "Começar Agora")
        badge = offer.get("badge", f"🚀 {niche.title()}")

        html = f"""<section class="lyzer-hero">
  <div class="lyzer-hero-bg"></div>
  <div class="lyzer-hero-container">
    <span class="lyzer-hero-badge">{badge}</span>
    <h1 class="lyzer-hero-title">{title}</h1>
    <p class="lyzer-hero-subtitle">{subtitle}</p>
    <div class="lyzer-hero-actions">
      <a href="#cta" class="lyzer-hero-cta">{cta}</a>
      <a href="#features" class="lyzer-hero-secondary">Saber Mais →</a>
    </div>
    <div class="lyzer-hero-social">
      <span>⚡ Mais de 10 mil alunos</span>
      <span>⭐ 4.9/5 avaliações</span>
      <span>🏆 Resultado em 30 dias</span>
    </div>
  </div>
</section>"""

        css = """.lyzer-hero {
  position: relative;
  min-height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
}
.lyzer-hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.15) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(59,130,246,0.08) 0%, transparent 50%);
  pointer-events: none;
}
.lyzer-hero-container {
  position: relative;
  max-width: 800px;
  text-align: center;
  z-index: 1;
}
.lyzer-hero-badge {
  display: inline-block;
  padding: 0.5rem 1.2rem;
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.3);
  border-radius: 100px;
  color: #a5b4fc;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  letter-spacing: 0.02em;
}
.lyzer-hero-title {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  color: #fff;
  margin: 0 0 1.5rem;
  letter-spacing: -0.03em;
}
.lyzer-hero-subtitle {
  font-size: clamp(1.1rem, 2vw, 1.35rem);
  color: #94a3b8;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto 2.5rem;
}
.lyzer-hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 3rem;
}
.lyzer-hero-cta {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 600;
  font-size: 1.05rem;
  border-radius: 12px;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 20px rgba(99,102,241,0.3);
}
.lyzer-hero-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(99,102,241,0.4);
}
.lyzer-hero-secondary {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(255,255,255,0.05);
  color: #cbd5e1;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  text-decoration: none;
  transition: background 0.2s;
}
.lyzer-hero-secondary:hover { background: rgba(255,255,255,0.1); }
.lyzer-hero-social {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
  color: #64748b;
  font-size: 0.9rem;
}"""

        return html, css
