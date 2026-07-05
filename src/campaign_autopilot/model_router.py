"""Multi-Model Router — Cost-aware, quality-aware LLM routing.

Camada sobre LiteLLM e FreeLLMProviders que adiciona:
- Roteamento por custo (escolhe o modelo mais barato que atende)
- Roteamento por qualidade (escolhe o melhor dentro do orcamento)
- Fallback automatico entre providers
- Politicas de roteamento customizaveis
- Rastreamento de custo por chamada

Uso:
    router = ModelRouter()
    result = router.route("Gere um artigo sobre marketing")
    # Auto-seleciona o melhor modelo disponivel
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoutingStrategy(Enum):
    COST_FIRST = "cost_first"  # Mais barato disponivel
    QUALITY_FIRST = "quality_first"  # Melhor qualidade no orcamento
    BALANCED = "balanced"  # Equilibrio custo x qualidade
    FASTEST = "fastest"  # Menor latencia
    FALLBACK_CHAIN = "fallback"  # Tenta do melhor para o pior


class ModelTier(Enum):
    PREMIUM = "premium"  # GPT-4, Claude 3.5, Gemini 2.0 Pro
    STANDARD = "standard"  # GPT-4o-mini, Claude 3 Haiku
    FREE = "free"  # Llama 3, Gemma, Mistral via free APIs


@dataclass
class ModelEndpoint:
    """A single model endpoint with cost/quality metadata."""

    name: str  # e.g. "groq/llama-3.3-70b-versatile"
    provider: str  # e.g. "groq"
    tier: ModelTier = ModelTier.FREE
    cost_per_1k_input: float = 0.0  # USD por 1K tokens de input
    cost_per_1k_output: float = 0.0  # USD por 1K tokens de output
    quality_score: float = 5.0  # 1-10
    avg_latency_ms: float = 500.0
    max_tokens: int = 8192
    supports_streaming: bool = False
    supports_tools: bool = False
    supports_vision: bool = False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (
            input_tokens / 1000 * self.cost_per_1k_input
            + output_tokens / 1000 * self.cost_per_1k_output
        )

    @property
    def is_free(self) -> bool:
        return self.cost_per_1k_input == 0.0 and self.cost_per_1k_output == 0.0


@dataclass
class RoutingPolicy:
    """Politica de roteamento para uma requisicao."""

    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    max_cost: float = 0.01  # USD maximo por chamada
    min_quality: float = 3.0  # Qualidade minima aceitavel
    max_latency_ms: float = 10000.0  # Latencia maxima
    preferred_providers: list[str] = field(default_factory=list)
    blocklisted_providers: list[str] = field(default_factory=list)
    fallback_enabled: bool = True


# ── Model Registry ────────────────────────────────────────────

FALLBACK_CHAIN = [
    # Premium (via chaves pagas)
    ModelEndpoint(
        "openrouter/anthropic/claude-3.5-sonnet",
        "anthropic",
        ModelTier.PREMIUM,
        0.003,
        0.015,
        9.5,
        800,
        supports_tools=True,
    ),
    ModelEndpoint(
        "openrouter/openai/gpt-4o",
        "openai",
        ModelTier.PREMIUM,
        0.0025,
        0.01,
        9.0,
        600,
        supports_tools=True,
    ),
    # Standard (via chaves gratuitas)
    ModelEndpoint(
        "groq/llama-3.3-70b-versatile",
        "groq",
        ModelTier.STANDARD,
        0.0,
        0.0,
        8.5,
        300,
        supports_tools=True,
    ),
    ModelEndpoint("groq/gemma4-4b-it", "groq", ModelTier.STANDARD, 0.0, 0.0, 7.5, 200),
    ModelEndpoint(
        "gemini/gemini-2.0-flash",
        "gemini",
        ModelTier.STANDARD,
        0.0,
        0.0,
        8.0,
        500,
        supports_vision=True,
    ),
    # Free tier (modelos abertos)
    ModelEndpoint(
        "openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
        "openrouter",
        ModelTier.FREE,
        0.0,
        0.0,
        8.0,
        1500,
    ),
    ModelEndpoint(
        "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "openrouter",
        ModelTier.FREE,
        0.0,
        0.0,
        7.5,
        1200,
    ),
    ModelEndpoint(
        "openrouter/google/gemma-4-31b-it:free",
        "openrouter",
        ModelTier.FREE,
        0.0,
        0.0,
        7.0,
        1000,
    ),
    ModelEndpoint(
        "openrouter/qwen/qwen3-coder:free",
        "openrouter",
        ModelTier.FREE,
        0.0,
        0.0,
        7.0,
        800,
    ),
    # Fallback universal
    ModelEndpoint("openrouter/free", "openrouter", ModelTier.FREE, 0.0, 0.0, 5.0, 2000),
]


# ── Model Router ──────────────────────────────────────────────


class ModelRouter:
    """Roteador inteligente de modelos LLM.

    Seleciona o melhor modelo com base em:
    - Custo (evita estourar orcamento)
    - Qualidade (minimo aceitavel)
    - Disponibilidade (provider ativo)
    - Latencia (maximo aceitavel)

    Uso:
        router = ModelRouter()
        text = router.route("Gere um texto", strategy=RoutingStrategy.COST_FIRST)
    """

    def __init__(self):
        self._models = list(FALLBACK_CHAIN)
        self._cache: dict[str, ModelEndpoint | None] = {}

    def route(
        self,
        prompt: str,
        max_tokens: int = 1024,
        strategy: RoutingStrategy | str = RoutingStrategy.BALANCED,
        policy: RoutingPolicy | None = None,
    ) -> str | None:
        """Route a prompt to the best model and return the response."""
        if isinstance(strategy, str):
            strategy = RoutingStrategy(strategy)

        policy = policy or RoutingPolicy(strategy=strategy)
        model = self._select_model(policy)

        if not model:
            if policy.fallback_enabled:
                return self._fallback(prompt, max_tokens)
            return None

        return self._call_model(model, prompt, max_tokens)

    def _select_model(self, policy: RoutingPolicy) -> ModelEndpoint | None:
        """Select the best model based on policy."""
        if policy.strategy == RoutingStrategy.COST_FIRST:
            return self._select_cheapest(policy)
        elif policy.strategy == RoutingStrategy.QUALITY_FIRST:
            return self._select_best_quality(policy)
        elif policy.strategy == RoutingStrategy.FASTEST:
            return self._select_fastest(policy)
        else:  # BALANCED or FALLBACK_CHAIN
            return self._select_balanced(policy)

    def _select_cheapest(self, policy: RoutingPolicy) -> ModelEndpoint | None:
        """Select the cheapest available model meeting quality floor."""
        candidates = [
            m
            for m in self._models
            if m.is_free or m.cost_per_1k_input <= policy.max_cost
            if m.quality_score >= policy.min_quality
            if m.avg_latency_ms <= policy.max_latency_ms
            if not policy.blocklisted_providers
            or m.provider not in policy.blocklisted_providers
            if not policy.preferred_providers
            or m.provider in policy.preferred_providers
        ]
        # Check if the model is actually available
        available = self._filter_available(candidates)
        if not available:
            return (
                self._models[-1] if policy.fallback_enabled else None
            )  # openrouter/free
        return min(available, key=lambda m: m.cost_per_1k_input + m.cost_per_1k_output)

    def _select_best_quality(self, policy: RoutingPolicy) -> ModelEndpoint | None:
        """Select the highest quality model within budget."""
        candidates = [
            m
            for m in self._models
            if m.is_free
            or (m.cost_per_1k_input + m.cost_per_1k_output) * 2 <= policy.max_cost
            if m.avg_latency_ms <= policy.max_latency_ms
        ]
        available = self._filter_available(candidates)
        if not available:
            return self._models[-1] if policy.fallback_enabled else None
        return max(available, key=lambda m: m.quality_score)

    def _select_fastest(self, policy: RoutingPolicy) -> ModelEndpoint | None:
        """Select the fastest model meeting quality criteria."""
        candidates = [m for m in self._models if m.quality_score >= policy.min_quality]
        available = self._filter_available(candidates)
        if not available:
            return self._models[-1] if policy.fallback_enabled else None
        return min(available, key=lambda m: m.avg_latency_ms)

    def _select_balanced(self, policy: RoutingPolicy) -> ModelEndpoint | None:
        """Select model balancing cost, quality, and speed."""
        candidates = [
            m
            for m in self._models
            if m.is_free or m.cost_per_1k_input <= policy.max_cost
            if m.quality_score >= policy.min_quality
        ]
        available = self._filter_available(candidates)
        if not available:
            return self._models[-1] if policy.fallback_enabled else None
        # Score: quality * 2 + (1 / latency) * 100 - cost * 50
        scored = [
            (
                m,
                m.quality_score * 2
                + (1.0 / max(m.avg_latency_ms, 1)) * 100
                - m.cost_per_1k_input * 50,
            )
            for m in available
        ]
        return max(scored, key=lambda x: x[1])[0]

    def _filter_available(self, models: list[ModelEndpoint]) -> list[ModelEndpoint]:
        """Filter to models whose providers have API keys configured."""
        result = []
        for m in models:
            # Check if provider is available
            if m.provider == "groq" and os.environ.get("GROQ_API_KEY"):
                result.append(m)
            elif m.provider == "openrouter" and os.environ.get("OPENROUTER_API_KEY"):
                result.append(m)
            elif m.provider == "gemini" and os.environ.get("GEMINI_API_KEY"):
                result.append(m)
            elif m.provider == "openai" and os.environ.get("OPENAI_API_KEY"):
                result.append(m)
            elif m.provider == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
                result.append(m)
            elif m.is_free:
                # Free models via OpenRouter work with just OPENROUTER_API_KEY
                if os.environ.get("OPENROUTER_API_KEY"):
                    result.append(m)
                # Or if it's the universal fallback
                elif m.name == "openrouter/free":
                    result.append(m)
        return result

    def _call_model(
        self, model: ModelEndpoint, prompt: str, max_tokens: int
    ) -> str | None:
        """Call the selected model via LiteLLM or FreeLLM providers."""
        try:
            from litellm import completion

            resp = completion(
                model=model.name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=30,
            )
            if resp and resp.choices:
                return resp.choices[0].message.content
        except Exception:
            pass
        # Fallback to FreeLLM
        return self._fallback(prompt, max_tokens)

    def _fallback(self, prompt: str, max_tokens: int) -> str | None:
        """Ultimate fallback using FreeLLM providers."""
        try:
            from campaign_autopilot.free_llm_providers import generate_text

            return generate_text(prompt, max_tokens=max_tokens)
        except Exception:
            return None

    def get_available_models(self) -> list[dict[str, Any]]:
        """List all models that are currently available."""
        return [
            {
                "name": m.name,
                "provider": m.provider,
                "tier": m.tier.value,
                "quality": m.quality_score,
                "free": m.is_free,
                "tools": m.supports_tools,
                "vision": m.supports_vision,
            }
            for m in self._models
            if self._filter_available([m])
        ]

    def estimate_cost(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for a specific model."""
        for m in self._models:
            if m.name == model_name:
                return m.estimate_cost(input_tokens, output_tokens)
        return 0.0


__all__ = [
    "ModelRouter",
    "ModelEndpoint",
    "RoutingPolicy",
    "RoutingStrategy",
    "ModelTier",
]
