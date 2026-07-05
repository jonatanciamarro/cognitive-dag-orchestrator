"""UI FAQ Agent — Gera seções de FAQ responsivas estilo 21st.dev.

FAQ com accordion JavaScript puro, schema.org markup e design system tokens.
Ponytail: stdlib-only, zero dependências.
"""

from __future__ import annotations

import time

from .base import AgentBase, AgentResult, CampaignContext, utc_now_iso


class UIFAQAgent(AgentBase):
    """Agent especializado em seções FAQ com accordion interativo."""

    def __init__(self, name: str = "ui_faq"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign or {}
        niche = campaign.get("niche", "marketing digital")

        try:
            faqs = self._generate_faqs(niche)
            html, css, js = self._generate_faq(niche, faqs)
            full = f"<style>{css}</style>\n{html}\n<script>{js}</script>"

            output = {
                "status": "success",
                "faq_id": f"faq_{int(time.time())}",
                "html": html,
                "css": css,
                "js": js,
                "faq_count": len(faqs),
                "full_component": full,
            }

            from pathlib import Path

            out_dir = Path("output") / "ui_design" / "faq"
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / f"faq_{int(time.time())}.html", "w") as f:
                f.write(full)

        except Exception as e:
            output = {"status": "error", "error": str(e)}

        finished_at = utc_now_iso()
        return AgentResult(
            agent=self.name,
            status=output.get("status", "error"),
            output=output,
        )

    def _generate_faqs(self, niche: str) -> list[dict]:
        return [
            {
                "q": f"O que é {niche}?",
                "a": f"{niche.title()} é uma metodologia comprovada que ajuda milhares de pessoas a transformarem seus resultados. Com nossa plataforma, você aprende na prática.",
            },
            {
                "q": "Preciso de experiência?",
                "a": "Não! Nosso sistema foi desenvolvido para iniciantes absolutos. Você começa do zero e avança no seu ritmo com suporte completo.",
            },
            {
                "q": "Quanto tempo até ver resultados?",
                "a": "Alunos dedicados começam a ver resultados nas primeiras semanas. O tempo varia conforme seu foco e consistência.",
            },
            {
                "q": "Qual a garantia?",
                "a": "Oferecemos 7 dias de garantia incondicional. Se não ficar satisfeito, devolvemos 100% do seu investimento.",
            },
            {
                "q": "Funciona para qualquer nicho?",
                "a": "Sim! Nossa metodologia é adaptável para qualquer nicho ou mercado.",
            },
        ]

    def _generate_faq(self, niche: str, faqs: list[dict]) -> tuple[str, str, str]:
        items_html = ""
        for i, faq in enumerate(faqs):
            items_html += f"""
  <div class="lyzer-faq-item">
    <button class="lyzer-faq-question" onclick="lyzerToggleFAQ(this)">
      <span>{faq["q"]}</span>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
    </button>
    <div class="lyzer-faq-answer">
      <p>{faq["a"]}</p>
    </div>
  </div>"""

        html = f"""<section class="lyzer-faq" itemscope itemtype="https://schema.org/FAQPage">
  <div class="lyzer-faq-container">
    <h2 class="lyzer-faq-title">Perguntas Frequentes</h2>
    <p class="lyzer-faq-subtitle">Tire suas dúvidas sobre {niche}</p>
    <div class="lyzer-faq-list">{items_html}
    </div>
  </div>
</section>"""

        css = """.lyzer-faq {
  padding: 6rem 2rem;
  background: #0d0d2b;
}
.lyzer-faq-container { max-width: 768px; margin: 0 auto; }
.lyzer-faq-title {
  text-align: center; font-size: 2.5rem; font-weight: 800;
  color: #fff; margin: 0 0 1rem;
}
.lyzer-faq-subtitle {
  text-align: center; color: #94a3b8;
  font-size: 1.1rem; margin: 0 0 4rem;
}
.lyzer-faq-item {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  margin-bottom: 1rem;
  overflow: hidden;
  background: rgba(255,255,255,0.02);
}
.lyzer-faq-question {
  width: 100%; display: flex; align-items: center;
  justify-content: space-between; padding: 1.25rem 1.5rem;
  background: none; border: none; cursor: pointer;
  color: #e2e8f0; font-size: 1rem; font-weight: 500;
  text-align: left; transition: background 0.2s;
}
.lyzer-faq-question:hover { background: rgba(255,255,255,0.03); }
.lyzer-faq-question svg { transition: transform 0.2s; flex-shrink: 0; }
.lyzer-faq-question.active svg { transform: rotate(180deg); }
.lyzer-faq-answer {
  max-height: 0; overflow: hidden;
  transition: max-height 0.3s ease;
}
.lyzer-faq-answer p {
  padding: 0 1.5rem 1.25rem; margin: 0;
  color: #94a3b8; line-height: 1.6;
}"""

        js = """function lyzerToggleFAQ(btn) {
  btn.classList.toggle('active');
  var answer = btn.nextElementSibling;
  if (answer.style.maxHeight) {
    answer.style.maxHeight = null;
  } else {
    answer.style.maxHeight = answer.scrollHeight + 'px';
  }
}"""

        return html, css, js
