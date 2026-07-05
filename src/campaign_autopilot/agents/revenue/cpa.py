"""CPAAgent — Redes de CPA (Cost Per Action): lead generation, formularios, tracking."""

from __future__ import annotations

from datetime import datetime, timezone

from ..base import AgentResult, AgentTrace, CampaignContext
from .base import RevenueBaseAgent, RevenueProtocol
from .memory import RevenueMemory
from ...logging_utils import StructuredLogger

log = StructuredLogger("cpa")


CPA_NETWORKS = {
    "lomadee": {
        "name": "Lomadee (Buscape)",
        "url": "https://www.lomadee.com",
        "type": "cpa",
    },
    "afiliados": {
        "name": "Afiliados.com.br",
        "url": "https://afiliados.com.br",
        "type": "cpa",
    },
    "socialminer": {
        "name": "SocialMiner",
        "url": "https://socialminer.com.br",
        "type": "cpa",
    },
    "leadster": {"name": "Leadster", "url": "https://leadster.com.br", "type": "cpa"},
}


class CPAAgent(RevenueBaseAgent):
    """Gerencia campanhas de CPA (Custo Por Acao).

    Protocolo E2E:
    1. SETUP: Criar conta em rede CPA, escolher ofertas
    2. INTEGRATE: Configurar formularios de lead, pixel de tracking
    3. ACTIVATE: Gerar leads com conteudo + imas digitais
    4. MONITOR: Tracking de leads, custo por lead, conversao
    5. OPTIMIZE: Melhorar taxa de conversao dos formularios
    """

    def __init__(self, **kwargs):
        protocol = RevenueProtocol(name="CPA Networks", source_type="cpa")
        super().__init__("cpa", protocol, **kwargs)
        self.memory = RevenueMemory()

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "protocol")

            if action == "protocol":
                return self._show_protocol(started_at)
            elif action == "generate_lead_form":
                return self._generate_lead_form(campaign, started_at)
            elif action == "generate_lead_magnet":
                return self._generate_lead_magnet(campaign, started_at)
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
                    step_id="cpa",
                    status="error",
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _show_protocol(self, started_at: str) -> AgentResult:
        finished_at = datetime.now(timezone.utc).isoformat()
        networks_info = [f"{v['name']} ({v['url']})" for v in CPA_NETWORKS.values()]

        trace = AgentTrace(
            agent=self.name,
            step_id="protocol",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"networks: {len(CPA_NETWORKS)}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "protocol": self.protocol.get_protocol_steps(),
                "cpa_networks": networks_info,
                "steps": [
                    "1. Escolha uma rede CPA (Lomadee, Afiliados.com.br, SocialMiner, Leadster)",
                    "2. Crie conta e escolha ofertas por CPA (custo por lead/acao)",
                    "3. Crie um ima digital (ebook, checklist, planilha) para capturar leads",
                    "4. Crie pagina de captura com formulario",
                    "5. Adicione pixel de tracking da rede CPA",
                    "6. Direcione trafego do blog para a pagina de captura",
                    "7. A cada lead, a rede CPA paga um valor fixo",
                ],
                "lead_magnet_ideas": [
                    "Ebook gratuito sobre o nicho",
                    "Checklist passo a passo",
                    "Planilha editavel",
                    "Video aula exclusiva",
                    "Mini-curso por email",
                ],
            },
            trace=trace,
        )

    def _generate_lead_form(self, campaign: dict, started_at: str) -> AgentResult:
        niche = campaign.get("niche", "tecnologia")
        lead_magnet = campaign.get("lead_magnet", "Ebook Gratuito")

        form_html = f"""<!-- Formulario de Captura CPA - {niche} -->
<div class="lead-form" style="max-width:500px;margin:40px auto;padding:30px;
     background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;color:white;">
  <h3 style="margin:0 0 10px;">🎯 Baixe seu {lead_magnet}</h3>
  <p style="opacity:0.9;margin:0 0 20px;">Gratuito! Preencha e receba no seu email.</p>
  <form action="/api/capture" method="POST" style="display:flex;flex-direction:column;gap:12px;">
    <input type="text" name="name" placeholder="Seu nome" required
           style="padding:12px;border:none;border-radius:8px;font-size:15px;">
    <input type="email" name="email" placeholder="Seu melhor email" required
           style="padding:12px;border:none;border-radius:8px;font-size:15px;">
    <button type="submit" style="background:#48bb78;color:white;border:none;
            padding:14px;border-radius:8px;font-weight:bold;font-size:16px;cursor:pointer;">
      📥 QUERO RECEBER
    </button>
  </form>
  <p style="font-size:0.8rem;opacity:0.7;margin-top:15px;">Sem spam. Descadastro facil.</p>
</div>"""

        self.memory.update_source(
            "cpa", status="form_generated", config={"niche": niche}
        )

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="lead_form",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"form generated for {niche}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "form_html": form_html,
                "niche": niche,
                "lead_magnet": lead_magnet,
                "note": "Cole este HTML no final dos artigos do nicho",
            },
            trace=trace,
        )

    def _generate_lead_magnet(self, campaign: dict, started_at: str) -> AgentResult:
        niche = campaign.get("niche", "tecnologia")

        magnets = {
            "tecnologia": "Guia Completo de Ferramentas de IA Gratuitas",
            "financas": "Planilha de Controle Financeiro Mensal",
            "saude": "Checklist de Habitos Saudaveis para Iniciantes",
            "carreira": "Template de Curriculo Aprovado pelos RHs",
        }
        magnet = magnets.get(niche, f"Guia Completo de {niche}")

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="lead_magnet",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=0,
            thread_name="main",
            notes=[f"magnet: {magnet}"],
        )
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "lead_magnet": magnet,
                "niche": niche,
                "description": f"Ofereca '{magnet}' como isca digital nas paginas de {niche}",
            },
            trace=trace,
        )
