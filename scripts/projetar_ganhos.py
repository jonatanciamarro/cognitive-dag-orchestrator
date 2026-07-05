#!/usr/bin/env python3
"""💰 Projetor de Ganhos — Calcule suas estimativas de receita realistas.

Uso:
    python3 scripts/projetar_ganhos.py                  # Modo interativo
    python3 scripts/projetar_ganhos.py --rapido         # Cenários pré-definidos
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def calcular(
    artigos_por_dia_por_nicho: int,
    nichos: int,
    visitas_por_artigo_peak: int,
    ctr_afiliado_pct: float,
    cvr_afiliado_pct: float,
    ticket_medio: float,
    comissao_pct: float,
    rpm_adsense: float,
    meses: int = 12,
) -> dict[str, Any]:
    """Calcula projeção de receita com modelo realista.

    Premissas:
    - 4 meses para pico de tráfego SEO
    - 3% decay/mês após pico (evergreen)
    - 30% artigos comerciais, 70% informacionais
    - 1% dos visitantes viram leads de email
    - CTR = % que clica no link de afiliado
    - CVR = % dos que clicam que compram
    """
    artigos_por_mes = artigos_por_dia_por_nicho * 30 * nichos
    resultados = []

    for mes in range(1, meses + 1):
        artigos_total = artigos_por_mes * mes
        visitas_total = 0

        for idade in range(1, mes + 1):
            arts_coorte = artigos_por_mes
            if idade <= 4:
                rampa = idade / 4.0
            else:
                rampa = 1.0
            decay = max(0.0, 1.0 - max(0, idade - 4) * 0.03)
            visitas_coorte = arts_coorte * visitas_por_artigo_peak * rampa * decay
            visitas_total += visitas_coorte

        visitas_comerciais = visitas_total * 0.30
        visitas_info = visitas_total * 0.70

        cliques_afiliado = visitas_comerciais * (ctr_afiliado_pct / 100.0)
        compras_afiliado = cliques_afiliado * (cvr_afiliado_pct / 100.0)
        receita_afiliado = compras_afiliado * ticket_medio * comissao_pct

        pv_adsense = visitas_info * 1.5
        receita_adsense = (pv_adsense / 1000.0) * rpm_adsense

        leads_email = visitas_total * 0.01
        receita_email = leads_email * 0.50 * 27.0

        receita_total = receita_afiliado + receita_adsense + receita_email

        resultados.append(
            {
                "mes": mes,
                "artigos": int(artigos_total),
                "visitas": int(visitas_total),
                "afiliado": round(receita_afiliado, 2),
                "adsense": round(receita_adsense, 2),
                "email": round(receita_email, 2),
                "total": round(receita_total, 2),
            }
        )

    return {
        "parametros": {
            "artigos_por_dia_por_nicho": artigos_por_dia_por_nicho,
            "nichos": nichos,
            "visitas_por_artigo_peak": visitas_por_artigo_peak,
            "ctr_afiliado_pct": ctr_afiliado_pct,
            "cvr_afiliado_pct": cvr_afiliado_pct,
            "ticket_medio": ticket_medio,
            "comissao_pct": comissao_pct,
            "rpm_adsense": rpm_adsense,
        },
        "resultados": resultados,
    }


def exibir(resultado: dict[str, Any]):
    params = resultado["parametros"]
    meses = resultado["resultados"]

    console.print(
        Panel(
            "[bold]💰 PROJEÇÃO DE GANHOS — CAMPAIGN AUTOPILOT[/bold]\n"
            "[dim]Cenário calculado[/dim]",
            box=box.HEAVY,
        )
    )

    # Parâmetros
    param_table = Table(box=box.SIMPLE)
    param_table.add_column("Parâmetro", style="cyan")
    param_table.add_column("Valor", style="green")
    param_table.add_row("Artigos/dia/nicho", str(params["artigos_por_dia_por_nicho"]))
    param_table.add_row("Nichos", str(params["nichos"]))
    param_table.add_row("Visitas/artigo (pico)", str(params["visitas_por_artigo_peak"]))
    param_table.add_row("CTR afiliado", f"{params['ctr_afiliado_pct']:.1f}%")
    param_table.add_row("CVR afiliado", f"{params['cvr_afiliado_pct']:.1f}%")
    param_table.add_row("Ticket médio", f"R$ {params['ticket_medio']:.2f}")
    param_table.add_row("Comissão", f"{params['comissao_pct'] * 100:.0f}%")
    param_table.add_row("RPM AdSense", f"R$ {params['rpm_adsense']:.2f}")
    console.print(param_table)

    # Tabela mensal
    table = Table(title="📊 Projeção Mês a Mês", box=box.ROUNDED)
    table.add_column("Mês", style="cyan")
    table.add_column("Artigos", style="blue")
    table.add_column("Visitas", style="magenta")
    table.add_column("Afiliado", style="green")
    table.add_column("AdSense", style="yellow")
    table.add_column("Email", style="blue")
    table.add_column("Total", style="bold green")

    for m in meses:
        table.add_row(
            str(m["mes"]),
            str(m["artigos"]),
            f"{m['visitas']:,}",
            f"R$ {m['afiliado']:.2f}",
            f"R$ {m['adsense']:.2f}",
            f"R$ {m['email']:.2f}",
            f"R$ {m['total']:.2f}",
        )

    total_visitas = sum(m["visitas"] for m in meses)
    total_receita = sum(m["total"] for m in meses)
    table.add_row(
        "[bold]TOTAL[/bold]",
        "[bold]—[/bold]",
        f"[bold]{total_visitas:,}[/bold]",
        f"[bold]R$ {sum(m['afiliado'] for m in meses):.2f}[/bold]",
        f"[bold]R$ {sum(m['adsense'] for m in meses):.2f}[/bold]",
        f"[bold]R$ {sum(m['email'] for m in meses):.2f}[/bold]",
        f"[bold]R$ {total_receita:.2f}[/bold]",
    )
    console.print(table)

    # Resumo
    console.print(
        Panel(
            f"[bold]📈 Resumo de 12 meses[/bold]\n"
            f"  Total de visitas: [green]{total_visitas:,}[/green]\n"
            f"  Receita total:    [green]R$ {total_receita:.2f}[/green]\n"
            f"  Média mensal:     [green]R$ {total_receita / 12:.2f}[/green]\n"
            f"  Mês 12:           [green]R$ {meses[-1]['total']:.2f}[/green]",
            box=box.SIMPLE,
        )
    )


def cenarios_rapidos():
    """Executa cenários pré-definidos para comparação rápida."""
    cenarios = [
        ("Mínimo", 1, 1, 100, 2.0, 3.0, 97, 0.60, 3.0),
        ("Conservador", 2, 2, 200, 2.5, 3.5, 97, 0.60, 3.5),
        ("Moderado", 3, 3, 400, 3.0, 4.0, 97, 0.60, 4.0),
        ("Agressivo", 5, 4, 800, 3.5, 5.0, 97, 0.60, 5.0),
        ("Máximo", 10, 5, 1500, 4.0, 6.0, 97, 0.60, 6.0),
    ]

    console.print(Panel("[bold]📊 CENÁRIOS RÁPIDOS[/bold]", box=box.HEAVY))

    table = Table(box=box.ROUNDED)
    table.add_column("Cenário", style="cyan")
    table.add_column("Nichos", style="blue")
    table.add_column("Arts/dia", style="blue")
    table.add_column("Visitas/mês 12", style="magenta")
    table.add_column("Rec/mês 12", style="green")
    table.add_column("Rec total 12m", style="bold green")

    for nome, nichos, arts, visitas, ctr, cvr, ticket, comissao, rpm in cenarios:
        res = calcular(arts, nichos, visitas, ctr, cvr, ticket, comissao, rpm, meses=12)
        ultimo = res["resultados"][-1]
        total = sum(m["total"] for m in res["resultados"])
        table.add_row(
            nome,
            str(nichos),
            str(arts),
            f"{ultimo['visitas']:,}",
            f"R$ {ultimo['total']:.2f}",
            f"R$ {total:.2f}",
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="💰 Projetor de Ganhos")
    parser.add_argument("--rapido", action="store_true", help="Cenários pré-definidos")
    args = parser.parse_args()

    if args.rapido:
        cenarios_rapidos()
        return

    try:
        console.print("[bold]💰 Projetor de Ganhos - Campaign Autopilot[/bold]\n")
        console.print("[dim]Deixe em branco para usar valores padrão[/dim]\n")

        artigos = int(input("Artigos por dia por nicho [3]: ") or "3")
        nichos = int(input("Número de nichos [3]: ") or "3")
        visitas = int(input("Visitas por artigo no pico [500]: ") or "500")
        ctr = float(input("CTR afiliado % [3.0]: ") or "3.0")
        cvr = float(input("CVR afiliado % [4.0]: ") or "4.0")
        ticket = float(input("Ticket médio R$ [97]: ") or "97")
        comissao = float(input("Comissão % [60]: ") or "60") / 100.0
        rpm = float(input("RPM AdSense R$ [3.0]: ") or "3.0")

        resultado = calcular(artigos, nichos, visitas, ctr, cvr, ticket, comissao, rpm)
        exibir(resultado)

    except (ValueError, EOFError):
        console.print(
            "[red]Entrada inválida. Use --rapido para cenários pré-definidos.[/red]"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
