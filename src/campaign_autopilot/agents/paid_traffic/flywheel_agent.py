"""PaidTrafficFlywheelAgent — Ciclo completo orgânico → flywheel → tráfego pago autopilot.

Fluxo:
1. Recebe receita orgânica do Parallel Revenue Tree
2. Calcula fase do flywheel (0-4) baseado na receita
3. Aloca orçamento de tráfego pago proporcional à fase
4. Cria campanhas (Google Ads, Meta Ads, Native Ads)
5. Rastreia performance e ajusta ROAS
6. Reforça o flywheel: lucro do tráfego pago → mais tráfego

Fases:
  Fase 0: CONSTRUIR  — Só orgânico (receita < R$ 500)
  Fase 1: TESTAR     — 20% reinvestido, ROAS 1.3x (R$ 500+)
  Fase 2: VALIDAR    — 35% reinvestido, ROAS 1.8x (R$ 5.000+)
  Fase 3: ESCALAR    — 50% reinvestido, ROAS 2.5x (R$ 50.000+)
  Fase 4: FLYWHEEL   — 60% reinvestido, ROAS 3.0x (R$ 500.000+)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ...logging_utils import StructuredLogger
from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext

log = StructuredLogger("paid_flywheel")

STATE_FILE = Path(".state/flywheel_state.json")

FLYWHEEL_PHASES = {
    0: {
        "name": "CONSTRUIR",
        "min_revenue": 0,
        "reinvest_pct": 0.00,
        "roas_target": 0.0,
        "desc": "Apenas conteúdo orgânico",
    },
    1: {
        "name": "TESTAR",
        "min_revenue": 500,
        "reinvest_pct": 0.20,
        "roas_target": 1.3,
        "desc": "Testes com 20% da receita orgânica",
    },
    2: {
        "name": "VALIDAR",
        "min_revenue": 5000,
        "reinvest_pct": 0.35,
        "roas_target": 1.8,
        "desc": "Campanhas aprendendo, 35% reinvestido",
    },
    3: {
        "name": "ESCALAR",
        "min_revenue": 50000,
        "reinvest_pct": 0.50,
        "roas_target": 2.5,
        "desc": "ROAS comprovado, 50% reinvestido",
    },
    4: {
        "name": "FLYWHEEL",
        "min_revenue": 500000,
        "reinvest_pct": 0.60,
        "roas_target": 3.0,
        "desc": "Tráfego pago se paga + alimenta crescimento",
    },
}


class PaidTrafficFlywheelAgent(AgentBase):
    """Agente único que gerencia o ciclo completo do flywheel orgânico → pago."""

    def __init__(self, **kwargs):
        super().__init__("paid_traffic_flywheel", **kwargs)
        self._state = self._load_state()

    def _load_state(self) -> dict:
        try:
            if STATE_FILE.exists():
                return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
        return {
            "phase": 0,
            "total_organic_revenue": 0.0,
            "total_paid_revenue": 0.0,
            "total_paid_spend": 0.0,
            "total_paid_profit": 0.0,
            "months_above_threshold": 0,
            "active": False,
            "flywheel_active": False,
            "history": [],
        }

    def _save_state(self) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
        STATE_FILE.write_text(json.dumps(self._state, indent=2))

    def _get_current_phase(self, monthly_revenue: float) -> int:
        for phase_num in sorted(FLYWHEEL_PHASES.keys(), reverse=True):
            if monthly_revenue >= FLYWHEEL_PHASES[phase_num]["min_revenue"]:
                return phase_num
        return 0

    def _calculate_budget(self, organic_revenue: float) -> dict:
        phase = self._get_current_phase(organic_revenue)
        phase_info = FLYWHEEL_PHASES[phase]
        reinvest_pct = phase_info["reinvest_pct"]

        # Budget base
        base_budget = organic_revenue * reinvest_pct

        # Flywheel bonus: 30% do lucro do tráfego pago anterior
        flywheel_bonus = 0.0
        if self._state.get("flywheel_active") and self._state["total_paid_profit"] > 0:
            flywheel_bonus = self._state["total_paid_profit"] * 0.30

        total_budget = base_budget + flywheel_bonus

        # Cap progressivo baseado em meses de atividade
        months_active = sum(
            1 for h in self._state["history"] if h.get("paid_spend", 0) > 0
        )
        if months_active <= 3:
            total_budget = min(total_budget, organic_revenue * 0.30)
        elif months_active <= 6:
            total_budget = min(total_budget, organic_revenue * 0.40)
        else:
            total_budget = min(total_budget, organic_revenue * 0.50)

        # Budget mínimo: R$ 200/mês (R$ 7/dia) para valer a pena
        if total_budget < 200:
            total_budget = 0.0

        return {
            "phase": phase,
            "phase_name": phase_info["name"],
            "reinvest_pct": reinvest_pct,
            "monthly_budget": round(total_budget, 2),
            "daily_budget": round(total_budget / 30, 2),
            "flywheel_bonus": round(flywheel_bonus, 2),
            "roas_target": phase_info["roas_target"],
            "months_paid_active": months_active,
            "description": phase_info["desc"],
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            campaign = context.campaign if hasattr(context, "campaign") else {}
            action = campaign.get("action", "cycle")

            if action == "cycle":
                return self._run_cycle(campaign, started_at)
            elif action == "status":
                return self._status(started_at)
            elif action == "reset":
                return self._reset(started_at)
            else:
                return self._run_cycle(campaign, started_at)

        except Exception as e:
            return AgentResult(
                agent=self.name,
                status="error",
                output={"error": str(e)},
                trace=AgentTrace(
                    agent=self.name,
                    step_id="flywheel",
                    status="error",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=0,
                    thread_name="main",
                ),
            )

    def _run_cycle(self, campaign: dict, started_at: str) -> AgentResult:
        """Executa um ciclo completo do flywheel."""
        # 1. Pega receita orgânica das 13 fontes
        sources = campaign.get("sources", {})
        organic_revenue = (
            sum(
                s.get("estimated_monthly_revenue", 0)
                for s in sources.values()
                if isinstance(s, dict)
            )
            if sources
            else campaign.get("estimated_monthly_revenue", 0)
        )

        paid_spend = float(campaign.get("paid_traffic_spend", 0))
        paid_revenue = float(campaign.get("paid_traffic_revenue", 0))

        # 2. Atualiza estado do flywheel
        self._state["total_organic_revenue"] += organic_revenue
        self._state["total_paid_spend"] += paid_spend
        self._state["total_paid_revenue"] += paid_revenue
        self._state["total_paid_profit"] += paid_revenue - paid_spend
        self._state["months_above_threshold"] = (
            self._state["months_above_threshold"] + 1 if organic_revenue >= 500 else 0
        )

        # 3. Calcula fase
        phase = self._get_current_phase(organic_revenue)
        if phase > self._state["phase"]:
            log.info("flywheel_up", old=self._state["phase"], new=phase)
        self._state["phase"] = phase

        # 4. Ativa flywheel se tráfego pago foi lucrativo
        if paid_revenue > paid_spend and paid_spend > 0:
            self._state["flywheel_active"] = True

        # 5. Calcula orçamento
        budget = self._calculate_budget(organic_revenue)

        # 6. Registra histórico
        self._state["history"].append(
            {
                "date": datetime.now(timezone.utc).isoformat(),
                "organic_revenue": round(organic_revenue, 2),
                "paid_spend": round(paid_spend, 2),
                "paid_revenue": round(paid_revenue, 2),
                "phase": phase,
                "budget": budget,
            }
        )
        self._state["history"] = self._state["history"][-24:]
        self._save_state()

        # 7. Decide se ativa tráfego pago
        can_activate = (
            organic_revenue >= 500
            and self._state["months_above_threshold"] >= 2
            and budget["monthly_budget"] > 0
        )
        self._state["active"] = can_activate

        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "flywheel_active": self._state["flywheel_active"],
                "phase": phase,
                "phase_name": FLYWHEEL_PHASES[phase]["name"],
                "phase_description": FLYWHEEL_PHASES[phase]["desc"],
                "organic_revenue": round(organic_revenue, 2),
                "can_activate_paid": can_activate,
                "months_stable": self._state["months_above_threshold"],
                **budget,
                "recommended_allocation": {
                    "google_ads": round(budget["monthly_budget"] * 0.60, 2),
                    "meta_ads": round(budget["monthly_budget"] * 0.30, 2),
                    "native_ads": round(budget["monthly_budget"] * 0.10, 2),
                },
                "total_all_time": {
                    "organic": round(self._state["total_organic_revenue"], 2),
                    "paid_revenue": round(self._state["total_paid_revenue"], 2),
                    "paid_spend": round(self._state["total_paid_spend"], 2),
                    "paid_profit": round(self._state["total_paid_profit"], 2),
                },
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="flywheel_cycle",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
                notes=[
                    "Fase {}: {} | R$ {:.2f} orçamento".format(
                        phase, FLYWHEEL_PHASES[phase]["name"], budget["monthly_budget"]
                    )
                ],
            ),
        )

    def _status(self, started_at: str) -> AgentResult:
        phase = self._state["phase"]
        budget = self._calculate_budget(self._state["total_organic_revenue"])
        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={
                "phase": phase,
                "phase_name": FLYWHEEL_PHASES[phase]["name"],
                "flywheel_active": self._state["flywheel_active"],
                "total_organic_revenue": round(self._state["total_organic_revenue"], 2),
                "total_paid_profit": round(self._state["total_paid_profit"], 2),
                **budget,
            },
            trace=AgentTrace(
                agent=self.name,
                step_id="flywheel_status",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )

    def _reset(self, started_at: str) -> AgentResult:
        self._state = {
            "phase": 0,
            "total_organic_revenue": 0.0,
            "total_paid_revenue": 0.0,
            "total_paid_spend": 0.0,
            "total_paid_profit": 0.0,
            "months_above_threshold": 0,
            "active": False,
            "flywheel_active": False,
            "history": [],
        }
        self._save_state()
        finished_at = datetime.now(timezone.utc).isoformat()
        return AgentResult(
            agent=self.name,
            status="success",
            output={"message": "Flywheel resetado para Fase 0"},
            trace=AgentTrace(
                agent=self.name,
                step_id="flywheel_reset",
                status="success",
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=0,
                thread_name="main",
            ),
        )
