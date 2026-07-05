"""Artifact Generator — Core engine for visual artifact creation.

Gera artefatos visuais (HTML, CSS, templates) a partir de especificações
de design system e dados de campanha. Bridge entre Open Design e o ecossistema
Lyzer Labs / Campaign Autopilot.
"""

from __future__ import annotations

import html
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from .color_palette import (
    LYZER_COLORS,
    LYZER_GRADIENTS,
    LYZER_SHADOWS,
    LYZER_RADIUS,
)


# ── Types ─────────────────────────────────────────────────────


class ArtifactType(str, Enum):
    LANDING_PAGE = "landing_page"
    DASHBOARD = "dashboard"
    EMAIL = "email"
    PRESENTATION = "presentation"
    REPORT = "report"
    SOCIAL_CARD = "social_card"
    AD_CREATIVE = "ad_creative"


@dataclass
class ArtifactSpec:
    """Specification for an artifact to generate."""

    type: ArtifactType
    title: str
    description: str = ""
    campaign_data: Dict[str, Any] = field(default_factory=dict)
    design_system_name: str = "lyzer-labs"
    template_name: str = "default"
    output_format: str = "html"  # html, md, json
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtifactResult:
    """Result of artifact generation."""

    spec: ArtifactSpec
    content: str
    file_path: Optional[str] = None
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    size_bytes: int = 0
    errors: List[str] = field(default_factory=list)
    success: bool = True


@dataclass
class RenderTemplate:
    """HTML/CSS template with named slots."""

    name: str
    html_template: str
    css_template: str = ""
    js_template: str = ""
    slots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Component Renderer ────────────────────────────────────────


class ComponentRenderer:
    """Renders individual UI components from DesignSystem specs."""

    def render_button(
        self,
        text: str,
        variant: str = "primary",
        size: str = "md",
        full_width: bool = False,
        href: Optional[str] = None,
        **kwargs,
    ) -> str:
        classes = f"lyzer-btn lyzer-btn-{variant} lyzer-btn-{size}"
        if full_width:
            classes += " lyzer-btn-full"
        safe_text = html.escape(text)
        if href:
            return f'<a href="{html.escape(href)}" class="{classes}">{safe_text}</a>'
        return f'<button class="{classes}">{safe_text}</button>'

    def render_card(
        self, content: str, variant: str = "elevated", padding: str = "lg", **kwargs
    ) -> str:
        classes = f"lyzer-card lyzer-card-{variant} lyzer-card-padding-{padding}"
        return f'<div class="{classes}">{content}</div>'

    def render_metric_card(
        self,
        label: str,
        value: str,
        change: Optional[str] = None,
        trend: str = "neutral",
        icon: Optional[str] = None,
    ) -> str:
        trend_class = f"lyzer-trend-{trend}"
        icon_html = f'<span class="lyzer-metric-icon">{icon}</span>' if icon else ""
        change_html = (
            f'<span class="lyzer-metric-change {trend_class}">{change}</span>'
            if change
            else ""
        )
        return f"""<div class="lyzer-metric-card">
          {icon_html}
          <div class="lyzer-metric-label">{html.escape(label)}</div>
          <div class="lyzer-metric-value">{value}</div>
          {change_html}
        </div>"""

    def render_hero(
        self,
        headline: str,
        subtitle: Optional[str] = None,
        cta_text: str = "Get Started",
        cta_link: str = "#",
        secondary_cta: Optional[str] = None,
        secondary_link: Optional[str] = None,
    ) -> str:
        sub_html = (
            f'<p class="lyzer-hero-subtitle">{html.escape(subtitle)}</p>'
            if subtitle
            else ""
        )
        secondary_html = ""
        if secondary_cta and secondary_link:
            secondary_html = (
                f'<a href="{html.escape(secondary_link)}" '
                f'class="lyzer-btn lyzer-btn-secondary lyzer-btn-lg">'
                f"{html.escape(secondary_cta)}</a>"
            )
        return f'''<section class="lyzer-hero">
          <div class="lyzer-hero-content">
            <h1 class="lyzer-hero-headline">{html.escape(headline)}</h1>
            {sub_html}
            <div class="lyzer-hero-actions">
              <a href="{html.escape(cta_link)}" class="lyzer-btn lyzer-btn-accent lyzer-btn-lg">{html.escape(cta_text)}</a>
              {secondary_html}
            </div>
          </div>
        </section>'''

    def render_pricing_card(
        self,
        tier: str,
        price: str,
        features: List[str],
        cta_text: str = "Choose Plan",
        period: str = "/month",
        featured: bool = False,
    ) -> str:
        featured_class = " lyzer-pricing-featured" if featured else ""
        features_html = "\n".join(
            f'<li class="lyzer-pricing-feature">✓ {html.escape(f)}</li>'
            for f in features
        )
        return f"""<div class="lyzer-pricing-card{featured_class}">
          <div class="lyzer-pricing-header">
            <h3 class="lyzer-pricing-tier">{html.escape(tier)}</h3>
            <div class="lyzer-pricing-price">
              <span class="lyzer-pricing-amount">{price}</span>
              <span class="lyzer-pricing-period">{period}</span>
            </div>
          </div>
          <ul class="lyzer-pricing-features">{features_html}</ul>
          <a href="#" class="lyzer-btn lyzer-btn-primary lyzer-btn-lg lyzer-btn-full">{html.escape(cta_text)}</a>
        </div>"""

    def render_section(
        self,
        title: str,
        content: str,
        background: str = "default",
        container_class: str = "",
    ) -> str:
        section_class = f"lyzer-section lyzer-section-{background}"
        return f'''<section class="{section_class}">
          <div class="lyzer-container {container_class}">
            <h2 class="lyzer-section-title">{html.escape(title)}</h2>
            {content}
          </div>
        </section>'''

    def render_footer(
        self, content: str, links: Optional[List[Dict[str, str]]] = None
    ) -> str:
        links_html = ""
        if links:
            items = "".join(
                f'<a href="{html.escape(l["url"])}" class="lyzer-footer-link">{html.escape(l["label"])}</a>'
                for l in links
            )
            links_html = f'<nav class="lyzer-footer-nav">{items}</nav>'
        return f"""<footer class="lyzer-footer">
          <div class="lyzer-container">
            {links_html}
            <div class="lyzer-footer-content">{content}</div>
            <div class="lyzer-footer-copyright">© {datetime.utcnow().year} Lyzer Labs. All rights reserved.</div>
          </div>
        </footer>"""


# ── Layout Renderer ───────────────────────────────────────────


class LayoutRenderer:
    """Renders layout grids from LayoutSpec."""

    def render_grid(
        self,
        items: List[str],
        columns: int = 3,
        gap: str = "1.5rem",
        responsive: bool = True,
    ) -> str:
        items_html = "\n".join(
            f'<div class="lyzer-grid-item">{item}</div>' for item in items
        )
        classes = f"lyzer-grid lyzer-grid-cols-{columns}"
        if responsive:
            classes += " lyzer-grid-responsive"
        return f'<div class="{classes}" style="gap: {gap};">{items_html}</div>'

    def render_sidebar_layout(
        self, main: str, sidebar: str, sidebar_position: str = "right"
    ) -> str:
        classes = "lyzer-sidebar-layout"
        if sidebar_position == "left":
            return (
                f'<div class="{classes}">'
                f'<aside class="lyzer-sidebar">{sidebar}</aside>'
                f'<main class="lyzer-main">{main}</main></div>'
            )
        return (
            f'<div class="{classes}">'
            f'<main class="lyzer-main">{main}</main>'
            f'<aside class="lyzer-sidebar">{sidebar}</aside></div>'
        )

    def render_container(self, content: str, max_width: str = "1200px") -> str:
        return f'<div class="lyzer-container" style="max-width: {max_width}; margin: 0 auto; padding: 0 1rem;">{content}</div>'


# ── Artifact Generator Engine ─────────────────────────────────


class ArtifactGenerator:
    """Core generator — transforms specs into rendered artifacts."""

    def __init__(self):
        self.component_renderer = ComponentRenderer()
        self.layout_renderer = LayoutRenderer()
        self._lock = threading.Lock()
        self._output_dir: Optional[str] = None
        self._templates: Dict[str, RenderTemplate] = {}

    def set_output_dir(self, path: str) -> None:
        self._output_dir = path
        Path(path).mkdir(parents=True, exist_ok=True)

    def register_template(self, template: RenderTemplate) -> None:
        self._templates[template.name] = template

    def _load_base_styles(self) -> str:
        """Carrega CSS base do design system."""
        from .color_palette import (
            LYZER_COLORS,
            LYZER_RADIUS,
        )

        primary = LYZER_COLORS.get("primary-500", "#7c2dff")
        bg_dark = LYZER_COLORS.get("bg-dark", "#0a0a0f")
        bg_card = LYZER_COLORS.get("bg-card", "#12121f")
        bg_elevated = LYZER_COLORS.get("bg-elevated", "#1a1a2e")
        text_primary = LYZER_COLORS.get("text-primary", "#f0f0ff")
        text_secondary = LYZER_COLORS.get("text-secondary", "#a0a0c0")
        accent = LYZER_COLORS.get("accent-500", "#f0b400")
        secondary = LYZER_COLORS.get("secondary-500", "#00aaff")
        border_color = LYZER_COLORS.get("border", "#2a2a3e")
        error_col = LYZER_COLORS.get("error", "#ff1744")
        success_col = LYZER_COLORS.get("success", "#00e676")
        glow_shadow = LYZER_SHADOWS.get("glow", "")

        return f"""/* ── Lyzer Labs Design System — Base Styles ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: {bg_dark}; color: {text_primary};
  line-height: 1.5; -webkit-font-smoothing: antialiased;
}}
h1, h2, h3, h4, h5, h6 {{ font-family: 'Space Grotesk', 'Inter', sans-serif; font-weight: 700; line-height: 1.1; }}
a {{ color: {secondary}; text-decoration: none; transition: color 0.2s; }}
a:hover {{ color: {accent}; }}
img {{ max-width: 100%; height: auto; }}
code, pre {{ font-family: 'JetBrains Mono', 'Fira Code', monospace; }}

/* ── Container ── */
.lyzer-container {{ width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 1rem; }}

/* ── Buttons ── */
.lyzer-btn {{
  display: inline-flex; align-items: center; justify-content: center;
  padding: 0.75rem 1.5rem; border-radius: {LYZER_RADIUS.get("lg", "0.75rem")};
  font-weight: 600; font-size: 0.875rem; cursor: pointer;
  border: none; transition: all 0.2s ease;
  text-decoration: none !important;
}}
.lyzer-btn-primary {{ background: {primary}; color: white; }}
.lyzer-btn-primary:hover {{ background: {primary}dd; transform: translateY(-1px); box-shadow: {glow_shadow}; }}
.lyzer-btn-secondary {{ background: transparent; color: {text_primary}; border: 1px solid {border_color}; }}
.lyzer-btn-secondary:hover {{ border-color: {primary}; color: {primary}; }}
.lyzer-btn-accent {{ background: {accent}; color: #000; }}
.lyzer-btn-accent:hover {{ background: {accent}dd; transform: translateY(-1px); }}
.lyzer-btn-ghost {{ background: transparent; color: {text_secondary}; }}
.lyzer-btn-ghost:hover {{ color: {text_primary}; background: {bg_elevated}; }}
.lyzer-btn-sm {{ padding: 0.5rem 1rem; font-size: 0.75rem; }}
.lyzer-btn-lg {{ padding: 1rem 2rem; font-size: 1rem; }}
.lyzer-btn-full {{ width: 100%; }}

/* ── Cards ── */
.lyzer-card {{
  background: {bg_card}; border: 1px solid {border_color};
  border-radius: {LYZER_RADIUS.get("xl", "1rem")}; overflow: hidden;
  transition: all 0.3s ease;
}}
.lyzer-card-elevated {{ box-shadow: 0 4px 6px rgba(0,0,0,0.4); }}
.lyzer-card-glass {{ background: {bg_card}cc; backdrop-filter: blur(12px); border: 1px solid {border_color}88; }}
.lyzer-card:hover {{ border-color: {primary}44; transform: translateY(-2px); }}
.lyzer-card-padding-lg {{ padding: 1.5rem; }}
.lyzer-card-padding-md {{ padding: 1rem; }}

/* ── Hero Section ── */
.lyzer-hero {{
  min-height: 80vh; display: flex; align-items: center;
  background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 50%, #1a0a2e 100%);
  position: relative; overflow: hidden;
}}
.lyzer-hero::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 50% 0%, {primary}22 0%, transparent 70%);
}}
.lyzer-hero-content {{ position: relative; z-index: 1; max-width: 800px; margin: 0 auto; padding: 2rem; text-align: center; }}
.lyzer-hero-headline {{ font-size: clamp(2.5rem, 5vw, 4.5rem); margin-bottom: 1.5rem; background: linear-gradient(135deg, {text_primary} 0%, {secondary} 50%, {primary} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
.lyzer-hero-subtitle {{ font-size: 1.25rem; color: {text_secondary}; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.75; }}
.lyzer-hero-actions {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}

/* ── Sections ── */
.lyzer-section {{ padding: 4rem 0; }}
.lyzer-section-dark {{ background: {bg_card}; }}
.lyzer-section-gradient {{ background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%); }}
.lyzer-section-title {{ font-size: 2.25rem; text-align: center; margin-bottom: 3rem; }}

/* ── Grid ── */
.lyzer-grid {{ display: grid; gap: 1.5rem; }}
.lyzer-grid-cols-1 {{ grid-template-columns: 1fr; }}
.lyzer-grid-cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
.lyzer-grid-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.lyzer-grid-cols-4 {{ grid-template-columns: repeat(4, 1fr); }}
@media (max-width: 768px) {{ .lyzer-grid-responsive {{ grid-template-columns: 1fr !important; }} }}
@media (min-width: 769px) and (max-width: 1024px) {{ .lyzer-grid-responsive.lyzer-grid-cols-3 {{ grid-template-columns: repeat(2, 1fr); }} }}
.lyzer-grid-item {{ min-width: 0; }}

/* ── Sidebar Layout ── */
.lyzer-sidebar-layout {{ display: grid; grid-template-columns: 1fr 320px; gap: 2rem; }}
@media (max-width: 768px) {{ .lyzer-sidebar-layout {{ grid-template-columns: 1fr; }} }}

/* ── Metric Card ── */
.lyzer-metric-card {{ background: {bg_card}; border: 1px solid {border_color}; border-radius: {LYZER_RADIUS.get("lg", "0.75rem")}; padding: 1.5rem; }}
.lyzer-metric-label {{ font-size: 0.875rem; color: {text_secondary}; margin-bottom: 0.5rem; }}
.lyzer-metric-value {{ font-size: 2.5rem; font-weight: 800; font-family: 'Space Grotesk', sans-serif; }}
.lyzer-metric-change {{ font-size: 0.875rem; font-weight: 600; }}
.lyzer-trend-up {{ color: {success_col}; }}
.lyzer-trend-down {{ color: {error_col}; }}
.lyzer-trend-neutral {{ color: {text_secondary}; }}
.lyzer-metric-icon {{ font-size: 1.5rem; margin-bottom: 0.5rem; display: block; }}

/* ── Pricing ── */
.lyzer-pricing-card {{
  background: {bg_card}; border: 1px solid {border_color};
  border-radius: {LYZER_RADIUS.get("xl", "1rem")}; padding: 2rem;
  display: flex; flex-direction: column; gap: 1.5rem;
  transition: all 0.3s ease; position: relative;
}}
.lyzer-pricing-featured {{
  border-color: {primary}; box-shadow: 0 0 30px {primary}33;
  transform: scale(1.02);
}}
.lyzer-pricing-tier {{ font-size: 1.25rem; color: {text_secondary}; }}
.lyzer-pricing-price {{ display: flex; align-items: baseline; gap: 0.25rem; }}
.lyzer-pricing-amount {{ font-size: 3rem; font-weight: 800; }}
.lyzer-pricing-period {{ color: {text_secondary}; }}
.lyzer-pricing-features {{ list-style: none; display: flex; flex-direction: column; gap: 0.75rem; }}
.lyzer-pricing-feature {{ color: {text_secondary}; }}

/* ── Footer ── */
.lyzer-footer {{
  border-top: 1px solid {border_color}; padding: 3rem 0; margin-top: 4rem;
  text-align: center; color: {text_secondary}; font-size: 0.875rem;
}}
.lyzer-footer-nav {{ display: flex; justify-content: center; gap: 2rem; margin-bottom: 1.5rem; }}
.lyzer-footer-link {{ color: {text_secondary}; }}
.lyzer-footer-link:hover {{ color: {primary}; }}

/* ── Navigation ── */
.lyzer-nav {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 2rem; background: {bg_card}cc; backdrop-filter: blur(12px);
  border-bottom: 1px solid {border_color}; position: sticky; top: 0; z-index: 100;
}}
.lyzer-nav-logo {{ font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 800; color: {text_primary}; }}
.lyzer-nav-logo span {{ color: {primary}; }}
.lyzer-nav-links {{ display: flex; gap: 2rem; align-items: center; }}
@media (max-width: 768px) {{ .lyzer-nav-links {{ display: none; }} }}

/* ── Dashboard ── */
.lyzer-dashboard {{ padding: 2rem; }}
.lyzer-dashboard-header {{ margin-bottom: 2rem; }}
.lyzer-dashboard-title {{ font-size: 2rem; }}
.lyzer-dashboard-subtitle {{ color: {text_secondary}; }}
.lyzer-kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
.lyzer-chart-container {{ background: {bg_card}; border: 1px solid {border_color}; border-radius: {LYZER_RADIUS.get("lg", "0.75rem")}; padding: 1.5rem; margin-bottom: 1.5rem; }}
.lyzer-chart-title {{ font-size: 1rem; font-weight: 600; margin-bottom: 1rem; }}
.lyzer-table {{ width: 100%; border-collapse: collapse; }}
.lyzer-table th {{ text-align: left; padding: 0.75rem; color: {text_secondary}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid {border_color}; }}
.lyzer-table td {{ padding: 0.75rem; border-bottom: 1px solid {border_color}44; }}

/* ── Email ── */
.lyzer-email {{ font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; background: {bg_dark}; }}
.lyzer-email-header {{ padding: 2rem; text-align: center; border-bottom: 1px solid {border_color}; }}
.lyzer-email-body {{ padding: 2rem; }}
.lyzer-email-footer {{ padding: 1.5rem; text-align: center; color: {text_secondary}; font-size: 0.75rem; border-top: 1px solid {border_color}; }}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .lyzer-hero-headline {{ font-size: 2rem; }}
  .lyzer-hero {{ min-height: 60vh; }}
  .lyzer-section {{ padding: 2rem 0; }}
  .lyzer-dashboard {{ padding: 1rem; }}
}}
"""

    def generate_artifact(
        self, spec: ArtifactSpec, output_dir: Optional[str] = None
    ) -> ArtifactResult:
        """Generate an artifact from spec."""
        try:
            out_dir = output_dir or self._output_dir or "output"
            base_styles = self._load_base_styles()

            if spec.type == ArtifactType.LANDING_PAGE:
                content = self._generate_landing_page(spec, base_styles)
                file_ext = ".html"
            elif spec.type == ArtifactType.DASHBOARD:
                content = self._generate_dashboard(spec, base_styles)
                file_ext = ".html"
            elif spec.type == ArtifactType.EMAIL:
                content = self._generate_email(spec, base_styles)
                file_ext = ".html"
            elif spec.type == ArtifactType.SOCIAL_CARD:
                content = self._generate_social_card(spec)
                file_ext = ".html"
            elif spec.type == ArtifactType.REPORT:
                content = self._generate_report(spec)
                file_ext = ".html"
            else:
                content = self._generate_generic(spec, base_styles)
                file_ext = ".html"

            safe_name = spec.title.lower().replace(" ", "_").replace("/", "_")
            filename = f"{safe_name}_{spec.type.value}{file_ext}"
            filepath = Path(out_dir) / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)

            return ArtifactResult(
                spec=spec,
                content=content,
                file_path=str(filepath),
                size_bytes=len(content.encode()),
            )
        except Exception as e:
            return ArtifactResult(
                spec=spec,
                content="",
                errors=[str(e)],
                success=False,
            )

    def _generate_landing_page(self, spec: ArtifactSpec, css: str) -> str:
        data = spec.campaign_data
        headline = data.get("headline", spec.title)
        subtitle = data.get("subtitle", spec.description)
        cta_text = data.get("cta_text", "Comece Agora")
        cta_link = data.get("cta_link", "#")

        features = data.get("features", [])
        features_html = ""
        if features:
            items = "".join(
                f'<div class="lyzer-card lyzer-card-elevated lyzer-card-padding-lg">'
                f"<h3>{html.escape(f.get('title', ''))}</h3>"
                f'<p style="color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")}">{html.escape(f.get("description", ""))}</p>'
                f"</div>"
                for f in features
            )
            features_html = f'<div class="lyzer-grid lyzer-grid-cols-3 lyzer-grid-responsive">{items}</div>'

        pricing_tiers = data.get("pricing", [])
        pricing_html = ""
        if pricing_tiers:
            renderer = self.component_renderer
            cards = "".join(
                renderer.render_pricing_card(**tier) for tier in pricing_tiers
            )
            pricing_html = cards

        testimonials = data.get("testimonials", [])
        testimonials_html = ""
        if testimonials:
            items = "".join(
                f'<div class="lyzer-card lyzer-card-glass lyzer-card-padding-lg">'
                f'<p style="font-style: italic; color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")}">"{html.escape(t.get("quote", ""))}"</p>'
                f'<p style="margin-top: 1rem; font-weight: 600;">— {html.escape(t.get("author", ""))}</p>'
                f"</div>"
                for t in testimonials
            )
            testimonials_html = f'<div class="lyzer-grid lyzer-grid-cols-3 lyzer-grid-responsive">{items}</div>'

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(spec.title)} — Lyzer Labs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
  <style>{css}</style>
</head>
<body>
  <nav class="lyzer-nav">
    <div class="lyzer-nav-logo">Lyzer <span>Labs</span></div>
    <div class="lyzer-nav-links">
      <a href="#features">Recursos</a>
      <a href="#pricing">Preços</a>
      <a href="#testimonials">Depoimentos</a>
      <a href="{html.escape(cta_link)}" class="lyzer-btn lyzer-btn-primary lyzer-btn-sm">{html.escape(cta_text)}</a>
    </div>
  </nav>

  <section class="lyzer-hero">
    <div class="lyzer-hero-content">
      <h1 class="lyzer-hero-headline">{html.escape(headline)}</h1>
      <p class="lyzer-hero-subtitle">{html.escape(subtitle)}</p>
      <div class="lyzer-hero-actions">
        <a href="{html.escape(cta_link)}" class="lyzer-btn lyzer-btn-accent lyzer-btn-lg">{html.escape(cta_text)}</a>
        <a href="#features" class="lyzer-btn lyzer-btn-secondary lyzer-btn-lg">Saiba Mais</a>
      </div>
    </div>
  </section>

  {f'''<section id="features" class="lyzer-section lyzer-section-dark"><div class="lyzer-container"><h2 class="lyzer-section-title">Recursos</h2>{features_html}</div></section>''' if features_html else ""}

  {f'''<section id="pricing" class="lyzer-section"><div class="lyzer-container"><h2 class="lyzer-section-title">Preços</h2><div class="lyzer-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">{pricing_html}</div></div></section>''' if pricing_html else ""}

  {f'''<section id="testimonials" class="lyzer-section lyzer-section-dark"><div class="lyzer-container"><h2 class="lyzer-section-title">Depoimentos</h2>{testimonials_html}</div></section>''' if testimonials_html else ""}

  <footer class="lyzer-footer">
    <div class="lyzer-container">
      <p>&copy; {datetime.utcnow().year} Lyzer Labs. Todos os direitos reservados.</p>
    </div>
  </footer>
</body>
</html>"""

    def _generate_dashboard(self, spec: ArtifactSpec, css: str) -> str:
        data = spec.campaign_data
        metrics = data.get("metrics", [])
        charts = data.get("charts", [])
        table_data = data.get("table", [])

        metrics_html = "".join(
            f'<div class="lyzer-metric-card"><div class="lyzer-metric-label">{html.escape(m.get("label", ""))}</div><div class="lyzer-metric-value">{m.get("value", "")}</div></div>'
            for m in metrics
        )

        charts_html = ""
        for c in charts:
            if c.get("type") == "bar":
                bars = "".join(
                    f'<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">'
                    f'<span style="width: 80px; font-size: 0.875rem; color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")};">{html.escape(b.get("label", ""))}</span>'
                    f'<div style="flex: 1; height: 24px; background: {LYZER_COLORS.get("bg-elevated", "#1a1a2e")}; border-radius: 12px; overflow: hidden;">'
                    f'<div style="width: {b.get("value", 0)}%; height: 100%; background: linear-gradient(90deg, {LYZER_COLORS.get("primary-500", "#7c2dff")}, {LYZER_COLORS.get("secondary-500", "#00aaff")}); border-radius: 12px;"></div>'
                    f"</div></div>"
                    for b in c.get("bars", [])
                )
                charts_html += f'<div class="lyzer-chart-container"><h3 class="lyzer-chart-title">{html.escape(c.get("title", ""))}</h3>{bars}</div>'

        table_html = ""
        if table_data:
            headers = table_data[0].keys() if table_data else []
            header_cells = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
            rows = "".join(
                f"<tr>{''.join(f'<td>{html.escape(str(v))}</td>' for v in row.values())}</tr>"
                for row in table_data
            )
            table_html = f'<div class="lyzer-chart-container"><table class="lyzer-table"><thead><tr>{header_cells}</tr></thead><tbody>{rows}</tbody></table></div>'

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard — {html.escape(spec.title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
  <style>{css}</style>
</head>
<body>
  <nav class="lyzer-nav">
    <div class="lyzer-nav-logo">Lyzer <span>Labs</span></div>
    <div class="lyzer-nav-links"><span style="color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")};">Dashboard</span></div>
  </nav>
  <div class="lyzer-dashboard">
    <div class="lyzer-dashboard-header">
      <h1 class="lyzer-dashboard-title">{html.escape(spec.title)}</h1>
      <p class="lyzer-dashboard-subtitle">{html.escape(spec.description)}</p>
    </div>

    {f'''<div class="lyzer-kpi-row">{metrics_html}</div>''' if metrics_html else ""}

    {charts_html}

    {table_html}
  </div>
</body>
</html>"""

    def _generate_email(self, spec: ArtifactSpec, css: str) -> str:
        data = spec.campaign_data
        body_content = data.get("body", spec.description)
        cta_text = data.get("cta_text", "Acessar")
        cta_link = data.get("cta_link", "#")
        footer_text = data.get(
            "footer", "Você recebeu este email porque se inscreveu no Lyzer Labs."
        )

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>{html.escape(spec.title)}</title></head>
<body class="lyzer-email" style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; background: {LYZER_COLORS.get("bg-dark", "#0a0a0f")}; color: {LYZER_COLORS.get("text-primary", "#f0f0ff")};">
  <div class="lyzer-email-header" style="padding: 2rem; text-align: center; border-bottom: 1px solid {LYZER_COLORS.get("border", "#2a2a3e")};">
    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem;">Lyzer <span style="color: {LYZER_COLORS.get("primary-500", "#7c2dff")};">Labs</span></h2>
  </div>
  <div class="lyzer-email-body" style="padding: 2rem;">
    <h1 style="font-family: 'Space Grotesk', sans-serif; margin-bottom: 1rem;">{html.escape(spec.title)}</h1>
    <div style="line-height: 1.75; color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")};">{body_content}</div>
    <div style="margin-top: 2rem; text-align: center;">
      <a href="{html.escape(cta_link)}" style="display: inline-block; padding: 1rem 2rem; background: {LYZER_COLORS.get("primary-500", "#7c2dff")}; color: white; text-decoration: none; border-radius: {LYZER_RADIUS.get("lg", "0.75rem")}; font-weight: 600;">{html.escape(cta_text)}</a>
    </div>
  </div>
  <div class="lyzer-email-footer" style="padding: 1.5rem; text-align: center; color: {LYZER_COLORS.get("text-muted", "#606080")}; font-size: 0.75rem; border-top: 1px solid {LYZER_COLORS.get("border", "#2a2a3e")};">
    {html.escape(footer_text)}
  </div>
</body>
</html>"""

    def _generate_social_card(self, spec: ArtifactSpec) -> str:
        data = spec.campaign_data
        title = data.get("title", spec.title)
        description = data.get("description", spec.description)
        gradient = LYZER_GRADIENTS.get(
            "quantum", "linear-gradient(135deg, #7c2dff, #00aaff)"
        )

        return f"""<div style="width: 1200px; height: 630px; display: flex; flex-direction: column; justify-content: center; align-items: center; background: {gradient}; font-family: 'Inter', sans-serif; color: white; text-align: center; padding: 4rem;">
  <h1 style="font-size: 4rem; font-weight: 800; margin-bottom: 1rem; max-width: 900px;">{html.escape(title)}</h1>
  <p style="font-size: 1.5rem; opacity: 0.9; max-width: 700px;">{html.escape(description)}</p>
  <div style="margin-top: 2rem; font-size: 1rem; opacity: 0.7;">Lyzer Labs</div>
</div>"""

    def _generate_report(self, spec: ArtifactSpec) -> str:
        data = spec.campaign_data
        sections = data.get("sections", [])
        sections_html = ""
        for s in sections:
            sections_html += f"""<section style="margin-bottom: 2rem;">
              <h2 style="font-family: 'Space Grotesk', sans-serif; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid {LYZER_COLORS.get("border", "#2a2a3e")};">{html.escape(s.get("title", ""))}</h2>
              <div style="line-height: 1.75; color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")};">{s.get("content", "")}</div>
            </section>"""
        return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{html.escape(spec.title)}</title></head>
        <body style="font-family: 'Inter', sans-serif; background: {LYZER_COLORS.get("bg-dark", "#0a0a0f")}; color: {LYZER_COLORS.get("text-primary", "#f0f0ff")}; max-width: 800px; margin: 0 auto; padding: 2rem;">
          <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; margin-bottom: 0.5rem;">{html.escape(spec.title)}</h1>
          <p style="color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")}; margin-bottom: 2rem;">{html.escape(spec.description)}</p>
          {sections_html}
        </body></html>"""

    def _generate_generic(self, spec: ArtifactSpec, css: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(spec.title)}</title><style>{css}</style>
</head>
<body>
  <nav class="lyzer-nav">
    <div class="lyzer-nav-logo">Lyzer <span>Labs</span></div>
  </nav>
  <div class="lyzer-container" style="padding: 4rem 1rem;">
    <h1>{html.escape(spec.title)}</h1>
    <p style="color: {LYZER_COLORS.get("text-secondary", "#a0a0c0")};">{html.escape(spec.description)}</p>
    <pre style="background: {LYZER_COLORS.get("bg-card", "#12121f")}; padding: 1.5rem; border-radius: 0.75rem; margin-top: 2rem; overflow-x: auto;"><code>{html.escape(json.dumps(spec.campaign_data, indent=2))}</code></pre>
  </div>
</body>
</html>"""
