"""Cinematic Engine — core visual effects library for image and video.

Provides cinematic-quality effects using Pillow and numpy:
- Color grading (teal/orange, warm, cool, bw, vintage, cinematic)
- Blend modes (screen, multiply, overlay, soft light, hard light)
- Lighting effects (vignette, spotlight, lens flare, god rays)
- Layer compositing with masks and opacity
- Texture generation (noise, grain, bokeh)
- Frame/post-processing (letterbox, sharpen, bloom)
"""

from __future__ import annotations

import math
import random
from enum import Enum
from typing import Tuple

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore
    HAS_NUMPY = False

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageMath, ImageEnhance

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


# ── Types ──────────────────────────────────────────────────────────

Point = Tuple[int, int]
Size = Tuple[int, int]
Color = Tuple[int, int, int]
ColorRGBA = Tuple[int, int, int, int]


class BlendMode(Enum):
    """Image blend modes for compositing."""

    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"
    HARD_LIGHT = "hard_light"
    DODGE = "dodge"
    BURN = "burn"
    DARKEN = "darken"
    LIGHTEN = "lighten"


class ColorGrade(Enum):
    """Cinematic color grading presets."""

    NONE = "none"
    CINEMATIC = "cinematic"  # Teal/orange blockbuster look
    WARM = "warm"  # Golden hour warmth
    COOL = "cool"  # Blue/cold atmosphere
    VINTAGE = "vintage"  # Retro film look
    BW = "black_and_white"  # Monochrome
    DRAMATIC = "dramatic"  # High contrast, desaturated
    MATTE = "matte"  # Faded blacks, flat look
    HORROR = "horror"  # Green tint, high contrast


class LightingEffect(Enum):
    """Lighting and atmosphere effects."""

    NONE = "none"
    VIGNETTE = "vignette"
    SPOTLIGHT = "spotlight"
    GOD_RAYS = "god_rays"
    LENS_FLARE = "lens_flare"
    BOKEH = "bokeh"
    FILM_GRRAIN = "film_grain"
    BLOOM = "bloom"


# ── Data Classes ──────────────────────────────────────────────────


class Layer:
    """A compositable layer with blending and opacity."""

    def __init__(
        self,
        image: Image.Image,
        position: Point = (0, 0),
        opacity: float = 1.0,
        blend_mode: BlendMode = BlendMode.NORMAL,
        mask: Image.Image | None = None,
        rotation: float = 0.0,
        scale: float = 1.0,
    ):
        self.image = image
        self.position = position
        self.opacity = opacity
        self.blend_mode = blend_mode
        self.mask = mask
        self.rotation = rotation
        self.scale = scale


class Composition:
    """A multi-layer composition ready for rendering."""

    def __init__(self, size: Size, background_color: Color = (0, 0, 0)):
        self.size = size
        self.background_color = background_color
        self.layers: list[Layer] = []

    def add_layer(self, layer: Layer) -> None:
        self.layers.append(layer)

    def render(self) -> Image.Image:
        """Render all layers into final image with blending."""
        base = Image.new("RGBA", self.size, (*self.background_color, 255))
        for layer in self.layers:
            img = layer.image
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            if layer.scale != 1.0:
                new_size = (int(img.width * layer.scale), int(img.height * layer.scale))
                img = img.resize(new_size, Image.LANCZOS)
            if layer.rotation:
                img = img.rotate(layer.rotation, expand=True, resample=Image.BICUBIC)
            blended = _blend_images(
                base, img, layer.position, layer.blend_mode, layer.opacity
            )
            if layer.mask:
                mask_resized = layer.mask.resize(blended.size, Image.LANCZOS)
                blended.putalpha(mask_resized)
            base = blended
        return base


# ── Cinematic Engine ──────────────────────────────────────────────


class CinematicEngine:
    """Core cinematic effects engine. All methods are static."""

    # ── Color Grading ──────────────────────────────────────────

    @staticmethod
    def apply_color_grade(image: Image.Image, grade: ColorGrade) -> Image.Image:
        """Apply cinematic color grading to an image."""
        if grade == ColorGrade.NONE or not HAS_PILLOW:
            return image

        img = image.convert("RGB")
        pixels = np.array(img, dtype=np.float32)

        if grade == ColorGrade.CINEMATIC:
            # Teal/orange blockbuster look
            pixels = _grade_cinematic(pixels)
        elif grade == ColorGrade.WARM:
            pixels = _grade_warm(pixels)
        elif grade == ColorGrade.COOL:
            pixels = _grade_cool(pixels)
        elif grade == ColorGrade.VINTAGE:
            pixels = _grade_vintage(pixels)
        elif grade == ColorGrade.BW:
            gray = np.dot(pixels[..., :3], [0.299, 0.587, 0.114])
            pixels = np.stack([gray, gray, gray], axis=-1)
        elif grade == ColorGrade.DRAMATIC:
            pixels = _grade_dramatic(pixels)
        elif grade == ColorGrade.MATTE:
            pixels = _grade_matte(pixels)

        pixels = np.clip(pixels, 0, 255).astype(np.uint8)
        return Image.fromarray(pixels, "RGB")

    # ── Lighting Effects ──────────────────────────────────────

    @staticmethod
    def apply_vignette(
        image: Image.Image,
        strength: float = 0.5,
        radius: float = 0.75,
        color: tuple = (0, 0, 0),
    ) -> Image.Image:
        """Apply cinematic vignette effect (darkened edges)."""
        img = image.convert("RGBA")
        w, h = img.size
        vignette = Image.new("RGBA", (w, h), (*color, 0))
        draw = ImageDraw.Draw(vignette)

        cx, cy = w // 2, h // 2
        max_rad = math.sqrt(cx**2 + cy**2) * radius

        for i in range(256):
            alpha = int(i * strength)
            if alpha == 0:
                continue
            r = max_rad * (1 - i / 256)
            if r < 1:
                break
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r], outline=(*color, alpha), width=3
            )

        result = Image.alpha_composite(img, vignette)
        return result.convert("RGB")

    @staticmethod
    def apply_spotlight(
        image: Image.Image,
        center: Point | None = None,
        radius: float = 0.4,
        intensity: float = 0.6,
    ) -> Image.Image:
        """Apply spotlight effect — bright center, dark edges."""
        img = image.convert("RGBA")
        w, h = img.size
        cx, cy = center or (w // 2, h // 3)
        max_rad = min(w, h) * radius

        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        for r in range(int(max_rad), 0, -1):
            alpha = int(255 * (1 - r / max_rad) * intensity)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)

        result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return result.convert("RGB")

    @staticmethod
    def apply_lens_flare(
        image: Image.Image,
        position: Point | None = None,
        intensity: float = 0.3,
    ) -> Image.Image:
        """Apply cinematic lens flare effect."""
        img = image.convert("RGBA")
        w, h = img.size
        cx, cy = position or (w // 3, h // 4)

        flare = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(flare)

        # Main flare
        r = min(w, h) // 8
        for i in range(5):
            alpha = int(100 * intensity / (i + 1))
            offset_x = int((w - cx) * i * 0.15)
            offset_y = int((h - cy) * i * 0.1)
            fr = r // (i + 1)
            draw.ellipse(
                [
                    cx + offset_x - fr,
                    cy + offset_y - fr,
                    cx + offset_x + fr,
                    cy + offset_y + fr,
                ],
                fill=(255, 255, 200, alpha),
            )

        # Light streak
        for i in range(3):
            alpha = int(60 * intensity)
            sy = cy + (h - cy) * i // 3
            draw.line(
                [(cx, cy), (w, sy)],
                fill=(255, 255, 220, alpha),
                width=max(1, 8 - i * 2),
            )

        result = Image.alpha_composite(img, flare)
        return result.convert("RGB")

    @staticmethod
    def apply_film_grain(image: Image.Image, intensity: float = 0.1) -> Image.Image:
        """Add film grain texture for cinematic feel."""
        img = np.array(image.convert("RGB"), dtype=np.float32)
        noise = np.random.randn(*img.shape) * intensity * 255
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(img, "RGB")

    @staticmethod
    def apply_bokeh(
        image: Image.Image, count: int = 8, max_size: int = 40
    ) -> Image.Image:
        """Apply decorative bokeh circles for cinematic look."""
        img = image.convert("RGBA")
        w, h = img.size
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for _ in range(count):
            x = random.randint(0, w)
            y = random.randint(0, h)
            r = random.randint(5, max_size)
            alpha = random.randint(10, 40)
            color = (255, 255, 255, alpha)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=None)
            # Inner glow
            if r > 10:
                draw.ellipse(
                    [x - r // 3, y - r // 3, x + r // 3, y + r // 3],
                    fill=(255, 255, 255, alpha // 2),
                )

        result = Image.alpha_composite(img, overlay)
        return result.convert("RGB")

    @staticmethod
    def apply_bloom(
        image: Image.Image,
        threshold: int = 200,
        radius: int = 10,
        intensity: float = 0.3,
    ) -> Image.Image:
        """Apply bloom/glow effect to bright areas."""
        img = image.convert("RGB")
        bright = img.point(lambda p: p if p > threshold else 0)
        blurred = bright.filter(ImageFilter.GaussianBlur(radius))
        blended = Image.blend(img, blurred, intensity)
        return blended

    # ── Post-Processing ────────────────────────────────────────

    @staticmethod
    def apply_letterbox(
        image: Image.Image, target_ratio: float = 16 / 9, color: Color = (0, 0, 0)
    ) -> Image.Image:
        """Add letterbox/pillarbox bars for cinematic aspect ratio."""
        w, h = image.size
        current_ratio = w / h
        if abs(current_ratio - target_ratio) < 0.01:
            return image

        if current_ratio > target_ratio:
            new_w = w
            new_h = int(w / target_ratio)
        else:
            new_h = h
            new_w = int(h * target_ratio)

        result = Image.new("RGB", (new_w, new_h), color)
        x = (new_w - w) // 2
        y = (new_h - h) // 2
        result.paste(image, (x, y))
        return result

    @staticmethod
    def apply_sharpen(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Sharpen image for cinematic clarity."""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def apply_contrast(image: Image.Image, factor: float = 1.1) -> Image.Image:
        """Adjust contrast."""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    # ── Background Generation ──────────────────────────────────

    @staticmethod
    def generate_cinematic_background(
        size: Size,
        palette: list[str],
        style: str = "gradient",
        prompt: str | None = None,
    ) -> Image.Image:
        """Generate a cinematic background with various styles."""
        w, h = size
        if prompt:
            try:
                import io
                from ..media_providers import get_best_image_provider
                provider = get_best_image_provider()
                if provider.name() != "pillow":
                    img_bytes = provider.generate(prompt, width=w, height=h)
                    img = Image.open(io.BytesIO(img_bytes))
                    return img.resize((w, h), Image.Resampling.LANCZOS)
            except Exception:
                pass

        if style == "gradient":
            return _gradient_background(w, h, palette)
        elif style == "noise":
            return _noise_background(w, h, palette)
        elif style == "mesh":
            return _mesh_gradient(w, h, palette)
        elif style == "radial":
            return _radial_gradient(w, h, palette)
        elif style == "duotone":
            return _duotone_background(w, h, palette)
        else:
            return _gradient_background(w, h, palette)


# ── Blend Implementation ──────────────────────────────────────────


def _blend_images(
    base: Image.Image,
    overlay: Image.Image,
    position: Point,
    mode: BlendMode,
    opacity: float,
) -> Image.Image:
    """Blend overlay onto base at position with given mode and opacity."""
    if mode == BlendMode.NORMAL:
        result = base.copy()
        if overlay.mode == "RGBA":
            result.paste(overlay, position, overlay)
        else:
            result.paste(overlay, position)
        return result

    # Ensure same size for pixel operations
    bx, by = position
    bw, bh = base.size
    ow, oh = overlay.size

    # Create a copy of base
    result = base.copy().convert("RGBA")
    overlay_rgba = overlay.convert("RGBA")

    for y in range(max(0, by), min(bh, by + oh)):
        for x in range(max(0, bx), min(bw, bx + ow)):
            ox = x - bx
            oy = y - by
            if ox < 0 or ox >= ow or oy < 0 or oy >= oh:
                continue

            bp = result.getpixel((x, y))
            op = overlay_rgba.getpixel((ox, oy))
            alpha = op[3] / 255.0 * opacity

            if alpha <= 0:
                continue

            # Blend base and overlay colors
            blended = _blend_pixels(bp[:3], op[:3], mode)
            # Alpha composite
            result.putpixel(
                (x, y),
                (
                    int(blended[0] * alpha + bp[0] * (1 - alpha)),
                    int(blended[1] * alpha + bp[1] * (1 - alpha)),
                    int(blended[2] * alpha + bp[2] * (1 - alpha)),
                    255,
                ),
            )

    return result


def _blend_pixels(base: tuple, overlay: tuple, mode: BlendMode) -> tuple:
    """Blend two RGB pixels."""
    b = np.array(base, dtype=np.float32) / 255.0
    o = np.array(overlay, dtype=np.float32) / 255.0
    eps = 1e-7

    if mode == BlendMode.MULTIPLY:
        result = b * o
    elif mode == BlendMode.SCREEN:
        result = 1 - (1 - b) * (1 - o)
    elif mode == BlendMode.OVERLAY:
        mask = b < 0.5
        result = np.where(mask, 2 * b * o, 1 - 2 * (1 - b) * (1 - o))
    elif mode == BlendMode.SOFT_LIGHT:
        result = (1 - 2 * o) * b**2 + 2 * o * b
    elif mode == BlendMode.HARD_LIGHT:
        mask = o < 0.5
        result = np.where(mask, 2 * b * o, 1 - 2 * (1 - b) * (1 - o))
    elif mode == BlendMode.DODGE:
        result = b / (1 - o + eps)
    elif mode == BlendMode.BURN:
        result = 1 - (1 - b) / (o + eps)
    elif mode == BlendMode.DARKEN:
        result = np.minimum(b, o)
    elif mode == BlendMode.LIGHTEN:
        result = np.maximum(b, o)
    else:
        result = o

    result = np.clip(result * 255, 0, 255).astype(int)
    return tuple(result)


# ── Color Grading Implementations ────────────────────────────────


def _grade_cinematic(pixels: np.ndarray) -> np.ndarray:
    """Teal/orange cinematic look — shadows teal, highlights orange."""
    result = pixels.copy()
    # Shadows → teal
    result[..., 0] *= 0.9  # Reduce red in shadows
    result[..., 2] *= 1.1  # Boost blue
    # Highlights → warm
    gray = np.dot(result[..., :3], [0.299, 0.587, 0.114])
    for c in range(3):
        channel = result[..., c]
        mask = channel > 100
        if c == 0:  # Red boost in highlights
            channel[mask] = np.clip(channel[mask] * 1.15, 0, 255)
        elif c == 2:  # Blue reduce in highlights
            channel[mask] = np.clip(channel[mask] * 0.85, 0, 255)
    # Split tone
    result[..., 0] = np.clip(result[..., 0] + 10, 0, 255)
    result[..., 2] = np.clip(result[..., 2] - 5, 0, 255)
    return result


def _grade_warm(pixels: np.ndarray) -> np.ndarray:
    """Golden hour warm look."""
    result = pixels.copy()
    result[..., 0] = np.clip(result[..., 0] * 1.15, 0, 255)  # Boost red
    result[..., 1] = np.clip(result[..., 1] * 1.05, 0, 255)  # Slight green boost
    result[..., 2] = np.clip(result[..., 2] * 0.85, 0, 255)  # Reduce blue
    return result


def _grade_cool(pixels: np.ndarray) -> np.ndarray:
    """Cold/blue atmospheric look."""
    result = pixels.copy()
    result[..., 0] = np.clip(result[..., 0] * 0.85, 0, 255)
    result[..., 1] = np.clip(result[..., 1] * 0.95, 0, 255)
    result[..., 2] = np.clip(result[..., 2] * 1.2, 0, 255)
    return result


def _grade_vintage(pixels: np.ndarray) -> np.ndarray:
    """Retro vintage film look."""
    result = pixels.copy()
    # Faded blacks
    result = result * 0.9 + 25
    # Warm tint
    result[..., 0] = np.clip(result[..., 0] * 1.1, 0, 255)
    result[..., 2] = np.clip(result[..., 2] * 0.8, 0, 255)
    # Reduce contrast
    gray = np.dot(result[..., :3], [0.299, 0.587, 0.114])
    result = result * 0.85 + np.stack([gray, gray, gray], axis=-1) * 0.15
    # Slight yellow
    result[..., 1] = np.clip(result[..., 1] * 1.05, 0, 255)
    return result


def _grade_dramatic(pixels: np.ndarray) -> np.ndarray:
    """High contrast dramatic look."""
    result = pixels.copy()
    gray = np.dot(result[..., :3], [0.299, 0.587, 0.114])
    # Crush blacks
    gray = np.clip((gray - 30) * 1.4, 0, 255)
    gray = np.clip((gray / 255) ** 1.2 * 255, 0, 255)
    result = np.stack([gray, gray, gray], axis=-1)
    # Slight cool tint in shadows
    shadow_mask = gray < 100
    result[shadow_mask, 2] = np.clip(result[shadow_mask, 2] * 1.1, 0, 255)
    return result


def _grade_matte(pixels: np.ndarray) -> np.ndarray:
    """Matte/flat look with faded blacks."""
    result = pixels.copy()
    gray = np.dot(result[..., :3], [0.299, 0.587, 0.114])
    # Lift blacks
    result = result * 0.85 + np.stack([gray * 0.15 + 20] * 3, axis=-1)
    # Desaturate slightly
    result = result * 0.8 + np.stack([gray * 0.2] * 3, axis=-1)
    result = np.clip(result, 0, 255)
    return result


# ── Background Generators ────────────────────────────────────────


def _hex_to_rgb(hx: str) -> tuple:
    hx = hx.lstrip("#")
    return (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16))


def _gradient_background(w: int, h: int, palette: list[str]) -> Image.Image:
    """Linear gradient background."""
    img = Image.new("RGB", (w, h))
    colors = [_hex_to_rgb(c) for c in palette[:3]]
    draw = ImageDraw.Draw(img)
    n = len(colors)
    seg_h = h / (n - 1) if n > 1 else h
    for y in range(h):
        seg = min(int(y / seg_h), n - 2) if n > 1 else 0
        local_y = y - seg * seg_h if n > 1 else y
        ratio = local_y / seg_h if seg_h > 0 else 0
        r = int(colors[seg][0] + (colors[seg + 1][0] - colors[seg][0]) * ratio)
        g = int(colors[seg][1] + (colors[seg + 1][1] - colors[seg][1]) * ratio)
        b = int(colors[seg][2] + (colors[seg + 1][2] - colors[seg][2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _mesh_gradient(w: int, h: int, palette: list[str]) -> Image.Image:
    """Mesh/grainy gradient background."""
    base = _gradient_background(w, h, palette)
    # Add noise for texture
    noise = np.random.randn(h, w, 3) * 15
    arr = np.array(base, dtype=np.float32)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _radial_gradient(w: int, h: int, palette: list[str]) -> Image.Image:
    """Radial gradient (vignette style)."""
    img = Image.new("RGB", (w, h))
    colors = [_hex_to_rgb(c) for c in palette[:2]]
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2
    max_r = math.sqrt(cx**2 + cy**2)
    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ratio = min(dist / max_r, 1.0)
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            draw.point((x, y), fill=(r, g, b))
    return img


def _noise_background(w: int, h: int, palette: list[str]) -> Image.Image:
    """Noise texture background."""
    color = _hex_to_rgb(palette[0])
    noise = np.random.randn(h, w, 3) * 30
    base = np.ones((h, w, 3), dtype=np.float32) * np.array(color)
    arr = np.clip(base + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _duotone_background(w: int, h: int, palette: list[str]) -> Image.Image:
    """Duotone gradient — two colors only."""
    c1 = _hex_to_rgb(palette[0])
    c2 = _hex_to_rgb(palette[1]) if len(palette) > 1 else (255, 255, 255)
    gray = np.linspace(0, 1, h * w).reshape(h, w)
    r = np.clip(c1[0] + (c2[0] - c1[0]) * gray, 0, 255).astype(np.uint8)
    g = np.clip(c1[1] + (c2[1] - c1[1]) * gray, 0, 255).astype(np.uint8)
    b = np.clip(c1[2] + (c2[2] - c1[2]) * gray, 0, 255).astype(np.uint8)
    arr = np.stack([r, g, b], axis=-1)
    return Image.fromarray(arr, "RGB")


# ── Text Helpers ─────────────────────────────────────────────────


def _wrap_text(text: str, max_chars: int = 30) -> list[str]:
    """Wrap text at word boundaries."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += " " + word if current else word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text[:max_chars]]
