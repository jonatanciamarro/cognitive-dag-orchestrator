"""MoneyPrinterTurbo Integration Layer — edge-tts, Pexels video B-roll, and stylized subtitle burning.

This module provides the core features of MoneyPrinterTurbo:
1. EdgeTTS Integration — realistic neural voice synthesis (pt-BR and en-US).
2. Pexels Video search and downloader.
3. Subtitle generator & builder using Pillow transparency layers (cross-platform, zero ImageMagick dependency).
4. TurboVideoProducer to generate shorts and landscape videos with background footage and burned subtitles.
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import random
import re
import tempfile
from pathlib import Path
from typing import Any, Tuple

import requests
from PIL import Image, ImageDraw, ImageFont

from .cinematic_engine import _hex_to_rgb
from ..media_providers import get_best_image_provider

# Check for MoviePy
HAS_MOVIEPY = False
try:
    from moviepy import (
        ImageClip,
        VideoClip,
        VideoFileClip,
        concatenate_videoclips,
        CompositeVideoClip,
        AudioFileClip,
    )
    HAS_MOVIEPY = True
except ImportError:
    try:
        from moviepy.editor import *
        HAS_MOVIEPY = True
    except ImportError:
        pass


class EdgeTTSSynthesizer:
    """Generates highly realistic voice narration using Microsoft Edge TTS (free neural voices)."""

    DEFAULT_VOICES = {
        "pt": "pt-BR-AntonioNeural",
        "en": "en-US-GuyNeural",
        "es": "es-ES-AlvaroNeural",
    }

    @staticmethod
    def run_async(coro):
        """Runs an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    @classmethod
    def synthesize(
        cls,
        text: str,
        output_audio_path: str | Path,
        lang: str = "pt",
        voice: str | None = None,
    ) -> dict[str, Any]:
        """Synthesize text to audio file and return timings for subtitles."""
        if not voice:
            voice = cls.DEFAULT_VOICES.get(lang, "pt-BR-AntonioNeural")

        output_audio_path = Path(output_audio_path)
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)

        return cls.run_async(cls._synthesize_async(text, output_audio_path, voice))

    @staticmethod
    async def _synthesize_async(text: str, output_path: Path, voice: str) -> dict[str, Any]:
        import edge_tts

        communicate = edge_tts.Communicate(text, voice)
        timings = []

        with output_path.open("wb") as fp:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    fp.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    offset_sec = chunk["offset"] / 10000000.0
                    duration_sec = chunk["duration"] / 10000000.0
                    timings.append({
                        "text": chunk["text"],
                        "start": offset_sec,
                        "end": offset_sec + duration_sec,
                    })

        return {
            "status": "success",
            "path": str(output_path),
            "voice": voice,
            "timings": timings,
        }


class PexelsDownloader:
    """Searches and downloads free background video footage from Pexels."""

    @staticmethod
    def search_and_download(
        query: str,
        output_dir: str | Path,
        max_duration: float = 15.0,
        orientation: str = "portrait",
    ) -> Path | None:
        """Search Pexels for a B-roll video clip and download it.

        Fallback: returns None if no PEXELS_API_KEY is configured.
        """
        api_key = os.getenv("PEXELS_API_KEY")
        if not api_key:
            return None

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation={orientation}"
        headers = {"Authorization": api_key}

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return None
            data = resp.json()
            videos = data.get("videos", [])
            if not videos:
                return None

            # Find a video with reasonable resolution and duration
            video = random.choice(videos)
            video_files = video.get("video_files", [])
            
            # Select mp4 files
            mp4_files = [f for f in video_files if f.get("file_type") == "video/mp4"]
            if not mp4_files:
                return None

            # Sort by width/quality, choose a medium one
            mp4_files.sort(key=lambda x: x.get("width", 0))
            selected_file = mp4_files[min(len(mp4_files) - 1, 1)] # preferred middle resolution
            video_url = selected_file.get("link")

            if not video_url:
                return None

            filename = f"pexels_{query.replace(' ', '_')}_{video.get('id')}.mp4"
            target_path = output_dir / filename

            # Download
            v_resp = requests.get(video_url, stream=True, timeout=15)
            if v_resp.status_code == 200:
                with target_path.open("wb") as f:
                    for chunk in v_resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                return target_path

        except Exception:
            pass

        return None


class SubtitleBurner:
    """Helper to burn stylized subtitles on top of video frames using Pillow transparent clips."""

    @staticmethod
    def draw_subtitle_image(
        text: str,
        size: Tuple[int, int],
        font_size: int = 40,
        text_color: str = "#ffff00", # Yellow
        stroke_color: str = "#000000",
        stroke_width: int = 3,
    ) -> Image.Image:
        """Create transparent overlay containing centered subtitle text."""
        w, h = size
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Try to load a font, otherwise use default
        font = None
        for name in ["calibri.ttf", "arial.ttf", "Impact.ttf", "cool.ttf"]:
            try:
                font = ImageFont.truetype(name, font_size)
                break
            except Exception:
                pass
        if not font:
            font = ImageFont.load_default()

        # Word wrap text if too long
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            # Rough estimation of text width
            if len(test_line) * (font_size * 0.5) > (w - 100):
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))

        # Draw lines centered near bottom
        y_offset = int(h * 0.75) # Subtitles at 75% height
        rgb_color = _hex_to_rgb(text_color)
        stroke_rgb = _hex_to_rgb(stroke_color)

        for line in lines:
            # Center of screen
            # Pillow 10+ text length calculation
            try:
                left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
                text_w = right - left
                text_h = bottom - top
            except Exception:
                text_w = len(line) * (font_size * 0.5)
                text_h = font_size

            x_pos = (w - text_w) // 2
            draw.text(
                (x_pos, y_offset),
                line,
                fill=rgb_color,
                font=font,
                stroke_fill=stroke_rgb,
                stroke_width=stroke_width,
            )
            y_offset += text_h + 10

        return img


class TurboVideoProducer:
    """Combines B-roll, realistic audio, and burned subtitles to create viral-style short videos."""

    def __init__(self, output_dir: str | Path = "output/videos") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path(tempfile.mkdtemp())

    def produce_viral_short(
        self,
        script_text: str,
        niche: str,
        keyword: str,
        voice: str = "pt-BR-AntonioNeural",
        music_path: str | None = None,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generates a complete dynamic short video (9:16)."""
        if not HAS_MOVIEPY:
            return {"status": "error", "error": "MoviePy is required"}

        size = (720, 1280) # vertical TikTok size

        # ── 1. Voice Narration & Subtitle Timings ────────────────────
        audio_filename = f"narration_{random.randint(1000, 9999)}.mp3"
        audio_path = self.temp_dir / audio_filename
        tts_result = EdgeTTSSynthesizer.synthesize(script_text, audio_path, voice=voice)
        timings = tts_result["timings"]

        # If no voice timings generated, create dummy timings
        if not timings:
            return {"status": "error", "error": "TTS narration synthesis failed"}

        total_duration = timings[-1]["end"]

        # ── 2. Background Video Footages ─────────────────────────────
        # Split script into keywords to download B-roll clip
        words_cleaned = re.sub(r'[^\w\s]', '', script_text).lower().split()
        search_terms = [w for w in words_cleaned if len(w) > 4][:3]
        if not search_terms:
            search_terms = [niche, "abstract"]

        bg_clips = []
        time_covered = 0.0

        for term in search_terms:
            if time_covered >= total_duration:
                break
            # Try to search and download a video clip
            video_file = PexelsDownloader.search_and_download(term, self.temp_dir, orientation="portrait")
            if video_file and video_file.exists():
                try:
                    clip = VideoFileClip(str(video_file))
                    # Mute the original clip audio
                    clip = clip.without_audio()
                    # Scale to fit
                    clip = clip.resize(height=size[1]).crop(x_center=clip.w/2, width=size[0])
                    
                    clip_duration = min(clip.duration, total_duration - time_covered)
                    clip = clip.subclip(0, clip_duration)
                    bg_clips.append(clip.with_start(time_covered))
                    time_covered += clip_duration
                except Exception:
                    pass

        # Fallback to AI images or solid gradients if not enough video clips
        if time_covered < total_duration:
            rem_duration = total_duration - time_covered
            try:
                from .cinematic_engine import CinematicEngine
                palette = {"bg": ["#0a0a0a", "#1a1a2e"]}
                bg_img = CinematicEngine.generate_cinematic_background(size, palette["bg"], style="radial")
                tmp_img = self.temp_dir / f"fallback_{random.randint(1000, 9999)}.png"
                bg_img.save(str(tmp_img))
                
                img_clip = ImageClip(str(tmp_img)).with_duration(rem_duration).with_start(time_covered)
                bg_clips.append(img_clip)
                time_covered += rem_duration
            except Exception:
                # Basic black fallback
                pass

        if not bg_clips:
            return {"status": "error", "error": "Failed to generate video background track"}

        bg_track = CompositeVideoClip(bg_clips, size=size)

        # ── 3. Subtitles Overlays ────────────────────────────────────
        subtitle_clips = []
        for item in timings:
            phrase_text = item["text"]
            phrase_start = item["start"]
            phrase_end = item["end"]
            sub_duration = phrase_end - phrase_start
            if sub_duration > 0.1:
                # Draw overlay PIL image
                sub_img = SubtitleBurner.draw_subtitle_image(
                    phrase_text,
                    size,
                    font_size=42,
                    text_color="#ffff00" # Yellow
                )
                sub_tmp = self.temp_dir / f"sub_{phrase_start:.2f}.png"
                sub_img.save(str(sub_tmp), "PNG")
                
                sub_clip = (ImageClip(str(sub_tmp))
                            .with_start(phrase_start)
                            .with_duration(sub_duration))
                subtitle_clips.append(sub_clip)

        # ── 4. Assembly & Audio Track ────────────────────────────────
        audio_clip = AudioFileClip(str(audio_path))
        
        # Combine music if supplied
        if music_path and os.path.exists(music_path):
            try:
                bg_music = AudioFileClip(music_path).with_volume_scaled(0.15) # 15% volume
                # Loop background music if shorter
                bg_music = bg_music.loop(duration=total_duration)
                from moviepy.audio.AudioClip import CompositeAudioClip
                audio_clip = CompositeAudioClip([audio_clip, bg_music])
            except Exception:
                pass

        final_clip = CompositeVideoClip([bg_track] + subtitle_clips, size=size)
        final_clip = final_clip.with_audio(audio_clip).with_duration(total_duration)

        # Output path
        if not filename:
            filename = f"viral_short_{keyword[:15].replace(' ', '_')}_{random.randint(1000, 9999)}.mp4"
        
        output_path = self.output_dir / filename

        # Write file
        final_clip.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            remove_temp=True,
            logger=None
        )

        # Cleanup clips to release resources
        try:
            final_clip.close()
            audio_clip.close()
            for c in bg_clips:
                c.close()
        except Exception:
            pass

        return {
            "status": "success",
            "path": str(output_path),
            "filename": filename,
            "duration": round(total_duration, 2),
            "voice": voice,
            "bg_sources": len(bg_clips),
            "pexels_used": len(bg_clips) - 1 if time_covered > 0 else 0,
            "width": size[0],
            "height": size[1],
        }
