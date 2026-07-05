"""External Monitor — market change detection, niche saturation analysis.

Monitora mudanças no ambiente externo que podem impactar a estratégia:
algoritmos, concorrência, comportamento do público, regulamentações.
"""

from __future__ import annotations


class MarketSignal:
    def __init__(
        self,
        source: str,
        signal_type: str,
        description: str,
        severity: str,
        recommendation: str,
    ):
        self.source = source
        self.signal_type = signal_type
        self.description = description
        self.severity = severity
        self.recommendation = recommendation

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "type": self.signal_type,
            "description": self.description,
            "severity": self.severity,
            "recommendation": self.recommendation,
        }


class NicheAnalyzer:
    def __init__(self, niche: str):
        self.niche = niche

    def analyze_saturation(
        self, competitors: int = 5, content_volume: int = 100
    ) -> dict:
        ratio = competitors / max(content_volume, 1)
        return {
            "niche": self.niche,
            "estimated_competitors": competitors,
            "content_volume": content_volume,
            "saturation_index": round(ratio * 100, 1),
            "level": "low"
            if ratio < 0.05
            else "medium"
            if ratio < 0.15
            else "high"
            if ratio < 0.3
            else "saturated",
            "recommendation": self._recommend(ratio),
        }

    def _recommend(self, ratio: float) -> str:
        if ratio > 0.3:
            return f"Nicho {self.niche} saturado. Considere sub-nicho."
        if ratio > 0.15:
            return f"Nicho {self.niche} competitivo. Diferencie-se."
        return f"Nicho {self.niche} com boa oportunidade."


class ExternalMonitor:
    @staticmethod
    def create_signal(
        source: str,
        signal_type: str,
        description: str,
        severity: str,
        recommendation: str,
    ) -> MarketSignal:
        return MarketSignal(source, signal_type, description, severity, recommendation)

    @staticmethod
    def analyze_niche(niche: str) -> NicheAnalyzer:
        return NicheAnalyzer(niche)

    @staticmethod
    def scan_external_signals(niche: str) -> list[MarketSignal]:
        signals = []
        signals.append(
            MarketSignal(
                "platform_algorithm",
                "change_risk",
                f"Possíveis mudanças no algoritmo do Google/Youtube podem impactar tráfego em {niche}",
                "medium",
                "Diversificar fontes de tráfego e focar em E-E-A-T",
            )
        )
        signals.append(
            MarketSignal(
                "market_trend",
                "opportunity",
                f"Interesse de busca por {niche} estável com tendência de crescimento",
                "low",
                "Manter produção de conteúdo consistente",
            )
        )
        signals.append(
            MarketSignal(
                "regulatory",
                "compliance",
                "Regulamentações de marketing de afiliados podem ficar mais restritivas",
                "medium",
                "Manter disclosures claros e conformidade com LGPD",
            )
        )
        signals.append(
            MarketSignal(
                "competitive",
                "threat",
                f"Novos concorrentes podem estar entrando no nicho {niche}",
                "medium",
                "Monitorar concorrência e identificar diferenciais",
            )
        )
        return signals

    @staticmethod
    def generate_monitoring_report(niche: str) -> dict:
        analyzer = NicheAnalyzer(niche)
        saturation = analyzer.analyze_saturation()
        signals = ExternalMonitor.scan_external_signals(niche)
        return {
            "niche": niche,
            "saturation_analysis": saturation,
            "external_signals": [s.to_dict() for s in signals],
            "total_signals": len(signals),
            "critical_signals": len([s for s in signals if s.severity == "high"]),
        }
