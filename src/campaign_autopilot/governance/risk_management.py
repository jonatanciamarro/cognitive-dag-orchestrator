"""Risk Management — risk assessment, bottleneck detection, strategic risk.

Identifica riscos operacionais e estratégicos, detecta gargalos
no pipeline e gera recomendações de mitigação.
"""

from __future__ import annotations


class RiskAssessment:
    def __init__(self, domain: str):
        self.domain = domain
        self.risks: list[dict] = []
        self.score: float = 0.0

    def add_risk(
        self, risk: str, probability: float, impact: float, mitigation: str
    ) -> dict:
        risk_item = {
            "risk": risk,
            "probability": round(probability, 2),
            "impact": round(impact, 2),
            "severity": round(probability * impact, 2),
            "mitigation": mitigation,
            "domain": self.domain,
        }
        self.risks.append(risk_item)
        return risk_item

    def calculate_score(self) -> float:
        if not self.risks:
            return 0.0
        self.score = sum(r["severity"] for r in self.risks) / len(self.risks)
        return round(self.score, 2)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "risk_count": len(self.risks),
            "overall_score": self.calculate_score(),
            "critical_risks": [r for r in self.risks if r["severity"] > 0.5],
            "risks": sorted(self.risks, key=lambda r: -r["severity"]),
        }


class BottleneckDetector:
    def __init__(self, pipeline_steps: list[str]):
        self.steps = pipeline_steps
        self.latency_data: dict[str, list[float]] = {s: [] for s in pipeline_steps}

    def record_latency(self, step: str, latency_ms: float):
        if step in self.latency_data:
            self.latency_data[step].append(latency_ms)

    def detect(self) -> list[dict]:
        bottlenecks = []
        for step, latencies in self.latency_data.items():
            if not latencies:
                continue
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            if avg_latency > 10000:
                bottlenecks.append(
                    {
                        "step": step,
                        "avg_latency_ms": round(avg_latency, 1),
                        "max_latency_ms": round(max_latency, 1),
                        "severity": "critical"
                        if avg_latency > 30000
                        else "high"
                        if avg_latency > 15000
                        else "medium",
                        "recommendation": self._recommend(step, avg_latency),
                    }
                )
        return sorted(bottlenecks, key=lambda b: -b["avg_latency_ms"])

    def _recommend(self, step: str, latency: float) -> str:
        if latency > 30000:
            return f"Gargalo crítico em {step}. Considere paralelizar ou reduzir frequência."
        elif latency > 15000:
            return f"Gargalo em {step}. Verificar se há dependências desnecessárias."
        return f"{step} com latência elevada. Otimizar processamento."


class RiskManager:
    @staticmethod
    def create_assessment(domain: str) -> RiskAssessment:
        return RiskAssessment(domain)

    @staticmethod
    def assess_system_risks(niche: str, performance: dict) -> RiskAssessment:
        ra = RiskAssessment(f"system_{niche}")
        revenue = performance.get("revenue", 0)
        traffic = performance.get("traffic", 0)
        channels = performance.get("active_channels", 1)

        # Strategic risks
        if channels <= 2:
            ra.add_risk(
                "Dependência excessiva de poucos canais",
                0.6,
                0.8,
                "Expandir para pelo menos 4 canais de tráfego",
            )
        if revenue == 0:
            ra.add_risk(
                "Zero de receita — modelo de negócio não validado",
                0.7,
                1.0,
                "Priorizar conteúdo com intenção de compra e revisar ofertas",
            )
        if traffic == 0:
            ra.add_risk(
                "Zero de tráfego — conteúdo não está sendo encontrado",
                0.8,
                0.9,
                "Revisar estratégia de SEO, palavras-chave e distribuição",
            )
        ra.add_risk(
            "Mudanças no algoritmo da plataforma",
            0.5,
            0.6,
            "Diversificar plataformas e manter conteúdo de alta qualidade",
        )
        ra.add_risk(
            "Concorrência aumentando no nicho",
            0.4,
            0.5,
            "Focar em sub-nichos com menor concorrência",
        )
        ra.add_risk(
            "Dependência de tráfego orgânico sem lista de emails",
            0.3,
            0.7,
            "Priorizar captura de leads e construção de audiência proprietária",
        )
        ra.calculate_score()
        return ra

    @staticmethod
    def create_bottleneck_detector(pipeline_steps: list[str]) -> BottleneckDetector:
        return BottleneckDetector(pipeline_steps)
