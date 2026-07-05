"""UI Full Page Composer — Landing page completa premium com SVG + CSS effects.

Gera uma única página HTML com TODOS os componentes:
Navbar + Hero + Features + Pricing + Testimonials + FAQ + CTA + Footer
Design premium com SVG icons, glassmorphism, animações CSS, mobile-first.
Ponytail: stdlib-only, ~15KB total.
"""

from __future__ import annotations

import time

from .base import AgentBase, AgentResult, CampaignContext, utc_now_iso


class UIFullPageAgent(AgentBase):
    """Campaign Autopilot — Lyzer Labs landing page generator."""
    """Agent que compõe landing pages completas premium em um único arquivo."""

    def __init__(self, name: str = "ui_full_page"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign or {}
        niche = campaign.get("niche", "marketing digital")

        try:
            full_html = self._generate_premium_page(niche)
            from pathlib import Path
            out_dir = Path("output") / "ui_design"
            out_dir.mkdir(parents=True, exist_ok=True)
            filename = f"landing_{niche.lower().replace(' ', '_')}_{int(time.time())}.html"
            output_path = out_dir / filename
            output_path.write_text(full_html)

            output = {
                "status": "success",
                "niche": niche,
                "output_file": str(output_path),
                "total_chars": len(full_html),
                "sections": ["navbar", "hero", "features", "pricing", "testimonials", "faq", "cta", "footer"],
            }
        except Exception as e:
            output = {"status": "error", "error": str(e)}

        finished_at = utc_now_iso()
        return AgentResult(agent=self.name, status=output.get("status", "error"), output=output)

    def _generate_premium_page(self, niche: str) -> str:
        """Generate a complete premium landing page with all components."""
        title_niche = niche.title()
        
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<title>{title_niche} — Plataforma Completa 2026</title>
<meta name="description" content="Transforme seus resultados com {niche}. Plataforma completa com metodologia comprovada.">
<style>
/* ═══ DESIGN TOKENS ═══ */
:root {{
  --bg: #0a0a1a;
  --bg2: #0d0d2b;
  --card: rgba(255,255,255,0.03);
  --card-hover: rgba(255,255,255,0.06);
  --primary: #6366f1;
  --primary-light: #818cf8;
  --primary-dark: #4f46e5;
  --gradient: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
  --gradient-glow: linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2));
  --text: #fff;
  --text2: #94a3b8;
  --text3: #64748b;
  --border: rgba(255,255,255,0.08);
  --success: #22c55e;
  --warning: #f59e0b;
  --radius: 12px;
  --radius-lg: 20px;
  --shadow: 0 4px 24px rgba(0,0,0,0.3);
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-heading: 'Inter', sans-serif;
}}

/* ═══ RESET ═══ */
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
html {{ scroll-behavior:smooth; -webkit-font-smoothing:antialiased; }}
body {{ font-family:var(--font); background:var(--bg); color:var(--text); line-height:1.6; overflow-x:hidden; }}
img {{ max-width:100%; height:auto; }}
a {{ color:inherit; text-decoration:none; }}

/* ═══ NAVBAR ═══ */
nav {{
  position:fixed; top:0; left:0; right:0; z-index:100;
  background:rgba(10,10,26,0.85); backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  padding:0 1.5rem;
}}
nav .nav-inner {{
  max-width:1200px; margin:0 auto;
  display:flex; align-items:center; justify-content:space-between;
  height:64px;
}}
nav .logo {{ font-size:1.25rem; font-weight:700; background:var(--gradient); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
nav .links {{ display:flex; gap:2rem; }}
nav .links a {{ color:var(--text2); font-size:0.9rem; font-weight:500; transition:color 0.2s; }}
nav .links a:hover {{ color:var(--text); }}
nav .nav-cta {{
  display:inline-flex; align-items:center; gap:0.5rem;
  padding:0.6rem 1.5rem; border-radius:100px;
  background:var(--gradient); color:#fff; font-weight:600; font-size:0.85rem;
  transition:transform 0.2s, box-shadow 0.2s;
}}
nav .nav-cta:hover {{ transform:translateY(-1px); box-shadow:0 4px 20px rgba(99,102,241,0.4); }}
.nav-toggle {{ display:none; flex-direction:column; gap:4px; cursor:pointer; background:none; border:none; padding:4px; }}
.nav-toggle span {{ display:block; width:24px; height:2px; background:var(--text); border-radius:2px; transition:0.2s; }}
@media (max-width:768px) {{
  nav .links {{ display:none; }}
  .nav-toggle {{ display:flex; }}
}}

/* ═══ HERO ═══ */
.hero {{
  min-height:90vh; display:flex; align-items:center; justify-content:center;
  padding:6rem 1.5rem 4rem; position:relative; overflow:hidden;
  background:linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
}}
.hero-bg {{
  position:absolute; inset:0; pointer-events:none;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.15) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, rgba(59,130,246,0.08) 0%, transparent 50%);
}}
.hero-content {{ position:relative; max-width:800px; text-align:center; z-index:1; }}
.hero-badge {{
  display:inline-flex; align-items:center; gap:0.5rem;
  padding:0.5rem 1.2rem; background:rgba(99,102,241,0.15);
  border:1px solid rgba(99,102,241,0.3); border-radius:100px;
  color:#a5b4fc; font-size:0.85rem; font-weight:500; margin-bottom:1.5rem;
}}
.hero h1 {{
  font-size:clamp(2.2rem,6vw,4rem); font-weight:800; line-height:1.1;
  margin-bottom:1.5rem; letter-spacing:-0.03em;
}}
.hero h1 span {{ background:var(--gradient); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
.hero p {{
  font-size:clamp(1rem,2vw,1.25rem); color:var(--text2);
  max-width:600px; margin:0 auto 2.5rem; line-height:1.7;
}}
.hero-actions {{ display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; margin-bottom:3rem; }}
.btn-primary {{
  display:inline-flex; align-items:center; gap:0.5rem;
  padding:1rem 2.5rem; background:var(--gradient); color:#fff;
  font-weight:600; font-size:1rem; border-radius:var(--radius);
  transition:transform 0.2s, box-shadow 0.2s; box-shadow:0 4px 20px rgba(99,102,241,0.3);
}}
.btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 6px 30px rgba(99,102,241,0.4); }}
.btn-secondary {{
  display:inline-flex; align-items:center; gap:0.5rem;
  padding:1rem 2rem; background:rgba(255,255,255,0.05);
  color:var(--text2); font-weight:500; border:1px solid var(--border);
  border-radius:var(--radius); transition:background 0.2s;
}}
.btn-secondary:hover {{ background:rgba(255,255,255,0.1); }}
.hero-proof {{
  display:flex; gap:2rem; justify-content:center; flex-wrap:wrap;
  color:var(--text3); font-size:0.85rem;
}}
.hero-proof span {{ display:flex; align-items:center; gap:0.4rem; }}

/* ═══ SECTIONS ═══ */
.section {{ padding:5rem 1.5rem; }}
.section-alt {{ background:var(--bg2); }}
.section-container {{ max-width:1100px; margin:0 auto; }}
.section-header {{ text-align:center; margin-bottom:4rem; }}
.section-header h2 {{ font-size:clamp(1.8rem,4vw,2.5rem); font-weight:800; margin-bottom:1rem; }}
.section-header p {{ color:var(--text2); font-size:1.1rem; max-width:600px; margin:0 auto; }}

/* ═══ FEATURES ═══ */
.features-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:1.5rem;
}}
.feature-card {{
  background:var(--card); border:1px solid var(--border); border-radius:var(--radius-lg);
  padding:2rem; transition:transform 0.2s, border-color 0.2s, background 0.2s;
}}
.feature-card:hover {{ transform:translateY(-4px); border-color:rgba(99,102,241,0.3); background:var(--card-hover); }}
.feature-icon {{ width:56px; height:56px; border-radius:16px; background:rgba(99,102,241,0.1); display:flex; align-items:center; justify-content:center; margin-bottom:1.25rem; }}
.feature-card h3 {{ font-size:1.15rem; font-weight:600; margin-bottom:0.5rem; }}
.feature-card p {{ color:var(--text2); font-size:0.9rem; line-height:1.6; }}

/* ═══ PRICING ═══ */
.pricing-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr));
  gap:2rem; align-items:start;
}}
.pricing-card {{
  background:var(--card); border:1px solid var(--border); border-radius:var(--radius-lg);
  padding:2.5rem 2rem; position:relative; transition:transform 0.2s, border-color 0.2s;
}}
.pricing-card:hover {{ transform:translateY(-4px); }}
.pricing-card.featured {{
  border-color:var(--primary); background:rgba(99,102,241,0.05);
  transform:scale(1.05);
}}
.pricing-card.featured:hover {{ transform:scale(1.05) translateY(-4px); }}
.pricing-badge {{
  position:absolute; top:-12px; left:50%; transform:translateX(-50%);
  background:var(--gradient); color:#fff; padding:0.3rem 1rem; border-radius:100px;
  font-size:0.8rem; font-weight:600; white-space:nowrap;
}}
.pricing-name {{ font-size:1.3rem; font-weight:600; margin-bottom:1rem; }}
.pricing-price {{ margin-bottom:1.5rem; }}
.pricing-amount {{ font-size:2.5rem; font-weight:800; }}
.pricing-period {{ color:var(--text3); font-size:0.9rem; }}
.pricing-features {{ list-style:none; padding:0; margin:0 0 2rem; }}
.pricing-features li {{ color:var(--text2); padding:0.5rem 0; font-size:0.9rem; display:flex; align-items:center; gap:0.5rem; }}
.pricing-features li .check {{ color:var(--success); flex-shrink:0; }}
.pricing-cta {{
  display:block; text-align:center; padding:0.85rem;
  background:rgba(255,255,255,0.05); border:1px solid var(--border);
  border-radius:var(--radius); color:var(--text2); font-weight:600;
  transition:background 0.2s;
}}
.pricing-card.featured .pricing-cta {{ background:var(--gradient); color:#fff; border:none; }}
.pricing-cta:hover {{ opacity:0.9; }}

/* ═══ TESTIMONIALS ═══ */
.testimonials-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:2rem;
}}
.testimonial-card {{
  background:var(--card); border:1px solid var(--border); border-radius:var(--radius-lg);
  padding:2rem; transition:transform 0.2s;
}}
.testimonial-card:hover {{ transform:translateY(-4px); }}
.testimonial-stars {{ color:var(--warning); margin-bottom:1rem; }}
.testimonial-text {{ color:var(--text2); font-style:italic; line-height:1.7; margin-bottom:1.5rem; }}
.testimonial-author {{ display:flex; align-items:center; gap:0.75rem; }}
.testimonial-avatar {{
  width:44px; height:44px; border-radius:50%;
  background:var(--gradient); display:flex; align-items:center; justify-content:center;
  font-weight:700; font-size:1rem; color:#fff; flex-shrink:0;
}}
.testimonial-author strong {{ display:block; font-size:0.9rem; }}
.testimonial-author span {{ font-size:0.8rem; color:var(--text3); }}

/* ═══ FAQ ═══ */
.faq-list {{ max-width:700px; margin:0 auto; }}
.faq-item {{
  border:1px solid var(--border); border-radius:var(--radius);
  margin-bottom:0.75rem; overflow:hidden; background:rgba(255,255,255,0.02);
}}
.faq-question {{
  width:100%; display:flex; align-items:center; justify-content:space-between;
  padding:1.25rem 1.5rem; background:none; border:none; cursor:pointer;
  color:var(--text); font-size:1rem; font-weight:500; text-align:left;
  transition:background 0.2s;
}}
.faq-question:hover {{ background:rgba(255,255,255,0.03); }}
.faq-question svg {{ transition:transform 0.2s; flex-shrink:0; }}
.faq-question.active svg {{ transform:rotate(180deg); }}
.faq-answer {{ max-height:0; overflow:hidden; transition:max-height 0.3s ease; }}
.faq-answer p {{ padding:0 1.5rem 1.25rem; margin:0; color:var(--text2); line-height:1.6; }}

/* ═══ CTA BANNER ═══ */
.cta-banner {{
  background:var(--gradient-glow); border:1px solid rgba(99,102,241,0.2);
  border-radius:var(--radius-lg); padding:4rem 2rem; text-align:center;
  position:relative; overflow:hidden;
}}
.cta-banner::before {{
  content:''; position:absolute; inset:0;
  background:radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.15), transparent);
  pointer-events:none;
}}
.cta-banner h2 {{ font-size:clamp(1.5rem,3vw,2rem); margin-bottom:1rem; }}
.cta-banner p {{ color:var(--text2); max-width:500px; margin:0 auto 2rem; }}
.cta-banner .btn-primary {{ font-size:1.1rem; padding:1.1rem 3rem; }}

/* ═══ FOOTER ═══ */
footer {{
  padding:3rem 1.5rem; border-top:1px solid var(--border);
  text-align:center; color:var(--text3); font-size:0.85rem;
}}
footer .footer-grid {{
  max-width:1100px; margin:0 auto 2rem;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
  gap:2rem; text-align:left;
}}
footer h4 {{ color:var(--text); font-weight:600; margin-bottom:1rem; font-size:0.9rem; }}
footer a {{ display:block; color:var(--text2); font-size:0.85rem; padding:0.25rem 0; transition:color 0.2s; }}
footer a:hover {{ color:var(--text); }}
footer .copyright {{ border-top:1px solid var(--border); padding-top:2rem; }}

/* ═══ ANIMATIONS ═══ */
@keyframes fadeInUp {{
  from {{ opacity:0; transform:translateY(30px); }}
  to {{ opacity:1; transform:translateY(0); }}
}}
@keyframes pulse {{
  0%,100% {{ opacity:1; }}
  50% {{ opacity:0.5; }}
}}
.animate {{ animation:fadeInUp 0.6s ease forwards; }}
.animate-d1 {{ animation-delay:0.1s; }}
.animate-d2 {{ animation-delay:0.2s; }}
.animate-d3 {{ animation-delay:0.3s; }}
.animate-d4 {{ animation-delay:0.4s; }}

/* ═══ RESPONSIVE ═══ */
@media (max-width:768px) {{
  .section {{ padding:3rem 1rem; }}
  .hero {{ padding:5rem 1rem 3rem; min-height:auto; }}
  .pricing-grid {{ grid-template-columns:1fr; }}
  .pricing-card.featured {{ transform:none; }}
  .pricing-card.featured:hover {{ transform:translateY(-4px); }}
  .testimonials-grid {{ grid-template-columns:1fr; }}
  .hero-proof {{ flex-direction:column; align-items:center; gap:0.75rem; }}
}}
@media (max-width:480px) {{
  .hero-actions {{ flex-direction:column; align-items:stretch; }}
  .btn-primary,.btn-secondary {{ justify-content:center; }}
  nav .links {{ display:none; }}
}}
</style>
</head>
<body>

<!-- ═══════════ NAVBAR ═══════════ -->
<nav>
  <div class="nav-inner">
    <span class="logo">{title_niche}</span>
    <div class="links">
      <a href="#features">Recursos</a>
      <a href="#pricing">Precos</a>
      <a href="#testimonials">Depoimentos</a>
      <a href="#faq">FAQ</a>
    </div>
    <a href="#cta" class="nav-cta">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      Comecar
    </a>
    <button class="nav-toggle" onclick="this.classList.toggle('active')" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<!-- ═══════════ HERO ═══════════ -->
<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-content animate">
    <div class="hero-badge">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#a5b4fc" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
      {title_niche}
    </div>
    <h1>Domine <span>{niche}</span> em 2026</h1>
    <p>Sua plataforma completa para aprender e transformar resultados com {niche}. Metodologia comprovada por milhares de alunos que geram lucro e fazem dinheiro todos os meses. Aproveite nosso desconto especial e comece a crescer agora.</p>
    <div class="hero-actions">
      <a href="#cta" class="btn-primary">
        Comecar Agora
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
      <a href="#features" class="btn-secondary">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20"/></svg>
        Saiba Mais
      </a>
    </div>
    <img src="https://image.pollinations.ai/prompt/premium%20digital%20marketing%20dashboard%202026?width=1200&height=630&nologo=true" alt="Dashboard" style="width:100%;max-width:700px;border-radius:20px;margin:2rem auto;box-shadow:0 8px 40px rgba(0,0,0,0.4);display:block;" loading="lazy" />
    <div class="hero-proof">
      <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg> Mais de 10 mil alunos</span>
      <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> 4.9/5 estrelas</span>
      <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg> Resultados em 30 dias</span>
    </div>
  </div>
</section>

<!-- ═══════════ FEATURES ═══════════ -->
<section class="section" id="features">
  <div class="section-container">
    <div class="section-header">
      <h2>Recursos Principais</h2>
      <p>Tudo que voce precisa para dominar {niche} e alcancar resultados extraordinarios.</p>
    </div>
    <div class="features-grid">
      <div class="feature-card animate animate-d1">
        <div class="feature-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M12 2v20M2 12h20"/><path d="M12 2a10 10 0 010 20"/></svg>
        </div>
        <h3>Automacao Inteligente</h3>
        <p>Processos automatizados que funcionam 24/7 sem intervencao manual. Deixe o sistema trabalhar por voce.</p>
      </div>
      <div class="feature-card animate animate-d2">
        <div class="feature-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M3 3v18h18"/><path d="M7 16l4-8 4 4 4-6"/></svg>
        </div>
        <h3>Analytics em Tempo Real</h3>
        <p>Dados atualizados em tempo real sobre suas campanhas, conversoes e revenue. Decisoes baseadas em dados.</p>
      </div>
      <div class="feature-card animate animate-d3">
        <div class="feature-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <h3>Escalabilidade Total</h3>
        <p>Cresca sem limites. Suporta de centenas a milhares de campanhas rodando simultaneamente.</p>
      </div>
      <div class="feature-card animate animate-d4">
        <div class="feature-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M2 12h2l2 4 3-9 3 11 3-7 3 9 2-4h2"/></svg>
        </div>
        <h3>Multiplas Fontes de Renda</h3>
        <p>13 fontes de renda paralelas: Hotmart, Kiwify, Eduzz, Amazon, Shopee e mais. Diversificacao automatica.</p>
      </div>
      <div class="feature-card animate animate-d4">
        <div class="feature-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        </div>
        <h3>IA Generativa</h3>
        <p>Criacao de conteudo, imagens, audio e video com IA. Pipeline completo de midia integrado.</p>
      </div>
      <div class="feature-card animate animate-d4">
        <div class="feature-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.5"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 002 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
        </div>
        <h3>Workflow DAG Paralelo</h3>
        <p>31 workflows orquestrados com execucao paralela. Qualidade garantida por 7 camadas de validacao.</p>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ PRICING ═══════════ -->
<section class="section section-alt" id="pricing">
  <div class="section-container">
    <div class="section-header">
      <h2>Planos e Precos</h2>
      <p>Escolha o plano ideal para seu negocio de {niche}. Todos com 7 dias de garantia.</p>
    </div>
    <div class="pricing-grid">
      <div class="pricing-card animate animate-d1">
        <h3 class="pricing-name">Basico</h3>
        <div class="pricing-price">
          <span class="pricing-amount">R$ 47</span>
          <span class="pricing-period">/mes</span>
        </div>
        <ul class="pricing-features">
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Acesso basico</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> 1 nicho</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Suporte email</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> 7 dias garantia</li>
        </ul>
        <a href="#cta" class="pricing-cta">Comecar Gratis</a>
      </div>

      <div class="pricing-card featured animate animate-d2">
        <span class="pricing-badge">Mais Popular</span>
        <h3 class="pricing-name">Profissional</h3>
        <div class="pricing-price">
          <span class="pricing-amount">R$ 97</span>
          <span class="pricing-period">/mes</span>
        </div>
        <ul class="pricing-features">
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Acesso completo</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> 3 nichos</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Suporte prioritario</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Relatorios avancados</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> API inclusa</li>
        </ul>
        <a href="#cta" class="pricing-cta">Escolher Profissional</a>
      </div>

      <div class="pricing-card animate animate-d3">
        <h3 class="pricing-name">Enterprise</h3>
        <div class="pricing-price">
          <span class="pricing-amount">R$ 197</span>
          <span class="pricing-period">/mes</span>
        </div>
        <ul class="pricing-features">
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Tudo do Profissional</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Nichos ilimitados</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Suporte 24/7</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Gerente dedicado</li>
          <li><svg class="check" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> Customizacoes</li>
        </ul>
        <a href="#cta" class="pricing-cta">Falar com Vendas</a>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ TESTIMONIALS ═══════════ -->
<section class="section" id="testimonials">
  <div class="section-container">
    <div class="section-header">
      <h2>O Que Nossos Alunos Dizem</h2>
      <p>Historias reais de quem transformou sua vida com {niche}.</p>
    </div>
    <div class="testimonials-grid">
      <div class="testimonial-card animate animate-d1">
        <div class="testimonial-stars">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </div>
        <p class="testimonial-text">"Transformei meu negocio com {niche}! Em apenas 3 meses ja estava vendo resultados que nao esperava. Recomendo para todos que querem crescer."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">A</div>
          <div>
            <strong>Ana Silva</strong>
            <span>Empreendedora {niche}</span>
          </div>
        </div>
      </div>
      <div class="testimonial-card animate animate-d2">
        <div class="testimonial-stars">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </div>
        <p class="testimonial-text">"A plataforma e intuitiva e o suporte e incrivel. Consegui aprender e aplicar tudo, gerei lucro e meu dinheiro cresceu. Meus resultados quadruplicaram com a metodologia."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">C</div>
          <div>
            <strong>Carlos Oliveira</strong>
            <span>Analista de Marketing</span>
          </div>
        </div>
      </div>
      <div class="testimonial-card animate animate-d3">
        <div class="testimonial-stars">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </div>
        <p class="testimonial-text">"Comecei do zero e hoje faturo mais de R$ 10k/mes gracas a metodologia. O diferencial e o acompanhamento proximo."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">M</div>
          <div>
            <strong>Mariana Costa</strong>
            <span>Produtora Digital</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ FAQ ═══════════ -->
<section class="section section-alt" id="faq">
  <div class="section-container">
    <div class="section-header">
      <h2>Perguntas Frequentes</h2>
      <p>Tire suas duvidas sobre {niche}.</p>
    </div>
    <div class="faq-list">
      <div class="faq-item">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>O que e {niche}?</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <div class="faq-answer"><p>{niche.title()} e uma metodologia comprovada que ajuda milhares de pessoas a transformarem seus resultados. Com nossa plataforma, voce aprende na pratica.</p></div>
      </div>
      <div class="faq-item">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>Preciso de experiencia?</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <div class="faq-answer"><p>Nao! Nosso sistema foi desenvolvido para iniciantes absolutos. Voce comeca do zero e avanca no seu ritmo com suporte completo.</p></div>
      </div>
      <div class="faq-item">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>Quanto tempo ate ver resultados?</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <div class="faq-answer"><p>Alunos dedicados comecam a ver resultados nas primeiras semanas. O tempo varia conforme seu foco e consistencia.</p></div>
      </div>
      <div class="faq-item">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>Qual a garantia?</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <div class="faq-answer"><p>Oferecemos 7 dias de garantia incondicional. Se nao ficar satisfeito, devolvemos 100% do seu investimento.</p></div>
      </div>
      <div class="faq-item">
        <button class="faq-question" onclick="toggleFaq(this)">
          <span>Funciona para qualquer nicho?</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <div class="faq-answer"><p>Sim! Nossa metodologia e adaptavel para qualquer nicho ou mercado. Ja temos alunos em mais de 50 areas diferentes.</p></div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ CTA ═══════════ -->
<section class="section" id="cta">
  <div class="section-container">
    <div class="cta-banner">
      <h2>Pronto para Comecar?</h2>
      <p>Junte-se a milhares de alunos que transformaram suas vidas com {niche}. Sua transformacao comeca hoje.</p>
      <a href="#" class="btn-primary" style="font-size:1.1rem;padding:1.1rem 3rem;">
        Quero Participar
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
    </div>
  </div>
</section>

<!-- ═══════════ FOOTER ═══════════ -->
<footer>
  <div class="footer-grid">
    <div>
      <h4>{title_niche}</h4>
      <p style="color:var(--text3);font-size:0.85rem;">Sua plataforma completa de {niche}.</p>
    </div>
    <div>
      <h4>Produto</h4>
      <a href="#features">Recursos</a>
      <a href="#pricing">Precos</a>
      <a href="#faq">FAQ</a>
    </div>
    <div>
      <h4>Empresa</h4>
      <a href="#">Sobre</a>
      <a href="#">Blog</a>
      <a href="#">Carreiras</a>
    </div>
    <div>
      <h4>Suporte</h4>
      <a href="#">Central de Ajuda</a>
      <a href="#">Contato</a>
      <a href="#">Termos de Uso</a>
    </div>
  </div>
  <div class="copyright">
    &copy; 2026 {title_niche}. Todos os direitos reservados. Lyzer Labs — Campaign Autopilot.
  </div>
</footer>

<script>
function toggleFaq(btn) {{
  btn.classList.toggle('active');
  var answer = btn.nextElementSibling;
  if (answer.style.maxHeight) {{
    answer.style.maxHeight = null;
  }} else {{
    answer.style.maxHeight = answer.scrollHeight + 'px';
  }}
}}
</script>
</body>
</html>"""
