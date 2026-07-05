"""Hotmart Intelligence Coordinator — Orquestrador do protocolo completo.

Pipeline de 10 fases:
  Discovery → Triage → Scoring → DueDiligence → Affiliation → Assets → Normalization → Ingestion → Enrichment → Activation

Cada fase e executada por um sub-agent especializado.
O coordinator gerencia a memoria compartilhada (ProductIntelligenceStore) e o fluxo entre fases.
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import ProductIntelligenceStore

from .discovery_agent import HotmartDiscoveryAgent
from .triage_agent import HotmartTriageAgent
from .scoring_agent import HotmartScoringAgent
from .due_diligence_agent import HotmartDueDiligenceAgent
from .affiliation_agent import HotmartAffiliationAgent
from .asset_collector import HotmartAssetCollector
from .normalizer import HotmartNormalizerAgent
from .ingestion_agent import HotmartIngestionAgent
from .enrichment_agent import HotmartEnrichmentAgent
from .activation_agent import HotmartActivationAgent


class HotmartIntelligenceAgent(AgentBase):
    """Agente orquestrador do Hotmart Affiliate Intelligence Protocol v1.

    Uso:
        agent = HotmartIntelligenceAgent()
        ctx = CampaignContext(campaign={"niche": "marketing digital"})
        result = agent.run(ctx)
    """

    def __init__(self, store: ProductIntelligenceStore | None = None, db_path: str | None = None, **kwargs):
        super().__init__("hotmart_intelligence", **kwargs)
        self.store = store or ProductIntelligenceStore(db_path or ":memory:")
        self._init_sub_agents()

    def _init_sub_agents(self) -> None:
        self.discovery = HotmartDiscoveryAgent(store=self.store)
        self.triage = HotmartTriageAgent(store=self.store)
        self.scoring = HotmartScoringAgent(store=self.store)
        self.diligence = HotmartDueDiligenceAgent(store=self.store)
        self.affiliation = HotmartAffiliationAgent(store=self.store)
        self.assets = HotmartAssetCollector(store=self.store)
        self.normalizer = HotmartNormalizerAgent(store=self.store)
        self.ingestion = HotmartIngestionAgent(store=self.store)
        self.enrichment = HotmartEnrichmentAgent(store=self.store)
        self.activation = HotmartActivationAgent(store=self.store)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        niche = str(context.campaign.get("niche", "marketing digital"))
        max_products = int(context.campaign.get("max_products", 10))
        skip_phases = context.campaign.get("skip_phases", [])

        pipeline_results = {}
        pipeline_errors = []
        phase_times = {}
        current_status = "discovered"

        phases = [
            ("discovery", self.discovery),
            ("triage", self.triage),
            ("scoring", self.scoring),
            ("diligence", self.diligence),
            ("affiliation", self.affiliation),
            ("assets", self.assets),
            ("normalization", self.normalizer),
            ("ingestion", self.ingestion),
            ("enrichment", self.enrichment),
            ("activation", self.activation),
        ]

        for phase_name, phase_agent in phases:
            if phase_name in skip_phases:
                continue

            t0 = time.time()
            try:
                result = phase_agent.run(context)
                pipeline_results[phase_name] = result.to_dict() if hasattr(result, 'to_dict') else result.output
                phase_times[phase_name] = round(time.time() - t0, 3)
                current_status = "activated" if phase_name == "activation" else phase_name
            except Exception as e:
                pipeline_errors.append(f"{phase_name}: {e}")
                phase_times[phase_name] = round(time.time() - t0, 3)
                break  # para o pipeline se uma fase falha

        stats = self.store.stats() if self.store else {}

        output = {
            "niche": niche,
            "max_products": max_products,
            "phases_executed": list(pipeline_results.keys()),
            "phases_skipped": skip_phases,
            "phase_times": phase_times,
            "errors": pipeline_errors,
            "final_status": current_status,
            "stats": stats,
            "pipeline_results": pipeline_results,
        }

        finished_at = utc_now_iso()
        duration = iso_duration_ms(started_at, finished_at)
        trace = AgentTrace(agent=self.name, step_id="hotmart_intelligence", status="success" if not pipeline_errors else "partial",
            started_at=started_at, finished_at=finished_at, duration_ms=duration, thread_name="main",
            notes=[f"Pipeline {niche}: {len(phase_times)} fases em {duration}ms",
                   f"Status final: {current_status}"],
            metadata={"phases": list(pipeline_results.keys()), "errors": len(pipeline_errors),
                      "phase_times": phase_times, "stats": stats})
        return AgentResult(agent=self.name, status="success" if not pipeline_errors else "partial",
                           output=output, trace=trace)
