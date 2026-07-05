#!/usr/bin/env python3
"""🎬 Pipeline Completa de Mídia — Executa o workflow full_media_pipeline.

Gera:
  - Artigo SEO
  - Imagens (Pollinations.ai)
  - Áudio (edge-tts/gTTS)
  - Landing page (Open Design)
  - Site estático

Uso:
    python scripts/run_full_pipeline.py
    python scripts/run_full_pipeline.py --niche "tecnologia"
    python scripts/run_full_pipeline.py --workflow-only
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.live import Live

console = Console()


def run_pipeline(
    niche: str = "marketing digital",
    workflow: str = "workflows/full_media_workflow.json",
):
    """Execute the full media pipeline."""
    from src.campaign_autopilot.cli import run_workflow
    from src.campaign_autopilot.free_llm_providers import _load_env_file

    _load_env_file()

    console.print(
        Panel(
            f"[bold]🎬 Pipeline Completa de Mídia[/bold]\n"
            f"  Nicho: {niche}\n"
            f"  Workflow: {workflow}\n"
            f"  Início: {datetime.now().strftime('%H:%M:%S')}",
            box=box.HEAVY,
        )
    )

    steps_table = Table(box=box.SIMPLE)
    steps_table.add_column("Step", style="cyan")
    steps_table.add_column("Status", style="green")
    steps_table.add_column("Detalhes", style="yellow")

    steps_table.add_row("1. SEO Research", "⏳", "Pesquisando palavras-chave...")
    steps_table.add_row("2. Content Generator", "⏳", "Gerando artigo...")
    steps_table.add_row("3. Image Generation", "⏳", "Pollinations.ai...")
    steps_table.add_row("4. Audio Production", "⏳", "edge-tts/gTTS...")
    steps_table.add_row("5. Media Pipeline", "⏳", "Orquestrando...")
    steps_table.add_row("6. UI Design", "⏳", "Open Design...")
    steps_table.add_row("7. Site Deploy", "⏳", "Publicando...")

    with Live(steps_table, console=console, refresh_per_second=4):
        try:
            result = run_workflow(
                context_path="examples/affiliate_context.json",
                workflow_path=workflow,
                db_path=".state/pipeline.db",
            )
            steps_table.rows[0].cells[1].text = "✅"
            steps_table.rows[0].cells[2].text = "Concluído"
        except Exception as e:
            console.print(f"\n[red]❌ Pipeline error: {e}[/red]")
            return None

    return result


def main():
    ap = argparse.ArgumentParser(description="🎬 Pipeline Completa de Mídia")
    ap.add_argument(
        "--niche", default="marketing digital", help="Nicho para gerar conteúdo"
    )
    ap.add_argument(
        "--workflow", default="workflows/full_media_workflow.json", help="Workflow JSON"
    )
    args = ap.parse_args()

    result = run_pipeline(args.niche, args.workflow)

    if result:
        console.print("\n[green]✅ Pipeline completa executada![/green]")
        console.print(
            Panel(
                "[bold]📁 Artefatos gerados em:[/bold]\n"
                "  output/ui_design/  — Landing pages\n"
                "  output/media/      — Imagens e áudio\n"
                "  site/              — Site estático completo",
                box=box.SIMPLE,
            )
        )
    else:
        console.print("\n[yellow]⚠️ Pipeline não foi executada completamente.[/yellow]")


if __name__ == "__main__":
    main()
