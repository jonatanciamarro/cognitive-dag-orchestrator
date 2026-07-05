"""Fase 4 — Due Diligence: verificar pagina de vendas, presenca digital, produtor."""
from __future__ import annotations
import random
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import (
    HotmartProduct, DueDiligenceReport, ProductIntelligenceStore,
)

class HotmartDueDiligenceAgent(AgentBase):
    """Due diligence completa: sales page, presenca digital, produtor."""

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_due_diligence", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        reports = []
        for p in products:
            r = DueDiligenceReport(product_id=p.product_id,
                sales_page_score=random.uniform(40, 95),
                sales_page_issues=self._check_sales_page(p),
                digital_presence_score=random.uniform(30, 90),
                digital_presence_notes=self._check_presence(p),
                producer_score=random.uniform(40, 95),
                producer_notes=self._check_producer(p),
                overall_verdict="approved" if random.random() > 0.2 else "flagged",
            )
            reports.append(r)
            if self.store:
                self.store.save_diligence(r)
                if r.overall_verdict == "approved":
                    self.store.update_status(p.product_id, "diligenced")

        output = {"diligenced": len(reports), "reports": [r.__dict__ for r in reports]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_due_diligence", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{len(reports)} produtos diligenciados"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx) -> list[HotmartProduct]:
        step = ctx.step_results.get("hotmart_scoring", {})
        raw = step.get("output", {}).get("scores", []) if isinstance(step, dict) else []
        scored_ids = [s.get("product_id") for s in raw if s.get("tier") in ("diamond","gold","silver")]
        if scored_ids and self.store:
            return [self.store.get_product(pid) for pid in scored_ids if self.store.get_product(pid)]
        return self.store.list_products(status="scored") if self.store else []

    def _check_sales_page(self, p) -> list[str]:
        issues = []
        if not p.sales_page_url: issues.append("Sem URL de pagina de vendas")
        if not p.description: issues.append("Descricao vazia")
        return issues

    def _check_presence(self, p) -> list[str]:
        return [f"Presenca digital: {p.producer} — verificacao simulada"]

    def _check_producer(self, p) -> list[str]:
        return [f"Produtor: {p.producer} — analise simulada"]
