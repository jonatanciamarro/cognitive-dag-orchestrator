"""GenericAffiliateNetworkAgent — Monetizze, Kiwify, Eduzz, etc.

Todas seguem o mesmo protocolo do Hotmart:
cada produto gera um link UNICO com parametro de afiliado.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentResult, AgentTrace, CampaignContext
from .base import RevenueBaseAgent, RevenueProtocol
from .memory import RevenueMemory
from ...logging_utils import StructuredLogger

log = StructuredLogger("generic_affiliate")

CONFIG_PATH = Path("configs/affiliate_offers.json")

NETWORKS = {
    "monetizze": {
        "name": "Monetizze",
        "url_patterns": [r"monetizze\.com\.br", r"monetizze\.com", r"app\.monetizze"],
        "signup_url": "https://monetizze.com.br/cadastro-afiliado",
        "param": "afiliado",
    },
    "kiwify": {
        "name": "Kiwify",
        "url_patterns": [r"kiwify\.com\.br", r"kiwify\.com", r"app\.kiwify"],
        "signup_url": "https://kiwify.com.br/afiliados",
        "param": "afiliado",
    },
    "eduzz": {
        "name": "Eduzz",
        "url_patterns": [r"eduzz\.com", r"eduzz\.com\.br", r"app\.eduzz"],
        "signup_url": "https://eduzz.com/afiliados",
        "param": "afiliado",
    },
    "mercadolivre": {
        "name": "Mercado Livre",
        "url_patterns": [r"mercadolivre\.com\.br", r"mercadolibre"],
        "signup_url": "https://mercadolivre.com.br/afiliados",
        "param": "afiliado",
    },
    "shopee": {
        "name": "Shopee",
        "url_patterns": [r"shopee\.com\.br", r"shopee\.com"],
        "signup_url": "https://shopee.com.br/afiliados",
        "param": "afiliado",
    },
    "shein": {
        "name": "SheIn",
        "url_patterns": [r"shein\.com"],
        "signup_url": "https://shein.com/afiliados",
        "param": "afiliado",
    },
    "aliexpress": {
        "name": "AliExpress",
        "url_patterns": [r"aliexpress\.com"],
        "signup_url": "https://portuguese.aliexpress.com/afiliados",
        "param": "afiliado",
    },
}


class GenericAffiliateNetworkAgent(RevenueBaseAgent):
    """Agente unico para Monetizze, Kiwify, Eduzz e outras redes similares.

    Protocolo E2E:
    1. SETUP: Criar conta na rede, obter link de afiliado
    2. INTEGRATE: Adicionar links ao configs/affiliate_offers.json
    3. ACTIVATE: AffiliateLinkInserterAgent insere nos artigos
    4. MONITOR: RevenueMemory registra cliques e conversoes
    5. OPTIMIZE: Substituir ofertas de baixa performance
    """

    def __init__(self, network: str = "monetizze", **kwargs):
        protocol = RevenueProtocol(
            name=NETWORKS.get(network, {}).get("name", network),
            source_type="affiliate",
        )
        super().__init__(f"affiliate_{network}", protocol, **kwargs)
        self.network = network
        self.network_info = NETWORKS.get(network, {})
        self.memory = RevenueMemory()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "protocol")

            if action == "protocol":
                return self._show_protocol(started_at)
            elif action == "validate":
                return self._validate_links(started_at)
            elif action == "add_link":
                return self._add_link(campaign, started_at)
            elif action == "status":
                return self._status(started_at)
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
                    step_id=self.network,
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _show_protocol(self, started_at: str) -> AgentResult:
        info = self.network_info
        protocol = self.protocol.get_protocol_steps()

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="protocol",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"network: {self.network}", f"steps: {len(protocol)}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "network": self.network,
                "network_name": info.get("name", self.network),
                "signup_url": info.get("signup_url", ""),
                "protocol": protocol,
                "steps": [
                    f"1. Acesse {info.get('signup_url', '')} e crie conta",
                    "2. No catalogo, escolha produtos do seu nicho",
                    "3. Copie o link de afiliado de cada produto",
                    "4. Adicione os links no configs/affiliate_offers.json",
                    "5. O sistema insere automaticamente nos artigos",
                ],
            },
            trace=trace,
        )

    def _validate_links(self, started_at: str) -> AgentResult:
        info = self.network_info
        issues = []
        valid = 0
        invalid = 0

        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
            for niche, products in data.get("offers_by_niche", {}).items():
                for p in products:
                    if p.get("network") != self.network:
                        continue
                    url = p.get("product_url", "")
                    # Check basic validity
                    patterns = info.get("url_patterns", [])
                    is_valid = (
                        any(re.search(pat, url) for pat in patterns)
                        if patterns
                        else bool(url)
                    )
                    if is_valid and p.get("product_name"):
                        valid += 1
                    else:
                        invalid += 1
                        issues.append(
                            f"[{niche}] {p.get('product_name', '?')}: link invalido"
                        )

        self.memory.update_source(
            self.network, status="validated" if valid > 0 else "pending"
        )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="validate",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"valid: {valid}", f"invalid: {invalid}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={"valid": valid, "invalid": invalid, "issues": issues},
            trace=trace,
        )

    def _add_link(self, campaign: dict, started_at: str) -> AgentResult:
        name = campaign.get("product_name", "")
        url = campaign.get("product_url", "")
        niche = campaign.get("niche", "tecnologia")

        if not name or not url:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": "product_name e product_url obrigatorios"},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="add",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        # Add to config
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
            if "offers_by_niche" not in data:
                data["offers_by_niche"] = {}
            if niche not in data["offers_by_niche"]:
                data["offers_by_niche"][niche] = []
            data["offers_by_niche"][niche].append(
                {
                    "network": self.network,
                    "product_name": name,
                    "product_url": url,
                    "commission_type": "percentage",
                    "commission_value": campaign.get("commission_value", 50.0),
                    "keywords": campaign.get("keywords", [name.lower()]),
                    "cookie_days": campaign.get("cookie_days", 30),
                }
            )
            CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))

        self.memory.update_source(
            self.network, status="active", config={"products_count": 1}
        )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="add_link",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"added: {name}", f"niche: {niche}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={"added": True, "product": name, "niche": niche},
            trace=trace,
        )

    def _status(self, started_at: str) -> AgentResult:
        status_list = self.memory.get_status()
        my_status = next((s for s in status_list if s["source"] == self.network), {})

        config_count = 0
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
            for niche, products in data.get("offers_by_niche", {}).items():
                config_count += sum(
                    1 for p in products if p.get("network") == self.network
                )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="status",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[
                f"links: {config_count}",
                f"status: {my_status.get('status', 'pending')}",
            ],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "network": self.network,
                "config_offers": config_count,
                "status": my_status.get("status", "pending"),
                "total_revenue": my_status.get("revenue", 0),
            },
            trace=trace,
        )
