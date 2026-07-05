"""Email Template Generator — Email marketing & newsletter templates."""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EmailStyle:
    background_color: str = "#0a0a0f"
    text_color: str = "#f0f0ff"
    secondary_color: str = "#a0a0c0"
    accent_color: str = "#7c2dff"
    button_color: str = "#7c2dff"
    border_color: str = "#2a2a3e"


@dataclass
class EmailSection:
    type: str = "paragraph"  # paragraph, image, button, divider, header, footer
    content: str = ""
    align: str = "left"
    style: Dict[str, str] = field(default_factory=dict)


@dataclass
class EmailSpec:
    """Complete email specification."""

    subject: str = ""
    preview_text: str = ""
    sender_name: str = "Lyzer Labs"
    sender_email: str = "hello@lyzerlabs.ai"
    sections: List[EmailSection] = field(default_factory=list)
    style: EmailStyle = field(default_factory=EmailStyle)
    unsubscribe_link: str = "#"
    open_tracking: bool = True


class EmailTemplateGenerator:
    """Generates email templates from spec."""

    def __init__(self):
        from .artifact_generator import ArtifactGenerator

        self._engine = ArtifactGenerator()

    def generate(self, spec: EmailSpec, output_dir: str = "output") -> str:
        """Generate and save an email template from spec."""
        from .artifact_generator import ArtifactSpec, ArtifactType

        body_parts = []
        for section in spec.sections:
            if section.type == "header":
                body_parts.append(
                    f"<h2 style=\"font-family: 'Space Grotesk', sans-serif; "
                    f'margin-bottom: 1rem; text-align: {section.align};">'
                    f"{section.content}</h2>"
                )
            elif section.type == "paragraph":
                body_parts.append(
                    f'<p style="line-height: 1.75; margin-bottom: 1rem; '
                    f'text-align: {section.align};">{section.content}</p>'
                )
            elif section.type == "button":
                link = section.style.get("link", "#")
                body_parts.append(
                    f'<div style="text-align: center; margin: 2rem 0;">'
                    f'<a href="{html.escape(link)}" style="display: inline-block; '
                    f"padding: 1rem 2rem; background: {spec.style.button_color}; "
                    f"color: white; text-decoration: none; border-radius: 0.75rem; "
                    f'font-weight: 600;">{section.content}</a></div>'
                )
            elif section.type == "divider":
                body_parts.append(
                    f'<hr style="border: none; border-top: 1px solid {spec.style.border_color}; '
                    f'margin: 1.5rem 0;">'
                )

        body_html = "\n".join(body_parts)
        campaign_data = {
            "body": body_html,
            "cta_text": "Acessar",
            "cta_link": "#",
            "footer": f"Você está recebendo este email porque se inscreveu no {spec.sender_name}. "
            f"<a href='{spec.unsubscribe_link}' style='color: {spec.style.secondary_color};'>Descadastrar</a>",
        }

        artifact_spec = ArtifactSpec(
            type=ArtifactType.EMAIL,
            title=spec.subject,
            description=spec.preview_text,
            campaign_data=campaign_data,
        )

        result = self._engine.generate_artifact(artifact_spec, output_dir)
        return result.file_path or ""

    def generate_affiliate_email(
        self,
        product_name: str,
        product_description: str,
        affiliate_link: str,
        bonus_text: str = "",
        output_dir: str = "output",
    ) -> str:
        """Gera email promocional para produto de afiliado."""
        spec = EmailSpec(
            subject=f"Recomendação: {product_name}",
            preview_text=product_description[:100],
        )
        spec.sections = [
            EmailSection(
                type="paragraph",
                content="Olá! Hoje quero compartilhar algo especial com você.",
            ),
            EmailSection(
                type="paragraph",
                content=f"<strong>{product_name}</strong> — {product_description}",
            ),
            EmailSection(
                type="button",
                content="Quero Acessar Agora",
                style={"link": affiliate_link},
            ),
        ]
        if bonus_text:
            spec.sections.append(
                EmailSection(type="paragraph", content=f"🎁 {bonus_text}")
            )
        spec.sections.append(EmailSection(type="divider"))
        return self.generate(spec, output_dir)
