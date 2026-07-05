"""Image provider classes and functions."""

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
from .base import ImageProvider

class PillowImageProvider(ImageProvider):
    """Current Pillow-based image generation (compositing + effects)."""

    def name(self) -> str:
        return "pillow"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (width, height), self._pick_color(prompt))
        draw = ImageDraw.Draw(img)

        # Add gradient overlay
        for y in range(height):
            alpha = int(255 * (1 - y / height))
            overlay = Image.new("RGBA", (width, 1), (0, 0, 0, alpha // 3))
            img.paste(overlay, (0, y), overlay)

        # Add text
        lines = self._wrap_text(prompt, width)
        font_size = max(
            24, min(60, width // max(len(l) for l in lines) * 2 if lines else 40)
        )
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size
            )
        except (OSError, IOError):
            font = ImageFont.load_default()

        y_pos = height // 2 - (len(lines) * font_size) // 2
        for line in lines[:4]:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((width - tw) // 2, y_pos), line, fill="white", font=font)
            y_pos += font_size + 8

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    def _pick_color(self, prompt: str) -> tuple:
        palettes = [
            (15, 32, 39),
            (35, 67, 77),
            (19, 78, 94),
            (35, 37, 38),
            (65, 67, 69),
            (142, 14, 0),
            (19, 78, 94),
            (19, 78, 94),
            (113, 178, 128),
            (26, 27, 46),
            (22, 33, 62),
            (15, 52, 96),
        ]
        idx = hash(prompt) % len(palettes)
        return palettes[idx]

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        words = text.split()
        lines, current, current_len = [], [], 0
        for w in words:
            if current_len + len(w) > max_width // 10:
                lines.append(" ".join(current))
                current, current_len = [w], len(w)
            else:
                current.append(w)
                current_len += len(w) + 1
        if current:
            lines.append(" ".join(current))
        return lines
class FIAPIImageProvider(ImageProvider):
    """AI image generation via the local FIAPI service."""

    def name(self) -> str:
        return "fiapi"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        try:
            import urllib.request
            import json
            import base64

            api_url = os.environ.get("FIAPI_API_URL", "http://localhost:8787/v1/images/generate")
            auth_token = os.environ.get("FIAPI_AUTH_TOKEN", "test-token")

            # FIAPI expects JSON request with 'prompt'
            payload = {
                "prompt": prompt,
                "model": "@cf/black-forest-labs/flux-1-schnell"
            }
            body = json.dumps(payload).encode("utf-8")

            req = urllib.request.Request(api_url, data=body)
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {auth_token}")
            req.add_header("User-Agent", "Mozilla/5.0 (compatible; CampaignAutopilot/1.0)")

            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                if resp_data.get("success") and "data" in resp_data:
                    img_data = resp_data["data"].get("image", "")
                    if img_data:
                        if ";base64," in img_data:
                            img_data = img_data.split(";base64,")[1]
                        return base64.b64decode(img_data)
                
                raise ValueError("FIAPI response format error or unsuccessful")
        except Exception:
            # Fallback to Pollinations
            return PollinationsImageProvider().generate(prompt, width, height, negative_prompt)
class PollinationsImageProvider(ImageProvider):
    """Free AI image generation via Pollinations.AI - no API key required.

    Uses pollinations.ai free text-to-image API. No dependencies beyond
    stdlib (urllib). Generates high-quality images using Flux/SD models.
    Natural fallback to PillowImageProvider on failure.
    """

    def name(self) -> str:
        return "pollinations"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        try:
            import urllib.request

            encoded = quote_plus(prompt[:200])
            url = "https://image.pollinations.ai/prompt/" + encoded
            url += "?width=" + str(width) + "&height=" + str(height)
            url += "&nologo=true&seed=" + str(abs(hash(prompt)) % 100000)
            if negative_prompt:
                url += "&negative=" + quote_plus(negative_prompt[:100])

            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0 (compatible; LyzerLabs/1.0)")
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception:
            return PillowImageProvider().generate(prompt, width, height)
class ReplicateImageProvider(ImageProvider):
    """AI image generation via Replicate (free tier + REPLICATE_API_KEY)."""

    def name(self) -> str:
        return "replicate"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        import replicate

        api_key = os.environ.get("REPLICATE_API_KEY", "")
        if not api_key:
            return PillowImageProvider().generate(prompt, width, height)

        os.environ["REPLICATE_API_TOKEN"] = api_key
        try:
            # Use FLUX.1-schnell (fast, free on Replicate)
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt
                    or "low quality, blurry, distorted",
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                    "num_inference_steps": 4,
                    "guidance_scale": 3.0,
                },
            )
            if output and isinstance(output, list) and len(output) > 0:
                url = str(output[0])
                import urllib.request

                with urllib.request.urlopen(url, timeout=30) as resp:
                    return resp.read()
        except Exception:
            pass
        return PillowImageProvider().generate(prompt, width, height)
class DiffusersImageProvider(ImageProvider):
    """Local AI image generation via HuggingFace diffusers."""

    def name(self) -> str:
        return "diffusers"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        try:
            import torch
            from diffusers import StableDiffusionXLPipeline

            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            pipe = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16
                if torch.cuda.is_available()
                else torch.float32,
                variant="fp16" if torch.cuda.is_available() else None,
            )
            if torch.cuda.is_available():
                pipe.to("cuda")

            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt or "low quality, blurry",
                width=width,
                height=height,
                num_inference_steps=25,
            ).images[0]

            buf = io.BytesIO()
            image.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return PillowImageProvider().generate(prompt, width, height)
class DeepAIImageProvider(ImageProvider):
    """AI image generation via DeepAI free tier — sem chave necessaria para uso limitado.

    DeepAI oferece geracao de imagens via API com qualidade profissional.
    Free tier: ~20 imagens/dia sem cartao de credito.
    Para mais: https://deepai.org/machine-learning-model/text2img
    """

    def name(self) -> str:
        return "deepai"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        try:
            import urllib.request
            import json
            import urllib.parse

            api_key = os.environ.get("DEEPAI_API_KEY", "")
            data = {"text": prompt[:500]}
            if width and height:
                data["width"] = str(width)
                data["height"] = str(height)
            body = urllib.parse.urlencode(data).encode()
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            if api_key:
                headers["api-key"] = api_key
            req = urllib.request.Request(
                "https://api.deepai.org/api/text2img",
                data=body,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                image_url = result.get("output_url", "")
                if image_url:
                    with urllib.request.urlopen(image_url, timeout=30) as img_resp:
                        return img_resp.read()
        except Exception:
            pass
        return PillowImageProvider().generate(prompt, width, height)
class ProdiaImageProvider(ImageProvider):
    """AI image generation via Prodia — free tier, alta qualidade, sem chave.

    Prodia oferece Stable Diffusion XL, SD 1.5 e outros modelos gratuitamente.
    API key opcional (PRODIA_API_KEY) aumenta limite de requests.
    Sem key: ~10 imagens/dia.
    Website: https://prodia.com
    """

    def name(self) -> str:
        return "prodia"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        try:
            import urllib.request
            import json
            import time

            api_key = os.environ.get("PRODIA_API_KEY", "")
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["X-Prodia-Key"] = api_key

            body = json.dumps(
                {
                    "model": "sd_xl_base_1.0.safetensors",
                    "prompt": prompt[:500],
                    "negative_prompt": negative_prompt[:200] or "",
                    "steps": 25,
                    "cfg_scale": 7,
                    "width": width,
                    "height": height,
                    "sampler": "DPM++ 2M Karras",
                }
            ).encode()

            req = urllib.request.Request(
                "https://api.prodia.com/v1/sdxl/generate",
                data=body,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                job = json.loads(resp.read())
                job_id = job.get("job", "")
                if not job_id:
                    raise ValueError("No job ID returned")
                for _ in range(30):
                    time.sleep(2)
                    status_req = urllib.request.Request(
                        f"https://api.prodia.com/v1/job/{job_id}",
                        headers=headers,
                    )
                    with urllib.request.urlopen(status_req, timeout=10) as s_resp:
                        status = json.loads(s_resp.read())
                        if status.get("status") == "finished":
                            img_url = status.get("imageUrl", "")
                            if img_url:
                                with urllib.request.urlopen(
                                    img_url, timeout=30
                                ) as i_resp:
                                    return i_resp.read()
                            break
                        elif status.get("status") == "failed":
                            break
        except Exception:
            pass
        return PillowImageProvider().generate(prompt, width, height)
class OpenRouterImageProvider(ImageProvider):
    """Geracao de imagens via OpenRouter — usa sua chave existente.

    Aproveita a API key OPENROUTER_API_KEY ja configurada.
    Suporta modelos como FLUX, Stable Diffusion, DALL-E e outros
    através do roteamento do OpenRouter.
    Zero dependencias extras (stdlib + urllib).
    """

    def name(self) -> str:
        return "openrouter_image"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        import urllib.request

        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return PillowImageProvider().generate(prompt, width, height)

        models = [
            "black-forest-labs/flux-schnell",
            "stabilityai/stable-diffusion-xl-base-1.0",
        ]

        for model in models:
            try:
                body = json.dumps(
                    {
                        "model": model,
                        "prompt": prompt[:500],
                        "negative_prompt": negative_prompt[:200] or None,
                        "n": 1,
                        "size": f"{width}x{height}",
                    }
                ).encode()
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/images/generations",
                    data=body,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/campaign-autopilot",
                        "X-Title": "Campaign Autopilot",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read())
                    image_url = result.get("data", [{}])[0].get("url", "")
                    if image_url:
                        with urllib.request.urlopen(image_url, timeout=30) as img_resp:
                            return img_resp.read()
            except Exception:
                continue

        return PillowImageProvider().generate(prompt, width, height)
class HFFastImageProvider(ImageProvider):
    """Geracao de imagens via HuggingFace Inference API — free, sem chave.

    Usa o endpoint gratuito de inferencia do HuggingFace.
    Modelos: Stable Diffusion, FLUX, SDXL (todos gratuitos).
    HF_API_KEY opcional (aumenta rate limit).
    """

    MODELS = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "black-forest-labs/FLUX.1-dev",
        "runwayml/stable-diffusion-v1-5",
    ]

    def name(self) -> str:
        return "huggingface_image"

    def generate(
        self,
        prompt: str,
        width: int = 1200,
        height: int = 630,
        negative_prompt: str = "",
    ) -> bytes:
        import urllib.request

        api_key = os.environ.get("HF_API_KEY", "")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        body = json.dumps(
            {
                "inputs": prompt[:500],
                "parameters": {
                    "negative_prompt": negative_prompt[:200] or "low quality, blurry",
                    "width": width,
                    "height": height,
                    "num_inference_steps": 25,
                    "guidance_scale": 7.0,
                },
            }
        ).encode()

        for model in self.MODELS:
            try:
                req = urllib.request.Request(
                    f"https://api-inference.huggingface.co/models/{model}",
                    data=body,
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return resp.read()
            except Exception:
                continue

        return PillowImageProvider().generate(prompt, width, height)
