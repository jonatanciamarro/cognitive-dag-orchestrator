#!/usr/bin/env python3
"""Assistente interativo para coleta de links Hotmart.

Uso:
    python scripts/hotmart_wizard.py                          # Modo interativo
    python scripts/hotmart_wizard.py --add-link               # Adicionar link manualmente
    python scripts/hotmart_wizard.py --validate               # Validar links existentes
    python scripts/hotmart_wizard.py --status                 # Ver status da colecao
    python scripts/hotmart_wizard.py --batch file.json        # Importar lote de links
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.agents.hotmart import (
    HotmartLinkManagerAgent,
    ProductMatcherAgent,
    AffiliateConfigUpdaterAgent,
    LinkValidatorAgent,
)
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.logging_utils import StructuredLogger

log = StructuredLogger("hotmart_wizard")

NICHES = ["tecnologia", "financas", "saude", "carreira"]
NICHE_LABELS = {
    "tecnologia": "💻 Tecnologia",
    "financas": "💰 Financas",
    "saude": "🏥 Saude",
    "carreira": "🚀 Carreira",
}
CONFIG_PATH = Path("configs/affiliate_offers.json")


def print_header():
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   HOTMART WIZARD — Coleta de Links          ║")
    print("╠══════════════════════════════════════════════╣")
    print("║  1. Liste os produtos no Hotmart            ║")
    print("║  2. Pegue o link de afiliado                ║")
    print("║  3. Cole aqui no assistente                 ║")
    print("║  4. O sistema configura automaticamente     ║")
    print("╚══════════════════════════════════════════════╝")
    print()


def add_link_interactive():
    """Modo interativo: usuario cola os links manualmente."""
    print_header()

    manager = HotmartLinkManagerAgent()
    matcher = ProductMatcherAgent()
    updater = AffiliateConfigUpdaterAgent()

    print("Escolha o nicho do produto:")
    for key, label in NICHE_LABELS.items():
        print(f"  {label}")
    niche = input("Nicho: ").strip().lower()

    if niche not in NICHES:
        print(f"Nicho invalido. Use um dos: {', '.join(NICHES)}")
        return

    print("\nAcesse https://hotmart.com → Catalogo de Produtos")
    print(f"Filtre por produtos de {NICHE_LABELS[niche]}")
    print("Para cada produto, clique em 'Pegar link' e cole abaixo.")
    print("Deixe em branco e pressione Enter para finalizar.")
    print()

    count = 0
    while True:
        print(f"--- Produto #{count + 1} ---")
        name = input("Nome do produto: ").strip()
        if not name:
            break
        url = input("Link de afiliado (completo com ?aff=): ").strip()
        if not url:
            print("Link obrigatorio. Tente novamente.")
            continue

        # Validate the link
        validator = LinkValidatorAgent()
        vctx = CampaignContext(
            campaign={
                "link": url,
                "product_name": name,
                "network": "hotmart",
            },
            run_id=f"validate-{count}",
        )
        vresult = validator.run(vctx)

        if vresult.status != "success":
            print(
                f"  ❌ Link invalido: {vresult.output.get('error', 'erro desconhecido')}"
            )
            continue

        if not vresult.output.get("valid", False):
            print(f"  ⚠️  Link parece invalido: {vresult.output.get('warnings', '')}")
            proceed = input("  Continuar mesmo assim? (s/N): ").strip().lower()
            if proceed != "s":
                continue

        # Suggest commission and keywords
        mctx = CampaignContext(
            campaign={
                "product_name": name,
                "niche": niche,
            },
            run_id=f"match-{count}",
        )
        mresult = matcher.run(mctx)
        keywords = mresult.output.get("suggested_keywords", [])
        commission = mresult.output.get("suggested_commission", 50.0)

        print(f"  Keywords sugeridas: {', '.join(keywords[:5])}")
        print(f"  Comissao sugerida: {commission}%")

        # Store the link
        lctx = CampaignContext(
            campaign={
                "niche": niche,
                "product_name": name,
                "product_url": url,
                "keywords": keywords,
                "commission_value": commission,
                "network": "hotmart",
            },
            run_id=f"link-{count}",
        )
        lresult = manager.run(lctx)

        if lresult.status == "success":
            print("  ✅ Link armazenado com sucesso!")
            count += 1
        else:
            print(f"  ❌ Erro: {lresult.output.get('error', 'desconhecido')}")

    if count > 0:
        print(f"\n📊 {count} produtos coletados para {NICHE_LABELS[niche]}")

        # Update the config file
        uctx = CampaignContext(
            campaign={
                "niche": niche,
                "source": "hotmart_wizard",
            },
            run_id=f"update-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        )
        uresult = updater.run(uctx)

        if uresult.status == "success":
            print("✅ Arquivo de configuracao atualizado!")
            print(
                f"   Total ofertas {NICHE_LABELS[niche]}: {uresult.output.get('total_offers', 0)}"
            )
        else:
            print(f"⚠️  Erro ao atualizar config: {uresult.output.get('error', '')}")
    else:
        print("Nenhum produto adicionado.")


def show_status():
    """Mostra status atual da colecao de links."""
    manager = HotmartLinkManagerAgent()
    ctx = CampaignContext(campaign={"action": "status"}, run_id="status")
    result = manager.run(ctx)

    if result.status != "success":
        print("Erro ao verificar status")
        return

    print_header()
    print("📊 STATUS DA COLECAO DE LINKS HOTMART")
    print("-" * 50)

    for niche_data in result.output.get("collection_status", []):
        niche = niche_data.get("niche", "?")
        count = niche_data.get("count", 0)
        label = NICHE_LABELS.get(niche, niche)
        print(f"  {label:20s}: {count} links")

    total = sum(n.get("count", 0) for n in result.output.get("collection_status", []))
    print(f"\n  TOTAL: {total} links coletados")

    # Show config file status
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text())
        total_offers = sum(len(v) for v in data.get("offers_by_niche", {}).values())
        hotmart_offers = sum(
            1
            for v in data.get("offers_by_niche", {}).values()
            for p in v
            if p.get("network") == "hotmart"
            and "seulink" not in p.get("product_url", "")
        )
        placeholder_offers = sum(
            1
            for v in data.get("offers_by_niche", {}).values()
            for p in v
            if p.get("network") == "hotmart" and "seulink" in p.get("product_url", "")
        )
        print(
            f"\n  📄 Config: {total_offers} ofertas totais, {hotmart_offers} Hotmart ativos, {placeholder_offers} placeholders"
        )


def batch_import(file_path: str):
    """Importa um lote de links de um arquivo JSON."""
    path = Path(file_path)
    if not path.exists():
        print(f"Arquivo nao encontrado: {file_path}")
        return

    with open(path) as f:
        batch = json.load(f)

    if not isinstance(batch, list):
        print("Formato invalido. Deve ser uma lista de objetos.")
        return

    manager = HotmartLinkManagerAgent()
    updater = AffiliateConfigUpdaterAgent()
    validator = LinkValidatorAgent()

    count = 0
    errors = 0
    for item in batch:
        name = item.get("product_name", "")
        url = item.get("product_url", "")
        niche = item.get("niche", "tecnologia")

        if not name or not url:
            errors += 1
            continue

        # Validate
        vctx = CampaignContext(
            campaign={"link": url, "product_name": name}, run_id="batch-v"
        )
        vresult = validator.run(vctx)
        if vresult.status != "success" or not vresult.output.get("valid", False):
            errors += 1
            continue

        # Store
        lctx = CampaignContext(
            campaign={
                "niche": niche,
                "product_name": name,
                "product_url": url,
                "keywords": item.get("keywords", []),
                "commission_value": item.get("commission_value", 50.0),
                "network": "hotmart",
            },
            run_id=f"batch-l-{count}",
        )
        lresult = manager.run(lctx)

        if lresult.status == "success":
            count += 1
        else:
            errors += 1

    # Update config
    uctx = CampaignContext(
        campaign={"niche": "all", "source": "batch_import"}, run_id="batch-update"
    )
    updater.run(uctx)

    print(f"Importados: {count} links, {errors} erros")


def validate_links():
    """Valida todos os links Hotmart na configuracao."""
    print_header()
    print("🔍 VALIDANDO LINKS HOTMART...")
    print("-" * 50)

    validator = LinkValidatorAgent()
    manager = HotmartLinkManagerAgent()

    ctx = CampaignContext(campaign={"action": "validate_all"}, run_id="validate-all")
    result = validator.run(ctx)

    if result.status == "success":
        summary = result.output.get("summary", {})
        print(f"  Validos: {summary.get('valid', 0)}")
        print(f"  Invalidos: {summary.get('invalid', 0)}")
        print(f"  Placeholders (seulink): {summary.get('placeholders', 0)}")

        for issue in result.output.get("issues", []):
            print(f"  ⚠️  {issue}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Assistente Hotmart")
    parser.add_argument(
        "--add-link", action="store_true", help="Adicionar link manualmente"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validar links existentes"
    )
    parser.add_argument("--status", action="store_true", help="Ver status da colecao")
    parser.add_argument(
        "--batch", type=str, help="Importar lote de links de arquivo JSON"
    )
    args = parser.parse_args()

    if args.add_link:
        add_link_interactive()
    elif args.validate:
        validate_links()
    elif args.status:
        show_status()
    elif args.batch:
        batch_import(args.batch)
    else:
        add_link_interactive()


if __name__ == "__main__":
    main()
