"""HotmartMarketplaceAgent — Coleta automatica de links de afiliado Hotmart.

Fluxo completo:
1. Pesquisa marketplace da Hotmart por produtos em cada nicho
2. Extrai codigos dos produtos das URLs de busca
3. Constrói links de afiliado (hotm.art/CODE?aff=SUA_CODE)
4. Registra tudo no sistema

Requer: codigo de afiliado Hotmart (fornecido uma vez pelo usuario)
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    requests = None  # type: ignore
    HAS_REQUESTS = False


from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("hotmart_marketplace")

CONFIG_PATH = Path("configs/affiliate_offers.json")

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Termos de busca para cada nicho (produtos com alta comissao e preco baixo)
NICHE_SEARCH_TERMS = {
    "tecnologia": [
        "curso programacao",
        "curso python",
        "inteligencia artificial",
        "curso excel",
        "curso javascript",
        "curso web",
        "curso ti",
        "curso dados",
        "curso cyber segurança",
        "ferramenta ia",
        "curso html css",
        "curso react",
        "curso mobile",
    ],
    "financas": [
        "planilha financeira",
        "curso investimentos",
        "renda extra",
        "educacao financeira",
        "curso bolsa valores",
        "planilha orcamento",
        "curso criptomoedas",
        "curso trader",
        "curso liberdade financeira",
        "ebook financas",
        "planilha controle financeiro",
    ],
    "saude": [
        "curso emagrecimento",
        "guia alimentacao saudavel",
        "curso exercicios em casa",
        "curso meditacao",
        "curso yoga",
        "curso nutricao",
        "curso fitness",
        "saude mental",
        "curso emagrecer",
        "curso bem estar",
    ],
    "carreira": [
        "curso linkedin",
        "curso oratoria",
        "curso produtividade",
        "curso lideranca",
        "curso entrevista emprego",
        "curso carreira",
        "curso freelancer",
        "curso marketing digital",
        "curriculo",
        "curso comunicacao",
    ],
}


@dataclass
class HotmartProduct:
    """Produto encontrado no marketplace Hotmart."""

    name: str
    slug: str
    code: str
    product_url: str
    affiliate_url: str = ""
    niche: str = ""
    price: float = 0.0
    commission_pct: float = 0.0
    earnings_per_sale: float = 0.0
    search_term: str = ""
    velocity_score: float = 0.0


class HotmartMarketplaceAgent(AgentBase):
    """Agente que pesquisa o marketplace Hotmart e coleta links automaticamente.

    E2E:
    1. Usuario fornece codigo de afiliado (1x)
    2. Agente pesquisa marketplace para cada nicho
    3. Extrai slugs/codigos dos produtos
    4. Constrói links de afiliado
    5. Registra no configs/affiliate_offers.json
    """

    def __init__(self, affiliate_code: str = "", **kwargs) -> None:
        super().__init__("hotmart_marketplace", **kwargs)
        self.affiliate_code = affiliate_code
        if HAS_REQUESTS:
            self.session = requests.Session()
        else:
            self.session = None

    def run(self, context: CampaignContext) -> AgentResult:
        if not HAS_REQUESTS:
            return AgentResult(
                agent=self.name,
                status="error",
                output={
                    "status": "unavailable",
                    "error": "requests library not installed. Install with: pip install requests",
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="run",
                    status="error",
                    started_at=datetime.now(timezone.utc).isoformat(),
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                    error="Missing optional dependency: requests",
                ),
            )
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "autocollect")
            self.affiliate_code = campaign.get("affiliate_code", self.affiliate_code)

            if action == "autocollect":
                return self._auto_collect(started_at, campaign)
            elif action == "search":
                return self._search_products(campaign, started_at)
            elif action == "register":
                return self._register_products(campaign, started_at)
            elif action == "status":
                return self._status(started_at)
            else:
                return self._auto_collect(started_at, campaign)

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
                    error=str(e)[:500],
                ),
            )

    def _auto_collect(self, started_at: str, campaign: dict) -> AgentResult:
        """Fluxo completo: pesquisa → extrai → constroi → registra."""
        if not self.affiliate_code:
            return AgentResult(
                agent=self.name,
                status="error",
                output={
                    "error": "affiliate_code_required",
                    "message": "Preciso do seu codigo de afiliado Hotmart! "
                    "Acesse https://hotmart.com, va em 'Perfil' > 'Codigo de Afiliado' "
                    "e me passe o codigo. Ex: abc123",
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="autocollect",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        max_per_niche = campaign.get("max_per_niche", 5)
        niches_to_search = campaign.get("niches", list(NICHE_SEARCH_TERMS.keys()))

        all_products: dict[str, list[dict]] = {}
        total_found = 0
        errors = []

        for niche in niches_to_search:
            niche_products = []
            search_terms = NICHE_SEARCH_TERMS.get(niche, ["curso"])

            for term in search_terms:
                if len(niche_products) >= max_per_niche:
                    break

                try:
                    products = self._search_marketplace(term, niche)
                    for p in products:
                        if len(niche_products) >= max_per_niche:
                            break
                        # Check if product name matches niche keywords
                        if self._is_relevant(p.name, niche):
                            p.affiliate_url = self._build_affiliate_url(p.code)
                            p.niche = niche
                            p.search_term = term
                            niche_products.append(
                                {
                                    "name": p.name,
                                    "slug": p.slug,
                                    "code": p.code,
                                    "product_url": p.product_url,
                                    "affiliate_url": p.affiliate_url,
                                    "niche": niche,
                                    "search_term": term,
                                    "price": p.price,
                                    "commission_pct": p.commission_pct,
                                    "earnings_per_sale": p.earnings_per_sale,
                                }
                            )

                    time.sleep(0.5)  # Rate limiting

                except Exception as e:
                    errors.append(f"{niche}/{term}: {e}")
                    continue

            all_products[niche] = niche_products
            total_found += len(niche_products)

        # Registrar no config
        registered_count = self._register_in_config(all_products)

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="autocollect",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[
                f"produtos: {total_found}",
                f"registrados: {registered_count}",
                f"nichos: {len(niches_to_search)}",
            ],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "action": "autocollect",
                "affiliate_code": self.affiliate_code,
                "total_found": total_found,
                "registered": registered_count,
                "products_by_niche": {
                    n: len(prods) for n, prods in all_products.items()
                },
                "products": all_products,
                "errors": errors[:5],
                "message": f"✅ Coletei {total_found} produtos Hotmart automaticamente! "
                f"Links de afiliado construidos com codigo '{self.affiliate_code}'.",
            },
            trace=trace,
        )

    def _search_marketplace(self, term: str, niche: str) -> list[HotmartProduct]:
        """Pesquisa marketplace da Hotmart e extrai produtos."""
        url = "https://hotmart.com/pt-br/marketplace/produtos"
        params = {"q": term, "page": 1}

        resp = self.session.get(url, params=params, timeout=20)
        resp.raise_for_status()

        # Extrair URLs de produto
        product_urls = re.findall(
            r'href="(https://hotmart\.com/[^"]*/marketplace/produtos/([^/"]+)/([^/"?]+)[^"]*)"',
            resp.text,
        )

        products = []
        seen_codes = set()
        for full_url, slug, code in product_urls:
            if code in seen_codes:
                continue
            seen_codes.add(code)

            # Extrair nome do produto (slug → nome legivel)
            name = self._slug_to_name(slug)

            products.append(
                HotmartProduct(
                    name=name,
                    slug=slug,
                    code=code,
                    product_url=full_url,
                    search_term=term,
                )
            )

        return products

    def _slug_to_name(self, slug: str) -> str:
        """Converte slug em nome legivel."""
        # Remove suffixes like -black-november, -2-0, etc
        name = re.sub(
            r"-(?:black|november|2-0|3-0|2024|2025|2026)$",
            "",
            slug,
            flags=re.IGNORECASE,
        )
        name = name.replace("-", " ").replace("_", " ")
        # Capitalize
        name = " ".join(w.capitalize() for w in name.split())
        return name[:80]

    def _is_relevant(self, name: str, niche: str) -> bool:
        """Verifica se o produto e relevante para o nicho."""
        name_lower = name.lower()

        # Palavras-chave de rejeicao (nao queremos esses tipos de produto)
        reject_keywords = {
            "tecnologia": [
                "agronom",
                "carga",
                "eletric",
                "construcao",
                "imposto",
                "mei",
                "confeiteira",
            ],
            "financas": [
                "agronom",
                "carga",
                "eletric",
                "construcao",
                "avaliacao fisica",
                "treino",
            ],
            "saude": [
                "imposto",
                "mei",
                "confeiteira",
                "cripto",
                "trader",
                "programacao",
            ],
            "carreira": ["agronom", "confeiteira", "carga", "eletric", "cripto"],
        }

        reject = reject_keywords.get(niche, [])
        for kw in reject:
            if kw in name_lower:
                return False

        return True

    def _build_affiliate_url(self, product_code: str) -> str:
        """Constroi URL de afiliado Hotmart."""
        return f"https://hotm.art/{product_code}?aff={self.affiliate_code}"

    def _register_in_config(self, products_by_niche: dict[str, list[dict]]) -> int:
        """Registra produtos no configs/affiliate_offers.json."""
        if not CONFIG_PATH.exists():
            return 0

        with open(CONFIG_PATH) as f:
            config = json.load(f)

        if "offers_by_niche" not in config:
            config["offers_by_niche"] = {}

        count = 0
        for niche, products in products_by_niche.items():
            if niche not in config["offers_by_niche"]:
                config["offers_by_niche"][niche] = []

            existing_urls = {
                o.get("product_url", "") for o in config["offers_by_niche"][niche]
            }

            for p in products:
                if p["product_url"] in existing_urls:
                    continue  # Ja existe

                config["offers_by_niche"][niche].append(
                    {
                        "network": "hotmart",
                        "product_name": p["name"],
                        "product_url": p["affiliate_url"],
                        "commission_type": "percentage",
                        "commission_value": 50.0,  # Valor generico, ajustavel
                        "keywords": [p["name"].lower()] + [niche],
                        "cookie_days": 30,
                        "auto_collected": True,
                        "search_term": p.get("search_term", ""),
                    }
                )
                existing_urls.add(p["product_url"])
                count += 1

        # Atualizar affiliate_ids
        if "affiliate_ids" in config:
            config["affiliate_ids"]["hotmart"] = self.affiliate_code

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return count

    def _status(self, started_at: str) -> AgentResult:
        """Status dos produtos Hotmart coletados."""
        if not CONFIG_PATH.exists():
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "status": "no_config",
                    "message": "Arquivo de configuracao nao encontrado.",
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="status",
                    status="success",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        with open(CONFIG_PATH) as f:
            config = json.load(f)

        hotmart_offers = {}
        total = 0
        auto = 0
        for niche, offers in config.get("offers_by_niche", {}).items():
            hotmart_offers[niche] = {
                "total": 0,
                "auto_collected": 0,
                "placeholder": 0,
            }
            for o in offers:
                if o.get("network") == "hotmart":
                    hotmart_offers[niche]["total"] += 1
                    total += 1
                    if o.get("auto_collected"):
                        hotmart_offers[niche]["auto_collected"] += 1
                        auto += 1
                    if "seulink" in o.get("product_url", "").lower():
                        hotmart_offers[niche]["placeholder"] += 1

        affiliate_id = config.get("affiliate_ids", {}).get("hotmart", "")

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "status": "active",
                "affiliate_code": affiliate_id,
                "total_hotmart_offers": total,
                "auto_collected": auto,
                "by_niche": hotmart_offers,
                "needs_affiliate_code": not bool(affiliate_id or self.affiliate_code),
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="status",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )

    def _search_products(self, campaign: dict, started_at: str) -> AgentResult:
        """Pesquisa sem registrar."""
        term = campaign.get("term", "curso")
        niche = campaign.get("niche", "tecnologia")

        products = self._search_marketplace(term, niche)
        for p in products:
            p.affiliate_url = self._build_affiliate_url(p.code)
            p.niche = niche

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="search",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"termo: {term}", f"encontrados: {len(products)}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "search_term": term,
                "niche": niche,
                "products_found": len(products),
                "products": [
                    {
                        "name": p.name,
                        "slug": p.slug,
                        "code": p.code,
                        "url": p.affiliate_url,
                    }
                    for p in products
                ],
            },
            trace=trace,
        )

    def _register_products(self, campaign: dict, started_at: str) -> AgentResult:
        """Registra produtos manualmente."""
        products = campaign.get("products", [])
        count = self._register_in_config(
            {
                "manual": [
                    {
                        k: v
                        for k, v in p.items()
                        if k
                        in (
                            "name",
                            "slug",
                            "code",
                            "product_url",
                            "affiliate_url",
                            "niche",
                            "search_term",
                        )
                    }
                    for p in products
                ]
            }
        )

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={"registered": count},
            trace=AgentTrace(
                agent=self.name,
                step_id="register",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )
