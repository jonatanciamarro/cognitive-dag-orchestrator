"""Agente de Produção Gratuita de Vídeos — cria vídeos usando moviepy + Pillow.

Gera slideshow videos com transições. Formatos:
- youtube: 1280x720 (16:9 redução para performance)
- tiktok: 720x1280 (9:16 vertical)

Dependências: pip install moviepy Pillow (ffmpeg required)
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)

HAS_PILLOW = False
HAS_MOVIEPY = False
try:
    from PIL import Image, ImageDraw

    HAS_PILLOW = True
except ImportError:
    pass
try:
    from moviepy import ImageClip, concatenate_videoclips
    from moviepy.video.fx import FadeIn, FadeOut

    HAS_MOVIEPY = True
except ImportError:
    try:
        from moviepy import ImageClip, concatenate_videoclips, vfx

        HAS_MOVIEPY = True
    except ImportError:
        pass


COLORS = [
    ("#0F2027", "#2C5364"),
    ("#232526", "#8E0E00"),
    ("#134E5E", "#71B280"),
    ("#1a1a2e", "#0f3460"),
    ("#2C1B4D", "#7B5EA7"),
    ("#000000", "#16213E"),
    ("#1B1B2F", "#3A3A5C"),
    ("#2D1B00", "#7B5E00"),
]


def _wrap(text: str, max_chars: int = 25) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur += " " + w if cur else w
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text[:max_chars]]


def _make_slide(text: str, subtitle: str, size: tuple, is_title: bool = False) -> Path:
    """Create a single slide as PNG."""
    import tempfile

    w, h = size
    c1, c2 = random.choice(COLORS)

    def _hex(hx):
        hx = hx.lstrip("#")
        return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)

    r1, g1, b1 = _hex(c1)
    r2, g2, b2 = _hex(c2)

    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    # Gradient
    for y in range(h):
        r = r1 + int((r2 - r1) * y / h)
        g = g1 + int((g2 - g1) * y / h)
        b = b1 + int((b2 - b1) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Decorative dots
    for _ in range(5):
        x = random.randint(50, w - 50)
        y = random.randint(50, h - 50)
        r = random.randint(10, 40)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 20))

    # Title
    fs = 42 if is_title else 32
    lines = _wrap(text, w // (fs // 2))
    y_start = h // 3
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line)
        tw = bbox[2] - bbox[0]
        for dx, dy in [(2, 2), (-1, 1)]:
            draw.text(((w - tw) // 2 + dx, y + dy), line, fill=(0, 0, 0, 80))
        draw.text(((w - tw) // 2, y), line, fill=(255, 255, 255))
        y += fs + 6

    # Subtitle
    if subtitle:
        y += 10
        draw.text((w // 2, y), subtitle, fill=(255, 215, 0))

    # Bottom accent bar
    accent = _hex(c2)
    draw.rectangle([(0, h - 6), (w, h)], fill=accent)

    path = Path(tempfile.mkdtemp()) / f"slide_{random.randint(0, 99999)}.png"
    img.save(str(path), "PNG", optimize=True)
    return path


class FreeVideoProducerAgent(AgentBase):
    """Produz videos gratuitamente usando o melhor provider disponivel.

    Usa:
    - MoviePy + media_providers para qualidade superior
    - Edge-TTS para narracao com vozes neurais (se disponivel)
    - Gera slideshow videos com transicoes e audio
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("free_video_producer", **kwargs)
        self.output_dir = Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._video_provider = None
        self._audio_provider = None

    def _get_video_provider(self):
        if self._video_provider is None:
            from campaign_autopilot.media_providers import get_best_video_provider

            self._video_provider = get_best_video_provider()
        return self._video_provider

    def _get_audio_provider(self):
        if self._audio_provider is None:
            from campaign_autopilot.media_providers import get_best_audio_provider

            self._audio_provider = get_best_audio_provider()
        return self._audio_provider

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        sr = context.step_results

        if not HAS_MOVIEPY or not HAS_PILLOW:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": "Instale: pip install moviepy Pillow"},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="free_video_producer",
                    status="error",
                    started_at=started_at,
                    finished_at=utc_now_iso(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        video_provider = self._get_video_provider()
        audio_provider = self._get_audio_provider()
        use_narration = audio_provider.name() not in ("gtts",)

        # Collect content
        articles = self._get_articles(sr)
        keywords = self._get_keywords(sr, campaign)

        videos: list[dict[str, Any]] = []
        errors: list[str] = []

        # YouTube (reduced res for speed: 854x480)
        for article in articles[:1]:
            try:
                title = article.get("title", niche)
                slug = article.get("slug", title)[:20]
                path = self._make_youtube(
                    title, niche, slug, video_provider, audio_provider, use_narration
                )
                mb = os.path.getsize(path) / (1024 * 1024) if path.exists() else 0
                videos.append(
                    {
                        "type": "youtube",
                        "filename": path.name,
                        "path": str(path),
                        "title": title,
                        "size_mb": round(mb, 1),
                        "duration_sec": 20,
                    }
                )
            except Exception as e:
                errors.append(f"yt: {e}")

        # TikTok
        for kw in keywords[:2]:
            try:
                k = kw.get("keyword", kw.get("term", niche))
                slug = k[:15]
                path = self._make_tiktok(
                    k, niche, slug, video_provider, audio_provider, use_narration
                )
                mb = os.path.getsize(path) / (1024 * 1024) if path.exists() else 0
                videos.append(
                    {
                        "type": "tiktok",
                        "filename": path.name,
                        "path": str(path),
                        "keyword": k,
                        "size_mb": round(mb, 1),
                        "duration_sec": 12,
                    }
                )
            except Exception as e:
                errors.append(f"tt: {e}")

        output = {
            "status": "success",
            "videos_generated": len(videos),
            "videos": videos,
            "errors": errors,
            "output_directory": str(self.output_dir.absolute()),
            "video_provider": video_provider.name(),
            "audio_provider": audio_provider.name(),
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="free_video_producer",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Produziu {len(videos)} videos. Audio: {audio_provider.name()}"],
            metadata={
                "videos": len(videos),
                "errors": len(errors),
                "video_provider": video_provider.name(),
                "audio_provider": audio_provider.name(),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _get_articles(self, sr: dict) -> list:
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        return out.get("articles", []) or out.get("generated_articles", []) or []

    def _get_keywords(self, sr: dict, campaign: dict) -> list:
        seo = sr.get("seo_research", {})
        out = seo.get("output", {}) if isinstance(seo, dict) else {}
        kws = out.get("top_opportunities", []) or out.get("keywords", [])
        return (
            kws
            if isinstance(kws, list) and kws
            else [{"keyword": str(campaign.get("objective", "teste"))}]
        )

    def _make_youtube(
        self,
        title: str,
        niche: str,
        slug: str,
        video_provider=None,
        audio_provider=None,
        use_narration=False,
    ) -> Path:
        """Create YouTube video (854x480, ~20s) with optional AI narration."""
        size = (854, 480)
        clips = []

        # Title slide
        t = _make_slide(title.upper(), niche, size, True)
        clips.append(ImageClip(str(t), duration=4))

        # Content slides
        segs = title.split()
        for i in range(0, min(len(segs), 6), 2):
            chunk = " ".join(segs[i : i + 2])
            s = _make_slide(
                f"\U0001f4cc {chunk}" if i > 0 else chunk, f"Passo {i // 2 + 1}", size
            )
            clips.append(ImageClip(str(s), duration=4))

        # CTA
        c = _make_slide(
            "Gostou? Inscreva-se! \U0001f680", f"Mais em {niche}", size, True
        )
        clips.append(ImageClip(str(c), duration=4))

        final = concatenate_videoclips(clips, method="compose")
        final = final.with_effects([FadeIn(0.5), FadeOut(0.5)])

        # Generate AI narration audio if available
        audio_path = ""
        if audio_provider and use_narration:
            try:
                script = f"{title}. Neste video, vamos explorar {niche}. {segs[0] if segs else ''}. Gostou? Inscreva-se para mais conteudo."
                audio_bytes = audio_provider.text_to_speech(script, lang="pt-BR")
                audio_path = str(self.output_dir / f"narration_{slug}.wav")
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
            except Exception:
                audio_path = ""

        path = self.output_dir / f"yt_{slug}.mp4"
        if audio_path and os.path.exists(audio_path):
            try:
                from moviepy import AudioFileClip

                audio = AudioFileClip(audio_path)
                if audio.duration < final.duration:
                    from moviepy import concatenate_audioclips

                    audio = concatenate_audioclips(
                        [audio, audio.subclipped(0, final.duration - audio.duration)]
                    )
                final = final.with_audio(audio)
                final.write_videofile(
                    str(path),
                    fps=12,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None,
                )
            except Exception:
                final.write_videofile(
                    str(path),
                    fps=12,
                    codec="libx264",
                    audio=False,
                    preset="ultrafast",
                    logger=None,
                )
        else:
            final.write_videofile(
                str(path),
                fps=12,
                codec="libx264",
                audio=False,
                preset="ultrafast",
                logger=None,
            )
        return path

    def _make_tiktok(
        self,
        keyword: str,
        niche: str,
        slug: str,
        video_provider=None,
        audio_provider=None,
        use_narration=False,
    ) -> Path:
        """Create TikTok video (540x960, ~12s) with optional AI narration."""
        size = (540, 960)
        clips = []

        h = _make_slide(f"\u26a0\ufe0f {keyword.upper()}", niche, size, True)
        clips.append(ImageClip(str(h), duration=3))

        tips = ["Dica: Consistencia e chave", f"Foque em {niche}", "Mede resultados"]
        for tip in tips:
            s = _make_slide(tip, "", size)
            clips.append(ImageClip(str(s), duration=3))

        c = _make_slide(
            "Segue para mais! \U0001f680", f"#{niche.replace(' ', '')}", size, True
        )
        clips.append(ImageClip(str(c), duration=3))

        final = concatenate_videoclips(clips, method="compose")
        final = final.with_effects([FadeIn(0.3), FadeOut(0.3)])

        # Generate AI narration audio if available
        audio_path = ""
        if audio_provider and use_narration:
            try:
                script = f"{keyword}! {tips[0]}. {tips[1]}. {tips[2]}. Segue para mais conteudo sobre {niche}."
                audio_bytes = audio_provider.text_to_speech(script, lang="pt-BR")
                audio_path = str(self.output_dir / f"narration_tt_{slug}.wav")
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
            except Exception:
                audio_path = ""

        path = self.output_dir / f"tt_{slug}.mp4"
        if audio_path and os.path.exists(audio_path):
            try:
                from moviepy import AudioFileClip

                audio = AudioFileClip(audio_path)
                if audio.duration < final.duration:
                    from moviepy import concatenate_audioclips

                    audio = concatenate_audioclips(
                        [audio, audio.subclipped(0, final.duration - audio.duration)]
                    )
                final = final.with_audio(audio)
                final.write_videofile(
                    str(path),
                    fps=10,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None,
                )
            except Exception:
                final.write_videofile(
                    str(path),
                    fps=10,
                    codec="libx264",
                    audio=False,
                    preset="ultrafast",
                    logger=None,
                )
        else:
            final.write_videofile(
                str(path),
                fps=10,
                codec="libx264",
                audio=False,
                preset="ultrafast",
                logger=None,
            )
        return path
