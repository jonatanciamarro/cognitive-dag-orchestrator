"""Governance Module — Second-order governance enhancements.

Fills the remaining gaps in the second-order layer:
- Resource management (budget, queues, rate limits)
- Quality assurance (output validation, benchmarks)
- Risk management (assessment, bottleneck detection)
- External monitoring (market changes, niche saturation)
- Performance analytics (temporal analysis, cost/benefit)
- Automatic rollback
"""

from .resource_manager import ResourceManager, ResourceBudget, QueueManager
from .quality_assurance import QualityAssurance, QualityCheck, Benchmark
from .risk_management import RiskManager, RiskAssessment, BottleneckDetector
from .external_monitor import ExternalMonitor, MarketSignal, NicheAnalyzer
from .performance_analytics import (
    PerformanceAnalytics,
    TemporalAnalyzer,
    CostBenefitAnalyzer,
)
from .rollback_manager import RollbackManager, ChangeRecord

__all__ = [
    "ResourceManager",
    "ResourceBudget",
    "QueueManager",
    "QualityAssurance",
    "QualityCheck",
    "Benchmark",
    "RiskManager",
    "RiskAssessment",
    "BottleneckDetector",
    "ExternalMonitor",
    "MarketSignal",
    "NicheAnalyzer",
    "PerformanceAnalytics",
    "TemporalAnalyzer",
    "CostBenefitAnalyzer",
    "RollbackManager",
    "ChangeRecord",
]
