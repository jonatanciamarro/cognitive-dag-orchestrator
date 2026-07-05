"""SEOTechnicalAgent — Schema markup, meta tags, Open Graph, URLs amigáveis.

Gera todo o markup técnico necessário para Google, Bing e Yahoo entenderem
e ranquearem o conteúdo corretamente.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("seo_technical")


class SEOTechnicalAgent(AgentBase):
    """Aplica markup técnico SEO em artigos."""

    def __init__(self, **kwargs) -> None:
        super().__init__("seo_technical", **kwargs)

    def generate_schema_article(
        self, article: dict[str, Any], site_url: str
    ) -> dict[str, Any]:
        """Gera schema Article completo."""
        now = datetime.now(timezone.utc).isoformat()
        slug = article.get("slug", "")

        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article.get("title", ""),
            "description": article.get("meta_description", ""),
            "image": f"{site_url}/images/{slug}-hero.jpg",
            "author": {
                "@type": "Person",
                "name": article.get("author_name", "Autor"),
                "url": f"{site_url}/autor/"
                + article.get("author_name", "autor").lower().replace(" ", "-"),
            },
            "publisher": {
                "@type": "Organization",
                "name": self._extract_domain(site_url),
                "logo": {"@type": "ImageObject", "url": f"{site_url}/logo.png"},
            },
            "datePublished": now,
            "dateModified": now,
            "mainEntityOfPage": {"@type": "WebPage", "@id": f"{site_url}/{slug}"},
            "wordCount": len(
                article.get("body", article.get("introduction", "")).split()
            ),
            "timeRequired": "PT"
            + str(max(1, len(article.get("body", "").split()) // 200))
            + "M",
            "inLanguage": "pt-BR",
            "isAccessibleForFree": True,
        }

    def generate_schema_faq(
        self, faq_items: list[dict[str, str]]
    ) -> dict[str, Any] | None:
        """Gera schema FAQPage."""
        if not faq_items or len(faq_items) < 2:
            return None

        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item["answer"][:500],
                    },
                }
                for item in faq_items[:5]  # Max 5 FAQ items
            ],
        }

    def generate_schema_breadcrumb(
        self, section: str, article_title: str, site_url: str
    ) -> dict[str, Any]:
        """Gera schema BreadcrumbList."""
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": site_url},
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": section.capitalize(),
                    "item": f"{site_url}/{section}",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": article_title[:60],
                    "item": f"{site_url}/{article_title.lower().replace(' ', '-')[:50]}",
                },
            ],
        }

    def generate_meta_tags(
        self, article: dict[str, Any], site_url: str, section: str
    ) -> dict[str, str]:
        """Gera todas as meta tags necessárias."""
        title = article.get("title", "")
        description = article.get("meta_description", "")
        slug = article.get("slug", title.lower().replace(" ", "-")[:50])
        image = f"{site_url}/images/{slug}-hero.jpg"

        tags = {}

        # Standard meta
        tags["title"] = title
        tags["description"] = description
        tags["keywords"] = article.get("keyword", "")
        tags["robots"] = "index, follow, max-snippet:-1, max-image-preview:large"
        tags["viewport"] = "width=device-width, initial-scale=1.0"
        tags["charset"] = "UTF-8"
        tags["language"] = "pt-BR"
        tags["author"] = article.get("author_name", "Autor")

        # Open Graph (Facebook, LinkedIn, Pinterest)
        tags["og:title"] = title[:60]
        tags["og:description"] = description[:200]
        tags["og:image"] = image
        tags["og:url"] = f"{site_url}/{slug}"
        tags["og:type"] = "article"
        tags["og:site_name"] = self._extract_domain(site_url)
        tags["og:locale"] = "pt_BR"
        tags["article:published_time"] = datetime.now(timezone.utc).isoformat()
        tags["article:author"] = article.get("author_name", "Autor")
        tags["article:section"] = section

        # Twitter Cards
        tags["twitter:card"] = "summary_large_image"
        tags["twitter:title"] = title[:60]
        tags["twitter:description"] = description[:200]
        tags["twitter:image"] = image

        return tags

    def generate_sitemap_entry(
        self, article: dict[str, Any], site_url: str, section: str
    ) -> dict[str, Any]:
        """Gera entrada de sitemap para o artigo."""
        slug = article.get(
            "slug", article.get("title", "").lower().replace(" ", "-")[:50]
        )
        return {
            "loc": f"{site_url}/{section}/{slug}",
            "lastmod": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "changefreq": "weekly",
            "priority": 0.8 if article.get("intent") == "commercial" else 0.6,
        }

    def generate_site_sitemap(self, entries: list[dict[str, Any]]) -> str:
        """Gera XML de sitemap."""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for entry in entries:
            lines.append("  <url>")
            lines.append(f"    <loc>{entry['loc']}</loc>")
            lines.append(f"    <lastmod>{entry['lastmod']}</lastmod>")
            lines.append(f"    <changefreq>{entry['changefreq']}</changefreq>")
            lines.append(f"    <priority>{entry['priority']}</priority>")
            lines.append("  </url>")
        lines.append("</urlset>")
        return "\n".join(lines)

    def generate_robots_txt(
        self, site_url: str, sitemap_path: str = "/sitemap.xml"
    ) -> str:
        """Gera robots.txt otimizado."""
        return f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /assets/
Sitemap: {site_url}{sitemap_path}

# Google-specific
User-agent: Googlebot
Allow: /
Crawl-delay: 1

# Bing-specific
User-agent: Bingbot
Allow: /
Crawl-delay: 1

# Yahoo-specific
User-agent: Slurp
Allow: /
Crawl-delay: 2
"""

    def _extract_domain(self, url: str) -> str:
        """Extrai nome do domínio de uma URL."""
        url = url.replace("https://", "").replace("http://", "")
        return url.split("/")[0].replace("www.", "")

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        articles = campaign.get("articles", [])
        if isinstance(articles, dict):
            articles = [articles]

        site_url = str(campaign.get("site_url", "https://seudominio.com"))
        section = str(campaign.get("section", "artigo"))

        schemas = []
        meta_tags_list = []
        sitemap_entries = []

        for article in articles:
            # Generate all schemas
            schema_article = self.generate_schema_article(article, site_url)
            schema_faq = None
            if article.get("faq_items"):
                schema_faq = self.generate_schema_faq(article.get("faq_items", []))
            schema_breadcrumb = self.generate_schema_breadcrumb(
                section, article.get("title", ""), site_url
            )

            schemas.append(
                {
                    "title": article.get("title", "Untitled"),
                    "schema_article": schema_article,
                    "schema_faq": schema_faq,
                    "schema_breadcrumb": schema_breadcrumb,
                }
            )

            # Generate meta tags
            meta_tags = self.generate_meta_tags(article, site_url, section)
            meta_tags_list.append(
                {
                    "title": article.get("title", "Untitled"),
                    "meta_tags": meta_tags,
                }
            )

            # Generate sitemap entry
            sitemap_entry = self.generate_sitemap_entry(article, site_url, section)
            sitemap_entries.append(sitemap_entry)

        # Generate full sitemap XML
        sitemap_xml = self.generate_site_sitemap(sitemap_entries)
        robots_txt = self.generate_robots_txt(site_url)

        output = {
            "site_url": site_url,
            "articles_processed": len(articles),
            "schemas": schemas,
            "meta_tags": meta_tags_list,
            "sitemap_entries": sitemap_entries,
            "sitemap_xml": sitemap_xml,
            "robots_txt": robots_txt,
            "technical_score": self._calculate_technical_score(schemas),
            "recommendations": [
                "Submeter sitemap ao Google Search Console imediatamente",
                "Submeter sitemap ao Bing Webmaster Tools",
                "Verificar Core Web Vitals após publicação",
                "Configurar Google Analytics 4 para monitorar tráfego",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="seo_technical",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Aplicou markup técnico em {len(articles)} artigos"],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _calculate_technical_score(self, schemas: list[dict]) -> dict[str, Any]:
        """Calcula score técnico baseado nos schemas gerados."""
        total = len(schemas)
        with_faq = sum(1 for s in schemas if s.get("schema_faq"))
        return {
            "articles_with_schema": total,
            "articles_with_faq_schema": with_faq,
            "completeness_score": round(70 + (with_faq / max(total, 1)) * 30, 1),
        }

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
