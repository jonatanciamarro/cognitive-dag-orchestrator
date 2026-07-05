"""Manager provider classes and functions."""

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
from .base import ProviderCapability, ProviderMetadata, TextProvider, ImageProvider, AudioProvider, MusicProvider, VideoProvider, CostTracker, QualityRanker, MediaConfig, check_provider
from .text import LiteLLMTextProvider, FreeLLMTextProvider, StdlibFallbackProvider
from .image import PillowImageProvider, FIAPIImageProvider, PollinationsImageProvider, ReplicateImageProvider, DiffusersImageProvider
from .audio import GttsProvider, EdgeTTSProvider
from .music import AlgorithmicMusicProvider, AudioCraftProvider
from .video import MoviePyVideoProvider

class ProviderManager:
    """Orquestrador central de todos os media providers.

    Gerencia descoberta, registro e acesso a provedores de:
    - Texto (LLM)
    - Imagem
    - Audio (TTS)
    - Musica
    - Video

    Uso:
        pm = ProviderManager.get_instance()
        provider = pm.get_best("image")
        img = provider.generate("prompt")
    """

    _instance: "ProviderManager | None" = None

    def __init__(self):
        self.text_providers: list[TextProvider] = []
        self.image_providers: list[ImageProvider] = []
        self.audio_providers: list[AudioProvider] = []
        self.music_providers: list[MusicProvider] = []
        self.video_providers: list[VideoProvider] = []
        self.cost_tracker = CostTracker()
        self.quality_ranker = QualityRanker()
        self._router = None
        self._discover()

    def _discover(self) -> None:
        """Auto-discover all available providers (lazy, no probes during import)."""
        # Text providers - always available
        self.text_providers = [
            LiteLLMTextProvider(),
            FreeLLMTextProvider(),
            StdlibFallbackProvider(),
        ]
        # Image providers - lazily discovered via check_provider
        self.image_providers = _discover_image_providers()
        # Audio providers
        self.audio_providers = _discover_audio_providers()
        # Music providers
        self.music_providers = _discover_music_providers()
        # Video providers
        self.video_providers = _discover_video_providers()

    def get_best(self, provider_type: str):
        """Get the best available provider of a type."""
        providers = self._get_providers(provider_type)
        return providers[0] if providers else None

    def get_all(self, provider_type: str) -> list:
        """Get all providers of a type, ranked by quality."""
        return self._get_providers(provider_type)

    def _get_providers(self, provider_type: str) -> list:
        mapping = {
            "text": self.text_providers,
            "image": self.image_providers,
            "audio": self.audio_providers,
            "music": self.music_providers,
            "video": self.video_providers,
            "tts": self.audio_providers,
        }
        return mapping.get(provider_type, [])

    def get_router(self) -> "MediaRouter":
        """Get or create the MediaRouter."""
        if self._router is None:
            self._router = MediaRouter(self)
        return self._router

    @staticmethod
    def get_instance() -> "ProviderManager":
        if ProviderManager._instance is None:
            ProviderManager._instance = ProviderManager()
        return ProviderManager._instance

    def get_full_report(self) -> dict[str, Any]:
        """Get complete status of all providers."""
        report = {}
        for ptype in ["text", "image", "audio", "music", "video"]:
            providers = self.get_all(ptype)
            report[ptype] = {
                "available": [
                    p.name()
                    for p in providers
                    if getattr(p, "is_available", lambda: True)()
                ],
                "best": self.get_best(ptype).name() if self.get_best(ptype) else None,
                "count": len(providers),
            }
        report["costs"] = self.cost_tracker.get_stats()
        return report
class MediaRouter:
    """Roteador inteligente de midia com auto-failover.

    Caracteristicas:
    - Tenta provedores do melhor para o pior
    - Se um falha, tenta o proximo automaticamente
    - Rastreia custos por provedor
    - Detecta capacidades disponiveis
    - Cache de melhor provedor para cada tipo
    """

    def __init__(self, manager: ProviderManager):
        self.manager = manager
        self._best_cache: dict[str, Any] = {}

    def generate_text(
        self, prompt: str, model: str = "", max_tokens: int = 2048
    ) -> str | None:
        """Generate text with auto-failover across all text providers."""
        providers = self.manager.text_providers

        # Try cached best first
        cached = self._best_cache.get("text")
        if cached:
            try:
                if cached.is_available():
                    result = cached.generate(prompt, model, max_tokens)
                    if result:
                        self.manager.cost_tracker.record_call(cached.name(), 0.0)
                        return result
            except Exception:
                pass

        for provider in providers:
            try:
                if not provider.is_available():
                    continue
                result = provider.generate(prompt, model, max_tokens)
                if result:
                    self._best_cache["text"] = provider
                    self.manager.cost_tracker.record_call(provider.name(), 0.0)
                    return result
            except Exception:
                continue
        return None

    def generate_image(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes | None:
        """Generate image with auto-failover."""
        providers = self.manager.image_providers

        cached = self._best_cache.get("image")
        if cached:
            try:
                result = cached.generate(prompt, width, height, negative_prompt)
                if result and len(result) > 100:
                    self.manager.cost_tracker.record_call(cached.name())
                    return result
            except Exception:
                pass

        for provider in providers:
            try:
                result = provider.generate(prompt, width, height, negative_prompt)
                if result and len(result) > 100:
                    self._best_cache["image"] = provider
                    self.manager.cost_tracker.record_call(provider.name())
                    return result
            except Exception:
                continue
        return None

    def text_to_speech(
        self, text: str, voice: str = "", lang: str = "pt-BR"
    ) -> bytes | None:
        """Generate speech with auto-failover."""
        providers = self.manager.audio_providers

        cached = self._best_cache.get("audio")
        if cached:
            try:
                result = cached.text_to_speech(text, voice, lang)
                if result and len(result) > 100:
                    self.manager.cost_tracker.record_call(cached.name())
                    return result
            except Exception:
                pass

        for provider in providers:
            try:
                result = provider.text_to_speech(text, voice, lang)
                if result and len(result) > 100:
                    self._best_cache["audio"] = provider
                    self.manager.cost_tracker.record_call(provider.name())
                    return result
            except Exception:
                continue
        return None

    def detect_capabilities(self) -> dict[str, list[str]]:
        """Detect all available capabilities across providers."""
        caps = {}
        for ptype in ["text", "image", "audio", "music", "video"]:
            providers = self.manager.get_all(ptype)
            available = []
            for p in providers:
                try:
                    if getattr(p, "is_available", lambda: True)():
                        available.append(p.name())
                except Exception:
                    continue
            caps[ptype] = available
        return caps

    def reset_cache(self) -> None:
        """Clear the best provider cache."""
        self._best_cache.clear()
def _discover_image_providers() -> list:
    """Discover available image providers."""
    result = [PillowImageProvider()]  # Always works
    if check_provider("fiapi"):
        result.insert(0, FIAPIImageProvider())
    if check_provider("pollinations"):
        result.insert(0, PollinationsImageProvider())
    if check_provider("replicate"):
        result.insert(0, ReplicateImageProvider())
    if check_provider("diffusers"):
        result.insert(0, DiffusersImageProvider())
    return result
def _discover_audio_providers() -> list:
    """Discover available audio providers."""
    result = []
    if check_provider("edge_tts"):
        result.append(EdgeTTSProvider())
    if check_provider("gtts"):
        result.append(GttsProvider())
    return result
def _discover_music_providers() -> list:
    """Discover available music providers."""
    result = [AlgorithmicMusicProvider()]  # Always works
    if check_provider("audiocraft"):
        result.insert(0, AudioCraftProvider())
    return result
def _discover_video_providers() -> list:
    """Discover available video providers."""
    result = []
    if check_provider("moviepy"):
        result.append(MoviePyVideoProvider())
    return result
def get_best_image_provider() -> ImageProvider:
    """Returns the best available image provider with caching."""
    return ImageProvider.best()
def get_best_audio_provider() -> AudioProvider:
    """Returns the best available audio provider with caching."""
    return AudioProvider.best()
def get_best_music_provider() -> MusicProvider:
    """Returns the best available music provider with caching."""
    return MusicProvider.best()
def get_best_video_provider() -> VideoProvider:
    """Returns the best available video provider."""
    return VideoProvider.best()
def get_provider_report() -> dict[str, str]:
    """Returns a report of available providers and which is active."""
    return {
        "image": {
            "available": [
                p
                for p in ["pollinations", "replicate", "diffusers", "pillow"]
                if check_provider(p)
            ],
            "active": get_best_image_provider().name(),
        },
        "audio_tts": {
            "available": [p for p in ["edge_tts", "gtts"] if check_provider(p)],
            "active": get_best_audio_provider().name(),
        },
        "music": {
            "available": [
                p for p in ["audiocraft", "algorithmic"] if check_provider(p)
            ],
            "active": get_best_music_provider().name(),
        },
        "video": {
            "available": [p for p in ["moviepy"] if check_provider(p)],
            "active": get_best_video_provider().name(),
        },
    }


__all__ = [
    "ImageProvider",
    "PillowImageProvider",
    "FIAPIImageProvider",
    "PollinationsImageProvider",
    "ReplicateImageProvider",
    "DiffusersImageProvider",
    "AudioProvider",
    "GttsProvider",
    "EdgeTTSProvider",
    "MusicProvider",
    "AlgorithmicMusicProvider",
    "AudioCraftProvider",
    "VideoProvider",
    "MoviePyVideoProvider",
    "get_best_image_provider",
    "get_best_audio_provider",
    "get_best_music_provider",
    "get_best_video_provider",
    "get_provider_report",
    "TextProvider",
    "LiteLLMTextProvider",
    "FreeLLMTextProvider",
    "StdlibFallbackProvider",
    "ProviderManager",
    "MediaRouter",
    "CostTracker",
    "QualityRanker",
    "ProviderCapability",
    "ProviderMetadata",
    "check_provider",
    "MediaConfig",
]
