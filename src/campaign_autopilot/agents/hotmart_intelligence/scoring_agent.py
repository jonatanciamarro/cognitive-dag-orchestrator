"""Fase 3 — Score de Oportunidade: 0-100."""
from __future__ import annotations
import random
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import (
    HotmartProduct, OpportunityScore, OpportunityTier, ProductIntelligenceStore,
)

class HotmartScoringAgent(AgentBase):
    """Calcula OpportunityScore (0-100) para cada produto aprovado na triagem.

    Criterios:
      Mercado (25%) — demanda, dor recorrente, mercado crescente
      Comissao (15%) — valor absoluto, percentual, recorrencia
      Conversao (20%) — pagina de vendas, copy, oferta, prova social, garantia
      Materiais (20%) — criativos, videos, banners, emails, VSL, scripts
      Compatibilidade (20%) — capacidade do Campaign Autopilot produzir
    """

    WEIGHTS = {"market": 0.25, "commission": 0.15, "conversion": 0.20, "materials": 0.20, "compatibility": 0.20}

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_scoring", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products = self._get_products(context)
        scores = []
        for p in products:
            s = self._score(p)
            scores.append(s)
            if self.store:
                self.store.save_score(s)
                tier = s.tier
                if tier in (OpportunityTier.DIAMOND.value, OpportunityTier.GOLD.value, OpportunityTier.SILVER.value):
                    self.store.update_status(p.product_id, "scored")

        output = {"scored": len(scores), "scores": [{"product_id": s.product_id, "total": s.total_score, "tier": s.tier} for s in scores]}
        avg = sum(s.total_score for s in scores) / len(scores) if scores else 0
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_scoring", status="success",
            started_at=started_at, finished_at=finished_at, duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main", notes=[f"{len(scores)} produtos pontuados, media {avg:.1f}"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _get_products(self, ctx) -> list[HotmartProduct]:
        step = ctx.step_results.get("hotmart_triage", {})
        raw = step.get("output", {}).get("results", []) if isinstance(step, dict) else []
        approved_ids = [r.get("product_id") for r in raw if r.get("verdict") in ("approved", "flagged")]
        if approved_ids and self.store:
            return [self.store.get_product(pid) for pid in approved_ids if self.store.get_product(pid)]
        return self.store.list_products(status="triaged") if self.store else []

    def _score(self, p: HotmartProduct) -> OpportunityScore:
        mkt = min(100, random.uniform(40, 95))  # simulacao
        comm = min(100, (p.commission_value / 500) * 100) if p.commission_value else 30
        conv = min(100, random.uniform(30, 90))
        mat = min(100, random.uniform(20, 80))
        compat = min(100, random.uniform(40, 95))
        total = (mkt * 0.25 + comm * 0.15 + conv * 0.20 + mat * 0.20 + compat * 0.20)
        if total >= 85: tier = OpportunityTier.DIAMOND.value
        elif total >= 70: tier = OpportunityTier.GOLD.value
        elif total >= 50: tier = OpportunityTier.SILVER.value
        elif total >= 30: tier = OpportunityTier.BRONZE.value
        else: tier = OpportunityTier.LOW.value
        return OpportunityScore(product_id=p.product_id, total_score=round(total, 1),
            market_potential=round(mkt, 1), commission_score=round(comm, 1),
            conversion_score=round(conv, 1), materials_score=round(mat, 1),
            compatibility_score=round(compat, 1), tier=tier)
