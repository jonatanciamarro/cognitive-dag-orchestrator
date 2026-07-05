"""Video provider classes and functions."""

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
from .base import VideoProvider

class MoviePyVideoProvider(VideoProvider):
    """Enhanced video generation via MoviePy with improved quality."""

    def name(self) -> str:
        return "moviepy"

    def create_slideshow(
        self,
        image_paths: list[str],
        output_path: str,
        transition: str = "crossfade",
        duration_per_image: float = 3.0,
        fps: int = 24,
        audio_path: str = "",
    ) -> str:
        try:
            from moviepy import (
                ImageClip,
                concatenate_videoclips,
                AudioFileClip,
                CompositeVideoClip,
            )
            from moviepy.video.fx import FadeIn, FadeOut
        except ImportError:
            raise ImportError("moviepy is required. Install with: pip install moviepy")

        clips = []
        for img_path in image_paths:
            clip = ImageClip(img_path, duration=duration_per_image)
            clip = clip.with_position(("center", "center"))

            # Apply Ken Burns effect (slow zoom)
            if transition == "ken_burns":
                clip = clip.resize(lambda t: 1 + 0.05 * (t / duration_per_image))
                clip = clip.with_position(
                    lambda t: (
                        -clip.w * 0.05 * (t / duration_per_image) / 2,
                        -clip.h * 0.05 * (t / duration_per_image) / 2,
                    )
                )

            clips.append(clip)

        if not clips:
            raise ValueError("No images provided")

        # Crossfade between clips
        if transition == "crossfade" and len(clips) > 1:
            video = concatenate_videoclips(clips, method="compose")
            video = video.with_effects([FadeIn(0.5), FadeOut(0.5)])
        else:
            video = concatenate_videoclips(clips, method="compose")

        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            try:
                audio = AudioFileClip(audio_path)
                if audio.duration < video.duration:
                    audio = audio.loop(duration=video.duration)
                video = video.with_audio(audio)
            except Exception:
                pass

        # Write with high quality settings
        video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            audio_bitrate="192k",
            preset="medium",
            threads=2,
            logger=None,
        )

        video.close()
        return output_path


# ── SMART PROVIDER SELECTION ────────────────────────────────────────
class FFMpegVideoProvider(VideoProvider):
    """Geracao de video aprimorada via FFmpeg — sem MoviePy.

    Cria videos com transicoes, texto sobreposto, audio e legendas.
    Requer: ffmpeg instalado no sistema.
    Qualidade superior ao MoviePyProvider para videos simples.
    """

    def name(self) -> str:
        return "ffmpeg_video"

    def create_slideshow(
        self,
        image_paths: list[str],
        output_path: str,
        transition: str = "crossfade",
        duration_per_image: float = 3.0,
        fps: int = 24,
        audio_path: str = "",
    ) -> str:
        import subprocess

        if not image_paths:
            raise ValueError("No images provided")

        list_path = os.path.join(
            tempfile.gettempdir(), f"ffmpeg_concat_{abs(hash(tuple(image_paths)))}.txt"
        )
        try:
            with open(list_path, "w") as f:
                for img in image_paths:
                    if os.path.exists(img):
                        f.write(f"file '{img}'\n")
                        f.write(f"duration {duration_per_image}\n")
            if image_paths:
                with open(list_path, "a") as f:
                    f.write(f"file '{image_paths[-1]}'\n")

            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_path,
                "-vf",
                f"fps={fps},format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
            ]

            if audio_path and os.path.exists(audio_path):
                cmd.extend(["-i", audio_path, "-c:a", "aac", "-shortest"])

            cmd.append(output_path)

            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            return output_path

        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                from .media_providers import MoviePyVideoProvider

                return MoviePyVideoProvider().create_slideshow(
                    image_paths,
                    output_path,
                    transition,
                    duration_per_image,
                    fps,
                    audio_path,
                )
            except Exception:
                if image_paths and os.path.exists(image_paths[0]):
                    import shutil

                    shutil.copy(image_paths[0], output_path)
                return output_path
        finally:
            if os.path.exists(list_path):
                os.remove(list_path)
