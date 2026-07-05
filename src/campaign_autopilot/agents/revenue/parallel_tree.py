"""ParallelRevenueTreeAgent — Árvore de múltiplas fontes de renda em paralelo.

Dispara TODAS as fontes de renda simultaneamente via ThreadPoolExecutor:
  - Hotmart, Kiwify, Eduzz, Monetizze
  - Shopee, Mercado Livre, SheIn, AliExpress
  - Amazon, AdSense, CPA
  - Produtos Digitais, Membros

Cada fonte roda em sua própria thread. Resultados agregados ao final.
"""

from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("parallel_revenue_tree")

# Todas as fontes de renda com seus agentes e IDs de config
REVENUE_BRANCHES = [
    # Infoprodutos (redes brasileiras)
    {"id": "hotmart", "name": "Hotmart", "env_var": "HOTMART_CLIENT_ID"},
    {"id": "kiwify", "name": "Kiwify", "env_var": "KIWIFY_AFFILIATE_ID"},
    {"id": "eduzz", "name": "Eduzz", "env_var": "EDUZZ_AFFILIATE_ID"},
    {"id": "monetizze", "name": "Monetizze", "env_var": "MONETIZZE_AFFILIATE_ID"},
    # Marketplaces
    {
        "id": "mercadolivre",
        "name": "Mercado Livre",
        "env_var": "MERCADOLIVRE_AFFILIATE_ID",
    },
    {"id": "shopee", "name": "Shopee", "env_var": "SHOPEE_AFFILIATE_ID"},
    {"id": "shein", "name": "SheIn", "env_var": "SHEIN_AFFILIATE_ID"},
    {"id": "aliexpress", "name": "AliExpress", "env_var": "ALIEXPRESS_AFFILIATE_ID"},
    # Amazon
    {"id": "amazon", "name": "Amazon", "env_var": "AMAZON_ASSOCIATES_TAG"},
    # Propaganda
    {"id": "adsense", "name": "AdSense", "env_var": ""},
    # CPA
    {"id": "cpa", "name": "CPA", "env_var": ""},
    # Produtos próprios
    {"id": "digital_product", "name": "Produto Digital", "env_var": ""},
    {"id": "membership", "name": "Assinatura/Membros", "env_var": ""},
]


class ParallelRevenueTreeAgent(AgentBase):
    """Agente que executa TODAS as fontes de renda em paralelo.

    Cada fonte roda em sua própria thread.
    Resultados consolidados em um único relatório.
    """

    def __init__(self, **kwargs):
        super().__init__("parallel_revenue_tree", **kwargs)
        self._lock = threading.Lock()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "harvest")

            if action == "harvest":
                return self._harvest_all(started_at, campaign)
            elif action == "status":
                return self._status_report(started_at)
            elif action == "scan":
                return self._scan_env(started_at)
            else:
                return self._harvest_all(started_at, campaign)

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="parallel_tree",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _check_source_configured(self, branch: dict) -> bool:
        """Verifica se a fonte tem chave/config no .env."""
        env_var = branch.get("env_var", "")
        if env_var:
            return bool(os.getenv(env_var))
        return True  # fontes sem env_var (AdSense, CPA, etc) sempre ativas

    def _harvest_branch(self, branch: dict) -> dict:
        """Executa uma única fonte de renda e retorna resultado."""
        source_id = branch["id"]
        source_name = branch["name"]
        configured = self._check_source_configured(branch)

        result = {
            "source": source_id,
            "name": source_name,
            "configured": configured,
            "status": "active" if configured else "pending",
            "products": 0,
            "estimated_monthly_revenue": 0.0,
        }

        if configured:
            # Tenta carregar produtos curados do config
            try:
                import json
                from pathlib import Path

                config_path = Path("configs/affiliate_offers.json")
                if config_path.exists():
                    data = json.loads(config_path.read_text())
                    affiliate_ids = data.get("affiliate_ids", {})
                    offers = data.get("offers_by_niche", {})
                    code = affiliate_ids.get(source_id, "")
                    result["affiliate_code"] = code if code else "configurado"

                    # Conta produtos para esta plataforma
                    product_count = 0
                    for niche, products in offers.items():
                        for p in products:
                            if isinstance(p, dict) and p.get("network") == source_id:
                                product_count += 1
                    result["products"] = product_count

                    # Estima receita baseada em produtos configurados
                    result["estimated_monthly_revenue"] = (
                        product_count * 15.0
                    )  # ~R$15/produto/mês
            except Exception:
                pass

        return result

    def _harvest_all(self, started_at: str, campaign: dict) -> AgentResult:
        """Executa todas as fontes em paralelo e agrega."""
        max_workers = min(len(REVENUE_BRANCHES), 10)
        branches = list(REVENUE_BRANCHES)

        log.info(
            f"🌳 ParallelRevenueTree: {len(branches)} fontes, {max_workers} workers"
        )

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._harvest_branch, b): b for b in branches}
            for future in as_completed(futures):
                branch = futures[future]
                try:
                    result = future.result()
                    with self._lock:
                        results.append(result)
                    log.info(
                        f"  ✅ {branch['name']}: {'ativo' if result['configured'] else 'pendente'}"
                    )
                except Exception as e:
                    with self._lock:
                        results.append(
                            {
                                "source": branch["id"],
                                "name": branch["name"],
                                "configured": False,
                                "status": "error",
                                "products": 0,
                                "error": str(e),
                            }
                        )
                    log.warning(f"  ⚠️ {branch['name']}: erro - {e}")

        # Agrega resultados
        active = [r for r in results if r.get("status") == "active"]
        pending = [r for r in results if r.get("status") == "pending"]
        errors = [r for r in results if r.get("status") == "error"]
        total_revenue = sum(r.get("estimated_monthly_revenue", 0) for r in active)
        total_products = sum(r.get("products", 0) for r in results)

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="harvest_all",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[
                f"{len(active)} ativas, {len(pending)} pendentes, R$ {total_revenue:.2f}/mês"
            ],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "status": "success",
                "total_sources": len(branches),
                "active_sources": len(active),
                "pending_sources": len(pending),
                "error_sources": len(errors),
                "total_products": total_products,
                "estimated_monthly_revenue": round(total_revenue, 2),
                "sources": sorted(results, key=lambda r: r.get("name", "")),
                "active_list": [r["name"] for r in active],
                "pending_list": [r["name"] for r in pending],
            },
            trace=trace,
        )

    def _status_report(self, started_at: str) -> AgentResult:
        """Relatório de estado de todas as fontes."""
        configured = []
        missing = []
        for branch in REVENUE_BRANCHES:
            env_var = branch.get("env_var", "")
            if env_var and os.getenv(env_var):
                configured.append(branch["name"])
            elif not env_var:
                configured.append(branch["name"])  # sempre ativa
            else:
                missing.append({"name": branch["name"], "env_var": env_var})

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "status": "scan_complete",
                "configured_sources": configured,
                "missing_configs": missing,
                "total_configured": len(configured),
                "total_missing": len(missing),
                "total_sources": len(REVENUE_BRANCHES),
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="status_report",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )

    def _scan_env(self, started_at: str) -> AgentResult:
        """Escaneia .env em busca de chaves de afiliado configuradas."""
        found = []
        missing = []
        for branch in REVENUE_BRANCHES:
            env_var = branch.get("env_var", "")
            if env_var:
                val = os.getenv(env_var, "")
                if val:
                    found.append(
                        {
                            "source": branch["name"],
                            "env_var": env_var,
                            "status": "✅ configurado",
                        }
                    )
                else:
                    missing.append(
                        {
                            "source": branch["name"],
                            "env_var": env_var,
                            "status": "❌ vazio",
                        }
                    )
            else:
                found.append(
                    {
                        "source": branch["name"],
                        "env_var": "N/A",
                        "status": "✅ sempre ativo",
                    }
                )

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "status": "scan_complete",
                "found": found,
                "missing": missing,
                "total_found": len(found),
                "total_missing": len(missing),
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="scan_env",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )
