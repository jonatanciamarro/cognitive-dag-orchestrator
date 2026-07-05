"""SEOMultimediaAgent — Gera e otimiza imagens, infográficos e recursos visuais para SEO.

Imagens otimizadas melhoram:
- Core Web Vitals (LCP)
- Google Image Search (fonte de tráfego)
- Engajamento do usuário (tempo na página)
- Acessibilidade (alt text)
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("seo_multimedia")

# Tiny placeholder SVG as 1x1 pixel (when no image library available)
PLACEHOLDER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#1a365d"/>
  <text x="600" y="315" font-family="Arial, sans-serif" font-size="48" fill="white" text-anchor="middle" dominant-baseline="middle">{text}</text>
</svg>"""


class SEOMultimediaAgent(AgentBase):
    """Gera e otimiza recursos visuais para SEO."""

    def __init__(self, **kwargs) -> None:
        super().__init__("seo_multimedia", **kwargs)
        self.output_dir = Path("site_generator/themes/seo/assets/images")

    def generate_hero_image(
        self, title: str, alt_text: str, keyword: str
    ) -> dict[str, Any]:
        """Gera imagem de destaque para o artigo."""
        # Create output dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        slug = title.lower().replace(" ", "-")[:50]

        # Generate SVG hero image
        svg_content = PLACEHOLDER_SVG.replace("{text}", title[:60])

        # Save SVG version
        svg_path = self.output_dir / f"{slug}-hero.svg"
        svg_path.write_text(svg_content)

        # Save placeholder HTML page for image (actual image generation requires Pillow)
        html_path = self.output_dir / f"{slug}-hero.html"
        html_path.write_text(
            f"<html><body><img src='{slug}-hero.svg' alt='{alt_text}' width='1200' height='630'>"
            f"<p>Hero image for: {title}</p></body></html>"
        )

        return {
            "type": "hero_image",
            "slug": slug,
            "paths": {
                "svg": f"images/{slug}-hero.svg",
                "html_preview": f"images/{slug}-hero.html",
            },
            "alt_text": alt_text,
            "dimensions": {"width": 1200, "height": 630},
            "format": "svg",
            "file_size_bytes": len(svg_content),
            "seo_metadata": self._generate_image_seo_metadata(alt_text, keyword),
        }

    def generate_infographic(
        self, title: str, data_points: list[dict[str, Any]], keyword: str
    ) -> dict[str, Any]:
        """Gera infográfico simples em SVG."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        slug = title.lower().replace(" ", "-")[:50]

        # Build SVG infographic
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{max(300, len(data_points) * 80 + 100)}" viewBox="0 0 800 {max(300, len(data_points) * 80 + 100)}">',
            '<rect width="800" height="100%" fill="#f7fafc"/>',
            f'<text x="400" y="50" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#1a365d" text-anchor="middle">{title[:50]}</text>',
        ]

        for i, point in enumerate(data_points):
            y = 100 + i * 70
            label = point.get("label", f"Item {i + 1}")
            value = str(point.get("value", ""))

            lines.append(
                f'<rect x="100" y="{y}" width="15" height="15" fill="#4299e1" rx="3"/>'
            )
            lines.append(
                f'<text x="130" y="{y + 12}" font-family="Arial, sans-serif" font-size="16" fill="#2d3748">{label}</text>'
            )
            lines.append(
                f'<text x="700" y="{y + 12}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#2b6cb0" text-anchor="end">{value}</text>'
            )

        lines.append("</svg>")

        svg_content = "\n".join(lines)
        svg_path = self.output_dir / f"{slug}-infographic.svg"
        svg_path.write_text(svg_content)

        return {
            "type": "infographic",
            "slug": slug,
            "path": f"images/{slug}-infographic.svg",
            "data_points": len(data_points),
            "file_size_bytes": len(svg_content),
            "alt_text": f"Infográfico: {title}",
            "seo_metadata": self._generate_image_seo_metadata(
                f"Infográfico: {title}", keyword
            ),
        }

    def generate_comparison_table_html(
        self, items: list[dict[str, Any]], keyword: str
    ) -> str:
        """Gera tabela comparativa em HTML (schema Table compatível)."""
        if not items:
            return ""

        # Extract headers from first item
        headers = list(items[0].keys()) if items else []
        if not headers:
            return ""

        lines = [
            '<div class="comparison-table-wrapper">',
            '<table class="comparison-table">',
            "<thead><tr>",
        ]
        for h in headers:
            lines.append(f"<th>{h.replace('_', ' ').title()}</th>")
        lines.append("</tr></thead><tbody>")

        for item in items:
            lines.append("<tr>")
            for h in headers:
                val = str(item.get(h, ""))
                lines.append(f"<td>{val}</td>")
            lines.append("</tr>")

        lines.append("</tbody></table></div>")
        return "\n".join(lines)

    def _generate_image_seo_metadata(
        self, alt_text: str, keyword: str
    ) -> dict[str, str]:
        """Gera metadados SEO para imagens."""
        return {
            "alt_text": alt_text[:125],
            "title": alt_text[:60],
            "caption": f"{alt_text} — Guia atualizado {datetime.now(timezone.utc).strftime('%Y')}",
            "description": f"Imagem ilustrativa sobre {keyword}. {alt_text}",
            "file_name": alt_text.lower().replace(" ", "-").replace(":", "")[:60]
            + ".svg",
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        articles = campaign.get("articles", [])
        if isinstance(articles, dict):
            articles = [articles]

        site_url = str(campaign.get("site_url", "https://seudominio.com"))

        all_images = []
        all_infographics = []
        all_tables = []

        for article in articles:
            title = article.get("title", "Untitled")
            keyword = article.get("keyword", "assunto")
            alt_text = article.get("image_alt_text", f"Imagem sobre {title}")

            # Generate hero image
            hero = self.generate_hero_image(title, alt_text, keyword)
            all_images.append(hero)

            # Generate infographic if data available
            data_points = article.get("data_points", [])
            if data_points:
                info = self.generate_infographic(title, data_points, keyword)
                all_infographics.append(info)

            # Generate comparison table if items available
            compare_items = article.get("comparison_items", [])
            if compare_items:
                table_html = self.generate_comparison_table_html(compare_items, keyword)
                if table_html:
                    all_tables.append(
                        {
                            "title": title,
                            "html": table_html,
                        }
                    )

        output = {
            "site_url": site_url,
            "images_generated": len(all_images),
            "infographics_generated": len(all_infographics),
            "tables_generated": len(all_tables),
            "images": all_images,
            "tables": all_tables,
            "recommendations": [
                "Comprimir imagens para WebP para melhorar Core Web Vitals",
                "Verificar se alt text está presente em todas as imagens",
                "Adicionar imagens em artigos com baixo desempenho",
                "Usar formato WebP para produção (SVG para desenvolvimento)",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="multimedia_generation",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(all_images)} imagens, {len(all_infographics)} infográficos, {len(all_tables)} tabelas"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _utcnow_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        from datetime import datetime

        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))
