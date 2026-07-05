"""Music provider classes and functions."""

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
from .base import MusicProvider

class AlgorithmicMusicProvider(MusicProvider):
    """Simple algorithmic background music (current implementation)."""

    def name(self) -> str:
        return "algorithmic"

    def generate_background(
        self,
        style: str = "cinematic",
        duration_seconds: int = 30,
    ) -> bytes:
        """Generate a simple algorithmic background track using pydub."""
        try:
            from pydub import AudioSegment, generators

            sample_rate = 44100

            if style == "cinematic":
                freq = 220
                chord = [261.63, 329.63, 392.00]
            elif style == "upbeat":
                freq = 440
                chord = [523.25, 659.25, 783.99]
            elif style == "ambient":
                freq = 110
                chord = [130.81, 164.81, 196.00]
            else:
                freq = 220
                chord = [261.63, 329.63, 392.00]

            # Generate a simple pad
            track = AudioSegment.silent(duration=0)
            for i in range(duration_seconds):
                tone = generators.Sine(freq + (i % 4) * 10)
                tone = tone.to_audio_segment(duration=1000).apply_gain(
                    -10 - (i % 3) * 2
                )
                track += tone

            # Add chord every 4 beats
            chord_track = AudioSegment.silent(duration=0)
            for i in range(duration_seconds // 4):
                chord_seg = AudioSegment.silent(duration=0)
                for cf in chord:
                    ct = generators.Sine(cf)
                    ct = ct.to_audio_segment(duration=4000).apply_gain(-18)
                    chord_seg = chord_seg.overlay(ct)
                chord_track += chord_seg
            chord_track += AudioSegment.silent(duration=(duration_seconds % 4) * 1000)

            track = track.overlay(chord_track, gain_during_overlay=-3)
            track = track.set_frame_rate(sample_rate).set_channels(2)

            buf = io.BytesIO()
            track.export(buf, format="wav")
            buf.seek(0)
            return buf.read()

        except ImportError:
            # Return silence if pydub not available
            return b""
class AudioCraftProvider(MusicProvider):
    """AI music generation via Meta's AudioCraft/MusicGen."""

    def name(self) -> str:
        return "audiocraft"

    def generate_background(
        self,
        style: str = "cinematic",
        duration_seconds: int = 30,
    ) -> bytes:
        try:
            from audiocraft.models import MusicGen

            model = MusicGen.get_pretrained("facebook/musicgen-small")
            model.set_generation_params(duration=duration_seconds)

            descriptions = {
                "cinematic": "Cinematic orchestral background music, epic and emotional",
                "upbeat": "Upbeat energetic background music for marketing video",
                "ambient": "Ambient atmospheric background music, calm and peaceful",
                "corporate": "Professional corporate background music, modern",
                "lofi": "Lo-fi chill hip hop background beats",
            }
            desc = descriptions.get(style, descriptions["cinematic"])
            wav = model.generate([desc])

            import torchaudio

            buf = io.BytesIO()
            torchaudio.save(buf, wav[0].cpu(), sample_rate=32000, format="wav")
            buf.seek(0)
            return buf.read()

        except Exception:
            return AlgorithmicMusicProvider().generate_background(
                style, duration_seconds
            )
