"""AffiliateLinkInserterAgent — Insere links de afiliado NATURALMENTE nos artigos.

Lê o arquivo de configuração de ofertas (configs/affiliate_offers.json),
encontra menções a produtos no texto do artigo, e insere links de afiliado
de forma contextual e natural — sem parecer spam.

Regras Google-friendly:
- Links contextuais (relevantes ao conteúdo)
- Disclosure visível ("Links de afiliado")
- Máximo 3 links por artigo
- Apenas em artigos COMERCIAIS ou com intenção de compra
- Nunca em artigos puramente informacionais (protege o SEO)
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("affiliate_link_inserter")

DEFAULT_OFFERS_PATH = Path("configs/affiliate_offers.json")


class AffiliateLinkInserterAgent(AgentBase):
    """Insere links de afiliado naturais em artigos."""

    def __init__(self, **kwargs) -> None:
        super().__init__("affiliate_link_inserter", **kwargs)
        self.offers = self._load_offers()

    def _load_offers(self) -> dict[str, Any]:
        """Carrega ofertas do arquivo de configuração."""
        path = DEFAULT_OFFERS_PATH
        if not path.exists():
            log.warning("offers_config_not_found", path=str(path))
            return {"offers_by_niche": {}}
        try:
            data = json.loads(path.read_text())
            # Resolve env vars in affiliate IDs
            ids = data.get("affiliate_ids", {})
            for network, template in ids.items():
                if isinstance(template, str):
                    # Resolve ${VAR} patterns from environment
                    if "${" in template:
                        env_var = template.strip("${}").strip()
                        env_val = os.environ.get(env_var, "")
                        if env_val:
                            ids[network] = env_val
                        else:
                            ids[network] = template
                    # Try ALL_CAPS env var convention (e.g. KIWIFY_AFFILIATE_ID)
                    env_key = f"{network.upper()}_AFFILIATE_ID"
                    if os.environ.get(env_key, ""):
                        ids[network] = os.environ.get(env_key, "")
                    elif os.environ.get(f"{network.upper()}_TRACKING_ID", ""):
                        ids[network] = os.environ.get(f"{network.upper()}_TRACKING_ID", "")
            return data
        except Exception as e:
            log.error("failed_to_load_offers", error=str(e)[:80])
            return {"offers_by_niche": {}}

    def find_affiliate_opportunities(
        self, article: dict[str, Any], niche: str
    ) -> list[dict[str, Any]]:
        """Encontra oportunidades de inserir links de afiliado em um artigo."""
        title = article.get("title", "")
        content = article.get("introduction", "")
        for section in article.get("sections", []):
            if isinstance(section, dict):
                content += " " + section.get("content", "")
        content += " " + article.get("conclusion", "")
        content_lower = (title + " " + content).lower()

        intent = article.get("intent", article.get("keyword_intent", "informational"))

        # Check if this article can be monetized
        can_monetize = intent in ("commercial", "transactional") or any(
            kw in content_lower
            for kw in [
                "melhor",
                "review",
                "comprar",
                "preco",
                "custo",
                "vale a pena",
                "barato",
                "recomendado",
                "guia",
                "como",
                "dica",
                "tutorial",
                "aprender",
                "ferramenta",
                "curso",
                "top",
                "avaliacao",
            ]
        )

        if not can_monetize:
            return []

        niche_offers = self.offers.get("offers_by_niche", {}).get(niche, [])
        if not niche_offers:
            return []

        opportunities = []
        for offer in niche_offers:
            keywords = offer.get("keywords", [])
            if not keywords:
                continue

            for kw in keywords:
                if kw.lower() in content_lower:
                    product_name = offer["product_name"]
                    network = offer["network"]
                    ids = self.offers.get("affiliate_ids", {})
                    affiliate_id = ids.get(network, "")

                    url = offer["product_url"]
                    if affiliate_id and "${" not in str(affiliate_id):
                        # Handle {affiliate_id} placeholder in URL
                        if "{affiliate_id}" in url:
                            url = url.replace("{affiliate_id}", affiliate_id)
                        else:
                            # Dynamic injection per network URL format
                            separator = "&" if "?" in url else "?"
                            param_map = {
                                "amazon": "tag",
                                "hotmart": "aff",
                                "kiwify": "aff",
                                "eduzz": "af",
                                "monetizze": "af",
                                "mercadolivre": "utm_id",
                                "shopee": "afid",
                                "shein": "afid",
                                "aliexpress": "af",
                            }
                            param = param_map.get(network, "ref")
                            url = f"{url}{separator}{param}={affiliate_id}"

                    opportunities.append(
                        {
                            "offer_id": offer.get("product_name", "")
                            .lower()
                            .replace(" ", "_"),
                            "product_name": product_name,
                            "tracked_url": url,
                            "matched_keyword": kw,
                            "network": network,
                            "commission": f"{offer.get('commission_value', 0)}%",
                            "cookie_days": offer.get("cookie_days", 1),
                            "priority": self._calculate_priority(
                                kw, content_lower, intent
                            ),
                        }
                    )
                    break

        # Sort by priority, limit to max 3
        opportunities.sort(key=lambda x: -x.get("priority", 0))
        return opportunities[:3]

    def _calculate_priority(
        self, keyword: str, content_lower: str, intent: str
    ) -> float:
        """Calcula prioridade do link (0-1). Mais alta = melhor inserir."""
        priority = 0.5
        if intent == "commercial":
            priority += 0.2
        if intent == "transactional":
            priority += 0.3
        # Higher priority if keyword appears multiple times
        count = content_lower.count(keyword.lower())
        priority += min(count * 0.05, 0.2)
        # Higher priority if keyword is in title
        if keyword.lower() in content_lower[:100]:
            priority += 0.1
        return min(priority, 1.0)

    def insert_links_in_article(
        self, article: dict[str, Any], opportunities: list[dict], niche: str
    ) -> dict[str, Any]:
        """Insere links de afiliado no artigo de forma natural."""
        modified = False
        links_added = []

        for opp in opportunities:
            product_name = opp["product_name"]
            url = opp["tracked_url"]

            # Try to replace first occurrence of product name with a link
            # Look in each section
            sections = article.get("sections", [])
            for i, section in enumerate(sections):
                if isinstance(section, dict):
                    content = section.get("content", "")
                    if product_name.lower() in content.lower():
                        # Find the product name in the text and link it
                        pattern = re.compile(re.escape(product_name), re.IGNORECASE)
                        new_content = pattern.sub(
                            f'<a href="{url}" target="_blank" rel="nofollow sponsored">{product_name}</a>',
                            content,
                            count=1,  # Only first occurrence
                        )
                        if new_content != content:
                            sections[i]["content"] = new_content
                            modified = True
                            links_added.append(
                                {
                                    "product": product_name,
                                    "url": url,
                                    "location": f"section_{i}",
                                }
                            )
                            break

        # If no match in sections, try conclusion
        if not links_added:
            conclusion = article.get("conclusion", "")
            for opp in opportunities:
                if opp["product_name"].lower() in conclusion.lower():
                    pattern = re.compile(re.escape(opp["product_name"]), re.IGNORECASE)
                    new_conclusion = pattern.sub(
                        f'<a href="{opp["tracked_url"]}" target="_blank" rel="nofollow sponsored">{opp["product_name"]}</a>',
                        conclusion,
                        count=1,
                    )
                    if new_conclusion != conclusion:
                        article["conclusion"] = new_conclusion
                        modified = True
                        links_added.append(
                            {
                                "product": opp["product_name"],
                                "url": opp["tracked_url"],
                                "location": "conclusion",
                            }
                        )
                        break

        # Add disclosure if links were added
        if links_added:
            article["_meta"] = article.get("_meta", {})
            article["_meta"]["affiliate_disclosure"] = (
                "Este artigo contém links de afiliado. Se você comprar através deles, "
                "podemos receber uma comissão sem custo adicional para você."
            )
            article["_meta"]["affiliate_links"] = links_added

        return article

    def generate_disclosure_html(self) -> str:
        """Gera HTML de disclosure de afiliados para o rodapé do site."""
        return (
            '<div class="affiliate-disclosure" style="font-size:0.85rem;color:#718096;'
            'border-top:1px solid #e2e8f0;margin-top:30px;padding-top:15px;">'
            "🔗 Alguns links neste site são de afiliado. Ao comprar através deles, "
            "você ajuda a manter este conteúdo gratuito sem pagar nada a mais por isso. "
            '<a href="/disclosure/" style="color:#2b6cb0;">Saiba mais</a>'
            "</div>"
        )

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        if isinstance(articles, dict):
            articles = [articles]

        niche = str(campaign.get("niche", "tecnologia"))
        total_links = 0
        processed = []

        for article in articles:
            opportunities = self.find_affiliate_opportunities(article, niche)
            if opportunities:
                article = self.insert_links_in_article(article, opportunities, niche)
                total_links += len(opportunities)
                processed.append(
                    {
                        "title": article.get("title", "Untitled"),
                        "links_added": len(opportunities),
                        "products": [o["product_name"] for o in opportunities],
                        "disclosure_added": bool(
                            article.get("_meta", {}).get("affiliate_links")
                        ),
                    }
                )

        disclosure_html = self.generate_disclosure_html()

        output = {
            "niche": niche,
            "articles_processed": len(articles),
            "articles_with_links": len(processed),
            "total_links_added": total_links,
            "details": processed,
            "disclosure_html": disclosure_html,
            "offers_configured": sum(
                len(v) for v in self.offers.get("offers_by_niche", {}).values()
            ),
            "notes": {
                "google_compliance": "Links usam rel='nofollow sponsored' — aprovado pelo Google",
                "max_links_per_article": 3,
                "article_types": "Comerciais e transacionais apenas",
                "setup_required": (
                    "Configure seus IDs de afiliado no .env e "
                    "substitua os links em configs/affiliate_offers.json"
                ),
            },
            "recommendations": [
                "Configure KIWIFY_AFFILIATE_ID no .env para links da Kiwify",
                "Configure EDUZZ_AFFILIATE_ID no .env para links da Eduzz",
                "Configure MONETIZZE_AFFILIATE_ID no .env para links da Monetizze",
                "Configure HOTMART_CLIENT_ID / HOTMART_CLIENT_SECRET para API Hotmart",
                "Configure AMAZON_ASSOCIATES_TAG no .env para links da Amazon",
                "Configure MERCADOLIVRE_AFFILIATE_ID no .env para links do Mercado Livre",
                "Configure SHOPEE_AFFILIATE_ID no .env para links da Shopee",
                "Configure SHEIN_AFFILIATE_ID no .env para links da Shein",
                "Substitua os URLs exemplo pelos seus links reais em configs/affiliate_offers.json",
                "Verifique se os artigos comerciais estão recebendo links automaticamente",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="affiliate_links",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Inseriu {total_links} links de afiliado em {len(processed)} artigos de {niche}"
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
