"""PaidTrafficOrchestratorAgent — Orquestra campanhas de tráfego pago multi-plataforma.

Coordena:
1. RevenueMonitor → verifica se pode ativar
2. BudgetOptimizer → aloca orçamento
3. Platform agents → criam campanhas
4. AdCopyGenerator → cria criativos
5. LandingPageAgent → cria páginas
6. PerformanceTracker → monitora resultados
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("paid_traffic_orchestrator")

# Thresholds de tráfego pago por nicho (CPC estimado)
NICHE_CPCS = {
    "tecnologia": {"google_ads": 3.50, "meta_ads": 2.80, "native_ads": 1.50},
    "financas": {"google_ads": 5.00, "meta_ads": 4.00, "native_ads": 2.00},
    "saude": {"google_ads": 2.50, "meta_ads": 3.00, "native_ads": 1.20},
    "carreira": {"google_ads": 4.00, "meta_ads": 3.50, "native_ads": 1.80},
}


class PaidTrafficOrchestratorAgent(AgentBase):
    """Orquestra campanhas de tráfego pago em múltiplas plataformas."""

    def __init__(self, **kwargs) -> None:
        super().__init__("paid_traffic_orchestrator", **kwargs)

    def _create_campaign_plan(
        self,
        niche: str,
        daily_budget: float,
        platform: str,
        articles: list[dict],
    ) -> dict[str, Any]:
        """Cria plano de campanha para um nicho + plataforma."""
        cpc = NICHE_CPCS.get(niche, {}).get(platform, 2.00)
        estimated_clicks = int(daily_budget / cpc) if cpc > 0 else 0

        # Seleciona os melhores artigos para promover
        candidate_articles = sorted(
            articles,
            key=lambda a: (
                a.get("score", {}).get("total", 0)
                if isinstance(a.get("score"), dict)
                else a.get("score", 0)
            ),
            reverse=True,
        )[:3]

        campaigns = []
        for article in candidate_articles:
            content = article.get("content", article)
            title = content.get("title", "Untitled")
            has_affiliate = bool(content.get("_meta", {}).get("affiliate_links"))
            intent = article.get(
                "intent", content.get("keyword_intent", "informational")
            )

            can_promote = has_affiliate or intent in ("commercial", "transactional")

            campaigns.append(
                {
                    "article_title": title,
                    "slug": content.get("slug", ""),
                    "can_promote": can_promote,
                    "intent": intent,
                    "has_affiliate_links": has_affiliate,
                    "estimated_cpc": cpc,
                    "reason": (
                        "✅ Ótimo para tráfego pago (links de afiliado + intenção comercial)"
                        if can_promote
                        else "⚠️ Apenas informacional — usar para remarketing ou topo de funil"
                    ),
                }
            )

        return {
            "niche": niche,
            "platform": platform,
            "daily_budget": daily_budget,
            "estimated_daily_clicks": estimated_clicks,
            "estimated_monthly_clicks": estimated_clicks * 30,
            "estimated_monthly_cost": daily_budget * 30,
            "cpc": cpc,
            "campaigns": campaigns,
            "total_campaigns": len(campaigns),
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        # Get decision from revenue monitor (passed via context)
        revenue_decision = campaign.get("revenue_decision", {})
        budget_allocation = campaign.get("budget_allocation", {})
        articles = campaign.get("articles", [])
        niches = campaign.get("niches", ["tecnologia", "financas", "saude", "carreira"])

        should_activate = revenue_decision.get("activate", False)
        total_budget = revenue_decision.get("budget", 0)

        if not should_activate:
            output = {
                "status": "inactive",
                "reason": revenue_decision.get(
                    "reason", "Receita insuficiente para tráfego pago"
                ),
                "prerequisites": {
                    "min_monthly_revenue": campaign.get("min_monthly_revenue", 500),
                    "current_revenue": campaign.get("current_revenue", 0),
                    "gap": max(
                        0,
                        campaign.get("min_monthly_revenue", 500)
                        - campaign.get("current_revenue", 0),
                    ),
                },
            }
            trace = AgentTrace(
                agent=self.name,
                step_id="paid_traffic",
                status="skipped",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc).isoformat(),
                duration_ms=0,
                thread_name="main",
                notes=["Tráfego pago não ativado — aguardando receita mínima"],
                metadata=output,
            )
            return AgentResult(
                agent=self.name, status="skipped", output=output, trace=trace
            )

        # Create campaign plans for each niche × platform
        platform_plans = {}
        for niche in niches:
            niche_articles = [
                a
                for a in articles
                if (
                    a.get("niche") == niche
                    or a.get("content", {}).get("section") == niche
                )
            ] or articles[:5]

            platform_plans[niche] = {}
            for platform, plat_alloc in budget_allocation.items():
                if platform == "testing":
                    continue
                plat_budget = plat_alloc.get("daily_budget", 0)
                if plat_budget <= 0:
                    continue

                plan = self._create_campaign_plan(
                    niche, plat_budget, platform, niche_articles
                )
                platform_plans[niche][platform] = plan

        # Summary
        total_campaigns = sum(
            len(niche_plans.get(p, {}).get("campaigns", []))
            for niche_plans in platform_plans.values()
            for p in niche_plans
        )

        output = {
            "status": "active",
            "total_daily_budget": total_budget,
            "total_monthly_budget": round(total_budget * 30, 2),
            "total_campaigns": total_campaigns,
            "active_niches": list(platform_plans.keys()),
            "niche_plans": platform_plans,
            "execution_plan": {
                "phase_1_setup": "Criar contas nas plataformas (Google Ads, Meta Ads)",
                "phase_2_campaigns": "Configurar campanhas com criativos gerados",
                "phase_3_launch": "Iniciar com 50% do budget, escalar conforme ROAS",
                "phase_4_optimize": "Ajustar lances, públicos e criativos semanalmente",
                "phase_5_scale": "Dobrar budget em campanhas com ROAS > 3.0",
            },
            "platform_order": [
                "1. Google Ads — Maior intenção de compra (60% budget)",
                "2. Meta Ads — Remarketing + públicos frios (30% budget)",
                "3. Native Ads — Reconhecimento de marca (10% budget)",
            ],
            "risk_management": [
                "Nunca ultrapassar ROAS < 1.0 por mais de 3 dias",
                "Parar campanha se ROAS < 1.0 por 7 dias",
                "Nunca investir mais que 50% da receita do mês anterior",
                "Manter 20% do budget para testar novos criativos",
            ],
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="paid_traffic_orchestrator",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=int(
                (
                    datetime.fromisoformat(finished_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
                * 1000
            ),
            thread_name="main",
            notes=[
                f"Plano criado: {total_campaigns} campanhas em {len(platform_plans)} nichos"
            ],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
