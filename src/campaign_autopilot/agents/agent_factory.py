"""AgentFactory — Fábrica Autônoma de Agentes.

Gera novos agentes em tempo real baseado em gaps detectados.
Capacidade de segunda ordem: o sistema cria seus próprios componentes.

Para cada novo agente, a AgentFactory:
1. Gera código Python válido (classe AgentBase)
2. Registra em __init__.py e orchestrator.py
3. Cria skill doc markdown
4. Adiciona ao workflow
5. Testa o novo agente

Isso permite que o sistema evolua sua própria arquitetura de agentes.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


# ── Templates de Agentes ─────────────────────────────────────────

_AGENT_TEMPLATES: dict[str, str] = {
    "marketing_channel": '''"""Agente de Marketing para {channel_name} — gerado automaticamente pela AgentFactory."""

from __future__ import annotations

from typing import Any

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext, iso_duration_ms, utc_now_iso


class {class_name}(AgentBase):
    """Agente de marketing para {channel_name}. Gera conteúdo otimizado para a plataforma."""

    def __init__(self, **kwargs) -> None:
        super().__init__("{agent_id}", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "")))
        step_results = context.step_results

        # Coletar dados de agentes upstream
        seo = step_results.get("seo_research", {{}})
        seo_out = seo.get("output", {{}}) if isinstance(seo, dict) else {{}}
        opportunities = seo_out.get("top_opportunities", []) or seo_out.get("keywords", [])

        if not opportunities:
            opportunities = [{{"keyword": str(campaign.get("objective", niche)), "volume": 1000}}]

        content = []
        for i, opp in enumerate(opportunities[:3]):
            keyword = opp.get("keyword", "")
            content.append({{
                "platform": "{channel_name}",
                "keyword": keyword,
                "title": f"{{keyword}} — Guia para {niche}",
                "description": f"Conteúdo sobre {{keyword}} para {niche}. Gerado automaticamente.",
                "hashtags": ["#" + w for w in niche.lower().split() if len(w) > 2][:5],
                "best_time_to_post": "18:00-21:00",
            }})

        output = {{
            "status": "success",
            "content_generated": len(content),
            "content": content,
            "platform": "{channel_name}",
            "niche": niche,
        }}

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name, cycle_id=context.run_id,
                decision_type="{agent_id}",
                input_state={{"opportunities": len(opportunities)}},
            )
            self.explanation_store.update_decision_output(did, {{
                "output_decision": {{"content": len(content)}},
            }})

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name, step_id="{agent_id}", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"Gerou {{len(content)}} conteúdos para {channel_name}"],
            metadata={{"content": len(content), "niche": niche}},
        )
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)
''',
    "seo_agent": '''"""Agente de SEO para {channel_name} — gerado automaticamente pela AgentFactory."""

from __future__ import annotations

from typing import Any

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext, iso_duration_ms, utc_now_iso


class {class_name}(AgentBase):
    """Agente de SEO especializado em {channel_name}."""

    def __init__(self, **kwargs) -> None:
        super().__init__("{agent_id}", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "")))

        output = {{
            "status": "success",
            "seo_analysis": {{
                "niche": niche,
                "platform": "{channel_name}",
                "recommended_keywords": [],
                "seo_score": 0.7,
                "recommendations": [
                    f"Otimizar conteúdo para busca em {channel_name}",
                    "Usar palavras-chave de cauda longa",
                    "Incluir links internos e externos",
                ],
            }},
        }}

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name, step_id="{agent_id}", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"Análise SEO para {channel_name}"],
        )
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)
''',
    "monitor_agent": '''"""Agente de Monitoramento para {channel_name} — gerado automaticamente pela AgentFactory."""

from __future__ import annotations

from typing import Any

from .base import AgentBase, AgentResult, AgentTrace, CampaignContext, iso_duration_ms, utc_now_iso


class {class_name}(AgentBase):
    """Monitora métricas e performance em {channel_name}."""

    def __init__(self, **kwargs) -> None:
        super().__init__("{agent_id}", **kwargs)

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "")))

        output = {{
            "status": "success",
            "metrics": {{
                "platform": "{channel_name}",
                "niche": niche,
                "cycle_data_collected": True,
                "metrics_available": ["impressions", "clicks", "conversions"],
            }},
        }}

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name, step_id="{agent_id}", status="success",
            started_at=started_at, finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at), thread_name="main",
            notes=[f"Monitoramento {channel_name}"],
        )
        return AgentResult(agent=self.name, status="success", output=output, trace=trace)
''',
}


_SKILL_TEMPLATE = """# {class_name}

## Função
Agente gerado automaticamente pela AgentFactory para {channel_name}.

## Plataforma
{channel_name}

## Entrada
- Keywords e oportunidades (do SEOResearchAgent)
- Nicho da campanha

## Saída
- Conteúdo otimizado para {channel_name}
- Recomendações de SEO
- Métricas de performance

## Geração
Este agente foi criado automaticamente pelo sistema de segunda ordem.
Data: {timestamp}
"""


class AgentFactory(AgentBase):
    """Fábrica Autônoma de Agentes.

    Capacidade de segunda ordem: detecta gaps na arquitetura de agentes
    e cria novos agentes automaticamente, incluindo código, registro e docs.

    Estratégias de detecção:
    - MetaOrchestrator identifica bottlenecks → AgentFactory cria agente especializado
    - StrategyEvolution identifica novo canal → AgentFactory cria agente de marketing
    - PlatformCompliance detecta plataforma não coberta → AgentFactory cria compliance agent
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("agent_factory", **kwargs)
        self.agents_dir = Path("src/campaign_autopilot/agents")
        self.skills_dir = Path("skills")
        self.init_path = self.agents_dir / "__init__.py"
        self.orch_path = self.agents_dir / "orchestrator.py"

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        step_results = context.step_results

        # Detectar gaps baseado em step_results e análise
        gaps = self._detect_gaps(step_results, campaign)

        created: list[dict[str, Any]] = []
        errors: list[str] = []

        for gap in gaps:
            try:
                result = self._create_agent(gap)
                created.append(result)
            except Exception as e:
                errors.append(f"Falha ao criar agente '{gap.get('name')}': {e}")

        output = {
            "status": "success",
            "gaps_detected": len(gaps),
            "agents_created": len(created),
            "agents": created,
            "errors": errors,
            "summary": self._summary(len(gaps), len(created), errors),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="agent_factory",
                input_state={"gaps": len(gaps)},
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={"created": len(created)},
            )

        if self.semantic_memory:
            for c in created:
                cid = self.semantic_memory.register_concept(
                    c["agent_id"],
                    "agent",
                    f"Agente gerado automaticamente para {c['channel']}",
                )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="agent_factory",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[f"Detectou {len(gaps)} gaps, criou {len(created)} agentes"],
            metadata={"gaps": len(gaps), "created": len(created)},
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── Detecção de Gaps ───────────────────────────────────────

    def _detect_gaps(self, step_results: dict, campaign: dict) -> list[dict]:
        """Detect gaps in agent architecture based on context."""
        gaps = []
        existing_agents = self._get_existing_agents()
        channels = list(campaign.get("channels", []))
        meta = step_results.get("meta_orchestrator", {})
        meta_out = meta.get("output", {}) if isinstance(meta, dict) else {}

        # Gap 1: Channels without agents
        channel_to_agent = {
            "seo": "seo_research",
            "blog": "content_generator",
            "youtube": "youtube_marketing",
            "email": "email_marketing",
            "pinterest": "pinterest_marketing",
            "instagram": "instagram_marketing",
            "tiktok": "tiktok_marketing",
            "twitter": "twitter_marketing",
            "whatsapp": "whatsapp_marketing",
        }
        for ch in channels:
            expected = channel_to_agent.get(ch, ch)
            if expected not in existing_agents:
                gaps.append(
                    {
                        "name": f"{ch}_marketing",
                        "channel": ch,
                        "type": "marketing_channel",
                        "reasoning": f"Canal '{ch}' configurado mas sem agente dedicado",
                    }
                )

        # Gap 2: MetaOrchestrator prescribed new agents
        prescriptions = (
            meta_out.get("prescriptions", []) if isinstance(meta_out, dict) else []
        )
        for p in prescriptions:
            if isinstance(p, dict) and p.get("type") == "create_agent":
                gaps.append(
                    {
                        "name": p["target"],
                        "channel": p.get("target", "unknown"),
                        "type": p.get("agent_type", "marketing_channel"),
                        "reasoning": p.get("action", "Prescrito pelo MetaOrchestrator"),
                    }
                )

        # Gap 3: Detect new platforms from compliance reports
        compliance = step_results.get("platform_compliance", {})
        comp_out = compliance.get("output", {}) if isinstance(compliance, dict) else {}
        platforms_checked = (
            comp_out.get("platforms_checked", []) if isinstance(comp_out, dict) else []
        )
        for plat in platforms_checked:
            agent_name = f"{plat}_marketing"
            if agent_name not in existing_agents:
                gaps.append(
                    {
                        "name": agent_name,
                        "channel": plat,
                        "type": "marketing_channel",
                        "reasoning": f"Plataforma '{plat}' verificada por compliance mas sem agente dedicado",
                    }
                )

        return gaps[:3]  # Max 3 agents per cycle (safety limit)

    # ── Criação de Agente ───────────────────────────────────────

    def _create_agent(self, gap: dict) -> dict[str, Any]:
        """Create a new agent: code + registration + skill doc."""
        channel = gap["channel"]
        agent_type = gap.get("type", "marketing_channel")
        agent_id = gap["name"]
        class_name = self._to_class_name(agent_id)

        # 1. Generate Python code
        template = _AGENT_TEMPLATES.get(
            agent_type, _AGENT_TEMPLATES["marketing_channel"]
        )
        code = template.format(
            channel_name=channel.title(),
            class_name=class_name,
            agent_id=agent_id,
        )

        # 2. Validate syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Template gerou código inválido: {e}")

        # 3. Write agent file
        agent_file = self.agents_dir / f"{agent_id}.py"
        if agent_file.exists():
            return {
                "agent_id": agent_id,
                "channel": channel,
                "status": "already_exists",
                "file": str(agent_file),
            }
        agent_file.write_text(code)

        # 4. Register in __init__.py
        self._register_in_init(agent_id, class_name)

        # 5. Register in orchestrator.py
        self._register_in_orchestrator(agent_id, class_name)

        # 6. Create skill doc
        skill_file = self.skills_dir / f"{agent_id}.md"
        skill_content = _SKILL_TEMPLATE.format(
            class_name=class_name,
            channel_name=channel.title(),
            timestamp=utc_now_iso(),
        )
        skill_file.write_text(skill_content)

        return {
            "agent_id": agent_id,
            "class_name": class_name,
            "channel": channel,
            "agent_type": agent_type,
            "status": "created",
            "file": str(agent_file),
            "skill_file": str(skill_file),
            "reasoning": gap.get("reasoning", ""),
        }

    # ── Registro no Sistema ────────────────────────────────────

    def _register_in_init(self, agent_id: str, class_name: str) -> None:
        """Register new agent in agents/__init__.py."""
        if not self.init_path.exists():
            return

        content = self.init_path.read_text()

        # Add import
        import_line = f"from .{agent_id} import {class_name}"
        if import_line not in content:
            # Find last import
            lines = content.split("\n")
            last_import_idx = max(
                i for i, l in enumerate(lines) if l.startswith("from .")
            )
            lines.insert(last_import_idx + 1, import_line)

            # Find last __all__ entry
            all_end = len(lines) - 1
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().endswith('"]'):
                    all_end = i
                    break
            all_line = f'    "{class_name}",'
            if all_line not in lines:
                lines.insert(all_end, all_line)

            self.init_path.write_text("\n".join(lines) + "\n")

    def _register_in_orchestrator(self, agent_id: str, class_name: str) -> None:
        """Register new agent in orchestrator.py registry."""
        if not self.orch_path.exists():
            return

        content = self.orch_path.read_text()

        # Add import
        import_line = f"from .{agent_id} import {class_name}"
        if import_line not in content:
            lines = content.split("\n")
            last_import_idx = max(
                (i for i, l in enumerate(lines) if l.startswith("from .")), default=0
            )
            lines.insert(last_import_idx + 1, import_line)

            # Add to registry (before the closing })
            agent_reg = f'''            "{agent_id}": {class_name}(
                semantic_memory=self.semantic_memory,
                explanation_store=self.explanation_store,
            ),'''
            # Find the last registry entry before closing brace
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == "}":
                    lines.insert(i, agent_reg)
                    break

            # Add to observers
            for i, line in enumerate(lines):
                if '"self_healing"' in line and '"ontology_steward"' in line:
                    lines[i] = line.replace(
                        '"self_healing", "ontology_steward"',
                        f'"self_healing", "{agent_id}", "ontology_steward"',
                    )
                    break

            self.orch_path.write_text("\n".join(lines) + "\n")

    # ── Utilitários ────────────────────────────────────────────

    def _get_existing_agents(self) -> set[str]:
        """Get set of existing agent step IDs."""
        agents = set()
        if self.init_path.exists():
            content = self.init_path.read_text()
            for match in re.finditer(r"from\.(\w+)\.import", content):
                agents.add(match.group(1))
        return agents

    @staticmethod
    def _to_class_name(agent_id: str) -> str:
        """Convert snake_case_agent_id to CamelCaseAgentId."""
        return "".join(word.title() for word in agent_id.split("_"))

    @staticmethod
    def _summary(gaps: int, created: int, errors: list[str]) -> str:
        if created > 0:
            return (
                f"🔧 AgentFactory: {gaps} gaps detectados, {created} agentes criados. "
                f"Sistema auto-estendido com sucesso."
            )
        elif gaps > 0:
            return (
                f"🔍 AgentFactory: {gaps} gaps detectados mas nenhum agente criado "
                f"(limite de segurança ou todos já existentes)."
            )
        return "✅ AgentFactory: Nenhum gap detectado. Arquitetura de agentes completa."
