"""AdSenseAgent — Google AdSense: configuracao de site, ads.txt, otimizacao de anúncios."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..base import AgentResult, AgentTrace, CampaignContext
from .base import RevenueBaseAgent, RevenueProtocol
from .memory import RevenueMemory
from ...logging_utils import StructuredLogger

log = StructuredLogger("adsense")


class AdSenseAgent(RevenueBaseAgent):
    """Gerencia integracao com Google AdSense.

    Protocolo E2E:
    1. SETUP: Criar site, configurar ads.txt, submeter ao AdSense
    2. INTEGRATE: Adicionar codigo AdSense ao site
    3. ACTIVATE: Anuncios comecam a aparecer apos aprovacao
    4. MONITOR: Acompanhar RPM, impressoes, receita
    5. OPTIMIZE: Testar posicoes de anuncio, formatos
    """

    def __init__(self, **kwargs):
        protocol = RevenueProtocol(name="Google AdSense", source_type="ads")
        super().__init__("adsense", protocol, **kwargs)
        self.memory = RevenueMemory()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "protocol")

            if action == "protocol":
                return self._show_protocol(started_at)
            elif action == "generate_ads_txt":
                return self._generate_ads_txt(campaign, started_at)
            elif action == "verify_site":
                return self._verify_site(campaign, started_at)
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
                    step_id="adsense",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _show_protocol(self, started_at: str) -> AgentResult:
        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="protocol",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=["protocol: 5 steps"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "protocol": self.protocol.get_protocol_steps(),
                "steps": [
                    "1. Crie um site/blog (WordPress ou site estatico)",
                    "2. Acesse https://adsense.google.com e crie conta",
                    "3. Submeta seu site para aprovacao",
                    "4. Apos aprovado, copie o codigo do anuncio",
                    "5. Adicione o codigo ao site (no template HTML)",
                    "6. Gere o arquivo ads.txt e publique na raiz do site",
                    "7. Os anuncios comecam a aparecer em 24-48h",
                ],
                "requirements": [
                    "Site com conteudo original (minimo 20 artigos)",
                    "Dominio proprio (nao blog gratuito)",
                    "Politicas de privacidade e disclosure",
                    "Maioria do trafego do Brasil",
                ],
            },
            trace=trace,
        )

    def _generate_ads_txt(self, campaign: dict, started_at: str) -> AgentResult:
        publisher_id = campaign.get("publisher_id", "")
        if not publisher_id:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": "publisher_id obrigatorio (ex: pub-123456789)"},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="ads_txt",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

        ads_txt_content = f"""google.com, {publisher_id}, DIRECT, f08c47fec0942fa0
google.com, {publisher_id}, RESELLER, f08c47fec0942fa0
"""
        ads_txt_path = Path("site/ads.txt")
        ads_txt_path.parent.mkdir(parents=True, exist_ok=True)
        ads_txt_path.write_text(ads_txt_content)

        self.memory.update_source(
            "adsense", status="ads_txt_generated", config={"publisher_id": publisher_id}
        )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="ads_txt",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"ads.txt generated: {ads_txt_path}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "ads_txt_path": str(ads_txt_path),
                "content": ads_txt_content,
                "note": "Copie este arquivo para a raiz do seu site",
            },
            trace=trace,
        )

    def _verify_site(self, campaign: dict, started_at: str) -> AgentResult:
        site_url = campaign.get("site_url", "")
        issues = []

        if site_url:
            # Check if ads.txt is accessible
            ads_txt_check = f"{site_url.rstrip('/')}/ads.txt"
            issues.append(f"Verifique se {ads_txt_check} esta acessivel")

        # Check if site has minimum content
        site_path = Path("site")
        if site_path.exists():
            articles = list(site_path.rglob("index.html"))
            if len(articles) < 20:
                issues.append(
                    f"Site tem apenas {len(articles)} artigos (minimo recomendado: 20)"
                )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="verify",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"issues: {len(issues)}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "site_url": site_url,
                "ready_for_adsense": len(issues) == 0,
                "issues": issues,
                "checklist": [
                    "Site com dominio proprio",
                    "Politica de privacidade visivel",
                    "Pagina 'Sobre' preenchida",
                    "20+ artigos publicados",
                    "Conteudo original (nao copiado)",
                    "ads.txt na raiz do site",
                    "Nao violar politicas do AdSense",
                ],
            },
            trace=trace,
        )
