"""Text provider classes and functions."""

from __future__ import annotations

import io
import json
import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Lock
from time import time, sleep
from typing import Any, Optional, Iterator
from urllib.parse import quote_plus

# Package imports
from .base import ProviderCapability, ProviderMetadata, TextProvider

class LiteLLMTextProvider(TextProvider):
    """Unified text provider via LiteLLM — 100+ models, OpenAI-compatible.

    Suporta: OpenRouter, Groq, DeepSeek, Gemini, Anthropic, Ollama, etc.
    Basta configurar a chave da API desejada no .env.
    """

    _imported = False
    _litellm = None

    def __init__(self):
        self._meta = ProviderMetadata(
            name="litellm",
            display_name="LiteLLM Unified",
            provider_type="text",
            capabilities={
                ProviderCapability.TEXT_GENERATION,
                ProviderCapability.STREAMING,
                ProviderCapability.FUNCTION_CALLING,
                ProviderCapability.MULTI_MODAL,
            },
            quality_rank=100,
            is_free=True,
            avg_latency_ms=1500,
        )

    def _ensure_import(self) -> bool:
        if not LiteLLMTextProvider._imported:
            try:
                import litellm  # noqa: F401

                LiteLLMTextProvider._litellm = True
            except ImportError:
                LiteLLMTextProvider._litellm = False
            LiteLLMTextProvider._imported = True
        return LiteLLMTextProvider._litellm

    def name(self) -> str:
        return "litellm"

    def metadata(self) -> ProviderMetadata:
        return self._meta

    def is_available(self) -> bool:
        # Just check if package exists without actual import
        try:
            from importlib.metadata import version

            version("litellm")
            return True
        except Exception:
            return False

    def generate(
        self, prompt: str, model: str = "", max_tokens: int = 2048
    ) -> str | None:
        if not self._ensure_import():
            return None
        try:
            import litellm
            import os

            # Detect configured API keys and prioritize those models
            has_openrouter = bool(os.environ.get("OPENROUTER_API_KEY"))
            has_groq = bool(os.environ.get("GROQ_API_KEY"))
            has_gemini = bool(os.environ.get("GEMINI_API_KEY"))

            models_to_try = []
            if model:
                models_to_try.append(model)

            # Prioritize models based on available API keys
            if has_groq:
                models_to_try.extend(
                    [
                        "groq/llama-3.3-70b-versatile",
                        "groq/gemma4-4b-it",
                        "groq/gemma2-9b-it",
                        "groq/llama-3.2-3b-preview",
                    ]
                )
            if has_openrouter:
                models_to_try.extend(
                    [
                        "openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
                        "openrouter/meta-llama/llama-3.3-70b-instruct:free",
                        "openrouter/google/gemma-4-31b-it:free",
                        "openrouter/free",
                    ]
                )
            if has_gemini:
                models_to_try.append("gemini/gemini-2.0-flash")

            # Universal fallbacks
            models_to_try.extend(
                [
                    "openrouter/free",
                    "groq/gemma4-4b-it",
                ]
            )

            for m in models_to_try:
                try:
                    resp = litellm.completion(
                        model=m,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=0.7,
                        timeout=30,
                    )
                    if resp and resp.choices:
                        return resp.choices[0].message.content
                except Exception:
                    continue
            return None
        except Exception:
            return None
class FreeLLMTextProvider(TextProvider):
    """Usa o sistema existente de 13 provedores gratuitos com failover.

    Wrapper em torno de free_llm_providers.py.
    Zero dependencias (stdlib only).
    """

    def __init__(self):
        self._meta = ProviderMetadata(
            name="free_llm",
            display_name="Free LLM (13 providers)",
            provider_type="text",
            capabilities={ProviderCapability.TEXT_GENERATION},
            quality_rank=80,
            is_free=True,
            avg_latency_ms=3000,
        )

    def name(self) -> str:
        return "free_llm"

    def metadata(self) -> ProviderMetadata:
        return self._meta

    def is_available(self) -> bool:
        try:
            # Quick check: are there any configured providers?
            return True  # Always has stdlib fallback
        except Exception:
            return False

    def generate(
        self, prompt: str, model: str = "", max_tokens: int = 2048
    ) -> str | None:
        try:
            from campaign_autopilot.free_llm_providers import generate_text

            return generate_text(prompt, max_tokens=max_tokens)
        except Exception:
            return None
class StdlibFallbackProvider(TextProvider):
    """Final fallback: template engine (stdlib only, sempre funciona)."""

    def __init__(self):
        self._meta = ProviderMetadata(
            name="stdlib",
            display_name="Stdlib Template Engine",
            provider_type="text",
            capabilities={ProviderCapability.TEXT_GENERATION},
            quality_rank=10,
            is_free=True,
            avg_latency_ms=100,
        )

    def name(self) -> str:
        return "stdlib"

    def metadata(self) -> ProviderMetadata:
        return self._meta

    def is_available(self) -> bool:
        return True

    def generate(
        self, prompt: str, model: str = "", max_tokens: int = 2048
    ) -> str | None:
        try:
            from campaign_autopilot.free_llm_providers import _stdlib_generate

            return _stdlib_generate(prompt, max_tokens)
        except Exception:
            return None
