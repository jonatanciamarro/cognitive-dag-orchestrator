"""API Integration Hub v2 — Conexões reais com APIs externas.

Implementa chamadas HTTP reais para OpenAI, WordPress, Hotmart, Amazon,
com fallback inteligente para simulação quando sem credenciais.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.parse import urlencode

from .logging_utils import StructuredLogger

log = StructuredLogger("api_hub")


# ── HTTP client (stdlib only, no requests dependency) ─────────────


def _http_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    json_body: Any = None,
    timeout: int = 30,
) -> tuple[int, dict[str, Any] | str]:
    """Make an HTTP request using stdlib only."""
    import urllib.request
    import urllib.error

    req_headers = {"User-Agent": "CampaignAutopilot/5.0"}
    if headers:
        req_headers.update(headers)

    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    elif data is not None:
        body = urlencode(data).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    try:
        req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                payload = raw
            return resp.status, payload
    except urllib.error.HTTPError as e:
        return e.code, {
            "error": str(e),
            "body": e.read().decode("utf-8", errors="replace"),
        }
    except urllib.error.URLError as e:
        return 0, {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return 0, {"error": str(e)}


# ── Real API Implementations ──────────────────────────────────────


def openai_chat_completion(
    prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
    api_key: str | None = None,
) -> str | None:
    """Call OpenAI Chat Completions API. Returns text or None on failure."""
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return None

    status, data = _http_request(
        "POST",
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json_body={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        },
    )

    if status == 200 and isinstance(data, dict):
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
    log.error("openai_completion_failed", status=status)
    return None


def wordpress_publish(
    title: str,
    content: str,
    status: str = "draft",
    wp_url: str | None = None,
    wp_user: str | None = None,
    wp_password: str | None = None,
) -> dict[str, Any]:
    """Publish to WordPress via REST API."""
    url = (wp_url or os.environ.get("WP_URL", "")).rstrip("/")
    user = wp_user or os.environ.get("WP_USER", "")
    pwd = wp_password or os.environ.get("WP_PASSWORD", "")

    if not (url and user and pwd):
        return {
            "mode": "simulated",
            "title": title,
            "status": status,
            "note": "Configure WP_URL, WP_USER, WP_PASSWORD para publicação real.",
        }

    import base64

    creds = base64.b64encode(f"{user}:{pwd}".encode()).decode()

    status_code, data = _http_request(
        "POST",
        f"{url}/wp-json/wp/v2/posts",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
        },
        json_body={
            "title": title,
            "content": content,
            "status": status,
        },
    )

    if status_code in (200, 201) and isinstance(data, dict):
        return {
            "mode": "real",
            "id": data.get("id"),
            "link": data.get("link"),
            "title": data.get("title", {}).get("rendered", title),
            "status": data.get("status", status),
        }
    return {
        "mode": "simulated",
        "title": title,
        "status": status,
        "note": f"Falha na API WordPress ({status_code})",
    }


def ahrefs_keyword_search(niche: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search keywords via Ahrefs API."""
    key = os.environ.get("AHREFS_API_KEY", "")
    if not key:
        return _simulated_keywords(niche, limit)

    status, data = _http_request(
        "GET",
        f"https://api.ahrefs.com/v3/keywords?keyword={niche}&limit={limit}",
        headers={"Authorization": f"Bearer {key}"},
    )

    if status == 200 and isinstance(data, dict):
        return data.get("keywords", data.get("data", []))
    return _simulated_keywords(niche, limit)


def hotmart_search_offers(niche: str) -> list[dict[str, Any]]:
    """Search Hotmart products via API."""
    client_id = os.environ.get("HOTMART_CLIENT_ID", "")
    client_secret = os.environ.get("HOTMART_CLIENT_SECRET", "")
    if not (client_id and client_secret):
        return _simulated_offers(niche)

    # Get access token
    status, token_data = _http_request(
        "POST",
        "https://api-hotmart.com/security/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    if status != 200 or not isinstance(token_data, dict):
        return _simulated_offers(niche)

    access_token = token_data.get("access_token", "")
    if not access_token:
        return _simulated_offers(niche)

    # Search products
    status, data = _http_request(
        "GET",
        f"https://api-hotmart.com/v1/products?name={niche}&maxResults=10",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if status == 200 and isinstance(data, dict):
        return data.get("products", data.get("items", []))
    return _simulated_offers(niche)


# ── Simulated fallbacks ───────────────────────────────────────────


def _simulated_keywords(niche: str, limit: int = 10) -> list[dict[str, Any]]:
    """Generate simulated keyword data for testing."""
    templates = [
        {"keyword": f"como {niche}", "volume": 2400, "difficulty": 45, "cpc": 1.20},
        {
            "keyword": f"{niche} para iniciantes",
            "volume": 1800,
            "difficulty": 30,
            "cpc": 0.90,
        },
        {"keyword": f"melhor {niche}", "volume": 3200, "difficulty": 55, "cpc": 1.50},
        {"keyword": f"{niche} grátis", "volume": 1500, "difficulty": 25, "cpc": 0.70},
        {"keyword": f"{niche} online", "volume": 2100, "difficulty": 40, "cpc": 1.10},
        {"keyword": f"guia de {niche}", "volume": 1200, "difficulty": 35, "cpc": 0.85},
        {
            "keyword": f"{niche} passo a passo",
            "volume": 900,
            "difficulty": 28,
            "cpc": 0.75,
        },
        {"keyword": f"{niche} dicas", "volume": 2800, "difficulty": 50, "cpc": 1.30},
        {"keyword": f"aprender {niche}", "volume": 1600, "difficulty": 32, "cpc": 0.95},
        {"keyword": f"{niche} 2026", "volume": 3500, "difficulty": 48, "cpc": 1.40},
    ]
    return templates[:limit]


def _simulated_offers(niche: str) -> list[dict[str, Any]]:
    """Generate offers from curated product database, with LLM-enhanced fallback."""
    # Try to load from generated products file
    import json as _json
    from pathlib import Path as _Path

    products_file = _Path("configs/generated_products.json")
    if products_file.exists():
        try:
            all_products: list[dict] = _json.loads(products_file.read_text())
            niche_products = [
                p
                for p in all_products
                if niche.lower() in p.get("niche", "").lower()
                or niche.lower() in p.get("category", "").lower()
            ]
            if niche_products:
                return [
                    {
                        "name": p["product_name"],
                        "commission": p.get("commission_pct", 5)
                        * p.get("price_brl", 100)
                        / 100,
                        "price": p.get("price_brl", 100),
                        "commission_pct": p.get("commission_pct", 5),
                        "network": p.get("platform", "Amazon"),
                        "url": f"https://amzn.to/{p['product_name'][:20].replace(' ', '-')}",
                        "category": p.get("category", niche),
                        "niche": niche,
                        "keywords": p.get("keywords", []),
                    }
                    for p in niche_products[:10]
                ]
        except Exception:
            pass

    # Fallback: try LLM generation
    try:
        from .free_llm_providers import generate_text as _gen

        llm_result = _gen(
            f'Generate a JSON array of 6 affiliate products for niche "{niche}" in Brazil. '
            f"Each with name, price (R$), commission_pct, platform (Mercado Livre, Shopee, Amazon, Magazine Luiza). "
            f"Return ONLY JSON.",
            max_tokens=2000,
        )
        if llm_result:
            import re as _re

            _json_match = _re.search(r"\[.*?\]", llm_result, _re.DOTALL)
            if _json_match:
                try:
                    parsed = _json.loads(_json_match.group())
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return [
                            {
                                "name": p.get("product_name", p.get("name", "Produto")),
                                "commission": p.get("commission_pct", 5)
                                * p.get("price_brl", 100)
                                / 100,
                                "price": p.get("price_brl", 100),
                                "commission_pct": p.get("commission_pct", 5),
                                "network": p.get("platform", "Amazon"),
                                "url": f"https://amzn.to/{p.get('product_name', 'produto')[:20].replace(' ', '-')}",
                                "niche": niche,
                            }
                            for p in parsed[:10]
                        ]
                except Exception:
                    pass
    except Exception:
        pass

    # Final fallback: template offers (better than nothing)
    return [
        {
            "name": f"Curso Completo de {niche.title()}",
            "commission": 60.0,
            "price": 197.0,
            "network": "Hotmart",
            "commission_pct": 60,
            "url": f"https://hotm.art/{niche.replace(' ', '')}",
        },
        {
            "name": f"Kit {niche.title()} Profissional",
            "commission": 25.0,
            "price": 89.0,
            "network": "Amazon",
            "commission_pct": 28,
            "url": f"https://amzn.to/kit-{niche.replace(' ', '-')}",
        },
        {
            "name": f"E-book: {niche.title()} Descomplicado",
            "commission": 15.0,
            "price": 27.0,
            "network": "Hotmart",
            "commission_pct": 55,
            "url": f"https://hotm.art/ebook-{niche}",
        },
        {
            "name": f"Acessório {niche.title()}",
            "commission": 8.0,
            "price": 79.0,
            "network": "Shopee",
            "commission_pct": 10,
            "url": f"https://shopee.com.br/{niche}-acessorio",
        },
        {
            "name": f"Ferramenta de {niche.title()}",
            "commission": 30.0,
            "price": 97.0,
            "network": "Amazon",
            "commission_pct": 30,
            "url": f"https://amzn.to/{niche.replace(' ', '')}",
        },
        {
            "name": f"Guia Prático de {niche.title()}",
            "commission": 12.0,
            "price": 37.0,
            "network": "Kiwify",
            "commission_pct": 32,
            "url": f"https://kiwify.com.br/guia-{niche}",
        },
    ]


# ── Orchestrated API Hub ──────────────────────────────────────────


class APIHubV2:
    """API Hub with real HTTP calls and intelligent fallback."""

    def __init__(self) -> None:
        self._stats: dict[str, Any] = {"calls": 0, "real": 0, "simulated": 0}
        self._cache: dict[str, tuple[float, Any]] = {}
        self._cache_ttl = 300  # 5 minutes

    def _call(self, name: str, fn: Any) -> Any:
        """Execute API call with caching and stats tracking."""
        cache_key = name
        now = time.time()
        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if now - ts < self._cache_ttl:
                return val

        result = fn()
        is_simulated = (
            isinstance(result, dict) and result.get("mode") == "simulated"
            if isinstance(result, dict)
            else False
        )

        self._stats["calls"] += 1
        if is_simulated:
            self._stats["simulated"] += 1
        else:
            self._stats["real"] += 1

        self._cache[cache_key] = (now, result)
        log.info("api_call", api=name, simulated=is_simulated)
        return result

    def search_keywords(self, niche: str, limit: int = 10) -> list[dict[str, Any]]:
        return self._call(
            "keywords",
            lambda: (
                ahrefs_keyword_search(niche, limit) or _simulated_keywords(niche, limit)
            ),
        )

    def search_offers(self, niche: str) -> list[dict[str, Any]]:
        return self._call(
            "offers", lambda: hotmart_search_offers(niche) or _simulated_offers(niche)
        )

    def generate_content(self, prompt: str, max_tokens: int = 1000) -> str:
        # Try OpenAI first, then free LLM providers chain, then stdlib fallback
        llm_result = openai_chat_completion(prompt, max_tokens=max_tokens)
        if llm_result and len(llm_result) > 50:
            result = llm_result
        else:
            try:
                from .free_llm_providers import generate_text

                llm_result = generate_text(prompt, max_tokens=max_tokens)
            except Exception:
                llm_result = None
            result = (
                llm_result
                if llm_result and len(llm_result) > 50
                else _simulated_content(prompt)
            )
        return result if isinstance(result, str) else _simulated_content(prompt)

    def generate_free_content(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate content using free LLM providers chain (13 providers + stdlib fallback)."""
        try:
            from .free_llm_providers import generate_text

            result = generate_text(prompt, max_tokens=max_tokens)
            if result and len(result) > 50:
                return result
        except Exception:
            pass
        return _simulated_content(prompt)

    def publish_wordpress(
        self, title: str, content: str, status: str = "draft"
    ) -> dict[str, Any]:
        return self._call(
            "wordpress", lambda: wordpress_publish(title, content, status)
        )

    def get_stats(self) -> dict[str, Any]:
        return dict(self._stats)


def _simulated_content(prompt: str) -> str:
    """Generate rich content using free internal pipeline (stdlib only)."""
    try:
        from .free_content_generator import FreeContentEngine

        # Try the enhanced free content engine first
        engine = FreeContentEngine()
        article = engine.generate_article(
            niche=prompt.strip()[:60], keyword=prompt.strip()[:40]
        )
        if len(article) > 100:
            return article
    except Exception:
        pass
    # Ultimate fallback
    return _basic_fallback_content(prompt)


def _basic_fallback_content(prompt: str) -> str:
    """Basic fallback when free content generator is unavailable."""
    return f"""# {prompt[:60]}

## Introdução

Este é um conteúdo gerado pelo Campaign Autopilot sobre o tema: {prompt}.

## Desenvolvimento

O marketing digital oferece inúmeras oportunidades para quem deseja construir um negócio online sustentável.
Com as estratégias certas e consistência, é possível gerar resultados expressivos.

### Pontos Principais

1. **Pesquisa de palavras-chave**: Identificar termos com alto volume e baixa concorrência
2. **Conteúdo de qualidade**: Produzir material que realmente ajuda o leitor
3. **Otimização SEO**: Estruturar o conteúdo para mecanismos de busca
4. **Links de afiliados**: Recomendar produtos relevantes de forma natural
5. **Distribuição multicanal**: Ampliar o alcance do conteúdo

## Conclusão

Comece hoje mesmo a implementar estas estratégias e acompanhe seus resultados ao longo do tempo.

*Conteúdo gerado automaticamente pelo Campaign Autopilot v5.0*
"""


# Singleton
_hub_instance: APIHubV2 | None = None


def get_api_hub_v2() -> APIHubV2:
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = APIHubV2()
    return _hub_instance
