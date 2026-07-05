# Product Forge — Lyzer Labs Visual Generation Layer

> Integração Open Design + Campaign Autopilot para geração de artefatos visuais.

---

## Arquitetura

```
Campaign Data
     ↓
Product Forge
     ├── DesignSystem         ← DESIGN.md (Open Design format)
     ├── ArtifactGenerator    ← Core engine (HTML/CSS/Email)
     ├── LandingPageGenerator ← Landing pages para afiliados
     ├── DashboardGenerator   ← Dashboards de campanha
     ├── EmailTemplateGenerator ← Email marketing
     ├── PresentationGenerator ← Slides/decks
     └── ComponentRenderer   ← UI components do design system
     ↓
Artefatos (HTML, CSS)
     ↓
Output/ → Site, Email, Dashboard
```

---

## Componentes

### 1. Design System (`design_system.py`)

Implementa a especificação Open Design como design system portável.

| Classe | Função |
|--------|--------|
| `DesignSystem` | Container do design system completo |
| `ColorToken` | Token de cor (hex, opacity, dark mode) |
| `TypographyToken` | Token tipográfico (font, size, weight) |
| `ComponentSpec` | Especificação de componente UI |
| `LayoutSpec` | Especificação de layout (grid, sidebar) |
| `DesignSystemRegistry` | Singleton — gerencia múltiplos design systems |

### 2. Artifact Generator (`artifact_generator.py`)

Core engine que transforma specs em HTML renderizado.

| Classe | Função |
|--------|--------|
| `ArtifactGenerator` | Gera artefatos de qualquer tipo |
| `ComponentRenderer` | Renderiza componentes individuais |
| `LayoutRenderer` | Renderiza layouts (grid, sidebar) |
| `RenderTemplate` | Template com slots nomeados |

**Tipos de artefato:**
- `LANDING_PAGE` — Landing pages completas
- `DASHBOARD` — Dashboards com KPIs, gráficos, tabelas
- `EMAIL` — Templates de email responsivos
- `SOCIAL_CARD` — Cards para redes sociais (1200×630)
- `REPORT` — Relatórios formatados
- `PRESENTATION` — Apresentações em slides

### 3. Landing Page Generator (`landing_page_generator.py`)

Otimizado para páginas de afiliados e product launches.

| Classe | Função |
|--------|--------|
| `LandingPageGenerator` | Gera landing pages de campanhas |
| `LandingPageSpec` | Especificação completa da página |
| `HeroSection` | Seção hero com headline + CTA |
| `FeaturesSection` | Grid de features |
| `TestimonialsSection` | Depoimentos |
| `PricingSection` | Tabela de preços |
| `CTASection` | Call to action com urgência |
| `FooterSection` | Footer com links e copyright |

### 4. Dashboard Generator (`dashboard_generator.py`)

Dashboards de campanha com métricas em tempo real.

| Classe | Função |
|--------|--------|
| `DashboardGenerator` | Gera dashboards completos |
| `DashboardSpec` | Especificação do dashboard |
| `MetricCard` | Card de KPI individual |
| `ChartSpec` | Especificação de gráfico |
| `TableSpec` | Tabela de dados |
| `KPIRow` | Linha de métricas |

### 5. Email Template Generator (`email_template_generator.py`)

Templates de email para marketing e nutrição.

| Classe | Função |
|--------|--------|
| `EmailTemplateGenerator` | Gera templates de email |
| `EmailSpec` | Especificação do email |
| `EmailSection` | Seção do email (texto, botão, imagem) |
| `EmailStyle` | Estilo do email |

### 6. Presentation Generator (`presentation_generator.py`)

Apresentações em slides em HTML puro.

| Classe | Função |
|--------|--------|
| `PresentationGenerator` | Gera apresentações completas |
| `PresentationSpec` | Especificação da apresentação |
| `SlideSpec` | Especificação de slide individual |
| `PresentationTheme` | Tema da apresentação |

### 7. Color Palette (`color_palette.py`)

Design tokens de cor, gradiente, sombra e tipografia.

| Função | Descrição |
|--------|-----------|
| `generate_css_variables()` | Gera CSS custom properties |
| `generate_tailwind_config()` | Gera config Tailwind |

---

## Integração com Campaign Autopilot

### Gerar Landing Page de Afiliado

```python
from campaign_autopilot.product_forge import LandingPageGenerator
from campaign_autopilot.product_forge import DesignSystemRegistry, default_lyzer_design_system

# Registrar design system
registry = DesignSystemRegistry()
registry.register("lyzer-labs", default_lyzer_design_system())

# Gerar landing page
gen = LandingPageGenerator()
path = gen.generate_affiliate_landing(
    product_name="Curso Marketing Digital",
    product_description="Aprenda marketing digital do zero ao avançado",
    affiliate_link="https://hotmart.com/product/123",
    price="R$ 197",
    features=[
        "Módulo 1 — Fundamentos",
        "Módulo 2 — SEO Avançado",
        "Módulo 3 — Tráfego Pago",
    ],
    testimonials=[
        "Transformou minha carreira",
        "Melhor curso que já fiz",
    ],
    urgency="Oferta por tempo limitado",
    output_dir="output/landing_pages",
)
print(f"Landing page gerada: {path}")
```

### Gerar Dashboard

```python
from campaign_autopilot.product_forge import (
    DashboardGenerator, DashboardSpec, MetricCard, ChartSpec, ChartType, KPIRow,
)

gen = DashboardGenerator()
spec = DashboardSpec(
    title="Campanha SEO — Janeiro",
    subtitle="Métricas de tráfego orgânico",
    kpi_rows=[
        KPIRow(metrics=[
            MetricCard(label="Visitantes", value="12,450", change="+23%", trend="up"),
            MetricCard(label="Conversões", value="345", change="+15%", trend="up"),
            MetricCard(label="Receita", value="R$ 8,290", change="+31%", trend="up"),
        ]),
    ],
)
path = gen.generate(spec, "output/dashboards")
```

### Gerar Apresentação

```python
from campaign_autopilot.product_forge import (
    PresentationGenerator, PresentationSpec, SlideSpec, SlideType, SlideSection,
)

gen = PresentationGenerator()
spec = PresentationSpec(
    title="Estratégia Q4 2026",
    subtitle="Plano de crescimento",
    author="Lyzer Labs",
    slides=[
        SlideSpec(type=SlideType.CONTENT, title="Resumo Executivo",
                  sections=[SlideSection(content="Crescimento de 40% em tráfego orgânico")]),
        SlideSpec(type=SlideType.METRICS, title="Métricas Atuais",
                  sections=[SlideSection(type="metric", content="45K|Visitantes/mês")]),
    ],
)
path = gen.generate(spec, "output/presentations")
```

---

## Revenue Path (Fast Path to Money)

O Product Forge gera artefatos que convertem:

1. **Landing Pages para Afiliados** → Tráfego orgânico converte em comissões
2. **Email Marketing** → Nutrição de leads com links de afiliado
3. **Dashboards** → Acompanhamento de métricas em tempo real
4. **Apresentações** → Vendas de consultoria / pitches
5. **Social Cards** → Conteúdo para redes sociais

---

## Dependências

- **Zero novas dependências** — stdlib + HTML/CSS puro
- Open Design é referência arquitetural, não runtime dependency
- Compatível com qualquer hospedagem estática (GitHub Pages, Netlify, Vercel)

---

## Próximos Passos

1. ✅ Design System base + DESIGN.md
2. ✅ Artifact Generator (landing page, dashboard, email, presentation)
3. ✅ Integração com agentes do Campaign Autopilot — `UIDesignAgent` no orchestrator
4. ✅ Geração automática de landing pages via workflow — `full_media_workflow.json`
5. ⬜ Template marketplace (compartilhar templates entre campanhas)

---

_Arquitetura: Lyzer Labs Product Forge — Open Design evolution_
