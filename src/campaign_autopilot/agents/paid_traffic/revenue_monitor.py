"""RevenueMonitorAgent — Monitora receita e decide quando ativar tráfego pago.

Regras de decisão:
- Threshold mínimo: R$ 500 de receita mensal consistente
- % do lucro reinvestido: 30-50% (configurável)
- Só ativa após 2 meses consecutivos acima do threshold
- Desativa campanhas se ROAS < 1.5 por 2 semanas
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..base import AgentBase, AgentResult, AgentTrace, CampaignContext
from ...logging_utils import StructuredLogger

log = StructuredLogger("revenue_monitor")

DEFAULT_CONFIG = {
    "min_monthly_revenue": 500.0,
    "min_consecutive_months": 2,
    "reinvest_percentage": 0.40,
    "min_roas": 1.5,
    "max_daily_budget": 200.0,
    "platforms": ["google_ads", "meta_ads"],
    "allowed_niches": ["tecnologia", "financas", "saude", "carreira"],
}

STATE_FILE = Path(".state/paid_traffic_state.json")


class FlywheelState:
    """Managed flywheel state persisted between cycles."""

    PHASES = {
        0: {
            "name": "CONSTRUIR",
            "min_revenue": 0,
            "reinvest_pct": 0.0,
            "roas_esperado": 0,
            "desc": "So conteudo organico",
        },
        1: {
            "name": "TESTAR",
            "min_revenue": 500,
            "reinvest_pct": 0.20,
            "roas_esperado": 1.3,
            "desc": "20% da receita em testes, ROAS baixo (aprendizado)",
        },
        2: {
            "name": "VALIDAR",
            "min_revenue": 5000,
            "reinvest_pct": 0.35,
            "roas_esperado": 1.8,
            "desc": "35% reinvestido, campanhas aprendendo",
        },
        3: {
            "name": "ESCALAR",
            "min_revenue": 50000,
            "reinvest_pct": 0.50,
            "roas_esperado": 2.5,
            "desc": "50% reinvestido, ROAS comprovado",
        },
        4: {
            "name": "FLYWHEEL",
            "min_revenue": 500000,
            "reinvest_pct": 0.60,
            "roas_esperado": 3.0,
            "desc": "Trafego pago se paga sozinho + alimenta crescimento",
        },
    }

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self._state = self._load()

    def _load(self) -> dict:
        try:
            if self.state_file.exists():
                return json.loads(self.state_file.read_text())
        except Exception:
            pass
        return {
            "phase": 0,
            "active": False,
            "total_organic_revenue": 0.0,
            "total_paid_revenue": 0.0,
            "total_paid_spend": 0.0,
            "total_paid_profit": 0.0,
            "months_above_threshold": 0,
            "last_month_revenue": 0.0,
            "last_month_paid_profit": 0.0,
            "cycle_count": 0,
            "roas_history": [],
            "history": [],
            "flywheel_active": False,
        }

    def _save(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.state_file.write_text(json.dumps(self._state, indent=2, default=str))

    @property
    def phase(self) -> int:
        return self._state.get("phase", 0)

    @phase.setter
    def phase(self, value: int) -> None:
        self._state["phase"] = min(value, max(self.PHASES.keys()))

    def get_phase_info(self) -> dict:
        return self.PHASES.get(self.phase, self.PHASES[0])

    def update_phase(self, monthly_revenue: float) -> None:
        """Atualiza a fase baseado na receita mensal."""
        for phase_num, phase_info in sorted(self.PHASES.items(), reverse=True):
            if monthly_revenue >= phase_info["min_revenue"]:
                if phase_num > self._state["phase"]:
                    (
                        log.info(
                            "flywheel_phase_up",
                            old_phase=self._state["phase"],
                            new_phase=phase_num,
                            phase_name=phase_info["name"],
                        ),
                    )
                self._state["phase"] = phase_num
                break

    def get_reinvest_percentage(self) -> float:
        """Retorna % de reinvestimento baseado na fase atual."""
        phase_info = self.get_phase_info()
        base_pct = phase_info["reinvest_pct"]

        # Bonus flywheel: se o trafego pago foi lucrativo, aumenta o reinvestimento
        if (
            self._state.get("flywheel_active")
            and self._state.get("last_month_paid_profit", 0) > 0
        ):
            bonus = min(
                0.10,
                self._state["last_month_paid_profit"]
                / max(self._state["last_month_revenue"], 1)
                * 0.05,
            )
            base_pct = min(base_pct * (1 + bonus), 0.80)  # Cap at 80%

        return base_pct

    def get_roas_target(self) -> float:
        """Retorna ROAS esperado para a fase atual."""
        return self.get_phase_info()["roas_esperado"]

    def record_cycle(
        self, organic_revenue: float, paid_spend: float, paid_revenue: float
    ) -> None:
        """Registra os resultados de um ciclo e atualiza o estado do flywheel."""
        self._state["cycle_count"] += 1
        self._state["total_organic_revenue"] += organic_revenue
        self._state["total_paid_revenue"] += paid_revenue
        self._state["total_paid_spend"] += paid_spend
        self._state["last_month_revenue"] = organic_revenue
        self._state["last_month_paid_profit"] = paid_revenue - paid_spend

        if paid_spend > 0:
            roas = paid_revenue / paid_spend
            self._state["roas_history"].append(
                {
                    "cycle": self._state["cycle_count"],
                    "roas": round(roas, 2),
                    "spend": paid_spend,
                    "revenue": paid_revenue,
                    "date": datetime.now(timezone.utc).isoformat(),
                }
            )
            self._state["roas_history"] = self._state["roas_history"][
                -24:
            ]  # Keep last 24
            self._state["total_paid_profit"] += paid_revenue - paid_spend

            # Flywheel ativa quando o trafego pago foi lucrativo no mes passado
            if paid_revenue > paid_spend:
                self._state["flywheel_active"] = True

        self._state["history"].append(
            {
                "cycle": self._state["cycle_count"],
                "date": datetime.now(timezone.utc).isoformat(),
                "organic_revenue": round(organic_revenue, 2),
                "paid_spend": round(paid_spend, 2),
                "paid_revenue": round(paid_revenue, 2),
                "paid_profit": round(paid_revenue - paid_spend, 2),
                "phase": self._state["phase"],
            }
        )
        self._state["history"] = self._state["history"][-12:]  # Keep last 12

        self.update_phase(organic_revenue)
        self._save()

    def get_flywheel_budget(self, organic_revenue: float) -> dict:
        """Calcula o orcamento de trafego pago com base no flywheel."""
        pct = self.get_reinvest_percentage()
        base_budget = organic_revenue * pct

        # Flywheel bonus: 30% do lucro do trafego pago do mes passado
        flywheel_bonus = 0
        if (
            self._state.get("flywheel_active")
            and self._state.get("last_month_paid_profit", 0) > 0
        ):
            flywheel_bonus = self._state["last_month_paid_profit"] * 0.30

        # Cap: nunca gastar mais que 60% da receita organica + bonus flywheel
        total_budget = min(base_budget + flywheel_bonus, organic_revenue * 0.60)

        # Escala gradual baseada no tempo de trafego pago ativo
        months_paid = sum(
            1 for h in self._state.get("history", []) if h.get("paid_spend", 0) > 0
        )
        if months_paid <= 3:
            total_budget = min(total_budget, 50000, organic_revenue * 0.30)
        elif months_paid <= 6:
            total_budget = min(total_budget, 100000, organic_revenue * 0.40)
        elif months_paid <= 12:
            total_budget = min(total_budget, 300000, organic_revenue * 0.50)
        else:
            total_budget = min(total_budget, 500000, organic_revenue * 0.50)

        if total_budget < 200:
            total_budget = 0

        return {
            "budget": round(total_budget, 2),
            "daily_budget": round(total_budget / 30, 2),
            "reinvest_pct": round(pct * 100, 1),
            "flywheel_bonus": round(flywheel_bonus, 2),
            "phase": self.phase,
            "phase_name": self.get_phase_info()["name"],
            "months_paid_active": months_paid,
        }


class RevenueMonitorAgent(AgentBase):
    """Monitora receita e ativa o flywheel de trafego pago com fases evolutivas.

    Flywheel completo:
    Fase 0: CONSTRUIR — So conteudo organico
    Fase 1: TESTAR — 20% em trafego pago, ROAS 1.3x
    Fase 2: VALIDAR — 35% reinvestido, ROAS 1.8x
    Fase 3: ESCALAR — 50% reinvestido, ROAS 2.5x
    Fase 4: FLYWHEEL — 60% reinvestido, trafego pago se paga sozinho
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("revenue_monitor", **kwargs)
        self.config = dict(DEFAULT_CONFIG)
        if os.environ.get("PAID_TRAFFIC_THRESHOLD"):
            self.config["min_monthly_revenue"] = float(
                os.environ["PAID_TRAFFIC_THRESHOLD"]
            )
        if os.environ.get("PAID_TRAFFIC_REINVEST_PCT"):
            self.config["reinvest_percentage"] = (
                float(os.environ["PAID_TRAFFIC_REINVEST_PCT"]) / 100.0
            )
        if os.environ.get("PAID_TRAFFIC_MAX_DAILY"):
            self.config["max_daily_budget"] = float(
                os.environ["PAID_TRAFFIC_MAX_DAILY"]
            )
        self.flywheel = FlywheelState()

    def _estimate_monthly_revenue(self, campaign: dict[str, Any]) -> dict[str, float]:
        """Estima receita mensal baseada nos dados disponiveis."""
        revenue = campaign.get("revenue_data", {})
        if revenue:
            affiliate = float(revenue.get("affiliate_hotmart", 0)) + float(
                revenue.get("affiliate_amazon", 0)
            )
            adsense = float(revenue.get("adsense", 0))
            products = float(revenue.get("digital_product", 0))
            membership = float(revenue.get("membership", 0))
            paid = float(revenue.get("paid_traffic", 0))
            total = affiliate + adsense + products + membership + paid
        else:
            articles = int(campaign.get("total_articles", 0))
            traffic = int(campaign.get("estimated_monthly_visitors", 0))
            affiliate = traffic * 0.005 * 50.0
            adsense = traffic * 5.0 / 1000.0
            total = affiliate + adsense
            paid = 0

        return {
            "affiliate": affiliate,
            "adsense": adsense,
            "digital_products": float(revenue.get("digital_product", 0)),
            "membership": float(revenue.get("membership", 0)),
            "paid_traffic": paid,
            "total": total,
            "estimated": not bool(revenue),
        }

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = datetime.now(timezone.utc).isoformat()
        campaign = context.campaign if hasattr(context, "campaign") else {}

        monthly = self._estimate_monthly_revenue(campaign)
        organic_revenue = monthly["total"] - monthly.get("paid_traffic", 0)

        # Get paid traffic results from the last cycle (if any)
        paid_spend = float(campaign.get("paid_traffic_spend", 0))
        paid_revenue = float(monthly.get("paid_traffic", 0))

        # Record cycle results in flywheel state
        self.flywheel.record_cycle(organic_revenue, paid_spend, paid_revenue)

        # Calculate flywheel budget for next cycle
        flywheel_budget = self.flywheel.get_flywheel_budget(organic_revenue)

        phase_info = self.flywheel.get_phase_info()
        state = self.flywheel._state
        months_paid = flywheel_budget["months_paid_active"]

        # Build decision
        threshold = self.config["min_monthly_revenue"]
        can_activate = organic_revenue >= threshold

        if (
            can_activate
            and organic_revenue >= threshold
            and flywheel_budget["budget"] > 0
        ):
            decision = {
                "activate": True,
                "reason": (
                    f"Flywheel Fase {self.flywheel.phase} — {phase_info['name']}: "
                    f"Receita R${organic_revenue:.2f}, "
                    f"Reinvestindo {flywheel_budget['reinvest_pct']}% "
                    f"(R${flywheel_budget['daily_budget']:.2f}/dia, "
                    f"R${flywheel_budget['budget']:.2f}/mes)"
                ),
                "budget": flywheel_budget["daily_budget"],
                "monthly_budget": round(flywheel_budget["budget"], 2),
                "confidence": min(1.0, months_paid / 6),
                "phase": self.flywheel.phase,
                "phase_name": phase_info["name"],
                "flywheel_bonus": flywheel_budget["flywheel_bonus"],
                "reinvest_pct": flywheel_budget["reinvest_pct"],
            }
            if not state.get("active"):
                log.info(
                    "flywheel_activated",
                    phase=self.flywheel.phase,
                    budget=flywheel_budget["budget"],
                )
                state["active"] = True
        else:
            decision = {
                "activate": False,
                "reason": (
                    f"Flywheel Fase {self.flywheel.phase} — {phase_info['name']}: "
                    f"Receita R${organic_revenue:.2f}/{threshold:.2f}. "
                    + (
                        f"Budget R${flywheel_budget['budget']:.2f} abaixo do minimo."
                        if flywheel_budget["budget"] == 0
                        else ""
                    )
                ),
                "budget": 0.0,
                "monthly_budget": 0.0,
                "confidence": 0.0,
                "phase": self.flywheel.phase,
                "phase_name": phase_info["name"],
                "flywheel_bonus": 0,
                "reinvest_pct": flywheel_budget["reinvest_pct"],
            }

        output = {
            "monthly_revenue": monthly,
            "organic_revenue": organic_revenue,
            "threshold": threshold,
            "decision": decision,
            "flywheel": {
                "phase": self.flywheel.phase,
                "phase_name": phase_info["name"],
                "phase_desc": phase_info["desc"],
                "active": state.get("active", False),
                "flywheel_active": state.get("flywheel_active", False),
                "months_paid_active": months_paid,
                "total_organic": round(state.get("total_organic_revenue", 0), 2),
                "total_paid_spend": round(state.get("total_paid_spend", 0), 2),
                "total_paid_revenue": round(state.get("total_paid_revenue", 0), 2),
                "total_paid_profit": round(state.get("total_paid_profit", 0), 2),
                "last_roas": round(state["roas_history"][-1]["roas"], 2)
                if state.get("roas_history")
                else 0,
                "cycle_count": state.get("cycle_count", 0),
                "reinvest_percentage": flywheel_budget["reinvest_pct"],
                "flywheel_bonus": flywheel_budget["flywheel_bonus"],
            },
            "next_steps": (
                [
                    f"🔄 FLYWHEEL FASE {self.flywheel.phase} — {phase_info['name']}",
                    f"  {phase_info['desc']}",
                    f"  Orcamento: R$ {flywheel_budget['daily_budget']:.2f}/dia (R$ {flywheel_budget['budget']:.2f}/mes)",
                    f"  Bonus flywheel: R$ {flywheel_budget['flywheel_bonus']:.2f}",
                    f"  ROAS target: {self.flywheel.get_roas_target():.1f}x",
                ]
                if decision["activate"]
                else [
                    f"⏳ Flywheel Fase {self.flywheel.phase} — {phase_info['name']}",
                    f"  {phase_info['desc']}",
                    f"  Receita organica: R$ {organic_revenue:.2f}/mes",
                    f"  Proxima fase em: R$ {max(0, self.flywheel.PHASES.get(self.flywheel.phase + 1, {}).get('min_revenue', 0) - organic_revenue):.2f}/mes",
                ]
                if self.flywheel.phase > 0
                else [
                    f"🏗️ CONSTRUINDO BASE — Fase {self.flywheel.phase}: {phase_info['name']}",
                    f"  {phase_info['desc']}",
                    f"  Ativar trafego pago em: R$ {max(0, threshold - organic_revenue):.2f}/mes de receita",
                ]
            ),
        }

        finished_at = datetime.now(timezone.utc).isoformat()
        trace = AgentTrace(
            agent=self.name,
            step_id="revenue_monitor",
            status="success",
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=int(
                (
                    datetime.fromisoformat(finished_at)
                    - datetime.fromisoformat(started_at)
                ).total_seconds()
                * 1000
            ),
            thread_name="main",
            notes=[decision["reason"]],
            metadata=output,
        )
        return AgentResult(
            agent=self.name, status="success", output=output, trace=trace
        )
