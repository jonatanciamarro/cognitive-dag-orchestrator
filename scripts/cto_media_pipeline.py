#!/usr/bin/env python3
"""CTO Media Pipeline — Gera prompts cinematográficos para imagem, vídeo e áudio.

Aplica o meta-prompt CTO Executive Director para construir prompts
estruturados de alta qualidade para todos os providers de mídia.

Uso:
    PYTHONPATH=src python3 scripts/cto_media_pipeline.py
    PYTHONPATH=src python3 scripts/cto_media_pipeline.py --niche "inteligencia artificial"
    PYTHONPATH=src python3 scripts/cto_media_pipeline.py --all
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.prompt_architect import MediaPromptArchitect, CTOMediaPromptIntegrator
from campaign_autopilot.quality_layers import OutputCritic
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box

console = Console()
architect = MediaPromptArchitect()
integrator = CTOMediaPromptIntegrator()
critic = OutputCritic(threshold=85)


def generate_cto_prompts(niche: str) -> None:
    """Generate CTO-graded prompts for all media types."""
    console.print(Panel.fit(f"[bold cyan]🎬 CTO Media Prompts: {niche}[/]", border_style="cyan"))

    # Image prompt
    image_data = architect.build_image_prompt(niche=niche, keyword=niche)
    image_prompt = image_data.get("prompt", "")
    image_quality = image_data.get("epistemic_quality", 0)

    # Video prompt
    video_data = architect.build_video_prompt(
        niche=niche,
        script_segments=[
            f"Introducao ao universo de {niche}",
            f"As 5 estrategias mais eficientes de {niche} em 2026",
            f"Resultados reais e proximos passos para dominar {niche}",
        ],
    )
    video_prompt = video_data.get("prompt", "")
    video_quality = video_data.get("epistemic_quality", 0)

    # Audio prompt
    audio_data = architect.build_audio_prompt(
        niche=niche,
        script_text=f"Guia completo sobre {niche}. Descubra como transformar seus resultados "
                    f"com as melhores estrategias de {niche}. Aprenda passo a passo.",
    )
    audio_prompt = audio_data.get("prompt", "")
    audio_quality = audio_data.get("epistemic_quality", 0)

    # Save
    stamp = int(time.time())
    out_dir = Path("output") / "cto_prompts"
    out_dir.mkdir(parents=True, exist_ok=True)

    for mtype, prompt, quality in [
        ("image", image_prompt, image_quality),
        ("video", video_prompt, video_quality),
        ("audio", audio_prompt, audio_quality),
    ]:
        (out_dir / f"{mtype}_{niche.lower().replace(' ', '_')}_{stamp}.md").write_text(
            f"# CTO Media Prompt — {mtype.upper()}\n"
            f"> Nicho: {niche}\n"
            f"> Qualidade CTO: {quality}/100\n"
            f"> Timestamp: {stamp}\n\n"
            f"{prompt}\n"
        )
        console.print(f"   [green]✅[/] {mtype.upper()}: {quality}/100")

    # Full JSON
    overview = {
        "niche": niche,
        "timestamp": stamp,
        "image": {"quality": image_quality, "file": f"image_{niche[:20]}_{stamp}.md"},
        "video": {"quality": video_quality, "file": f"video_{niche[:20]}_{stamp}.md"},
        "audio": {"quality": audio_quality, "file": f"audio_{niche[:20]}_{stamp}.md"},
    }
    (out_dir / f"overview_{niche.lower().replace(' ', '_')}_{stamp}.json").write_text(
        json.dumps(overview, indent=2)
    )

    # Table
    table = Table(box=box.ROUNDED)
    table.add_column("Mídia", style="cyan")
    table.add_column("Qualidade CTO", style="green")
    table.add_column("Palavras", style="yellow")
    table.add_column("Arquivo", style="blue")

    for mtype, prompt, quality in [
        ("Imagem", image_prompt, image_quality),
        ("Vídeo", video_prompt, video_quality),
        ("Áudio", audio_prompt, audio_quality),
    ]:
        wc = len(prompt.split())
        fname = f"{mtype}_{niche[:15]}_{stamp}.md"
        status = "✅" if quality >= 90 else "⚠️"
        table.add_row(mtype.upper(), f"{quality}/100 {status}", str(wc), fname)

    console.print(table)


def run_full_pipeline(niches: list[str]) -> None:
    """Generate CTO prompts for multiple niches and show comparison."""
    console.print(Panel.fit("[bold magenta]🏁 CTO MEDIA PROMPT ARCHITECT — FULL PIPELINE[/]", border_style="magenta"))
    
    results = []
    for niche in niches:
        image_data = architect.build_image_prompt(niche=niche, keyword=niche)
        video_data = architect.build_video_prompt(niche=niche)
        audio_data = architect.build_audio_prompt(niche=niche, script_text=f"Guia de {niche}")
        results.append({
            "niche": niche,
            "image": image_data.get("epistemic_quality", 0),
            "video": video_data.get("epistemic_quality", 0),
            "audio": audio_data.get("epistemic_quality", 0),
        })
        generate_cto_prompts(niche)

    # Comparison table
    table = Table(title="CTO Prompt Quality por Nicho", box=box.ROUNDED)
    table.add_column("Nicho", style="cyan")
    table.add_column("Imagem", style="green")
    table.add_column("Vídeo", style="blue")
    table.add_column("Áudio", style="yellow")
    table.add_column("Média", style="magenta")
    
    for r in results:
        avg = (r["image"] + r["video"] + r["audio"]) / 3
        table.add_row(
            r["niche"][:30],
            f"{r['image']}/100",
            f"{r['video']}/100",
            f"{r['audio']}/100",
            f"{avg:.1f}/100",
        )
    
    console.print(table)
    console.print(f"\n[bold green]✅ CTO Media Pipeline concluída para {len(niches)} nichos[/]")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="cto_media_pipeline")
    parser.add_argument("--niche", type=str, help="Nicho específico")
    parser.add_argument("--all", action="store_true", help="Rodar para todos os nichos")
    args = parser.parse_args()

    if args.niche:
        generate_cto_prompts(args.niche)
    elif args.all:
        run_full_pipeline([
            "marketing digital afiliados",
            "empreendedorismo digital",
            "inteligencia artificial",
            "financas pessoais",
            "renda extra online",
        ])
    else:
        run_full_pipeline(["marketing digital afiliados"])
