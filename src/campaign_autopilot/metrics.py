from __future__ import annotations

from typing import Iterable

from .models import Event, Metrics


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def calculate_metrics(events: Iterable[Event]) -> Metrics:
    impressions = 0
    clicks = 0
    conversions = 0
    spend = 0.0
    revenue = 0.0

    for event in events:
        kind = event.kind.lower()
        if kind == "impression":
            impressions += event.count
            spend += event.value
        elif kind == "click":
            clicks += event.count
            spend += event.value
        elif kind == "conversion":
            conversions += event.count
            revenue += event.value
            spend += event.metadata.get("spend", 0.0)
        elif kind == "spend":
            spend += event.value
        elif kind == "revenue":
            revenue += event.value

    ctr = _safe_div(clicks, impressions)
    cvr = _safe_div(conversions, clicks)
    cpa = _safe_div(spend, conversions) if conversions else None
    roas = _safe_div(revenue, spend) if spend else None
    return Metrics(
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        spend=round(spend, 6),
        revenue=round(revenue, 6),
        ctr=ctr,
        cvr=cvr,
        cpa=cpa,
        roas=roas,
    )


def apply_anomaly_flags(
    metrics: Metrics,
    *,
    min_impressions: int = 100,
    min_clicks: int = 25,
    min_ctr: float = 0.02,
    min_cvr: float = 0.02,
    max_cpa: float | None = None,
    min_roas: float | None = None,
) -> Metrics:
    flags: list[str] = []
    if metrics.impressions < min_impressions:
        flags.append("low_sample_impressions")
    if metrics.clicks < min_clicks:
        flags.append("low_sample_clicks")
    if metrics.impressions >= min_impressions and metrics.ctr < min_ctr:
        flags.append("low_ctr")
    if metrics.clicks >= min_clicks and metrics.cvr < min_cvr:
        flags.append("low_cvr")
    if metrics.conversions == 0 and metrics.clicks >= min_clicks:
        flags.append("no_conversions")
    if max_cpa is not None and metrics.cpa is not None and metrics.cpa > max_cpa:
        flags.append("high_cpa")
    if min_roas is not None and metrics.roas is not None and metrics.roas < min_roas:
        flags.append("low_roas")
    if metrics.spend > 0 and metrics.revenue == 0 and metrics.clicks >= min_clicks:
        flags.append("spend_without_return")

    metrics.anomaly_flags = list(dict.fromkeys(flags))
    return metrics
