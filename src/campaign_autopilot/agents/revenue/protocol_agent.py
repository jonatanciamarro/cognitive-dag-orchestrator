"""RevenueProtocolAgent — Agente de protocolo E2E para cada fonte de renda.

Define passo a passo detalhado para configurar cada uma das 13 fontes
de renda, com checklists, links, comandos e validação.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from .memory import RevenueMemory, REVENUE_SOURCES
from ...logging_utils import StructuredLogger

log = StructuredLogger("revenue_protocol")

# ── Protocolos E2E detalhados para cada fonte ────────────────
SOURCE_PROTOCOLS: dict[str, dict[str, Any]] = {
    "hotmart": {
        "name": "Hotmart",
        "type": "affiliate",
        "icon": "🔥",
        "signup_url": "https://hotmart.com",
        "setup_steps": [
            "1. Acesse https://hotmart.com e crie conta como afiliado (gratuito)",
            "2. Vá em 'Catálogo de Produtos'",
            "3. Filtre por nichos: tecnologia, finanças, saúde, carreira",
            "4. Escolha produtos com boa comissão (30-70%)",
            "5. Clique 'Pegar link' em cada produto",
            "6. Copie o link COMPLETO (ex: https://hotm.art/produto?aff=SEUCODIGO)",
        ],
        "integration_commands": [
            "python scripts/hotmart_wizard.py",
            "Ou edite manualmente configs/affiliate_offers.json",
        ],
        "activation_note": "AffiliateLinkInserterAgent insere links automaticamente",
        "cookie_days": 30,
        "commission_range": "30-70%",
    },
    "amazon": {
        "name": "Amazon Associates",
        "type": "affiliate",
        "icon": "📦",
        "signup_url": "https://associados.amazon.com.br",
        "setup_steps": [
            "1. Acesse https://associados.amazon.com.br",
            "2. Crie conta (gratuito, precisa de site/blog)",
            "3. Obtenha seu Tracking ID (ex: seunome-20)",
            "4. Adicione AMAZON_TRACKING_ID ao .env",
        ],
        "integration_commands": [
            "Edite .env: AMAZON_TRACKING_ID=seunome-20",
            "Adicione produtos em configs/affiliate_offers.json com network=amazon",
        ],
        "activation_note": "Links Amazon são inseridos automaticamente nos artigos",
        "cookie_days": 1,
        "commission_range": "1-10%",
    },
    "monetizze": {
        "name": "Monetizze",
        "type": "affiliate",
        "icon": "💰",
        "signup_url": "https://monetizze.com.br/cadastro-afiliado",
        "setup_steps": [
            "1. Acesse https://monetizze.com.br",
            "2. Crie conta como afiliado",
            "3. Navegue no catálogo de produtos",
            "4. Escolha produtos nos nichos do sistema",
            "5. Copie o link com parametro de afiliado (?afiliado=SEUCODIGO)",
        ],
        "integration_commands": [
            "GenericAffiliateNetworkAgent(network='monetizze').run(ctx)",
            "Ou edite configs/affiliate_offers.json manualmente",
        ],
        "activation_note": "Links inseridos automaticamente pelo sistema",
        "cookie_days": 30,
        "commission_range": "20-80%",
    },
    "kiwify": {
        "name": "Kiwify",
        "type": "affiliate",
        "icon": "💜",
        "signup_url": "https://kiwify.com.br/afiliados",
        "setup_steps": [
            "1. Acesse https://kiwify.com.br",
            "2. Crie conta como afiliado",
            "3. Navegue no catálogo de produtos",
            "4. Escolha produtos nos nichos do sistema",
            "5. Copie o link com parametro de afiliado",
        ],
        "integration_commands": [
            "GenericAffiliateNetworkAgent(network='kiwify').run(ctx)",
        ],
        "activation_note": "Links inseridos automaticamente pelo sistema",
        "cookie_days": 30,
        "commission_range": "20-80%",
    },
    "eduzz": {
        "name": "Eduzz",
        "type": "affiliate",
        "icon": "🎓",
        "signup_url": "https://eduzz.com/afiliados",
        "setup_steps": [
            "1. Acesse https://eduzz.com",
            "2. Crie conta como afiliado",
            "3. Navegue no catálogo de produtos",
            "4. Escolha produtos nos nichos do sistema",
            "5. Copie o link com parametro de afiliado",
        ],
        "integration_commands": [
            "GenericAffiliateNetworkAgent(network='eduzz').run(ctx)",
        ],
        "activation_note": "Links inseridos automaticamente pelo sistema",
        "cookie_days": 30,
        "commission_range": "20-70%",
    },
    "adsense": {
        "name": "Google AdSense",
        "type": "ads",
        "icon": "📢",
        "signup_url": "https://adsense.google.com",
        "setup_steps": [
            "1. Acesse https://adsense.google.com",
            "2. Crie conta com seu site (precisa de conteudo original)",
            "3. Aguarde aprovacao (1-2 dias uteis)",
            "4. Crie unidades de anuncio (display, in-feed, in-article)",
            "5. Copie o codigo do AdSense ou configure auto-ads",
        ],
        "integration_commands": [
            "AdSenseAgent().run(ctx) com action='configure'",
            "O sistema insere anuncios automaticamente no site",
        ],
        "activation_note": "Anuncios sao inseridos automaticamente no site gerado",
        "cookie_days": "N/A",
        "commission_range": "CPM (R$1-15 por 1000 impressoes)",
    },
    "cpa": {
        "name": "CPA Networks (Lomadee, Awin, etc)",
        "type": "cpa",
        "icon": "📊",
        "signup_url": "https://www.lomadee.com",
        "setup_steps": [
            "1. Escolha redes CPA: Lomadee, Awin, PagBank, Rakuten",
            "2. Crie conta como publisher/afiliado em cada rede",
            "3. Navegue no catalogo de ofertas",
            "4. Filtre por nicho (tecnologia, financas, saude, carreira)",
            "5. Escolha ofertas com boa CPA (custo por acao)",
            "6. Copie o link de cada oferta",
        ],
        "integration_commands": [
            "CPAAgent().run(ctx) com action='discover'",
            "Adicione ofertas em configs/affiliate_offers.json com network='cpa'",
        ],
        "activation_note": "Ofertas CPA sao inseridas em artigos relevantes",
        "cookie_days": "7-90 (varia por rede)",
        "commission_range": "R$5-200 por lead/venda",
    },
    "digital_product": {
        "name": "Produtos Digitais Proprios",
        "type": "product",
        "icon": "💡",
        "signup_url": "N/A (crie voce mesmo)",
        "setup_steps": [
            "1. Escolha um nicho com demanda",
            "2. Crie produto digital: e-book, template, checklist, mini-curso",
            "3. Hospede em plataforma (Hotmart, Monetizze, ou site proprio)",
            "4. Defina preco e comissao para afiliados (se quiser)",
        ],
        "integration_commands": [
            "DigitalProductAgent().run(ctx)",
            "Ou configure manualmente no sistema",
        ],
        "activation_note": "Produtos sao promovidos nos artigos do nicho",
        "cookie_days": "30-365",
        "commission_range": "50-100% (voce define)",
    },
    "membership": {
        "name": "Membership / Assinaturas",
        "type": "membership",
        "icon": "🔑",
        "signup_url": "N/A",
        "setup_steps": [
            "1. Defina modelo de assinatura (conteudo exclusivo, newsletter paga)",
            "2. Crie niveis de acesso (basico, premium, vip)",
            "3. Configure sistema de pagamento recorrente",
            "4. Crie conteudo exclusivo para membros",
        ],
        "integration_commands": [
            "MembershipAgent().run(ctx)",
        ],
        "activation_note": "Assinaturas geram receita recorrente mensal",
        "cookie_days": "N/A",
        "commission_range": "R$10-100/mes por membro",
    },
    "email_marketing": {
        "name": "Email Marketing",
        "type": "email",
        "icon": "📧",
        "signup_url": "N/A (use sua lista)",
        "setup_steps": [
            "1. Capture leads com iscas digitais no site",
            "2. Crie sequencia de boas-vindas (3-5 emails)",
            "3. Crie sequencia de nutricao (conteudo + ofertas)",
            "4. Configure automacoes de disparo",
        ],
        "integration_commands": [
            "EmailMarketingAgent().run(ctx)",
        ],
        "activation_note": "Emails sao disparados automaticamente",
        "cookie_days": "N/A",
        "commission_range": "Indireto (aumenta conversao em 2-5x)",
    },
    "lead_capture": {
        "name": "Captura de Leads",
        "type": "lead",
        "icon": "🎯",
        "signup_url": "N/A",
        "setup_steps": [
            "1. Crie iscas digitais (e-book gratis, checklist, planilha, curso mini)",
            "2. Configure formularios de captura no site",
            "3. Conecte ao sistema de email marketing",
            "4. Crie pagina de obrigado com upsell",
        ],
        "integration_commands": [
            "LeadCaptureAgent().run(ctx)",
        ],
        "activation_note": "Leads sao capturados automaticamente nos artigos",
        "cookie_days": "N/A",
        "commission_range": "Valor do lead: R$1-20 (para vendas futuras)",
    },
    "traffic_recycling": {
        "name": "Reciclagem de Trafego",
        "type": "recycle",
        "icon": "♻️",
        "signup_url": "N/A (tecnica de otimizacao)",
        "setup_steps": [
            "1. Configure pixels de retargeting nas paginas",
            "2. Crie audiencias de visitantes (30d, 7d, 1d)",
            "3. O sistema automaticamente recicla trafego",
            "4. Visitantes que nao converteram recebem novos conteudos",
        ],
        "integration_commands": [
            "TrafficRecyclerAgent().run(ctx)",
        ],
        "activation_note": "Reciclagem acontece automaticamente sem custo adicional",
        "cookie_days": "N/A",
        "commission_range": "Aumenta conversao em 15-30%",
    },
    "paid_traffic": {
        "name": "Trafego Pago (Reinvestimento)",
        "type": "paid",
        "icon": "🚀",
        "signup_url": "https://ads.google.com, https://business.facebook.com",
        "setup_steps": [
            "1. Configure contas de anuncio (Google Ads, Meta Ads)",
            "2. Defina budget inicial (vem da receita organica)",
            "3. Crie campanhas baseadas nos artigos de maior performance",
            "4. O sistema gerencia bids e otimizacao",
        ],
        "integration_commands": [
            "PaidTrafficOrchestratorAgent().run(ctx)",
            "O budget e reinvestido automaticamente da receita organica",
        ],
        "activation_note": "Ativado automaticamente quando ha receita organica suficiente",
        "cookie_days": "N/A",
        "commission_range": "ROAS 2-5x (retorno sobre investimento)",
    },
}


class RevenueProtocolAgent(AgentBase):
    """Agente de protocolo E2E — mostra passo a passo para cada fonte de renda."""

    def __init__(self, **kwargs):
        super().__init__("revenue_protocol", **kwargs)
        self.memory = RevenueMemory()
        self.protocols = SOURCE_PROTOCOLS

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "list")
            source = campaign.get("source", "")

            if action == "list":
                return self._list_all(started_at)
            elif action == "show" and source:
                return self._show_protocol(source, started_at)
            elif action == "checklist" and source:
                return self._checklist(source, started_at)
            elif action == "status":
                return self._status(started_at)
            elif action == "verify" and source:
                return self._verify(source, started_at)
            else:
                return self._list_all(started_at)

        except Exception as e:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="protocol",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _list_all(self, started_at: str) -> AgentResult:
        summary = []
        sources_status = self.memory.get_status()
        status_map = {s["source"]: s["status"] for s in sources_status}

        for source_key in REVENUE_SOURCES:
            proto = self.protocols.get(source_key, {})
            summary.append(
                {
                    "source": source_key,
                    "name": proto.get("name", source_key),
                    "icon": proto.get("icon", ""),
                    "type": proto.get("type", ""),
                    "status": status_map.get(source_key, "pending"),
                    "setup_steps_count": len(proto.get("setup_steps", [])),
                }
            )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="list",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(summary)} protocols loaded"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={"total": len(summary), "sources": summary},
            trace=trace,
        )

    def _show_protocol(self, source: str, started_at: str) -> AgentResult:
        proto = self.protocols.get(source)
        if not proto:
            finished_at = datetime.now(timezone.utc).isoformat()
            return AgentResult(
                agent=self.name,
                status="error",
                output={
                    "error": f"Fonte '{source}' nao encontrada. Disponiveis: {', '.join(REVENUE_SOURCES)}"
                },
                trace=AgentTrace(
                    agent=self.name,
                    step_id="show",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        sources_status = self.memory.get_status()
        current_status = next(
            (s["status"] for s in sources_status if s["source"] == source), "pending"
        )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="show_protocol",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"source: {source}", f"status: {current_status}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "source": source,
                "protocol": proto,
                "current_status": current_status,
                "setup_complete": current_status == "active",
            },
            trace=trace,
        )

    def _checklist(self, source: str, started_at: str) -> AgentResult:
        """Retorna checklist verificavel de setup para uma fonte."""
        proto = self.protocols.get(source)
        if not proto:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": f"Fonte '{source}' nao encontrada"},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="checklist",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        checklist = []
        for step in proto.get("setup_steps", []):
            # Extract action from step
            checklist.append(
                {
                    "step": step,
                    "done": False,  # User marks manually
                    "required": True,
                }
            )
        for cmd in proto.get("integration_commands", []):
            checklist.append(
                {
                    "step": f"Execute: {cmd}",
                    "done": False,
                    "required": True,
                }
            )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="checklist",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(checklist)} steps for {source}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "source": source,
                "total_steps": len(checklist),
                "checklist": checklist,
            },
            trace=trace,
        )

    def _status(self, started_at: str) -> AgentResult:
        sources_status = self.memory.get_status()
        completed = sum(1 for s in sources_status if s["status"] == "active")
        total = len(sources_status)

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="status",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{completed}/{total} sources configured"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "completed": completed,
                "total": total,
                "progress_pct": round(completed / total * 100) if total > 0 else 0,
                "sources": sources_status,
            },
            trace=trace,
        )

    def _verify(self, source: str, started_at: str) -> AgentResult:
        """Verifica se uma fonte esta configurada corretamente."""
        from pathlib import Path
        import json

        issues = []
        config_path = Path("configs/affiliate_offers.json")

        if source == "hotmart":
            if config_path.exists():
                data = json.loads(config_path.read_text())
                offers = []
                for niche, products in data.get("offers_by_niche", {}).items():
                    offers.extend(p for p in products if p.get("network") == "hotmart")
                if not offers:
                    issues.append("Nenhum link Hotmart encontrado no config")
                else:
                    for o in offers:
                        if "hotm.art" not in o.get("product_url", ""):
                            issues.append(f"Link invalido: {o.get('product_name')}")
            else:
                issues.append("configs/affiliate_offers.json nao encontrado")

        elif source == "amazon":
            import os

            tid = os.environ.get("AMAZON_TRACKING_ID", "")
            if not tid or tid == "":
                issues.append("AMAZON_TRACKING_ID nao configurado no .env")
            if config_path.exists():
                data = json.loads(config_path.read_text())
                offers = []
                for niche, products in data.get("offers_by_niche", {}).items():
                    offers.extend(p for p in products if p.get("network") == "amazon")
                if not offers:
                    issues.append("Nenhum link Amazon encontrado no config")

        elif source in ("monetizze", "kiwify", "eduzz"):
            if config_path.exists():
                data = json.loads(config_path.read_text())
                offers = []
                for niche, products in data.get("offers_by_niche", {}).items():
                    offers.extend(p for p in products if p.get("network") == source)
                if not offers:
                    issues.append(f"Nenhum link {source} encontrado no config")

        elif source == "adsense":
            # Check if site generator has adsense config
            site_config = Path("site_generator/config.py")
            if site_config.exists():
                config_content = site_config.read_text()
                if (
                    "adsense" not in config_content.lower()
                    and "ad_client" not in config_content.lower()
                ):
                    issues.append("AdSense nao configurado no gerador de site")
            else:
                issues.append("site_generator/config.py nao encontrado")

        status = "verified" if not issues else "issues_found"
        self.memory.update_source(source, status=status)

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="verify",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"{len(issues)} issues for {source}"],
        )
        return AgentResult(
            agent=self.name,
            status=status,
            output={
                "source": source,
                "verified": len(issues) == 0,
                "issues": issues,
                "recommendation": "Tudo ok!"
                if not issues
                else f"Resolva {len(issues)} pendencia(s)",
            },
            trace=trace,
        )
