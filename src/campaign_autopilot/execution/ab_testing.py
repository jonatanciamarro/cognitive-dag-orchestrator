"""AB Testing Engine — backward-compat shim."""
from .orchestrator import ABTestingEngine, ABTest, HEADLINE_VARIANTS
__all__ = ["ABTestingEngine", "ABTest", "HEADLINE_VARIANTS"]
