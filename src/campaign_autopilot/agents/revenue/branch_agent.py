"""RevenueBranchAgent — Step individual de uma fonte de renda na árvore paralela.

Cada instância representa UMA fonte (hotmart, shopee, ml, etc).
Todas rodam em paralelo via ThreadPoolExecutor do workflow engine.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext

# Mapa de fontes → nome amigável + env_var
SOURCE_MAP: dict[str, dict[str, str]] = {
    "hotmart": {"name": "Hotmart", "env": "HOTMART_CLIENT_ID"},
    "kiwify": {"name": "Kiwify", "env": "KIWIFY_AFFILIATE_ID"},
    "eduzz": {"name": "Eduzz", "env": "EDUZZ_AFFILIATE_ID"},
    "monetizze": {"name": "Monetizze", "env": "MONETIZZE_AFFILIATE_ID"},
    "mercadolivre": {"name": "Mercado Livre", "env": "MERCADOLIVRE_AFFILIATE_ID"},
    "shopee": {"name": "Shopee", "env": "SHOPEE_AFFILIATE_ID"},
    "shein": {"name": "SheIn", "env": "SHEIN_AFFILIATE_ID"},
    "aliexpress": {"name": "AliExpress", "env": "ALIEXPRESS_AFFILIATE_ID"},
    "amazon": {"name": "Amazon", "env": "AMAZON_ASSOCIATES_TAG"},
    "adsense": {"name": "AdSense", "env": ""},
    "cpa": {"name": "CPA", "env": ""},
    "digital_product": {"name": "Produto Digital", "env": ""},
    "membership": {"name": "Assinatura", "env": ""},
}


class RevenueBranchAgent(AgentBase):
    """Step individual de fonte de renda na árvore paralela."""

    def __init__(self, source: str = "", **kwargs):
        name = f"revenue_{source}" if source else "revenue_branch"
        super().__init__(name, **kwargs)
        self._source_id = source

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        source_id = (
            context.campaign.get("source", self._source_id)
            if hasattr(context, "campaign")
            else self._source_id
        )
        info = SOURCE_MAP.get(source_id, {"name": source_id, "env": ""})

        env_var = info.get("env", "")
        configured = bool(os.getenv(env_var)) if env_var else True

        products = 0
        revenue_est = 0.0
        affiliate_code = ""

        if configured:
            try:
                import json
                from pathlib import Path

                cfg = Path("configs/affiliate_offers.json")
                if cfg.exists():
                    data = json.loads(cfg.read_text())
                    code = data.get("affiliate_ids", {}).get(source_id, "")
                    affiliate_code = code or "configurado"
                    for niche, offers in data.get("offers_by_niche", {}).items():
                        for p in offers:
                            if isinstance(p, dict) and p.get("network") == source_id:
                                products += 1
                    revenue_est = products * 15.0
            except Exception:
                pass

        finished_at = datetime.now(timezone.utc).isoformat()
        d_ms = 0
        try:
            from ..base import iso_duration_ms

            d_ms = iso_duration_ms(started_at, finished_at)
        except Exception:
            pass

        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "source": source_id,
                "name": info["name"],
                "configured": configured,
                "active": configured,
                "products": products,
                "estimated_monthly_revenue": round(revenue_est, 2),
                "affiliate_code": affiliate_code,
                "env_var": env_var,
            },
            trace=AgentTrace(
                agent=self.name,
                step_id=source_id or "branch",
                status="success" if configured else "pending",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=d_ms,
                thread_name="main",
            ),
        )
