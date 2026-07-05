"""Cinematic Audio Producer — audio production pipeline using free tools.

Features:
- Text-to-speech narration via gTTS (free, no API key)
- Background music generation (algorithmic/loops, no API)
- Audio mixing and mastering
- Volume normalization and dynamics
- Crossfade transitions between audio segments
- Multi-track composition (narration + music + sound effects)
- Support for video synchronization

All using free tools: gTTS + pydub + numpy (no paid APIs)
"""

from __future__ import annotations

import os
import random
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore
    HAS_NUMPY = False

HAS_GTTS = False
HAS_PYDUB = False

try:
    from gtts import gTTS
    from gtts.tts import gTTSError

    HAS_GTTS = True
except ImportError:
    pass

try:
    from pydub import AudioSegment, generators
    from pydub.effects import normalize, compress_dynamic_range

    HAS_PYDUB = True
except ImportError:
    pass


class NarrationStyle(Enum):
    """TTS narration styles."""

    NATURAL = "natural"  # Default speed
    SLOW = "slow"  # Slower, more deliberate
    FAST = "fast"  # Faster pace
    FORMAL = "formal"  # More formal, clear enunciation
    CASUAL = "casual"  # Conversational tone


class BackgroundMusic(Enum):
    """Background music types (algorithmically generated)."""

    NONE = "none"
    CINEMATIC = "cinematic"  # Epic orchestral-style
    LO_FI = "lo_fi"  # Relaxed lo-fi beats
    AMBIENT = "ambient"  # Atmospheric pads
    CORPORATE = "corporate"  # Upbeat corporate
    INSPIRATIONAL = "inspirational"  # Uplifting
    TECH = "tech"  # Modern/tech style
    CALM = "calm"  # Soft piano/strings


# ── Audio Tracks ─────────────────────────────────────────────────


class AudioTrack:
    """An audio track with processing capabilities."""

    def __init__(
        self,
        audio: "AudioSegment | None" = None,
        path: str | Path | None = None,
        volume_db: float = 0.0,
        fade_in_ms: int = 0,
        fade_out_ms: int = 0,
    ):
        if path is not None:
            path = str(path)
            if path.endswith(".mp3"):
                self.audio = AudioSegment.from_mp3(path)
            elif path.endswith(".wav"):
                self.audio = AudioSegment.from_wav(path)
            elif path.endswith(".ogg"):
                self.audio = AudioSegment.from_ogg(path)
            else:
                self.audio = AudioSegment.from_file(path)
        elif audio is not None:
            self.audio = audio
        else:
            self.audio = AudioSegment.silent(duration=1000)
        self.volume_db = volume_db
        self.fade_in_ms = fade_in_ms
        self.fade_out_ms = fade_out_ms

    def apply_effects(self) -> "AudioSegment":
        """Apply volume and fade effects."""
        audio = self.audio
        if self.volume_db != 0:
            audio = audio + self.volume_db
        if self.fade_in_ms > 0:
            audio = audio.fade_in(self.fade_in_ms)
        if self.fade_out_ms > 0:
            audio = audio.fade_out(self.fade_out_ms)
        return audio


# ── Cinematic Audio Producer ─────────────────────────────────────


class CinematicAudioProducer:
    """Cinematic audio production using free tools.

    Capabilities:
    - TTS narration in Portuguese (gTTS, no API key)
    - Algorithmic background music generation
    - Multi-track mixing
    - Audio mastering (normalize, compress)
    - Export to MP3, WAV, or OGG
    """

    def __init__(self, output_dir: str = "output/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_narration(
        self,
        text: str,
        lang: str = "pt-BR",
        style: NarrationStyle = NarrationStyle.NATURAL,
        slow: bool = False,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate narration audio from text using gTTS (free).

        Args:
            text: Text to narrate
            lang: Language code (pt-BR, en, es, etc.)
            style: Narration style
            slow: Whether to use slow speech
            filename: Output filename
        """
        if not HAS_GTTS:
            return {
                "status": "error",
                "error": "gTTS not installed. Run: pip install gtts",
                "fallback": True,
                "message": "Instalação recomendada: pip install gtts",
            }

        try:
            # gTTS doesn't have style control, so we use slow parameter
            # and post-process for style effects
            tts = gTTS(text=text, lang=lang, slow=slow)
            filename = filename or f"narration_{random.randint(1000, 9999)}.mp3"
            path = self.output_dir / filename
            tts.save(str(path))

            duration_sec = 0
            if HAS_PYDUB:
                audio = AudioSegment.from_mp3(str(path))
                duration_sec = len(audio) / 1000.0

                # Apply style-based processing
                if style == NarrationStyle.FAST and duration_sec > 5:
                    # Speed up by 15%
                    fast_audio = audio.speedup(playback_speed=1.15)
                    fast_audio.export(str(path), format="mp3")
                    duration_sec = len(fast_audio) / 1000.0
                elif style == NarrationStyle.FORMAL:
                    # Slight compression for clarity
                    compressed = compress_dynamic_range(audio)
                    compressed.export(str(path), format="mp3")

            return {
                "status": "success",
                "filename": filename,
                "path": str(path),
                "duration_sec": round(duration_sec, 1),
                "text_length": len(text),
                "lang": lang,
                "style": style.value,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": True,
                "message": "Erro ao gerar narração com gTTS. Verifique conexão com internet.",
            }

    def generate_background_music(
        self,
        duration_sec: float = 30.0,
        style: BackgroundMusic = BackgroundMusic.AMBIENT,
        tempo_bpm: int = 80,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate background music algorithmically using pydub.

        Creates simple but pleasant background music using
        algorithmic audio generation (no APIs, no samples).
        """
        if not HAS_PYDUB:
            return {
                "status": "error",
                "error": "pydub not installed. Run: pip install pydub",
                "fallback": True,
            }

        try:
            duration_ms = int(duration_sec * 1000)
            sample_rate = 44100

            if style == BackgroundMusic.AMBIENT:
                audio = self._generate_ambient_pad(duration_ms, sample_rate)
            elif style == BackgroundMusic.LO_FI:
                audio = self._generate_lo_fi(duration_ms, sample_rate, tempo_bpm)
            elif style == BackgroundMusic.CINEMATIC:
                audio = self._generate_cinematic_drone(duration_ms, sample_rate)
            elif style == BackgroundMusic.CORPORATE:
                audio = self._generate_corporate(duration_ms, sample_rate, tempo_bpm)
            elif style == BackgroundMusic.INSPIRATIONAL:
                audio = self._generate_inspirational(
                    duration_ms, sample_rate, tempo_bpm
                )
            elif style == BackgroundMusic.TECH:
                audio = self._generate_tech(duration_ms, sample_rate, tempo_bpm)
            elif style == BackgroundMusic.CALM:
                audio = self._generate_calm_piano(duration_ms, sample_rate)
            else:
                audio = AudioSegment.silent(duration=duration_ms)

            # Normalize volume
            audio = normalize(audio)

            # Fade in/out
            fade = min(duration_ms // 4, 3000)
            audio = audio.fade_in(fade).fade_out(fade)

            filename = filename or f"bg_{style.value}_{random.randint(1000, 9999)}.mp3"
            path = self.output_dir / filename
            audio.export(str(path), format="mp3", bitrate="192k")

            return {
                "status": "success",
                "filename": filename,
                "path": str(path),
                "duration_sec": round(len(audio) / 1000, 1),
                "style": style.value,
                "tempo_bpm": tempo_bpm,
                "format": "mp3",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": True,
            }

    def mix_audio_tracks(
        self,
        tracks: list[dict[str, Any]],
        filename: str | None = None,
        normalize_output: bool = True,
    ) -> dict[str, Any]:
        """Mix multiple audio tracks together.

        Args:
            tracks: List of track configs:
                [{"path": "narration.mp3", "volume_db": 0, "start_ms": 0},
                 {"path": "bg_music.mp3", "volume_db": -6, "start_ms": 0, "loop": True}]
            filename: Output filename
            normalize_output: Whether to normalize the final mix
        """
        if not HAS_PYDUB:
            return {"status": "error", "error": "pydub not installed"}

        try:
            mixed = AudioSegment.silent(duration=100)
            for track in tracks:
                path = track.get("path", "")
                if not os.path.exists(path):
                    continue
                audio = AudioSegment.from_file(path)
                vol = track.get("volume_db", 0)
                start = track.get("start_ms", 0)
                loop = track.get("loop", False)
                duration = track.get("duration_ms", 0)

                if vol != 0:
                    audio = audio + vol
                if loop:
                    # Loop to fill duration
                    target_dur = duration if duration > 0 else len(mixed) + 30000
                    loops_needed = max(1, int(target_dur / len(audio)) + 1)
                    audio = audio * loops_needed

                # Pad or trim to fit
                end_pos = start + len(audio)
                if end_pos > len(mixed):
                    # Extend silent track
                    mixed = mixed + AudioSegment.silent(duration=end_pos - len(mixed))

                # Overlay
                mixed = mixed.overlay(audio, position=start)

            if normalize_output:
                mixed = normalize(mixed)

            # Fade out
            fade = min(len(mixed) // 10, 3000)
            mixed = mixed.fade_out(fade)

            filename = filename or f"mix_{random.randint(1000, 9999)}.mp3"
            path = self.output_dir / filename
            mixed.export(str(path), format="mp3", bitrate="192k")

            return {
                "status": "success",
                "filename": filename,
                "path": str(path),
                "duration_sec": round(len(mixed) / 1000, 1),
                "tracks": len(tracks),
                "format": "mp3",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def produce_full_audio_track(
        self,
        script_text: str,
        niche: str,
        bg_style: BackgroundMusic = BackgroundMusic.AMBIENT,
        narration_lang: str = "pt-BR",
        bg_volume_db: float = -8.0,
        voice_volume_db: float = 0.0,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Produce a complete audio track: narration + background music.

        One-shot function for the full pipeline.
        """
        # 1. Generate narration
        narration = self.generate_narration(
            text=script_text,
            lang=narration_lang,
            style=NarrationStyle.NATURAL,
        )
        if narration.get("status") != "success":
            return narration

        # 2. Generate background music
        narration_dur = narration.get("duration_sec", 30)
        music = self.generate_background_music(
            duration_sec=narration_dur + 2.0,  # Add padding
            style=bg_style,
        )
        if music.get("status") != "success":
            music = {"status": "fallback", "message": "No background music"}

        # 3. Mix
        tracks = [
            {"path": narration["path"], "volume_db": voice_volume_db, "start_ms": 0},
        ]
        if music.get("status") == "success":
            tracks.append(
                {
                    "path": music["path"],
                    "volume_db": bg_volume_db,
                    "start_ms": 0,
                    "loop": True,
                    "duration_ms": int(narration_dur * 1000),
                }
            )

        mix = self.mix_audio_tracks(
            tracks, filename=filename or f"full_audio_{random.randint(1000, 9999)}.mp3"
        )
        if mix.get("status") == "success":
            mix["narration"] = narration
            mix["background_music"] = music

        return mix

    # ── Algorithmic Music Generators ───────────────────────────

    def _generate_ambient_pad(self, duration_ms: int, sr: int) -> "AudioSegment":
        """Generate ambient pad sounds using additive synthesis."""
        segments = []
        # Multiple detuned sine waves for rich pad
        freqs = [110, 220, 330, 440, 550]
        for freq in freqs:
            detune = random.uniform(-1.5, 1.5)
            vol = random.uniform(-12, -6)
            tone = generators.Sine(freq + detune).to_audio_segment(
                duration=duration_ms, volume=vol
            )
            # Low pass filter for softness
            tone = tone.low_pass_filter(800)
            segments.append(tone)

        # Mix
        mixed = segments[0]
        for seg in segments[1:]:
            mixed = mixed.overlay(seg)
        return mixed

    def _generate_lo_fi(self, duration_ms: int, sr: int, bpm: int) -> "AudioSegment":
        """Generate lo-fi beat."""
        beat_dur = 60000 // bpm
        bars = duration_ms // beat_dur + 1

        # Kick drum
        kick = generators.Sine(60).to_audio_segment(duration=beat_dur // 2, volume=-3)
        kick = kick.low_pass_filter(150)

        # Hi-hat
        hat = generators.WhiteNoise().to_audio_segment(
            duration=beat_dur // 4, volume=-15
        )
        hat = hat.high_pass_filter(8000)

        # Simple chord pad
        chord = generators.Sine(261).to_audio_segment(duration=beat_dur, volume=-12)
        chord = chord.low_pass_filter(400)

        result = AudioSegment.silent(duration=0)
        for i in range(bars):
            # Beat pattern: kick on 1 and 3, hat on off-beats
            bar = AudioSegment.silent(duration=beat_dur * 4)
            bar = bar.overlay(kick, position=0)
            bar = bar.overlay(kick, position=beat_dur * 2)
            bar = bar.overlay(hat, position=beat_dur // 2)
            bar = bar.overlay(hat, position=beat_dur // 2 * 3)
            bar = bar.overlay(hat, position=beat_dur * 2 + beat_dur // 2)
            bar = bar.overlay(hat, position=beat_dur * 3 + beat_dur // 2)
            bar = bar.overlay(chord, position=0)
            result = result + bar

        return result[:duration_ms]

    def _generate_cinematic_drone(self, duration_ms: int, sr: int) -> "AudioSegment":
        """Generate cinematic drone (epic sustained notes)."""
        segments = []
        # Deep bass drone
        bass = generators.Sine(55).to_audio_segment(duration=duration_ms, volume=-3)
        bass = bass.low_pass_filter(200)
        segments.append(bass)

        # Mid harmony
        mid = generators.Sine(110).to_audio_segment(duration=duration_ms, volume=-9)
        segments.append(mid)

        # High strings-like
        high = generators.Sine(220).to_audio_segment(duration=duration_ms, volume=-15)
        high = high.low_pass_filter(1000)
        segments.append(high)

        mixed = segments[0]
        for seg in segments[1:]:
            mixed = mixed.overlay(seg)
        return mixed

    def _generate_corporate(
        self, duration_ms: int, sr: int, bpm: int
    ) -> "AudioSegment":
        """Generate upbeat corporate background."""
        beat_dur = 60000 // bpm
        bars = duration_ms // beat_dur + 1

        kick = generators.Sine(80).to_audio_segment(duration=beat_dur // 2, volume=-3)
        kick = kick.low_pass_filter(100)

        clap = generators.WhiteNoise().to_audio_segment(
            duration=beat_dur // 3, volume=-10
        )
        clap = clap.high_pass_filter(2000)

        result = AudioSegment.silent(duration=0)
        for i in range(bars):
            bar = AudioSegment.silent(duration=beat_dur * 4)
            bar = bar.overlay(kick, position=0)
            bar = bar.overlay(kick, position=beat_dur * 2)
            bar = bar.overlay(clap, position=beat_dur * 1)
            bar = bar.overlay(clap, position=beat_dur * 3)
            result = result + bar

        return result[:duration_ms]

    def _generate_inspirational(
        self, duration_ms: int, sr: int, bpm: int
    ) -> "AudioSegment":
        """Generate inspirational/uplifting background."""
        beat_dur = 60000 // bpm
        bars = duration_ms // beat_dur + 1

        # Piano-like melody (simple arpeggio)
        notes = [261, 329, 392, 523]  # C4, E4, G4, C5
        melody = AudioSegment.silent(duration=0)
        for i in range(bars * 4):
            note_freq = notes[i % len(notes)]
            note = generators.Sine(note_freq).to_audio_segment(
                duration=beat_dur, volume=-12
            )
            note = note.low_pass_filter(500)
            melody = melody + note

        # Pad underneath
        pad = generators.Sine(130).to_audio_segment(
            duration=melody.duration_seconds * 1000, volume=-18
        )
        pad = pad.low_pass_filter(300)

        result = melody.overlay(pad)
        return result[:duration_ms]

    def _generate_tech(self, duration_ms: int, sr: int, bpm: int) -> "AudioSegment":
        """Generate modern/tech background."""
        beat_dur = 60000 // bpm
        bars = duration_ms // beat_dur + 1

        kick = generators.Sine(100).to_audio_segment(duration=beat_dur // 2, volume=-3)
        kick = kick.low_pass_filter(80)

        snare = generators.WhiteNoise().to_audio_segment(
            duration=beat_dur // 2, volume=-12
        )
        snare = snare.high_pass_filter(3000)

        result = AudioSegment.silent(duration=0)
        for i in range(bars):
            bar = AudioSegment.silent(duration=beat_dur * 4)
            bar = bar.overlay(kick, position=0)
            bar = bar.overlay(kick, position=beat_dur * 2)
            bar = bar.overlay(snare, position=beat_dur * 1)
            bar = bar.overlay(snare, position=beat_dur * 3)
            result = result + bar

        return result[:duration_ms]

    def _generate_calm_piano(self, duration_ms: int, sr: int) -> "AudioSegment":
        """Generate calm piano-like background."""
        # Slow sine waves with soft envelopes
        chords = [
            [261, 329, 392],  # C major
            [293, 349, 440],  # D minor
            [329, 392, 493],  # E minor
            [349, 440, 523],  # F major
        ]
        chord_dur = duration_ms // len(chords)
        result = AudioSegment.silent(duration=0)
        for chord_freqs in chords:
            chord = AudioSegment.silent(duration=0)
            for freq in chord_freqs:
                tone = generators.Sine(freq).to_audio_segment(
                    duration=chord_dur, volume=-15
                )
                tone = tone.low_pass_filter(400).fade_in(200).fade_out(2000)
                chord = chord.overlay(tone)
            result = result + chord

        return result[:duration_ms]
