"""HotmartProductResearcherAgent — Pesquisa e ranqueia os melhores produtos Hotmart por nicho.

Faz análise multilcritério:
- Comissão (%)
- Faixa de preço
- Demanda de mercado
- Conversão estimada
- Velocidade para primeiro ganho
- Saturação/concorrência
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("hotmart_researcher")

# ── Conhecimento de mercado Hotmart ──────────────────────────────────


@dataclass
class HotmartProductProfile:
    """Perfil de um tipo de produto Hotmart com metadados de mercado."""

    category: str
    product_type: str  # curso, ebook, mentoria, comunidade, ferramenta
    avg_price_brl: float
    avg_commission_pct: float
    demand_score: float  # 0-10
    conversion_difficulty: float  # 0-10 (menor = mais facil)
    saturation: float  # 0-10 (maior = mais concorrido)
    speed_to_money: float  # 0-10 (maior = mais rapido)
    cookie_days: int = 30
    description: str = ""

    @property
    def earnings_per_sale(self) -> float:
        return self.avg_price_brl * (self.avg_commission_pct / 100)

    @property
    def velocity_score(self) -> float:
        """Score composto priorizando velocidade de ganhos."""
        return (
            self.speed_to_money * 3.0
            + (10 - self.conversion_difficulty) * 2.0
            + (self.avg_commission_pct / 10) * 1.5
            + self.demand_score * 1.0
            + (10 - self.saturation) * 0.5
        )


# Base de conhecimento de produtos Hotmart de alto desempenho
PRODUCT_KNOWLEDGE_BASE: dict[str, list[HotmartProductProfile]] = {
    "tecnologia": [
        HotmartProductProfile(
            "Programacao Web Full Stack",
            "curso",
            97.0,
            60.0,
            9.0,
            4.0,
            7.0,
            7.0,
            30,
            "Curso completo de desenvolvimento web — alta demanda constante",
        ),
        HotmartProductProfile(
            "Inteligencia Artificial p/ Iniciantes",
            "curso",
            67.0,
            60.0,
            9.5,
            3.0,
            5.0,
            9.0,
            30,
            "IA esta em alta — produto novo com menos concorrencia",
        ),
        HotmartProductProfile(
            "Pacote Python do Zero",
            "curso",
            47.0,
            50.0,
            8.5,
            3.0,
            6.0,
            8.0,
            30,
            "Preco acessivel, facil conversao",
        ),
        HotmartProductProfile(
            "Excel do Basico ao Avancado",
            "curso",
            37.0,
            60.0,
            8.0,
            2.0,
            8.0,
            9.0,
            30,
            "Produto classico, conversao muito alta",
        ),
        HotmartProductProfile(
            "Ferramenta de Automacao de Tarefas",
            "ferramenta",
            197.0,
            30.0,
            7.5,
            5.0,
            4.0,
            6.0,
            30,
            "Ticket alto mas comissao menor",
        ),
        HotmartProductProfile(
            "Apps para Produtividade (Android/iOS)",
            "software",
            27.0,
            40.0,
            8.0,
            2.0,
            5.0,
            9.0,
            30,
            "Preco baixo = conversao muito alta",
        ),
        HotmartProductProfile(
            "Comunidade de Devs",
            "comunidade",
            33.0,
            60.0,
            7.0,
            4.0,
            4.0,
            7.0,
            30,
            "Receita recorrente via assinatura",
        ),
        HotmartProductProfile(
            "Curso de Ciberseguranca",
            "curso",
            87.0,
            50.0,
            8.0,
            5.0,
            4.0,
            7.0,
            30,
            "Area quente, boa comissao",
        ),
        HotmartProductProfile(
            "Pacote de Templates Web",
            "template",
            27.0,
            60.0,
            7.5,
            1.0,
            6.0,
            9.0,
            30,
            "Preco baixo, comissao alta, conversao facil",
        ),
        HotmartProductProfile(
            "Curso de Marketing Digital",
            "curso",
            77.0,
            50.0,
            9.0,
            4.0,
            7.0,
            7.0,
            30,
            "Mercado sempre aquecido",
        ),
    ],
    "financas": [
        HotmartProductProfile(
            "Curso de Investimentos p/ Iniciantes",
            "curso",
            67.0,
            50.0,
            9.0,
            3.0,
            6.0,
            8.0,
            30,
            "Brasileiro quer aprender a investir",
        ),
        HotmartProductProfile(
            "Planilha de Controle Financeiro",
            "planilha",
            27.0,
            70.0,
            8.5,
            1.0,
            3.0,
            10.0,
            30,
            "Comissao altissima, preco baixo — conversao instantanea",
        ),
        HotmartProductProfile(
            "Guia de Renda Extra Online",
            "ebook",
            37.0,
            70.0,
            9.0,
            2.0,
            4.0,
            9.0,
            30,
            "Promessa de renda vende muito",
        ),
        HotmartProductProfile(
            "Curso de Bolsa de Valores",
            "curso",
            97.0,
            50.0,
            7.5,
            5.0,
            5.0,
            6.0,
            30,
            "Ticket alto, publico qualificado",
        ),
        HotmartProductProfile(
            "Ebook Pai Rico Pai Pobre Alternativo",
            "ebook",
            17.0,
            70.0,
            8.0,
            1.0,
            5.0,
            10.0,
            30,
            "Preco baixissimo, comissao maxima",
        ),
        HotmartProductProfile(
            "Metodo de Criptomoedas",
            "curso",
            147.0,
            50.0,
            8.0,
            6.0,
            7.0,
            6.0,
            30,
            "Alta volatilidade = alto interesse",
        ),
        HotmartProductProfile(
            "Assessoria Financeira Digital",
            "mentoria",
            197.0,
            40.0,
            7.0,
            7.0,
            3.0,
            4.0,
            30,
            "Ticket alto, conversao dificil",
        ),
        HotmartProductProfile(
            "Curso de Liberdade Financeira",
            "curso",
            47.0,
            60.0,
            9.0,
            3.0,
            6.0,
            9.0,
            30,
            "Preco medio, comissao boa, alta demanda",
        ),
        HotmartProductProfile(
            "Pacote de Cursos Financas",
            "curso",
            127.0,
            60.0,
            8.0,
            4.0,
            5.0,
            7.0,
            30,
            "Ticket alto com comissao boa",
        ),
        HotmartProductProfile(
            "Planilha de Orcamento Inteligente",
            "planilha",
            17.0,
            70.0,
            8.0,
            1.0,
            3.0,
            10.0,
            30,
            "Mais barato possivel, comissao 70%",
        ),
    ],
    "saude": [
        HotmartProductProfile(
            "Guia de Alimentacao Saudavel",
            "ebook",
            27.0,
            60.0,
            8.0,
            2.0,
            5.0,
            9.0,
            30,
            "Publico amplo, conversao facil",
        ),
        HotmartProductProfile(
            "Curso de Exercicios em Casa",
            "curso",
            47.0,
            50.0,
            8.5,
            3.0,
            5.0,
            8.0,
            30,
            "Home fitness cresceu muito",
        ),
        HotmartProductProfile(
            "Protocolo de Emagrecimento",
            "curso",
            67.0,
            60.0,
            9.0,
            4.0,
            7.0,
            8.0,
            30,
            "Emagrecimento e o nicho mais quente da saude",
        ),
        HotmartProductProfile(
            "Curso de Meditacao Guiada",
            "curso",
            37.0,
            60.0,
            7.5,
            2.0,
            4.0,
            9.0,
            30,
            "Saude mental em alta",
        ),
        HotmartProductProfile(
            "Guia de Sono Reparador",
            "ebook",
            27.0,
            70.0,
            7.5,
            2.0,
            3.0,
            9.0,
            30,
            "Problema universal, solucao simples",
        ),
        HotmartProductProfile(
            "Suplementos Naturais Guia",
            "ebook",
            37.0,
            60.0,
            7.0,
            3.0,
            4.0,
            8.0,
            30,
            "Nichado mas consistente",
        ),
        HotmartProductProfile(
            "Curso de Yoga Digital",
            "curso",
            47.0,
            50.0,
            7.0,
            3.0,
            4.0,
            7.0,
            30,
            "Publico fiel e engajado",
        ),
        HotmartProductProfile(
            "Comunidade Fit",
            "comunidade",
            27.0,
            60.0,
            8.0,
            4.0,
            5.0,
            8.0,
            30,
            "Receita recorrente, prezando comunidade",
        ),
    ],
    "carreira": [
        HotmartProductProfile(
            "Curso de Linkedin",
            "curso",
            37.0,
            60.0,
            9.0,
            2.0,
            5.0,
            9.0,
            30,
            "Preco acessivel, alta procura",
        ),
        HotmartProductProfile(
            "Guia de Entrevista de Emprego",
            "ebook",
            27.0,
            70.0,
            8.5,
            1.0,
            4.0,
            10.0,
            30,
            "Desemprego impulsiona busca",
        ),
        HotmartProductProfile(
            "Curso de Oratoria",
            "curso",
            47.0,
            50.0,
            8.0,
            3.0,
            4.0,
            8.0,
            30,
            "Habilidade universal, sempre requisitada",
        ),
        HotmartProductProfile(
            "Pacote de Curriculo Perfeito",
            "template",
            17.0,
            60.0,
            9.0,
            1.0,
            3.0,
            10.0,
            30,
            "Preco minimo, conversao instantanea",
        ),
        HotmartProductProfile(
            "Mentoria de Carreira",
            "mentoria",
            197.0,
            40.0,
            7.0,
            7.0,
            4.0,
            4.0,
            30,
            "Ticket alto mas conversao dificil",
        ),
        HotmartProductProfile(
            "Curso de Produtividade",
            "curso",
            47.0,
            60.0,
            8.0,
            3.0,
            5.0,
            8.0,
            30,
            "Demanda constante em todos os nichos",
        ),
        HotmartProductProfile(
            "Guia de Freelancer",
            "ebook",
            27.0,
            70.0,
            8.0,
            2.0,
            4.0,
            9.0,
            30,
            "Trabalho autonomo em alta",
        ),
        HotmartProductProfile(
            "Curso de Lideranca",
            "curso",
            67.0,
            50.0,
            7.5,
            4.0,
            4.0,
            7.0,
            30,
            "Publico corporativo, ticket medio",
        ),
    ],
}

# Nichos que usamos
NICHES = ["tecnologia", "financas", "saude", "carreira"]


class HotmartProductResearcherAgent(AgentBase):
    """Pesquisa e ranqueia os melhores produtos Hotmart por nicho.

    Usa base de conhecimento interna (analise de mercado) para
    recomendar produtos com maior potencial de ganhos rapidos.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("hotmart_product_researcher", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            niche = campaign.get("niche", "all").lower()
            max_results = campaign.get("max_results", 5)
            min_velocity = campaign.get("min_velocity", 0.0)

            if niche == "all" or niche not in PRODUCT_KNOWLEDGE_BASE:
                # Pesquisar todos os nichos
                results: dict[str, list[dict[str, Any]]] = {}
                for n in NICHES:
                    results[n] = self._research_niche(n, max_results, min_velocity)
                total = sum(len(r) for r in results.values())

                finished_at = datetime.now(timezone.utc).isoformat()
                trace = AgentTrace(
                    agent=self.name,
                    step_id="research_all",
                    status="success",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    notes=[f"nichos: {len(results)}", f"produtos: {total}"],
                )
                return AgentResult(
                    agent=self.name,
                    status="success",
                    output={
                        "action": "research_all",
                        "results": results,
                        "total_products": total,
                        "recommendation": self._generate_recommendation(results),
                    },
                    trace=trace,
                )
            else:
                # Pesquisar nicho especifico
                results_list = self._research_niche(niche, max_results, min_velocity)

                finished_at = datetime.now(timezone.utc).isoformat()
                trace = AgentTrace(
                    agent=self.name,
                    step_id=f"research_{niche}",
                    status="success",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    notes=[f"nicho: {niche}", f"produtos: {len(results_list)}"],
                )
                return AgentResult(
                    agent=self.name,
                    status="success",
                    output={
                        "action": "research_niche",
                        "niche": niche,
                        "results": results_list,
                        "total_products": len(results_list),
                    },
                    trace=trace,
                )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="research",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    error=str(e)[:500],
                ),
            )

    def _research_niche(
        self, niche: str, max_results: int, min_velocity: float
    ) -> list[dict[str, Any]]:
        """Pesquisa e ranqueia produtos para um nicho."""
        products = PRODUCT_KNOWLEDGE_BASE.get(niche, [])

        # Calcular scores
        scored = []
        for p in products:
            score = p.velocity_score
            if score < min_velocity:
                continue
            scored.append(
                {
                    "product_name": p.category,
                    "product_type": p.product_type,
                    "niche": niche,
                    "avg_price_brl": p.avg_price_brl,
                    "avg_commission_pct": p.avg_commission_pct,
                    "earnings_per_sale": round(p.earnings_per_sale, 2),
                    "demand_score": p.demand_score,
                    "conversion_difficulty": p.conversion_difficulty,
                    "saturation": p.saturation,
                    "speed_to_money": p.speed_to_money,
                    "velocity_score": round(score, 2),
                    "cookie_days": p.cookie_days,
                    "description": p.description,
                    "_hotmart_url_placeholder": f"https://hotm.art/{niche}-{p.product_type}?aff=SEUCODIGO",
                }
            )

        # Ordenar por velocity_score (maior primeiro)
        scored.sort(key=lambda x: x["velocity_score"], reverse=True)
        return scored[:max_results]

    def _generate_recommendation(self, results: dict[str, list[dict[str, Any]]]) -> str:
        """Gera recomendacao textual dos melhores produtos."""
        lines = ["🎯 RECOMENDACAO DE PRODUTOS HOTMART", ""]
        all_products = []
        for niche, products in results.items():
            if products:
                lines.append(f"📌 {niche.upper()}:")
                for p in products:
                    lines.append(
                        f"  • {p['product_name']} — R${p['avg_price_brl']:.0f} | "
                        f"Comissão: {p['avg_commission_pct']:.0f}% | "
                        f"Velocidade: {p['velocity_score']:.1f}"
                    )
                    all_products.append(p)
                lines.append("")

        if all_products:
            top = all_products[0]
            lines.append(f"🚀 TOP 1 ABSOLUTO: {top['product_name']} ({top['niche']})")
            lines.append(
                f"   Motivo: R${top['earnings_per_sale']:.2f}/venda | "
                f"Velocidade {top['speed_to_money']:.0f}/10 | "
                f"Dificuldade {top['conversion_difficulty']:.0f}/10"
            )

        return "\n".join(lines)


class HotmartAffiliateSelectorAgent(AgentBase):
    """Seleciona os melhores produtos para se afiliar, priorizando ganhos rapidos.

    Usa os resultados do HotmartProductResearcherAgent e aplica
    criterios adicionais de selecao para maximizar ROI imediato.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("hotmart_affiliate_selector", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            products = campaign.get("products", [])
            niche = campaign.get("niche", "all")
            budget_tier = campaign.get(
                "budget_tier", "rapido"
            )  # rapido, equilibrio, ticket_alto

            if not products:
                # Se nao recebeu produtos, pesquisa primeiro
                researcher = HotmartProductResearcherAgent()
                research_ctx = CampaignContext(
                    campaign={"niche": niche, "max_results": 10}
                )
                research_result = researcher.run(research_ctx)
                if research_result.status == "success":
                    if niche == "all":
                        all_prods = []
                        for n_res in research_result.output.get("results", {}).values():
                            all_prods.extend(n_res)
                        products = all_prods
                    else:
                        products = research_result.output.get("results", [])
                else:
                    raise ValueError("Nao foi possivel pesquisar produtos")

            # Aplicar criterios de selecao
            selected = self._select_best(products, budget_tier)

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="select",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"analisados: {len(products)}",
                    f"selecionados: {len(selected)}",
                    f"tier: {budget_tier}",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "total_analyzed": len(products),
                    "total_selected": len(selected),
                    "selected": selected,
                    "budget_tier": budget_tier,
                    "selection_criteria": self._criteria_explanation(budget_tier),
                    "hunt_list": self._generate_hunt_list(selected),
                },
                trace=trace,
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="select",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    error=str(e)[:500],
                ),
            )

    def _select_best(
        self, products: list[dict[str, Any]], tier: str
    ) -> list[dict[str, Any]]:
        """Seleciona os melhores produtos baseado no tier de estrategia."""
        if tier == "rapido":
            # Prioridade: velocidade > preco baixo > comissao alta > saturacao baixa
            for p in products:
                p["_selection_score"] = (
                    p.get("speed_to_money", 5) * 4.0
                    + (10 - p.get("conversion_difficulty", 5)) * 3.0
                    + (10 - p.get("saturation", 5)) * 2.0
                    + (p.get("avg_commission_pct", 50) / 10) * 1.5
                    + (10 - min(p.get("avg_price_brl", 50) / 30, 10)) * 1.0
                )

        elif tier == "equilibrio":
            # Equilibrio entre ticket e velocidade
            for p in products:
                p["_selection_score"] = (
                    p.get("velocity_score", 0) * 2.0
                    + p.get("earnings_per_sale", 0) / 10 * 2.0
                    + p.get("demand_score", 5) * 1.5
                    + (10 - p.get("conversion_difficulty", 5)) * 1.0
                )

        elif tier == "ticket_alto":
            # Prioridade: maior ganho por venda
            for p in products:
                p["_selection_score"] = (
                    p.get("earnings_per_sale", 0) / 5 * 3.0
                    + p.get("avg_price_brl", 0) / 20 * 2.0
                    + p.get("demand_score", 5) * 1.5
                    + p.get("velocity_score", 0) * 0.5
                )
        else:
            for p in products:
                p["_selection_score"] = p.get("velocity_score", 0)

        # Ordenar e pegar top 3
        products.sort(key=lambda x: x["_selection_score"], reverse=True)
        return products[:3]

    def _criteria_explanation(self, tier: str) -> str:
        explanations = {
            "rapido": "Priorizamos produtos com PREÇO BAIXO, COMISSÃO ALTA e BAIXA CONCORRÊNCIA — "
            "o que maximiza a velocidade de conversão e primeiros ganhos.",
            "equilibrio": "Buscamos o EQUILÍBRIO entre ticket médio, taxa de comissão e volume de busca — "
            "estratégia ideal para construir receita consistente.",
            "ticket_alto": "Foco em produtos de TICKET ALTO que pagam mais por venda — "
            "ideal quando voce ja tem trafego qualificado.",
        }
        return explanations.get(tier, explanations["rapido"])

    def _generate_hunt_list(self, selected: list[dict[str, Any]]) -> str:
        """Gera lista de 'caca' — produtos que o usuario precisa pegar o link."""
        lines = ["🔍 LISTA DE PRODUTOS PARA COLETAR LINKS", ""]
        for i, p in enumerate(selected, 1):
            lines.append(f"{i}. {p['product_name']}")
            lines.append(
                f"   Nicho: {p.get('niche', '?')} | Preço: R${p['avg_price_brl']:.0f} | "
                f"Comissão: {p['avg_commission_pct']:.0f}%"
            )
            lines.append(
                f"   Ganho/venda: R${p['earnings_per_sale']:.2f} | "
                f"Score: {p.get('_selection_score', 0):.1f}"
            )
            lines.append(
                f"   🔗 Acesse: https://hotmart.com → Catálogo → busque '{p['product_name']}'"
            )
            lines.append("   📋 Depois cole o link aqui no chat!")
            lines.append("")
        lines.append("Quer que eu comece por algum nicho especifico?")
        return "\n".join(lines)
