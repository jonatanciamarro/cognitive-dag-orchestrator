#!/usr/bin/env python3
"""Importa produtos REAIS da Hotmart via API pública e registra no ProductLinkRegistry.

Uso:
  python scripts/import_hotmart_products.py                    # Importa top 30
  python scripts/import_hotmart_products.py --max 50           # Importa 50
  python scripts/import_hotmart_products.py --niche marketing  # Filtra por nicho
  python scripts/import_hotmart_products.py --only-new         # Só produtos novos
"""

import json, os, sys, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['CAMPAIGN_BOT_REQUIRE_OPT_IN'] = 'false'

from campaign_autopilot.affiliate import ProductLinkRegistry


API_URLS = [
    'https://api-content-search.dsp.hotmart.com/v1/product/topSales?language=pt_br',
    'https://api-content-search.dsp.hotmart.com/v1/product/recommendation?locale=PT_BR',
]

NICHE_MAP = {
    'digital_entrepreneurship': 'empreendedorismo digital',
    'marketing': 'marketing digital',
    'education': 'educacao',
    'health_and_sports': 'saude',
    'personal_development': 'desenvolvimento pessoal',
    'spirituality': 'desenvolvimento pessoal',
    'finance': 'financas',
    'technology': 'tecnologia',
    'career': 'carreira',
}


def fetch_products() -> dict:
    """Fetch products from Hotmart public APIs."""
    all_products = {}
    for url in API_URLS:
        req = urllib.request.Request(url, headers={
            'Origin': 'https://hotmart.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36',
        })
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            items = data if isinstance(data, list) else data.get('content', data.get('products', []))
            for p in items:
                pid = p.get('productId')
                if pid and pid not in all_products:
                    all_products[pid] = p
        except Exception as e:
            print(f"  ⚠️  Erro: {url[:50]}... -> {e}")
    return all_products


def score_product(p: dict) -> float:
    """Score de 0-100 baseado em rating + reviews."""
    rating = float(p.get('rating') or 0)
    reviews = float(p.get('totalReviews') or 0)
    return (rating * 0.6 + min(reviews / 1000, 1) * 0.4) * 100


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Importar produtos da Hotmart")
    parser.add_argument("--max", type=int, default=30, help="Max produtos")
    parser.add_argument("--niche", help="Filtrar por nicho")
    parser.add_argument("--only-new", action="store_true", help="So produtos novos")
    args = parser.parse_args()

    reg = ProductLinkRegistry()

    print("🔍 Buscando produtos na Hotmart...")
    products = fetch_products()
    print(f"   {len(products)} produtos encontrados\n")

    scored = [(score_product(p), pid, p) for pid, p in products.items()]
    scored.sort(reverse=True)

    # Filter by niche if specified
    if args.niche:
        niche_lower = args.niche.lower()
        scored = [(s, pid, p) for s, pid, p in scored
                  if niche_lower in NICHE_MAP.get(p.get('category', ''), '').lower()
                  or niche_lower in (p.get('title', '') or '').lower()]

    count, skipped = 0, 0
    for score, pid, p in scored[:args.max]:
        title = (p.get('title') or '').strip()
        category = p.get('category') or 'geral'
        owner = p.get('ownerName') or ''
        offer = p.get('offer') or ''
        rating = p.get('rating') or 0
        reviews = p.get('totalReviews') or 0
        checkout_link = f"https://pay.hotmart.com/{pid}?off={offer}"

        if not title or not offer:
            continue

        niche = NICHE_MAP.get(category, 'geral')

        # Skip if already registered
        if args.only_new:
            existing = reg.get_link(title, 'hotmart')
            if existing:
                skipped += 1
                continue

        notes = f"API Hotmart. Produtor: {owner}. Rating: {rating:.1f} ({reviews} reviews). ATUALIZE com link de afiliado!"
        lid = reg.register('hotmart', title, checkout_link, niche, notes)
        print(f"  ✅ [{niche:30}] {title[:45]:45} score={score:.0f}")
        count += 1

    print(f"\n✅ {count} produtos registrados ({skipped} pulados)")
    print()
    print("📊 TOTAL NO REGISTRY:")
    stats = reg.get_stats()
    for net, cnt in sorted(stats.get('by_network', {}).items()):
        print(f"   {net}: {cnt} produtos")

    if count > 0:
        print(f"\n⚠️  ATENCAO: Links sao de CHECKOUT (pay.hotmart.com).")
        print(f"   Para GANHAR COMISSAO, voce precisa do seu link de afiliado real.")
        print(f"   1. Acesse o produto na Hotmart")
        print(f"   2. Clique em 'Promover' (ou 'Virar Afiliado')")
        print(f"   3. Copie o link gerado (ex: go.hotmart.com/PRODUTO?aff=SEU_CODIGO)")
        print(f"   4. Atualize no sistema:")
        print(f"      python scripts/manage_links.py list")
        print(f"      python scripts/manage_links.py update <ID> --link 'https://go.hotmart.com/...?aff=SEUCODIGO'")


if __name__ == "__main__":
    main()
