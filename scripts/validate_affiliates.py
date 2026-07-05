#!/usr/bin/env python3
"""🔗 Validador de Links de Afiliado — Verifica se suas configurações estão corretas.

Uso:
    python3 scripts/validate_affiliates.py          # Validar tudo
    python3 scripts/validate_affiliates.py --links  # Só validar links
    python3 scripts/validate_affiliates.py --env    # Só validar .env
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


def ok(msg: str) -> None:
    console.print(f"  [green]✅[/green] {msg}")


def warn(msg: str) -> None:
    console.print(f"  [yellow]⚠️[/yellow] {msg}")


def err(msg: str) -> None:
    console.print(f"  [red]❌[/red] {msg}")


def info(msg: str) -> None:
    console.print(f"  [blue]ℹ️[/blue] {msg}")


def validate_env() -> list[str]:
    """Validate .env file for affiliate credentials."""
    errors = []
    env_path = Path(".env")

    if not env_path.exists():
        err("Arquivo .env não encontrado!")
        return ["NO_ENV_FILE"]

    content = env_path.read_text()
    info("Arquivo .env encontrado ✅")

    checks = {
        "HOTMART_AFFILIATE_ID": "Hotmart",
        "AMAZON_TRACKING_ID": "Amazon Associates",
        "AMAZON_ACCESS_KEY": "Amazon API Key",
    }

    for var, label in checks.items():
        match = re.search(rf"^{var}=(.+)$", content, re.MULTILINE)
        if match:
            value = match.group(1).strip().strip('"').strip("'")
            if value and value != "seu_codigo" and not value.startswith("${"):
                ok(f"{label} ({var}) configurado: {value[:15]}...")
            else:
                warn(f"{label} ({var}) — valor parece ser placeholder")
                errors.append(f"{var}=placeholder")
        else:
            warn(f"{label} ({var}) — não encontrado no .env")
            errors.append(f"{var}=missing")

    return errors


def make_link(platform: str, affiliate_id: str | None) -> tuple[str, bool]:
    """Generate marketplace link and validity."""
    if not affiliate_id or affiliate_id == "seu_id":
        return "❌ ID não configurado", False

    links = {
        "hotmart": f"https://www.hotmart.com/page/{affiliate_id}",
        "kiwify": f"https://kiwify.com.br/{affiliate_id}",
        "eduzz": f"https://eduzz.com/{affiliate_id}",
        "monetizze": f"https://monetizze.com.br/{affiliate_id}",
        "amazon": f"https://amzn.to/{affiliate_id}",
        "mercadolivre": f"https://mercadolivre.com.br/{affiliate_id}",
        "shopee": f"https://shopee.com.br/{affiliate_id}",
        "shein": f"https://shein.com/{affiliate_id}",
    }

    link = links.get(platform)
    if not link:
        return f"❌ Plataforma {platform} desconhecida", False
    return link, True


def validate_links() -> dict[str, Any]:
    """Validate affiliate links from .env"""
    env_path = Path(".env")
    if not env_path.exists():
        return {"error": ".env não encontrado"}

    content = env_path.read_text()
    platforms = {
        "hotmart": ("HOTMART_AFFILIATE_ID", "Hotmart"),
        "kiwify": ("KIWIFY_AFFILIATE_ID", "Kiwify"),
        "eduzz": ("EDUZZ_AFFILIATE_ID", "Eduzz"),
        "monetizze": ("MONETIZZE_AFFILIATE_ID", "Monetizze"),
        "mercadolivre": ("MERCADOLIVRE_AFFILIATE_ID", "Mercado Livre"),
        "shopee": ("SHOPEE_AFFILIATE_ID", "Shopee"),
        "shein": ("SHEIN_AFFILIATE_ID", "SheIn"),
        "aliexpress": ("ALIEXPRESS_AFFILIATE_ID", "AliExpress"),
        "amazon": ("AMAZON_ASSOCIATES_TAG", "Amazon"),
    }

    results = {}
    for plat, (var, name) in platforms.items():
        match = re.search(rf"^{var}=(.+)$", content, re.MULTILINE)
        affiliate_id = match.group(1).strip().strip('"').strip("'") if match else None
        if affiliate_id and affiliate_id not in ("", "seu_id", "seu_codigo"):
            link, valid = make_link(plat, affiliate_id)
            results[plat] = {
                "nome": name,
                "id": affiliate_id,
                "link": link,
                "valido": valid,
            }
            if valid:
                ok(f"{name}: {link}")
            else:
                err(f"{name}: {link}")
        else:
            results[plat] = {
                "nome": name,
                "id": None,
                "link": "❌ Não configurado",
                "valido": False,
            }
            warn(f"{name}: não configurado")

    return results


def validate_all():
    """Validação completa: .env + links + dicas."""
    console.print(
        Panel(
            "[bold]🔗 Validação de Afiliados — Campaign Autopilot[/bold]", box=box.HEAVY
        )
    )

    # .env check
    console.print("\n[bold]📁 Verificação do .env[/bold]")
    env_errors = validate_env()

    # Links
    console.print("\n[bold]🔗 Verificação de Links[/bold]")
    links = validate_links()

    # Summary
    total = len(links)
    validos = sum(1 for v in links.values() if v.get("valido"))
    console.print(f"\n[bold]📊 Resumo: {validos}/{total} links válidos[/bold]")

    if validos < total:
        console.print(
            Panel(
                "[bold yellow]⚠️ Configure todos os IDs de afiliado no .env:[/bold yellow]\n"
                "    HOTMART_AFFILIATE_ID=seu_id\n"
                "    KIWIFY_AFFILIATE_ID=seu_id\n"
                "    EDUZZ_AFFILIATE_ID=seu_id\n"
                "    MONETIZZE_AFFILIATE_ID=seu_id\n"
                "    MERCADOLIVRE_AFFILIATE_ID=seu_id\n"
                "    SHOPEE_AFFILIATE_ID=seu_id\n"
                "    SHEIN_AFFILIATE_ID=seu_id\n"
                "    AMAZON_ASSOCIATES_TAG=seu_tag",
                title="💡 Dica",
                box=box.SIMPLE,
            )
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="🔗 Validador de Afiliados")
    parser.add_argument("--links", action="store_true", help="Só validar links")
    parser.add_argument("--env", action="store_true", help="Só validar .env")
    args = parser.parse_args()

    if args.env:
        validate_env()
    elif args.links:
        validate_links()
    else:
        validate_all()


if __name__ == "__main__":
    main()
