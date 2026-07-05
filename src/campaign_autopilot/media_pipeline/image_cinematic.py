"""Cinematic Image Producer — high-quality image generation with cinematic effects.

Features:
- Multi-layer compositing with blend modes
- Cinematic color grading (teal/orange, warm, cool, vintage, dramatic, matte)
- Lighting effects (vignette, spotlight, lens flare, bokeh, bloom)
- Film grain and texture overlays
- Advanced typography with text hierarchy
- Photo-realistic backgrounds (gradient, noise, mesh, radial, duotone)
- Support for all standard formats (featured, thumbnail, pin, instagram, story)
"""

from __future__ import annotations

import os
import random
from enum import Enum
from pathlib import Path
from typing import Any, Tuple

from .cinematic_engine import (
    CinematicEngine,
    ColorGrade,
    LightingEffect,
    Composition,
    Layer,
    _hex_to_rgb,
)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


# ── Style Configuration ──────────────────────────────────────────


class ImageStyle(Enum):
    """Preset cinematic image styles."""

    CINEMATIC = "cinematic"  # Teal/orange, vignette, film grain
    PREMIUM = "premium"  # Clean, high contrast, sharp
    MINIMAL = "minimal"  # Clean background, minimal text
    DRAMATIC = "dramatic"  # High contrast, dark, intense
    WARM = "warm"  # Golden hour warmth, soft
    VINTAGE = "vintage"  # Retro film look, warm tones
    DARK = "dark"  # Dark background, neon accents
    BOLD = "bold"  # Bright colors, strong typography


class AspectRatio(Enum):
    """Common aspect ratios for different platforms."""

    FEATURED = (1200, 630)  # Blog/OG image
    THUMBNAIL = (1280, 720)  # YouTube
    PIN = (1000, 1500)  # Pinterest (2:3)
    INSTAGRAM = (1080, 1080)  # Instagram square
    STORY = (1080, 1920)  # Instagram/TikTok story
    TWITTER = (1200, 675)  # Twitter card
    LINKEDIN = (1200, 627)  # LinkedIn card
    BANNER = (1500, 500)  # Website banner


# ── Cinematic Color Palettes ─────────────────────────────────────

CINEMATIC_PALETTES: list[dict[str, Any]] = [
    # Blockbuster cinematic
    {
        "name": "blockbuster",
        "bg": ["#0a1628", "#1a2a4a", "#2a4a6a"],
        "accent": "#e8a040",
        "text": "#ffffff",
        "grade": ColorGrade.CINEMATIC,
        "lighting": LightingEffect.VIGNETTE,
    },
    # Warm golden
    {
        "name": "golden_hour",
        "bg": ["#2a1a0a", "#4a3a1a", "#8a6a2a"],
        "accent": "#ffc040",
        "text": "#ffffff",
        "grade": ColorGrade.WARM,
        "lighting": LightingEffect.SPOTLIGHT,
    },
    # Cool/tech
    {
        "name": "cyber",
        "bg": ["#0a0a1a", "#0a1a3a", "#0a3a6a"],
        "accent": "#00ffaa",
        "text": "#ffffff",
        "grade": ColorGrade.COOL,
        "lighting": LightingEffect.BOKEH,
    },
    # Dark dramatic
    {
        "name": "noir",
        "bg": ["#050505", "#1a1a1a", "#2a2a2a"],
        "accent": "#ff3040",
        "text": "#ffffff",
        "grade": ColorGrade.DRAMATIC,
        "lighting": LightingEffect.GOD_RAYS,
    },
    # Vintage retro
    {
        "name": "retro",
        "bg": ["#1a0a00", "#3a2a0a", "#5a4a1a"],
        "accent": "#ffa050",
        "text": "#f0e0c0",
        "grade": ColorGrade.VINTAGE,
        "lighting": LightingEffect.FILM_GRRAIN,
    },
    # Clean premium
    {
        "name": "premium",
        "bg": ["#f8f9fa", "#e8ecf0", "#d0d8e0"],
        "accent": "#1a5cff",
        "text": "#1a1a2e",
        "grade": ColorGrade.MATTE,
        "lighting": LightingEffect.NONE,
    },
    # Bold vibrant
    {
        "name": "vibrant",
        "bg": ["#1a0030", "#3a0060", "#5a0090"],
        "accent": "#ff00ff",
        "text": "#ffffff",
        "grade": ColorGrade.CINEMATIC,
        "lighting": LightingEffect.BLOOM,
    },
    # Nature
    {
        "name": "forest",
        "bg": ["#0a1a0a", "#1a3a1a", "#2a5a2a"],
        "accent": "#50ff50",
        "text": "#ffffff",
        "grade": ColorGrade.CINEMATIC,
        "lighting": LightingEffect.BOKEH,
    },
]


# ── Typography Helpers ───────────────────────────────────────────


def _find_font(
    preferred: str = "DejaVuSans-Bold", size: int = 40
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Find available font, fallback to default."""
    paths_to_try = [
        f"/usr/share/fonts/truetype/dejavu/{preferred}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


class TypographyEngine:
    """Advanced typography for cinematic images."""

    @staticmethod
    def draw_text_block(
        draw: ImageDraw.ImageDraw,
        text: str,
        box: Tuple[int, int, int, int],  # left, top, right, bottom
        font_size: int = 48,
        color: str = "#ffffff",
        align: str = "center",
        max_lines: int = 6,
        shadow: bool = True,
        glow: bool = False,
        tracking: float = 1.0,  # letter spacing multiplier
    ) -> None:
        """Draw a text block with cinematic quality."""
        font = _find_font("DejaVuSans-Bold", font_size)
        small_font = _find_font("DejaVuSans", font_size // 2)

        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cw = x2 - x1

        # Word wrap
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            bb = draw.textbbox((0, 0), test, font=font)
            tw = bb[2] - bb[0]
            if tw <= cw:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
                if len(lines) >= max_lines - 1:
                    break
        if current and len(lines) < max_lines:
            lines.append(current)

        if not lines:
            lines = [text[: int(cw / font_size) * 2]]

        # Calculate total height
        line_h = font_size + 8
        total_h = len(lines) * line_h
        y = y1 + (y2 - y1 - total_h) // 2

        for line in lines:
            bb = draw.textbbox((0, 0), line, font=font)
            tw = bb[2] - bb[0]

            if align == "center":
                x = cx - tw // 2
            elif align == "left":
                x = x1
            else:
                x = x2 - tw

            # Shadow
            if shadow:
                r, g, b = _hex_to_rgb(color)
                shadow_color = (r // 4, g // 4, b // 4, 128)
                for dx, dy in [(2, 2), (0, 1), (1, 0)]:
                    draw.text((x + dx, y + dy), line, font=font, fill=shadow_color)

            # Glow
            if glow:
                for r in range(3, 0, -1):
                    draw.text((x, y), line, font=font, fill=(255, 255, 255, 30 // r))

            # Main text
            draw.text((x, y), line, font=font, fill=color)

            y += line_h

    @staticmethod
    def draw_subtitle(
        draw: ImageDraw.ImageDraw,
        text: str,
        position: Tuple[int, int],
        color: str = "#cccccc",
        font_size: int = 24,
    ) -> None:
        """Draw subtitle/secondary text."""
        font = _find_font("DejaVuSans", font_size)
        x, y = position
        bb = draw.textbbox((0, 0), text, font=font)
        tw = bb[2] - bb[0]
        x = x - tw // 2
        # Shadow
        draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), text, font=font, fill=color)

    @staticmethod
    def draw_badge(
        draw: ImageDraw.ImageDraw,
        text: str,
        position: Tuple[int, int],
        bg_color: str = "#ff0000",
        text_color: str = "#ffffff",
        padding: int = 12,
        font_size: int = 20,
    ) -> Tuple[int, int, int, int]:
        """Draw a badge/label with rounded rect background."""
        font = _find_font("DejaVuSans-Bold", font_size)
        x, y = position
        bb = draw.textbbox((0, 0), text, font=font)
        tw = bb[2] - bb[0] + padding * 2
        th = bb[3] - bb[1] + padding
        bg = _hex_to_rgb(bg_color)
        draw.rounded_rectangle(
            [x, y, x + tw, y + th],
            radius=th // 3,
            fill=bg,
        )
        tx = x + padding
        ty = y + padding // 2
        draw.text((tx, ty), text, font=font, fill=text_color)
        return (x, y, x + tw, y + th)


# ── Decorative Elements ──────────────────────────────────────────


class DecorativeElements:
    """Cinematic decorative elements for images."""

    @staticmethod
    def draw_accent_bar(
        draw: ImageDraw.ImageDraw,
        size: Tuple[int, int],
        color: str,
        position: str = "bottom",
        height: int = 6,
        margin: int = 0,
    ) -> None:
        """Draw accent bar at top or bottom."""
        w, h = size
        color_rgb = _hex_to_rgb(color)
        if position == "bottom":
            draw.rectangle([(margin, h - height), (w - margin, h)], fill=color_rgb)
        elif position == "top":
            draw.rectangle([(margin, 0), (w - margin, height)], fill=color_rgb)
        elif position == "left":
            draw.rectangle([(0, margin), (height, h - margin)], fill=color_rgb)

    @staticmethod
    def draw_geometric_pattern(
        draw: ImageDraw.ImageDraw,
        size: Tuple[int, int],
        color: str,
        count: int = 5,
        opacity: int = 30,
    ) -> None:
        """Draw geometric decorative patterns."""
        w, h = size
        color_rgb = (*_hex_to_rgb(color), opacity)
        for _ in range(count):
            x = random.randint(0, w)
            y = random.randint(0, h)
            shape = random.choice(["circle", "rect", "line"])
            if shape == "circle":
                r = random.randint(10, 60)
                draw.ellipse([x - r, y - r, x + r, y + r], outline=color_rgb, width=2)
            elif shape == "rect":
                s = random.randint(20, 80)
                draw.rectangle([x, y, x + s, y + s], outline=color_rgb, width=2)
            elif shape == "line":
                draw.line(
                    [
                        (x, y),
                        (x + random.randint(50, 150), y + random.randint(-30, 30)),
                    ],
                    fill=color_rgb,
                    width=3,
                )

    @staticmethod
    def draw_corner_accents(
        draw: ImageDraw.ImageDraw,
        size: Tuple[int, int],
        color: str,
        length: int = 50,
        thickness: int = 4,
    ) -> None:
        """Draw cinematic corner accents (film frame look)."""
        w, h = size
        c = _hex_to_rgb(color)
        # Top-left
        draw.line([(0, 0), (length, 0)], fill=c, width=thickness)
        draw.line([(0, 0), (0, length)], fill=c, width=thickness)
        # Top-right
        draw.line([(w - length, 0), (w, 0)], fill=c, width=thickness)
        draw.line([(w - 1, 0), (w - 1, length)], fill=c, width=thickness)
        # Bottom-left
        draw.line([(0, h - 1), (length, h - 1)], fill=c, width=thickness)
        draw.line([(0, h - 1), (0, h - length)], fill=c, width=thickness)
        # Bottom-right
        draw.line([(w - length, h - 1), (w, h - 1)], fill=c, width=thickness)
        draw.line([(w - 1, h - length), (w - 1, h)], fill=c, width=thickness)


# ── Cinematic Image Producer ─────────────────────────────────────


class CinematicImageProducer:
    """High-quality cinematic image generator using free tools."""

    def __init__(self, output_dir: str = "output/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_featured_image(
        self,
        title: str,
        niche: str,
        style: ImageStyle = ImageStyle.CINEMATIC,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate cinematic blog featured image (1200x630)."""
        w, h = AspectRatio.FEATURED.value
        palette = self._select_palette(style)

        # Create layered composition
        comp = Composition((w, h))

        prompt = f"Professional blog featured image about {title} in the niche of {niche}, cinematic style, high quality"
        # 1. Background with cinematic style
        bg = CinematicEngine.generate_cinematic_background(
            (w, h), palette["bg"], style="mesh", prompt=prompt
        )
        comp.add_layer(Layer(bg, (0, 0)))

        # 2. Apply lighting
        if palette["lighting"] != LightingEffect.NONE:
            if palette["lighting"] == LightingEffect.VIGNETTE:
                bg = CinematicEngine.apply_vignette(bg, strength=0.4)
            elif palette["lighting"] == LightingEffect.SPOTLIGHT:
                bg = CinematicEngine.apply_spotlight(bg, intensity=0.5)
            elif palette["lighting"] == LightingEffect.BOKEH:
                bg = CinematicEngine.apply_bokeh(bg, count=6, max_size=50)

        # 3. Color grade
        bg = CinematicEngine.apply_color_grade(bg, palette["grade"])

        # 4. Film grain
        bg = CinematicEngine.apply_film_grain(bg, intensity=0.05)

        # Draw on the final image
        img = bg.copy()
        draw = ImageDraw.Draw(img)

        # Decorative elements
        DecorativeElements.draw_accent_bar(
            draw, (w, h), palette["accent"], position="bottom", height=8
        )
        DecorativeElements.draw_corner_accents(
            draw, (w, h), palette["accent"], length=40, thickness=3
        )
        DecorativeElements.draw_geometric_pattern(
            draw, (w, h), palette["accent"], count=3, opacity=25
        )

        # Badge (niche)
        TypographyEngine.draw_badge(
            draw,
            niche.upper(),
            (40, 40),
            bg_color=palette["accent"],
            text_color="#ffffff",
            font_size=18,
            padding=10,
        )

        # Main title
        TypographyEngine.draw_text_block(
            draw,
            title,
            (60, 100, w - 60, h - 80),
            font_size=48,
            color=palette["text"],
            align="left",
            max_lines=4,
            shadow=True,
            glow=False,
        )

        # Save
        filename = filename or f"featured_cinematic_{random.randint(1000, 9999)}.png"
        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)

        return {
            "type": "blog_featured",
            "filename": filename,
            "path": str(path),
            "title": title,
            "style": style.value,
            "width": w,
            "height": h,
            "size_kb": os.path.getsize(path) // 1024,
        }

    def generate_youtube_thumbnail(
        self,
        title: str,
        niche: str,
        style: ImageStyle = ImageStyle.DRAMATIC,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate cinematic YouTube thumbnail (1280x720)."""
        w, h = AspectRatio.THUMBNAIL.value
        palette = self._select_palette(style)

        prompt = f"Eye-catching YouTube thumbnail about {title} in the niche of {niche}, cinematic style, dramatic lighting"
        # Create image with dramatic background
        bg = CinematicEngine.generate_cinematic_background(
            (w, h), palette["bg"], style="radial", prompt=prompt
        )
        bg = CinematicEngine.apply_color_grade(bg, palette["grade"])

        if palette["lighting"] != LightingEffect.NONE:
            bg = CinematicEngine.apply_vignette(bg, strength=0.6)
            bg = CinematicEngine.apply_spotlight(
                bg, center=(w // 2, h // 2), intensity=0.3
            )

        img = bg.copy()
        draw = ImageDraw.Draw(img)

        # YouTube-specific: big bold text
        TypographyEngine.draw_text_block(
            draw,
            title.upper(),
            (80, 80, w - 80, h - 200),
            font_size=64,
            color=palette["text"],
            align="center",
            max_lines=3,
            shadow=True,
            glow=True,
        )

        # Play button overlay
        accent = _hex_to_rgb(palette["accent"])
        play_size = 80
        cx, cy = w // 2, h - 140
        # Circle
        draw.ellipse(
            [cx - play_size, cy - play_size, cx + play_size, cy + play_size],
            fill=accent,
            outline=(255, 255, 255),
            width=4,
        )
        # Triangle
        ts = play_size // 3
        draw.polygon(
            [(cx - ts, cy - ts), (cx - ts, cy + ts), (cx + ts * 2, cy)],
            fill=(255, 255, 255),
        )

        # Bottom bar
        DecorativeElements.draw_accent_bar(
            draw, (w, h), palette["accent"], position="top", height=6
        )
        DecorativeElements.draw_accent_bar(
            draw, (w, h), palette["accent"], position="bottom", height=6
        )

        filename = filename or f"thumb_cinematic_{random.randint(1000, 9999)}.png"
        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)

        return {
            "type": "youtube_thumbnail",
            "filename": filename,
            "path": str(path),
            "title": title,
            "style": style.value,
            "width": w,
            "height": h,
        }

    def generate_pinterest_pin(
        self,
        keyword: str,
        niche: str,
        style: ImageStyle = ImageStyle.VINTAGE,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate cinematic Pinterest pin (1000x1500)."""
        w, h = AspectRatio.PIN.value
        palette = self._select_palette(style)

        prompt = f"Vertical Pinterest pin about {keyword} in the niche of {niche}, elegant cinematic look"
        bg = CinematicEngine.generate_cinematic_background(
            (w, h), palette["bg"], style="mesh", prompt=prompt
        )
        bg = CinematicEngine.apply_color_grade(bg, palette["grade"])
        bg = CinematicEngine.apply_vignette(bg, strength=0.3)

        if palette["lighting"] == LightingEffect.BOKEH:
            bg = CinematicEngine.apply_bokeh(bg, count=12, max_size=60)
        elif palette["lighting"] == LightingEffect.FILM_GRRAIN:
            bg = CinematicEngine.apply_film_grain(bg, intensity=0.08)

        img = bg.copy()
        draw = ImageDraw.Draw(img)

        # Vertical layout
        DecorativeElements.draw_corner_accents(
            draw, (w, h), palette["accent"], length=60, thickness=4
        )

        # Top badge
        TypographyEngine.draw_badge(
            draw,
            f"✨ {niche.upper()}",
            (w // 2 - 80, 60),
            bg_color=palette["accent"],
            text_color="#ffffff",
            font_size=22,
            padding=14,
        )

        # Main keyword - large, centered
        TypographyEngine.draw_text_block(
            draw,
            keyword.upper(),
            (80, 200, w - 80, h - 400),
            font_size=58,
            color=palette["text"],
            align="center",
            max_lines=5,
            shadow=True,
        )

        # Decorative divider
        accent_rgb = _hex_to_rgb(palette["accent"])
        for i in range(3):
            dy = h // 2 + i * 6 - 80
            draw.line([(200, dy), (w - 200, dy)], fill=accent_rgb, width=2)

        # Bottom CTA
        TypographyEngine.draw_badge(
            draw,
            "🔖 SALVAR PARA DEPOIS",
            (w // 2 - 110, h - 200),
            bg_color=palette["accent"],
            text_color="#ffffff",
            font_size=20,
            padding=14,
        )

        filename = filename or f"pin_cinematic_{random.randint(1000, 9999)}.png"
        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)

        return {
            "type": "pinterest_pin",
            "filename": filename,
            "path": str(path),
            "keyword": keyword,
            "style": style.value,
            "width": w,
            "height": h,
        }

    def generate_instagram_post(
        self,
        keyword: str,
        niche: str,
        style: ImageStyle = ImageStyle.BOLD,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate cinematic Instagram post (1080x1080)."""
        w, h = AspectRatio.INSTAGRAM.value
        palette = self._select_palette(style)

        prompt = f"Square Instagram post about {keyword} in the niche of {niche}, clean cinematic design"
        bg = CinematicEngine.generate_cinematic_background(
            (w, h), palette["bg"], style="radial", prompt=prompt
        )
        bg = CinematicEngine.apply_color_grade(bg, palette["grade"])
        bg = CinematicEngine.apply_bloom(bg, threshold=180, radius=8, intensity=0.2)
        bg = CinematicEngine.apply_sharpen(bg, factor=1.2)

        img = bg.copy()
        draw = ImageDraw.Draw(img)

        # Instagram aesthetic frame
        accent_rgb = _hex_to_rgb(palette["accent"])
        draw.rectangle([20, 20, w - 20, h - 20], outline=accent_rgb, width=3)

        # Main content
        TypographyEngine.draw_text_block(
            draw,
            keyword.upper(),
            (80, 200, w - 80, h - 300),
            font_size=62,
            color=palette["text"],
            align="center",
            max_lines=4,
            shadow=True,
            glow=True,
        )

        # Subtitle
        TypographyEngine.draw_subtitle(
            draw,
            f"DICAS DE {niche.upper()}",
            (w // 2, h - 240),
            color=palette["accent"],
            font_size=28,
        )

        # Bottom CTA bar
        draw.rectangle(
            [(w // 2 - 140, h - 180), (w // 2 + 140, h - 140)],
            fill=accent_rgb,
        )
        draw.text((w // 2, h - 165), "💾 SALVE ESTE POST", fill=(255, 255, 255))

        filename = filename or f"ig_cinematic_{random.randint(1000, 9999)}.png"
        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)

        return {
            "type": "instagram_post",
            "filename": filename,
            "path": str(path),
            "keyword": keyword,
            "style": style.value,
            "width": w,
            "height": h,
        }

    def generate_social_card(
        self,
        title: str,
        niche: str,
        style: ImageStyle = ImageStyle.PREMIUM,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate cinematic social media card (1200x630)."""
        w, h = AspectRatio.FEATURED.value
        palette = self._select_palette(style)

        prompt = f"Professional social media sharing card about {title} in the niche of {niche}, clean minimalist design"
        bg = CinematicEngine.generate_cinematic_background(
            (w, h), palette["bg"], style="duotone", prompt=prompt
        )
        bg = CinematicEngine.apply_color_grade(bg, palette["grade"])
        bg = CinematicEngine.apply_letterbox(
            bg, target_ratio=1.91, color=_hex_to_rgb(palette["bg"][0])
        )

        img = bg.copy()
        draw = ImageDraw.Draw(img)

        # Clean card layout
        DecorativeElements.draw_accent_bar(
            draw, (w, h), palette["accent"], position="top", height=4
        )

        TypographyEngine.draw_text_block(
            draw,
            title.upper(),
            (80, 120, w - 80, h - 160),
            font_size=42,
            color=palette["text"],
            align="center",
            max_lines=4,
            shadow=True,
        )

        # Bottom tag
        TypographyEngine.draw_badge(
            draw,
            niche.upper(),
            (w // 2 - 70, h - 100),
            bg_color=palette["accent"],
            text_color="#ffffff",
            font_size=18,
            padding=14,
        )

        filename = filename or f"card_cinematic_{random.randint(1000, 9999)}.png"
        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)

        return {
            "type": "social_card",
            "filename": filename,
            "path": str(path),
            "title": title,
            "style": style.value,
            "width": w,
            "height": h,
        }

    def generate_infographic_slide(
        self,
        title: str,
        bullet_points: list[str],
        niche: str,
        style: ImageStyle = ImageStyle.CINEMATIC,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate a cinematic infographic slide."""
        w, h = 1200, 1200
        palette = self._select_palette(style)

        prompt = f"Abstract modern infographic background about {title} in the niche of {niche}, high resolution"
        bg = CinematicEngine.generate_cinematic_background(
            (w, h), palette["bg"], style="mesh", prompt=prompt
        )
        bg = CinematicEngine.apply_color_grade(bg, palette["grade"])
        bg = CinematicEngine.apply_vignette(bg, strength=0.3)

        img = bg.copy()
        draw = ImageDraw.Draw(img)

        # Title
        TypographyEngine.draw_text_block(
            draw,
            title,
            (80, 60, w - 80, 200),
            font_size=48,
            color=palette["text"],
            align="left",
            max_lines=2,
            shadow=True,
        )

        # Accent line under title
        accent_rgb = _hex_to_rgb(palette["accent"])
        draw.line([(80, 210), (w - 80, 210)], fill=accent_rgb, width=3)

        # Bullet points
        y = 270
        for i, point in enumerate(bullet_points[:6]):
            icon = f"{i + 1}. "
            font = _find_font("DejaVuSans-Bold", 30)

            # Number circle
            cx, cy = 100, y + 20
            draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=accent_rgb)
            draw.text(
                (cx - 6, cy - 10),
                str(i + 1),
                fill=(255, 255, 255),
                font=_find_font("DejaVuSans-Bold", 22),
            )

            # Text
            font_text = _find_font("DejaVuSans", 28)
            draw.text((140, y), point, fill=palette["text"], font=font_text)

            y += 80

        # Bottom brand
        DecorativeElements.draw_accent_bar(
            draw, (w, h), palette["accent"], position="bottom", height=6, margin=40
        )
        draw.text(
            (60, h - 60),
            f"@{niche.replace(' ', '').lower()}",
            fill=accent_rgb,
            font=_find_font("DejaVuSans", 22),
        )

        filename = filename or f"infographic_cinematic_{random.randint(1000, 9999)}.png"
        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)

        return {
            "type": "infographic_slide",
            "filename": filename,
            "path": str(path),
            "title": title,
            "style": style.value,
            "width": w,
            "height": h,
        }

    def generate_multi_format(
        self,
        title: str,
        niche: str,
        keywords: list[str],
    ) -> list[dict[str, Any]]:
        """Generate all image formats for a campaign in one shot."""
        results = []
        try:
            results.append(
                self.generate_featured_image(title, niche, ImageStyle.CINEMATIC)
            )
        except Exception as e:
            results.append({"type": "error", "step": "featured", "error": str(e)})
        try:
            results.append(
                self.generate_youtube_thumbnail(title, niche, ImageStyle.DRAMATIC)
            )
        except Exception as e:
            results.append({"type": "error", "step": "thumbnail", "error": str(e)})
        for kw in keywords[:3]:
            try:
                results.append(
                    self.generate_pinterest_pin(kw, niche, ImageStyle.VINTAGE)
                )
            except Exception as e:
                results.append({"type": "error", "step": f"pin_{kw}", "error": str(e)})
            try:
                results.append(self.generate_instagram_post(kw, niche, ImageStyle.BOLD))
            except Exception as e:
                results.append({"type": "error", "step": f"ig_{kw}", "error": str(e)})
        try:
            results.append(self.generate_social_card(title, niche, ImageStyle.PREMIUM))
        except Exception as e:
            results.append({"type": "error", "step": "card", "error": str(e)})
        return results

    def _select_palette(self, style: ImageStyle) -> dict:
        """Select color palette based on style."""
        style_map = {
            ImageStyle.CINEMATIC: 0,
            ImageStyle.PREMIUM: 5,
            ImageStyle.MINIMAL: 5,
            ImageStyle.DRAMATIC: 3,
            ImageStyle.WARM: 1,
            ImageStyle.VINTAGE: 4,
            ImageStyle.DARK: 3,
            ImageStyle.BOLD: 6,
        }
        idx = style_map.get(style, 0)
        palette = dict(CINEMATIC_PALETTES[idx])
        palette["grade"] = CINEMATIC_PALETTES[idx]["grade"]
        palette["lighting"] = CINEMATIC_PALETTES[idx]["lighting"]
        return palette
