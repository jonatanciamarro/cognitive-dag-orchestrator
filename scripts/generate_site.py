#!/usr/bin/env python3
"""🎨 Gerador de Site — Usa Open Design / Product Forge para gerar site completo.

Gera landing pages, páginas de site, emails e dashboards usando o
Design System Lyzer Labs com design tokens consistentes.

Uso:
    python scripts/generate_site.py                                      # Landing page (interativo)
    python scripts/generate_site.py --title "Meu Produto" --niche "tecnologia"
    python scripts/generate_site.py --type email --title "Newsletter"
    python scripts/generate_site.py --type dashboard
    python scripts/generate_site.py --all                                # Gera tudo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def generate_landing_page(
    title: str,
    niche: str = "marketing digital",
    product_name: str = "",
    price: float = 97.0,
    output_dir: str = "output/ui_design",
) -> dict:
    """Generate a landing page using the Open Design system."""
    from src.campaign_autopilot.agents.ui_design import UIDesignAgent
    from src.campaign_autopilot.agents.base import CampaignContext

    agent = UIDesignAgent()
    context = CampaignContext(
        campaign={
            "action": "landing_page",
            "title": title,
            "niche": niche,
            "product_name": product_name or title,
            "price": price,
            "original_price": price * 2,
            "cta_text": f"Comprar {product_name or title}",
            "cta_link": "#",
            "output_dir": output_dir,
        }
    )
    result = agent.run(context)
    return result.to_dict()


def generate_email(
    title: str, niche: str = "marketing digital", output_dir: str = "output/ui_design"
) -> dict:
    """Generate an email template using the Open Design system."""
    from src.campaign_autopilot.agents.ui_design import UIDesignAgent
    from src.campaign_autopilot.agents.base import CampaignContext

    agent = UIDesignAgent()
    context = CampaignContext(
        campaign={
            "action": "email",
            "title": title,
            "subtitle": f"Ofertas exclusivas de {niche} para você",
            "content_html": f"<p>Confira as melhores ofertas de {niche} selecionadas especialmente para você.</p>",
            "cta_text": "Ver Ofertas",
            "cta_link": "#",
            "output_dir": output_dir,
        }
    )
    result = agent.run(context)
    return result.to_dict()


def generate_dashboard(
    title: str = "Campaign Dashboard", output_dir: str = "output/ui_design"
) -> dict:
    """Generate a dashboard HTML using the Open Design system."""
    from src.campaign_autopilot.agents.ui_design import UIDesignAgent
    from src.campaign_autopilot.agents.base import CampaignContext

    agent = UIDesignAgent()
    context = CampaignContext(
        campaign={
            "action": "dashboard",
            "title": title,
            "metrics": [
                {"label": "Visitantes", "value": "12,847", "change": "+12%"},
                {"label": "Conversões", "value": "847", "change": "+8%"},
                {"label": "Receita", "value": "R$ 47.290", "change": "+23%"},
                {"label": "Comissões", "value": "R$ 8.490", "change": "+15%"},
            ],
            "charts": [],
            "output_dir": output_dir,
        }
    )
    result = agent.run(context)
    return result.to_dict()


def main():
    ap = argparse.ArgumentParser(description="🎨 Gerador de Site — Open Design")
    ap.add_argument(
        "--type", choices=["landing", "email", "dashboard"], default="landing"
    )
    ap.add_argument("--title", default="", help="Título do artefato")
    ap.add_argument("--niche", default="marketing digital", help="Nicho")
    ap.add_argument("--product", default="", help="Nome do produto")
    ap.add_argument("--price", type=float, default=97.0, help="Preço do produto")
    ap.add_argument("--output", default="output/ui_design", help="Diretório de saída")
    ap.add_argument("--all", action="store_true", help="Gera todos os tipos")
    args = ap.parse_args()

    output_dir = args.output
    results = []

    if args.all:
        console.print(
            Panel("[bold]🎨 Gerando todos os artefatos de design[/bold]", box=box.HEAVY)
        )
        results.append(
            generate_landing_page(
                "Landing Page Principal",
                "marketing digital",
                "Curso Completo",
                97,
                output_dir,
            )
        )
        results.append(
            generate_email("Newsletter Semanal", "marketing digital", output_dir)
        )
        results.append(generate_dashboard("Campaign Dashboard", output_dir))
    else:
        title = args.title or input("Título: ") or "Minha Oferta"

        if args.type == "landing":
            niche = (
                args.niche
                or input("Nicho [marketing digital]: ")
                or "marketing digital"
            )
            product = args.product or title
            console.print(f"\n[bold]🎨 Gerando landing page:[/bold] {title}")
            results.append(
                generate_landing_page(title, niche, product, args.price, output_dir)
            )

        elif args.type == "email":
            console.print(f"\n[bold]📧 Gerando email:[/bold] {title}")
            results.append(generate_email(title, args.niche, output_dir))

        elif args.type == "dashboard":
            console.print(f"\n[bold]📊 Gerando dashboard:[/bold] {title}")
            results.append(generate_dashboard(title, output_dir))

    # Show results
    table = Table(title="📊 Artefatos Gerados", box=box.ROUNDED)
    table.add_column("Tipo", style="cyan")
    table.add_column("Arquivo", style="green")
    table.add_column("Status", style="yellow")

    for r in results:
        out = r.get("output", {})
        file_path = out.get("file_path", "")
        status = r.get("status", "error")
        exists = "✅" if file_path and Path(file_path).exists() else "❌"
        table.add_row(
            r.get("agent", "?"),
            file_path or "—",
            f"{exists} {status}",
        )

    console.print(table)
    if results:
        console.print(f"\n[green]✅ Artefatos salvos em: {output_dir}/[/green]")


if __name__ == "__main__":
    main()
