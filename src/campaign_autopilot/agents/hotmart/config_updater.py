"""AffiliateConfigUpdaterAgent — Atualiza configs/affiliate_offers.json com links coletados."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("config_updater")

CONFIG_PATH = Path("configs/affiliate_offers.json")


class AffiliateConfigUpdaterAgent(AgentBase):
    """Le os links do banco Hotmart e atualiza o arquivo de configuracao."""

    def __init__(self, **kwargs) -> None:
        super().__init__("config_updater", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            # Load current config
            config = {}
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH) as f:
                    config = json.load(f)

            # Get links from HotmartLinkStore
            from .link_manager import HotmartLinkStore

            store = HotmartLinkStore()
            all_links = store.get_links()

            # Merge links into config
            for link in all_links:
                niche = link.get("niche", "tecnologia")
                product = {
                    "network": "hotmart",
                    "product_name": link["product_name"],
                    "product_url": link["product_url"],
                    "commission_type": link.get("commission_type", "percentage"),
                    "commission_value": link.get("commission_value", 50.0),
                    "keywords": link.get("keywords", []),
                    "cookie_days": link.get("cookie_days", 30),
                }

                # Ensure niche exists
                if "offers_by_niche" not in config:
                    config["offers_by_niche"] = {}
                if niche not in config["offers_by_niche"]:
                    config["offers_by_niche"][niche] = []

                # Add or update (avoid duplicate by product_url)
                existing = [
                    p
                    for p in config["offers_by_niche"][niche]
                    if p.get("product_url") == link["product_url"]
                ]
                if existing:
                    existing[0].update(product)
                else:
                    config["offers_by_niche"][niche].append(product)

            # Save
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # Count
            total_offers = sum(
                len(v) for v in config.get("offers_by_niche", {}).values()
            )
            hotmart_offers = sum(
                1
                for v in config.get("offers_by_niche", {}).values()
                for p in v
                if p.get("network") == "hotmart"
            )

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="update_config",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    f"saved: {CONFIG_PATH}",
                    f"total: {total_offers}",
                    f"hotmart: {hotmart_offers}",
                ],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "config_path": str(CONFIG_PATH),
                    "total_offers": total_offers,
                    "hotmart_offers": hotmart_offers,
                    "niches_updated": len(config.get("offers_by_niche", {})),
                },
                trace=trace,
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="update_config",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    error=str(e)[:500],
                ),
            )
