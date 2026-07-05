"""Complete static site generator — creates deployable HTML site from agent output."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class SiteGenerator:
    """Gera site estático completo a partir do output dos agentes.

    Produz:
    - index.html (home com últimos artigos)
    - /blog/artigo-slug.html (cada artigo)
    - /pages/sobre.html, /pages/contato.html
    - lead-capture.html (landing page)
    - sitemap.xml
    - robots.txt
    - rss.xml
    - CSS (tailwind-like minimal)
    """

    def __init__(self, output_dir: str | Path = "site"):
        self.output_dir = Path(output_dir)
        self.site_url = ""  # Configurar depois

    def generate(
        self,
        articles: list[dict[str, Any]],
        repurposed: list[dict[str, Any]] | None = None,
        lead_magnets: list[dict[str, Any]] | None = None,
        pin_data: list[dict[str, Any]] | None = None,
        niche: str = "marketing digital",
        site_title: str = "Guia Completo para Iniciantes",
        site_url: str = "https://seudominio.com",
        author: str = "Equipe Autopilot",
    ) -> dict[str, int]:
        """Generate complete static site. Returns file counts."""
        self.site_url = site_url.rstrip("/")
        now = datetime.now(timezone.utc)

        # Create directories
        dirs = ["", "blog", "pages", "assets/css", "assets/js"]
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)

        file_count = 0

        # Generate CSS
        file_count += self._generate_css()

        # Generate pages
        file_count += self._generate_home(articles, repurposed, niche, site_title, now)
        file_count += self._generate_about(niche, author)
        file_count += self._generate_contact()
        file_count += self._generate_privacy()
        file_count += self._generate_disclosure()

        # Generate blog articles
        for i, article in enumerate(articles):
            file_count += self._generate_article(article, i, niche, site_title, now)

        # Generate lead capture landing page
        if lead_magnets:
            file_count += self._generate_lead_capture(lead_magnets, niche)

        # Generate sitemap + robots + RSS
        file_count += self._generate_sitemap(articles, now)
        file_count += self._generate_robots()
        file_count += self._generate_rss(articles, site_title, now)

        return {
            "files_generated": file_count,
            "articles_published": len(articles),
            "output_directory": str(self.output_dir.absolute()),
            "site_url": site_url,
        }

    # ── HTML Helpers ──────────────────────────────────────────────

    def _shell(
        self, title: str, body: str, meta_desc: str = "", canonical: str = ""
    ) -> str:
        """Generate full HTML5 document shell."""
        meta = (
            f'<meta name="description" content="{self._h(meta_desc)}">'
            if meta_desc
            else ""
        )
        canon = (
            f'<link rel="canonical" href="{self._h(canonical)}">' if canonical else ""
        )
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._h(title)}</title>
    {meta}
    {canon}
    <meta name="robots" content="index, follow">
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="nav">
        <div class="container">
            <a href="/" class="logo">Autopilot</a>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="/blog/">Blog</a>
                <a href="/pages/sobre.html">Sobre</a>
                <a href="/pages/contato.html">Contato</a>
            </div>
        </div>
    </nav>
    <main class="container">
        {body}
    </main>
    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} Autopilot. Alguns links são de afiliados.</p>
        </div>
    </footer>
</body>
</html>"""

    @staticmethod
    def _h(text: str) -> str:
        """Escape HTML entities."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    @staticmethod
    def _md_to_html(text: str) -> str:
        """Minimal markdown-like formatting to HTML."""
        text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
        text = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
        text = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
        text = re.sub(r"^- (.*?)$", r"<li>\1</li>", text, flags=re.MULTILINE)
        text = re.sub(r"(<li>.*?</li>)", r"<ul>\1</ul>", text, flags=re.DOTALL)
        text = re.sub(r"\n\n", r"</p><p>", text)
        text = f"<p>{text}</p>"
        text = re.sub(r"<p><ul>", "<ul>", text)
        text = re.sub(r"</ul></p>", "</ul>", text)
        return text

    # ── CSS ───────────────────────────────────────────────────────

    def _generate_css(self) -> int:
        css = """*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6;color:#333;background:#fafafa}
.container{max-width:900px;margin:0 auto;padding:0 20px}
.nav{background:#1a1a2e;color:#fff;padding:15px 0;position:sticky;top:0;z-index:100}
.nav .container{display:flex;justify-content:space-between;align-items:center}
.nav a{color:#fff;text-decoration:none}
.logo{font-size:1.4em;font-weight:700}
.nav-links a{margin-left:20px;font-size:.95em}
.nav-links a:hover{color:#e94560}
.hero{text-align:center;padding:60px 0;background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;margin-bottom:40px;border-radius:12px}
.hero h1{font-size:2.2em;margin-bottom:15px}
.hero p{font-size:1.15em;opacity:.9;max-width:600px;margin:0 auto 25px}
.cta-btn{display:inline-block;background:#e94560;color:#fff;padding:14px 35px;border-radius:8px;text-decoration:none;font-weight:600;font-size:1.05em}
.cta-btn:hover{opacity:.9}
.card{background:#fff;border-radius:10px;padding:25px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);transition:transform .2s}
.card:hover{transform:translateY(-3px)}
.card h2{margin-bottom:10px}
.card h2 a{color:#1a1a2e;text-decoration:none}
.card .meta{color:#666;font-size:.9em;margin-bottom:10px}
.card p{color:#555}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.article-body h2{margin:30px 0 15px;color:#1a1a2e}
.article-body h3{margin:20px 0 10px;color:#333}
.article-body p{margin-bottom:15px;color:#444}
.article-body ul{margin:10px 0 20px 20px}
.article-body li{margin-bottom:8px}
.article-body a{color:#e94560}
.offer-box{background:#f0f8ff;border:1px solid #d0e8f7;border-radius:10px;padding:20px;margin:25px 0}
.offer-box h3{color:#1a1a2e;margin-bottom:10px}
.offer-box a{display:inline-block;background:#1a1a2e;color:#fff;padding:10px 25px;border-radius:6px;text-decoration:none;margin-top:10px}
.disclosure{font-size:.85em;color:#888;margin-top:30px;padding-top:15px;border-top:1px solid #eee}
.footer{background:#1a1a2e;color:#aaa;text-align:center;padding:25px 0;margin-top:60px}
.form-section{background:#fff;border-radius:10px;padding:30px;max-width:500px;margin:30px auto;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.form-section h2{text-align:center;margin-bottom:20px}
.form-section input{width:100%;padding:12px;margin-bottom:15px;border:1px solid #ddd;border-radius:6px;font-size:1em}
.form-section button{width:100%;padding:14px;background:#e94560;color:#fff;border:none;border-radius:6px;font-size:1.05em;cursor:pointer;font-weight:600}
.form-section button:hover{opacity:.9}
@media(max-width:600px){.two-col{grid-template-columns:1fr}.hero h1{font-size:1.6em}}
"""
        (self.output_dir / "assets/css/style.css").write_text(encoding="utf-8", data=css)
        return 1

    # ── Pages ─────────────────────────────────────────────────────

    def _generate_home(
        self,
        articles: list,
        repurposed: list | None,
        niche: str,
        site_title: str,
        now: datetime,
    ) -> int:
        articles_html = ""
        for i, art in enumerate(articles):
            title = art.get("title", "Artigo")
            slug = art.get("slug", f"artigo-{i}")
            meta = art.get("meta_description", "")
            words = art.get("word_count", 0)
            articles_html += f"""
            <div class="card">
                <h2><a href="/blog/{self._h(slug)}.html">{self._h(title)}</a></h2>
                <div class="meta">📝 {words} palavras • {now.strftime("%d/%m/%Y")}</div>
                <p>{self._h(meta[:150])}</p>
            </div>"""

        channels_html = ""
        if repurposed:
            for item in repurposed[:3]:
                src = item.get("source_article", {})
                title = src.get("title", "")
                channels_html += f"""
            <div class="card">
                <h3>📺 YouTube</h3>
                <p>{self._h(title)} — roteiro completo pronto para gravação.</p>
            </div>"""

        body = f"""
        <section class="hero">
            <h1>{self._h(site_title)}</h1>
            <p>Conteúdo completo sobre {self._h(niche)}. Guias, reviews e tutoriais para ajudar você a começar.</p>
            <a href="/lead-capture.html" class="cta-btn">📥 Baixar Guia Grátis</a>
        </section>

        <section>
            <h2 style="margin-bottom:20px">📝 Últimos Artigos</h2>
            {articles_html if articles_html else "<p>Nenhum artigo publicado ainda.</p>"}
        </section>

        <section style="margin-top:40px">
            <h2 style="margin-bottom:20px">📺 Conteúdo em Vídeo</h2>
            <div class="two-col">
                {channels_html if channels_html else '<div class="card"><p>Em breve!</p></div>'}
            </div>
        </section>

        <section class="form-section" style="margin-top:40px">
            <h2>🎯 Receba Conteúdo Exclusivo</h2>
            <p style="text-align:center;margin-bottom:20px">Inscreva-se e receba dicas sobre {self._h(niche)} diretamente no seu email.</p>
            <form>
                <input type="text" placeholder="Seu nome" required>
                <input type="email" placeholder="Seu melhor email" required>
                <button type="submit">📥 Quero Receber</button>
            </form>
        </section>"""

        html = self._shell(
            site_title, body, f"Guia completo sobre {niche} para iniciantes."
        )
        (self.output_dir / "index.html").write_text(encoding="utf-8", data=html)
        (self.output_dir / "lead-capture.html").write_text(encoding="utf-8", data=
            html.replace('class="cta-btn"', 'class="cta-btn" style="display:none"')
        )
        return 2

    def _generate_article(
        self, article: dict, idx: int, niche: str, site_title: str, now: datetime
    ) -> int:
        title = article.get("title", "Artigo")
        slug = article.get("slug", f"artigo-{idx}")
        body = article.get("body", "")
        meta = article.get("meta_description", "")
        keyword = article.get("keyword", "")
        words = article.get("word_count", 0) or len(body.split())

        content_html = self._md_to_html(body)

        html = self._shell(
            f"{title} | {site_title}",
            f"""
            <article>
                <h1>{self._h(title)}</h1>
                <div class="meta" style="margin-bottom:25px">
                    📝 {words} palavras • {now.strftime("%d/%m/%Y")} • {self._h(niche)}
                </div>
                <div class="article-body">
                    {content_html}
                </div>
                <div class="disclosure">
                    *Alguns links neste artigo são de afiliados. Se você comprar através deles,
                    eu posso ganhar uma comissão sem custo adicional para você.
                </div>
            </article>
            <section class="form-section" style="margin-top:40px">
                <h2>📩 Gostou do conteúdo?</h2>
                <p style="text-align:center;margin-bottom:15px">Receba mais artigos como este diretamente no seu email.</p>
                <form>
                    <input type="text" placeholder="Seu nome" required>
                    <input type="email" placeholder="Seu melhor email" required>
                    <button type="submit">📥 Inscrever</button>
                </form>
            </section>
            <p style="margin-top:20px"><a href="/">← Voltar para Home</a></p>
            """,
            meta,
            f"{self.site_url}/blog/{slug}.html",
        )
        (self.output_dir / f"blog/{slug}.html").write_text(encoding="utf-8", data=html)
        return 1

    def _generate_about(self, niche: str, author: str) -> int:
        body = f"""
        <h1>Sobre Nós</h1>
        <p>Somos apaixonados por {self._h(niche)} e acreditamos que conhecimento de qualidade
        deve ser acessível a todos. Criamos este site para compartilhar guias completos,
        reviews honestos e tutoriais práticos.</p>
        <p>Nosso objetivo é ajudar iniciantes a darem os primeiros passos sem cair em
        armadilhas comuns. Todo conteúdo é cuidadosamente pesquisado e testado antes de ser publicado.</p>
        <p><strong>Transparência:</strong> Alguns links neste site são de afiliados. Isso significa que
        podemos ganhar uma pequena comissão se você comprar através deles, sem custo adicional para você.</p>
        """
        html = self._shell("Sobre | Autopilot", body, f"Sobre o site de {niche}")
        (self.output_dir / "pages/sobre.html").write_text(encoding="utf-8", data=html)
        return 1

    def _generate_contact(self) -> int:
        body = """
        <h1>Contato</h1>
        <p>Tem dúvidas, sugestões ou quer entrar em contato? Preencha o formulário abaixo:</p>
        <div class="form-section">
            <form>
                <input type="text" placeholder="Seu nome" required>
                <input type="email" placeholder="Seu email" required>
                <textarea placeholder="Sua mensagem" rows="5" style="width:100%;padding:12px;border:1px solid #ddd;border-radius:6px;font-size:1em;margin-bottom:15px;font-family:inherit"></textarea>
                <button type="submit">📨 Enviar Mensagem</button>
            </form>
        </div>
        """
        html = self._shell("Contato | Autopilot", body, "Entre em contato conosco")
        (self.output_dir / "pages/contato.html").write_text(encoding="utf-8", data=html)
        return 1

    def _generate_privacy(self) -> int:
        body = """
        <h1>Política de Privacidade</h1>
        <p>Sua privacidade é importante para nós. Esta política descreve como coletamos, usamos e protegemos suas informações.</p>
        <h2>Informações que coletamos</h2>
        <p>Coletamos apenas as informações que você voluntariamente fornece, como nome e email ao se inscrever em nossa newsletter.</p>
        <h2>Cookies</h2>
        <p>Utilizamos cookies para melhorar sua experiência de navegação. Você pode desativá-los nas configurações do seu navegador.</p>
        <h2>Links de Afiliados</h2>
        <p>Alguns links em nosso site são de afiliados. Quando você clica nesses links e faz uma compra, podemos receber uma comissão.</p>
        <h2>Contato</h2>
        <p>Para dúvidas sobre esta política, entre em contato através da nossa página de contato.</p>
        """
        html = self._shell("Política de Privacidade | Autopilot", body)
        (self.output_dir / "pages/privacidade.html").write_text(encoding="utf-8", data=html)
        return 1

    def _generate_disclosure(self) -> int:
        body = """
        <h1>Política de Disclosure</h1>
        <p>Em conformidade com as regulamentações de defesa do consumidor, informamos que:</p>
        <p><strong>Links de Afiliados:</strong> Alguns links neste site são links de afiliados. Se você clicar em um link e
        fizer uma compra, podemos receber uma comissão sem custo adicional para você.</p>
        <p><strong>Conteúdo:</strong> Todo o conteúdo é criado de forma independente e baseado em pesquisas e experiências reais.
        Nossas opiniões são honestas e não são influenciadas por parcerias.</p>
        <p><strong>Transparência:</strong> Acreditamos em transparência total. Se um conteúdo contém links de afiliados,
        isso será claramente indicado.</p>
        """
        html = self._shell("Política de Disclosure | Autopilot", body)
        (self.output_dir / "pages/disclosure.html").write_text(encoding="utf-8", data=html)
        return 1

    def _generate_lead_capture(self, lead_magnets: list[dict], niche: str) -> int:
        magnets_html = ""
        for lm in lead_magnets:
            magnets_html += f"""
            <div class="card">
                <h3>{self._h(lm.get("title", ""))}</h3>
                <p>{self._h(lm.get("subtitle", ""))}</p>
                <p style="margin-top:8px;color:#666">📄 Formato: {lm.get("format", "PDF")}</p>
            </div>"""

        body = f"""
        <section class="hero">
            <h1>📥 Materiais Gratuitos</h1>
            <p>Baixe guias, checklists e templates para ajudar você em {self._h(niche)}.</p>
        </section>
        <section>
            <h2 style="margin-bottom:20px">🎁 Materiais Disponíveis</h2>
            <div class="two-col">
                {magnets_html}
            </div>
        </section>
        <section class="form-section">
            <h2>📩 Baixe Agora</h2>
            <p style="text-align:center;margin-bottom:15px">Deixe seu email e receba o material gratuito:</p>
            <form>
                <input type="text" placeholder="Seu nome" required>
                <input type="email" placeholder="Seu melhor email" required>
                <button type="submit">📥 Baixar Grátis</button>
            </form>
        </section>
        """
        html = self._shell(
            "Materiais Gratuitos | Autopilot", body, f"Baixe guias grátis sobre {niche}"
        )
        (self.output_dir / "lead-capture.html").write_text(encoding="utf-8", data=html)
        return 1

    # ── SEO ────────────────────────────────────────────────────────

    def _generate_sitemap(self, articles: list[dict], now: datetime) -> int:
        """Generate sitemap.xml."""
        urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

        pages = [
            ("", "1.0", "daily"),
            ("/lead-capture.html", "0.9", "weekly"),
            ("/pages/sobre.html", "0.7", "monthly"),
            ("/pages/contato.html", "0.5", "monthly"),
            ("/pages/privacidade.html", "0.3", "yearly"),
            ("/pages/disclosure.html", "0.3", "yearly"),
        ]
        for path, priority, freq in pages:
            u = SubElement(urlset, "url")
            SubElement(u, "loc").text = f"{self.site_url}{path}"
            SubElement(u, "lastmod").text = now.strftime("%Y-%m-%d")
            SubElement(u, "changefreq").text = freq
            SubElement(u, "priority").text = priority

        for art in articles:
            slug = art.get("slug", "artigo")
            u = SubElement(urlset, "url")
            SubElement(u, "loc").text = f"{self.site_url}/blog/{slug}.html"
            SubElement(u, "lastmod").text = now.strftime("%Y-%m-%d")
            SubElement(u, "changefreq").text = "weekly"
            SubElement(u, "priority").text = "0.8"

        xml_str = minidom.parseString(tostring(urlset)).toprettyxml(indent="  ")
        (self.output_dir / "sitemap.xml").write_text(encoding="utf-8", data=xml_str)
        return 1

    def _generate_robots(self) -> int:
        """Generate robots.txt."""
        content = f"""User-agent: *
Allow: /
Sitemap: {self.site_url}/sitemap.xml
"""
        (self.output_dir / "robots.txt").write_text(encoding="utf-8", data=content)
        return 1

    def _generate_rss(
        self, articles: list[dict], site_title: str, now: datetime
    ) -> int:
        """Generate RSS feed."""
        rss = Element("rss", version="2.0")
        channel = SubElement(rss, "channel")
        SubElement(channel, "title").text = site_title
        SubElement(channel, "link").text = self.site_url
        SubElement(
            channel, "description"
        ).text = f"Conteúdo atualizado sobre {site_title}"
        SubElement(channel, "language").text = "pt-BR"
        SubElement(channel, "lastBuildDate").text = now.strftime(
            "%a, %d %b %Y %H:%M:%S %z"
        )

        for art in articles:
            title = art.get("title", "Artigo")
            slug = art.get("slug", "artigo")
            desc = art.get("meta_description", "")
            body = art.get("body", "")[:300]

            item = SubElement(channel, "item")
            SubElement(item, "title").text = title
            SubElement(item, "link").text = f"{self.site_url}/blog/{slug}.html"
            SubElement(item, "description").text = desc or body
            SubElement(item, "pubDate").text = now.strftime("%a, %d %b %Y %H:%M:%S %z")

        xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent="  ")
        (self.output_dir / "rss.xml").write_text(encoding="utf-8", data=xml_str)
        return 1
