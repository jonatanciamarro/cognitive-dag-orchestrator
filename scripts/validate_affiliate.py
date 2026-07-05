#!/usr/bin/env python3
"""Valida a configuracao de afiliados (Hotmart, Amazon, etc).

Uso:
    python scripts/validate_affiliate.py
    python scripts/validate_affiliate.py --detalhado
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from campaign_autopilot.affiliate import Hotmart

ENV_VARS = {
    # Hotmart: nao tem ID fixo (cada link tem seu proprio aff)
    "AMAZON_TRACKING_ID": "Amazon Associates",
    "MONETIZZE_AFFILIATE_ID": "Monetizze",
    "KIWIFY_AFFILIATE_ID": "Kiwify",
    "EDUZZ_AFFILIATE_ID": "Eduzz",
}


def check_env():
    print("\n=== VARIAVEIS DE AMBIENTE ===")
    configured = 0
    for var, name in ENV_VARS.items():
        val = os.environ.get(var, "")
        if val:
            print(f"  ✅ {name:20s} ({var}): configurado")
            configured += 1
        else:
            print(f"  ⬜ {name:20s} ({var}): vazio — usar: export {var}=seu_codigo")
    return configured


def check_offers():
    print("\n=== OFERTAS CONFIGURADAS ===")
    path = Path("configs/affiliate_offers.json")
    if not path.exists():
        print("  ❌ Arquivo nao encontrado: configs/affiliate_offers.json")
        return 0

    data = json.loads(path.read_text())
    total = 0
    for niche, products in data.get("offers_by_niche", {}).items():
        active = [
            p
            for p in products
            if p.get("product_url") and "seulink" not in p.get("product_url", "")
        ]
        placeholder = [p for p in products if "seulink" in p.get("product_url", "")]
        total += len(products)
        print(
            f"  {niche:15s}: {len(products)} ofertas ({len(active)} ativos, {len(placeholder)} placeholders)"
        )
    return total


def check_pipeline():
    print("\n=== PIPELINE DE AFILIADOS ===")

    # Test Hotmart
    hotmart_id = os.environ.get("HOTMART_AFFILIATE_ID", "")
    if hotmart_id:
        hotmart = Hotmart(hotmart_id)
        from campaign_autopilot.affiliate import AffiliateOffer

        test_offer = AffiliateOffer(
            offer_id="test",
            network="hotmart",
            product_name="Test Product",
            product_url="https://hotm.art/test",
            commission_type="percentage",
            commission_value=50.0,
        )
        link = hotmart.build_link(test_offer)
        print(f"  🔗 Hotmart link test: {link}")
        if hotmart_id in link:
            print("     ✅ ID de afiliado presente no link")
        else:
            print("     ❌ ID de afiliado NAO encontrado no link")
    else:
        print("  ⬜ Hotmart: configurar HOTMART_AFFILIATE_ID no .env")

    # Test affiliate link inserter
    try:
        from campaign_autopilot.agents.money.affiliate_link_inserter import (
            AffiliateLinkInserterAgent,
        )

        agent = AffiliateLinkInserterAgent()
        print(
            f"  ✅ AffiliateLinkInserterAgent: carregado com {len(agent.offers.get('offers_by_niche', {}))} nichos"
        )
    except Exception as e:
        print(f"  ❌ AffiliateLinkInserterAgent: {e}")


def main():
    print("=" * 60)
    print("  VALIDACAO DE AFILIADOS — Campaign Autopilot")
    print("=" * 60)

    env_count = check_env()
    offer_count = check_offers()
    check_pipeline()

    print(f"\n{'=' * 60}")
    if env_count == 0 and offer_count == 0:
        print("  ❌ NENHUMA configuracao de afiliado encontrada")
        print("  Para comecar:")
        print("  1. Crie conta em https://hotmart.com")
        print("  2. Copie seu codigo de afiliado")
        print("  3. Edite .env: HOTMART_AFFILIATE_ID=seu_codigo")
        print("  3a. Opcional: edite configs/affiliate_offers.json com seus links")
    elif env_count > 0:
        print(f"  ✅ {env_count} redes configuradas, {offer_count} ofertas carregadas")
        print("  Sistema pronto para monetizar!")
    else:
        print("  ⚠️  Ofertas configuradas mas IDs de afiliado vazios")
        print("  Configure suas IDs no .env")

    print(f"{'=' * 60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--detalhado", action="store_true")
    args = parser.parse_args()
    main()
    if args.detalhado:
        print("\nDetalhamento das ofertas:")
        data = json.loads(Path("configs/affiliate_offers.json").read_text())
        for niche, products in data.get("offers_by_niche", {}).items():
            for p in products:
                print(
                    f"  [{niche}] {p['product_name']:40s} | {p['network']:10s} | {p['commission_value']}%"
                )
