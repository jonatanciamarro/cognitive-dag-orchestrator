"""Media Providers — Unified Provider Layer v2

Arquitetura em camadas:

  ProviderManager (Orquestrador)
  ├── TextProvider (LLM)
  │   ├── LiteLLMTextProvider   ← 100+ modelos, OpenAI compativel
  │   ├── FreeLLMTextProvider    ← 13 provedores gratuitos com failover
  │   └── StdlibFallbackProvider  ← Template engine (stdlib)
  ├── ImageProvider
  │   ├── PollinationsImageProvider ← Gratis, sem chave, IA via URL
  │   ├── ReplicateImageProvider    ← FLUX via Replicate (free tier)
  │   ├── DiffusersImageProvider    ← Local via HuggingFace (GPU)
  │   └── PillowImageProvider       ← Composicao manual (fallback)
  ├── AudioProvider
  │   ├── EdgeTTSProvider          ← Vozes neurais Microsoft (gratis)
  │   └── GttsProvider             ← Google TTS (fallback)
  ├── MusicProvider
  │   ├── AudioCraftProvider       ← MusicGen (local, GPU)
  │   └── AlgorithmicMusicProvider ← Sintese procedural (fallback)
  └── VideoProvider
  │   └── MoviePyVideoProvider     ← Slideshow + transicoes

  MediaRouter
  ├── Auto Failover
  ├── Cost Tracking
  ├── Quality Ranking
  └── Capability Detection
"""

from __future__ import annotations

import io
import os
import json
import tempfile
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote_plus


# ═══════════════════════════════════════════════════════════════════
# PROVIDER CAPABILITY ENUM
# ═══════════════════════════════════════════════════════════════════



class ProviderCapability:
    """Capability flags for media providers."""

    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_TTS = "audio_tts"
    AUDIO_MUSIC = "audio_music"
    VIDEO_SLIDESHOW = "video_slideshow"
    VIDEO_GENERATION = "video_generation"
    STREAMING = "streaming"
    REALTIME = "realtime"
    MULTI_MODAL = "multi_modal"
    FUNCTION_CALLING = "function_calling"
@dataclass
class ProviderMetadata:
    """Metadata for provider selection and ranking."""

    name: str
    display_name: str
    provider_type: str  # "text", "image", "audio", "video", "music"
    capabilities: set[str] = field(default_factory=set)
    quality_rank: int = 0  # Higher = better quality
    cost_per_unit: float = 0.0  # Estimated cost (USD)
    is_free: bool = True
    needs_api_key: bool = False
    needs_gpu: bool = False
    needs_local_server: bool = False
    avg_latency_ms: float = 0.0
    supported_languages: list[str] = field(default_factory=list)
    max_resolution: tuple[int, int] = (0, 0)
    failover_priority: int = 999  # Lower = tried first
class TextProvider(ABC):
    """Abstract base for text/LLM generation providers."""

    @abstractmethod
    def generate(
        self, prompt: str, model: str = "", max_tokens: int = 2048
    ) -> str | None:
        """Generate text from a prompt."""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        raise NotImplementedError

    def is_available(self) -> bool:
        return True

    @staticmethod
    def best() -> "TextProvider":
        """Returns the best available text provider."""
        litellm = LiteLLMTextProvider()
        if litellm.is_available():
            return litellm
        free_llm = FreeLLMTextProvider()
        if free_llm.is_available():
            return free_llm
        return StdlibFallbackProvider()
class ImageProvider(ABC):
    """Abstract base for image generation providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        """Generate an image from a text prompt. Returns PNG bytes."""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @staticmethod
    def best() -> "ImageProvider":
        """Returns the best available image provider."""
        if check_provider("fiapi"):
            return FIAPIImageProvider()
        if check_provider("pollinations"):
            return PollinationsImageProvider()
        if check_provider("replicate"):
            return ReplicateImageProvider()
        if check_provider("diffusers"):
            return DiffusersImageProvider()
        return PillowImageProvider()
class AudioProvider(ABC):
    """Abstract base for audio generation providers."""

    @abstractmethod
    def text_to_speech(self, text: str, voice: str = "", lang: str = "pt-BR") -> bytes:
        """Convert text to speech audio. Returns WAV bytes."""
        raise NotImplementedError

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @staticmethod
    def best() -> "AudioProvider":
        if check_provider("edge_tts"):
            return EdgeTTSProvider()
        return GttsProvider()
class MusicProvider(ABC):
    """Abstract base for music/background generation."""

    @abstractmethod
    def generate_background(
        self,
        style: str = "cinematic",
        duration_seconds: int = 30,
    ) -> bytes:
        raise NotImplementedError

    @staticmethod
    def best() -> "MusicProvider":
        if check_provider("audiocraft"):
            return AudioCraftProvider()
        return AlgorithmicMusicProvider()
class VideoProvider(ABC):
    """Abstract base for video generation providers."""

    @abstractmethod
    def create_slideshow(
        self,
        image_paths: list[str],
        output_path: str,
        transition: str = "crossfade",
        duration_per_image: float = 3.0,
        fps: int = 24,
        audio_path: str = "",
    ) -> str:
        """Create a video slideshow from images. Returns output path."""
        raise NotImplementedError

    @staticmethod
    def best() -> "VideoProvider":
        return MoviePyVideoProvider()
class CostTracker:
    """Track usage costs across all providers."""

    def __init__(self):
        self._usage: dict[str, int] = {}
        self._costs: dict[str, float] = {}

    def record_call(self, provider_name: str, estimated_cost: float = 0.0) -> None:
        self._usage[provider_name] = self._usage.get(provider_name, 0) + 1
        self._costs[provider_name] = (
            self._costs.get(provider_name, 0.0) + estimated_cost
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_calls": sum(self._usage.values()),
            "total_cost": sum(self._costs.values()),
            "by_provider": {
                k: {"calls": self._usage.get(k, 0), "cost": self._costs.get(k, 0.0)}
                for k in set(list(self._usage.keys()) + list(self._costs.keys()))
            },
        }

    def reset(self) -> None:
        self._usage.clear()
        self._costs.clear()
class QualityRanker:
    """Ranks providers by quality for each capability."""

    def rank_providers(self, providers: list, capability: str) -> list:
        """Sort providers by quality rank descending for given capability."""
        scored = []
        for p in providers:
            meta = getattr(p, "metadata", lambda: None)()
            if meta and capability in meta.capabilities:
                scored.append((meta.quality_rank, meta.is_free, p))
            elif hasattr(p, "name") and capability in getattr(p, "capabilities", set()):
                scored.append((0, True, p))
        scored.sort(key=lambda x: (-x[0], not x[1]))
        return [p for _, _, p in scored]


# ═══════════════════════════════════════════════════════════════════
# PROVIDER MANAGER
# ═══════════════════════════════════════════════════════════════════
@dataclass
class MediaConfig:
    """Global configuration for media providers."""

    output_dir: str = "output"
    replicate_api_key: str = ""
    hf_token: str = ""
    default_image_width: int = 1200
    default_image_height: int = 630
    default_video_fps: int = 24
    default_audio_sample_rate: int = 44100


# ── Provider Status ────────────────────────────────────────────────

_PROVIDER_STATUS: dict[str, bool] = {}
def check_provider(name: str) -> bool:
    """Check if a provider is available (cached)."""
    if name not in _PROVIDER_STATUS:
        _PROVIDER_STATUS[name] = _probe_provider(name)
    return _PROVIDER_STATUS[name]
def _probe_provider(name: str) -> bool:
    if name == "pillow":
        try:
            from PIL import Image

            return True
        except ImportError:
            return False
    elif name == "moviepy":
        try:
            from importlib.metadata import version

            version("moviepy")
            return True
        except (ImportError, Exception):
            return False
    elif name == "gtts":
        try:
            from importlib.metadata import version

            version("gtts")
            return True
        except (ImportError, Exception):
            return False
    elif name == "pydub":
        try:
            from importlib.metadata import version

            version("pydub")
            return True
        except (ImportError, Exception):
            return False
    elif name == "edge_tts":
        try:
            # Use importlib.metadata instead of actual import (faster)
            from importlib.metadata import version

            version("edge-tts")
            return True
        except (ImportError, Exception):
            return False
    elif name == "replicate":
        try:
            from importlib.metadata import version

            version("replicate")
            return bool(os.environ.get("REPLICATE_API_KEY"))
        except (ImportError, Exception):
            return False
    elif name == "diffusers":
        try:
            from importlib.metadata import version

            version("torch")
            version("diffusers")
            return True
        except (ImportError, Exception):
            return False
    elif name == "audiocraft":
        try:
            from importlib.metadata import version

            version("audiocraft")
            return True
        except (ImportError, Exception):
            return False
    elif name == "ffmpeg":
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    elif name == "pollinations":
        # Pollinations.AI is a free HTTP API - no deps to install.
        return True
    elif name == "fiapi":
        # FIAPI is available if we configure it.
        return True
    return False
