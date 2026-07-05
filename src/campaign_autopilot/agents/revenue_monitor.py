"""⚠️ NOTA: Use agents/paid_traffic/revenue_monitor.py em vez deste.

Este agente será removido em versão futura.

Agente de Monitoramento de Receita — tracking de comissões, cliques, taxas de conversão e ROI."""

from __future__ import annotations

import sqlite3
from typing import Any
from pathlib import Path

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


class RevenueMonitorAgent(AgentBase):
    """Monitora receita de afiliados, taxas de conversão e ROI por canal.

    Este agente é o 'financeiro' do sistema: ele calcula quanto cada canal
    está gerando, quais ofertas convertem melhor, e onde focar os esforços.
    """

    def __init__(self, db_path: str = "", **kwargs) -> None:
        super().__init__("revenue_monitor", **kwargs)
        self.db_path = db_path or str(Path(__file__).resolve().parent.parent.parent.parent / ".state" / "revenue.db")

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(
            campaign.get("niche", campaign.get("objective", "marketing digital"))
        )

        # Get offers that were used this cycle
        offers_step = context.step_results.get("offer_lookup", {})
        offers_out = (
            offers_step.get("output", {}) if isinstance(offers_step, dict) else {}
        )
        offers = offers_out.get("available_offers", [])

        # Get content produced this cycle
        gen = context.step_results.get("content_generator", {})
        gen_out = gen.get("output", {}) if isinstance(gen, dict) else {}
        articles = gen_out.get("articles", [])

        yt = context.step_results.get("youtube_marketing", {})
        yt_out = yt.get("output", {}) if isinstance(yt, dict) else {}
        videos = yt_out.get("videos", [])

        em = context.step_results.get("email_marketing", {})
        em_out = em.get("output", {}) if isinstance(em, dict) else {}

        pubs = context.step_results.get("wp_publisher", {})
        pubs_out = pubs.get("output", {}) if isinstance(pubs, dict) else {}
        publications = pubs_out.get("publications", [])

        # Simulated revenue projections based on industry benchmarks
        # These are placeholders until real API tracking is connected
        revenue_projections = self._calculate_projections(
            articles=articles,
            videos=videos,
            emails=em_out.get("total_emails", 0),
            publications=publications,
            offers=offers,
        )

        # Try to load historical data if db_path is available
        historical = self._load_historical(context)
        self._save_revenue(context, revenue_projections, offers)

        output = {
            "current_cycle": {
                "content_produced": {
                    "articles": len(articles),
                    "videos": len(videos),
                    "emails": em_out.get("total_emails", 0),
                    "publications": len(publications),
                },
                "offers_available": len(offers),
                "top_offers": [
                    {
                        "name": o.get("product_name", "?"),
                        "network": o.get("network", "?"),
                        "commission": f"{o.get('commission_value', 0)}%",
                        "price": f"R${o.get('price', 0):.2f}",
                        "estimated_commission": round(
                            o.get("price", 0) * o.get("commission_value", 0) / 100, 2
                        ),
                        "cookie_days": o.get("cookie_days", 30),
                    }
                    for o in offers[:5]
                ],
                **revenue_projections,
            },
            "historical": historical or {"cycles_tracked": 0},
            "niche": niche,
            "recommendation": self._generate_recommendation(
                offers, revenue_projections
            ),
            "config_required": {
                "hotmart": "HOTMART_CLIENT_ID + HOTMART_CLIENT_SECRET",
                "amazon": "AMAZON_ACCESS_KEY + AMAZON_SECRET_KEY + AMAZON_ASSOCIATE_TAG",
                "tracking": "Integrar pixel de conversão nas páginas",
            },
        }

        # Record explanation
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="revenue_monitoring",
                input_state={"offers": len(offers), "articles": len(articles)},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "estimated_monthly_revenue": revenue_projections.get(
                        "estimated_monthly_revenue", 0
                    ),
                    "top_offer": offers[0].get("product_name") if offers else "",
                },
            )

        # Semantic memory
        if self.semantic_memory and offers:
            rev_concept = self.semantic_memory.register_concept(
                f"rev_{context.run_id[:8]}",
                "revenue",
                f"Receita estimada: R${revenue_projections.get('estimated_monthly_revenue', 0)}",
            )
            for offer in offers[:3]:
                offer_concept = self.semantic_memory.find_concept(
                    offer.get("product_name", "")[:50], "offer"
                )
                if offer_concept:
                    self.semantic_memory.assert_claim(
                        subject=rev_concept,
                        predicate="includes_offer",
                        object=offer_concept["concept_id"],
                        confidence=0.6,
                        evidence_type="STATISTICAL_INFERENCE",
                        epistemic_status="HYPOTHETICAL",
                        supporting_data={
                            "estimated_commission": round(
                                offer.get("price", 0)
                                * offer.get("commission_value", 0)
                                / 100,
                                2,
                            ),
                            "cookie_days": offer.get("cookie_days", 30),
                        },
                        source_cycle_id=context.run_id,
                        asserted_by=self.name,
                        observer_id=self.name,
                    )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="revenue_monitor",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Projeção mensal: R${revenue_projections.get('estimated_monthly_revenue', 0):.2f} com {len(offers)} ofertas"
            ],
            metadata={
                "offers": len(offers),
                "articles": len(articles),
                "estimated_monthly_revenue": revenue_projections.get(
                    "estimated_monthly_revenue", 0
                ),
                "estimated_monthly_clicks": revenue_projections.get(
                    "estimated_monthly_clicks", 0
                ),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _calculate_projections(
        articles: list,
        videos: list,
        emails: int,
        publications: list,
        offers: list,
    ) -> dict[str, Any]:
        """Calculate revenue projections based on content volume and industry benchmarks.

        Benchmarks (conservadores para iniciantes):
        - Blog: 100-500 visitas/mês por artigo no primeiro mês
        - YouTube: 50-200 views/mês por vídeo
        - Email: 10-30% open rate, 2-5% click rate
        - Pinterest: 100-1000 impressions/mês por pin
        - Taxa de conversão afiliados: 1-3% (iniciante), 3-8% (estabelecido)
        """
        total_articles = len(articles)
        total_videos = len(videos)
        total_publications = len(publications)

        # Traffic estimates (monthly, conservative)
        blog_traffic = total_articles * 200  # 200 visits/article/month
        video_views = total_videos * 100  # 100 views/video/month

        # Clicks from traffic (CTR ~3% for content)
        blog_clicks = int(blog_traffic * 0.03)
        video_clicks = int(video_views * 0.05)
        email_clicks = int(emails * 0.02) if emails else 0
        total_clicks = blog_clicks + video_clicks + email_clicks

        # Revenue projections (conservative)
        avg_commission = 0
        if offers:
            commissions = [
                o.get("price", 0) * o.get("commission_value", 0) / 100
                for o in offers
                if o.get("price") and o.get("commission_value")
            ]
            if commissions:
                avg_commission = sum(commissions) / len(commissions)

        # Conversion rate: 2% for content (conservative)
        conversion_rate = 0.02
        estimated_conversions = int(total_clicks * conversion_rate)
        estimated_revenue = estimated_conversions * avg_commission

        # Scale up for monthly (each cycle produces this much, 2 cycles/month = 48h interval)
        cycles_per_month = 15  # every 48h = ~15 cycles/month
        monthly_clicks = total_clicks * cycles_per_month
        monthly_conversions = int(monthly_clicks * conversion_rate)
        monthly_revenue = round(monthly_conversions * avg_commission, 2)

        return {
            "estimated_monthly_traffic": blog_traffic * cycles_per_month
            + video_views * cycles_per_month,
            "estimated_monthly_clicks": monthly_clicks,
            "estimated_monthly_conversions": monthly_conversions,
            "estimated_monthly_revenue": monthly_revenue,
            "avg_commission_per_sale": round(avg_commission, 2),
            "conversion_rate_assumed": conversion_rate,
            "cycles_per_month": cycles_per_month,
            "note": "Projeções conservadoras baseadas em benchmarks de mercado. Conecte APIs reais para dados precisos.",
            "disclaimer": "Estes valores são estimativas. Resultados reais variam conforme nicho, qualidade do conteúdo e estratégia.",
        }

    def _save_revenue(self, context, projections, offers):
        """Write revenue projections to revenue.db."""
        if not self.db_path:
            return
        try:
            conn = sqlite3.connect(self.db_path)
            monthly = projections.get("estimated_monthly_revenue", 0)
            clicks = projections.get("estimated_monthly_clicks", 0)
            convs = projections.get("estimated_monthly_conversions", 0)
            conn.execute(
                "INSERT INTO revenue_events (source, event_type, amount, description, created_at) VALUES (?,?,?,?,?)",
                ("campaign_autopilot", "cycle_projection", monthly,
                 f"Cycle {context.run_id}: {convs} conversions, {clicks} clicks", utc_now_iso())
            )
            for offer in offers[:5]:
                net = offer.get("network", "unknown")
                est = offer.get("price", 0) * offer.get("commission_value", 0) / 100
                cur = conn.execute(
                    "UPDATE revenue_sources SET total_revenue = total_revenue + ?, total_clicks = total_clicks + ?, last_active = ? WHERE source = ?",
                    (est, clicks // max(1, len(offers[:5])), utc_now_iso(), net)
                )
                if cur.rowcount == 0:
                    conn.execute(
                        "INSERT INTO revenue_sources (source, status, config, total_revenue, total_clicks, last_active, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                        (net, "active", "{}", est, clicks // max(1, len(offers[:5])), utc_now_iso(), utc_now_iso(), utc_now_iso())
                    )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _load_historical(self, context: CampaignContext) -> dict[str, Any] | None:
        """Load historical cycle data from database if available."""
        if not self.db_path:
            return None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT COUNT(*) as cycles, COALESCE(SUM(total_words_generated),0) as words, "
                "COALESCE(SUM(total_videos_generated),0) as videos, "
                "COALESCE(SUM(total_emails_generated),0) as emails "
                "FROM autopilot_cycles"
            ).fetchone()
            conn.close()
            if rows and rows["cycles"] > 0:
                return {
                    "cycles_tracked": rows["cycles"],
                    "total_words": rows["words"],
                    "total_videos": rows["videos"],
                    "total_emails": rows["emails"],
                }
            return {"cycles_tracked": 0}
        except Exception:
            return {"cycles_tracked": 0, "error": "Could not access database"}

    @staticmethod
    def _generate_recommendation(offers: list, projections: dict) -> str:
        """Generate actionable revenue recommendation."""
        if not offers:
            return "Nenhuma oferta de afiliado encontrada. Configure integração com Hotmart ou Amazon."

        top_offer = max(
            offers, key=lambda o: o.get("price", 0) * o.get("commission_value", 0) / 100
        )
        avg_comm = projections.get("avg_commission_per_sale", 0)
        monthly_rev = projections.get("estimated_monthly_revenue", 0)

        if monthly_rev > 1000:
            return (
                f"Projeção mensal: R${monthly_rev:.2f}. "
                f"Foco em escalar oferta '{top_offer.get('product_name', '')}' "
                f"(comissão média R${avg_comm:.2f}/venda). "
                f"Priorizar SEO para aumentar tráfego orgânico."
            )
        else:
            return (
                f"Fase inicial: projeção de R${monthly_rev:.2f}/mês. "
                f"Principal oferta: '{top_offer.get('product_name', '')}' "
                f"(R${avg_comm:.2f}/venda, {top_offer.get('cookie_days', 30)}d cookie). "
                f"Produzir mais conteúdo e diversificar canais para escalar."
            )
