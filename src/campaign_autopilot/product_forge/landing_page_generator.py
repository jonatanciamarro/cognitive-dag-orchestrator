"""Landing Page Generator — Landing pages for affiliate offers & product launches."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SectionBase:
    type: str = "generic"
    title: str = ""
    description: str = ""


@dataclass
class HeroSection(SectionBase):
    type: str = "hero"
    headline: str = ""
    subtitle: str = ""
    cta_text: str = "Comece Agora"
    cta_link: str = "#"
    secondary_cta_text: str = ""
    secondary_cta_link: str = ""
    background: str = "gradient"


@dataclass
class FeaturesSection(SectionBase):
    type: str = "features"
    items: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class CTASection(SectionBase):
    type: str = "cta"
    cta_text: str = "Quero Agora"
    cta_link: str = "#"
    urgency_text: str = ""


@dataclass
class TestimonialsSection(SectionBase):
    type: str = "testimonials"
    items: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class PricingSection(SectionBase):
    type: str = "pricing"
    tiers: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FooterSection(SectionBase):
    type: str = "footer"
    links: List[Dict[str, str]] = field(default_factory=list)
    copyright_text: str = ""


@dataclass
class LandingPageSpec:
    """Complete landing page specification."""

    title: str
    slug: str = ""
    meta_description: str = ""
    sections: List[Any] = field(default_factory=list)
    offer_data: Dict[str, Any] = field(default_factory=dict)
    seo_keywords: List[str] = field(default_factory=list)
    google_analytics_id: str = ""
    facebook_pixel_id: str = ""
    custom_css: str = ""
    custom_js: str = ""

    def add_section(self, section: Any) -> None:
        self.sections.append(section)


class LandingPageGenerator:
    """Generates complete landing pages from spec."""

    def __init__(self):
        from .artifact_generator import ArtifactGenerator

        self._engine = ArtifactGenerator()

    def generate(self, spec: LandingPageSpec, output_dir: str = "output") -> str:
        """Generate and save a landing page from spec."""
        from .artifact_generator import ArtifactSpec, ArtifactType

        # Build campaign data from spec
        campaign_data = {
            "headline": "",
            "subtitle": "",
            "cta_text": "Comece Agora",
            "cta_link": "#",
            "features": [],
            "testimonials": [],
            "pricing": [],
        }

        for section in spec.sections:
            if section.type == "hero":
                campaign_data["headline"] = (
                    campaign_data.get("headline") or section.headline
                )
                campaign_data["subtitle"] = (
                    campaign_data.get("subtitle") or section.subtitle
                )
                campaign_data["cta_text"] = section.cta_text
                campaign_data["cta_link"] = section.cta_link
            elif section.type == "features":
                campaign_data["features"] = section.items
            elif section.type == "testimonials":
                campaign_data["testimonials"] = section.items
            elif section.type == "pricing":
                campaign_data["pricing"] = section.tiers

        # Merge offer data
        campaign_data.update(spec.offer_data)

        artifact_spec = ArtifactSpec(
            type=ArtifactType.LANDING_PAGE,
            title=spec.title,
            description=spec.meta_description,
            campaign_data=campaign_data,
        )

        result = self._engine.generate_artifact(artifact_spec, output_dir)
        return result.file_path or ""

    def generate_affiliate_landing(
        self,
        product_name: str,
        product_description: str,
        affiliate_link: str,
        price: str = "",
        features: Optional[List[str]] = None,
        testimonials: Optional[List[str]] = None,
        urgency: str = "",
        output_dir: str = "output",
    ) -> str:
        """Gera landing page otimizada para produto de afiliado."""
        spec = LandingPageSpec(
            title=f"{product_name} — Lyzer Labs",
            slug=product_name.lower().replace(" ", "-"),
            meta_description=f"Conheça {product_name}: {product_description[:150]}",
        )

        spec.add_section(
            HeroSection(
                headline=f"Transforme seus resultados com {product_name}",
                subtitle=product_description,
                cta_text="Quero Acessar Agora",
                cta_link=affiliate_link,
            )
        )

        if features:
            spec.add_section(
                FeaturesSection(
                    title="Recursos Incríveis",
                    items=[{"title": f, "description": ""} for f in features],
                )
            )

        if testimonials:
            spec.add_section(
                TestimonialsSection(
                    title="O Que Dizem Quem Usou",
                    items=[{"quote": t, "author": ""} for t in testimonials],
                )
            )

        spec.add_section(
            CTASection(
                title="Não Perca Esta Oportunidade",
                cta_text="Quero Agora",
                cta_link=affiliate_link,
                urgency_text=urgency,
            )
        )

        spec.add_section(
            FooterSection(
                copyright_text=f"© {datetime.utcnow().year} Lyzer Labs. Links de afiliado podem gerar comissão.",
            )
        )

        return self.generate(spec, output_dir)

    def batch_generate(
        self, specs: List[LandingPageSpec], output_dir: str = "output"
    ) -> List[str]:
        """Gera múltiplas landing pages de uma vez."""
        return [self.generate(s, output_dir) for s in specs]
