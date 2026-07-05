#!/usr/bin/env python3
"""📦 Enriquecer Banco de Produtos — Gera produtos de afiliado reais via LLM.

Uso:
    python scripts/enrich_products.py                          # Gerar catálogo completo
    python scripts/enrich_products.py --niche "saude"          # Nicho específico
    python scripts/enrich_products.py --count 50               # Quantidade de produtos
    python scripts/enrich_products.py --output configs/products.json  # Salvar em arquivo
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# ── Nichos com alta demanda no Brasil ────────────────────────

NICHES = [
    "tecnologia",
    "smartphones",
    "informatica",
    "games",
    "fitness",
    "saude",
    "beleza",
    "moda",
    "casa",
    "cozinha",
    "ferramentas",
    "automotivo",
    "brinquedos",
    "livros",
    "escritorio",
    "pet shop",
    "jardim",
    "esporte",
    "bebe",
    "instrumentos musicais",
]

PLATFORMS = ["Mercado Livre", "Shopee", "Amazon Brasil", "Magazine Luiza"]

CATEGORIES = {
    "tecnologia": "eletronicos",
    "smartphones": "celulares",
    "informatica": "computadores",
    "games": "jogos",
    "fitness": "esportes",
    "saude": "saude",
    "beleza": "beleza",
    "moda": "roupas",
    "casa": "casa",
    "cozinha": "casa",
    "ferramentas": "ferramentas",
    "automotivo": "automotivo",
    "brinquedos": "brinquedos",
    "livros": "livros",
    "escritorio": "escritorio",
    "pet shop": "pets",
    "jardim": "jardim",
    "esporte": "esportes",
    "bebe": "bebe",
    "instrumentos musicais": "musica",
}


def generate_products_for_niche(niche: str, count: int = 10) -> list[dict]:
    """Generate products for a niche using the LLM provider chain."""
    from src.campaign_autopilot.free_llm_providers import (
        get_llm_manager,
        _load_env_file,
    )

    _load_env_file()
    manager = get_llm_manager()

    category = CATEGORIES.get(niche, niche)
    platform = PLATFORMS[list(NICHES).index(niche) % len(PLATFORMS)]

    prompt = f"""Generate a JSON array of {count} real physical products for the "{niche}" niche in Brazil.
Include realistic Brazilian prices (R$), categories, and platform names.
Each product must be a real product that exists in the Brazilian market.

Return ONLY valid JSON array:
[
  {{
    "product_name": "Product Name",
    "price_brl": 129.90,
    "commission_pct": 5,
    "platform": "{platform}",
    "category": "{category}",
    "niche": "{niche}",
    "keywords": ["word1", "word2", "word3"]
  }}
]"""

    for attempt in range(3):
        result = manager.generate(prompt, max_tokens=3000)
        if result:
            # Try to extract JSON from the response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            result = result.strip()
            try:
                products = json.loads(result)
                if isinstance(products, list) and len(products) > 0:
                    return products
            except json.JSONDecodeError:
                pass
        time.sleep(1)
    return []


def main():
    ap = argparse.ArgumentParser(description="📦 Enriquecer Banco de Produtos")
    ap.add_argument("--niche", help="Nicho específico (default: todos)")
    ap.add_argument(
        "--count", type=int, default=10, help="Produtos por nicho (default: 10)"
    )
    ap.add_argument(
        "--output", default="configs/generated_products.json", help="Arquivo de saída"
    )
    args = ap.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    niches = [args.niche] if args.niche else NICHES
    all_products = []
    total = len(niches) * args.count

    console.print(
        Panel(
            f"[bold]📦 Gerando Catálogo de Produtos[/bold]\n"
            f"  Nichos: {len(niches)} | Produtos/nicho: {args.count} | Total: ~{total}",
            box=box.HEAVY,
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[green]Gerando produtos...", total=len(niches))
        for niche in niches:
            progress.update(task, description=f"[green]{niche}...")
            products = generate_products_for_niche(niche, args.count)
            if products:
                all_products.extend(products)
                console.print(f"  ✅ {niche}: {len(products)} produtos")
            else:
                console.print(f"  ⚠️  {niche}: falhou (LLM indisponível)")
            progress.update(task, advance=1)

    # Save to file
    output_path.write_text(json.dumps(all_products, indent=2, ensure_ascii=False))

    # Summary table
    if all_products:
        table = Table(
            title=f"📊 Catálogo Gerado: {len(all_products)} produtos", box=box.ROUNDED
        )
        table.add_column("Plataforma", style="cyan")
        table.add_column("Qtd", style="green")

        by_platform = {}
        for p in all_products:
            plat = p.get("platform", "Unknown")
            by_platform[plat] = by_platform.get(plat, 0) + 1

        for plat, count in sorted(by_platform.items(), key=lambda x: -x[1]):
            table.add_row(plat, str(count))

        console.print(table)
        console.print(f"\n[green]✅ Salvo em: {output_path}[/green]")
    else:
        console.print(
            "\n[yellow]⚠️ Nenhum produto gerado. LLM pode estar offline.[/yellow]"
        )
        console.print("[dim]Execute com chaves de API válidas no .env[/dim]")


if __name__ == "__main__":
    main()
