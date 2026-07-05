"""Audio provider classes and functions."""

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
from .base import AudioProvider

class GttsProvider(AudioProvider):
    """gTTS-based TTS (current implementation)."""

    def name(self) -> str:
        return "gtts"

    def text_to_speech(self, text: str, voice: str = "", lang: str = "pt-BR") -> bytes:
        from gtts import gTTS

        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
class EdgeTTSProvider(AudioProvider):
    """Microsoft Edge neural TTS — high quality, free, no API key needed.

    Uses edge-tts library which taps into Microsoft's neural TTS engine.
    Supports multiple voices, emotions, and languages.
    """

    def name(self) -> str:
        return "edge_tts"

    def text_to_speech(self, text: str, voice: str = "", lang: str = "pt-BR") -> bytes:
        import edge_tts
        import asyncio

        # Voice mapping for Portuguese (Brazil)
        voice_map = {
            "pt-BR": "pt-BR-FranciscaNeural",
            "pt-BR-male": "pt-BR-AntonioNeural",
            "pt-BR-female": "pt-BR-FranciscaNeural",
            "en-US": "en-US-JennyNeural",
            "en-US-male": "en-US-GuyNeural",
            "es": "es-ES-AlvaroNeural",
        }
        voice_id = voice_map.get(voice, voice_map.get(lang, voice_map["pt-BR"]))

        async def _generate() -> bytes:
            communicate = edge_tts.Communicate(text, voice_id)
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            buf.seek(0)
            return buf.read()

        try:
            return asyncio.run(_generate())
        except Exception:
            return GttsProvider().text_to_speech(text, voice, lang)
class KokoroTTSProvider(AudioProvider):
    """Kokoro TTS — modelo TTS leve (~82M params) com qualidade superior.

    Kokoro e um dos melhores TTS open-source em 2026.
    Requer: pip install kokoro misaki[ja] misaki[zh]
    Funciona em CPU, sem GPU necessaria.
    Qualidade comparavel a ElevenLabs e Microsoft Edge TTS.
    """

    def name(self) -> str:
        return "kokoro"

    def text_to_speech(self, text: str, voice: str = "", lang: str = "pt-BR") -> bytes:
        try:
            from kokoro import KPipeline
            import numpy as np
            from scipy.io import wavfile
            import tempfile

            voice_map = {
                "pt-BR": "af_heart",
                "pt-BR-male": "am_mind",
                "pt-BR-female": "af_heart",
                "en-US": "am_mind",
                "en-US-female": "af_bella",
            }
            voice_id = voice_map.get(voice, voice_map.get(lang, voice_map["pt-BR"]))
            pipeline = KPipeline(lang_code="a")

            generator = pipeline(text, voice=voice_id, speed=1.0)
            audio_chunks = []
            for _, (_, _, audio) in enumerate(generator):
                if audio is not None and len(audio) > 0:
                    audio_chunks.append(audio)

            if audio_chunks:
                full_audio = np.concatenate(audio_chunks)
                buf = io.BytesIO()
                wavfile.write(buf, 24000, (full_audio * 32767).astype(np.int16))
                buf.seek(0)
                return buf.read()
        except ImportError:
            pass
        except Exception:
            pass
        return EdgeTTSProvider().text_to_speech(text, voice, lang)
class OpenAITTSSpeechProvider(AudioProvider):
    """TTS via API compativel com OpenAI — usa OPENROUTER_API_KEY.

    Muitos providers no OpenRouter oferecem TTS.
    Tambem compativel com API da OpenAI, Groq, etc.
    """

    def name(self) -> str:
        return "openai_tts"

    def text_to_speech(self, text: str, voice: str = "", lang: str = "pt-BR") -> bytes:
        import urllib.request

        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return EdgeTTSProvider().text_to_speech(text, voice, lang)

        try:
            voice_id = voice or "alloy"
            body = json.dumps(
                {
                    "model": "openai/tts-1",
                    "input": text[:500],
                    "voice": voice_id,
                    "response_format": "wav",
                }
            ).encode()
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/audio/speech",
                data=body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception:
            pass
        return EdgeTTSProvider().text_to_speech(text, voice, lang)
