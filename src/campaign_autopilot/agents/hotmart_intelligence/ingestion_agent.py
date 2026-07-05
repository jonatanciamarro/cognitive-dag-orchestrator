"""Fase 8 — Ingestao no Campaign Autopilot: Product Knowledge Base."""
from __future__ import annotations
import random
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import (
    ProductNormalized, ProductIntelligence, ProductIntelligenceStore,
)

class HotmartIngestionAgent(AgentBase):
    """Ingere produtos normalizados na Product Knowledge Base do Campaign Autopilot.

    Extracoes automaticas: Avatar, Oferta, Linguagem.
    """

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_ingestion", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        ingested = []
        for n in products:
            pi = ProductIntelligence(
                product_id=n.product_id,
                avatar={"quem_compra": "Iniciante em " + n.category, "idade": "25-45",
                        "objetivos": [f"Aprender {n.category}"], "dores": ["Falta de resultado"]},
                offer={"promessa": f"Aprenda {n.name} rapidamente", "mecanismo": "Passo a passo",
                       "transformacao": "Domine " + n.category, "urgencia": "Vagas limitadas"},
                language={"tom": "didatico", "vocabulario": "simples", "argumentacao": "logica"},
                buyer_personas=[{"nome": "Persona 1", "perfil": f"Interessado em {n.category}"}],
            )
            ingested.append(pi)
            if self.store:
                self.store.save_intelligence(pi)
                self.store.update_status(n.product_id, "ingested")

        output = {"ingested": len(ingested), "intelligence": [{"product_id": i.product_id,
            "avatar": i.avatar, "offer": i.offer} for i in ingested]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_ingestion", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{len(ingested)} produtos ingeridos na Knowledge Base"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx):
        step = ctx.step_results.get("hotmart_normalizer", {})
        raw = step.get("output", {}).get("products", []) if isinstance(step, dict) else []
        ids = [n.get("product_id") for n in raw]
        if self.store and ids:
            return [n for pid in ids if (n := self.store.get_product(pid))]
        return self.store.list_products(status="normalized") if self.store else []
