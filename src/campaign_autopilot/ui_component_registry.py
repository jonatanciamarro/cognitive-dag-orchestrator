"""UI Component Registry — 21st.dev-style component system for Campaign Autopilot.

Registro de componentes UI reutilizáveis, estilo 21st.dev.
Cada componente é um artefato HTML/CSS/JS autocontido com design system tokens.

Ponytail: stdlib-only, SQLite persistence, JSON serializable.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any


class ComponentCategory(Enum):
    """Categorias de componentes UI estilo 21st.dev."""

    HERO = "hero"
    NAVBAR = "navbar"
    CARD = "card"
    FORM = "form"
    BUTTON = "button"
    MODAL = "modal"
    SECTION = "section"
    FOOTER = "footer"
    TESTIMONIAL = "testimonial"
    PRICING = "pricing"
    FEATURES = "features"
    CTA = "cta"
    FAQ = "faq"
    BLOG = "blog"
    DASHBOARD = "dashboard"
    CHART = "chart"
    TABLE = "table"
    LIST = "list"
    BADGE = "badge"
    AVATAR = "avatar"


@dataclass
class ComponentDefinition:
    """Definição completa de um componente UI."""

    component_id: str
    name: str
    category: ComponentCategory
    description: str
    tags: list[str]
    html_template: str
    css_variables: dict[str, str]
    design_tokens: dict[str, str]
    variants: list[dict[str, Any]]
    dependencies: list[str]
    preview_image: str = ""
    version: str = "1.0.0"
    author: str = "Lyzer Labs"
    created_at: float = 0.0
    updated_at: float = 0.0
    usage_count: int = 0
    quality_score: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def render(self, **kwargs) -> str:
        """Render the component HTML with given parameters."""
        rendered = self.html_template
        for key, value in kwargs.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ComponentVariant:
    """Uma variação de componente (ex: botão primário vs secundário)."""

    variant_id: str
    name: str
    description: str
    changes: dict[str, str]  # CSS variable overrides
    preview_image: str = ""


# ── Design System Tokens (21st.dev inspired) ────────────────

DESIGN_TOKENS_21ST = {
    # Colors
    "--bg-primary": "#0a0a0f",
    "--bg-secondary": "#14141f",
    "--bg-card": "#1a1a2e",
    "--bg-elevated": "#1f1f35",
    "--text-primary": "#f0f0f5",
    "--text-secondary": "#a0a0b8",
    "--text-muted": "#6b6b80",
    "--accent": "#6366f1",
    "--accent-hover": "#818cf8",
    "--accent-muted": "rgba(99, 102, 241, 0.15)",
    "--success": "#22c55e",
    "--warning": "#f59e0b",
    "--error": "#ef4444",
    "--border": "rgba(255,255,255,0.08)",
    "--border-hover": "rgba(255,255,255,0.15)",
    "--radius-sm": "6px",
    "--radius-md": "10px",
    "--radius-lg": "16px",
    "--radius-xl": "24px",
    "--shadow-sm": "0 1px 2px rgba(0,0,0,0.3)",
    "--shadow-md": "0 4px 12px rgba(0,0,0,0.4)",
    "--shadow-lg": "0 8px 32px rgba(0,0,0,0.5)",
    "--shadow-glow": "0 0 20px rgba(99,102,241,0.3)",
    "--font-sans": "'Inter', system-ui, -apple-system, sans-serif",
    "--font-mono": "'JetBrains Mono', monospace",
    "--font-display": "'Space Grotesk', sans-serif",
    "--transition": "all 0.2s ease",
}

# ── Built-in Component Templates ────────────────────────────

BUILTIN_COMPONENTS: list[ComponentDefinition] = []

# Hero Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="hero-default",
        name="Hero Section 21st",
        category=ComponentCategory.HERO,
        description="Hero section com gradiente, headline impactante e CTA",
        tags=["hero", "landing", "header", "21st.dev"],
        html_template="""<section class="lyzer-hero">
  <div class="lyzer-hero-bg"></div>
  <div class="lyzer-hero-content">
    <span class="lyzer-badge">{{badge}}</span>
    <h1 class="lyzer-hero-title">{{title}}</h1>
    <p class="lyzer-hero-subtitle">{{subtitle}}</p>
    <div class="lyzer-hero-actions">
      <a href="{{cta_link}}" class="lyzer-btn lyzer-btn-primary">{{cta_text}}</a>
      <a href="{{secondary_link}}" class="lyzer-btn lyzer-btn-ghost">{{secondary_text}}</a>
    </div>
  </div>
</section>""",
        css_variables={
            "--hero-min-height": "80vh",
            "--hero-gradient": "linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1a 100%)",
        },
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "centered", "description": "Texto centralizado"},
            {"name": "left-aligned", "description": "Texto alinhado à esquerda"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# Card Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="card-default",
        name="Card 21st",
        category=ComponentCategory.CARD,
        description="Card com glassmorphism, borda sutil e hover effect",
        tags=["card", "glassmorphism", "ui", "21st.dev"],
        html_template="""<div class="lyzer-card">
  <div class="lyzer-card-icon">{{icon}}</div>
  <h3 class="lyzer-card-title">{{title}}</h3>
  <p class="lyzer-card-desc">{{description}}</p>
  <div class="lyzer-card-footer">
    <span class="lyzer-card-tag">{{tag}}</span>
  </div>
</div>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "default", "description": "Card padrão com borda"},
            {"name": "elevated", "description": "Card com sombra elevada"},
            {"name": "bordered", "description": "Card com borda destacada"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# Features Grid Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="features-grid",
        name="Features Grid 21st",
        category=ComponentCategory.FEATURES,
        description="Grid de features com icones, descricao e hover animation",
        tags=["features", "grid", "landing", "21st.dev"],
        html_template="""<section class="lyzer-features">
  <div class="lyzer-features-header">
    <h2 class="lyzer-features-title">{{section_title}}</h2>
    <p class="lyzer-features-subtitle">{{section_subtitle}}</p>
  </div>
  <div class="lyzer-features-grid">
    {{features}}
  </div>
</section>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "3-col", "description": "3 colunas"},
            {"name": "2-col", "description": "2 colunas"},
            {"name": "4-col", "description": "4 colunas"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# Pricing Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="pricing-table",
        name="Pricing Table 21st",
        category=ComponentCategory.PRICING,
        description="Tabela de precos com destaque para plano recomendado",
        tags=["pricing", "saas", "landing", "21st.dev"],
        html_template="""<section class="lyzer-pricing">
  <div class="lyzer-pricing-header">
    <h2>{{section_title}}</h2>
    <p>{{section_subtitle}}</p>
  </div>
  <div class="lyzer-pricing-grid">
    {{plans}}
  </div>
</section>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "3-tiers", "description": "3 planos"},
            {"name": "4-tiers", "description": "4 planos com enterprise"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# CTA Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="cta-section",
        name="CTA Section 21st",
        category=ComponentCategory.CTA,
        description="Call-to-action com gradiente, urgencia e botao destacado",
        tags=["cta", "conversion", "landing", "21st.dev"],
        html_template="""<section class="lyzer-cta">
  <div class="lyzer-cta-glow"></div>
  <h2 class="lyzer-cta-title">{{title}}</h2>
  <p class="lyzer-cta-desc">{{description}}</p>
  <a href="{{button_link}}" class="lyzer-btn lyzer-btn-primary lyzer-btn-lg">{{button_text}}</a>
  <p class="lyzer-cta-urgency">{{urgency_text}}</p>
</section>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "default", "description": "CTA padrao"},
            {"name": "urgent", "description": "Com indicador de urgencia"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# Testimonial Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="testimonial-card",
        name="Testimonial Card 21st",
        category=ComponentCategory.TESTIMONIAL,
        description="Card de depoimento com avatar, nome e avaliacao",
        tags=["testimonial", "social-proof", "landing", "21st.dev"],
        html_template="""<div class="lyzer-testimonial">
  <div class="lyzer-testimonial-stars">{{stars}}</div>
  <p class="lyzer-testimonial-text">"{{quote}}"</p>
  <div class="lyzer-testimonial-author">
    <div class="lyzer-testimonial-avatar">{{avatar}}</div>
    <div>
      <p class="lyzer-testimonial-name">{{name}}</p>
      <p class="lyzer-testimonial-role">{{role}}</p>
    </div>
  </div>
</div>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "default", "description": "Card padrao"},
            {"name": "compact", "description": "Versao compacta"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# Navbar Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="navbar-default",
        name="Navbar 21st",
        category=ComponentCategory.NAVBAR,
        description="Navbar com glass effect, links e CTA",
        tags=["navbar", "header", "navigation", "21st.dev"],
        html_template="""<nav class="lyzer-navbar">
  <div class="lyzer-navbar-inner">
    <a href="/" class="lyzer-navbar-logo">{{logo}}</a>
    <div class="lyzer-navbar-links">
      {{links}}
    </div>
    <div class="lyzer-navbar-actions">
      <a href="{{cta_link}}" class="lyzer-btn lyzer-btn-primary lyzer-btn-sm">{{cta_text}}</a>
    </div>
  </div>
</nav>""",
        css_variables={
            "--navbar-bg": "rgba(10, 10, 15, 0.8)",
            "--navbar-blur": "12px",
        },
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "default", "description": "Navbar padrao"},
            {"name": "transparent", "description": "Navbar transparente"},
            {"name": "sticky", "description": "Navbar fixa no topo"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# Footer Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="footer-default",
        name="Footer 21st",
        category=ComponentCategory.FOOTER,
        description="Footer completo com links, redes sociais e copyright",
        tags=["footer", "landing", "21st.dev"],
        html_template="""<footer class="lyzer-footer">
  <div class="lyzer-footer-grid">
    <div class="lyzer-footer-brand">
      <h3>{{brand_name}}</h3>
      <p>{{brand_description}}</p>
    </div>
    {{columns}}
  </div>
  <div class="lyzer-footer-bottom">
    <p>{{copyright}}</p>
  </div>
</footer>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "4-col", "description": "4 colunas"},
            {"name": "3-col", "description": "3 colunas"},
        ],
        dependencies=["lyzer-design-system"],
    )
)

# FAQ Component
BUILTIN_COMPONENTS.append(
    ComponentDefinition(
        component_id="faq-section",
        name="FAQ Section 21st",
        category=ComponentCategory.FAQ,
        description="Secao de perguntas frequentes com accordion",
        tags=["faq", "landing", "21st.dev"],
        html_template="""<section class="lyzer-faq">
  <h2 class="lyzer-faq-title">{{section_title}}</h2>
  <div class="lyzer-faq-list">
    {{items}}
  </div>
</section>""",
        css_variables={},
        design_tokens=DESIGN_TOKENS_21ST,
        variants=[
            {"name": "default", "description": "Accordion padrao"},
        ],
        dependencies=["lyzer-design-system"],
    )
)


# ── CSS Generator ──────────────────────────────────────────


def generate_css(tokens: dict[str, str] | None = None) -> str:
    """Generate CSS from design tokens (21st.dev style)."""
    t = {**DESIGN_TOKENS_21ST, **(tokens or {})}
    vars_str = "\n  ".join(f"{k}: {v};" for k, v in t.items())

    return f""":root {{
  {vars_str}
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: var(--font-sans);
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}

/* ── Buttons ── */
.lyzer-btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
  border: 1px solid transparent;
}}

.lyzer-btn-primary {{
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}}
.lyzer-btn-primary:hover {{
  background: var(--accent-hover);
  box-shadow: var(--shadow-glow);
  transform: translateY(-1px);
}}

.lyzer-btn-ghost {{
  background: transparent;
  color: var(--text-secondary);
  border-color: var(--border);
}}
.lyzer-btn-ghost:hover {{
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-hover);
}}

.lyzer-btn-lg {{
  padding: 16px 32px;
  font-size: 1.1rem;
}}

.lyzer-btn-sm {{
  padding: 8px 16px;
  font-size: 0.85rem;
}}

/* ── Cards ── */
.lyzer-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: var(--transition);
}}
.lyzer-card:hover {{
  border-color: var(--border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}}

/* ── Hero ── */
.lyzer-hero {{
  position: relative;
  min-height: var(--hero-min-height, 80vh);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--hero-gradient, linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1a 100%));
  overflow: hidden;
}}

.lyzer-hero-content {{
  position: relative;
  z-index: 2;
  text-align: center;
  max-width: 800px;
  padding: 0 24px;
}}

.lyzer-hero-title {{
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #f0f0f5 0%, #818cf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

.lyzer-hero-subtitle {{
  font-size: 1.2rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 32px;
}}

.lyzer-hero-actions {{
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}}

.lyzer-badge {{
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--accent-muted);
  color: var(--accent-hover);
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 16px;
}}

/* ── Features ── */
.lyzer-features {{
  padding: 80px 24px;
  max-width: 1200px;
  margin: 0 auto;
}}

.lyzer-features-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 48px;
}}

/* ── Pricing ── */
.lyzer-pricing {{
  padding: 80px 24px;
  max-width: 1200px;
  margin: 0 auto;
}}

.lyzer-pricing-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 48px;
}}

/* ── CTA ── */
.lyzer-cta {{
  position: relative;
  text-align: center;
  padding: 80px 24px;
  background: linear-gradient(135deg, var(--accent-muted) 0%, transparent 100%);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}}

.lyzer-cta-title {{
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 3rem);
  margin-bottom: 16px;
}}

.lyzer-cta-urgency {{
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 12px;
}}

/* ── Testimonials ── */
.lyzer-testimonial {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
}}

.lyzer-testimonial-stars {{
  color: var(--warning);
  margin-bottom: 12px;
}}

/* ── Navbar ── */
.lyzer-navbar {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--navbar-bg, rgba(10,10,15,0.8));
  backdrop-filter: blur(var(--navbar-blur, 12px));
  border-bottom: 1px solid var(--border);
}}

.lyzer-navbar-inner {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

.lyzer-navbar-links {{
  display: flex;
  gap: 24px;
}}

/* ── Footer ── */
.lyzer-footer {{
  padding: 60px 24px 24px;
  max-width: 1200px;
  margin: 0 auto;
}}

.lyzer-footer-grid {{
  display: grid;
  grid-template-columns: 2fr repeat(3, 1fr);
  gap: 40px;
}}

.lyzer-footer-bottom {{
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  text-align: center;
  color: var(--text-muted);
}}

/* ── FAQ ── */
.lyzer-faq {{
  padding: 80px 24px;
  max-width: 800px;
  margin: 0 auto;
}}

/* ── Responsive ── */
@media (max-width: 768px) {{
  .lyzer-footer-grid {{
    grid-template-columns: 1fr;
  }}
  .lyzer-navbar-links {{
    display: none;
  }}
  .lyzer-features-grid {{
    grid-template-columns: 1fr;
  }}
  .lyzer-pricing-grid {{
    grid-template-columns: 1fr;
  }}
}}
"""


# ── Component Registry ──────────────────────────────────────


class UIComponentRegistry:
    """Registry of UI components (21st.dev-style).

    Gerencia:
    - Catálogo de componentes com templates
    - Variantes por componente
    - Design system tokens
    - Geração de CSS
    - Versionamento
    """

    def __init__(self, db_path: str = ".state/ui_components.db"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._components: dict[str, ComponentDefinition] = {}
        self._ensure_schema()
        self._load_builtins()

    def _ensure_schema(self):
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS components (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    tags TEXT,
                    variants TEXT,
                    html_template TEXT,
                    css_variables TEXT,
                    design_tokens TEXT,
                    version TEXT,
                    author TEXT,
                    usage_count INTEGER DEFAULT 0,
                    quality_score REAL DEFAULT 0,
                    created_at REAL,
                    updated_at REAL
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_component_category
                ON components(category)
            """)
            self._conn.commit()

    def _load_builtins(self):
        """Load built-in components into registry."""
        for comp in BUILTIN_COMPONENTS:
            if comp.component_id not in self._components:
                self.register(comp)

    def register(self, component: ComponentDefinition) -> str:
        """Register a new component."""
        with self._lock:
            self._components[component.component_id] = component
            self._conn.execute(
                "INSERT OR REPLACE INTO components "
                "(id, name, category, description, tags, variants, html_template, "
                "css_variables, design_tokens, version, author, usage_count, "
                "quality_score, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    component.component_id,
                    component.name,
                    component.category.value,
                    component.description,
                    json.dumps(component.tags),
                    json.dumps(component.variants),
                    component.html_template,
                    json.dumps(component.css_variables),
                    json.dumps(component.design_tokens),
                    component.version,
                    component.author,
                    component.usage_count,
                    component.quality_score,
                    component.created_at,
                    component.updated_at,
                ),
            )
            self._conn.commit()
        return component.component_id

    def get(self, component_id: str) -> ComponentDefinition | None:
        """Get a component by ID."""
        return self._components.get(component_id)

    def list_by_category(
        self, category: ComponentCategory
    ) -> list[ComponentDefinition]:
        """List components by category."""
        return [c for c in self._components.values() if c.category == category]

    def search(self, query: str) -> list[ComponentDefinition]:
        """Search components by name, tag, or description."""
        q = query.lower()
        return [
            c
            for c in self._components.values()
            if q in c.name.lower()
            or q in c.description.lower()
            or any(q in t.lower() for t in c.tags)
        ]

    def render_page(self, sections: list[dict[str, Any]]) -> str:
        """Render a complete page from component sections."""
        css = generate_css()
        sections_html = []

        for section in sections:
            comp_id = section.get("component", "hero-default")
            params = section.get("params", {})
            comp = self.get(comp_id)
            if comp:
                rendered = comp.render(**params)
                sections_html.append(rendered)

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{page_title}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
{"".join(sections_html)}
</body>
</html>"""

    def count(self) -> int:
        return len(self._components)

    def stats(self) -> dict[str, Any]:
        categories = {}
        for c in self._components.values():
            cat = c.category.value
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_components": self.count(),
            "categories": categories,
            "total_variants": sum(len(c.variants) for c in self._components.values()),
        }


# ── Quick Test ──────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    registry = UIComponentRegistry(db_path=tempfile.mktemp(suffix=".db"))
    stats = registry.stats()
    print("Component Registry (21st.dev style)")
    print(f"  Total components: {stats['total_components']}")
    print(f"  Categories: {len(stats['categories'])}")
    for cat, count in sorted(stats["categories"].items()):
        print(f"    {cat}: {count}")
    print("\nSearch 'card':")
    for c in registry.search("card"):
        print(f"  - {c.name} ({c.component_id}): {c.description[:60]}")
    print(f"\nCSS generated: {len(generate_css())} chars")
