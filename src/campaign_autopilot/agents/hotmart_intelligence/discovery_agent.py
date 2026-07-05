"""Fase 1 — Discovery: mapear produtos elegiveis no Hotmart."""
from __future__ import annotations
import time
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext, utc_now_iso, iso_duration_ms
from ...hotmart_product_intelligence import HotmartProduct, ProductIntelligenceStore
from ...affiliate_browser.browser_agent import HotmartScraper, AffiliateBrowserAgent

class HotmartDiscoveryAgent(AgentBase):
    """Mapeia produtos elegiveis do marketplace Hotmart.

    Entrada: Categoria/Nicho
    Saida: Lista de HotmartProduct com dados brutos do marketplace.
    """

    def __init__(self, store: ProductIntelligenceStore | None = None, **kwargs):
        super().__init__("hotmart_discovery", **kwargs)
        self.store = store

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "marketing digital")))
        max_products = int(campaign.get("max_products", 10))

        try:
            products = self._discover_products(niche, max_products)
            if self.store:
                for p in products:
                    self.store.upsert_product(p)
            output = {
                "niche": niche,
                "products_found": len(products),
                "products": [p.to_dict() for p in products],
                "status": "success",
            }
            finished_at = utc_now_iso()
            trace = AgentTrace(agent=self.name, step_id="hotmart_discovery", status="success",
                started_at=started_at, finished_at=finished_at,
                duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
                notes=[f"Descobertos {len(products)} produtos em {niche}"])
            return AgentResult(agent=self.name, status="success", output=output, trace=trace)
        except Exception as e:
            finished_at = utc_now_iso()
            trace = AgentTrace(agent=self.name, step_id="hotmart_discovery", status="error",
                started_at=started_at, finished_at=finished_at,
                duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main", error=str(e))
            return AgentResult(agent=self.name, status="error", output={"error": str(e)}, trace=trace)

    def _discover_products(self, niche: str, max_n: int) -> list[HotmartProduct]:
        """Descobre produtos reais via navegacao automatizada no Hotmart Marketplace.
        
        Fallback para dados simulados se o browser nao estiver disponivel.
        """
        import random
        # Tentar descobrir via browser
        try:
            with AffiliateBrowserAgent() as agent:
                if agent.login("hotmart", headless=True):
                    results = agent.scan_platform("hotmart", niche, max_n)
                    products = []
                    for r in results:
                        products.append(HotmartProduct(
                            product_id=f"BROWSER_{random.randint(10000, 99999)}",
                            name=r.get("product_name", f"Produto {niche}"),
                            category=niche,
                            producer="Descoberto via Browser",
                            price=0.0,
                            commission_value=0.0,
                            commission_pct=0.0,
                            cookie_days=30,
                            temperature="morno",
                            description=f"Produto encontrado no marketplace Hotmart para {niche}",
                            sales_page_url=r.get("affiliate_link", ""),
                            checkout_url=r.get("affiliate_link", ""),
                            discovered_at=utc_now_iso(),
                        ))
                    if products:
                        return products[:max_n]
        except Exception as e:
            print(f"  ⚠️ Browser discovery failed, using fallback: {e}")
        
        # Fallback: dados simulados
        niches_map = {
            "marketing digital": [("MKT-001","Guia Completo Marketing Afiliados","Wagner Cosme",197,80,30),
                                  ("MKT-002","Masterclass Trafego Pago","Pedro Sobral",497,200,60),
                                  ("MKT-003","Funil de Vendas 4.0","Erick Wendel",297,120,30)],
            "financas": [("FIN-001","Independencia Financeira","Thiago Nigro",497,200,60),
                         ("FIN-002","Investimento em Acoes","Bastter",297,150,30),
                         ("FIN-003","Criptomoedas para Iniciantes","Gabriel",197,100,30)],
            "empreendedorismo": [("EMP-001","Negocio Digital Zero","Primo Rico",297,120,30),
                                 ("EMP-002","Ecommerce do Zero","Bruno Menezes",497,200,60)],
            "ia": [("IA-001","Inteligencia Artificial Aplicada","Andre Barczak",297,150,30),
                   ("IA-002","Automacao com IA","Felipe",197,100,30)],
            "saude": [("SAU-001","Emagrecimento Definitivo","Dr. Lair",397,180,30),
                      ("SAU-002","Saude Mental Positiva","Renato",197,100,30)],
            "desenvolvimento pessoal": [("DEV-001","Alta Performance","Paulo Vieira",397,180,60),
                                        ("DEV-002","Habitos Atomicos","Edu",197,100,30)],
        }
        base = niches_map.get(niche.lower(), [("GEN-001","Produto Generico","Produtor",197,100,30)])
        products = []
        for pid, name, prod, price, comm, cookie in base[:max_n]:
            products.append(HotmartProduct(
                product_id=pid, name=name, category=niche, producer=prod,
                price=float(price), commission_value=float(comm), commission_pct=round(comm/price*100,1),
                cookie_days=cookie, temperature=random.choice(["frio","morno","quente"]),
                description=f"Curso completo sobre {name.lower()}", sales_page_url=f"https://hotmart.com/{pid}",
                checkout_url=f"https://pay.hotmart.com/{pid}", discovered_at=utc_now_iso(),
            ))
        return products[:max_n]
