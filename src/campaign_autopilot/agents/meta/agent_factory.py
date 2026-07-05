"""AgentFactory — 3ª Ordem: Cria novos agentes automaticamente baseado em necessidades detectadas.

O sistema que se auto-expande:
- Detecta gaps no ecossistema de agentes
- Gera código de novos agentes
- Registra no __init__.py
- Cria skills docs
- Adiciona ao workflow apropriado
"""

from __future__ import annotations

from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("agent_factory")


AGENT_TEMPLATES = {
    "content": {
        "category": "news",
        "description": "Agente de conteúdo SEO",
        "template": """\"\"\"{name}Agent — Gerado automaticamente pelo AgentFactory.

Detectado em: {detected_at}
Necessidade: {need}
\"\"\"

from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("{name}")


class {name}Agent(AgentBase):
    \"\"\"Agente auto-gerado para: {need}\"\"\"

    def __init__(self, **kwargs) -> None:
        super().__init__("{name}", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        # Auto-generated agent: synthesize from context
        need = "{need}"
        niche = context.campaign.get("niche", "general")
        goal = context.campaign.get("goal", need)
        output = {{
            "status": "auto_generated",
            "need": need,
            "niche": niche,
            "goal": goal,
            "action": f"Resolve {need} for {niche}",
        }}
        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name, step_id="{name}", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=["Agente gerado automaticamente pelo AgentFactory"],
            metadata=output,
        )
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)
""",
    },
    "money": {
        "category": "money",
        "description": "Agente de receita",
        "template": """\"\"\"{name}Agent — Gerado pelo AgentFactory para nova fonte de renda.\"\"\"
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger
log = StructuredLogger("{name}")

class {name}Agent(AgentBase):
    \"\"\"{description}\"\"\"
    def __init__(self, **kwargs) -> None:
        super().__init__("{name}", **kwargs)
    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        output = {{"status": "auto_generated", "source": "{name}"}}
        finished_at = self._utcnow_iso()
        trace = AgentTrace(agent=self.name, step_id="{name}", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main", notes=["Auto-gerado"], metadata=output)
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)
""",
    },
    "meta": {
        "category": "meta",
        "description": "Agente de meta-cognição",
        "template": """\"\"\"{name}Agent — Auto-gerado para nova capacidade meta-cognitiva.\"\"\"
from __future__ import annotations
from typing import Any
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger
log = StructuredLogger("{name}")

class {name}Agent(AgentBase):
    \"\"\"{description}\"\"\"
    def __init__(self, **kwargs) -> None:
        super().__init__("{name}", **kwargs)
    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()
        output = {{"status": "auto_generated", "capability": "{name}"}}
        finished_at = self._utcnow_iso()
        trace = AgentTrace(agent=self.name, step_id="{name}", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main", notes=["Auto-gerado"], metadata=output)
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)
""",
    },
}


class AgentFactory(AgentBase):
    """Cria novos agentes automaticamente — 3ª Ordem."""

    def __init__(self, **kwargs) -> None:
        super().__init__("agent_factory", **kwargs)

    def detect_agent_needs(self, context: CampaignContext) -> list[dict[str, Any]]:
        """Detecta necessidade de criar novos agentes."""
        sr = context.step_results if hasattr(context, "step_results") else {}
        campaign = context.campaign if hasattr(context, "campaign") else {}
        needs = []

        # 1. New affiliate programs detected but no specialized agent
        opp_out = self._get_step_output(sr, "opportunity_scan", {})
        if isinstance(opp_out, dict):
            new_programs = opp_out.get("scan", {}).get("new_affiliate_programs", [])
            for prog in new_programs[:2]:
                needs.append(
                    {
                        "type": "money",
                        "name": f"affiliate_{prog.lower().replace(' ', '_')}",
                        "need": f"Agente especializado para programa de afiliados {prog}",
                        "description": f"Gerencia links, promoções e tracking do {prog}",
                        "priority": 0.7,
                    }
                )

        # 2. New niches detected but no content agent
        niche = str(campaign.get("niche", ""))
        if niche and niche not in ["tecnologia", "financas", "saude", "carreira"]:
            needs.append(
                {
                    "type": "content",
                    "name": f"{niche}_specialist",
                    "need": f"Especialista de conteúdo para o nicho {niche}",
                    "description": f"Cria conteúdo SEO-otimizado para {niche}",
                    "priority": 0.8,
                }
            )

        # 3. Missing meta-capabilities
        meta_agents = self._get_step_output(sr, "recursive_observer", {})
        if isinstance(meta_agents, dict):
            gaps = meta_agents.get("gaps_detected", [])
            for gap in gaps[:2]:
                needs.append(
                    {
                        "type": "meta",
                        "name": f"{gap.get('capability', 'new_capability')}_agent",
                        "need": gap.get(
                            "description", "Nova capacidade meta-cognitiva"
                        ),
                        "description": gap.get(
                            "description", "Agente para nova capacidade"
                        ),
                        "priority": gap.get("priority", 0.5),
                    }
                )

        needs.sort(key=lambda x: -x["priority"])
        return needs

    def generate_agent_code(self, need: dict) -> str:
        """Gera código do agente baseado no template."""
        template_info = AGENT_TEMPLATES.get(need["type"], AGENT_TEMPLATES["content"])
        name = need["name"]
        name_camel = "".join(word.capitalize() for word in name.split("_"))
        return template_info["template"].format(
            name=name,
            nameAgent=name_camel,
            need=need["need"],
            description=need.get("description", ""),
            detected_at=self._utcnow_iso(),
        )

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = self._utcnow_iso()

        needs = self.detect_agent_needs(context)
        generated = []
        for need in needs:
            code = self.generate_agent_code(need)
            generated.append(
                {
                    "name": need["name"],
                    "type": need["type"],
                    "need": need["need"],
                    "code": code[:200] + "...",
                    "code_length": len(code),
                    "priority": need["priority"],
                }
            )

        output = {
            "needs_detected": len(needs),
            "agents_to_create": generated,
            "pending_actions": generated,
            "status": "detection_complete",
            "self_evolution_note": (
                "AgentFactory detecta necessidades. "
                "Para auto-criação completa (escrever arquivo + registrar __init__), "
                "é necessária permissão explícita."
            ),
        }

        if generated:
            output["next_steps"] = [
                f"Criar {generated[0]['name']}Agent — {generated[0]['need']}",
                "Registrar no __init__.py apropriado",
                "Criar skill doc para o novo agente",
            ]

        finished_at = self._utcnow_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="agent_factory",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=self._duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Detectou {len(needs)} necessidades de novos agentes"],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    @staticmethod
    def _utcnow_iso() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _duration_ms(start: str, end: str) -> int:
        from datetime import datetime

        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return max(0, int((e - s).total_seconds() * 1000))

    @staticmethod
    def _get_step_output(step_results: dict, step_id: str, default: Any = None) -> Any:
        step = step_results.get(step_id, {})
        if isinstance(step, dict):
            return step.get("output", step)
        return default
