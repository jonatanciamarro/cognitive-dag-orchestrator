import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "configs" / "opt_in_cycle.json").read_text(encoding="utf-8")
)


def evaluate_metrics(metrics, thresholds):
    if metrics["sample_size"] < thresholds["minimum_sample_size"]:
        return False, "sample_size_below_threshold"
    if metrics["success_rate"] < thresholds["success_rate_min"]:
        return False, "success_rate_below_threshold"
    if metrics["ctr"] < thresholds["ctr_min"]:
        return False, "ctr_below_threshold"
    if metrics["cpa"] > thresholds["cpa_max"]:
        return False, "cpa_above_threshold"
    return True, "pass"


class TestMetrics(unittest.TestCase):
    def test_good_metrics_pass_thresholds(self):
        ok, reason = evaluate_metrics(
            {"sample_size": 280, "success_rate": 0.93, "ctr": 0.024, "cpa": 41.25},
            CONFIG["metrics"],
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "pass")

    def test_low_sample_size_fails(self):
        ok, reason = evaluate_metrics(
            {"sample_size": 150, "success_rate": 0.98, "ctr": 0.03, "cpa": 25.0},
            CONFIG["metrics"],
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "sample_size_below_threshold")

    def test_cpa_over_limit_fails(self):
        ok, reason = evaluate_metrics(
            {"sample_size": 300, "success_rate": 0.98, "ctr": 0.03, "cpa": 52.0},
            CONFIG["metrics"],
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "cpa_above_threshold")
