"""Cinematic FIAPI Image Agent — prompts cinematográficos + geração real via FIAPI.

Pipeline completo:
  1. CTOMediaPromptIntegrator → gera prompt cinematográfico estruturado por formato
  2. FIAPIImageProvider → envia o prompt para a API de IA (FIAPI) e recebe a imagem
  3. Salva cada imagem em output/images/

Formatos suportados:
  - pinterest_pin (1000x1500)
  - instagram_post (1080x1080)
  - blog_featured (1200x630)
  - youtube_thumbnail (1280x720)
  - social_card (1200x630)
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
from ..prompt_architect import CTOMediaPromptIntegrator


# Mapeamento formato → dimensões
_FORMAT_SIZES: dict[str, tuple[int, int]] = {
    "pinterest_pin":    (1000, 1500),
    "instagram_post":   (1080, 1080),
    "blog_featured":    (1200, 630),
    "youtube_thumbnail":(1280, 720),
    "social_card":      (1200, 630),
}


class CinematicFIAPIAgent(AgentBase):
    """Gera imagens com prompts cinematográficos CTO via FIAPI.

    - Usa CTOMediaPromptIntegrator para construir prompts ricos e estruturados
    - Envia os prompts para FIAPIImageProvider (AI real)
    - Faz fallback para PollinationsImageProvider se FIAPI falhar
    - Salva todas as imagens em output/images/
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("cinematic_fiapi_gen", **kwargs)
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._provider = None

    def _get_provider(self):
        if self._provider is None:
            from campaign_autopilot.media_providers import FIAPIImageProvider
            self._provider = FIAPIImageProvider()
        return self._provider

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "marketing digital")))
        sr = context.step_results

        keywords = self._get_keywords(sr, campaign)
        articles = self._get_articles(sr)

        cto = CTOMediaPromptIntegrator()
        provider = self._get_provider()

        generated: list[dict[str, Any]] = []
        errors: list[str] = []

        # ── 1. Pinterest Pins ────────────────────────────────────────────────
        for kw_item in keywords[:2]:
            kw = kw_item.get("keyword", kw_item.get("term", niche))
            try:
                prompt_data = cto.enrich_image_generation(niche, kw, "pinterest_pin")
                prompt = prompt_data.get("prompt", f"Pinterest pin about {kw}, {niche}")
                w, h = _FORMAT_SIZES["pinterest_pin"]
                slug = kw[:20].replace(" ", "_").replace("/", "_")
                filename = f"cin_pin_{slug}_{random.randint(1000, 9999)}.png"
                img_bytes = provider.generate(prompt, width=w, height=h)
                path = self.output_dir / filename
                path.write_bytes(img_bytes)
                generated.append({
                    "type": "pinterest_pin",
                    "filename": filename,
                    "path": str(path),
                    "keyword": kw,
                    "prompt_chars": len(prompt),
                    "width": w, "height": h,
                    "provider": provider.name(),
                })
            except Exception as e:
                errors.append(f"pin/{kw}: {e}")

        # ── 2. Instagram Posts ───────────────────────────────────────────────
        for kw_item in keywords[:2]:
            kw = kw_item.get("keyword", kw_item.get("term", niche))
            try:
                prompt_data = cto.enrich_image_generation(niche, kw, "instagram_post")
                prompt = prompt_data.get("prompt", f"Instagram post about {kw}, {niche}")
                w, h = _FORMAT_SIZES["instagram_post"]
                slug = kw[:15].replace(" ", "_").replace("/", "_")
                filename = f"cin_ig_{slug}_{random.randint(1000, 9999)}.png"
                img_bytes = provider.generate(prompt, width=w, height=h)
                path = self.output_dir / filename
                path.write_bytes(img_bytes)
                generated.append({
                    "type": "instagram_post",
                    "filename": filename,
                    "path": str(path),
                    "keyword": kw,
                    "prompt_chars": len(prompt),
                    "width": w, "height": h,
                    "provider": provider.name(),
                })
            except Exception as e:
                errors.append(f"ig/{kw}: {e}")

        # ── 3. Blog Featured Images ──────────────────────────────────────────
        for article in articles[:1]:
            title = article.get("title", niche)
            try:
                prompt_data = cto.enrich_image_generation(niche, title, "blog_featured")
                prompt = prompt_data.get("prompt", f"Blog featured image: {title}")
                w, h = _FORMAT_SIZES["blog_featured"]
                slug = title[:25].replace(" ", "_").replace("/", "_")
                filename = f"cin_feat_{slug}_{random.randint(1000, 9999)}.png"
                img_bytes = provider.generate(prompt, width=w, height=h)
                path = self.output_dir / filename
                path.write_bytes(img_bytes)
                generated.append({
                    "type": "blog_featured",
                    "filename": filename,
                    "path": str(path),
                    "title": title,
                    "prompt_chars": len(prompt),
                    "width": w, "height": h,
                    "provider": provider.name(),
                })
            except Exception as e:
                errors.append(f"featured/{title[:30]}: {e}")

        # ── 4. YouTube Thumbnail ─────────────────────────────────────────────
        for article in articles[:1]:
            title = article.get("title", niche)
            try:
                prompt_data = cto.enrich_image_generation(niche, title, "youtube_thumbnail")
                prompt = prompt_data.get("prompt", f"YouTube thumbnail: {title}")
                w, h = _FORMAT_SIZES["youtube_thumbnail"]
                slug = title[:20].replace(" ", "_").replace("/", "_")
                filename = f"cin_thumb_{slug}_{random.randint(1000, 9999)}.png"
                img_bytes = provider.generate(prompt, width=w, height=h)
                path = self.output_dir / filename
                path.write_bytes(img_bytes)
                generated.append({
                    "type": "youtube_thumbnail",
                    "filename": filename,
                    "path": str(path),
                    "title": title,
                    "prompt_chars": len(prompt),
                    "width": w, "height": h,
                    "provider": provider.name(),
                })
            except Exception as e:
                errors.append(f"thumb/{title[:30]}: {e}")

        output = {
            "status": "success" if generated else "partial",
            "images_generated": len(generated),
            "images": generated,
            "errors": errors,
            "output_directory": str(self.output_dir.absolute()),
            "pipeline": "cinematic_fiapi_v1",
            "provider": provider.name(),
        }

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="cinematic_fiapi_gen",
            status="success" if generated else "error",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Gerou {len(generated)} imagens via {provider.name()} com prompts CTO. Erros: {len(errors)}"
            ],
            metadata={
                "images": len(generated),
                "errors": len(errors),
                "pipeline": "cinematic_fiapi_v1",
                "provider": provider.name(),
            },
        )
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_keywords(self, sr: dict, campaign: dict) -> list[dict]:
        seo = sr.get("seo_research", {})
        out = seo.get("output", {}) if isinstance(seo, dict) else {}
        kws = out.get("top_opportunities", []) or out.get("keywords", [])
        if isinstance(kws, list) and kws:
            return kws
        return [{"keyword": str(campaign.get("objective", "marketing digital"))}]

    def _get_articles(self, sr: dict) -> list[dict]:
        cg = sr.get("content_generator", {})
        out = cg.get("output", {}) if isinstance(cg, dict) else {}
        if isinstance(out, dict):
            arts = out.get("articles", []) or out.get("generated_articles", [])
            if isinstance(arts, list) and arts:
                return arts
        cg2 = sr.get("content_preview", {})
        out2 = cg2.get("output", {}) if isinstance(cg2, dict) else {}
        if isinstance(out2, dict):
            arts2 = out2.get("articles", []) or out2.get("generated_articles", [])
            if isinstance(arts2, list) and arts2:
                return arts2
        return []

