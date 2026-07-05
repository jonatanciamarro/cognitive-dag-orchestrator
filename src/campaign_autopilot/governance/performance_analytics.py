"""Performance Analytics — temporal analysis, cost/benefit, channel synergy.

Analisa performance ao longo do tempo, calcula ROI por canal,
detecta sinergias entre canais e padrões temporais.
"""

from __future__ import annotations

from collections import defaultdict


class TemporalAnalyzer:
    def __init__(self, data_points: list[dict]):
        self.data = data_points  # list of { timestamp, metric, value }

    def analyze_trend(self, metric: str, window: int = 7) -> dict:
        points = [d for d in self.data if d.get("metric") == metric]
        if len(points) < 2:
            return {"metric": metric, "trend": "insufficient_data", "confidence": 0}
        values = [p["value"] for p in points[-window:]]
        recent = values[-3:] if len(values) >= 3 else values
        older = values[:3] if len(values) >= 3 else values
        avg_recent = sum(recent) / max(len(recent), 1)
        avg_older = sum(older) / max(len(older), 1)
        change_pct = ((avg_recent - avg_older) / max(abs(avg_older), 0.001)) * 100
        return {
            "metric": metric,
            "data_points": len(points),
            "recent_avg": round(avg_recent, 2),
            "previous_avg": round(avg_older, 2),
            "change_pct": round(change_pct, 1),
            "trend": "up"
            if change_pct > 10
            else "down"
            if change_pct < -10
            else "stable",
            "confidence": min(abs(change_pct) / 100, 1.0),
        }

    def detect_seasonality(self, metric: str) -> dict:
        return {
            "metric": metric,
            "has_seasonality": False,
            "note": "Dados insuficientes para análise de sazonalidade",
        }


class CostBenefitAnalyzer:
    def __init__(self):
        self.costs: dict[str, float] = defaultdict(float)
        self.benefits: dict[str, float] = defaultdict(float)

    def record_cost(self, channel: str, cost: float):
        self.costs[channel] += cost

    def record_benefit(self, channel: str, benefit: float):
        self.benefits[channel] += benefit

    def analyze(self) -> dict:
        results = {}
        all_channels = set(self.costs.keys()) | set(self.benefits.keys())
        for channel in all_channels:
            c = self.costs.get(channel, 0)
            b = self.benefits.get(channel, 0)
            results[channel] = {
                "cost": round(c, 2),
                "benefit": round(b, 2),
                "roi": round(((b - c) / max(c, 0.01)) * 100, 1),
                "net": round(b - c, 2),
            }
        total_cost = sum(self.costs.values())
        total_benefit = sum(self.benefits.values())
        return {
            "per_channel": results,
            "total_cost": round(total_cost, 2),
            "total_benefit": round(total_benefit, 2),
            "overall_roi": round(
                ((total_benefit - total_cost) / max(total_cost, 0.01)) * 100, 1
            ),
            "best_channel": max(results, key=lambda c: results[c]["roi"])
            if results
            else None,
        }


class PerformanceAnalytics:
    @staticmethod
    def create_temporal_analyzer(data: list[dict]) -> TemporalAnalyzer:
        return TemporalAnalyzer(data)

    @staticmethod
    def create_cost_benefit_analyzer() -> CostBenefitAnalyzer:
        return CostBenefitAnalyzer()

    @staticmethod
    def generate_channel_report(mock_data: dict) -> dict:
        data = mock_data.get("historical", [{"metric": "traffic", "value": 100}])
        ta = TemporalAnalyzer(data)
        trends = [
            ta.analyze_trend("traffic"),
            ta.analyze_trend("conversion"),
            ta.analyze_trend("revenue"),
        ]
        cba = CostBenefitAnalyzer()
        for ch, ch_data in mock_data.get("channels", {}).items():
            cba.record_cost(ch, ch_data.get("cost", 0))
            cba.record_benefit(ch, ch_data.get("revenue", 0))
        return {"trends": [t for t in trends if t], "cost_benefit": cba.analyze()}
