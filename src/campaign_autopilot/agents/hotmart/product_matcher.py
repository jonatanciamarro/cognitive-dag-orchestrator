"""ProductMatcherAgent — Analisa nome do produto e sugere keywords, comissao e nicho."""

from __future__ import annotations

from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("product_matcher")


COMMISSION_BY_TYPE = {
    "curso": 50.0,
    "ebook": 70.0,
    "mentoria": 40.0,
    "ferramenta": 30.0,
    "software": 30.0,
    "comunidade": 60.0,
    "evento": 20.0,
    "servico": 30.0,
    "aplicativo": 40.0,
    "planilha": 70.0,
    "template": 60.0,
}

PRODUCT_TYPES = {
    "curso": [
        "curso",
        "treinamento",
        "programa",
        "formacao",
        "masterclass",
        "workshop",
    ],
    "ebook": ["ebook", "guia", "manual", "apostila", "livro digital"],
    "mentoria": ["mentoria", "consultoria", "coaching", "acompanhamento"],
    "ferramenta": ["ferramenta", "kit", "conjunto", "pacote"],
    "software": ["software", "app", "plataforma", "sistema"],
    "comunidade": ["comunidade", "grupo vip", "assinatura", "clube"],
}

KEYWORD_BY_NICHE = {
    "tecnologia": [
        "tecnologia",
        "digital",
        "programacao",
        "software",
        "aplicativo",
        "internet",
        "computador",
        "celular",
        "inovacao",
        "inteligencia artificial",
    ],
    "financas": [
        "dinheiro",
        "investir",
        "economizar",
        "renda",
        "financeiro",
        "orcamento",
        "poupanca",
        "acoes",
        "cripto",
        "passiva",
    ],
    "saude": [
        "saude",
        "bem-estar",
        "alimentacao",
        "exercicio",
        "emagrecer",
        "nutricao",
        "fitness",
        "mental",
        "suplemento",
        "qualidade de vida",
    ],
    "carreira": [
        "carreira",
        "emprego",
        "curriculo",
        "entrevista",
        "promocao",
        "lideranca",
        "networking",
        "linkedin",
        "profissional",
        "trabalho",
    ],
}


class ProductMatcherAgent(AgentBase):
    """Analisa nome do produto e sugere keywords, comissao e nicho adequado."""

    def __init__(self, **kwargs) -> None:
        super().__init__("product_matcher", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            product_name = campaign.get("product_name", "").lower()
            niche = campaign.get("niche", "").lower()

            # Detect product type from name
            product_type = self._detect_product_type(product_name)

            # Suggest commission based on type
            suggested_commission = COMMISSION_BY_TYPE.get(product_type, 50.0)

            # Suggest keywords
            suggested_keywords = self._generate_keywords(product_name, niche)

            # Suggest niche if not provided
            suggested_niche = niche or self._detect_niche(product_name)
            if not suggested_niche:
                suggested_niche = "tecnologia"  # fallback

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="match",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"type: {product_type}",
                    f"niche: {suggested_niche}",
                    f"kw: {len(suggested_keywords)}",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "product_type": product_type,
                    "suggested_commission": suggested_commission,
                    "suggested_keywords": suggested_keywords,
                    "suggested_niche": suggested_niche,
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
                    step_id="match",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    error=str(e)[:500],
                ),
            )

    def _detect_product_type(self, name: str) -> str:
        for ptype, keywords in PRODUCT_TYPES.items():
            for kw in keywords:
                if kw in name:
                    return ptype
        return "curso"

    def _generate_keywords(self, name: str, niche: str) -> list[str]:
        words = name.replace(":", "").replace(",", "").split()
        keywords = [w for w in words if len(w) > 2][:6]

        if niche in KEYWORD_BY_NICHE:
            niche_kw = KEYWORD_BY_NICHE[niche][:4]
            keywords.extend(niche_kw)

        # Add product-type keywords
        ptype = self._detect_product_type(name)
        if ptype in COMMISSION_BY_TYPE:
            keywords.append(ptype)

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
        return result[:10]

    def _detect_niche(self, name: str) -> str:
        name_lower = name.lower()
        niche_scores = {}
        for niche, keywords in KEYWORD_BY_NICHE.items():
            score = sum(1 for kw in keywords if kw in name_lower)
            if score > 0:
                niche_scores[niche] = score
        if niche_scores:
            return max(niche_scores, key=niche_scores.get)
        return ""
