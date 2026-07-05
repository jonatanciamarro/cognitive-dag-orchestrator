#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Projeção da Árvore Paralela de Renda — 13 Fontes Simultâneas"""

from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

FONTES = [
    {
        "id": "hotmart",
        "nome": "Hotmart",
        "tipo": "afiliado",
        "comissao_pct": 0.60,
        "ticket": 97,
        "ctr": 0.012,
        "cvr": 0.03,
        "peso": 0.15,
    },
    {
        "id": "kiwify",
        "nome": "Kiwify",
        "tipo": "afiliado",
        "comissao_pct": 0.60,
        "ticket": 67,
        "ctr": 0.010,
        "cvr": 0.03,
        "peso": 0.10,
    },
    {
        "id": "eduzz",
        "nome": "Eduzz",
        "tipo": "afiliado",
        "comissao_pct": 0.55,
        "ticket": 57,
        "ctr": 0.010,
        "cvr": 0.025,
        "peso": 0.10,
    },
    {
        "id": "monetizze",
        "nome": "Monetizze",
        "tipo": "afiliado",
        "comissao_pct": 0.55,
        "ticket": 47,
        "ctr": 0.008,
        "cvr": 0.025,
        "peso": 0.08,
    },
    {
        "id": "mercadolivre",
        "nome": "M.Livre",
        "tipo": "afiliado",
        "comissao_pct": 0.03,
        "ticket": 120,
        "ctr": 0.015,
        "cvr": 0.05,
        "peso": 0.10,
    },
    {
        "id": "shopee",
        "nome": "Shopee",
        "tipo": "afiliado",
        "comissao_pct": 0.07,
        "ticket": 65,
        "ctr": 0.015,
        "cvr": 0.06,
        "peso": 0.12,
    },
    {
        "id": "shein",
        "nome": "SheIn",
        "tipo": "afiliado",
        "comissao_pct": 0.10,
        "ticket": 45,
        "ctr": 0.012,
        "cvr": 0.05,
        "peso": 0.08,
    },
    {
        "id": "aliexpress",
        "nome": "AliExp",
        "tipo": "afiliado",
        "comissao_pct": 0.05,
        "ticket": 35,
        "ctr": 0.008,
        "cvr": 0.04,
        "peso": 0.05,
    },
    {
        "id": "amazon",
        "nome": "Amazon",
        "tipo": "afiliado",
        "comissao_pct": 0.04,
        "ticket": 150,
        "ctr": 0.020,
        "cvr": 0.07,
        "peso": 0.12,
    },
    {"id": "adsense", "nome": "AdSense", "tipo": "adsense", "rpm": 3.0, "peso": 0.05},
    {
        "id": "cpa",
        "nome": "CPA",
        "tipo": "cpa",
        "cpa_lead": 4.0,
        "lead_rate": 0.003,
        "peso": 0.03,
    },
    {
        "id": "digital",
        "nome": "P.Digit",
        "tipo": "proprio",
        "ticket": 47,
        "cvr": 0.015,
        "peso": 0.02,
    },
    {
        "id": "membership",
        "nome": "Assin.",
        "tipo": "membro",
        "valor_mensal": 27,
        "taxa_conv": 0.003,
        "peso": 0.00,
    },
]

CENARIOS = {
    "minimo": {
        "nome": "Mínimo (Teste)",
        "nichos": 1,
        "arts_dia": 1,
        "visitas_pico": 100,
        "meses_pico": 6,
    },
    "conservador": {
        "nome": "Conservador",
        "nichos": 2,
        "arts_dia": 2,
        "visitas_pico": 200,
        "meses_pico": 5,
    },
    "moderado": {
        "nome": "Moderado",
        "nichos": 4,
        "arts_dia": 3,
        "visitas_pico": 500,
        "meses_pico": 4,
    },
    "agressivo": {
        "nome": "Agressivo",
        "nichos": 6,
        "arts_dia": 4,
        "visitas_pico": 1000,
        "meses_pico": 4,
    },
    "maximo": {
        "nome": "MÁXIMO (13 Fontes)",
        "nichos": 8,
        "arts_dia": 5,
        "visitas_pico": 2000,
        "meses_pico": 3,
    },
}


def projetar(chave: str, meses: int = 12) -> list[dict]:
    cfg = CENARIOS[chave]
    arts_mes = cfg["arts_dia"] * 30 * cfg["nichos"]
    res = []

    for mes in range(1, meses + 1):
        visitas_mes = 0
        for idade in range(1, mes + 1):
            rampa = min(1.0, idade / cfg["meses_pico"])
            decay = max(0, 1.0 - max(0, idade - cfg["meses_pico"]) * 0.02)
            visitas_mes += arts_mes * cfg["visitas_pico"] * rampa * decay

        recs = {}
        total_rec = 0.0

        for f in FONTES:
            vis = visitas_mes * f.get("peso", 0.05)
            tid = f["id"]
            rec = 0.0

            if f["tipo"] == "afiliado":
                cliques = vis * f["ctr"]
                compras = cliques * f["cvr"]
                rec = compras * f["ticket"] * f["comissao_pct"]
                recs[tid] = {"v": round(vis), "r": round(rec, 2)}

            elif f["tipo"] == "adsense":
                pv = vis * 1.5
                rec = (pv / 1000) * f["rpm"]
                recs[tid] = {"v": round(pv), "r": round(rec, 2)}

            elif f["tipo"] == "cpa":
                leads = vis * f["lead_rate"]
                rec = leads * f["cpa_lead"]
                recs[tid] = {"v": round(vis), "r": round(rec, 2)}

            elif f["tipo"] == "proprio":
                compras = vis * f["cvr"]
                rec = compras * f["ticket"]
                recs[tid] = {"v": round(vis), "r": round(rec, 2)}

            elif f["tipo"] == "membro":
                novos = visitas_mes * f["taxa_conv"]
                existentes = (
                    res[-1]["recs"].get(tid, {}).get("ativos", 0)
                    if mes > 1 and res
                    else 0
                )
                ativos = round(existentes + novos)
                rec_mes = ativos * f["valor_mensal"]
                recs[tid] = {
                    "v": round(vis),
                    "r": round(rec_mes, 2),
                    "novos": round(novos),
                    "ativos": ativos,
                }
                rec = rec_mes

            total_rec += rec

        res.append(
            {
                "mes": mes,
                "arts": arts_mes * mes,
                "v": round(visitas_mes),
                "rec": round(total_rec, 2),
                "recs": recs,
            }
        )

    return res


def exibir(resultados: list[dict], chave: str, detalhe: bool = False):
    cfg = CENARIOS[chave]

    console.print(
        Panel(
            f"[bold]{cfg['nome']}[/bold] — {cfg['nichos']} nichos, {cfg['arts_dia']}/dia, "
            f"{cfg['visitas_pico']} vis/artigo pico",
            box=box.HEAVY,
        )
    )

    # Tabela principal
    table = Table(box=box.ROUNDED)
    table.add_column("Mês", style="cyan")
    table.add_column("Arts", style="blue")
    table.add_column("Visitas", style="magenta")

    cores = [
        "green",
        "yellow",
        "blue",
        "cyan",
        "magenta",
        "red",
        "green",
        "yellow",
        "blue",
        "cyan",
        "magenta",
        "red",
        "green",
    ]
    for i, f in enumerate(FONTES):
        table.add_column(f["nome"], style=cores[i % len(cores)])
    table.add_column("TOTAL", style="bold green")

    for r in resultados:
        linha = [str(r["mes"]), str(r["arts"]), f"{r['v']:,}"]
        for f in FONTES:
            val = r["recs"].get(f["id"], {}).get("r", 0)
            linha.append(f"R$ {val:.2f}")
        linha.append(f"R$ {r['rec']:.2f}")
        table.add_row(*linha)

    console.print(table)

    # Totais
    total_v = sum(r["v"] for r in resultados)
    total_r = sum(r["rec"] for r in resultados)
    media = total_r / len(resultados)
    ultimo = resultados[-1]

    console.print(
        Panel(
            f"[bold]📊 12 meses:[/bold] {total_v:,} visitas | "
            f"[green]R$ {total_r:.2f}[/green] total | "
            f"[green]R$ {media:.2f}[/green]/mês | "
            f"Mês 12: [green]R$ {ultimo['rec']:.2f}[/green]",
            box=box.SIMPLE,
        )
    )

    if detalhe:
        r = resultados[-1]
        det_table = Table(title=f"📋 Detalhamento Mês {r['mes']}", box=box.SIMPLE)
        det_table.add_column("Fonte", style="cyan")
        det_table.add_column("Receita/mês", style="green")
        det_table.add_column("Detalhes", style="blue")
        for f in FONTES:
            d = r["recs"].get(f["id"], {})
            if d.get("r", 0) > 0:
                extra = (
                    f" ({d['ativos']} membros)"
                    if f["tipo"] == "membro" and "ativos" in d
                    else ""
                )
                det_table.add_row(f["nome"], f"R$ {d['r']:.2f}", extra.strip())
        console.print(det_table)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--detalhado", action="store_true", help="Mostra detalhamento por fonte"
    )
    ap.add_argument("--json", action="store_true", help="Output em JSON")
    args = ap.parse_args()

    console.print(
        Panel(
            f"[bold]🌳 PROJEÇÃO DA ÁRVORE PARALELA DE RENDA[/bold]\n"
            f"[dim]13 Fontes Simultâneas — {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC[/dim]",
            box=box.HEAVY,
        )
    )

    for chave in ["minimo", "conservador", "moderado", "agressivo", "maximo"]:
        resultados = projetar(chave)
        if args.json:
            print(
                json.dumps(
                    {
                        "cenario": CENARIOS[chave]["nome"],
                        "resultados": resultados,
                        "total": sum(r["rec"] for r in resultados),
                    },
                    indent=2,
                )
            )
        else:
            exibir(resultados, chave, detalhe=args.detalhado)

    console.print(
        Panel(
            "[dim]Aviso: Projeções baseadas em médias de mercado. Resultados reais "
            "dependem de qualidade, consistência e conformidade com cada plataforma.[/dim]",
            box=box.SIMPLE,
        )
    )


if __name__ == "__main__":
    main()
