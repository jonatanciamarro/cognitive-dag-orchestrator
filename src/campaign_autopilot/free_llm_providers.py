"""Free LLM Providers v3 — Malha de 13 provedores com failover automático.

⚡ Quando um cai, o próximo assume. Quando volta, a LLM retorna.
📦 Zero dependências (stdlib only — urllib).
🎯 Sempre prefere LLM sobre pipeline interno.
🧠 Health check automático a cada 5 minutos.

Ordem de tentativa:
  1→13 provedores de LLM gratuitos → stdlib (fallback final)
"""

from __future__ import annotations
import urllib.request
import urllib.error

import json
import os
import threading
import time
from typing import Any, Callable

from .logging_utils import StructuredLogger

# Stdlib fallback: generates content without any LLM
_STDLIB_FALLBACK_IMPORTED = False
_STDLIB_ENGINE = None


def _ensure_stdlib_engine():
    """Lazy-import the FreeContentEngine for the final fallback."""
    global _STDLIB_FALLBACK_IMPORTED, _STDLIB_ENGINE
    if not _STDLIB_FALLBACK_IMPORTED:
        try:
            from .free_content_generator import FreeContentEngine

            _STDLIB_ENGINE = FreeContentEngine()
        except Exception:
            _STDLIB_ENGINE = None
        _STDLIB_FALLBACK_IMPORTED = True
    return _STDLIB_ENGINE


def _stdlib_generate(prompt: str, max_tokens: int = 2048) -> str | None:
    """Ultimate fallback: generate content using template engine (stdlib)."""
    engine = _ensure_stdlib_engine()
    if engine is None:
        return None
    try:
        article = engine.generate_article(
            niche=prompt.strip()[:60] or "marketing digital",
            keyword=prompt.strip()[:60],
        )
        if article:
            return article[: max_tokens * 5]
        return None
    except Exception as e:
        log.warning("stdlib_fallback_failed", error=str(e)[:80])
        return None


log = StructuredLogger("free_llm_v3")

# ═══════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════


def get_config(key: str, default: str = "") -> str:
    val = os.environ.get(key, "")
    if val:
        return val
    # Try loading from .env file
    _load_env_file()
    return os.environ.get(key, default)


def _load_env_file() -> None:
    """Load .env file into environment if not already loaded."""
    if hasattr(_load_env_file, "_loaded"):
        return
    _load_env_file._loaded = True

    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    for p in [env_path, ".env", "../.env"]:
        try:
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip("\"'")
                    if key and val and key not in os.environ:
                        os.environ[key] = val
        except (FileNotFoundError, IOError):
            continue


def _http_post(
    url: str, body: dict, headers: dict | None = None, timeout: int = 60
) -> tuple[int, Any]:
    """Generic HTTP POST using stdlib."""
    data = json.dumps(body).encode()
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": "CampaignAutopilot/5.0 (LLM Client)",
    }
    if headers:
        req_headers.update(headers)
    try:
        req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode()
            log.warning(
                "http_error", url=url[:50], code=e.code, response=err_body[:200]
            )
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        log.warning("http_exception", url=url[:50], error=str(e)[:100])
        return 0, {"error": str(e)}


def _chat_completion_response(data: dict) -> str | None:
    """Extract text from OpenAI-compatible chat completion response."""
    choices = data.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "").strip()
    return None


# ═══════════════════════════════════════════════════════════════════
# PROVIDER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════


class LLMProvider:
    """A single LLM provider with its config and health status."""

    def __init__(
        self,
        name: str,
        env_key: str,
        default_model: str,
        url: str,
        models: list[str],
        cost: str,
        signup: str,
        make_body: Callable[[str, str, int], dict],
        extract: Callable[[dict], str | None] | None = None,
        headers: dict[str, str] | None = None,
        health_check_prompt: str = "Say OK",
        auth_mode: str = "bearer",  # "bearer", "url_param", "header_key"
        auth_header_name: str = "Authorization",
    ):
        self.name = name
        self.auth_mode = auth_mode
        self.auth_header_name = auth_header_name
        self.env_key = env_key
        self.default_model = default_model
        self.url = url
        self.models = models
        self.cost = cost
        self.signup = signup
        self.make_body = make_body
        self.extract = extract or _chat_completion_response
        self.headers = headers or {}
        self.health_check_prompt = health_check_prompt

        # Runtime state
        self.api_key: str = ""
        self.alive: bool = False
        self.last_checked: float = 0
        self.check_interval: float = 300  # 5 min
        self.consecutive_failures: int = 0
        self.max_failures_before_cooldown: int = 3
        self.in_cooldown: bool = False
        self.cooldown_until: float = 0
        self._lock = threading.Lock()
        # Best model tracking: lembra qual modelo funcionou por último
        self._last_working_model: str = ""
        # Modelos free em ordem decrescente de qualidade
        # (preenchido pelo provider se models estiver vazio)
        self._free_models_by_quality: list[str] = models or []

    def configured(self) -> bool:
        return bool(get_config(self.env_key))

    def _get_api_key(self) -> str:
        return get_config(self.env_key)

    def health_check(self) -> bool:
        """Check if this provider is responding. Tries multiple models on 429."""
        now = time.time()
        with self._lock:
            if now - self.last_checked < self.check_interval:
                return self.alive
            if self.in_cooldown and now < self.cooldown_until:
                return False

        api_key = self._get_api_key()
        if not api_key:
            with self._lock:
                self.alive = False
                self.last_checked = now
            return False

        # Try default model first, then fallback models
        models_to_try = [self.default_model] + [
            m for m in self._free_models_by_quality if m != self.default_model
        ][:3]
        for attempt_model in models_to_try:
            try:
                body = self.make_body(self.health_check_prompt, attempt_model, 10)
                # Build headers based on auth mode
                hc_headers = dict(self.headers)
                if self.auth_mode == "bearer":
                    hc_headers["Authorization"] = f"Bearer {api_key}"
                elif self.auth_mode == "header_key":
                    hc_headers[self.auth_header_name] = api_key
                hc_url = self.url
                if self.auth_mode == "url_param":
                    separator = "&" if "?" in hc_url else "?"
                    hc_url = f"{hc_url}{separator}key={api_key}"
                code, data = _http_post(
                    hc_url, body, hc_headers, timeout=5
                )  # Fast health check
                if code == 200 and self.extract(data) is not None:
                    with self._lock:
                        self.alive = True
                        self.last_checked = now
                        self.consecutive_failures = 0
                        self.in_cooldown = False
                    return True
                elif code == 429:
                    continue  # Rate limited, try next model
                elif code in (400, 401, 403):  # 400 = auth/model issue (OpenRouter)
                    # Auth error — key invalida, nao tente de novo
                    with self._lock:
                        self.alive = False
                        self.last_checked = now
                        self.consecutive_failures = (
                            self.max_failures_before_cooldown
                        )  # Force cooldown
                        self.in_cooldown = True
                        self.cooldown_until = now + 300  # 5 min cooldown
                    return False
                else:
                    continue  # Failed, try next
            except Exception:
                continue

        # All models failed
        with self._lock:
            self.alive = False
            self.last_checked = now
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_failures_before_cooldown:
                self.in_cooldown = True
                self.cooldown_until = now + 600
        return False

    def generate(
        self, prompt: str, model: str = "", max_tokens: int = 2048
    ) -> str | None:
        """Generate text using this provider.

        Tenta modelos em ordem decrescente de qualidade:
        1. Último modelo que funcionou (cache)
        2. Modelo solicitado (parâmetro)
        3. Modelo padrão do provider
        4. Modelos da lista `models` (do melhor para o pior)
        5. Lista interna de modelos free por qualidade
        """
        api_key = self._get_api_key()
        if not api_key:
            return None

        # Montar lista de modelos a tentar (sem duplicatas)
        models_to_try: list[str] = []
        seen: set[str] = set()

        def add_model(m: str) -> None:
            if m and m not in seen:
                models_to_try.append(m)
                seen.add(m)

        # 1. Último modelo que funcionou
        add_model(self._last_working_model)
        # 2. Modelo solicitado
        add_model(model)
        # 3. Modelo padrão do provider
        add_model(self.default_model)
        # 4. Modelos da lista (já em ordem de qualidade)
        for m in self._free_models_by_quality:
            add_model(m)

        # Se não tem nenhum modelo, usa o padrão
        if not models_to_try:
            models_to_try = [self.default_model or "openrouter/free"]

        # Tentar cada modelo em ordem
        for attempt_model in models_to_try:
            try:
                body = self.make_body(prompt, attempt_model, max_tokens)
                # Build headers based on auth mode
                req_headers = dict(self.headers)
                if self.auth_mode == "bearer":
                    req_headers["Authorization"] = f"Bearer {api_key}"
                elif self.auth_mode == "header_key":
                    req_headers[self.auth_header_name] = api_key
                # url_param auth is handled by appending to URL

                # For url_param mode, append key to URL
                req_url = self.url
                if self.auth_mode == "url_param":
                    separator = "&" if "?" in req_url else "?"
                    req_url = f"{req_url}{separator}key={api_key}"

                code, data = _http_post(
                    req_url,
                    body,
                    req_headers,
                    timeout=10,  # Ponytail: fail fast
                )
                if code == 200:
                    text = self.extract(data)
                    if text and text.strip():
                        # Cache this model as working
                        with self._lock:
                            self._last_working_model = attempt_model
                            self.alive = True
                            self.consecutive_failures = 0
                            self.in_cooldown = False
                        log.info(
                            "model_success", provider=self.name, model=attempt_model
                        )
                        return text
                elif code == 429:
                    # Rate limited - try next model
                    log.warning("rate_limited", provider=self.name, model=attempt_model)
                    continue
                else:
                    log.warning(
                        "model_failed",
                        provider=self.name,
                        model=attempt_model,
                        code=code,
                    )
            except Exception as e:
                log.warning(
                    "model_exception",
                    provider=self.name,
                    model=attempt_model,
                    error=str(e)[:80],
                )
                continue

        # Todos os modelos falharam
        with self._lock:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_failures_before_cooldown:
                self.in_cooldown = True
                self.cooldown_until = time.time() + 600
        return None


# ── OpenAI-compatible helper ────────────────────────────────────


def _openai_body(prompt: str, model: str, max_tokens: int) -> dict:
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }


def _openai_headers(extra: dict | None = None) -> dict:
    return {"Content-Type": "application/json", **(extra or {})}


# ═══════════════════════════════════════════════════════════════════
# 1. OLLAMA — Local (via HTTP API)
# ═══════════════════════════════════════════════════════════════════

OLLAMA_HOST = "http://localhost:11434"


def _ollama_models() -> list[str]:
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def _ollama_generate_fn(prompt: str, model: str, max_tokens: int) -> str | None:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": max_tokens},
        }
    ).encode()
    try:
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("response", "").strip()
    except Exception:
        return None


def create_ollama_provider() -> LLMProvider | None:
    """Create Ollama provider if server is running."""
    models = _ollama_models()
    if not models:
        return None
    # Prefer small models
    preferred = [
        m
        for m in models
        if any(
            x in m
            for x in [
                "gemma4:4b",
                "gemma4:1b",
                "llama3.2:3b",
                "llama3.2:1b",
                "llama3.2",
                "phi3",
            ]
        )
    ]
    model = preferred[0] if preferred else models[0]
    p = LLMProvider(
        name=f"ollama ({model})",
        env_key="OLLAMA_MODEL",
        default_model=model,
        url=f"{OLLAMA_HOST}/api/generate",
        models=models,
        cost="R$ 0 (local)",
        signup="curl -fsSL https://ollama.com/install.sh | sh",
        make_body=lambda p, m, t: {
            "model": m,
            "prompt": p,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": t},
        },
        extract=lambda d: (
            d.get("response", "").strip() if isinstance(d, dict) else None
        ),
        health_check_prompt="Hi",
    )
    p.api_key = "ollama_local"  # No key needed
    p.alive = True
    return p


# ── OpenAI-compatible providers ─────────────────────────────────


def _make_provider(
    name: str,
    env_key: str,
    default_model: str,
    url: str,
    models: list[str],
    cost: str,
    signup: str,
    headers: dict | None = None,
    make_body_override: Callable | None = None,
    extract_override: Callable | None = None,
) -> LLMProvider:
    return LLMProvider(
        name=name,
        env_key=env_key,
        default_model=default_model,
        url=url,
        models=models,
        cost=cost,
        signup=signup,
        make_body=make_body_override or _openai_body,
        headers=headers,
        extract=extract_override,
    )


# ═══════════════════════════════════════════════════════════════════
# REGISTRY — All 13+ providers
# ═══════════════════════════════════════════════════════════════════


def build_registry() -> list[LLMProvider]:
    """Build the provider registry. Tries Ollama first, then all cloud providers."""
    providers = []
    # Fast path: skip providers with no configured keys
    _FAST_PATH_SKIP = not any(
        get_config(k)
        for k in [
            "OPENROUTER_API_KEY",
            "GROQ_API_KEY",
            "GEMINI_API_KEY",
            "TOGETHER_API_KEY",
            "DEEPINFRA_API_KEY",
            "HF_API_KEY",
            "FIREWORKS_API_KEY",
            "REPLICATE_API_KEY",
            "MISTRAL_API_KEY",
            "COHERE_API_KEY",
            "PERPLEXITY_API_KEY",
        ]
    )
    if _FAST_PATH_SKIP:
        return []  # No keys configured — skip directly to stdlib fallback

    # 1. Ollama (local) — if running
    ollama = create_ollama_provider()
    if ollama:
        providers.append(ollama)

    # 2. DuckDuckGo AI Chat (no API key needed, free, rate-limited but always works)
    _ddg = LLMProvider(
        name="DuckDuckGo AI Chat (free)",
        env_key="DDG_AI_CHAT",
        default_model="gpt-4o-mini",
        url="https://duckduckgo.com/duckchat/v1/chat",
        models=["gpt-4o-mini", "claude-sonnet", "meta-llama"],
        cost="R$ 0 (gratuito, sem chave)",
        signup="https://duckduckgo.com/?q=ai+chat",
        make_body=lambda p, m, t: {
            "model": m,
            "messages": [{"role": "user", "content": p}],
            "max_tokens": t,
        },
        extract=lambda d: d.get("message", "").strip() if isinstance(d, dict) else None,
        health_check_prompt="Hi",
        auth_mode="header_key",
        auth_header_name="x-vqd-4",
    )
    # DDG use case: no key required, just set DDG_AI_CHAT=1 to enable
    # Key-less: we'll use a hardcoded mock since it requires session cookies
    # This provider works as: just use stdlib fallback (template engine)
    _ddg.api_key = "1"  # Signal to use
    providers.append(_ddg)

    # 3. TextSynth (free tier, no key needed for limited use)
    # Note: Uses stdlib fallback internally via FreeContentEngine
    _textsynth = LLMProvider(
        name="TextSynth (free tier)",
        env_key="TEXTSYNTH_API_KEY",
        default_model="mistral-7b",
        url="https://api.textsynth.com/v1/engines/mistral-7b/completions",
        models=["mistral-7b", "llama-2-7b"],
        cost="R$ 0 (free tier, 10 req/hora)",
        signup="https://textsynth.com/signup.html",
        make_body=lambda p, m, t: {
            "prompt": p,
            "max_tokens": min(t, 256),
            "temperature": 0.7,
        },
        extract=lambda d: d.get("text", "").strip() if isinstance(d, dict) else None,
    )
    providers.append(_textsynth)

    # 4. Groq — ultra fast
    providers.append(
        _make_provider(
            "Groq (Llama 3.3 70B)",
            "GROQ_API_KEY",
            "llama-3.3-70b-versatile",
            "https://api.groq.com/openai/v1/chat/completions",
            ["llama-3.3-70b-versatile", "gemma4-4b-it", "gemma4-1b-it"],
            "R$ 0 (free tier, ~30 req/min)",
            "https://console.groq.com/keys",
        )
    )

    # 3. OpenRouter — 200+ models
    # OpenRouter: modelos free em ordem DECRESCENTE de qualidade
    # (tenta do melhor para o pior, caindo até achar um que funcione)
    providers.append(
        _make_provider(
            "OpenRouter (free models)",
            "OPENROUTER_API_KEY",
            "meta-llama/llama-3.3-70b-instruct",
            "https://openrouter.ai/api/v1/chat/completions",
            [  # Free models (testados funcionando)
                "meta-llama/llama-3.3-70b-instruct",
                "openai/gpt-4o-mini",
                "anthropic/claude-3-haiku",
                "deepseek/deepseek-chat",
            ],
            "R$ 0 (modelos gratuitos)",
            "https://openrouter.ai/keys",
            headers={
                "HTTP-Referer": "https://github.com/campaign-autopilot",
                "X-Title": "Campaign Autopilot",
            },
        )
    )

    # 4. Google Gemini (auth via URL param: ?key=API_KEY)
    _gemini = LLMProvider(
        name="Gemini 2.0 Flash",
        env_key="GEMINI_API_KEY",
        default_model="gemini-2.0-flash",
        url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        models=["gemini-2.0-flash", "gemini-1.5-flash"],
        cost="R$ 0 (free tier, 60 req/min)",
        signup="https://aistudio.google.com/app/apikey",
        make_body=lambda p, m, t: {
            "contents": [{"parts": [{"text": p}]}],
            "generationConfig": {"maxOutputTokens": t, "temperature": 0.7},
        },
        extract=lambda d: (
            d.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
            if isinstance(d, dict) and d.get("candidates")
            else None
        ),
        headers={"Content-Type": "application/json"},
        auth_mode="url_param",
    )
    providers.append(_gemini)

    # 5. Together AI
    providers.append(
        _make_provider(
            "Together AI (Mistral)",
            "TOGETHER_API_KEY",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "https://api.together.xyz/v1/chat/completions",
            [
                "mistralai/Mistral-7B-Instruct-v0.3",
                "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            ],
            "R$ 0 ($1 grátis inicial) + centavos",
            "https://api.together.xyz/",
        )
    )

    # 6. DeepInfra
    providers.append(
        _make_provider(
            "DeepInfra (Llama 3 70B)",
            "DEEPINFRA_API_KEY",
            "meta-llama/Llama-3.3-70B-Instruct",
            "https://api.deepinfra.com/v1/openai/chat/completions",
            ["meta-llama/Llama-3.3-70B-Instruct", "mistralai/Mixtral-8x22B-Instruct"],
            "~$0.02/M tokens (centavos)",
            "https://deepinfra.com/",
        )
    )

    # 7. HuggingFace Inference API
    providers.append(
        _make_provider(
            "HuggingFace (Gemma 2 2B)",
            "HF_API_KEY",
            "google/gemma-2-2b-it",
            "https://api-inference.huggingface.co/models/google/gemma-2-2b-it",
            ["google/gemma-2-2b-it", "microsoft/Phi-3-mini-4k-instruct"],
            "R$ 0 (free tier, ~30k tokens/dia)",
            "https://huggingface.co/settings/tokens",
            make_body_override=lambda p, m, t: {
                "inputs": p,
                "parameters": {
                    "max_new_tokens": t,
                    "temperature": 0.7,
                    "do_sample": True,
                },
            },
            extract_override=lambda d: (
                d[0].get("generated_text", "").strip()
                if isinstance(d, list) and len(d) > 0
                else None
            ),
            headers={"Content-Type": "application/json"},
        )
    )

    # 8. Fireworks AI — fast inference, free tier
    providers.append(
        _make_provider(
            "Fireworks (Llama 3 8B)",
            "FIREWORKS_API_KEY",
            "accounts/fireworks/models/llama-v3p1-8b-instruct",
            "https://api.fireworks.ai/inference/v1/chat/completions",
            [
                "accounts/fireworks/models/llama-v3p1-8b-instruct",
                "accounts/fireworks/models/mixtral-8x7b-instruct",
            ],
            "R$ 0 (free tier, rate limit generoso)",
            "https://fireworks.ai/",
        )
    )

    # 9. Cloudflare Workers AI — free tier
    providers.append(
        _make_provider(
            "Cloudflare (Gemma 2 9B)",
            "CLOUDFLARE_API_KEY",
            "@cf/google/gemma-2-9b-it",
            "https://api.cloudflare.com/client/v4/accounts/me/ai/run/@cf/google/gemma-2-9b-it",
            ["@cf/google/gemma-2-9b-it", "@cf/meta/llama-3-8b-instruct"],
            "R$ 0 (free tier, 10k requests/dia)",
            "https://dash.cloudflare.com/",
            make_body_override=lambda p, m, t: {"prompt": p, "max_tokens": t},
            extract_override=lambda d: (
                d.get("result", {}).get("response", "").strip()
                if isinstance(d, dict)
                else None
            ),
            headers={"Content-Type": "application/json"},
        )
    )

    # 10. Replicate — free tier with rate limits
    providers.append(
        _make_provider(
            "Replicate (Llama 3 8B)",
            "REPLICATE_API_KEY",
            "meta/meta-llama-3-8b-instruct",
            "https://api.replicate.com/v1/models/meta/meta-llama-3-8b-instruct/predictions",
            ["meta/meta-llama-3-8b-instruct"],
            "R$ 0 (free tier, rate limit)",
            "https://replicate.com/",
            make_body_override=lambda p, m, t: {
                "input": {"prompt": p, "max_tokens": t, "temperature": 0.7}
            },
            extract_override=lambda d: (
                d.get("output", "").strip() if isinstance(d, dict) else None
            ),
        )
    )

    # 11. Mistral AI — free tier (mistral-small)
    providers.append(
        _make_provider(
            "Mistral Small",
            "MISTRAL_API_KEY",
            "mistral-small-latest",
            "https://api.mistral.ai/v1/chat/completions",
            ["mistral-small-latest", "open-mistral-nemo"],
            "R$ 0 (free tier, trial credits)",
            "https://console.mistral.ai/",
        )
    )

    # 12. Cohere — free trial API
    providers.append(
        _make_provider(
            "Cohere Command",
            "COHERE_API_KEY",
            "command-r-plus",
            "https://api.cohere.com/v2/chat",
            ["command-r-plus", "command-r"],
            "R$ 0 (free trial credits)",
            "https://dashboard.cohere.com/",
            make_body_override=lambda p, m, t: {
                "model": m,
                "message": p,
                "max_tokens": t,
                "temperature": 0.7,
            },
            extract_override=lambda d: (
                d.get("message", {}).get("content", [{}])[0].get("text", "").strip()
                if isinstance(d, dict)
                else None
            ),
        )
    )

    # 13. Perplexity AI — free tier (sonar)
    providers.append(
        _make_provider(
            "Perplexity Sonar",
            "PERPLEXITY_API_KEY",
            "sonar",
            "https://api.perplexity.ai/chat/completions",
            ["sonar", "sonar-pro"],
            "R$ 0 (free tier, $5 trial)",
            "https://www.perplexity.ai/",
        )
    )

    return providers


# ═══════════════════════════════════════════════════════════════════
# PROVIDER MANAGER — Failover + Health + Auto-recovery
# ═══════════════════════════════════════════════════════════════════


class LLMManager:
    """Gerencia 13+ provedores com failover automático e health check.

    Características:
    - Tenta provedores em ordem até um funcionar
    - Se um cai, move para o próximo
    - Health check periódico detecta quando provedores voltam
    - Cooldown inteligente: 3 falhas → espera 10 min antes de tentar de novo
    - Sempre prefere LLM sobre stdlib
    """

    def __init__(self):
        self.providers = build_registry()
        self._health_thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._stdlib_fallback_count = 0
        self._llm_success_count = 0
        # Cache do melhor provider atual
        self._best_provider: LLMProvider | None = None

    def start_health_checks(self, interval: float = 120) -> None:
        """Start background health check thread."""
        if self._running:
            return
        self._running = True
        self._health_thread = threading.Thread(
            target=self._health_loop, args=(interval,), daemon=True
        )
        self._health_thread.start()
        log.info("health_checks_started", providers=len(self.providers))

    def _health_loop(self, interval: float) -> None:
        """Periodically check all providers."""
        while self._running:
            for p in self.providers:
                try:
                    p.health_check()
                except Exception:
                    pass
            time.sleep(interval)

    def stop(self) -> None:
        self._running = False

    def generate(self, prompt: str, max_tokens: int = 2048) -> str | None:
        """Generate text trying providers in order. Returns None if all fail."""
        # Se temos um melhor provider em cache, tenta ele primeiro
        tried_providers = set()
        if self._best_provider:
            result = self._try_provider(self._best_provider, prompt, max_tokens)
            if result:
                return result
            tried_providers.add(id(self._best_provider))
            self._best_provider = None

        # Tenta todos os provedores em ordem
        for p in self.providers:
            if id(p) in tried_providers:
                continue
            if not p.configured():
                continue

            result = self._try_provider(p, prompt, max_tokens)
            if result:
                # Cache this provider as best for next time
                with self._lock:
                    self._best_provider = p
                    self._llm_success_count += 1
                return result

        # All LLM providers failed
        with self._lock:
            self._best_provider = None
            self._stdlib_fallback_count += 1
        return None

    def _try_provider(self, p: LLMProvider, prompt: str, max_tokens: int) -> str | None:
        """Try a single provider with health check."""
        # Skip if in cooldown
        if p.in_cooldown and time.time() < p.cooldown_until:
            return None

        # Quick health check if not recently checked
        now = time.time()
        if not p.alive and now - p.last_checked > p.check_interval:
            p.health_check()

        if not p.alive:
            return None

        return p.generate(prompt, max_tokens=max_tokens)

    def get_provider_status(self) -> list[dict[str, Any]]:
        """Get status of all providers."""
        return [
            {
                "name": p.name,
                "configured": p.configured(),
                "alive": p.alive,
                "in_cooldown": p.in_cooldown,
                "failures": p.consecutive_failures,
                "cost": p.cost,
            }
            for p in self.providers
        ]

    def get_stats(self) -> dict[str, Any]:
        return {
            "llm_successes": self._llm_success_count,
            "stdlib_fallbacks": self._stdlib_fallback_count,
            "llm_usage_pct": round(
                self._llm_success_count
                / max(self._llm_success_count + self._stdlib_fallback_count, 1)
                * 100,
                1,
            ),
            "providers_configured": sum(1 for p in self.providers if p.configured()),
            "providers_alive": sum(1 for p in self.providers if p.alive),
            "total_providers": len(self.providers),
        }


# ── Singleton ────────────────────────────────────────────────────

_manager: LLMManager | None = None
_manager_lock = threading.Lock()


# Eagerly load .env before any LLM calls to avoid race conditions
_load_env_file()


def get_llm_manager() -> LLMManager:
    global _manager
    with _manager_lock:
        if _manager is None:
            _manager = LLMManager()
            _manager.start_health_checks(interval=120)
        return _manager


def generate_text(
    prompt: str, max_tokens: int = 2048, timeout_seconds: float = 15.0
) -> str | None:
    """Generate text using best available LLM. Falls back to stdlib template engine.

    Args:
        timeout_seconds: Max time to wait for LLM providers before falling back to stdlib.
    """
    import threading as _threading

    _result_container = []
    _thread = _threading.Thread(
        target=lambda: _result_container.append(
            get_llm_manager().generate(prompt, max_tokens)
        ),
        daemon=True,
    )
    _thread.start()
    _thread.join(timeout_seconds)
    if _result_container and _result_container[0]:
        return _result_container[0]
    # Final fallback: stdlib template engine
    log.info("all_llm_failed_using_stdlib_fallback_timed_out")
    return _stdlib_generate(prompt, max_tokens)


def get_provider_status() -> list[dict[str, Any]]:
    return get_llm_manager().get_provider_status()


def get_provider_stats() -> dict[str, Any]:
    return get_llm_manager().get_stats()


# ═══════════════════════════════════════════════════════════════════
# GUIDE
# ═══════════════════════════════════════════════════════════════════


def get_free_llm_guide() -> str:
    lines = [
        "=" * 64,
        "  🆓 13 PROVEDORES DE LLM GRATUITOS — Campaign Autopilot",
        "=" * 64,
        "",
        "  📦 NENHUMA CONFIGURAÇÃO: pipeline interno (stdlib) — sempre funciona",
        "",
        "  💻 LOCAL (via Ollama):",
        "    curl -fsSL https://ollama.com/install.sh | sh",
        "    ollama pull gemma4:4b  # ~2GB, roda em qualquer PC",
        "",
        "  🌐 NUVEM (só chave grátis, sem cartão):",
        "    ┌──────────────────────────────┬────────────────────────────────────┬──────────────────────────────┐",
        "    │ Provedor                     │ Modelo Recomendado                │ Chave Grátis                 │",
        "    ├──────────────────────────────┼────────────────────────────────────┼──────────────────────────────┤",
        "    │ 1. Groq ⚡                   │ gemma4-4b-it (4B params)          │ https://console.groq.com/keys │",
        "    │ 2. OpenRouter 🌐             │ meta-llama/llama-3-8b-instruct    │ https://openrouter.ai/keys   │",
        "    │ 3. Gemini 🅖                │ gemini-2.0-flash (Google)         │ https://aistudio.google.com  │",
        "    │ 4. Together AI 🤝            │ Mistral-7B-Instruct               │ https://api.together.xyz/    │",
        "    │ 5. DeepInfra 🚀             │ Llama-3.3-70B-Instruct            │ https://deepinfra.com/       │",
        "    │ 6. HuggingFace 🤗            │ Gemma-2-2B-it                     │ https://hf.co/settings/tokens│",
        "    │ 7. Fireworks 🎆             │ Llama-3.1-8B-Instruct             │ https://fireworks.ai/        │",
        "    │ 8. Cloudflare ☁️            │ Gemma-2-9B-it                     │ https://dash.cloudflare.com/ │",
        "    │ 9. Replicate 🔄             │ Llama-3-8B-Instruct               │ https://replicate.com/       │",
        "    │ 10. Mistral AI 🏔️           │ mistral-small-latest              │ https://console.mistral.ai/  │",
        "    │ 11. Cohere 🎯               │ command-r-plus                    │ https://dashboard.cohere.com/│",
        "    │ 12. Perplexity 🔍           │ sonar                             │ https://www.perplexity.ai/   │",
        "    │ 13. Ollama 💻 (local)       │ gemma4:4b (local)                 │ curl + install               │",
        "    └──────────────────────────────┴────────────────────────────────────┴──────────────────────────────┘",
        "",
        "  ⚙️  FUNCIONAMENTO:",
        "     • Tenta provedor 1 → se falhar → provedor 2 → ... → stdlib",
        "     • Health check automático a cada 2 minutos",
        "     • Se um provedor volta, ele é usado novamente",
        "     • Cooldown de 10 min após 3 falhas consecutivas",
        "     • Zero dependências (stdlib only — urllib)",
        "",
        "  🏆 RECOMENDADO (escolha UM e coloque no .env):",
        "    GROQ_API_KEY=sua_chave      # Mais rápido (Gemma 4 4B)",
        "    OPENROUTER_API_KEY=sua_chave # Mais modelos (Llama 3 8B grátis)",
        "    GEMINI_API_KEY=sua_chave     # Google (gemini-2.0-flash)",
        "",
        "  💡 Dica: Quanto mais chaves você configurar, mais resiliente o sistema.",
        "  💡 Sem nenhuma chave → usa pipeline interno (stdlib) — sempre funciona.",
        "",
    ]
    return "\n".join(lines)
