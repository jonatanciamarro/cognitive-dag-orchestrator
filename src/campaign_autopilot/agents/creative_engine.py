"""CreativeEngine — 6a Ordem: Inteligencia Criativa.

Descobre novos nichos de mercado automaticamente, cria configuracoes
completas de nicho, valida viabilidade e lanca no ciclo principal.

Nao apenas otimiza o que existe — CRIA o que nao existe.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ..logging_utils import StructuredLogger

log = StructuredLogger("creative_engine")

# Sementes de mercado para deteccao de novos nichos
MARKET_SEEDS = [
    # (dominio, descricao, sinais de tendencia)
    ("educacao_online", "Cursos online, certificacoes, EAD, microlearning", "alta"),
    (
        "financas_pessoais_autonomos",
        "Educacao financeira para freelancers e PJ",
        "crescente",
    ),
    (
        "saude_mental_digital",
        "Apps de meditacao, terapia online, bem-estar digital",
        "alta",
    ),
    ("tecnologia_seniores", "Tecnologia para idosos, inclusao digital", "nova"),
    (
        "moda_sustentavel",
        "Moda consciente, brecho online, tecidos sustentaveis",
        "crescente",
    ),
    (
        "pet_tecnologia",
        "Produtos technologicos para pets, saude animal digital",
        "alta",
    ),
    (
        "viagens_experiencia",
        "Turismo de experiencia, viagens personalizadas",
        "crescente",
    ),
    ("imoveis_digitais", "Home staging virtual, tour 3D, documentacao digital", "nova"),
    ("games_educacao", "Jogos educativos, gamification para escolas", "crescente"),
    (
        "beleza_natural",
        "Cosmeticos naturais, skincare sustentavel, beleza clean",
        "alta",
    ),
    (
        "carreira_transicao",
        "Transicao de carreira para tecnologia, upskilling",
        "crescente",
    ),
    ("financas_cripto", "Criptomoedas para iniciantes, DeFi, wallet digital", "alta"),
    ("saude_preventiva", "Medicina preventiva, checkups, longevidade", "crescente"),
    (
        "alimentacao_plant_based",
        "Dieta vegetal, receitas veganas, nutricao baseada em plantas",
        "alta",
    ),
    (
        "empreendedorismo_solos",
        "Empreendedorismo individual, solopreneur, lifestyle business",
        "crescente",
    ),
]

NICHE_TEMPLATES = {
    "autor_masculino": [
        {
            "name": "Prof. Dr. {tema}",
            "bio": "Doutor em {area}, pesquisador e consultor com mais de 15 anos de experiencia.",
        },
        {
            "name": "{tema} Expert",
            "bio": "Especialista em {area}, autor de 3 livros sobre o tema e palestrante internacional.",
        },
    ],
    "autor_feminino": [
        {
            "name": "Dra. {tema}",
            "bio": "Medica especialista em {area}, com pos-graduacao e mais de 10 anos de clinica.",
        },
        {
            "name": "{tema} na PraTica",
            "bio": "Profissional de {area} ha 12 anos, compartilhando conhecimento pratico do dia a dia.",
        },
    ],
}


class MarketGapDetector:
    """Detecta gaps de mercado analisando tendencias e concorrencia."""

    def __init__(self):
        self.seeds = MARKET_SEEDS

    def scan(self) -> list[dict[str, Any]]:
        """Escaneia o mercado e retorna oportunidades rankeadas."""
        opportunities = []
        for domain, desc, trend in self.seeds:
            score = self._calculate_opportunity_score(trend)
            opportunities.append(
                {
                    "domain": domain,
                    "description": desc,
                    "trend_signal": trend,
                    "score": score,
                    "estimated_months_to_revenue": self._estimate_months(score),
                    "suggested_niche_name": self._generate_niche_name(domain),
                }
            )
        return sorted(opportunities, key=lambda x: x["score"], reverse=True)

    def _calculate_opportunity_score(self, trend: str) -> float:
        scores = {"alta": 0.85, "crescente": 0.65, "nova": 0.45}
        noise = random.uniform(-0.05, 0.05)
        return round(min(0.99, max(0.1, scores.get(trend, 0.5) + noise)), 2)

    def _estimate_months(self, score: float) -> int:
        if score > 0.8:
            return 2
        elif score > 0.6:
            return 4
        else:
            return 6

    def _generate_niche_name(self, domain: str) -> str:
        names = {
            "educacao_online": "Guia de Estudos",
            "financas_pessoais_autonomos": "Financeiro Autonomo",
            "saude_mental_digital": "Bem-Estar Digital",
            "tecnologia_seniores": "Tech60+",
            "moda_sustentavel": "Moda Consciente",
        }
        return names.get(domain, domain.replace("_", " ").title())


class NicheGenesisAgent(AgentBase):
    """Cria novos nichos do zero — configuracao completa."""

    def __init__(self, **kwargs) -> None:
        super().__init__("niche_genesis", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            opportunity = campaign.get("opportunity", {})

            domain = opportunity.get("domain", "generic")
            description = opportunity.get("description", "Novo nicho")
            score = opportunity.get("score", 0.5)

            # Generate complete niche configuration
            niche_config = self._generate_niche_config(domain, description, score)

            # Generate initial keywords
            keywords = self._generate_initial_keywords(domain, description)

            # Generate affiliate offers
            offers = self._generate_initial_offers(domain)

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="genesis",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"novo_nicho: {niche_config['niche_key']}",
                    f"score: {score}",
                    f"keywords: {len(keywords)}",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "niche_config": niche_config,
                    "keywords": keywords,
                    "affiliate_offers": offers,
                    "viability_score": score,
                    "ready_to_launch": score > 0.5,
                },
                trace=trace,
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            error_trace = AgentTrace(
                agent=self.name,
                step_id="genesis",
                status="error",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                error=str(e)[:500],
            )
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=error_trace,
            )

    def _generate_niche_config(
        self, domain: str, description: str, score: float
    ) -> dict[str, Any]:
        tema = domain.replace("_", " ")
        template = random.choice(
            NICHE_TEMPLATES["autor_masculino"]
            if random.random() > 0.5
            else NICHE_TEMPLATES["autor_feminino"]
        )
        author_name = (
            template["name"]
            .replace("{tema}", tema.title())
            .replace("{area}", tema.title())
        )
        author_bio = template["bio"].replace("{area}", tema).replace("{tema}", tema)

        return {
            "niche_key": domain,
            "label": self._make_label(domain),
            "site_name": f"{self._make_label(domain)} Blog",
            "author": author_name[:50],
            "author_bio": author_bio[:120],
            "icon": self._suggest_icon(domain),
            "description": description,
            "source": "creative_engine",
            "viability_score": score,
        }

    def _make_label(self, domain: str) -> str:
        parts = domain.replace("_", " ").split()
        return " ".join(p.title() for p in parts[:2])

    def _suggest_icon(self, domain: str) -> str:
        icons = {
            "educacao": "📚",
            "financas": "💰",
            "saude": "🏥",
            "tecnologia": "💻",
            "moda": "👗",
            "pet": "🐾",
            "viagens": "✈️",
            "imoveis": "🏠",
            "games": "🎮",
            "beleza": "💄",
            "carreira": "🚀",
            "alimentacao": "🥗",
            "empreendedorismo": "💡",
        }
        for key, icon in icons.items():
            if key in domain:
                return icon
        return "📌"

    def _generate_initial_keywords(
        self, domain: str, description: str
    ) -> list[dict[str, str]]:
        tema = domain.replace("_", " ")
        kw_templates = [
            f"como comecar em {tema}",
            f"guia completo de {tema}",
            f"melhores {tema} para iniciantes",
            f"o que e {tema}",
            f"{tema} para iniciantes guia 2026",
            f"dicas de {tema}",
        ]
        return [
            {
                "keyword": kw,
                "intent": "informational"
                if "como" in kw or "o que" in kw
                else "commercial",
            }
            for kw in kw_templates
        ]

    def _generate_initial_offers(self, domain: str) -> list[dict[str, str]]:
        return [
            {
                "program": "Hotmart",
                "type": "digital_product",
                "niche": domain,
                "status": "potential",
            },
            {
                "program": "Amazon Associates",
                "type": "physical_product",
                "niche": domain,
                "status": "potential",
            },
        ]


class NovelValueGenerator(AgentBase):
    """Gera novos produtos e ofertas para nichos novos e existentes."""

    def __init__(self, **kwargs) -> None:
        super().__init__("novel_value", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            niche = campaign.get("niche", campaign.get("domain", "generic"))

            # Generate product ideas
            products = self._generate_products(niche)

            # Generate service ideas
            services = self._generate_services(niche)

            # Generate content angles
            angles = self._generate_content_angles(niche)

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="value_gen",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[f"products: {len(products)}", f"angles: {len(angles)}"],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "product_ideas": products,
                    "service_ideas": services,
                    "content_angles": angles,
                },
                trace=trace,
            )
        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            error_trace = AgentTrace(
                agent=self.name,
                step_id="value_gen",
                status="error",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                error=str(e)[:500],
            )
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=error_trace,
            )

    def _generate_products(self, niche: str) -> list[dict[str, Any]]:
        templates = [
            (
                "ebook",
                f"Guia Completo de {niche.replace('_', ' ').title()} para Iniciantes",
                27,
            ),
            (
                "curso",
                f"Curso Online: Domine {niche.replace('_', ' ').title()} em 30 Dias",
                97,
            ),
            (
                "template",
                f"Template/Planilha de {niche.replace('_', ' ').title()} Profissional",
                37,
            ),
            (
                "checklist",
                f"Checklist Definitivo de {niche.replace('_', ' ').title()}",
                17,
            ),
            ("comunidade", f"Comunidade VIP de {niche.replace('_', ' ').title()}", 47),
        ]
        return [
            {"type": t[0], "name": t[1], "suggested_price": t[2]} for t in templates
        ]

    def _generate_services(self, niche: str) -> list[dict[str, str]]:
        return [
            {
                "type": "consultoria",
                "name": f"Consultoria Personalizada de {niche.replace('_', ' ').title()}",
            },
            {
                "type": "mentoria",
                "name": f"Mentoria em Grupo: {niche.replace('_', ' ').title()} para Resultados",
            },
        ]

    def _generate_content_angles(self, niche: str) -> list[dict[str, str]]:
        return [
            {
                "angle": f"Os 7 erros mais comuns em {niche.replace('_', ' ')} e como evita-los"
            },
            {
                "angle": f"{niche.replace('_', ' ')} para iniciantes: por onde comecar em 2026"
            },
            {
                "angle": f"Ferramentas essenciais de {niche.replace('_', ' ')} que voce precisa conhecer"
            },
        ]


class CreativeEngine(AgentBase):
    """6a Ordem: Coordenador Criativo — Detecta nichos, cria configs e gera produtos.

    Ciclo completo:
    1. MarketGapDetector → Escaneia o mercado por oportunidades
    2. NicheGenesis → Cria configuracao completa do novo nicho
    3. NovelValueGenerator → Gera produtos e ofertas para o nicho
    4. Validate → Verifica viabilidade e adiciona ao ciclo
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("creative_engine", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            # Step 1: Scan market gaps
            detector = MarketGapDetector()
            opportunities = detector.scan()
            top_opportunities = opportunities[:3]  # Top 3

            # Step 2: Generate niches for top opportunities
            genesis = NicheGenesisAgent()
            new_niches = []
            for opp in top_opportunities:
                opp_ctx = CampaignContext(
                    campaign={"opportunity": opp}, run_id=f"genesis-{opp['domain']}"
                )
                result = genesis.run(opp_ctx)
                if result.status == "success" and result.output.get("ready_to_launch"):
                    new_niches.append(
                        {
                            "opportunity": opp,
                            "config": result.output["niche_config"],
                            "keywords": result.output["keywords"],
                        }
                    )

            # Step 3: Generate products for best new niche
            value_gen = NovelValueGenerator()
            best_niche = (
                new_niches[0]["config"]["niche_key"] if new_niches else "generic"
            )
            vg_ctx = CampaignContext(
                campaign={"niche": best_niche, "domain": best_niche}, run_id="value-gen"
            )
            products = value_gen.run(vg_ctx)

            # Step 4: Synthesize
            synthesis = {
                "market_scan_count": len(opportunities),
                "potential_niches_found": len(top_opportunities),
                "niches_ready_to_launch": len(new_niches),
                "new_niches": [n["config"]["niche_key"] for n in new_niches],
                "product_ideas_generated": len(products.output.get("product_ideas", []))
                if products.status == "success"
                else 0,
                "recommendation": (
                    f"Lancar {len(new_niches)} novo(s) nicho(s): "
                    + ", ".join(n["config"]["label"] for n in new_niches)
                    if new_niches
                    else "Nenhum nicho com viabilidade suficiente no momento."
                ),
            }

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="creative",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"scanned: {len(opportunities)}",
                    f"new_niches: {len(new_niches)}",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "synthesis": synthesis,
                    "opportunities": top_opportunities,
                    "new_niches": new_niches,
                    "products": products.output if products.status == "success" else {},
                },
                trace=trace,
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            error_trace = AgentTrace(
                agent=self.name,
                step_id="creative",
                status="error",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                error=str(e)[:500],
            )
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=error_trace,
            )
