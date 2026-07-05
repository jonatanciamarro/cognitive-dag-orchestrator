#!/usr/bin/env python3
"""Gerenciador de Links de Afiliado — Product Link Registry CLI.

Uso:
  python scripts/manage_links.py list                    # Listar todos os links
  python scripts/manage_links.py add                      # Adicionar link interativo
  python scripts/manage_links.py add --network hotmart --product "Curso X" --link "https://..." --category tech
  python scripts/manage_links.py search "produto"        # Buscar produto
  python scripts/manage_links.py stats                   # Estatisticas
  python scripts/manage_links.py import-config           # Importar produtos do config faltando
  python scripts/manage_links.py unregister <link_id>    # Remover link
  python scripts/manage_links.py update <link_id> --link "https://..."  # Atualizar link
"""

import sys, os, argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ['CAMPAIGN_BOT_REQUIRE_OPT_IN'] = 'false'

from campaign_autopilot.affiliate import ProductLinkRegistry

REG = ProductLinkRegistry()

NETWORKS = [
    'hotmart', 'kiwify', 'eduzz', 'monetizze',
    'amazon', 'mercadolivre', 'shopee', 'shein', 'aliexpress',
]


def cmd_list(args):
    links = REG.list_all(status=args.status)
    if not links:
        print("📭 Nenhum link registrado.")
        return
    print(f"\n📋 Links Registrados ({len(links)} ativos):")
    print("-" * 80)
    for l in links:
        status_icon = "✅" if l['status'] == 'active' else "❌"
        link_short = l['affiliate_link'][:55] + "..." if len(l['affiliate_link']) > 55 else l['affiliate_link']
        print(f"\n{status_icon} [{l['network']:15}] {l['product_name']}")
        print(f"   ID: {l['link_id'][:8]}...")
        print(f"   Link: {link_short}")
        if l['category']:
            print(f"   Categoria: {l['category']}")
    print()


def cmd_add(args):
    if args.interactive:
        print("\n📝 Registrar Novo Link de Afiliado")
        print("-" * 40)
        print("Redes disponiveis:", ", ".join(NETWORKS))
        network = input("Rede: ").strip().lower()
        product = input("Nome do Produto: ").strip()
        link = input("Link de Afiliado (completo): ").strip()
        category = input("Categoria (opcional): ").strip()
        notes = input("Observacoes (opcional): ").strip()
    else:
        network = args.network
        product = args.product
        link = args.link
        category = args.category or ""
        notes = args.notes or ""

    if not network or not product or not link:
        print("❌ Erro: network, product e link sao obrigatorios")
        sys.exit(1)

    lid = REG.register(network, product, link, category, notes)
    print(f"✅ Link registrado! ID: {lid}")


def cmd_search(args):
    term = args.term.lower()
    links = REG.list_all(status="all")
    results = [l for l in links if term in l['product_name'].lower() or term in l['network'].lower()]
    if not results:
        print(f"📭 Nenhum resultado para '{term}'")
        return
    print(f"\n🔍 Resultados para '{term}':")
    for l in results:
        status_icon = "✅" if l['status'] == 'active' else "❌"
        print(f"\n{status_icon} [{l['network']}] {l['product_name']}")
        print(f"   ID: {l['link_id']}")
        print(f"   Link: {l['affiliate_link']}")


def cmd_stats(args):
    stats = REG.get_stats()
    print("\n📊 Product Link Registry — Estatisticas")
    print("=" * 40)
    print(f"Total de links ativos: {stats['total_active']}")
    print(f"\nPor rede:")
    for network, count in sorted(stats['by_network'].items()):
        print(f"  {network:15}: {count}")
    if stats['recently_added']:
        print(f"\nAdicionados recentemente:")
        for r in stats['recently_added']:
            print(f"  - {r['product_name']} ({r['network']})")
    print()


def cmd_import_config(args):
    """Importa produtos do config que ainda nao tem link registrado."""
    import json
    from pathlib import Path

    config_path = Path(__file__).resolve().parent.parent / "configs" / "affiliate_offers.json"
    if not config_path.exists():
        print("❌ configs/affiliate_offers.json nao encontrado")
        return

    with open(config_path) as f:
        cfg = json.load(f)

    imported = 0
    skipped = 0
    for niche, offers in cfg.get("offers_by_niche", {}).items():
        for o in offers:
            name = o["product_name"]
            network = o["network"]
            # Check if already registered
            existing = REG.get_link(name, network)
            if existing:
                skipped += 1
                continue
            # Register with default URL (user should update with real link)
            default_url = o.get("product_url", "")
            notes = f"Importado do config. SUBSTITUA pelo seu link REAL de afiliado!"
            lid = REG.register(network, name, default_url, niche, notes)
            print(f"  ⚠️  [{network}] {name}")
            print(f"       Link DEFAULT: {default_url}")
            print(f"       ID: {lid} — ATUALIZE com seu link real!")
            imported += 1

    print(f"\n✅ {imported} produtos importados (links DEFAULT, precisam ser atualizados)")
    print(f"⏭️  {skipped} ja estavam registrados")
    print(f"\n💡 Use: python scripts/manage_links.py update <ID> --link 'https://...'")


def cmd_unregister(args):
    REG.unregister(args.link_id)
    print(f"✅ Link {args.link_id[:8]}... desativado")


def cmd_update(args):
    REG.update_link(args.link_id, args.link)
    print(f"✅ Link {args.link_id[:8]}... atualizado")


def main():
    parser = argparse.ArgumentParser(description="Product Link Registry CLI")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="Listar links")
    p_list.add_argument("--status", default="active", choices=["active", "inactive", "all"])
    p_list.set_defaults(func=cmd_list)

    p_add = sub.add_parser("add", help="Adicionar link")
    p_add.add_argument("--network", help="Rede (hotmart, kiwify, eduzz, etc)")
    p_add.add_argument("--product", help="Nome do produto")
    p_add.add_argument("--link", help="Link de afiliado completo")
    p_add.add_argument("--category", help="Categoria (opcional)")
    p_add.add_argument("--notes", help="Observacoes (opcional)")
    p_add.add_argument("--interactive", "-i", action="store_true", help="Modo interativo")
    p_add.set_defaults(func=cmd_add)

    p_search = sub.add_parser("search", help="Buscar produto")
    p_search.add_argument("term", help="Termo de busca")
    p_search.set_defaults(func=cmd_search)

    p_stats = sub.add_parser("stats", help="Estatisticas")
    p_stats.set_defaults(func=cmd_stats)

    p_import = sub.add_parser("import-config", help="Importar produtos do config")
    p_import.set_defaults(func=cmd_import_config)

    p_unreg = sub.add_parser("unregister", help="Remover link")
    p_unreg.add_argument("link_id", help="ID do link")
    p_unreg.set_defaults(func=cmd_unregister)

    p_upd = sub.add_parser("update", help="Atualizar link")
    p_upd.add_argument("link_id", help="ID do link")
    p_upd.add_argument("--link", required=True, help="Novo link de afiliado")
    p_upd.set_defaults(func=cmd_update)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
