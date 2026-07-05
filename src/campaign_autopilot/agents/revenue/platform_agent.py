"""PlatformAffiliateAgent — Selecao e configuracao automatica de afiliados para ML, Shopee, SheIn, AliExpress.

Usa banco curado de produtos + codigo de afiliado do usuario para
construir links automaticamente e registrar no sistema.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ...logging_utils import StructuredLogger
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from .base import RevenueBaseAgent, RevenueProtocol
from .memory import RevenueMemory
from .platform_products import (
    PLATFORM_LINK_PATTERNS,
    get_products_by_platform,
    get_all_platforms,
)

log = StructuredLogger("platform_affiliate")

CONFIG_PATH = Path("configs/affiliate_offers.json")


class PlatformAffiliateAgent(RevenueBaseAgent):
    """Agente unificado para ML, Shopee, SheIn, AliExpress.

    E2E:
    1. Usuario informa codigos de afiliado de cada plataforma (1x)
    2. Agente seleciona melhores produtos do banco curado
    3. Constroi links de afiliado automaticamente
    4. Registra no configs/affiliate_offers.json
    """

    def __init__(self, platform: str = "mercadolivre", **kwargs):
        protocol = RevenueProtocol(
            name=PLATFORM_LINK_PATTERNS.get(platform, {}).get("name", platform),
            source_type="affiliate",
        )
        super().__init__(f"affiliate_{platform}", protocol, **kwargs)
        self.platform = platform
        self.platform_info = PLATFORM_LINK_PATTERNS.get(platform, {})
        self.memory = RevenueMemory()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "protocol")

            if action == "protocol":
                return self._show_protocol(started_at)
            elif action == "autosetup":
                return self._autosetup(campaign, started_at)
            elif action == "status":
                return self._status(started_at)
            elif action == "list_products":
                return self._list_products(campaign, started_at)
            else:
                return self._show_protocol(started_at)

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id=self.platform,
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _show_protocol(self, started_at: str) -> AgentResult:
        info = self.platform_info
        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "platform": self.platform,
                "platform_name": info.get("name", self.platform),
                "signup_url": info.get("signup_url", ""),
                "link_format": info.get("link_format", ""),
                "protocol": [
                    f"1. Crie conta em {info.get('signup_url', '')}",
                    "2. Obtenha seu codigo de afiliado",
                    "3. Informe o codigo ao sistema (via .env ou autosetup)",
                    "4. Execute autosetup para configurar ofertas automaticamente",
                ],
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="protocol",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )

    def _autosetup(self, campaign: dict, started_at: str) -> AgentResult:
        """Configuracao automatica: seleciona produtos e registra."""
        affiliate_code = campaign.get("affiliate_code", "")
        if not affiliate_code:
            # Try to get from env
            import os

            env_key = f"{self.platform.upper()}_AFFILIATE_ID"
            affiliate_code = os.getenv(env_key, "")

        if not affiliate_code:
            return AgentResult(
                agent=self.name,
                status="error",
                output={
                    "error": "affiliate_code_required",
                    "message": f"Preciso do seu codigo de afiliado {self.platform_info.get('name', self.platform)}! "
                    f"Crie conta em {self.platform_info.get('signup_url', '')} "
                    f"e me passe o codigo ou coloque em .env como {self.platform.upper()}_AFFILIATE_ID",
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="autosetup",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        niche = campaign.get("niche", "all")
        max_per_niche = campaign.get("max_per_niche", 4)

        # Selecionar produtos
        if niche == "all":
            products_to_register = get_products_by_platform(self.platform)
        else:
            all_products = get_products_by_platform(self.platform)
            products_to_register = [p for p in all_products if p.niche == niche]

        # Limitar por nicho
        niche_counts: dict[str, int] = {}
        filtered = []
        for p in products_to_register:
            n = p.niche
            if niche_counts.get(n, 0) >= max_per_niche:
                continue
            niche_counts[n] = niche_counts.get(n, 0) + 1
            filtered.append(p)

        # Construir URLs e registrar
        registered = self._register_in_config(filtered, affiliate_code)

        # Atualizar memory se registrou algo
        if registered > 0:
            self.memory.update_source(self.platform, status="active", revenue=0.0)

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="autosetup",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"registered: {registered}", f"niche: {niche}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "action": "autosetup",
                "platform": self.platform,
                "platform_name": self.platform_info.get("name", self.platform),
                "affiliate_code": affiliate_code,
                "products_found": len(filtered),
                "registered": registered,
                "by_niche": dict(niche_counts),
                "message": f"✅ Configurei {registered} produtos da {self.platform_info.get('name', self.platform)} "
                f"com seu codigo de afiliado!",
            },
            trace=trace,
        )

    def _register_in_config(self, products: list, affiliate_code: str) -> int:
        """Registra produtos no config JSON."""
        if not CONFIG_PATH.exists():
            return 0

        with open(CONFIG_PATH) as f:
            config = json.load(f)

        if "offers_by_niche" not in config:
            config["offers_by_niche"] = {}
        if "affiliate_ids" not in config:
            config["affiliate_ids"] = {}

        # Salvar codigo de afiliado
        config["affiliate_ids"][self.platform] = affiliate_code

        count = 0
        for p in products:
            niche = p.niche
            if niche not in config["offers_by_niche"]:
                config["offers_by_niche"][niche] = []

            # Check if already exists
            existing = [
                o
                for o in config["offers_by_niche"][niche]
                if o.get("network") == self.platform
                and o.get("product_name") == p.product_name
            ]
            if existing:
                continue

            # Construir URL de afiliado
            url = p.build_url(affiliate_code)

            config["offers_by_niche"][niche].append(
                {
                    "network": self.platform,
                    "product_name": p.product_name,
                    "product_url": url,
                    "product_id": p.product_id,
                    "commission_type": p.commission_type,
                    "commission_value": p.commission_pct,
                    "keywords": p.keywords or [p.product_name.lower(), p.niche],
                    "cookie_days": p.cookie_days,
                    "auto_collected": True,
                }
            )
            count += 1

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return count

    def _status(self, started_at: str) -> AgentResult:
        """Status dos produtos desta plataforma."""
        status_list = self.memory.get_status()
        my_status = next((s for s in status_list if s["source"] == self.platform), {})

        config_count = 0
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                config = json.load(f)
            for niche, offers in config.get("offers_by_niche", {}).items():
                config_count += sum(
                    1
                    for o in offers
                    if o.get("network") == self.platform and o.get("auto_collected")
                )

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "platform": self.platform,
                "active_offers": config_count,
                "status": my_status.get("status", "pending"),
                "total_revenue": my_status.get("revenue", 0),
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="status",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )

    def _list_products(self, campaign: dict, started_at: str) -> AgentResult:
        """Lista produtos disponiveis para esta plataforma."""
        niche = campaign.get("niche", "all")

        if niche == "all":
            products = get_products_by_platform(self.platform)
        else:
            products = [
                p for p in get_products_by_platform(self.platform) if p.niche == niche
            ]

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "platform": self.platform,
                "total": len(products),
                "products": [
                    {
                        "name": p.product_name,
                        "niche": p.niche,
                        "price": p.price_brl,
                        "commission": f"{p.commission_pct}%",
                    }
                    for p in products
                ],
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="list",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )


class AllPlatformsSetupAgent(AgentBase):
    """Configura todas as plataformas de uma vez."""

    def __init__(self, **kwargs):
        super().__init__("all_platforms_setup", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            affiliate_codes = campaign.get("affiliate_codes", {})

            results = {}
            errors = []
            total_registered = 0

            for platform in get_all_platforms():
                code = affiliate_codes.get(platform, "")
                if not code:
                    # Try env
                    import os

                    env_key = f"{platform.upper()}_AFFILIATE_ID"
                    code = os.getenv(env_key, "")

                if not code:
                    errors.append(f"{platform}: codigo de afiliado nao fornecido")
                    results[platform] = {"status": "skipped", "reason": "no_code"}
                    continue

                agent = PlatformAffiliateAgent(platform=platform)
                plat_ctx = CampaignContext(
                    campaign={
                        "action": "autosetup",
                        "affiliate_code": code,
                        "niche": "all",
                        "max_per_niche": 4,
                    }
                )
                result = agent.run(plat_ctx)

                if result.status == "success":
                    registered = result.output.get("registered", 0)
                    total_registered += registered
                    results[platform] = {
                        "status": "success",
                        "registered": registered,
                        "message": result.output.get("message", ""),
                    }
                else:
                    errors.append(
                        f"{platform}: {result.output.get('error', 'unknown')}"
                    )
                    results[platform] = {
                        "status": "error",
                        "error": result.output.get("error", ""),
                    }

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="setup_all",
                status="success" if not errors else "partial",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[f"total: {total_registered}", f"errors: {len(errors)}"],
            )
            return AgentResult(
                agent=self.name,
                status="success",
                output={
                    "total_registered": total_registered,
                    "results": results,
                    "errors": errors[:10],
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
                    step_id="setup_all",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )
