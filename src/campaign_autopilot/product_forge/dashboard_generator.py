"""Dashboard Generator — Campaign analytics dashboards."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ChartType(str, Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    METRIC = "metric"


@dataclass
class MetricCard:
    """Single KPI metric display."""

    label: str = ""
    value: str = ""
    change: Optional[str] = None
    trend: str = "neutral"  # up, down, neutral
    icon: str = ""


@dataclass
class ChartSpec:
    """Chart specification for dashboard."""

    title: str = ""
    type: ChartType = ChartType.BAR
    data: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TableSpec:
    """Data table specification."""

    title: str = ""
    headers: List[str] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class KPIRow:
    """Row of KPI metric cards."""

    metrics: List[MetricCard] = field(default_factory=list)


@dataclass
class DashboardSpec:
    """Complete dashboard specification."""

    title: str = ""
    subtitle: str = ""
    kpi_rows: List[KPIRow] = field(default_factory=list)
    charts: List[ChartSpec] = field(default_factory=list)
    tables: List[TableSpec] = field(default_factory=list)
    refresh_interval: int = 60  # seconds
    theme: str = "dark"


class DashboardGenerator:
    """Generates analytics dashboards from spec."""

    def __init__(self):
        from .artifact_generator import ArtifactGenerator

        self._engine = ArtifactGenerator()

    def generate(self, spec: DashboardSpec, output_dir: str = "output") -> str:
        """Generate and save a dashboard from spec."""
        from .artifact_generator import ArtifactSpec, ArtifactType

        campaign_data = {
            "metrics": [],
            "charts": [],
            "table": [],
        }

        # Flatten KPI rows into metrics list
        for kpi_row in spec.kpi_rows:
            for m in kpi_row.metrics:
                change = (
                    f"{'+' if m.change else ''}{m.change or ''}" if m.change else None
                )
                campaign_data["metrics"].append(
                    {
                        "label": m.label,
                        "value": m.value,
                        "change": change,
                        "trend": m.trend,
                    }
                )

        # Charts
        for c in spec.charts:
            if c.type == ChartType.BAR:
                bars = [
                    {"label": item.get("label", ""), "value": item.get("value", 0)}
                    for item in c.data
                ]
                campaign_data["charts"].append(
                    {
                        "title": c.title,
                        "type": "bar",
                        "bars": bars,
                    }
                )

        # Tables
        for t in spec.tables:
            campaign_data["table"] = t.rows

        artifact_spec = ArtifactSpec(
            type=ArtifactType.DASHBOARD,
            title=spec.title,
            description=spec.subtitle,
            campaign_data=campaign_data,
        )

        result = self._engine.generate_artifact(artifact_spec, output_dir)
        return result.file_path or ""

    def generate_campaign_dashboard(
        self,
        campaign_name: str,
        metrics: List[MetricCard],
        charts: List[ChartSpec],
        output_dir: str = "output",
    ) -> str:
        """Gera dashboard rápido para campanha."""
        spec = DashboardSpec(
            title=campaign_name,
            subtitle="Métricas em tempo real da campanha",
            kpi_rows=[KPIRow(metrics=metrics)],
            charts=charts,
        )
        return self.generate(spec, output_dir)
