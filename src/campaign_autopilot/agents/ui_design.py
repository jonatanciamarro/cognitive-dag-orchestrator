"""🎨 UI Design Agent — Gera landing pages, sites e artefatos visuais usando Open Design.

Usa o DesignSystem + ArtifactGenerator do Product Forge para gerar
artefatos profissionais com design system Lyzer Labs.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ..logging_utils import StructuredLogger

log = StructuredLogger("ui_design")

# Try to import product_forge components (optional dependency)
try:
    from ..product_forge import (
        DesignSystem,
        DesignSystemRegistry,
        default_lyzer_design_system,
        LandingPageGenerator,
        LandingPageSpec,
        HeroSection,
        FeaturesSection,
        CTASection,
        TestimonialsSection,
        PricingSection,
        FooterSection,
        ArtifactGenerator,
        ArtifactSpec,
        ArtifactType,
    )

    HAS_PRODUCT_FORGE = True
except ImportError:
    HAS_PRODUCT_FORGE = False


class UIDesignAgent(AgentBase):
    """Agente de design UI — gera landing pages, sites, emails e dashboards.

    Usa o DesignSystem do Product Forge (Open Design compatible) para
    produzir artefatos visuais consistentes com a identidade Lyzer Labs.

    Modos de operação:
    - landing_page: Gera landing page completa com seções
    - site_page: Gera página de site/blog
    - email: Gera template de email
    - dashboard: Gera dashboard HTML
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("ui_design", **kwargs)
        self._design_system: DesignSystem | None = None
        self._landing_gen: LandingPageGenerator | None = None
        self._artifact_gen: ArtifactGenerator | None = None

    def _ensure_design_system(self) -> bool:
        """Initialize design system if not already loaded."""
        if not HAS_PRODUCT_FORGE:
            return False
        if self._design_system is None:
            self._design_system = default_lyzer_design_system()
        if self._landing_gen is None:
            self._landing_gen = LandingPageGenerator()
        if self._artifact_gen is None:
            self._artifact_gen = ArtifactGenerator()
        return True

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        # Try to extract data from previous step results
        step_results = context.step_results if hasattr(context, "step_results") else {}
        if step_results:
            for step_id in [
                "content_generator",
                "content_repurposer",
                "publisher",
                "content_planner",
            ]:
                prev = step_results.get(step_id, {})
                if isinstance(prev, dict):
                    prev_output = prev.get("output", prev)
                    if isinstance(prev_output, dict):
                        for key in [
                            "title",
                            "niche",
                            "articles",
                            "content",
                            "product_name",
                            "cta_link",
                        ]:
                            if key not in campaign and key in prev_output:
                                campaign[key] = prev_output[key]

        action = campaign.get("action", "landing_page")
        output_dir = campaign.get("output_dir", "output/ui_design")

        if not self._ensure_design_system():
            return AgentResult(
                agent=self.name,
                status="error",
                output={
                    "error": "product_forge module not available",
                    "hint": "Ensure src/campaign_autopilot/product_forge/ exists",
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="run",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                    error="product_forge import failed",
                ),
            )

        try:
            if action == "landing_page":
                return self._generate_landing_page(campaign, output_dir, started_at)
            elif action == "site":
                return self._generate_site_page(campaign, output_dir, started_at)
            elif action == "email":
                return self._generate_email(campaign, output_dir, started_at)
            elif action == "dashboard":
                return self._generate_dashboard(campaign, output_dir, started_at)
            else:
                return self._generate_landing_page(campaign, output_dir, started_at)
        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="run",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    error=str(e),
                ),
            )

    def _build_landing_spec(self, campaign: dict) -> LandingPageSpec:
        """Build a LandingPageSpec from campaign data."""
        title = campaign.get("title", "Oferta Especial")
        niche = campaign.get("niche", "marketing digital")
        cta_link = campaign.get("cta_link", "#")
        cta_text = campaign.get("cta_text", "Saiba Mais")

        spec = LandingPageSpec(
            title=title,
            slug=campaign.get("slug", title.lower().replace(" ", "-")),
            meta_description=campaign.get(
                "meta_description", f"Oferta especial de {niche}"
            ),
            offer_data={
                "product_name": campaign.get("product_name", title),
                "price": campaign.get("price", 97),
                "original_price": campaign.get("original_price", 197),
                "affiliate_link": cta_link,
                "niche": niche,
            },
        )

        # Hero section
        spec.add_section(
            HeroSection(
                headline=title,
                subtitle=campaign.get("subtitle", f"A melhor opção em {niche}"),
                cta_text=cta_text,
                cta_link=cta_link,
                secondary_cta_text=campaign.get("secondary_cta", "Saiba Mais"),
                secondary_cta_link="#learn-more",
            )
        )

        # Features section
        features = campaign.get(
            "features",
            [
                {
                    "title": "Qualidade Premium",
                    "description": "Produtos selecionados com os mais altos padrões de qualidade",
                },
                {
                    "title": "Melhor Preço",
                    "description": "Preços competitivos com descontos especiais para você",
                },
                {
                    "title": "Entrega Rápida",
                    "description": "Receba seu produto com rapidez e segurança",
                },
            ],
        )
        spec.add_section(FeaturesSection(items=features))

        # Testimonials
        testimonials = campaign.get(
            "testimonials",
            [
                {
                    "quote": "Produto excelente! Superou minhas expectativas.",
                    "author": "Maria S.",
                },
                {
                    "quote": "Entrega rápida e produto de alta qualidade.",
                    "author": "João P.",
                },
            ],
        )
        spec.add_section(TestimonialsSection(items=testimonials))

        # CTA section
        spec.add_section(
            CTASection(
                cta_text=cta_text,
                cta_link=cta_link,
            )
        )

        # Footer
        spec.add_section(FooterSection())

        return spec

    def _generate_landing_page(
        self, campaign: dict, output_dir: str, started_at: str
    ) -> AgentResult:
        """Generate a landing page using the Open Design system."""
        spec = self._build_landing_spec(campaign)
        file_path = self._landing_gen.generate(spec, output_dir)

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "file_path": file_path,
                "title": spec.title,
                "sections": len(spec.sections),
                "design_system": "Lyzer Labs (Open Design)",
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="landing_page",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[f"Landing page generated: {file_path}"],
            ),
        )

    def _generate_site_page(
        self, campaign: dict, output_dir: str, started_at: str
    ) -> AgentResult:
        """Generate a site/blog page using the Open Design system."""
        title = campaign.get("title", "Artigo")
        content_html = campaign.get("content_html", "<p>Conteúdo do artigo</p>")

        spec = ArtifactSpec(
            type=ArtifactType.LANDING_PAGE,
            title=title,
            description=campaign.get("meta_description", ""),
            campaign_data={
                "headline": title,
                "subtitle": campaign.get("subtitle", ""),
                "content": content_html,
                "author": campaign.get("author", "Equipe Autopilot"),
                "date": campaign.get(
                    "date", datetime.now(timezone.utc).strftime("%d/%m/%Y")
                ),
            },
        )

        result = self._artifact_gen.generate_artifact(spec, output_dir)
        finished_at = datetime.now(timezone.utc).isoformat()

        return AgentResult(
            agent=self.name,
            status="success" if result.success else "error",
            output={
                "file_path": result.file_path,
                "title": title,
                "size_bytes": result.size_bytes,
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="site_page",
                status="success" if result.success else "error",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[f"Site page: {result.file_path}"]
                if result.success
                else [f"Error: {result.errors}"],
            ),
        )

    def _generate_email(
        self, campaign: dict, output_dir: str, started_at: str
    ) -> AgentResult:
        """Generate an email template."""
        from ..product_forge.email_template_generator import (
            EmailTemplateGenerator,
            EmailSpec,
        )

        gen = EmailTemplateGenerator()
        from ..product_forge.email_template_generator import EmailSection

        spec = EmailSpec(
            subject=campaign.get("title", "Oferta Especial"),
            preview_text=campaign.get("subtitle", ""),
            sections=[
                EmailSection(
                    type="header",
                    content=campaign.get("title", "Oferta Especial"),
                    align="center",
                ),
                EmailSection(
                    type="paragraph",
                    content=campaign.get(
                        "content_html", "<p>Confira esta oferta especial para você.</p>"
                    ),
                    align="left",
                ),
                EmailSection(
                    type="button",
                    content=campaign.get("cta_text", "Saiba Mais"),
                    align="center",
                    style={"url": campaign.get("cta_link", "#")},
                ),
                EmailSection(
                    type="footer",
                    content="Enviado por Campaign Autopilot • Lyzer Labs",
                    align="center",
                ),
            ],
        )
        file_path = gen.generate(spec, output_dir)

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={"file_path": str(file_path)},
            trace=AgentTrace(
                agent=self.name,
                step_id="email",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )

    def _generate_dashboard(
        self, campaign: dict, output_dir: str, started_at: str
    ) -> AgentResult:
        """Generate a dashboard HTML."""
        from ..product_forge.dashboard_generator import (
            DashboardGenerator,
            DashboardSpec,
        )

        gen = DashboardGenerator()
        from ..product_forge.dashboard_generator import KPIRow, MetricCard

        raw_metrics = campaign.get("metrics", [])
        kpi_rows = [
            KPIRow(
                metrics=[
                    MetricCard(
                        label=m.get("label", ""),
                        value=m.get("value", ""),
                        change=m.get("change", ""),
                        trend="up" if "+" in m.get("change", "") else "down",
                    )
                    for m in raw_metrics
                ]
            )
        ]
        spec = DashboardSpec(
            title=campaign.get("title", "Dashboard"),
            kpi_rows=kpi_rows,
        )
        file_path = gen.generate(spec, output_dir)

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={"file_path": str(file_path)},
            trace=AgentTrace(
                agent=self.name,
                step_id="dashboard",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )
