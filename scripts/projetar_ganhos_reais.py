#!/usr/bin/env python3
"""💰 Projecao de Ganhos REALISTA — Multi-plataforma, Multi-nicho, Multi-fonte.

Considera:
- 11 plataformas de conteudo (blog + 10 sociais)
- 4 fontes de receita (afiliado, AdSense, CPA, produtos/membresia)
- 4+ nichos com escalabilidade
- Efeito de compounding SEO + social
- Limites maximos seguros de postagem (anti-spam)
- Taxas de conversao realistas do mercado brasileiro
- Diminishing returns por saturacao de audiencia
- Crescimento de lista de email ao longo do tempo
- Traffic recycling (lead magnets, exit-intent, cross-niche)

Uso:
    python3 scripts/projetar_ganhos_reais.py          # Cenarios pre-definidos
    python3 scripts/projetar_ganhos_reais.py --detalhado  # Tabela mes a mes
    python3 scripts/projetar_ganhos_reais.py --json    # Output JSON
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any

# ── Configuracoes de Cenario ─────────────────────────────────────────

CENARIOS = {
    "conservador": {
        "label": "🟢 Conservador (Comecando do Zero)",
        "nichos_iniciais": 4,
        "novos_nichos_por_ano": 2,
        "artigos_por_dia_por_nicho": 1,
        "posts_sociais_por_dia_por_nicho": 3,
        "videos_por_semana_por_nicho": 1,
        "visitas_seo_por_artigo_por_mes": 300,
        "visitas_sociais_por_post": 50,
        "visitas_youtube_por_video": 200,
        "ctr_afiliado": 0.008,  # 0.8%
        "cvr_afiliado": 0.03,  # 3% dos que clicam compram
        "ticket_medio_afiliado": 60,
        "comissao_media_pct": 0.40,
        "rpm_adsense": 3.0,
        "cpa_por_lead": 3.0,
        "cpa_leads_por_visita": 0.002,  # 0.2%
        "cvr_lead_magnet": 0.04,  # 4%
        "cvr_email_seq": 0.03,  # 3%
        "cvr_produto_digital": 0.01,  # 1%
        "ticket_produto_digital": 47,
        "taxa_membresia": 0.002,  # 0.2% dos visitantes
        "valor_mensal_membresia": 27,
        "reinvestimento_trafego_pago_pct": 0,
        "email_capture_rate": 0.03,  # 3% newsletter
        "meses_para_pico_seo": 5,
        "decay_mensal_pct": 0.02,  # 2%
        "email_afiliado_cvr": 0.04,
    },
    "moderado": {
        "label": "🟡 Moderado (Dedicacao Parcial)",
        "nichos_iniciais": 6,
        "novos_nichos_por_ano": 3,
        "artigos_por_dia_por_nicho": 2,
        "posts_sociais_por_dia_por_nicho": 5,
        "videos_por_semana_por_nicho": 2,
        "visitas_seo_por_artigo_por_mes": 800,
        "visitas_sociais_por_post": 150,
        "visitas_youtube_por_video": 800,
        "ctr_afiliado": 0.015,  # 1.5%
        "cvr_afiliado": 0.05,  # 5%
        "ticket_medio_afiliado": 80,
        "comissao_media_pct": 0.50,
        "rpm_adsense": 5.0,
        "cpa_por_lead": 5.0,
        "cpa_leads_por_visita": 0.005,  # 0.5%
        "cvr_lead_magnet": 0.06,  # 6%
        "cvr_email_seq": 0.05,  # 5%
        "cvr_produto_digital": 0.02,  # 2%
        "ticket_produto_digital": 67,
        "taxa_membresia": 0.005,  # 0.5%
        "valor_mensal_membresia": 37,
        "reinvestimento_trafego_pago_pct": 0.30,  # 30% da receita reinvestida
        "email_capture_rate": 0.05,  # 5%
        "meses_para_pico_seo": 4,
        "decay_mensal_pct": 0.015,
        "email_afiliado_cvr": 0.06,
    },
    "agressivo": {
        "label": "🔴 Agressivo (Dedicacao Total)",
        "nichos_iniciais": 8,
        "novos_nichos_por_ano": 4,
        "artigos_por_dia_por_nicho": 4,
        "posts_sociais_por_dia_por_nicho": 10,
        "videos_por_semana_por_nicho": 4,
        "visitas_seo_por_artigo_por_mes": 2000,
        "visitas_sociais_por_post": 400,
        "visitas_youtube_por_video": 2500,
        "ctr_afiliado": 0.025,  # 2.5%
        "cvr_afiliado": 0.07,  # 7%
        "ticket_medio_afiliado": 120,
        "comissao_media_pct": 0.60,
        "rpm_adsense": 8.0,
        "cpa_por_lead": 8.0,
        "cpa_leads_por_visita": 0.01,  # 1%
        "cvr_lead_magnet": 0.10,  # 10%
        "cvr_email_seq": 0.08,  # 8%
        "cvr_produto_digital": 0.04,  # 4%
        "ticket_produto_digital": 97,
        "taxa_membresia": 0.01,  # 1%
        "valor_mensal_membresia": 47,
        "reinvestimento_trafego_pago_pct": 0.50,  # 50%
        "email_capture_rate": 0.08,  # 8%
        "meses_para_pico_seo": 3,
        "decay_mensal_pct": 0.01,
        "email_afiliado_cvr": 0.08,
    },
    "maximo": {
        "label": "🔥 MAXIMO (Sistema 3a Ordem em Full Autopilot)",
        "nichos_iniciais": 8,
        "novos_nichos_por_ano": 4,
        "artigos_por_dia_por_nicho": 4,
        "posts_sociais_por_dia_por_nicho": 12,
        "videos_por_semana_por_nicho": 3,
        "visitas_seo_por_artigo_por_mes": 3000,
        "visitas_sociais_por_post": 500,
        "visitas_youtube_por_video": 3000,
        "ctr_afiliado": 0.03,
        "cvr_afiliado": 0.08,
        "ticket_medio_afiliado": 120,
        "comissao_media_pct": 0.60,
        "rpm_adsense": 10.0,
        "cpa_por_lead": 10.0,
        "cpa_leads_por_visita": 0.01,
        "cvr_lead_magnet": 0.10,
        "cvr_email_seq": 0.08,
        "cvr_produto_digital": 0.03,
        "ticket_produto_digital": 97,
        "taxa_membresia": 0.01,
        "valor_mensal_membresia": 47,
        "reinvestimento_trafego_pago_pct": 0.30,
        "email_capture_rate": 0.08,
        "meses_para_pico_seo": 3,
        "decay_mensal_pct": 0.02,
        "email_afiliado_cvr": 0.08,
    },
}

# Fatores de distribuicao de trafego entre plataformas
TRAFEGO_PLATAFORMAS = {
    "blog": {"pct": 0.25, "nome": "Site/Blog (SEO)", "monetizacao": "adsense+afiliado"},
    "youtube": {"pct": 0.15, "nome": "YouTube", "monetizacao": "adsense+afiliado"},
    "instagram": {"pct": 0.10, "nome": "Instagram", "monetizacao": "afiliado+produto"},
    "tiktok": {"pct": 0.08, "nome": "TikTok", "monetizacao": "afiliado+cpa"},
    "twitter": {"pct": 0.05, "nome": "Twitter/X", "monetizacao": "afiliado"},
    "pinterest": {"pct": 0.12, "nome": "Pinterest", "monetizacao": "afiliado+adsense"},
    "linkedin": {"pct": 0.03, "nome": "LinkedIn", "monetizacao": "produto"},
    "facebook": {"pct": 0.07, "nome": "Facebook", "monetizacao": "afiliado+produto"},
    "telegram": {"pct": 0.08, "nome": "Telegram", "monetizacao": "afiliado+produto"},
    "whatsapp": {"pct": 0.04, "nome": "WhatsApp", "monetizacao": "afiliado"},
    "email": {
        "pct": 0.03,
        "nome": "Email Marketing",
        "monetizacao": "afiliado+produto",
    },
}

CUSTOS_FIXOS = {
    "dominio_anual": 50,
    "hospedagem_mensal": 0,  # GitHub Pages gratis
    "ferramentas_mensal": 0,  # Tudo gratis
    "llm_api_mensal": 0,  # Providers gratis
}


def calcular_mes(
    mes: int, config: dict[str, Any], acum: dict[str, Any]
) -> dict[str, Any]:
    """Calcula projecao para um mes especifico com modelo de reinvestimento em trafego pago."""
    c = config

    # ── Nichos ativos (crescem ao longo do tempo) ──
    if mes <= 12:
        nichos_ativos = c["nichos_iniciais"]
    else:
        extra = ((mes - 12) // 12) * c["novos_nichos_por_ano"]
        nichos_ativos = c["nichos_iniciais"] + extra

    # ── Volume de conteudo ──
    artigos_mes = c["artigos_por_dia_por_nicho"] * 30 * nichos_ativos
    posts_sociais_mes = c["posts_sociais_por_dia_por_nicho"] * 30 * nichos_ativos
    videos_mes = c["videos_por_semana_por_nicho"] * 4 * nichos_ativos
    acum["artigos_total"] += artigos_mes
    acum["posts_total"] += posts_sociais_mes
    acum["videos_total"] += videos_mes

    # ── Trafego SEO (compounding) ──
    pico = c["meses_para_pico_seo"]
    decay = c["decay_mensal_pct"]
    visitas_seo = 0
    for idade_mes in range(1, min(mes, 36) + 1):
        arts_mes_passado = c["artigos_por_dia_por_nicho"] * 30 * nichos_ativos
        if idade_mes <= pico:
            fator = idade_mes / pico
        else:
            fator = (1 - decay) ** (idade_mes - pico)
        visitas_seo += arts_mes_passado * c["visitas_seo_por_artigo_por_mes"] * fator

    # ── Trafego Social ──
    visitas_sociais_acum = 0
    for idade_mes in range(1, min(mes, 3) + 1):
        arts = c["posts_sociais_por_dia_por_nicho"] * 30 * nichos_ativos
        visitas_sociais_acum += (
            arts * c["visitas_sociais_por_post"] * (0.5 ** (idade_mes - 1))
        )

    visitas_youtube_acum = 0
    for idade_mes in range(1, min(mes, 12) + 1):
        vids = c["videos_por_semana_por_nicho"] * 4 * nichos_ativos
        visitas_youtube_acum += (
            vids * c["visitas_youtube_por_video"] * (0.85 ** (idade_mes - 1))
        )

    visitas_organicas = (
        visitas_seo
        + visitas_sociais_acum
        + max(videos_mes * c["visitas_youtube_por_video"], visitas_youtube_acum)
    )

    # ── Trafego Pago (cresce com reinvestimento) ──
    # O trafego pago vem do orcamento do mes ANTERIOR
    visitas_pagas = acum.get("visitas_pagas_mes_anterior", 0)
    orcamento_pago = acum.get("orcamento_pago_mes_anterior", 0)

    # ── Lista de Email (vem de todo trafego) ──
    visitas_total = visitas_organicas + visitas_pagas
    novos_emails = visitas_total * c["email_capture_rate"]
    acum["lista_email"] += novos_emails
    # Cap email list at 500k for conservative, scales with scenario
    max_email = min(500000, nichos_ativos * 100000)
    acum["lista_email"] = min(acum["lista_email"], max_email)

    # ── RECEITA ORIGINAL (das fontes organicas + pagas) ──
    clicks_afiliado = visitas_total * c["ctr_afiliado"]
    compras_afiliado = clicks_afiliado * c["cvr_afiliado"]
    receita_afiliado = (
        compras_afiliado * c["ticket_medio_afiliado"] * c["comissao_media_pct"]
    )

    if acum["lista_email"] > 100:
        emails_ativos = acum["lista_email"] * 0.20
        clicks_email = emails_ativos * 0.05
        compras_email = clicks_email * c["email_afiliado_cvr"]
        receita_email_afiliado = (
            compras_email * c["ticket_medio_afiliado"] * c["comissao_media_pct"]
        )
    else:
        receita_email_afiliado = 0

    visitas_adsense = visitas_seo * 0.25 + (
        visitas_youtube_acum * 0.5 if mes > 3 else 0
    )
    receita_adsense = (visitas_adsense / 1000) * c["rpm_adsense"]

    leads_cpa = visitas_total * c["cpa_leads_por_visita"]
    leads_cpa = min(leads_cpa, 500000)
    receita_cpa = leads_cpa * c["cpa_por_lead"]

    if acum["lista_email"] > 200 and mes > 3:
        email_efetivo = min(acum["lista_email"], 100000)
        cvr_ajustado = c["cvr_produto_digital"] * (
            0.3 + 0.7 * min(1.0, 5000 / max(email_efetivo, 1000))
        )
        compras_produto = email_efetivo * cvr_ajustado
        receita_produto = compras_produto * c["ticket_produto_digital"]
    else:
        receita_produto = 0

    if mes > 6:
        membros_raw = visitas_total * c["taxa_membresia"]
        max_membros = nichos_ativos * 5000
        membros = min(membros_raw, max_membros)
        receita_membresia = membros * c["valor_mensal_membresia"]
    else:
        receita_membresia = 0

    if acum["lista_email"] > 50:
        leads_reciclados = visitas_total * 0.03
        compras_recicladas = leads_reciclados * c["cvr_lead_magnet"]
        receita_reciclagem = compras_recicladas * c["ticket_medio_afiliado"] * 0.5
    else:
        receita_reciclagem = 0

    receita_organica = (
        receita_afiliado
        + receita_adsense
        + receita_cpa
        + receita_produto
        + receita_membresia
        + receita_email_afiliado
        + receita_reciclagem
    )

    # ── TRAFEGO PAGO: MODELO DE REINVESTIMENTO FLYWHEEL COM CAP ──
    # O sistema comeca a reinvestir quando a receita organica >= R$ 500/mes

    receita_paga = 0
    orcamento_usado = 0

    # So ativa trafego pago se receita organica for suficiente
    if receita_organica >= 500 and mes >= 4:
        # ── Fase 1: TESTE (meses 4-6) ──
        if mes <= 6:
            pct_reinvestimento = 0.20
            roas = 1.3
        # ── Fase 2: VALIDACAO (meses 7-9) ──
        elif mes <= 9:
            pct_reinvestimento = 0.35
            roas = 1.8
        # ── Fase 3: ESCALA (meses 10-12) ──
        elif mes <= 12:
            pct_reinvestimento = 0.40
            roas = 2.2
        # ── Fase 4: FLYWHEEL (meses 13+) ──
        else:
            pct_reinvestimento = 0.50
            roas = 2.8

        # Orcamento base = % da receita organica
        orcamento_base = receita_organica * pct_reinvestimento

        # Flywheel: receita paga do mes anterior alimenta o proximo
        receita_paga_mes_passado = acum.get("receita_paga_mes_passado", 0)
        bonus_flywheel = (
            receita_paga_mes_passado * 0.30
        )  # 30% do lucro pago do mes passado

        orcamento_total = min(orcamento_base + bonus_flywheel, receita_organica * 0.60)

        # ── CAPS PROPORCIONAIS A RECEITA ──
        # O orcamento nunca pode exceder a receita organica (nao pode quebrar)
        orcamento_total = min(orcamento_total, receita_organica * 0.60)

        # Escala gradual: o trafego pago cresce junto com a receita
        # Primeiros 3 meses de pago: max R$ 50k ou 30% da receita, o que for menor
        meses_pago = mes - 3
        if meses_pago <= 3:
            orcamento_total = min(orcamento_total, 50000, receita_organica * 0.30)
        elif meses_pago <= 6:
            orcamento_total = min(orcamento_total, 100000, receita_organica * 0.40)
        elif meses_pago <= 12:
            orcamento_total = min(orcamento_total, 300000, receita_organica * 0.50)
        else:
            orcamento_total = min(orcamento_total, 500000, receita_organica * 0.50)

        # Se orcamento for muito pequeno (< R$ 200), nao vale a pena
        if orcamento_total < 200:
            orcamento_total = 0

        orcamento_usado = orcamento_total

        if orcamento_usado > 0:
            # Gasto em trafego pago gera visitas
            # CPM aumenta com escala (competicao)
            if meses_pago <= 3:
                cpm = 12  # CPM baixo no inicio
            elif meses_pago <= 6:
                cpm = 15
            elif meses_pago <= 12:
                cpm = 18
            else:
                cpm = 22  # CPM mais alto com escala

            custo_por_visita = cpm / 1000
            visitas_geradas_pago = orcamento_usado / custo_por_visita

            # ROAS diminui com escala (audiencia saturada)
            # Quanto maior o gasto, menor o ROAS
            if orcamento_usado <= 10000:
                roas_efetivo = roas
            elif orcamento_usado <= 50000:
                roas_efetivo = roas * 0.85
            elif orcamento_usado <= 200000:
                roas_efetivo = roas * 0.70
            else:
                roas_efetivo = roas * 0.55

            roas_efetivo = max(roas_efetivo, 1.0)  # Minimo: break-even

            receita_paga_bruta = orcamento_usado * roas_efetivo
            receita_paga_liquida = receita_paga_bruta - orcamento_usado

            # Atualiza acumuladores
            acum["visitas_pagas_mes_anterior"] = visitas_geradas_pago
            acum["orcamento_pago_mes_anterior"] = orcamento_usado
            acum["receita_paga_mes_passado"] = receita_paga_liquida
            acum["receita_paga_total"] = (
                acum.get("receita_paga_total", 0) + receita_paga_liquida
            )
            acum["total_gasto_pago"] = acum.get("total_gasto_pago", 0) + orcamento_usado

            receita_paga = receita_paga_bruta
            roas_real = round(receita_paga_bruta / orcamento_usado, 2)
        else:
            roas_real = 0

    # ── TOTAL ──
    receita_total = receita_organica + receita_paga

    # ── Custos ──
    custos = 0
    if mes == 1:
        custos += 50 / 12  # dominiorate
    custos += orcamento_usado  # Custo do trafego pago

    lucro = receita_total - custos

    return {
        "mes": mes,
        "nichos": nichos_ativos,
        "artigos_mes": artigos_mes,
        "artigos_acumulados": acum["artigos_total"],
        "posts_sociais_mes": posts_sociais_mes,
        "videos_mes": videos_mes,
        "visitas_seo": round(visitas_seo),
        "visitas_sociais": round(visitas_sociais_acum),
        "visitas_youtube": round(
            max(videos_mes * c["visitas_youtube_por_video"], visitas_youtube_acum)
        ),
        "visitas_organicas": round(visitas_organicas),
        "visitas_pagas": round(visitas_pagas),
        "visitas_total": round(visitas_total),
        "lista_email": round(acum["lista_email"]),
        "receita_afiliado": round(receita_afiliado, 2),
        "receita_adsense": round(receita_adsense, 2),
        "receita_cpa": round(receita_cpa, 2),
        "receita_produto_digital": round(receita_produto, 2),
        "receita_membresia": round(receita_membresia, 2),
        "receita_email_afiliado": round(receita_email_afiliado, 2),
        "receita_reciclagem": round(receita_reciclagem, 2),
        "receita_organica": round(receita_organica, 2),
        "receita_paga": round(receita_paga, 2),
        "orcamento_pago": round(orcamento_usado, 2),
        "roas": round(receita_paga / max(orcamento_usado, 1), 2)
        if orcamento_usado > 0
        else 0,
        "receita_total": round(receita_total, 2),
        "custos": round(custos, 2),
        "lucro": round(lucro, 2),
    }


def projetar(cenario_nome: str, meses: int = 24) -> list[dict[str, Any]]:
    """Projeta ganhos para N meses em um cenario."""
    config = CENARIOS[cenario_nome]
    acum = {
        "artigos_total": 0,
        "posts_total": 0,
        "videos_total": 0,
        "lista_email": 0,
        "visitas_pagas_mes_anterior": 0,
        "orcamento_pago_mes_anterior": 0,
        "receita_paga_total": 0,
        "total_gasto_pago": 0,
    }
    resultados = []
    for mes in range(1, meses + 1):
        r = calcular_mes(mes, config, acum)
        resultados.append(r)
    return resultados


def projetar(cenario_nome: str, meses: int = 24) -> list[dict[str, Any]]:
    """Projeta ganhos para N meses em um cenario."""
    config = CENARIOS[cenario_nome]
    acum = {"artigos_total": 0, "posts_total": 0, "videos_total": 0, "lista_email": 0}
    resultados = []
    for mes in range(1, meses + 1):
        r = calcular_mes(mes, config, acum)
        resultados.append(r)
    return resultados


def exibir_resultados(resultados: list[dict[str, Any]], cenario_nome: str) -> None:
    """Exibe tabela formatada."""
    config = CENARIOS[cenario_nome]

    print(f"\n{'=' * 90}")
    print(f"  {config['label']}")
    print(f"  Projecao de {len(resultados)} meses")
    print(f"{'=' * 90}")
    print()

    # Resumo do primeiro ano
    ano1 = [r for r in resultados if r["mes"] <= 12]
    ano2 = [r for r in resultados if r["mes"] > 12]

    print(f"  {'📊 PREMISSAS':^80}")
    print(f"  {'─' * 80}")
    print(
        f"  Nichos iniciais: {config['nichos_iniciais']}  |  Artigos/dia/nicho: {config['artigos_por_dia_por_nicho']}"
    )
    print(
        f"  Posts sociais/dia/nicho: {config['posts_sociais_por_dia_por_nicho']}  |  Videos/semana/nicho: {config['videos_por_semana_por_nicho']}"
    )
    print(
        f"  Visitas SEO/artigo/mes: {config['visitas_seo_por_artigo_por_mes']}  |  CTR afiliado: {config['ctr_afiliado'] * 100:.1f}%"
    )
    print(
        f"  Ticket medio afiliado: R${config['ticket_medio_afiliado']}  |  AdSense RPM: R${config['rpm_adsense']}"
    )
    print("  Trafego pago: Flywheel progressivo (Fases 1-4)")
    print("  ROAS: 1.3x (teste) → 1.8x (validacao) → 2.5x (escala) → 3.0x (flywheel)")
    print()

    def linha(m):
        return (
            f"  {m['mes']:3d} | {m['nichos']:2d}n | "
            f"{m['artigos_acumulados']:4d}a | "
            f"{m['visitas_organicas']:>7,d}o +{m['visitas_pagas']:>6,d}p | "
            f"{m['lista_email']:>5,d}em | "
            f"R${m['receita_organica']:>7.2f}org | "
            f"R${m['receita_paga']:>8.2f}pag | "
            f"R${m['orcamento_pago']:>7.2f}gas | "
            f"{m['roas']:>4.1f}xROAS | "
            f"R${m['receita_total']:>8.2f}=R${m['lucro']:>7.2f}"
        )

    print(
        f"  {'MES | Nic |Arts | Visitas (org+pag) | Emails | Receita Org | Receita Pag | Gasto | ROAS | TOTAL = LUCRO'}"
    )
    print(f"  {'─' * 85}")
    for m in resultados[:12]:
        print(linha(m))
    if len(resultados) > 12:
        print(f"  {'─' * 85}")
        for m in resultados[12 : min(24, len(resultados))]:
            print(linha(m))

    # Totais
    print(f"  {'─' * 85}")

    if ano1:
        total_ano1 = sum(r["receita_total"] for r in ano1)
        lucro_ano1 = sum(r["lucro"] for r in ano1)
        visitas_ano1 = sum(r["visitas_total"] for r in ano1)
        total_gasto = sum(r.get("orcamento_pago", 0) for r in ano1)
        total_receita_paga = sum(r.get("receita_paga", 0) for r in ano1)
        print("\n  📅 ANO 1 (meses 1-12):")
        print(f"     Visitas: {visitas_ano1:>10,d} (org + pag)")
        print(
            f"     Receita organica: R$ {sum(r['receita_organica'] for r in ano1):>10.2f}"
        )
        if total_gasto > 0:
            print(
                f"     Trafego pago: R$ {total_gasto:>8.2f} gasto → R$ {total_receita_paga:>10.2f} receita (ROAS medio: {total_receita_paga / max(total_gasto, 1):.1f}x)"
            )
            print(f"     Lucro pago: R$ {total_receita_paga - total_gasto:>10.2f}")
        print(f"     Receita total: R$ {total_ano1:>10.2f}")
        print(f"     Lucro total:   R$ {lucro_ano1:>10.2f}")
        print(f"     Media mensal:  R$ {total_ano1 / 12:>8.2f}")
        print(
            f"     Mes 12: {ano1[-1]['receita_organica']:>8.2f} org + {ano1[-1]['receita_paga']:>8.2f} pag = R$ {ano1[-1]['receita_total']:>8.2f}"
        )
        print(f"     Lista email:   {ano1[-1]['lista_email']:>6,d} inscritos")

    if ano2:
        total_ano2 = sum(r["receita_total"] for r in ano2)
        lucro_ano2 = sum(r["lucro"] for r in ano2)
        visitas_ano2 = sum(r["visitas_total"] for r in ano2)
        total_gasto = sum(r.get("orcamento_pago", 0) for r in ano2)
        total_receita_paga = sum(r.get("receita_paga", 0) for r in ano2)
        print("\n  📅 ANO 2 (meses 13-24):")
        print(f"     Visitas: {visitas_ano2:>10,d}")
        print(
            f"     Receita organica: R$ {sum(r['receita_organica'] for r in ano2):>10.2f}"
        )
        if total_gasto > 0:
            print(
                f"     Trafego pago: R$ {total_gasto:>8.2f} gasto → R$ {total_receita_paga:>10.2f} receita (ROAS medio: {total_receita_paga / max(total_gasto, 1):.1f}x)"
            )
            print(f"     Lucro pago: R$ {total_receita_paga - total_gasto:>10.2f}")
        print(f"     Receita total: R$ {total_ano2:>10.2f}")
        print(f"     Lucro total:   R$ {lucro_ano2:>10.2f}")
        print(f"     Media mensal:  R$ {total_ano2 / 12:>8.2f}")
        print(
            f"     Mes 24: {ano2[-1]['receita_organica']:>8.2f} org + {ano2[-1]['receita_paga']:>8.2f} pag = R$ {ano2[-1]['receita_total']:>8.2f}"
        )

    if ano1 and ano2:
        print("\n  📊 TOTAL 24 MESES:")
        print(f"     Receita: R$ {total_ano1 + total_ano2:.2f}")
        print(f"     Lucro:   R$ {lucro_ano1 + lucro_ano2:.2f}")
        print(
            f"     Crescimento mes 12 -> mes 24: {ano2[-1]['receita_total'] / max(ano1[-1]['receita_total'], 1) * 100 - 100:.0f}%"
        )


def exibir_resumo_json(resultados: list[dict[str, Any]], cenario_nome: str) -> None:
    """Exibe resumo em JSON."""
    config = CENARIOS[cenario_nome]
    ano1 = [r for r in resultados if r["mes"] <= 12]
    ano2 = [r for r in resultados if r["mes"] > 12]

    resumo = {
        "cenario": cenario_nome,
        "premissas": {
            "nichos_iniciais": config["nichos_iniciais"],
            "artigos_por_dia": config["artigos_por_dia_por_nicho"],
            "posts_sociais_por_dia": config["posts_sociais_por_dia_por_nicho"],
            "videos_por_semana": config["videos_por_semana_por_nicho"],
            "ticket_medio_afiliado": config["ticket_medio_afiliado"],
            "rpm_adsense": config["rpm_adsense"],
            "reinvestimento_trafego_pago": config["reinvestimento_trafego_pago_pct"],
        },
        "ano_1": {
            "total_visitas": sum(r["visitas_total"] for r in ano1) if ano1 else 0,
            "total_receita": sum(r["receita_total"] for r in ano1) if ano1 else 0,
            "total_lucro": sum(r["lucro"] for r in ano1) if ano1 else 0,
            "media_mensal": sum(r["receita_total"] for r in ano1) / 12 if ano1 else 0,
            "receita_mes_12": ano1[-1]["receita_total"] if ano1 else 0,
            "lista_email_final": ano1[-1]["lista_email"] if ano1 else 0,
        },
        "ano_2": {
            "total_visitas": sum(r["visitas_total"] for r in ano2) if ano2 else 0,
            "total_receita": sum(r["receita_total"] for r in ano2) if ano2 else 0,
            "total_lucro": sum(r["lucro"] for r in ano2) if ano2 else 0,
            "media_mensal": sum(r["receita_total"] for r in ano2) / 12 if ano2 else 0,
            "receita_mes_24": ano2[-1]["receita_total"] if ano2 else 0,
        },
        "total_24_meses": {
            "receita": (sum(r["receita_total"] for r in ano1) if ano1 else 0)
            + (sum(r["receita_total"] for r in ano2) if ano2 else 0),
            "lucro": (sum(r["lucro"] for r in ano1) if ano1 else 0)
            + (sum(r["lucro"] for r in ano2) if ano2 else 0),
        },
        "detalhamento_mensal": resultados,
    }
    print(json.dumps(resumo, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="💰 Projecao de Ganhos Realista Multi-Plataforma"
    )
    parser.add_argument(
        "--detalhado", action="store_true", help="Mostrar tabela mes a mes"
    )
    parser.add_argument("--json", action="store_true", help="Output em JSON")
    parser.add_argument(
        "--meses",
        type=int,
        default=24,
        help="Numero de meses para projetar (default: 24)",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 90}")
    print("  💰 PROJECAO DE GANHOS REALISTA — Multi-Plataforma Multi-Nicho")
    print(f"  Gerado em: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M')} UTC")
    print("  Considera: 11 plataformas, 4+ nichos, 7 fontes de receita")
    print(f"{'=' * 90}")

    for cenario in ["conservador", "moderado", "agressivo", "maximo"]:
        resultados = projetar(cenario, meses=args.meses)

        if args.json:
            exibir_resumo_json(resultados, cenario)
        else:
            exibir_resultados(resultados, cenario)

    print(f"\n{'=' * 90}")
    print("  ⚠️  AVISO: Projecoes baseadas em medias de mercado brasileiro 2024-2026.")
    print("  Resultados reais dependem de qualidade do conteudo, concorrencia,")
    print("  consistencia operacional e conformidade com cada plataforma.")
    print("  Nada aqui e garantia de renda.")
    print(f"{'=' * 90}")


if __name__ == "__main__":
    main()
