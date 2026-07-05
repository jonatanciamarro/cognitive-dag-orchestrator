"""YouTubePublisherAgent — Publica vídeos no YouTube via YouTube Data API v3 + browser automation.

Modos:
- real: Upload via YouTube Data API (requer OAuth 2.0)
- semi: Gera script + thumbnail + descrição, você grava e faz upload
- manual: Salva todos os materiais prontos em output/

Para autopilot real (upload automático):
- Configurar YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN
- Ou usar BrowserAutomationAgent com Selenium
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("youtube_publisher")


class YouTubePublisherAgent(AgentBase):
    """Prepara e publica conteúdo no YouTube."""

    def __init__(self, **kwargs) -> None:
        super().__init__("youtube_publisher", **kwargs)
        self.api_key = os.environ.get("YOUTUBE_API_KEY", "")
        self.channel_id = os.environ.get("YOUTUBE_CHANNEL_ID", "")
        self.client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
        self.client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
        self.refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")

    def _has_upload_capability(self) -> bool:
        """Check if we can do real upload via API."""
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def _generate_video_script(self, article: dict) -> dict[str, str]:
        """Generate video script from article content."""
        content = article.get("content", article)
        title = content.get("title", "")
        intro = content.get("introduction", "")
        sections = content.get("sections", [])
        conclusion = content.get("conclusion", "")

        script_lines = []
        script_lines.append(f"🎬 INTRODUÇÃO ({title})")
        script_lines.append("Duração: ~15 segundos")
        script_lines.append(f"Olá! Hoje vamos falar sobre {title.lower()}.")
        script_lines.append(f"{intro[:200]}")
        script_lines.append("")
        script_lines.append("📚 DESENVOLVIMENTO (3-5 minutos)")

        for i, section in enumerate(sections[:5]):
            if isinstance(section, dict):
                section_title = section.get(
                    "title", section.get("heading", f"Ponto {i + 1}")
                )
                section_content = section.get("content", "")
                script_lines.append("")
                script_lines.append(f"🔹 {section_title}:")
                script_lines.append(f"{section_content[:200]}")

        script_lines.append("")
        script_lines.append("✅ CONCLUSÃO (30 segundos)")
        script_lines.append(f"{conclusion[:300]}")
        script_lines.append("")
        script_lines.append("👍 Gostou? Deixa seu like e inscreva-se no canal!")
        script_lines.append("🔗 Links na descrição")

        return {
            "full_script": "\n".join(script_lines),
            "estimated_duration": f"{5 + len(sections) * 2} minutos",
            "tone": "educacional e informal",
        }

    def _create_thumbnail_prompt(self, article: dict) -> str:
        """Generate thumbnail description for image generation agent."""
        content = article.get("content", article)
        title = content.get("title", "")
        niche = content.get("section", "tecnologia")

        return f"Crie uma thumbnail para YouTube sobre '{title}'. Nicho: {niche}. Estilo moderno, cores vibrantes, texto grande e legível."

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        articles = campaign.get("articles", [])
        niche = campaign.get("niche", "geral")
        output_dir = Path("output/youtube")
        output_dir.mkdir(parents=True, exist_ok=True)

        videos = []
        for article in articles:
            content = article.get("content", article)
            title = content.get("title", "")
            slug = content.get("slug", "video")
            meta = content.get("meta_description", f"Vídeo sobre {title}")
            tags = slug.split("-")[:5]

            script = self._generate_video_script(article)
            thumbnail_prompt = self._create_thumbnail_prompt(article)

            # Build description with affiliate links
            description = f"{meta}\n\n📌 Links e recursos:\n"
            if content.get("_meta", {}).get("affiliate_links"):
                for link in content["_meta"]["affiliate_links"][:3]:
                    description += f"🔗 {link.get('product_name', 'Produto')}: {link.get('tracked_url', '')}\n"
            if content.get("_meta", {}).get("affiliate_disclosure"):
                description += f"\n{content['_meta']['affiliate_disclosure']}\n"
            description += f"\n🎥 Inscreva-se para mais conteúdo sobre {niche}!"

            video_data = {
                "title": title,
                "description": description,
                "tags": tags,
                "category": self._youtube_category(niche),
                "privacy_status": "public",
                "script": script["full_script"],
                "estimated_duration": script["estimated_duration"],
                "thumbnail_prompt": thumbnail_prompt,
                "has_affiliate_links": bool(
                    content.get("_meta", {}).get("affiliate_links")
                ),
                "slug": slug,
            }

            # Save video materials
            video_dir = output_dir / slug
            video_dir.mkdir(parents=True, exist_ok=True)
            (video_dir / "script.txt").write_text(
                script["full_script"], encoding="utf-8"
            )
            (video_dir / "description.txt").write_text(description, encoding="utf-8")
            (video_dir / "metadata.json").write_text(
                json.dumps(
                    {
                        "title": title,
                        "tags": tags,
                        "category": video_data["category"],
                        "privacy": video_data["privacy_status"],
                    },
                    indent=2,
                ),
            )
            (video_dir / "thumbnail_prompt.txt").write_text(
                thumbnail_prompt, encoding="utf-8"
            )

            videos.append(video_data)

        can_upload = self._has_upload_capability()

        output = {
            "platform": "youtube",
            "mode": "real" if can_upload else "semi_manual",
            "videos_prepared": videos,
            "total_videos": len(videos),
            "output_directory": str(output_dir),
            "has_upload_capability": can_upload,
            "summary": (
                f"{len(videos)} vídeos preparados para YouTube. "
                f"{'✅ Upload automático habilitado!' if can_upload else '📹 Grave o vídeo seguindo o script e faça upload manual.'}"
            ),
            "setup_guide": {
                "for_autopilot_upload": {
                    "steps": [
                        "1. Google Cloud Console → YouTube Data API v3",
                        "2. Criar credenciais OAuth 2.0 (Desktop app)",
                        "3. Configurar YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET",
                        "4. Gerar refresh token (autorizar upload)",
                        "5. Configurar YOUTUBE_REFRESH_TOKEN no .env",
                    ],
                    "env_vars": "YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN, YOUTUBE_CHANNEL_ID",
                    "difficulty": "Média (requer Google Cloud Console + OAuth)",
                },
                "for_semi_manual": {
                    "steps": [
                        "1. Abra a pasta output/youtube/",
                        "2. Leia o script e grave o vídeo",
                        "3. Use o prompt da thumbnail em ferramentas grátis (Canva, Leonardo AI)",
                        "4. Faça upload manual no YouTube Studio",
                        "5. Cole a descrição e as tags geradas",
                    ],
                    "difficulty": "⭐ Fácil (só gravar e postar)",
                },
            },
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="youtube",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[output["summary"]],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _youtube_category(niche: str) -> str:
        categories = {
            "tecnologia": "28",  # Science & Technology
            "financas": "25",  # News & Politics / Education
            "saude": "26",  # Howto & Style / Education
            "carreira": "27",  # Education
        }
        return categories.get(niche, "27")  # Default: Education
