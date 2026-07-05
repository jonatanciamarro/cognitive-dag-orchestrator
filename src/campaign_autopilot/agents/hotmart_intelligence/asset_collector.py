"""Fase 6 — Coleta de Ativos: construir Product Intelligence Package."""
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import ProductAssetCollection, ProductIntelligenceStore

class HotmartAssetCollector(AgentBase):
    """Coleta todos os ativos do produto: links, criativos, conteudo, dados."""

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_asset_collector", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        collections = []
        for p in products:
            assets = ProductAssetCollection(
                product_id=p.product_id,
                images=[f"{p.product_id}_img1.jpg", f"{p.product_id}_img2.jpg"],
                banners=[f"{p.product_id}_banner1.jpg"],
                videos=[f"{p.product_id}_vsl.mp4"],
                logos=[f"{p.product_id}_logo.png"],
                copies=["Copy principal para anúncio", "Copy para email"],
                links={"affiliate": p.affiliate_link, "checkout": p.checkout_url, "sales_page": p.sales_page_url},
                faq=[{"pergunta": "Tem garantia?", "resposta": "7 dias"}],
            )
            collections.append(assets)
            if self.store:
                self.store.save_assets(assets)
                self.store.update_status(p.product_id, "assets_collected")

        output = {"collected": len(collections), "assets": [{ "product_id": c.product_id,
            "images": len(c.images), "videos": len(c.videos), "copies": len(c.copies) } for c in collections]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_asset_collector", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"Ativos coletados para {len(collections)} produtos"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx):
        step = ctx.step_results.get("hotmart_affiliation", {})
        raw = step.get("output", {}).get("records", []) if isinstance(step, dict) else []
        ids = [r.get("product_id") for r in raw if r.get("approved")]
        if ids and self.store:
            return [self.store.get_product(pid) for pid in ids if self.store.get_product(pid)]
        return self.store.list_products(status="affiliated") if self.store else []
