"""Agente de Geração Gratuita de Imagens — cria imagens profissionais usando Pillow (sem APIs pagas).

Gera:
- Blog featured images (1200x630)
- YouTube thumbnails (1280x720)
- Pinterest pins (1000x1500)
- Instagram posts (1080x1080)
- Instagram stories (1080x1920)
- Social media cards
- Infográficos simples
"""

from __future__ import annotations

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

try:
    from PIL import Image, ImageDraw, ImageFont

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


# ── Paletas de Cores ──────────────────────────────────────────────

_COLOR_PALETTES: list[dict[str, Any]] = [
    {
        "name": "ocean",
        "bg": ["#0F2027", "#203A43", "#2C5364"],
        "accent": "#00D2FF",
        "text": "#FFFFFF",
    },
    {
        "name": "sunset",
        "bg": ["#232526", "#414345", "#8E0E00"],
        "accent": "#FF6B35",
        "text": "#FFFFFF",
    },
    {
        "name": "forest",
        "bg": ["#134E5E", "#134E5E", "#71B280"],
        "accent": "#71B280",
        "text": "#FFFFFF",
    },
    {
        "name": "lavender",
        "bg": ["#2C1B4D", "#4A2C6D", "#7B5EA7"],
        "accent": "#E8D5FF",
        "text": "#FFFFFF",
    },
    {
        "name": "corporate",
        "bg": ["#1a1a2e", "#16213e", "#0f3460"],
        "accent": "#e94560",
        "text": "#FFFFFF",
    },
    {
        "name": "warm",
        "bg": ["#2D1B00", "#4A2C00", "#7B5E00"],
        "accent": "#FFB347",
        "text": "#FFFFFF",
    },
    {
        "name": "dark",
        "bg": ["#000000", "#1A1A2E", "#16213E"],
        "accent": "#00FF88",
        "text": "#FFFFFF",
    },
    {
        "name": "clean",
        "bg": ["#FFFFFF", "#F5F5F5", "#E8E8E8"],
        "accent": "#2563EB",
        "text": "#1A1A2E",
    },
]


def _interpolate_color(c1: str, c2: str, ratio: float) -> tuple[int, int, int]:
    """Interpolate between two hex colors."""

    def _h(hx: str) -> tuple[int, int, int]:
        hx = hx.lstrip("#")
        return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)

    r1, g1, b1 = _h(c1)
    r2, g2, b2 = _h(c2)
    return (
        int(r1 + (r2 - r1) * ratio),
        int(g1 + (g2 - g1) * ratio),
        int(b1 + (b2 - b1) * ratio),
    )


def _hex_to_rgb(hx: str) -> tuple[int, int, int]:
    hx = hx.lstrip("#")
    return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)


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


class FreeImageGeneratorAgent(AgentBase):
    """Gera imagens gratuitas usando o melhor provider disponivel.

    Usa:
    - Pollinations.AI (AI images, zero dependencias) se disponivel
    - Pillow (composicao manual) como fallback

    Formatos suportados:
    - featured: 1200x630 (blog/Open Graph)
    - thumbnail: 1280x720 (YouTube)
    - pin: 1000x1500 (Pinterest)
    - instagram: 1080x1080 (feed quadrado)
    - social_card: 1200x630 (Twitter/LinkedIn card)
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("free_image_gen", **kwargs)
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._provider = None

    def _get_provider(self):
        if self._provider is None:
            from campaign_autopilot.media_providers import get_best_image_provider

            self._provider = get_best_image_provider()
        return self._provider

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )
        step_results = context.step_results

        if not HAS_PILLOW:
            return AgentResult(
                agent=self.name,
                status="error",
                output={
                    "error": "Pillow (PIL) nao instalado. Execute: pip install Pillow"
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="free_image_gen",
                    status="error",
                    started_at=started_at,
                    finished_at=utc_now_iso(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        provider = self._get_provider()
        use_ai = provider.name() != "pillow"

        # Collect content for image generation
        articles = self._get_articles(step_results)
        youtube_videos = self._get_youtube_videos(step_results)
        keywords = self._get_keywords(step_results, campaign)
        offers = self._get_offers(step_results)

        generated: list[dict[str, Any]] = []
        errors: list[str] = []

        # 1. Blog featured images
        for article in articles[:5]:
            try:
                title = article.get("title", niche)
                filename = "featured_" + article.get("slug", title)[:30] + ".png"
                if use_ai:
                    prompt = f"Professional blog featured image for: {title} - {niche}, modern design, clean, minimalist, high quality"
                    path = self._save_with_provider(
                        provider, prompt, 1200, 630, filename
                    )
                else:
                    path = self._generate_featured_image(title, niche, filename)
                generated.append(
                    {
                        "type": "blog_featured",
                        "filename": filename,
                        "path": str(path),
                        "title": title,
                        "width": 1200,
                        "height": 630,
                    }
                )
            except Exception as e:
                errors.append(f"featured: {e}")

        # 2. YouTube thumbnails
        for video in youtube_videos[:2]:
            try:
                title = video.get("title", niche)
                filename = "thumb_" + video.get("slug", title)[:20] + ".png"
                if use_ai:
                    prompt = f"Eye-catching YouTube thumbnail for: {title} - {niche}, bold text, vibrant colors, clickable, high contrast"
                    path = self._save_with_provider(
                        provider, prompt, 1280, 720, filename
                    )
                else:
                    path = self._generate_youtube_thumbnail(title, niche, filename)
                generated.append(
                    {
                        "type": "youtube_thumbnail",
                        "filename": filename,
                        "path": str(path),
                        "title": title,
                        "width": 1280,
                        "height": 720,
                    }
                )
            except Exception as e:
                errors.append(f"thumbnail: {e}")

        # 3. Pinterest pins
        for kw in keywords[:3]:
            try:
                k = kw.get("keyword", kw.get("term", niche))
                filename = "pin_" + k[:20] + ".png"
                if use_ai:
                    prompt = f"Beautiful Pinterest pin about: {k} - {niche}, vertical format, inspirational, elegant, social media"
                    path = self._save_with_provider(
                        provider, prompt, 1000, 1500, filename
                    )
                else:
                    path = self._generate_pinterest_pin(k, niche, filename)
                generated.append(
                    {
                        "type": "pinterest_pin",
                        "filename": filename,
                        "path": str(path),
                        "keyword": k,
                        "width": 1000,
                        "height": 1500,
                    }
                )
            except Exception as e:
                errors.append(f"pin: {e}")

        # 4. Instagram posts
        for kw in keywords[:3]:
            try:
                k = kw.get("keyword", kw.get("term", niche))
                filename = "ig_" + k[:15] + ".png"
                if use_ai:
                    prompt = f"Instagram square post about: {k} - {niche}, social media, engaging, modern design"
                    path = self._save_with_provider(
                        provider, prompt, 1080, 1080, filename
                    )
                else:
                    path = self._generate_instagram_post(k, niche, filename)
                generated.append(
                    {
                        "type": "instagram_post",
                        "filename": filename,
                        "path": str(path),
                        "keyword": k,
                        "width": 1080,
                        "height": 1080,
                    }
                )
            except Exception as e:
                errors.append(f"ig: {e}")

        # 5. Social media cards
        for article in articles[:3]:
            try:
                title = article.get("title", niche)
                filename = "social_" + article.get("slug", title)[:25] + ".png"
                if use_ai:
                    prompt = f"Professional social media sharing card for: {title} - {niche}, clean, modern, shareable"
                    path = self._save_with_provider(
                        provider, prompt, 1200, 630, filename
                    )
                else:
                    path = self._generate_social_card(title, niche, filename)
                generated.append(
                    {
                        "type": "social_card",
                        "filename": filename,
                        "path": str(path),
                        "title": title,
                        "width": 1200,
                        "height": 630,
                    }
                )
            except Exception as e:
                errors.append(f"social: {e}")

        output = {
            "status": "success",
            "images_generated": len(generated),
            "images": generated,
            "errors": errors,
            "output_directory": str(self.output_dir.absolute()),
            "provider": provider.name(),
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="free_image_gen",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(generated)} imagens via {provider.name()}. Erros: {len(errors)}"
            ],
            metadata={
                "images": len(generated),
                "errors": len(errors),
                "provider": provider.name(),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _save_with_provider(
        self, provider, prompt: str, width: int, height: int, filename: str
    ) -> Path:
        """Generate image using the given provider and save to disk."""
        img_bytes = provider.generate(prompt, width=width, height=height)
        path = self.output_dir / filename
        with open(path, "wb") as f:
            f.write(img_bytes)
        return path

    def _get_articles(self, sr: dict) -> list[dict]:
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        arts = out.get("articles", []) or out.get("generated_articles", [])
        if isinstance(arts, list):
            return arts
        wp = sr.get("wp_publisher", {})
        wout = wp.get("output", {}) if isinstance(wp, dict) else {}
        posts = wout.get("posts", [])
        if isinstance(posts, list):
            return posts
        return []

    def _get_youtube_videos(self, sr: dict) -> list[dict]:
        yt = sr.get("youtube_marketing", {})
        out = yt.get("output", {}) if isinstance(yt, dict) else {}
        return out.get("videos", []) if isinstance(out.get("videos"), list) else []

    def _get_keywords(self, sr: dict, campaign: dict) -> list[dict]:
        seo = sr.get("seo_research", {})
        out = seo.get("output", {}) if isinstance(seo, dict) else {}
        kws = out.get("top_opportunities", []) or out.get("keywords", [])
        if isinstance(kws, list) and kws:
            return kws
        return [
            {
                "keyword": str(campaign.get("objective", "marketing digital")),
                "volume": 1000,
            }
        ]

    def _get_offers(self, sr: dict) -> list[dict]:
        ol = sr.get("offer_lookup", {})
        out = ol.get("output", {}) if isinstance(ol, dict) else {}
        return (
            out.get("available_offers", [])
            if isinstance(out.get("available_offers"), list)
            else []
        )

    def _pick_palette(self) -> dict:
        return random.choice(_COLOR_PALETTES)

    def _draw_gradient(
        self, draw: ImageDraw, size: tuple, palette: dict, vertical: bool = True
    ) -> None:
        """Draw gradient background."""
        w, h = size
        colors = palette["bg"]
        steps = len(colors) - 1
        for i in range(h if vertical else w):
            step = min(
                int(i / (h / steps)) if vertical else int(i / (w / steps)), steps - 1
            )
            ratio = (
                ((i / (h / steps)) - step) if vertical else ((i / (w / steps)) - step)
            )
            ratio = min(ratio, 1.0)
            c = _interpolate_color(colors[step], colors[step + 1], ratio)
            if vertical:
                draw.line([(0, i), (w, i)], fill=c)
            else:
                draw.line([(i, 0), (i, h)], fill=c)

    def _add_decorative_elements(
        self, draw: ImageDraw, w: int, h: int, palette: dict
    ) -> None:
        """Add decorative shapes."""
        accent = _hex_to_rgb(palette["accent"])
        for _ in range(3):
            x = random.randint(0, w)
            y = random.randint(0, h)
            r = random.randint(20, 80)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(*accent, 30), outline=None)

    def _add_text(
        self,
        draw: ImageDraw,
        text: str,
        position: tuple,
        color: str,
        size: int = 40,
        max_width: int = 30,
        align: str = "center",
    ) -> int:
        """Add wrapped text to image. Returns total height used."""
        lines = _wrap_text(text, max_width)
        y_offset = position[1]
        rgb = _hex_to_rgb(color)
        for i, line in enumerate(lines):
            # Shadow for readability
            for dx, dy in [(2, 2), (-1, 1), (1, -1)]:
                draw.text((position[0] + dx, y_offset + dy), line, fill=(0, 0, 0, 100))
            draw.text(position, line, fill=rgb)
            y_offset += size + 5
        return y_offset - position[1]

    def _generate_featured_image(self, title: str, niche: str, filename: str) -> Path:
        """Generate blog featured image (1200x630)."""
        w, h = 1200, 630
        palette = self._pick_palette()
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        self._draw_gradient(draw, (w, h), palette)
        self._add_decorative_elements(draw, w, h, palette)

        # Tag
        self._add_text(
            draw,
            niche.upper(),
            (60, 40),
            palette["accent"],
            size=24,
            max_width=40,
            align="left",
        )

        # Title
        self._add_text(
            draw, title, (60, 120), palette["text"], size=52, max_width=25, align="left"
        )

        # Bottom bar
        draw.rectangle([(0, h - 8), (w, h)], fill=_hex_to_rgb(palette["accent"]))

        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)
        return path

    def _generate_youtube_thumbnail(
        self, title: str, niche: str, filename: str
    ) -> Path:
        """Generate YouTube thumbnail (1280x720)."""
        w, h = 1280, 720
        palette = self._pick_palette()
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        self._draw_gradient(draw, (w, h), palette, vertical=False)
        self._add_decorative_elements(draw, w, h, palette)

        # Big title
        self._add_text(
            draw,
            title.upper(),
            (w // 2, 180),
            palette["text"],
            size=64,
            max_width=18,
            align="center",
        )

        # Play button hint
        accent = _hex_to_rgb(palette["accent"])
        draw.ellipse([(w // 2 - 40, h - 160), (w // 2 + 40, h - 80)], fill=accent)
        draw.polygon(
            [(w // 2 - 15, h - 140), (w // 2 - 15, h - 100), (w // 2 + 20, h - 120)],
            fill=(255, 255, 255),
        )

        # Bottom accent bar
        draw.rectangle([(0, h - 10), (w, h)], fill=accent)

        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)
        return path

    def _generate_pinterest_pin(self, keyword: str, niche: str, filename: str) -> Path:
        """Generate Pinterest pin (1000x1500 - 2:3 ratio)."""
        w, h = 1000, 1500
        palette = self._pick_palette()
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        self._draw_gradient(draw, (w, h), palette)
        self._add_decorative_elements(draw, w, h, palette)

        # Vertical pin - text centered
        self._add_text(
            draw,
            keyword.upper(),
            (w // 2, 300),
            palette["text"],
            size=58,
            max_width=16,
            align="center",
        )

        # Decorative line
        accent = _hex_to_rgb(palette["accent"])
        for i in range(5):
            line_y = 600 + i * 8
            draw.line([(200, line_y), (800, line_y)], fill=accent, width=3)

        # Niche label at bottom
        self._add_text(
            draw,
            niche,
            (w // 2, 1200),
            palette["accent"],
            size=36,
            max_width=20,
            align="center",
        )

        # Save button hint
        draw.rectangle([(w // 2 - 80, h - 200), (w // 2 + 80, h - 150)], fill=accent)
        draw.text((w // 2, h - 180), "SALVAR", fill=(255, 255, 255))

        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)
        return path

    def _generate_instagram_post(self, keyword: str, niche: str, filename: str) -> Path:
        """Generate Instagram post (1080x1080 - square)."""
        w, h = 1080, 1080
        palette = self._pick_palette()
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        self._draw_gradient(draw, (w, h), palette)
        self._add_decorative_elements(draw, w, h, palette)

        # Keyword as main text
        self._add_text(
            draw,
            keyword.upper(),
            (w // 2, 300),
            palette["text"],
            size=60,
            max_width=18,
            align="center",
        )

        # Subtitle
        self._add_text(
            draw,
            f"✨ Dicas de {niche}",
            (w // 2, 650),
            palette["accent"],
            size=32,
            max_width=22,
            align="center",
        )

        # Bottom buttons
        accent = _hex_to_rgb(palette["accent"])
        draw.rectangle([(w // 2 - 120, h - 180), (w // 2 + 120, h - 120)], fill=accent)
        draw.text((w // 2, h - 155), "SALVE ESTE POST", fill=(255, 255, 255))

        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)
        return path

    def _generate_social_card(self, title: str, niche: str, filename: str) -> Path:
        """Generate social media card (1200x630)."""
        w, h = 1200, 630
        palette = self._pick_palette()
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        self._draw_gradient(draw, (w, h), palette, vertical=True)
        self._add_decorative_elements(draw, w, h, palette)

        # Title
        self._add_text(
            draw,
            title.upper(),
            (w // 2, 180),
            palette["text"],
            size=44,
            max_width=28,
            align="center",
        )

        # Niche tag at bottom
        accent = _hex_to_rgb(palette["accent"])
        draw.rectangle([(w // 2 - 120, h - 100), (w // 2 + 120, h - 60)], fill=accent)
        draw.text((w // 2, h - 82), niche.upper(), fill=(255, 255, 255))

        path = self.output_dir / filename
        img.save(str(path), "PNG", optimize=True)
        return path
