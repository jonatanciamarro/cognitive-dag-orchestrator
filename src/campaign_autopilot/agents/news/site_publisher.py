"""SitePublisherAgent — Publica site estático SEO-otimizado.

Gera HTML completo com:
- Schema markup (JSON-LD) para Google/Bing/Yahoo
- Meta tags Open Graph + Twitter Cards
- Sitemap.xml e robots.txt
- Core Web Vitals otimizado (100% estático)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("site_publisher")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR" prefix="og: https://ogp.me/ns#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
    <meta name="language" content="pt-BR">
    <meta name="author" content="{author}">

    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">

    <!-- Open Graph -->
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_description}">
    <meta property="og:image" content="{og_image}">
    <meta property="og:url" content="{og_url}">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="pt_BR">
    <meta property="og:site_name" content="{site_name}">
    <meta property="article:published_time" content="{published_time}">
    <meta property="article:author" content="{author}">
    <meta property="article:section" content="{section}">

    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{twitter_title}">
    <meta name="twitter:description" content="{twitter_description}">
    <meta name="twitter:image" content="{twitter_image}">

    <!-- Schema Markup -->
    <script type="application/ld+json">
{schema_article}
    </script>
    {schema_faq}

    <!-- Canonical URL -->
    <link rel="canonical" href="{canonical_url}">

    <!-- Preload hero image -->
    <link rel="preload" as="image" href="{hero_image}">

    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.8; color: #1a1a2e; background: #fff; }}
        .container {{ max-width: 720px; margin: 0 auto; padding: 0 20px; }}
        header {{ background: #1a365d; color: white; padding: 20px 0; }}
        header .container {{ display: flex; justify-content: space-between; align-items: center; }}
        header a {{ color: white; text-decoration: none; }}
        .site-title {{ font-size: 1.5rem; font-weight: bold; }}
        nav a {{ margin-left: 20px; font-size: 0.9rem; opacity: 0.9; }}
        nav a:hover {{ opacity: 1; }}
        article {{ padding: 40px 0; }}
        h1 {{ font-size: 2rem; line-height: 1.3; margin-bottom: 15px; color: #1a365d; }}
        .meta {{ color: #718096; font-size: 0.9rem; margin-bottom: 20px; }}
        .meta span {{ margin-right: 15px; }}
        .hero-image {{ width: 100%; height: auto; border-radius: 8px; margin-bottom: 30px; }}
        h2 {{ font-size: 1.5rem; margin: 30px 0 15px; color: #2d3748; }}
        h3 {{ font-size: 1.2rem; margin: 25px 0 10px; color: #4a5568; }}
        p {{ margin-bottom: 15px; color: #4a5568; }}
        ul, ol {{ margin: 15px 0; padding-left: 25px; }}
        li {{ margin-bottom: 8px; }}
        .faq-section {{ background: #f7fafc; border-radius: 8px; padding: 20px; margin: 30px 0; }}
        .faq-item {{ margin-bottom: 20px; }}
        .faq-item h3 {{ font-size: 1.1rem; margin-bottom: 8px; color: #2d3748; cursor: pointer; }}
        .related-posts {{ border-top: 2px solid #e2e8f0; padding: 30px 0; margin-top: 40px; }}
        .related-posts h2 {{ margin-bottom: 20px; }}
        .related-posts a {{ display: block; padding: 10px; margin-bottom: 10px; background: #f7fafc; border-radius: 6px; color: #2b6cb0; text-decoration: none; }}
        .related-posts a:hover {{ background: #edf2f7; }}
        .author-box {{ background: #f7fafc; border-radius: 8px; padding: 20px; margin: 30px 0; display: flex; align-items: center; gap: 15px; }}
        .author-info h3 {{ margin: 0; font-size: 1.1rem; }}
        .author-info p {{ font-size: 0.9rem; color: #718096; }}
        .comparison-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .comparison-table th, .comparison-table td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
        .comparison-table th {{ background: #1a365d; color: white; }}
        .comparison-table tr:nth-child(even) {{ background: #f7fafc; }}
        footer {{ background: #1a365d; color: white; padding: 30px 0; margin-top: 40px; }}
        footer a {{ color: #bee3f8; }}
        @media (max-width: 768px) {{ h1 {{ font-size: 1.5rem; }} .container {{ padding: 0 15px; }} }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <a href="/" class="site-title">{site_name}</a>
            <nav>
                <a href="/">Home</a>
                <a href="/{section}/">{section_label}</a>
                <a href="/sobre/">Sobre</a>
                <a href="/contato/">Contato</a>
            </nav>
        </div>
    </header>

    <article>
        <div class="container">
            <div class="meta">
                <span>📅 {published_date}</span>
                <span>📖 {reading_time} min de leitura</span>
                <span>👤 {author}</span>
                <span>🏷️ {section_label}</span>
            </div>

            <h1>{title}</h1>

            <img src="{hero_image}" alt="{hero_alt}" class="hero-image" width="1200" height="630" loading="eager">

            <p>{introduction}</p>

            {content}

            {faq_html}

            {author_html}

            {related_html}
        </div>
    </article>

    <footer>
        <div class="container">
            <p>&copy; {year} {site_name}. Todos os direitos reservados.</p>
            <p><a href="/privacidade/">Política de Privacidade</a> | <a href="/contato/">Contato</a> | <a href="/sobre/">Sobre</a></p>
        </div>
    </footer>
</body>
</html>"""


class SitePublisherAgent(AgentBase):
    """Publica artigos como HTML estático SEO-otimizado."""

    def __init__(self, **kwargs) -> None:
        super().__init__("site_publisher", **kwargs)

    def publish_article(
        self, article: dict[str, Any], site_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Gera HTML completo para um artigo."""
        site_url = site_config.get("site_url", "https://seudominio.com")
        site_name = site_config.get("site_name", "Meu Site")
        section = article.get("section", site_config.get("default_section", "artigo"))
        section_label = {
            "tecnologia": "Tecnologia",
            "financas": "Finanças",
            "saude": "Saúde",
            "carreira": "Carreira",
        }.get(section, section.capitalize())

        keyword = article.get("keyword", "")
        title = article.get("title", "")
        description = article.get("meta_description", "")
        slug = article.get("slug", title.lower().replace(" ", "-")[:50])
        author = article.get("author_name", "Autor")

        now = datetime.now(timezone.utc)

        # Build content HTML
        content_html = ""
        for s in article.get("sections", []):
            heading = s.get("heading", "") if isinstance(s, dict) else str(s)
            text = s.get("content", "") if isinstance(s, dict) else ""
            if heading:
                content_html += f"<h2>{heading}</h2>\n"
            if text:
                paragraphs = text.split("\n\n")
                for p in paragraphs:
                    p = p.strip()
                    if not p:
                        continue
                    if p.startswith("- ") or p.startswith("• "):
                        items = "".join(
                            f"<li>{x.strip('- •')}</li>" for x in p.split("\n")
                        )
                        content_html += f"<ul>{items}</ul>\n"
                    else:
                        content_html += f"<p>{p}</p>\n"

        # Build FAQ HTML
        faq_html = ""
        faq_items = article.get("faq_items", [])
        if faq_items:
            items_html = ""
            for faq in faq_items:
                items_html += f"""
                <div class="faq-item">
                    <h3>{faq.get("question", "")}</h3>
                    <p>{faq.get("answer", "")}</p>
                </div>"""
            faq_html = f"""
            <div class="faq-section">
                <h2>Perguntas Frequentes</h2>
                {items_html}
            </div>"""

        # Build author box HTML
        author_bio = article.get("author_bio", "Especialista no assunto.")
        author_html = f"""
        <div class="author-box">
            <div class="author-info">
                <h3>{author}</h3>
                <p>{author_bio}</p>
            </div>
        </div>"""

        # Build related posts HTML
        related_posts = article.get("related_posts", [])
        related_html = ""
        if related_posts:
            links_html = "".join(
                f'<a href="{p.get("url", "#")}">{p.get("title", "")}</a>'
                for p in related_posts
            )
            related_html = f"""
            <div class="related-posts">
                <h2>Leia também</h2>
                {links_html}
            </div>"""

        # Build schema
        schema_article = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "image": f"{site_url}/images/{slug}-hero.svg",
            "author": {"@type": "Person", "name": author},
            "publisher": {"@type": "Organization", "name": site_name},
            "datePublished": now.isoformat(),
            "dateModified": now.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{site_url}/{section}/{slug}",
            },
            "wordCount": len(content_html.split()),
            "inLanguage": "pt-BR",
        }

        schema_faq_html = ""
        if faq_items:
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f["question"],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f["answer"][:500],
                        },
                    }
                    for f in faq_items[:5]
                ],
            }
            schema_faq_html = f'\n    <script type="application/ld+json">\n{json.dumps(faq_schema, ensure_ascii=False, indent=2)}\n    </script>'

        # Calculate reading time
        word_count = len(content_html.split()) + len(
            article.get("introduction", "").split()
        )
        reading_time = max(1, word_count // 200)

        # Render HTML
        html = HTML_TEMPLATE.format(
            title=title[:60],
            description=description[:160],
            keywords=keyword,
            og_title=title[:60],
            og_description=description[:200],
            og_image=f"{site_url}/images/{slug}-hero.svg",
            og_url=f"{site_url}/{section}/{slug}",
            site_name=site_name,
            published_time=now.isoformat(),
            author=author,
            section=section,
            twitter_title=title[:60],
            twitter_description=description[:200],
            twitter_image=f"{site_url}/images/{slug}-hero.svg",
            schema_article=json.dumps(schema_article, ensure_ascii=False, indent=2),
            schema_faq=schema_faq_html,
            canonical_url=f"{site_url}/{section}/{slug}",
            hero_image=f"/images/{slug}-hero.svg",
            hero_alt=article.get("image_alt_text", title),
            published_date=now.strftime("%d/%m/%Y"),
            reading_time=reading_time,
            introduction=article.get("introduction", ""),
            content=content_html,
            faq_html=faq_html,
            author_html=author_html,
            related_html=related_html,
            year=now.year,
            section_label=section_label,
        )

        # Save file
        output_dir = Path("site") / section / slug
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(html, encoding="utf-8")

        return {
            "title": title,
            "url": f"{site_url}/{section}/{slug}",
            "file_path": str(output_dir / "index.html"),
            "word_count": word_count,
            "reading_time": reading_time,
            "html_size_bytes": len(html.encode("utf-8")),
            "published_at": now.isoformat(),
            "slug": slug,
        }

    def publish_sitemap(
        self, articles_meta: list[dict], site_url: str, output_dir: Path
    ) -> None:
        """Gera sitemap.xml completo."""
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]

        # Homepage
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{site_url}/</loc>")
        xml_lines.append(
            f"    <lastmod>{datetime.now(timezone.utc).strftime('%Y-%m-%d')}</lastmod>"
        )
        xml_lines.append("    <changefreq>daily</changefreq>")
        xml_lines.append("    <priority>1.0</priority>")
        xml_lines.append("  </url>")

        for art in articles_meta:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{art['url']}</loc>")
            xml_lines.append(
                f"    <lastmod>{art.get('published_at', datetime.now(timezone.utc).isoformat())[:10]}</lastmod>"
            )
            xml_lines.append("    <changefreq>weekly</changefreq>")
            xml_lines.append("    <priority>0.8</priority>")
            xml_lines.append("  </url>")

        xml_lines.append("</urlset>")
        (output_dir / "sitemap.xml").write_text("\n".join(xml_lines), encoding="utf-8")

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        articles = campaign.get("articles", [])
        if isinstance(articles, dict):
            articles = [articles]

        site_config = {
            "site_url": str(campaign.get("site_url", "https://seudominio.com")),
            "site_name": str(campaign.get("site_name", "Meu Site")),
            "default_section": str(campaign.get("section", "artigo")),
        }

        published = []
        for article in articles:
            result = self.publish_article(article, site_config)
            published.append(result)
            log.info(
                "article_published", title=article.get("title", ""), url=result["url"]
            )

        # Publish sitemap
        output_dir = Path("site")
        self.publish_sitemap(published, site_config["site_url"], output_dir)

        # Create index page listing all articles
        self._publish_index(published, site_config)

        output = {
            "site_url": site_config["site_url"],
            "articles_published": len(published),
            "articles": published,
            "sitemap_url": f"{site_config['site_url']}/sitemap.xml",
            "total_site_size_bytes": sum(a["html_size_bytes"] for a in published),
            "recommendations": [
                f"Submeter sitemap ao Google Search Console: {site_config['site_url']}/sitemap.xml",
                "Submeter sitemap ao Bing Webmaster Tools",
                "Verificar renderização no Google Rich Results Test",
                "Configurar Cloudflare Pages para deploy automático",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="site_publish",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Publicou {len(published)} artigos + sitemap em {output_dir}"],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _publish_index(self, articles: list[dict], site_config: dict[str, Any]) -> None:
        """Gera página inicial listando artigos."""
        site_name = site_config["site_name"]
        site_url = site_config["site_url"]

        articles_html = ""
        for art in articles:
            date = art.get("published_at", "")[:10]
            articles_html += f"""
            <article class="post-preview">
                <h2><a href="{art["url"]}">{art["title"]}</a></h2>
                <div class="meta">📅 {date} | 📖 {art["reading_time"]} min</div>
            </article>"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_name}</title>
    <meta name="description" content="Conteúdo útil e atualizado sobre tecnologia, finanças, saúde e carreira.">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; line-height: 1.8; color: #1a1a2e; }}
        .container {{ max-width: 720px; margin: 0 auto; padding: 20px; }}
        header {{ background: #1a365d; color: white; padding: 40px 0; text-align: center; }}
        header h1 {{ font-size: 2rem; margin-bottom: 10px; }}
        header p {{ opacity: 0.9; }}
        .post-preview {{ padding: 20px 0; border-bottom: 1px solid #e2e8f0; }}
        .post-preview h2 a {{ color: #2b6cb0; text-decoration: none; }}
        .post-preview h2 a:hover {{ text-decoration: underline; }}
        .meta {{ color: #718096; font-size: 0.9rem; }}
        footer {{ text-align: center; padding: 30px; color: #718096; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{site_name}</h1>
            <p>Conteúdo útil para suas decisões</p>
        </div>
    </header>
    <main class="container">
        <h2 style="margin: 30px 0 20px;">Últimos Artigos</h2>
        {articles_html}
    </main>
    <footer>
        <p>&copy; {datetime.now().year} {site_name}</p>
    </footer>
</body>
</html>"""

        (Path("site") / "index.html").write_text(html, encoding="utf-8")

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
