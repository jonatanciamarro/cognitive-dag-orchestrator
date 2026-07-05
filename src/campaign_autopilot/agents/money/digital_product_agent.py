"""DigitalProductAgent — Cria e gerencia produtos digitais: ebooks, cursos, templates, PLR.

Fluxo:
1. Detecta demanda por produtos digitais no nicho
2. Gera conteúdo do produto via LLM
3. Formata em PDF/template
4. Cria página de vendas
5. Registra na Hotmart/Kiwify
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("digital_product")


PRODUCT_TYPES = {
    "ebook": {
        "name": "E-book / Guia",
        "price_range": (17, 67),
        "commission": 0.70,  # 70% para afiliados se vender via Hotmart
        "production_time": "2-3 ciclos",
        "description": "Guia completo em PDF sobre um tema específico",
    },
    "curso": {
        "name": "Curso Online",
        "price_range": (97, 497),
        "commission": 0.50,
        "production_time": "5-7 ciclos",
        "description": "Curso gravado com videoaulas e material de apoio",
    },
    "template": {
        "name": "Template / Planilha",
        "price_range": (27, 97),
        "commission": 0.80,
        "production_time": "1 ciclo",
        "description": "Template pronto para uso (planilha, canvas, design)",
    },
    "plr": {
        "name": "PLR (Private Label Rights)",
        "price_range": (47, 197),
        "commission": 0.60,
        "production_time": "2 ciclos",
        "description": "Conteúdo com direitos de revenda para outros afiliados",
    },
    "checklist": {
        "name": "Checklist / Guia Rápido",
        "price_range": (7, 27),
        "commission": 0.80,
        "production_time": "1 ciclo",
        "description": "Checklist prático em PDF para download rápido",
    },
    "ferramenta": {
        "name": "Ferramenta Online",
        "price_range": (0, 0),  # Grátis para capturar leads
        "commission": 0.0,
        "production_time": "3-4 ciclos",
        "description": "Ferramenta web simples (calculadora, quiz, gerador)",
    },
}


class DigitalProductAgent(AgentBase):
    """Cria e gerencia produtos digitais para geração de receita."""

    def __init__(self, **kwargs) -> None:
        super().__init__("digital_product", **kwargs)

    def detect_product_opportunity(
        self, niche: str, keywords: list[str]
    ) -> dict[str, Any]:
        """Detecta oportunidades de produtos digitais no nicho."""
        # Simula análise de demanda
        # Em produção: integrar com Google Trends, Amazon, Hotmart
        demand_scores = {
            "tecnologia": {
                "ebook": {
                    "score": 0.7,
                    "topics": ["guia inteligencia artificial", "manual notebook"],
                },
                "curso": {"score": 0.8, "topics": ["curso programacao", "curso excel"]},
                "template": {
                    "score": 0.5,
                    "topics": ["template currículo tech", "planilha projetos"],
                },
            },
            "financas": {
                "ebook": {
                    "score": 0.9,
                    "topics": [
                        "guia investir pouco dinheiro",
                        "ebook sair das dividas",
                    ],
                },
                "curso": {
                    "score": 0.7,
                    "topics": ["curso educacao financeira", "curso renda extra"],
                },
                "template": {
                    "score": 0.8,
                    "topics": ["planilha orçamento pessoal", "planilha investimentos"],
                },
                "checklist": {
                    "score": 0.6,
                    "topics": [
                        "checklist economizar dinheiro",
                        "checklist organização financeira",
                    ],
                },
            },
            "saude": {
                "ebook": {
                    "score": 0.6,
                    "topics": ["guia alimentacao saudavel", "ebook emagrecer"],
                },
                "template": {
                    "score": 0.4,
                    "topics": ["planilha treinos", "diario alimentar"],
                },
            },
            "carreira": {
                "ebook": {
                    "score": 0.8,
                    "topics": ["guia fazer curriculo", "ebook LinkedIn"],
                },
                "curso": {
                    "score": 0.6,
                    "topics": ["curso entrevista emprego", "curso carreira"],
                },
                "template": {
                    "score": 0.7,
                    "topics": ["template curriculo", "template carta apresentação"],
                },
            },
        }

        niche_data = demand_scores.get(niche.lower(), {})
        opportunities = []
        for product_type, data in niche_data.items():
            info = PRODUCT_TYPES.get(product_type, {})
            opportunities.append(
                {
                    "type": product_type,
                    "name": info.get("name", product_type),
                    "score": data["score"],
                    "suggested_price": info.get("price_range", [27, 97])[0],
                    "suggested_topics": data.get("topics", []),
                }
            )

        opportunities.sort(key=lambda x: -x["score"])
        return {
            "niche": niche,
            "opportunities": opportunities,
            "top_opportunity": opportunities[0] if opportunities else None,
            "monthly_revenue_estimate": self._estimate_revenue(opportunities),
        }

    def _estimate_revenue(self, opportunities: list[dict]) -> dict[str, float]:
        """Estima receita mensal potencial."""
        total = 0.0
        for opp in opportunities[:3]:
            score = opp.get("score", 0)
            price = opp.get("suggested_price", 27)
            sales_per_month = score * 30  # Simulated: score determines sales
            total += price * sales_per_month * 0.7  # 70% margin after fees
        return {"estimated_monthly_revenue": round(total, 2), "confidence": "medium"}

    def generate_product_outline(
        self, product_type: str, topic: str, niche: str
    ) -> dict[str, Any]:
        """Gera outline do produto digital."""
        templates = {
            "ebook": {
                "chapters": [
                    f"O que é {topic}?",
                    f"Por que {topic} é importante para {niche}",
                    f"Passo a passo para começar em {topic}",
                    "Estratégias avançadas",
                    "Erros comuns e como evitá-los",
                    "Estudos de caso e exemplos reais",
                    "Conclusão e próximos passos",
                ],
                "bonus": ["Checklist de implementação", "Planilha de acompanhamento"],
                "page_count_estimate": 80,
            },
            "curso": {
                "modulos": [
                    f"Introdução ao {topic}",
                    f"Fundamentos de {topic}",
                    f"Aplicações práticas de {topic}",
                    f"Técnicas avançadas em {topic}",
                    "Projeto final",
                ],
                "total_aulas": 20,
                "duracao_estimada": "5 horas",
            },
            "template": {
                "sections": [
                    "Instruções de uso",
                    "Template principal",
                    "Exemplos preenchidos",
                    "Dicas de personalização",
                ],
            },
        }
        return templates.get(product_type, {"description": f"Produto sobre {topic}"})

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        campaign = context.campaign

        niche = str(campaign.get("niche", "financas"))
        keywords = campaign.get("keywords", campaign.get("opportunities", []))
        if isinstance(keywords, list) and keywords and isinstance(keywords[0], dict):
            keywords = [k.get("keyword", "") for k in keywords[:5]]
        elif isinstance(keywords, list) and keywords and isinstance(keywords[0], str):
            keywords = keywords[:5]
        else:
            keywords = []

        # Detect opportunities
        analysis = self.detect_product_opportunity(niche, keywords)
        top = analysis.get("top_opportunity", {})

        # Generate outline for best opportunity
        outline = {}
        if top:
            topic = (top.get("suggested_topics") or [f"Guia de {niche}"])[0]
            outline = self.generate_product_outline(top["type"], topic, niche)

        # Create product page
        products_dir = Path("output/products")
        products_dir.mkdir(parents=True, exist_ok=True)

        product_page = self._create_product_page(top, outline, niche)
        product_path = products_dir / f"{top.get('type', 'produto')}-{niche}.html"
        product_path.write_text(product_page, encoding="utf-8")

        output = {
            "niche": niche,
            "products_analyzed": len(analysis.get("opportunities", [])),
            "top_product": top,
            "product_outline": outline,
            "revenue_estimate": analysis.get("monthly_revenue_estimate", {}),
            "product_page": str(product_path),
            "recommendations": [
                f"Criar ebook sobre '{topic}' primeiro — maior potencial de receita",
                "Publicar na Hotmart com 70% de comissão para afiliados",
                "Usar artigos do site como conteúdo base do produto",
                "Oferecer como bônus em ofertas de afiliados maiores",
            ],
        }

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="digital_product",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Criou produto digital '{top.get('name', '')}' para nicho '{niche}'"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    def _create_product_page(self, product: dict, outline: dict, niche: str) -> str:
        """Gera página HTML de vendas para o produto digital."""
        name = product.get("name", "Produto Digital")
        price = product.get("suggested_price", 27)
        chapters = outline.get("chapters", outline.get("modulos", []))
        chapters_html = "".join(f"<li>{ch}</li>" for ch in chapters)

        return f"""<!DOCTYPE html><html lang="pt-BR"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} — {niche.capitalize()}</title>
<style>
body {{ font-family: -apple-system, sans-serif; line-height: 1.8; color: #1a1a2e; max-width: 720px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #1a365d; font-size: 2rem; }}
.price {{ font-size: 2.5rem; color: #2b6cb0; font-weight: bold; }}
.cta {{ display: inline-block; background: #2b6cb0; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; font-size: 1.2rem; margin: 20px 0; }}
.cta:hover {{ background: #1a365d; }}
ul {{ padding-left: 20px; }}
li {{ margin-bottom: 8px; }}
</style>
</head><body>
<h1>{name}</h1>
<p>O guia completo para dominar {product.get("suggested_topics", [niche])[0]} e transformar seus resultados.</p>
<div class="price">R$ {price},00</div>
<a class="cta" href="#">🛒 COMPRAR AGORA</a>
<h2>O que você vai aprender:</h2>
<ul>{chapters_html}</ul>
<h2>Para quem é este produto?</h2>
<ul><li>Iniciantes que querem aprender do zero</li><li>Profissionais que buscam aprofundamento</li><li>Pessoas que querem resultados práticos</li></ul>
<a class="cta" href="#">📥 QUERO MEU ACESSO</a>
<p style="color:#718096;font-size:0.9rem;margin-top:30px;">Compra 100% segura • Acesso imediato • Suporte via email</p>
</body></html>"""

    @staticmethod
    def _utcnow_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))
