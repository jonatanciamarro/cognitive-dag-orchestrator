"""Product Forge — Open Design integration for Lyzer Labs.

Gera artefatos visuais (landing pages, dashboards, emails, apresentações)
a partir de dados de campanha, usando o formato Open Design como especificação
de design system.

Integração com:
    - Campaign Autopilot agents (dados de campanha → artefatos)
    - Open Design format (DESIGN.md como design system portável)
    - AG-Kit evolution modules (cognitive mesh, world model, etc.)
"""

from __future__ import annotations

from .design_system import (
    DesignSystem,
    DesignToken,
    ColorToken,
    TypographyToken,
    SpacingToken,
    ComponentSpec,
    LayoutSpec,
    DesignSystemRegistry,
    load_design_system,
    default_lyzer_design_system,
)

from .artifact_generator import (
    ArtifactGenerator,
    ArtifactSpec,
    ArtifactType,
    ArtifactResult,
    RenderTemplate,
    ComponentRenderer,
    LayoutRenderer,
)

from .landing_page_generator import (
    LandingPageGenerator,
    LandingPageSpec,
    HeroSection,
    FeaturesSection,
    CTASection,
    TestimonialsSection,
    PricingSection,
    FooterSection,
    SectionBase,
)

from .dashboard_generator import (
    DashboardGenerator,
    DashboardSpec,
    MetricCard,
    ChartSpec,
    ChartType,
    TableSpec,
    KPIRow,
)

from .email_template_generator import (
    EmailTemplateGenerator,
    EmailSpec,
    EmailSection,
    EmailStyle,
)

from .color_palette import (
    LYZER_COLORS,
    LYZER_GRADIENTS,
    LYZER_SHADOWS,
    LYZER_TYPOGRAPHY,
    generate_css_variables,
    generate_tailwind_config,
)

from .presentation_generator import (
    PresentationGenerator,
    PresentationSpec,
    SlideSpec,
    SlideType,
    SlideSection,
    PresentationTheme,
)

__all__ = [
    "DesignSystem",
    "DesignToken",
    "ColorToken",
    "TypographyToken",
    "SpacingToken",
    "ComponentSpec",
    "LayoutSpec",
    "DesignSystemRegistry",
    "load_design_system",
    "default_lyzer_design_system",
    "ArtifactGenerator",
    "ArtifactSpec",
    "ArtifactType",
    "ArtifactResult",
    "RenderTemplate",
    "ComponentRenderer",
    "LayoutRenderer",
    "LandingPageGenerator",
    "LandingPageSpec",
    "HeroSection",
    "FeaturesSection",
    "CTASection",
    "TestimonialsSection",
    "PricingSection",
    "FooterSection",
    "SectionBase",
    "DashboardGenerator",
    "DashboardSpec",
    "MetricCard",
    "ChartSpec",
    "ChartType",
    "TableSpec",
    "KPIRow",
    "EmailTemplateGenerator",
    "EmailSpec",
    "EmailSection",
    "EmailStyle",
    "LYZER_COLORS",
    "LYZER_GRADIENTS",
    "LYZER_SHADOWS",
    "LYZER_TYPOGRAPHY",
    "generate_css_variables",
    "generate_tailwind_config",
    "PresentationGenerator",
    "SlideSpec",
    "SlideType",
    "SlideSection",
    "PresentationSpec",
    "PresentationTheme",
]
