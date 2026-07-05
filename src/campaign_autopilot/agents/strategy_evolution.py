"""StrategyEvolutionAgent — Planejamento Estratégico Evolutivo entre Ciclos.

Este agente opera na camada de segunda ordem:
- Avalia tendências de longo prazo (múltiplos ciclos)
- Gera estratégias adaptativas baseadas em resultados acumulados
- Recomenda pivotagem de nicho, canais ou formato de conteúdo
- Planeja campanhas multi-ciclo com objetivos progressivos
- Identifica janelas de oportunidade baseadas em dados históricos
"""

from __future__ import annotations

import json
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


# ── Templates de Estratégia Evolutiva ─────────────────────────────

_EVOLUTION_STRATEGIES: list[dict[str, Any]] = [
    {
        "name": "nichos_adjacentes",
        "description": "Expandir para nichos adjacentes ao nicho principal",
        "trigger": "Alta saturação de keywords no nicho atual (>70% keywords com dificuldade >50)",
        "action": "Pesquisar keywords em nichos vizinhos com baixa concorrência",
        "risk": "Médio",
        "reward": "Alto",
    },
    {
        "name": "formato_dominante",
        "description": "Identificar e focar no formato de conteúdo com melhor ROI",
        "trigger": "Disparidade de performance entre canais >40%",
        "action": "Redirecionar esforço para o canal com melhor custo-benefício",
        "risk": "Baixo",
        "reward": "Médio",
    },
    {
        "name": "pivotagem_conteudo",
        "description": "Mudar o formato/language do conteúdo baseado em tendências",
        "trigger": "3 ciclos consecutivos com tráfego orgânico estável ou declinante",
        "action": "Testar novo formato (ex: de texto para vídeo, de blog para YouTube)",
        "risk": "Alto",
        "reward": "Muito Alto",
    },
    {
        "name": "deep_dive",
        "description": "Aprofundar em tópicos com melhor performance orgânica",
        "trigger": "Keyword com CTR >5% e volume >1000 aparece em mais de 1 ciclo",
        "action": "Criar cluster de 5-10 artigos aprofundando no tópico vencedor",
        "risk": "Baixo",
        "reward": "Alto",
    },
    {
        "name": "sazonalidade",
        "description": "Antecipar tendências sazonais baseadas em histórico de ciclos",
        "trigger": "Disponível após 12+ ciclos de dados históricos",
        "action": "Criar conteúdo sazonal com 30-60 dias de antecedência",
        "risk": "Médio",
        "reward": "Alto",
    },
    {
        "name": "cross_nicho_pollination",
        "description": "Cruzar conteúdo entre nichos para atingir novas audiências",
        "trigger": "2+ nichos ativos com sobreposição de audiência >20%",
        "action": "Criar conteúdo bridge entre nichos",
        "risk": "Médio",
        "reward": "Médio",
    },
]


class StrategyEvolutionAgent(AgentBase):
    """Planejamento Estratégico Evolutivo — opera entre ciclos para guiar a evolução do sistema.

    Diferente dos agentes de ciclo (que otimizam o ciclo atual),
    este agente olha para a trajetória de múltiplos ciclos e ajusta
    a direção estratégica geral.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("strategy_evolution", **kwargs)
        self.strategy_file = Path(".state/strategy_evolution.json")
        self.strategy_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        if self.strategy_file.exists():
            try:
                self.state = json.loads(self.strategy_file.read_text())
            except (json.JSONDecodeError, Exception):
                self.state = self._default_state()
        else:
            self.state = self._default_state()

    def _save_state(self) -> None:
        self.strategy_file.write_text(json.dumps(self.state, indent=2, default=str))

    def _default_state(self) -> dict:
        return {
            "cycles_analyzed": 0,
            "strategies_attempted": [],
            "strategies_succeeded": [],
            "niche_history": [],
            "channel_performance": {},
            "current_phase": "exploration",  # exploration → growth → optimization → scale
            "long_term_goals": [],
            "evolution_timeline": [],
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        campaign = context.campaign
        niche = str(campaign.get("niche", campaign.get("objective", "")))
        step_results = context.step_results

        # Atualizar estado
        self.state["cycles_analyzed"] += 1
        self.state["niche_history"].append(
            {
                "cycle": self.state["cycles_analyzed"],
                "niche": niche,
                "timestamp": utc_now_iso(),
            }
        )
        if len(self.state["niche_history"]) > 20:
            self.state["niche_history"] = self.state["niche_history"][-20:]

        # Coletar métricas do ciclo
        cycle_metrics = self._collect_cycle_metrics(step_results)
        self._update_channel_performance(cycle_metrics)

        # Determinar fase evolutiva
        new_phase = self._determine_phase()
        if new_phase != self.state["current_phase"]:
            self.state["evolution_timeline"].append(
                {
                    "cycle": self.state["cycles_analyzed"],
                    "from": self.state["current_phase"],
                    "to": new_phase,
                    "timestamp": utc_now_iso(),
                }
            )
            self.state["current_phase"] = new_phase

        # Identificar estratégias aplicáveis
        applicable = self._find_applicable_strategies(cycle_metrics)

        # Gerar recomendações estratégicas
        recommendations = self._generate_strategic_recommendations(
            applicable, cycle_metrics, niche
        )

        # Atualizar metas de longo prazo
        long_term = self._update_long_term_goals(cycle_metrics)

        self._save_state()

        output = {
            "status": "success",
            "current_phase": self.state["current_phase"],
            "cycles_analyzed": self.state["cycles_analyzed"],
            "niche_focus": niche,
            "applicable_strategies": applicable,
            "strategic_recommendations": recommendations,
            "long_term_goals": long_term,
            "channel_performance_summary": self._summarize_channel_performance(),
            "phase_description": self._phase_description(self.state["current_phase"]),
        }

        if self.explanation_store:
            did = self.explanation_store.record_decision(
                agent_id=self.name,
                cycle_id=context.run_id,
                decision_type="strategy_evolution",
                input_state={
                    "cycles": self.state["cycles_analyzed"],
                    "phase": self.state["current_phase"],
                },
            )
            self.explanation_store.update_decision_output(
                did,
                output_decision={"recommendations": len(recommendations)},
            )

        finished_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id="strategy_evolution",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=iso_duration_ms(started_at, finished_at),
            thread_name="main",
            notes=[
                f"Ciclo {self.state['cycles_analyzed']} | Fase: {self.state['current_phase']} | "
                f"{len(recommendations)} recomendações estratégicas"
            ],
            metadata={
                "phase": self.state["current_phase"],
                "cycles": self.state["cycles_analyzed"],
                "active_channels": len(self.state.get("channel_performance", {})),
            },
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )

    # ── Coleta de Métricas ──────────────────────────────────────

    def _collect_cycle_metrics(self, step_results: dict) -> dict[str, Any]:
        """Coletar métricas relevantes para decisões estratégicas."""
        metrics: dict[str, Any] = {
            "total_agents_executed": 0,
            "content_generated": 0,
            "images_generated": 0,
            "videos_generated": 0,
            "channels_covered": set(),
            "errors": 0,
        }

        def _get_out(step_id: str) -> dict:
            s = step_results.get(step_id, {})
            o = s.get("output", {}) if isinstance(s, dict) else {}
            return o if isinstance(o, dict) else {}

        metrics["total_agents_executed"] = len(step_results)
        cg = _get_out("content_generator")
        metrics["content_generated"] = len(
            cg.get("articles", []) or cg.get("generated_articles", [])
        )

        ig = _get_out("free_image_gen")
        metrics["images_generated"] = ig.get("images_generated", 0)

        vp = _get_out("free_video_producer")
        metrics["videos_generated"] = vp.get("videos_generated", 0)

        for ch in [
            "youtube_marketing",
            "instagram_marketing",
            "tiktok_marketing",
            "twitter_marketing",
            "pinterest_marketing",
            "whatsapp_marketing",
        ]:
            out = _get_out(ch)
            if out:
                metrics["channels_covered"].add(ch.replace("_marketing", ""))

        pm = _get_out("platform_compliance")
        metrics["compliance_issues"] = pm.get("total_issues", 0)

        rm = _get_out("revenue_monitor")
        metrics["revenue_projection"] = (
            rm.get("total_projected", rm.get("projections", [{}])[0].get("value", 0))
            if rm
            else 0
        )

        metrics["channels_covered"] = list(metrics["channels_covered"])
        return metrics

    # ── Performance de Canais ───────────────────────────────────

    def _update_channel_performance(self, metrics: dict) -> None:
        for channel in metrics.get("channels_covered", []):
            if channel not in self.state["channel_performance"]:
                self.state["channel_performance"][channel] = {
                    "cycles_active": 0,
                    "total_content": 0,
                    "total_revenue": 0,
                }
            perf = self.state["channel_performance"][channel]
            perf["cycles_active"] += 1
            perf["total_content"] += metrics.get("content_generated", 0)

    def _summarize_channel_performance(self) -> list[dict]:
        return sorted(
            [
                {"channel": ch, **perf}
                for ch, perf in self.state["channel_performance"].items()
            ],
            key=lambda x: x["cycles_active"],
            reverse=True,
        )

    # ── Determinação de Fase Evolutiva ──────────────────────────

    def _determine_phase(self) -> str:
        cycles = self.state["cycles_analyzed"]
        if cycles < 3:
            return "exploration"
        elif cycles < 10:
            return "growth"
        elif cycles < 30:
            return "optimization"
        else:
            return "scale"

    def _phase_description(self, phase: str) -> str:
        descriptions = {
            "exploration": "Testando diferentes nichos, canais e formatos. Coletando dados de baseline.",
            "growth": "Escalando canais com melhor performance. Foco em quantidade e consistência.",
            "optimization": "Refinando processos. Removendo canais de baixo ROI. Automatizando ao máximo.",
            "scale": "Sistema maduro. Foco em eficiência máxima e expansão para múltiplos nichos.",
        }
        return descriptions.get(phase, "Fase desconhecida")

    # ── Estratégias Aplicáveis ──────────────────────────────────

    def _find_applicable_strategies(self, metrics: dict) -> list[dict]:
        """Find strategies applicable to current cycle state."""
        applicable = []
        for strategy in _EVOLUTION_STRATEGIES:
            applicable.append(
                {
                    "name": strategy["name"],
                    "description": strategy["description"],
                    "trigger": strategy["trigger"],
                    "action": strategy["action"],
                    "risk": strategy["risk"],
                    "reward": strategy["reward"],
                    "is_active": False,  # Would require more data to determine
                }
            )
        return applicable

    # ── Recomendações Estratégicas ──────────────────────────────

    def _generate_strategic_recommendations(
        self, strategies: list[dict], metrics: dict, niche: str
    ) -> list[dict]:
        """Generate strategic recommendations based on current phase."""
        recs = []
        phase = self.state["current_phase"]

        if phase == "exploration":
            recs.append(
                {
                    "type": "focus",
                    "priority": "high",
                    "recommendation": f"Fase de exploração. Testar {niche} por pelo menos 3 ciclos antes de pivotar.",
                    "rationale": "Dados insuficientes para conclusões estatísticas.",
                }
            )
            recs.append(
                {
                    "type": "breadth",
                    "priority": "medium",
                    "recommendation": "Experimentar 2-3 canais diferentes para identificar qual gera melhor resposta.",
                    "rationale": "Exploração de canais no início acelera o aprendizado.",
                }
            )

        elif phase == "growth":
            channels = len(metrics.get("channels_covered", []))
            if channels >= 3:
                recs.append(
                    {
                        "type": "depth",
                        "priority": "high",
                        "recommendation": f"{channels} canais ativos. Focar nos 2-3 com melhor resposta e aprofundar.",
                        "rationale": "Crescimento vem de profundidade, não de quantidade de canais.",
                    }
                )
            recs.append(
                {
                    "type": "consistency",
                    "priority": "high",
                    "recommendation": "Aumentar frequência de publicação. Consistência semanal supera intensidade esporádica.",
                    "rationale": "Algoritmos priorizam consistência.",
                }
            )

        elif phase == "optimization":
            recs.append(
                {
                    "type": "remove_low_roi",
                    "priority": "high",
                    "recommendation": "Analisar canais com baixo engajamento e considerar realocar esforço.",
                    "rationale": "Fase de otimização exige cortar o que não funciona.",
                }
            )
            recs.append(
                {
                    "type": "automation",
                    "priority": "medium",
                    "recommendation": "Automatizar publicação e distribuição para reduzir atrito operacional.",
                    "rationale": "Eficiência operacional libera recursos para estratégia.",
                }
            )

        elif phase == "scale":
            recs.append(
                {
                    "type": "new_niches",
                    "priority": "high",
                    "recommendation": f"Sistema maduro. Iniciar expansão para nicho adjacente a '{niche}'.",
                    "rationale": "Escalar significa multiplicar o modelo que funciona.",
                }
            )
            recs.append(
                {
                    "type": "authority",
                    "priority": "medium",
                    "recommendation": "Focar em backlinks de autoridade e guest posts para fortalecer domínio.",
                    "rationale": "Domínio autoritativo escala melhor a longo prazo.",
                }
            )

        return recs

    # ── Metas de Longo Prazo ────────────────────────────────────

    def _update_long_term_goals(self, metrics: dict) -> list[dict]:
        """Update long-term strategic goals."""
        cycles = self.state["cycles_analyzed"]

        # Generate milestone goals based on phase
        goals = []
        phase = self.state["current_phase"]

        if phase == "exploration":
            goals.append(
                {
                    "goal": "Completar 3 ciclos de exploração",
                    "progress": f"{min(cycles, 3)}/3",
                    "deadline": "3 ciclos",
                }
            )
            goals.append(
                {
                    "goal": "Identificar canal primário com melhor resposta",
                    "progress": "Em andamento",
                    "deadline": "5 ciclos",
                }
            )

        elif phase == "growth":
            goals.append(
                {
                    "goal": "Estabelecer frequência de publicação consistente",
                    "progress": "Ativo",
                    "deadline": "Contínuo",
                }
            )
            goals.append(
                {
                    "goal": "Acumular 10+ ciclos de dados para otimização",
                    "progress": f"{min(cycles, 10)}/10",
                    "deadline": f"{max(0, 10 - cycles)} ciclos",
                }
            )

        elif phase in ("optimization", "scale"):
            goals.append(
                {
                    "goal": "Automação completa do pipeline",
                    "progress": "90%",
                    "deadline": "Próximo ciclo",
                }
            )
            goals.append(
                {
                    "goal": f"Expandir para novos nichos (meta: {min(cycles // 10 + 2, 5)} nichos)",
                    "progress": f"{len(set(h['niche'] for h in self.state['niche_history']))} nicho(s)",
                    "deadline": "Longo prazo",
                }
            )

        return goals
