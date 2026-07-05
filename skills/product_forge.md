# Product Forge — Lyzer Labs Visual Generation Layer

## Purpose
Generate HTML/CSS artifacts (landing pages, dashboards, emails, presentations) from campaign data using the Lyzer Labs design system.

## When to use
- Need a landing page for an affiliate product
- Need a campaign dashboard
- Need an email template for marketing
- Need a presentation deck

## How to use

### Generate affiliate landing page
```python
from campaign_autopilot.product_forge import LandingPageGenerator

gen = LandingPageGenerator()
path = gen.generate_affiliate_landing(
    product_name="Curso X",
    product_description="Descrição",
    affiliate_link="https://hotmart.com/...",
    features=["Feature 1", "Feature 2"],
    output_dir="output/landing_pages",
)
```

### Generate dashboard
```python
from campaign_autopilot.product_forge import (
    DashboardGenerator, DashboardSpec, MetricCard, KPIRow, ChartSpec, ChartType,
)

gen = DashboardGenerator()
spec = DashboardSpec(
    title="Campanha Nome",
    kpi_rows=[KPIRow(metrics=[MetricCard(label="Vendas", value="123")])],
)
path = gen.generate(spec)
```

## Design Tokens
All colors, gradients, typography in `color_palette.py`. CSS variables: `--lyzer-*`.

## Key classes
- `LandingPageGenerator` — generate_affiliate_landing(), batch_generate()
- `DashboardGenerator` — generate(), generate_campaign_dashboard()
- `EmailTemplateGenerator` — generate(), generate_affiliate_email()
- `PresentationGenerator` — generate()
- `DesignSystemRegistry` — singleton for design system management
