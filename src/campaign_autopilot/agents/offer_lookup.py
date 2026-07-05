"""Agente de Busca de Ofertas — lê do Hotmart Intelligence DB + config real."""

from __future__ import annotations

import json
import sqlite3
from typing import Any
from pathlib import Path

from ..affiliate import ProductLinkRegistry
from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_HOTMART_DB = _PROJECT_ROOT / ".state" / "hotmart_intelligence.db"
_AFFILIATE_CONFIG = _PROJECT_ROOT / "configs" / "affiliate_offers.json"


class OfferLookupAgent(AgentBase):
    """Lê ofertas reais do Hotmart Intelligence DB + affiliate_offers.json."""

    def __init__(self, **kwargs) -> None:
        super().__init__("offer_lookup", **kwargs)

    def _load_hotmart_offers(self) -> list[dict[str, Any]]:
        """Load qualified products from hotmart_intelligence.db."""
        if not _HOTMART_DB.exists():
            return []
        offers: list[dict[str, Any]] = []
        try:
            conn = sqlite3.connect(str(_HOTMART_DB))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT p.product_id, p.name, p.category, p.price,
                       p.commission_value, p.commission_pct, p.cookie_days,
                       p.affiliate_link, p.checkout_url, p.sales_page_url,
                       p.producer, p.status, p.temperature,
                       s.total_score, s.tier
                FROM products p
                LEFT JOIN opportunity_scores s ON p.product_id = s.product_id
                WHERE p.status = 'activated'
            """)
            for row in cur.fetchall():
                offers.append({
                    "offer_id": row["product_id"],
                    "network": "hotmart",
                    "product_name": row["name"],
                    "category": row["category"],
                    "commission_type": "percentage",
                    "commission_value": row["commission_pct"] or 0.0,
                    "price": row["price"] or 0.0,
                    "cookie_days": row["cookie_days"] or 30,
                    "affiliate_link": row["affiliate_link"] or "",
                    "checkout_url": row["checkout_url"] or "",
                    "sales_page_url": row["sales_page_url"] or "",
                    "producer": row["producer"] or "",
                    "temperature": row["temperature"] or "",
                    "opportunity_score": row["total_score"] or 0.0,
                    "tier": row["tier"] or "",
                    "data_source": "hotmart_intelligence_db",
                })
            conn.close()
        except Exception:
            pass
        return offers

    def _load_config_offers(self) -> list[dict[str, Any]]:
        """Load offers from configs/affiliate_offers.json."""
        if not _AFFILIATE_CONFIG.exists():
            return []
        offers: list[dict[str, Any]] = []
        try:
            with _AFFILIATE_CONFIG.open("r", encoding="utf-8") as fh:
                cfg = json.load(fh)
            for _niche, niche_offers in cfg.get("offers_by_niche", {}).items():
                for o in niche_offers:
                    offers.append({
                        "offer_id": f"{o['network']}_{o.get('product_name', '')[:20]}",
                        "network": o["network"],
                        "product_name": o["product_name"],
                        "category": _niche,
                        "commission_type": o.get("commission_type", "percentage"),
                        "commission_value": o.get("commission_value", 0.0),
                        "price": o.get("price", 0.0),
                        "cookie_days": o.get("cookie_days", 1),
                        "affiliate_link": o.get("product_url", ""),
                        "checkout_url": "",
                        "sales_page_url": "",
                        "keywords": o.get("keywords", []),
                        "data_source": "affiliate_offers_config",
                    })
        except Exception:
            pass
        return offers

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        seo = context.step_results.get("seo_research", {})
        seo_output = seo.get("output", {}) if isinstance(seo, dict) else {}

        niche = str(campaign.get("niche", campaign.get("objective", ""))).lower()
        keywords = [kw["keyword"] for kw in seo_output.get("top_opportunities", [])]
        keyword_text = " ".join(keywords)

        # Load real data sources (priority: DB > config)
        db_offers = self._load_hotmart_offers()
        config_offers = self._load_config_offers()
        # Resolve links reais via ProductLinkRegistry (se disponivel)
        try:
            _registry = ProductLinkRegistry()
            for offer in db_offers + config_offers:
                real_link = _registry.resolve_link(
                    offer.get("product_name", ""),
                    offer.get("network", ""),
                    offer.get("affiliate_link", ""),
                )
                if real_link:
                    offer["affiliate_link"] = real_link
                    offer["product_url"] = real_link
        except Exception:
            pass  # Registry não disponivel, usar links do config
        all_offers = db_offers + config_offers
        source_label = "hotmart_db+config" if db_offers and config_offers else (
            "hotmart_db" if db_offers else ("config" if config_offers else "none")
        )

        # Match: ofertas cuja categoria ou nome corresponde ao nicho/keywords
        matched = []
        for offer in all_offers:
            score = 0
            if offer["category"] in niche or niche in offer["category"]:
                score += 3
            if any(
                term in offer["product_name"].lower() for term in keyword_text.split()
            ):
                score += 1
            if any(term in offer["category"] for term in keyword_text.split()):
                score += 2
            # Boost: higher opportunity_score = higher relevance
            opp = offer.get("opportunity_score", 0)
            if opp > 60:
                score += 2
            elif opp > 50:
                score += 1
            if score > 0:
                offer["match_score"] = score
                matched.append(offer)

        matched.sort(key=lambda x: -x["match_score"])

        # If no match found, return top offers by score/commission
        if not matched:
            all_offers.sort(
                key=lambda x: -(x.get("opportunity_score", 0) + x.get("commission_value", 0))
            )
            matched = all_offers[:5]

        # Calcular comissão potencial
        total_potential = 0.0
        for offer in matched[:5]:
            commission = offer["commission_value"]
            price = offer["price"]
            if offer["commission_type"] == "percentage":
                estimated = price * (commission / 100)
            else:
                estimated = commission
            offer["estimated_commission_per_sale"] = round(estimated, 2)
            total_potential += estimated

        output = {
            "available_offers": matched[:10],
            "total_offers_found": len(matched),
            "source": source_label,
            "db_offers_count": len(db_offers),
            "config_offers_count": len(config_offers),
            "estimated_potential_per_sale": round(
                total_potential / max(1, len(matched[:5])), 2
            ),
            "top_networks": list(set(o["network"] for o in matched[:5])),
            "recommendation": (
                f"Ofertas reais ({source_label}): {len(matched)} para nicho '{niche}'. "
                f"DB={len(db_offers)} | Config={len(config_offers)}."
            ),
        }

        # Registrar explicação
        if self.explanation_store:
            decision_id = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="offer_lookup",
                input_state={"niche": niche, "keywords_count": len(keywords)},
            )
            self.explanation_store.update_decision_output(
                decision_id=decision_id,
                output_decision={
                    "offers_found": len(matched),
                    "top_network": output["top_networks"][0]
                    if output["top_networks"]
                    else "",
                },
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="offer_lookup",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Ofertas reais ({source_label}): {len(matched)} para nicho '{niche}'"
            ],
            metadata={"niche": niche, "offers_found": len(matched), "source": source_label},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
