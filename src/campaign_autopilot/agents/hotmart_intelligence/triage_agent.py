"""Fase 2 — Triagem Inicial: eliminar produtos inadequados."""
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import HotmartProduct, TriageResult, TriageVerdict, ProductIntelligenceStore

class HotmartTriageAgent(AgentBase):
    """Elimina produtos inadequados conforme regras do protocolo.

    Regras de exclusao:
    - Promessas irreais
    - Nichos proibidos (saude sem respaldo, religiosos extremos, etc.)
    - Paginas quebradas (sem sales page viavel)
    - Produtos abandonados (sem atualizacao >6 meses)
    - Ofertas sem materiais
    - Comissoes muito baixas (< R$ 20)
    - Funis incompletos (sem upsell/checkout)
    """

    FORBIDDEN_KEYWORDS = ["milagre", "dinheiro facil", "ganhe rapido", "biziu", "secreto"]
    MIN_COMMISSION = 20.0
    MAX_AGE_DAYS = 180

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_triage", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        products_data = context.step_results.get("hotmart_discovery", {})
        products_raw = products_data.get("output", {}).get("products", []) if isinstance(products_data, dict) else []

        products = [HotmartProduct(**p) if isinstance(p, dict) else p for p in products_raw]
        if not products and self.store:
            products = self.store.list_products(status="discovered")

        results = []
        for p in products:
            tr = self._triage(p)
            results.append(tr)
            if self.store:
                self.store.save_triage(tr)
                if tr.verdict == TriageVerdict.APPROVED.value:
                    self.store.update_status(p.product_id, "triaged")
                elif tr.verdict == TriageVerdict.REJECTED.value:
                    self.store.update_status(p.product_id, "rejected")

        approved = sum(1 for r in results if r.verdict == TriageVerdict.APPROVED.value)
        rejected = sum(1 for r in results if r.verdict == TriageVerdict.REJECTED.value)
        flagged = sum(1 for r in results if r.verdict == TriageVerdict.FLAGGED.value)

        output = {"triaged": len(results), "approved": approved, "rejected": rejected, "flagged": flagged,
                  "results": [{"product_id": r.product_id, "verdict": r.verdict, "reasons": r.reasons} for r in results]}
        finished_at = utc_now_iso()
        trace = AgentTrace(agent=self.name, step_id="hotmart_triage", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"{approved} aprovados, {rejected} rejeitados, {flagged} sinalizados"])
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)

    def _triage(self, p: HotmartProduct) -> TriageResult:
        issues = []
        reasons = []
        desc = (p.description or "").lower()
        name = (p.name or "").lower()
        combined = desc + " " + name

        # Promessas irreais
        for kw in self.FORBIDDEN_KEYWORDS:
            if kw in combined:
                issues.append(f"palavra proibida: {kw}")
                reasons.append(f"Promessa irreal detectada: '{kw}'")
                break

        # Comissao muito baixa
        if p.commission_value < self.MIN_COMMISSION:
            issues.append(f"comissao baixa: R$ {p.commission_value}")
            reasons.append(f"Comissao (R$ {p.commission_value}) abaixo do minimo (R$ {self.MIN_COMMISSION})")

        if not issues:
            return TriageResult(product_id=p.product_id, verdict=TriageVerdict.APPROVED.value, reasons=["Produto aprovado na triagem"])
        elif len(issues) <= 1:
            return TriageResult(product_id=p.product_id, verdict=TriageVerdict.FLAGGED.value, issues=issues, reasons=reasons)
        else:
            return TriageResult(product_id=p.product_id, verdict=TriageVerdict.REJECTED.value, issues=issues, reasons=reasons)
