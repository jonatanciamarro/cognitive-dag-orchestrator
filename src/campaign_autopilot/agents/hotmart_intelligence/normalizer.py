"""Fase 7 — Normalizacao: transformar tudo em formato padrao."""
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import HotmartProduct, ProductNormalized, ProductIntelligenceStore

class HotmartNormalizerAgent(AgentBase):
    """Normaliza produtos para schema padrao /products/produto_x/metadata.json."""

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_normalizer", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        normalized = []
        for p in products:
            n = ProductNormalized(
                product_id=p.product_id, name=p.name, category=p.category,
                price=p.price, commission=p.commission_value,
                affiliate_link=p.affiliate_link or f"https://go.hotmart.com/{p.product_id}",
                sales_page=p.sales_page_url,
                target_audience=f"Interessados em {p.category}",
                pain_points=[f"Dificuldade com {p.category}"],
                benefits=[f"Aprenda {p.name}"],
                objections=["Preco salgado", "Falta de tempo"],
            )
            normalized.append(n)
            if self.store:
                self.store.save_normalized(n)
                self.store.update_status(p.product_id, "normalized")

        output = {"normalized": len(normalized), "products": [n.__dict__ for n in normalized]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_normalizer", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{len(normalized)} produtos normalizados"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx):
        step = ctx.step_results.get("hotmart_asset_collector", {})
        raw = step.get("output", {}).get("assets", []) if isinstance(step, dict) else []
        ids = [a.get("product_id") for a in raw]
        if ids and self.store:
            return [self.store.get_product(pid) for pid in ids if self.store.get_product(pid)]
        return self.store.list_products(status="assets_collected") if self.store else []
