#!/usr/bin/env python3
"""Converte links de checkout Hotmart em links de afiliado REAIS.

Uso:
  1. Primeiro, DESCOBRE seu ID de afiliado:
     - Acesse app.hotmart.com/products/affiliations pelo CELULAR/PC
     - Clique em qualquer produto que já esteja afiliado
     - Copie o link gerado (ex: https://go.hotmart.com/S12345678?aff=SEUCODIGO)
     - SEUCODIGO é seu affiliate ID

  2. Aplique a todos os produtos:
     python scripts/convert_hotmart_links.py SEUCODIGO

  Exemplo:
     python scripts/convert_hotmart_links.py S12345678
"""

import sys, os, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['CAMPAIGN_BOT_REQUIRE_OPT_IN'] = 'false'

from campaign_autopilot.affiliate import ProductLinkRegistry


def convert(affiliate_id: str, dry_run: bool = False) -> int:
    """Converte todos os links pay.hotmart.com para links com affiliate ID."""
    reg = ProductLinkRegistry()
    products = reg.list_all()
    count = 0

    for p in products:
        if p['network'] != 'hotmart':
            continue
        
        old_link = p['affiliate_link']
        
        # Check if already has an affiliate ID
        if '?aff=' in old_link or '&aff=' in old_link:
            print(f"  ⏭️  JÁ TEM AFFILIATE: [{p['product_name'][:40]}]")
            continue
        
        # Convert pay.hotmart.com links
        # Pattern: https://pay.hotmart.com/PRODUCT_ID?off=OFFER_CODE
        match = re.match(r'(https://pay\.hotmart\.com/\d+\?off=[^&]+)', old_link)
        if match:
            base_url = match.group(1)
            new_link = f'{base_url}&aff={affiliate_id}'
        elif 'pay.hotmart.com' in old_link and '?' not in old_link:
            new_link = f'{old_link}?aff={affiliate_id}'
        else:
            # Generic go.hotmart.com or other format
            new_link = f'https://go.hotmart.com/{affiliate_id}?product={p["product_id"]}'
        
        if dry_run:
            print(f"  📝 [DRY-RUN] {p['product_name'][:35]:35} → {new_link[:70]}")
        else:
            reg.update_link(p['link_id'], new_link)
            print(f"  ✅ {p['product_name'][:35]:35} → {new_link[:70]}")
        count += 1
    
    return count


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    affiliate_id = sys.argv[1].strip()
    dry_run = '--dry-run' in sys.argv
    
    print(f"\n🔗 Convertendo links Hotmart para affiliate ID: {affiliate_id}")
    print(f"{' (DRY RUN)' if dry_run else ''}")
    print("-" * 70)
    
    count = convert(affiliate_id, dry_run)
    
    if count == 0:
        print("\n   Nenhum link para converter.")
        print("   Motivos possíveis:")
        print("   - Todos já tem affiliate ID")
        print("   - Nenhum produto Hotmart encontrado")
    else:
        print(f"\n✅ {count} links atualizados!")
        print(f"\n📊 Verifique: python scripts/manage_links.py stats")
    
    print(f"\n💡 DICA: Seu affiliate ID Hotmart parece ser algo como 'S12345678' ou 'H12345678'")
    print(f"   Para encontrar: https://app.hotmart.com/products/affiliations")
    print(f"   Click em qualquer produto afiliado e veja o link gerado")


if __name__ == "__main__":
    main()
