"""Revenue Protocol Base — Define o protocolo E2E para qualquer fonte de renda."""

from __future__ import annotations

from typing import Any

from ..base import AgentBase
from ...logging_utils import StructuredLogger

log = StructuredLogger("revenue_base")


class RevenueProtocol:
    """Protocolo E2E para uma fonte de renda.

    Define as 5 fases que toda fonte de renda deve seguir:
    1. SETUP — Configurar conta, obter credenciais
    2. INTEGRATE — Conectar ao sistema (API, links, tracking)
    3. ACTIVATE — Comecar a gerar receita (inserir links, ads, etc)
    4. MONITOR — Acompanhar performance, cliques, conversoes
    5. OPTIMIZE — Melhorar resultados (A/B test, ajustes)
    """

    def __init__(self, name: str, source_type: str):
        self.name = name
        self.source_type = (
            source_type  # "affiliate", "ads", "cpa", "product", "membership"
        )

    def get_protocol_steps(self) -> list[dict[str, str]]:
        return [
            {
                "phase": "SETUP",
                "step": f"Criar conta em {self.name}",
                "effort": "30min",
            },
            {
                "phase": "SETUP",
                "step": "Obter credenciais de afiliado/API",
                "effort": "5min",
            },
            {
                "phase": "INTEGRATE",
                "step": "Adicionar credenciais ao .env",
                "effort": "2min",
            },
            {
                "phase": "INTEGRATE",
                "step": "Configurar ofertas no sistema",
                "effort": "10min",
            },
            {
                "phase": "ACTIVATE",
                "step": "Sistema comeca a gerar receita automaticamente",
                "effort": "0min",
            },
            {
                "phase": "MONITOR",
                "step": "Acompanhar receita no dashboard",
                "effort": "5min/dia",
            },
            {
                "phase": "OPTIMIZE",
                "step": "Substituir ofertas com baixa performance",
                "effort": "15min/semana",
            },
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.source_type,
            "steps": self.get_protocol_steps(),
        }


class RevenueBaseAgent(AgentBase):
    """Classe base para agentes de fonte de renda."""

    def __init__(self, name: str, protocol: RevenueProtocol, **kwargs):
        super().__init__(name, **kwargs)
        self.protocol = protocol

    def get_protocol(self) -> RevenueProtocol:
        return self.protocol

    def log_revenue_event(
        self,
        event_type: str,
        source: str,
        amount: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        log.info(
            "revenue_event",
            event_type=event_type,
            source=source,
            amount=amount,
            metadata=metadata,
        )
