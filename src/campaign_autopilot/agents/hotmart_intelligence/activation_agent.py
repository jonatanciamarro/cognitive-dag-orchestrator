"""Fase 10 — Activation: gerar criativos, conteudo e campanhas."""
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import (
    ProductIntelligenceStore, HotmartProductDossier, HotmartProduct,
)

class HotmartActivationAgent(AgentBase):
    """Ativa produtos aprovados gerando dossie operacional completo.

    Output: HOTMART PRODUCT DOSSIER com todos os ativos e campanhas.
    """

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_activation", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        dossiers = []
        for p in products:
            dossier = self._build_dossier(p)
            dossiers.append(dossier)
            if self.store:
                self.store.save_dossier(p.product_id, dossier)
                self.store.update_status(p.product_id, "activated")

        output = {
            "activated": len(dossiers),
            "dossiers": dossiers,
            "product_ids": [d["product_id"] for d in dossiers],
        }
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_activation", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{len(dossiers)} dossies operacionais gerados"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx):
        step = ctx.step_results.get("hotmart_enrichment", {})
        raw = step.get("output", {}).get("maps", []) if isinstance(step, dict) else []
        ids = [m.get("product_id") for m in raw]
        if self.store and ids:
            return [self.store.get_product(pid) for pid in ids if self.store.get_product(pid)]
        return self.store.list_products(status="enriched") if self.store else []

    def _build_dossier(self, p: HotmartProduct) -> dict:
        """Constroi dossie operacional completo."""
        return {
            "product_id": p.product_id,
            "product_name": p.name,
            "producer": p.producer,
            "category": p.category,
            "price": p.price,
            "commission": p.commission_value,
            "affiliate_link": p.affiliate_link or f"https://go.hotmart.com/{p.product_id}",
            "sales_page": p.sales_page_url,
            "status": "activated",
            "product_intelligence": {
                "market_tier": self._get_tier(p),
                "target_audience": f"Interessados em {p.category}",
                "pain_points": [f"Dificuldade com {p.category}"],
                "benefits": [f"Aprenda {p.name}"],
            },
            "affiliate_assets": {
                "creatives": [f"{p.product_id}_banner.jpg", f"{p.product_id}_video.mp4"],
                "copies": [f"Copy 1 para {p.name}", f"Copy 2 para {p.name}"],
                "links": {
                    "affiliate": p.affiliate_link or f"https://go.hotmart.com/{p.product_id}",
                    "checkout": p.checkout_url or f"https://pay.hotmart.com/{p.product_id}",
                },
            },
            "campaign_templates": {
                "facebook": f"Anuncio para {p.name}",
                "instagram": f"Post para {p.name}",
                "email": f"Email promocional {p.name}",
                "landing_page": f"LP para {p.name}",
            },
            "tracking": {
                "utm_source": "campaign_autopilot",
                "utm_medium": "hotmart_intelligence",
                "utm_campaign": p.product_id,
            },
            "generated_at": utc_now_iso(),
        }

    def _get_tier(self, p) -> str:
        if self.store:
            score = self.store._conn.execute(
                "SELECT tier FROM opportunity_scores WHERE product_id=?", (p.product_id,)
            ).fetchone()
            if score: return score[0]
        return "silver"
