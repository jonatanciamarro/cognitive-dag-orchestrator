"""InternalLinkerAgent — Cria malha de links internos entre artigos.

Links internos são um dos sinais mais importantes para SEO:
- Distribuem autoridade entre páginas
- Melhoram a navegação do usuário
- Ajudam buscadores a entender a estrutura do site
- Aumentam tempo na página
"""

from __future__ import annotations


from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("internal_linker")


class InternalLinkerAgent(AgentBase):
    """Cria e gerencia links internos entre artigos."""

    def __init__(self, **kwargs) -> None:
        super().__init__("internal_linker", **kwargs)

    def find_related_articles(
        self, article_keyword: str, existing_articles: list[dict]
    ) -> list[dict]:
        """Encontra artigos relacionados no banco."""
        related = []
        keyword_terms = article_keyword.lower().split()

        for art in existing_articles:
            art_keyword = art.get("keyword", "").lower()
            art_title = art.get("title", "").lower()

            # Check for keyword overlap
            overlap = sum(
                1 for term in keyword_terms if term in art_keyword or term in art_title
            )
            if overlap > 0:
                related.append(
                    {
                        "title": art.get("title", ""),
                        "url": art.get("slug", ""),
                        "relevance": overlap / max(len(keyword_terms), 1),
                        "reason": f"Compartilha termos com '{article_keyword}'",
                    }
                )

        # Sort by relevance
        related.sort(key=lambda x: -x["relevance"])
        return related[:5]  # Max 5 related articles

    def build_contextual_links(
        self, article_text: str, related_articles: list[dict]
    ) -> list[dict]:
        """Encontra pontos no texto onde links internos podem ser inseridos."""
        link_points = []
        text_lower = article_text.lower()

        for rel in related_articles:
            title = rel.get("title", "")
            title_terms = title.lower().split()[:3]  # Use first 3 words

            for term in title_terms:
                if len(term) < 3:
                    continue
                idx = text_lower.find(term)
                if idx >= 0:
                    # Extract context around the match
                    start = max(0, idx - 30)
                    end = min(len(article_text), idx + len(term) + 30)
                    context = article_text[start:end]

                    link_points.append(
                        {
                            "article_title": title,
                            "article_url": rel.get("url", ""),
                            "matched_term": term,
                            "context_snippet": f"...{context.strip()}...",
                            "relevance": rel.get("relevance", 0.5),
                            "position": idx,
                        }
                    )
                    break  # One link per related article

        # Sort by position in text
        link_points.sort(key=lambda x: x["position"])
        return link_points[:10]  # Max 10 internal links per article

    def build_related_posts_section(
        self,
        article_keyword: str,
        existing_articles: list[dict],
        site_url: str,
        section: str,
    ) -> list[dict]:
        """Gera seção de 'Artigos Relacionados' para o final do artigo."""
        related = self.find_related_articles(article_keyword, existing_articles)

        posts = []
        for rel in related[:4]:  # Max 4 in related posts section
            slug = rel.get("url", rel["title"].lower().replace(" ", "-")[:50])
            posts.append(
                {
                    "title": rel["title"],
                    "url": f"{site_url}/{section}/{slug}",
                    "reason": rel.get("reason", "Conteúdo relacionado"),
                }
            )

        return posts

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        new_article = campaign.get("article", campaign.get("articles", [{}]))
        if isinstance(new_article, list):
            new_article = new_article[0] if new_article else {}

        existing_articles = campaign.get("existing_articles", [])
        site_url = str(campaign.get("site_url", "https://seudominio.com"))
        section = str(campaign.get("section", "artigo"))

        keyword = new_article.get("keyword", "")
        body = new_article.get("body", new_article.get("introduction", ""))

        # Find related articles
        related = self.find_related_articles(keyword, existing_articles)

        # Build contextual links
        contextual_links = self.build_contextual_links(body, related)

        # Build related posts section
        related_posts = self.build_related_posts_section(
            keyword, existing_articles, site_url, section
        )

        # Build anchor link structure for the article itself
        article_headings = []
        for section_item in new_article.get("sections", []):
            heading = (
                section_item.get("heading", "")
                if isinstance(section_item, dict)
                else str(section_item)
            )
            if heading:
                article_headings.append(
                    {
                        "text": heading,
                        "anchor": heading.lower().replace(" ", "-")[:30],
                    }
                )

        output = {
            "article_keyword": keyword,
            "related_articles_found": len(related),
            "contextual_links_suggested": len(contextual_links),
            "related_posts_for_footer": related_posts,
            "contextual_links": contextual_links[:5],
            "article_table_of_contents": article_headings,
            "link_graph": {
                "nodes": [{"title": new_article.get("title", "New")}]
                + [{"title": r["title"]} for r in related],
                "edges": [
                    {"from": "New", "to": r["title"], "type": "related"}
                    for r in related[:5]
                ],
            },
            "recommendations": [
                "Links internos melhoram SEO distribuindo PageRank",
                "Usar anchor text descritivo com keyword relevante",
                "Evitar links internos excessivos (>10 por artigo)",
                "Priorizar links para artigos com alto score E-E-A-T",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="internal_linking",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Encontrou {len(related)} artigos relacionados, sugeriu {len(contextual_links)} links contextuais"
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
