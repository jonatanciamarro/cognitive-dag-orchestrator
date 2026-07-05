"""CTO Media Prompt Agent — Aplica o meta-prompt CTO para gerar prompts de mídia.

Integra o MediaPromptArchitect nos cinemas de geração de imagem, vídeo e áudio.
Gera prompts cinematográficos validados pelo framework CTO para cada provider.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .base import AgentBase, AgentResult, CampaignContext, utc_now_iso


class CTOMediaPromptAgent(AgentBase):
    """CTO-graded media prompt generator for all providers.

    Para cada pedido de midia, aplica:
    PHASE 0  → Validacao do input executivo
    PHASE 0.5 → Revisao epistemica do nicho/audiencia
    PHASE 1  → Classificacao tecnica (tipo, formato, resolucao)
    PHASE 2  → Modelagem de dominio (conceitos visuais/auditivos)
    PHASE 3  → Design arquitetural do prompt cinematografico
    PHASE 4  → Revisao de qualidade do prompt
    PHASE 5  → Atribuicao ao provider especifico
    """

    def __init__(self, name: str = "cto_media_prompt"):
        super().__init__(name)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign or {}
        niche = str(campaign.get("niche", campaign.get("objective", "marketing digital")))
        keyword = str(campaign.get("keyword", niche))
        script_text = str(campaign.get("script", campaign.get("objective", f"Guia completo de {niche}")))

        try:
            from ..prompt_architect import MediaPromptArchitect

            architect = MediaPromptArchitect()

            # Generate prompts for all media types
            image_prompt = architect.build_image_prompt(
                niche=niche, keyword=keyword, format_type="blog_featured",
            )
            video_prompt = architect.build_video_prompt(
                niche=niche, format_type="slideshow",
                script_segments=[
                    f"Introducao ao {niche}",
                    f"Principais estrategias de {keyword}",
                    f"Resultados e proximos passos em {niche}",
                ],
            )
            audio_prompt = architect.build_audio_prompt(
                niche=niche, format_type="voiceover",
                script_text=script_text,
            )

            # Save prompts to output
            output_dir = Path("output") / "cto_prompts"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = int(time.time())

            prompts = {
                "niche": niche,
                "keyword": keyword,
                "timestamp": timestamp,
                "image": image_prompt,
                "video": video_prompt,
                "audio": audio_prompt,
                "prompt_quality": {
                    "image": image_prompt.get("epistemic_quality", 0),
                    "video": video_prompt.get("epistemic_quality", 0),
                    "audio": audio_prompt.get("epistemic_quality", 0),
                },
            }

            # Save as JSON
            (output_dir / f"prompts_{niche.lower().replace(' ', '_')}_{timestamp}.json").write_text(
                json.dumps(prompts, indent=2, default=str)
            )

            # Save individual prompts as .md for readability
            for mtype in ("image", "video", "audio"):
                pdata = prompts[mtype]
                prompt_text = pdata.get("prompt", "")
                if prompt_text:
                    (output_dir / f"{mtype}_{niche.lower().replace(' ', '_')}_{timestamp}.md").write_text(
                        f"# CTO Media Prompt — {mtype.upper()}\n"
                        f"> Niche: {niche} | Keyword: {keyword}\n"
                        f"> Qualidade do prompt: {pdata.get('epistemic_quality', 0)}/100\n\n"
                        f"{prompt_text}\n"
                    )

            output = {
                "status": "success",
                "niche": niche,
                "prompts_generated": 3,
                "image_prompt_quality": image_prompt.get("epistemic_quality", 0),
                "video_prompt_quality": video_prompt.get("epistemic_quality", 0),
                "audio_prompt_quality": audio_prompt.get("epistemic_quality", 0),
                "output_dir": str(output_dir),
                "image_prompt": image_prompt.get("prompt", ""),
                "video_prompt": video_prompt.get("prompt", ""),
                "audio_prompt": audio_prompt.get("prompt", ""),
            }

        except Exception as e:
            output = {"status": "error", "error": str(e)}

        finished_at = utc_now_iso()
        return AgentResult(
            agent=self.name,
            status=output.get("status", "error"),
            output=output,
        )
