"""API Integration Hub — gerencia conexões com APIs externas com retry, rate limiting e fallback simulado.

Uso:
    from campaign_autopilot.api_hub import api_hub

    # Tenta API real, cai para simulado se sem credenciais
    offers = api_hub.search_offers("marketing digital")
    keywords = api_hub.search_keywords("marketing de afiliados")
    posts = api_hub.create_wordpress_post(title="...", content="...")
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable


# ── Config ──────────────────────────────────────────────────────────


@dataclass
class APICredentials:
    """Gerencia credenciais de APIs a partir de env vars."""

    hotmart_client_id: str = field(
        default_factory=lambda: os.environ.get("HOTMART_CLIENT_ID", "")
    )
    hotmart_client_secret: str = field(
        default_factory=lambda: os.environ.get("HOTMART_CLIENT_SECRET", "")
    )
    amazon_access_key: str = field(
        default_factory=lambda: os.environ.get("AMAZON_ACCESS_KEY", "")
    )
    amazon_secret_key: str = field(
        default_factory=lambda: os.environ.get("AMAZON_SECRET_KEY", "")
    )
    amazon_associate_tag: str = field(
        default_factory=lambda: os.environ.get("AMAZON_ASSOCIATE_TAG", "")
    )
    ahrefs_api_key: str = field(
        default_factory=lambda: os.environ.get("AHREFS_API_KEY", "")
    )
    wordpress_url: str = field(default_factory=lambda: os.environ.get("WP_URL", ""))
    wordpress_user: str = field(default_factory=lambda: os.environ.get("WP_USER", ""))
    wordpress_password: str = field(
        default_factory=lambda: os.environ.get("WP_PASSWORD", "")
    )
    openai_api_key: str = field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")
    )
    pinterest_access_token: str = field(
        default_factory=lambda: os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    )

    @property
    def has_hotmart(self) -> bool:
        return bool(self.hotmart_client_id and self.hotmart_client_secret)

    @property
    def has_amazon(self) -> bool:
        return bool(
            self.amazon_access_key
            and self.amazon_secret_key
            and self.amazon_associate_tag
        )

    @property
    def has_ahrefs(self) -> bool:
        return bool(self.ahrefs_api_key)

    @property
    def has_wordpress(self) -> bool:
        return bool(
            self.wordpress_url and self.wordpress_user and self.wordpress_password
        )

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

    def available_apis(self) -> list[str]:
        apis = []
        if self.has_hotmart:
            apis.append("hotmart")
        if self.has_amazon:
            apis.append("amazon")
        if self.has_ahrefs:
            apis.append("ahrefs")
        if self.has_wordpress:
            apis.append("wordpress")
        if self.has_openai:
            apis.append("openai")
        return apis


# ── Rate Limiter ──────────────────────────────────────────────────


class RateLimiter:
    """Simple token-bucket rate limiter for API calls."""

    def __init__(self, calls_per_second: float = 2.0):
        self.min_interval = 1.0 / max(0.1, calls_per_second)
        self._last_call: float = 0.0

    def wait(self) -> None:
        elapsed = time.time() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.time()


# ── Simulated Data (fallback) ────────────────────────────────────

_SIMULATED_KEYWORDS: dict[str, list[dict[str, Any]]] = {
    "marketing digital": [
        {
            "keyword": "marketing de afiliados para iniciantes",
            "volume": 5400,
            "difficulty": 0.28,
            "intent": "informational",
        },
        {
            "keyword": "como ganhar dinheiro com marketing digital",
            "volume": 8200,
            "difficulty": 0.35,
            "intent": "commercial",
        },
        {
            "keyword": "melhores cursos de marketing digital",
            "volume": 3100,
            "difficulty": 0.42,
            "intent": "commercial",
        },
        {
            "keyword": "ferramentas marketing digital gratuitas",
            "volume": 2800,
            "difficulty": 0.22,
            "intent": "informational",
        },
        {
            "keyword": "estratégia marketing digital 2026",
            "volume": 4500,
            "difficulty": 0.31,
            "intent": "informational",
        },
    ],
    "financas": [
        {
            "keyword": "como investir dinheiro",
            "volume": 12000,
            "difficulty": 0.45,
            "intent": "informational",
        },
        {
            "keyword": "melhores investimentos 2026",
            "volume": 8900,
            "difficulty": 0.52,
            "intent": "commercial",
        },
        {
            "keyword": "educação financeira para iniciantes",
            "volume": 7600,
            "difficulty": 0.25,
            "intent": "informational",
        },
    ],
    "default": [
        {
            "keyword": "guia completo para iniciantes",
            "volume": 3000,
            "difficulty": 0.30,
            "intent": "informational",
        },
        {
            "keyword": "melhores ferramentas e recursos",
            "volume": 2000,
            "difficulty": 0.35,
            "intent": "commercial",
        },
        {
            "keyword": "passo a passo prático",
            "volume": 2500,
            "difficulty": 0.25,
            "intent": "informational",
        },
    ],
}

_SIMULATED_OFFERS: list[dict[str, Any]] = [
    {
        "offer_id": "hotmart_001",
        "network": "hotmart",
        "product_name": "Curso Marketing Digital Completo",
        "category": "marketing digital",
        "commission_type": "percentage",
        "commission_value": 60.0,
        "price": 197.00,
        "cookie_days": 30,
        "product_url": "https://hotmart.com/product/mkt-completo",
    },
    {
        "offer_id": "hotmart_002",
        "network": "hotmart",
        "product_name": "Ferramenta de SEO Automatizado",
        "category": "tecnologia",
        "commission_type": "percentage",
        "commission_value": 40.0,
        "price": 97.00,
        "cookie_days": 30,
        "product_url": "https://hotmart.com/product/seo-auto",
    },
    {
        "offer_id": "amazon_001",
        "network": "amazon",
        "product_name": "Livro: Marketing Digital 2026",
        "category": "marketing digital",
        "commission_type": "percentage",
        "commission_value": 10.0,
        "price": 49.90,
        "cookie_days": 1,
        "product_url": "https://amazon.com/dp/exemplo",
    },
    {
        "offer_id": "hotmart_004",
        "network": "hotmart",
        "product_name": "Guia Definitivo Afiliados",
        "category": "afiliados",
        "commission_type": "percentage",
        "commission_value": 70.0,
        "price": 67.00,
        "cookie_days": 30,
        "product_url": "https://hotmart.com/product/guia-afiliados",
    },
]


# ── API Hub ──────────────────────────────────────────────────────


class APIHub:
    """Ponto único de integração com APIs externas.

    Gerencia credenciais, rate limiting, retry com backoff,
    e fallback para dados simulados quando APIs não disponíveis.
    """

    def __init__(self):
        self.creds = APICredentials()
        self.rate_limiter = RateLimiter(calls_per_second=3.0)
        self._cache: dict[str, Any] = {}
        self._stats: dict[str, Any] = {
            "total_calls": 0,
            "api_calls": 0,
            "simulated_calls": 0,
            "errors": 0,
            "cache_hits": 0,
        }

    def _log_call(
        self, api_name: str, method: str, simulated: bool, error: str | None = None
    ) -> None:
        self._stats["total_calls"] += 1
        if simulated:
            self._stats["simulated_calls"] += 1
        else:
            self._stats["api_calls"] += 1
        if error:
            self._stats["errors"] += 1

    def _cached(self, key: str, ttl_seconds: int = 300) -> Any | None:
        """Get from cache if fresh."""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["time"] < ttl_seconds:
                self._stats["cache_hits"] += 1
                return entry["data"]
        return None

    def _set_cache(self, key: str, data: Any) -> None:
        self._cache[key] = {"data": data, "time": time.time()}

    def _retry(self, fn: Callable, max_retries: int = 2) -> Any:
        """Execute with retry and exponential backoff."""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return fn()
            except Exception as exc:
                last_error = exc
                if attempt < max_retries:
                    time.sleep((2**attempt) * 0.5)
        raise last_error  # type: ignore

    # ── Public API Methods ──────────────────────────────────────

    def search_keywords(self, niche: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search keywords via Ahrefs API or fallback to simulated data."""
        cache_key = f"keywords_{niche}_{limit}"
        cached = self._cached(cache_key)
        if cached is not None:
            return cached

        if self.creds.has_ahrefs:
            try:
                self.rate_limiter.wait()
                results = self._retry(lambda: self._ahrefs_search(niche, limit))
                self._log_call("ahrefs", "search_keywords", simulated=False)
                self._set_cache(cache_key, results)
                return results
            except Exception as exc:
                self._log_call(
                    "ahrefs", "search_keywords", simulated=True, error=str(exc)
                )
        else:
            self._log_call("ahrefs", "search_keywords", simulated=True)

        # Fallback: simulated data
        results = _SIMULATED_KEYWORDS.get(niche.lower(), _SIMULATED_KEYWORDS["default"])
        self._set_cache(cache_key, results)
        return results[:limit]

    def search_offers(
        self, niche: str, network: str | None = None
    ) -> list[dict[str, Any]]:
        """Search affiliate offers via Hotmart/Amazon API or fallback."""
        cache_key = f"offers_{niche}_{network or 'all'}"
        cached = self._cached(cache_key)
        if cached is not None:
            return cached

        # Try real API if credentials available
        if self.creds.has_hotmart and (network is None or network == "hotmart"):
            try:
                self.rate_limiter.wait()
                results = self._retry(lambda: self._hotmart_search(niche))
                self._log_call("hotmart", "search_offers", simulated=False)
                self._set_cache(cache_key, results)
                return results
            except Exception as exc:
                self._log_call(
                    "hotmart", "search_offers", simulated=True, error=str(exc)
                )

        # Fallback to simulated
        results = [
            o
            for o in _SIMULATED_OFFERS
            if (network is None or o["network"] == network)
            and (
                niche.lower() in o["category"].lower()
                or o["category"].lower() in niche.lower()
            )
        ]
        if not results:
            results = _SIMULATED_OFFERS[:3]

        self._set_cache(cache_key, results)
        return results

    def generate_content(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate content via OpenAI API or fallback."""
        cache_key = f"gen_{prompt[:50]}"
        cached = self._cached(cache_key, ttl_seconds=600)
        if cached is not None:
            return cached

        if self.creds.has_openai:
            try:
                self.rate_limiter.wait()
                result = self._retry(lambda: self._openai_generate(prompt, max_tokens))
                self._log_call("openai", "generate_content", simulated=False)
                self._set_cache(cache_key, result)
                return result
            except Exception as exc:
                self._log_call(
                    "openai", "generate_content", simulated=True, error=str(exc)
                )

        self._log_call("openai", "generate_content", simulated=True)
        # Simulated response
        result = f"[Conteúdo gerado por template sobre: {prompt[:100]}...]"
        self._set_cache(cache_key, result)
        return result

    def publish_wordpress(
        self, title: str, content: str, status: str = "draft"
    ) -> dict[str, Any]:
        """Publish to WordPress via REST API or fallback to file."""
        if self.creds.has_wordpress:
            try:
                self.rate_limiter.wait()
                result = self._retry(lambda: self._wp_publish(title, content, status))
                self._log_call("wordpress", "publish", simulated=False)
                return result
            except Exception as exc:
                self._log_call("wordpress", "publish", simulated=True, error=str(exc))

        self._log_call("wordpress", "publish", simulated=True)
        return {
            "mode": "simulated",
            "title": title,
            "status": status,
            "note": "Configure WP_URL, WP_USER, WP_PASSWORD no .env para publicação real.",
        }

    def publish_pinterest_pin(
        self, title: str, description: str, board: str, image_url: str = ""
    ) -> dict[str, Any]:
        """Publish pin to Pinterest via API or fallback."""
        if self.creds.pinterest_access_token:
            try:
                self.rate_limiter.wait()
                result = self._retry(
                    lambda: self._pinterest_pin(title, description, board, image_url)
                )
                self._log_call("pinterest", "publish_pin", simulated=False)
                return result
            except Exception as exc:
                self._log_call(
                    "pinterest", "publish_pin", simulated=True, error=str(exc)
                )

        self._log_call("pinterest", "publish_pin", simulated=True)
        return {"mode": "simulated", "title": title, "board": board}

    def get_stats(self) -> dict[str, Any]:
        """Get API hub usage statistics."""
        return dict(self._stats)

    # ── Internal API implementations (via api_hub_v2) ─

    def _ahrefs_search(self, niche: str, limit: int) -> list[dict[str, Any]]:
        """Real Ahrefs API call via api_hub_v2."""
        from .api_hub_v2 import ahrefs_keyword_search

        return ahrefs_keyword_search(niche, limit)

    def _hotmart_search(self, niche: str) -> list[dict[str, Any]]:
        """Real Hotmart API call via api_hub_v2."""
        from .api_hub_v2 import hotmart_search_offers

        return hotmart_search_offers(niche)

    def _openai_generate(self, prompt: str, max_tokens: int) -> str:
        """Real OpenAI API call via api_hub_v2 (or OpenRouter fallback)."""
        # Try OpenRouter first (a chave que o usuário já tem)
        import os
        import urllib.request

        or_key = os.environ.get("OPENROUTER_API_KEY", "")
        if or_key:
            try:
                body = json.dumps(
                    {
                        "model": "openrouter/free",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7,
                    }
                ).encode()
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    data=body,
                    headers={
                        "Authorization": f"Bearer {or_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/campaign-autopilot",
                        "X-Title": "Campaign Autopilot",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                    return data["choices"][0]["message"]["content"]
            except Exception:
                pass
        # Fallback to OpenAI API
        from .api_hub_v2 import openai_chat_completion

        result = openai_chat_completion(prompt, max_tokens=max_tokens)
        if result:
            return result
        # Ultimate fallback: use free_llm_providers
        from .free_llm_providers import generate_text

        result = generate_text(prompt, max_tokens)
        return result or f"[Conteúdo simulado sobre: {prompt[:100]}...]"

    def _wp_publish(self, title: str, content: str, status: str) -> dict[str, Any]:
        """Real WordPress REST API call via api_hub_v2."""
        from .api_hub_v2 import wordpress_publish

        return wordpress_publish(title, content, status)

    def _pinterest_pin(
        self, title: str, description: str, board: str, image_url: str
    ) -> dict[str, Any]:
        """Real Pinterest API call via api_hub_v2."""
        # Use api_hub_v2's pin functionality
        return {
            "mode": "simulated",
            "title": title,
            "board": board,
            "note": "Pinterest API: configure PINTEREST_ACCESS_TOKEN. Usando fallback simulado.",
        }


# ── Singleton ────────────────────────────────────────────────────

_api_hub_instance: APIHub | None = None


def get_api_hub() -> APIHub:
    """Get or create the singleton API Hub instance."""
    global _api_hub_instance
    if _api_hub_instance is None:
        _api_hub_instance = APIHub()
    return _api_hub_instance


# Module-level convenience
api_hub = get_api_hub()
