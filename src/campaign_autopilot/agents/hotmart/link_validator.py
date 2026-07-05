"""LinkValidatorAgent — Valida links de afiliado Hotmart (formato, duplicatas, placeholders)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("link_validator")

CONFIG_PATH = Path("configs/affiliate_offers.json")

HOTMART_PATTERNS = [
    re.compile(r"^https?://(?:www\.)?hotm\.art/"),
    re.compile(r"^https?://(?:www\.)?hotmart\.com/"),
    re.compile(r"^https?://(?:www\.)?clubhotmart\.com/"),
    re.compile(r"^https?://[a-z]+\.hotmart\.com/"),
]


class LinkValidatorAgent(AgentBase):
    """Valida links de afiliado: formato, presenca de aff, duplicatas, placeholders."""

    def __init__(self, **kwargs) -> None:
        super().__init__("link_validator", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            link = campaign.get("link", "")
            action = campaign.get("action", "validate")

            if action == "validate_all":
                return self._validate_all(started_at)

            product_name = campaign.get("product_name", "desconhecido")
            network = campaign.get("network", "hotmart")

            result = self._validate_single(link, product_name, network)

            finished_at = datetime.now(timezone.utc).isoformat()
            trace = AgentTrace(
                agent=self.name,
                step_id="validate",
                status="success" if result["valid"] else "error",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[f"valid: {result['valid']}", result.get("warnings", "")[:80]],
            )
            return AgentResult(
                agent=self.name, status="success", output=result, trace=trace
            )

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="validate",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                    error=str(e)[:500],
                ),
            )

    def _validate_single(
        self, link: str, product_name: str, network: str
    ) -> dict[str, Any]:
        issues = []
        warnings = ""
        valid = True

        if not link:
            return {"valid": False, "error": "Link vazio", "issues": issues}

        # Check for placeholders
        if "seulink" in link or "exemplo" in link or "SEUCODIGO" in link:
            issues.append(
                f"PLACEHOLDER: {product_name} contem link de exemplo (seulink)"
            )
            return {
                "valid": False,
                "error": "Link placeholder — substitua pelo link real do Hotmart",
                "issues": issues,
            }

        # Check for http/https
        if not link.startswith("http://") and not link.startswith("https://"):
            issues.append("Link nao comeca com http/https")
            valid = False

        # Check for hotm.art or hotmart domain
        if network == "hotmart":
            is_hotmart = any(p.match(link) for p in HOTMART_PATTERNS)
            if not is_hotmart:
                issues.append(
                    "Link nao parece ser da Hotmart (dominio nao reconhecido)"
                )
                warnings = "dominio nao Hotmart"

            # Check for aff parameter
            if "?aff=" not in link and "&aff=" not in link:
                issues.append(
                    "Link sem parametro ?aff= — nao e um link de afiliado valido"
                )
                warnings = "faltando ?aff="
                valid = False
                return {
                    "valid": False,
                    "error": "Link sem ?aff=",
                    "warnings": warnings,
                    "issues": issues,
                }

        # Check for duplicate in config
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text())
                for niche, products in data.get("offers_by_niche", {}).items():
                    for p in products:
                        if (
                            p.get("product_url") == link
                            and p.get("product_name") != product_name
                        ):
                            issues.append(
                                f"Link duplicado: ja usado em '{p['product_name']}' ({niche})"
                            )
            except Exception:
                pass

        return {
            "valid": valid,
            "warnings": warnings,
            "issues": issues,
            "product_name": product_name,
            "link": link,
        }

    def _validate_all(self, started_at: str) -> AgentResult:
        issues = []
        valid_count = 0
        invalid_count = 0
        placeholder_count = 0

        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text())
            for niche, products in data.get("offers_by_niche", {}).items():
                for p in products:
                    if p.get("network") != "hotmart":
                        continue
                    result = self._validate_single(
                        p.get("product_url", ""), p.get("product_name", ""), "hotmart"
                    )
                    if "Placeholder" in str(
                        result.get("issues", [])
                    ) or "placeholder" in str(result.get("error", "")):
                        placeholder_count += 1
                        issues.append(f"[{niche}] Placeholder: {p['product_name']}")
                    elif result["valid"]:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        issues.append(
                            f"[{niche}] Invalido: {p['product_name']} - {result.get('warnings', '')}"
                        )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="validate_all",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[
                f"valid: {valid_count}, invalid: {invalid_count}, placeholders: {placeholder_count}"
            ],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "summary": {
                    "valid": valid_count,
                    "invalid": invalid_count,
                    "placeholders": placeholder_count,
                },
                "issues": issues,
            },
            trace=trace,
        )
