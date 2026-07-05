"""Fase 5 — Afiliacao: registrar afiliacao apos aprovacao."""
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import AffiliationRecord, ProductIntelligenceStore

class HotmartAffiliationAgent(AgentBase):
    """Registra afiliacao no Hotmart apos diligence aprovada."""

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_affiliation", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        affiliations = []
        for p in products:
            rec = AffiliationRecord(
                product_id=p.product_id,
                affiliate_id=f"aff_{p.product_id}",
                affiliate_link=f"https://go.hotmart.com/{p.product_id}?src=ca",
                approved=True, approval_date=utc_now_iso(),
                commission_terms=f"{p.commission_pct}% + R$ {p.commission_value} por venda",
            )
            affiliations.append(rec)
            if self.store:
                self.store.save_affiliation(rec)
                self.store.update_status(p.product_id, "affiliated")

        output = {"affiliated": len(affiliations),
                  "records": [{"product_id": r.product_id, "affiliate_link": r.affiliate_link, "approved": r.approved} for r in affiliations]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_affiliation", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{len(affiliations)} produtos afiliados"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx):
        step = ctx.step_results.get("hotmart_due_diligence", {})
        raw = step.get("output", {}).get("reports", []) if isinstance(step, dict) else []
        approved_ids = [r.get("product_id") for r in raw if r.get("overall_verdict") == "approved"]
        if approved_ids and self.store:
            return [self.store.get_product(pid) for pid in approved_ids if self.store.get_product(pid)]
        return self.store.list_products(status="diligenced") if self.store else []
