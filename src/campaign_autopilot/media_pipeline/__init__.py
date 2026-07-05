"""Cinematic Media Pipeline — Image, Video, and Audio production engine.

Provides cinematic-quality multimedia generation using only free tools:
- Pillow for image compositing, filters, effects
- MoviePy for video editing, transitions, effects
- gTTS for text-to-speech narration
- pydub for audio mixing and processing
"""

from .cinematic_engine import (
    CinematicEngine,
    BlendMode,
    ColorGrade,
    LightingEffect,
    Layer,
    Composition,
)

from .image_cinematic import (
    CinematicImageProducer,
    ImageStyle,
    AspectRatio,
)

from .video_cinematic import (
    CinematicVideoProducer,
    TransitionType,
    KenBurnsEffect,
    TextAnimation,
)

from .audio_cinematic import (
    CinematicAudioProducer,
    AudioTrack,
    NarrationStyle,
    BackgroundMusic,
)

# ── Unified Media Providers ────────────────────────────────────────
from ..media_providers import (
    ImageProvider,
    PillowImageProvider,
    ReplicateImageProvider,
    DiffusersImageProvider,
    AudioProvider,
    GttsProvider,
    EdgeTTSProvider,
    MusicProvider,
    AlgorithmicMusicProvider,
    AudioCraftProvider,
    VideoProvider,
    MoviePyVideoProvider,
    get_best_image_provider,
    get_best_audio_provider,
    get_best_music_provider,
    get_best_video_provider,
    get_provider_report,
    check_provider,
)

__all__ = [
    "CinematicEngine",
    "BlendMode",
    "ColorGrade",
    "LightingEffect",
    "Layer",
    "Composition",
    "CinematicImageProducer",
    "ImageStyle",
    "AspectRatio",
    "CinematicVideoProducer",
    "TransitionType",
    "KenBurnsEffect",
    "TextAnimation",
    "CinematicAudioProducer",
    "AudioTrack",
    "NarrationStyle",
    "BackgroundMusic",
    "get_provider_report",
    "check_provider",
    "get_best_image_provider",
]
