# Design System — Lyzer Labs

> Version 1.0.0
> Open Design Compatible — https://github.com/nexu-io/open-design

Quantum design system for Lyzer Labs ecosystem — dark-first, agent-native, AI-adaptive interface language.

---

## Colors

| Token | Value | Description |
|-------|-------|-------------|
| `primary` | `#7c2dff` | Roxo quantum — identidade central |
| `secondary` | `#00aaff` | Ciano elétrico — acento tech |
| `accent` | `#f0b400` | Dourado — CTA, premium, destaque |
| `bg-dark` | `#0a0a0f` | Background principal |
| `bg-card` | `#12121f` | Superfície de cards |
| `bg-elevated` | `#1a1a2e` | Superfície elevada |
| `text-primary` | `#f0f0ff` | Texto principal |
| `text-secondary` | `#a0a0c0` | Texto secundário |
| `text-muted` | `#606080` | Texto low emphasis |
| `border` | `#2a2a3e` | Borda padrão |
| `success` | `#00e676` | Verde sucesso |
| `warning` | `#ffab00` | Amarelo alerta |
| `error` | `#ff1744` | Vermelho erro |
| `info` | `#00b0ff` | Azul informação |

### Gradients

| Name | Value |
|------|-------|
| `quantum` | `linear-gradient(135deg, #7c2dff 0%, #00aaff 100%)` |
| `quantum-dark` | `linear-gradient(135deg, #250673 0%, #00334d 100%)` |
| `sunset` | `linear-gradient(135deg, #7c2dff 0%, #f0b400 100%)` |
| `neon` | `linear-gradient(135deg, #00e676 0%, #00b0ff 100%)` |
| `deep` | `linear-gradient(180deg, #0a0a0f 0%, #12121f 50%, #1a1a2e 100%)` |
| `card` | `linear-gradient(145deg, #1a1a2e 0%, #12121f 100%)` |

### Shadows

| Name | Value |
|------|-------|
| `glow` | `0 0 20px rgba(124,45,255,0.3)` |
| `glow-blue` | `0 0 20px rgba(0,170,255,0.3)` |
| `glow-gold` | `0 0 20px rgba(240,180,0,0.3)` |

---

## Typography

| Family | Font |
|--------|------|
| `sans` | `'Inter', 'Segoe UI', system-ui, sans-serif` |
| `display` | `'Space Grotesk', 'Inter', sans-serif` |
| `mono` | `'JetBrains Mono', 'Fira Code', monospace` |

### Scale

| Size | Value | Usage |
|------|-------|-------|
| `xs` | 0.75rem | Caption, labels |
| `sm` | 0.875rem | Body small, metadata |
| `base` | 1rem | Body text |
| `lg` | 1.125rem | Large body |
| `xl` | 1.25rem | Small headings |
| `2xl` | 1.5rem | Section headings |
| `3xl` | 1.875rem | Page headings |
| `4xl` | 2.25rem | Hero headings |
| `5xl` | 3rem | Large hero |
| `6xl` | 3.75rem | Display |
| `7xl` | 4.5rem | Massive display |

---

## Components

### button

_Action button with multiple variants._

**Variants:** primary, secondary, ghost, accent

| Prop | Type | Default |
|------|------|---------|
| `variant` | string | primary |
| `size` | string | md |
| `fullWidth` | boolean | false |
| `loading` | boolean | false |
| `icon` | string | — |

### card

_Content container with glassmorphism._

**Variants:** elevated, outlined, glass

| Prop | Type | Default |
|------|------|---------|
| `variant` | string | elevated |
| `padding` | string | lg |
| `hover` | boolean | true |

### metric-card

_KPI metric display card._

**Variants:** default, compact

| Prop | Type | Default |
|------|------|---------|
| `label` | string | — |
| `value` | string | — |
| `change` | string | — |
| `trend` | string | neutral |
| `icon` | string | — |

### hero-section

_Landing page hero with headline, subtitle, CTA._

| Prop | Type | Default |
|------|------|---------|
| `headline` | string | — |
| `subtitle` | string | — |
| `cta_text` | string | — |
| `cta_link` | string | — |
| `background` | string | gradient |

### pricing-card

_Pricing tier display._

| Prop | Type | Default |
|------|------|---------|
| `tier` | string | — |
| `price` | string | — |
| `period` | string | /month |
| `features` | array | — |
| `featured` | boolean | false |

---

## Layouts

### page

- Columns: 1
- Max Width: 1200px
- Gap: —

### grid-3

- Columns: 3
- Max Width: 1200px
- Gap: 1.5rem
- Responsive: sm=1, md=2, lg=3, xl=3

### sidebar-layout

- Columns: 2
- Max Width: 1200px
- Gap: 2rem
- Responsive: sm=1, md=1, lg=2, xl=2

---

## Breakpoints

- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

---

## Spacing

| Token | Value |
|-------|-------|
| `0` | 0 |
| `px` | 1px |
| `0.5` | 0.125rem |
| `1` | 0.25rem |
| `2` | 0.5rem |
| `3` | 0.75rem |
| `4` | 1rem |
| `5` | 1.25rem |
| `6` | 1.5rem |
| `8` | 2rem |
| `10` | 2.5rem |
| `12` | 3rem |
| `16` | 4rem |
| `20` | 5rem |
| `24` | 6rem |

---

## Border Radius

| Token | Value |
|-------|-------|
| `sm` | 0.25rem |
| `md` | 0.5rem |
| `lg` | 0.75rem |
| `xl` | 1rem |
| `2xl` | 1.5rem |
| `full` | 9999px |

---

## Usage

### CSS Variables

```css
:root {
  --lyzer-primary: #7c2dff;
  --lyzer-secondary: #00aaff;
  --lyzer-accent: #f0b400;
  --lyzer-bg-dark: #0a0a0f;
  --lyzer-bg-card: #12121f;
  --lyzer-text-primary: #f0f0ff;
  --lyzer-font-sans: 'Inter', system-ui, sans-serif;
  --lyzer-font-display: 'Space Grotesk', sans-serif;
}
```

### Tailwind Config

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: { 500: '#7c2dff', /* ... */ },
        secondary: { 500: '#00aaff', /* ... */ },
        accent: { 500: '#f0b400', /* ... */ },
      },
      fontFamily: {
        display: ['Space Grotesk', 'Inter', 'sans-serif'],
      },
    },
  },
};
```

### Python API

```python
from campaign_autopilot.product_forge import (
    default_lyzer_design_system,
    DesignSystemRegistry,
    generate_css_variables,
)

# Load design system
ds = default_lyzer_design_system()
registry = DesignSystemRegistry()
registry.register("lyzer-labs", ds)

# Generate CSS
css = generate_css_variables()
```

---

## Metadata

- **author**: Lyzer Labs
- **framework**: Open Design Compatible
- **generated**: 2026-06-24
- **repository**: https://github.com/Ciamarro1/campaign-autopilot

---

_Generated by Lyzer Labs Product Forge — Open Design compatible_
