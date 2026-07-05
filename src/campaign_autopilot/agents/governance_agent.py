"""Governance Agent — delegates to governance/execution modules.

Consolidates 7 thin agent wrappers (quality_assurance, external_monitor,
risk_management, rollback_manager, performance_analytics, resource_manager,
ab_testing) into a single parameterized agent. Each wrapper was ~25 lines
following the same pattern: call a static method, wrap in AgentResult.

Saves ~120 lines and 6 files. ponytail: consolidation of 7 identical patterns.
"""

from __future__ import annotations

from typing import Any, Callable

from .base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    iso_duration_ms,
    utc_now_iso,
)


def _format_note(*parts: str) -> str:
    return ", ".join(p for p in parts if p)


def _run_quality_assurance(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.quality_assurance import QualityAssurance

    benchmarks = QualityAssurance.get_content_benchmarks()
    checks = {
        k: v.evaluate(
            {
                "min_words": 1000,
                "has_title": 1,
                "has_sections": 4,
                "keyword_density_min": 1.0,
                "keyword_density_max": 2.5,
                "min_width": 1200,
                "min_height": 630,
                "has_text": 1,
                "min_duration_sec": 30,
                "has_transitions": 1,
                "has_audio": 0,
                "has_meta_description": 1,
                "has_headings": 1,
                "keyword_in_title": 1,
                "has_internal_links": 1,
                "has_external_links": 1,
            }
        )
        for k, v in benchmarks.items()
    }
    return {
        "status": "success",
        "benchmarks_evaluated": len(checks),
        "results": checks,
        "_notes": [f"Avaliou {len(checks)} benchmarks de qualidade"],
        "_metadata": {"benchmarks": len(checks)},
    }


def _run_external_monitor(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.external_monitor import ExternalMonitor

    niche = str(ctx.campaign.get("niche", "marketing digital"))
    report = ExternalMonitor.generate_monitoring_report(niche)
    return {
        "status": "success",
        "monitoring_report": report,
        "_notes": [
            f"Sinais externos: {report['total_signals']}, Saturação: {report['saturation_analysis']['level']}"
        ],
        "_metadata": {
            "signals": report["total_signals"],
            "saturation": report["saturation_analysis"]["level"],
        },
    }


def _run_risk_management(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.risk_management import RiskManager

    niche = str(ctx.campaign.get("niche", "marketing digital"))
    perf = {
        "revenue": ctx.campaign.get("revenue", 0),
        "traffic": ctx.campaign.get("traffic", 0),
        "active_channels": 5,
    }
    ra = RiskManager.assess_system_risks(niche, perf)
    return {
        "status": "success",
        "risk_assessment": ra.to_dict(),
        "_notes": [f"Risco geral: {ra.score}", f"{len(ra.risks)} riscos identificados"],
        "_metadata": {"risks": len(ra.risks), "score": ra.score},
    }


def _run_rollback_manager(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.rollback_manager import RollbackManager

    rm = RollbackManager()
    health = rm.health_check()
    history = rm.get_history(5)
    return {
        "status": "success",
        "health": health,
        "recent_changes": history,
        "_notes": [f"Rollback health: {health['rollback_rate']}% rate"],
        "_metadata": {"total_changes": health["total_changes"]},
    }


def _run_performance_analytics(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.performance_analytics import PerformanceAnalytics

    pa = PerformanceAnalytics.generate_channel_report(
        {
            "historical": [
                {"metric": "traffic", "value": 100},
                {"metric": "traffic", "value": 150},
                {"metric": "revenue", "value": 50},
                {"metric": "revenue", "value": 80},
            ],
            "channels": {
                "blog": {"cost": 10, "revenue": 50},
                "youtube": {"cost": 20, "revenue": 80},
                "pinterest": {"cost": 5, "revenue": 30},
            },
        }
    )
    return {
        "status": "success",
        "analytics": pa,
        "_notes": ["Análise de performance concluída"],
        "_metadata": {},
    }


def _run_resource_manager(ctx: CampaignContext) -> dict[str, Any]:
    from ..governance.resource_manager import ResourceManager

    budget = ResourceManager.create_budget(
        "daily_operations", {"api_calls": 1000, "tokens": 50000, "time_minutes": 480}
    )
    queue = ResourceManager.create_queue_manager(max_concurrent=5)
    return {
        "status": "success",
        "budget": budget.to_dict(),
        "queue_status": queue.get_status(),
        "cost_estimates": {
            "generate_image": ResourceManager.estimate_cost("generate_image", {}),
            "generate_video": ResourceManager.estimate_cost("generate_video", {}),
            "seo_scrape": ResourceManager.estimate_cost("seo_scrape", {}),
        },
        "_notes": ["Gerenciamento de recursos inicializado"],
        "_metadata": {},
    }


def _run_ab_testing(ctx: CampaignContext) -> dict[str, Any]:
    from ..execution.ab_testing import ABTestingEngine

    niche = str(ctx.campaign.get("niche", "marketing digital"))
    h_variants = ABTestingEngine.generate_headline_variants(
        "marketing de afiliados", niche
    )
    cta_variants = ABTestingEngine.generate_cta_variants("Curso de Afiliados")
    test = ABTestingEngine.create_test("headline_test", h_variants[:3])
    analysis = test.analyze()
    return {
        "status": "success",
        "headline_variants": h_variants,
        "cta_variants": cta_variants,
        "test_analysis": analysis,
        "_notes": [
            f"Gerou {len(h_variants)} variantes de headline",
            f"{len(cta_variants)} variantes de CTA",
        ],
        "_metadata": {"headlines": len(h_variants), "ctas": len(cta_variants)},
    }


# Map of delegate key -> handler function
_GOVERNANCE_HANDLERS: dict[str, Callable[[CampaignContext], dict[str, Any]]] = {
    "resource_manager": _run_resource_manager,
    "quality_assurance": _run_quality_assurance,
    "risk_management": _run_risk_management,
    "external_monitor": _run_external_monitor,
    "rollback_manager": _run_rollback_manager,
    "performance_analytics": _run_performance_analytics,
    "ab_testing": _run_ab_testing,
}


class GovernanceAgent(AgentBase):
    """Single agent delegating to governance/execution modules.

    Replaces 7 thin wrappers. Usage: GovernanceAgent("quality_assurance", ...)
    """

    def __init__(self, delegate: str = "quality_assurance", **kwargs: Any) -> None:
        super().__init__(delegate, **kwargs)
        if delegate not in _GOVERNANCE_HANDLERS:
            raise ValueError(
                f"Unknown governance delegate: {delegate}. Options: {list(_GOVERNANCE_HANDLERS)}"
            )
        self._handler = _GOVERNANCE_HANDLERS[delegate]

    def run(self, context: CampaignContext) -> AgentResult:
        started = utc_now_iso()
        try:
            result = self._handler(context)
            notes = result.pop("_notes", [])
            metadata = result.pop("_metadata", {})
            status = "success"
        except Exception as e:
            result = {"status": "error", "error": str(e)}
            notes = [f"Erro: {e}"]
            metadata = {}
            status = "error"

        return AgentResult(
            agent=self.name,
            status=status,
            output=result,
            trace=AgentTrace(
                agent=self.name,
                step_id=self.name,
                status=status,
                started_at=started,
                finished_at=utc_now_iso(),
                duration_ms=iso_duration_ms(started, utc_now_iso()),
                thread_name="main",
                notes=notes,
                metadata=metadata,
            ),
        )
