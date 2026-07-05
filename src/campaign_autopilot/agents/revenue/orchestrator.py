"""RevenueOrchestratorAgent — Coordena TODAS as 13 fontes de renda.

Mantem estado de cada fonte, recomenda proximos passos,
e garante que todas estejam gerando receita.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from .memory import RevenueMemory, REVENUE_SOURCES
from ...logging_utils import StructuredLogger

log = StructuredLogger("revenue_orchestrator")


class RevenueOrchestratorAgent(AgentBase):
    """Orquestrador central de todas as 13 fontes de renda."""

    def __init__(self, **kwargs):
        super().__init__("revenue_orchestrator", **kwargs)
        self.memory = RevenueMemory()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "dashboard")

            if action == "dashboard":
                return self._dashboard(started_at)
            elif action == "setup_all":
                return self._setup_all(started_at)
            elif action == "next_steps":
                return self._next_steps(started_at)
            else:
                return self._dashboard(started_at)

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="orchestrator",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _dashboard(self, started_at: str) -> AgentResult:
        summary = self.memory.get_summary()
        sources_status = self.memory.get_status()

        active = [s for s in sources_status if s["status"] == "active"]
        pending = [s for s in sources_status if s["status"] == "pending"]
        in_progress = [
            s for s in sources_status if s["status"] not in ("active", "pending")
        ]

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="dashboard",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(active)} active, {len(pending)} pending"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "summary": summary,
                "active_sources": [s["source"] for s in active],
                "pending_sources": [s["source"] for s in pending],
                "in_progress_sources": [s["source"] for s in in_progress],
            },
            trace=trace,
        )

    def _setup_all(self, started_at: str) -> AgentResult:
        quick_guide = []
        for source in REVENUE_SOURCES:
            if source == "hotmart":
                quick_guide.append(
                    {"source": source, "guide": "python scripts/hotmart_wizard.py"}
                )
            elif source in ("monetizze", "kiwify", "eduzz"):
                quick_guide.append(
                    {
                        "source": source,
                        "guide": f"GenericAffiliateNetworkAgent (network={source})",
                    }
                )
            elif source in ("mercadolivre", "shopee", "shein", "aliexpress"):
                quick_guide.append(
                    {
                        "source": source,
                        "guide": f"GenericAffiliateNetworkAgent (network={source}) — criar conta e adicionar link",
                    }
                )
            elif source == "adsense":
                quick_guide.append(
                    {
                        "source": source,
                        "guide": "AdSenseAgent — configurar site no Google AdSense",
                    }
                )
            elif source == "cpa":
                quick_guide.append(
                    {
                        "source": source,
                        "guide": "CPAAgent — escolher redes CPA e configurar ofertas",
                    }
                )
            else:
                quick_guide.append(
                    {
                        "source": source,
                        "guide": f"RevenueBaseAgent protocol for {source}",
                    }
                )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="setup_all",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(quick_guide)} sources to configure"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "total_sources": len(REVENUE_SOURCES),
                "setup_guide": quick_guide,
            },
            trace=trace,
        )

    def _next_steps(self, started_at: str) -> AgentResult:
        sources_status = self.memory.get_status()
        pending = [s for s in sources_status if s["status"] == "pending"]

        recommendations = []
        for source in sorted(pending, key=lambda x: x["source"]):
            src_name = source["source"]
            module_name = (
                "generic_affiliate"
                if src_name
                in (
                    "monetizze",
                    "kiwify",
                    "eduzz",
                    "mercadolivre",
                    "shopee",
                    "shein",
                    "aliexpress",
                )
                else src_name
            )
            recommendations.append(
                {
                    "source": src_name,
                    "status": source["status"],
                    "action": f"Configurar {src_name} - veja o protocolo no agente correspondente",
                    "command": f"python -c 'from campaign_autopilot.agents.revenue.{module_name} import ...'",
                }
            )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="next_steps",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(recommendations)} pending sources"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "pending_sources": len(pending),
                "recommendations": recommendations,
                "quick_wins": [
                    "Hotmart: python scripts/hotmart_wizard.py",
                    "Amazon: colocar AMAZON_TRACKING_ID no .env",
                    "Email: configurar sequencia de boas-vindas",
                ],
            },
            trace=trace,
        )
