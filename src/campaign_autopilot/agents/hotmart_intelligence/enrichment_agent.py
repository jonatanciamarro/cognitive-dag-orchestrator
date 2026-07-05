"""Fase 9 — Enriquecimento: gerar Buyer Personas, Market Map, Competitor Map."""
from __future__ import annotations
import random
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import (
    ProductIntelligence, ProductIntelligenceStore,
)

class HotmartEnrichmentAgent(AgentBase):
    """Enriquece produtos com analises: personas, mercado, concorrencia."""

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_enrichment", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        enriched = []
        for p in products:
            pi = ProductIntelligence(
                product_id=p.product_id,
                buyer_personas=[
                    {"nome": "Iniciante", "perfil": f"Interessado em {p.category}", "idade": "25-35", "renda": "2-5k"},
                    {"nome": "Intermediario", "perfil": f"Ja conhece {p.category}", "idade": "30-45", "renda": "5-10k"},
                ],
                market_map={"categoria": p.category, "tamanho": "grande", "tendencia": "crescimento"},
                competitor_map=[{"nome": "Concorrente A", "diferencial": "Preco"}, {"nome": "Concorrente B", "diferencial": "Suporte"}],
                pain_map=[{"dor": f"Dificuldade com {p.category}", "intensidade": "alta"}],
                objection_map=[{"objecao": "Preco alto", "contra_argumento": "ROI em 30 dias"}],
                offer_map={"promessa": p.name, "mecanismo": "Metodo", "transformacao": f"Domine {p.category}"},
            )
            enriched.append(pi)
            if self.store:
                self.store.save_intelligence(pi)
                self.store.update_status(p.product_id, "enriched")

        output = {"enriched": len(enriched), "maps": [{"product_id": e.product_id,
            "personas": len(e.buyer_personas), "competitors": len(e.competitor_map)} for e in enriched]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_enrichment", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{len(enriched)} produtos enriquecidos"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx):
        step = ctx.step_results.get("hotmart_ingestion", {})
        raw = step.get("output", {}).get("intelligence", []) if isinstance(step, dict) else []
        ids = [i.get("product_id") for i in raw]
        if self.store and ids:
            return [self.store.get_product(pid) for pid in ids if self.store.get_product(pid)]
        return self.store.list_products(status="ingested") if self.store else []
