import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "configs" / "opt_in_cycle.json").read_text(encoding="utf-8")
)
RUN = json.loads(
    (ROOT / "examples" / "opt_in_cycle_run.json").read_text(encoding="utf-8")
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


def policy_gate(run, policy):
    if policy["requires_explicit_opt_in"] and not run.get("opt_in", False):
        return False, "missing_explicit_opt_in"
    if policy["requires_consent_record"] and not run.get("consent_recorded", False):
        return False, "missing_consent_record"
    if policy["requires_compliance_pass"] and run.get("compliance_status") != "pass":
        return False, "compliance_failed"
    return True, "pass"


def execute_workflow(config, run):
    history = []

    history.append("load_inputs")

    ok, reason = policy_gate(run, config["policy"])
    if not ok:
        return {
            "state": "blocked",
            "blocked_at": "consent_gate",
            "reason": reason,
            "history": history,
        }

    history.append("consent_gate")

    ok, reason = evaluate_metrics(run["metrics"], config["metrics"])
    if not ok:
        return {
            "state": "blocked",
            "blocked_at": "metrics_check",
            "reason": reason,
            "history": history,
        }

    history.append("metrics_check")

    history.append("policy_review")
    history.append("generate_plan")

    if run.get("approval_status") != "approved":
        return {
            "state": "waiting_approval",
            "blocked_at": "await_approval",
            "history": history,
        }

    history.append("await_approval")

    if config["defaults"]["dry_run"] and run.get("execution_mode") != "execute":
        history.append("dry_run")
        history.append("record_memory")
        return {"state": "dry_run_complete", "history": history}

    if run.get("execution_mode") != "execute":
        return {
            "state": "waiting_execution",
            "blocked_at": "execute",
            "history": history,
        }

    history.append("execute")
    if config["defaults"]["record_memory"]:
        history.append("record_memory")

    return {"state": "executed", "history": history}


class TestWorkflow(unittest.TestCase):
    def test_approved_run_executes_full_path(self):
        result = execute_workflow(CONFIG, RUN)
        self.assertEqual(result["state"], "executed")
        self.assertEqual(
            result["history"],
            [
                "load_inputs",
                "consent_gate",
                "metrics_check",
                "policy_review",
                "generate_plan",
                "await_approval",
                "execute",
                "record_memory",
            ],
        )

    def test_missing_opt_in_stops_before_optimization(self):
        denied = dict(RUN)
        denied["opt_in"] = False
        result = execute_workflow(CONFIG, denied)
        self.assertEqual(result["state"], "blocked")
        self.assertEqual(result["blocked_at"], "consent_gate")
        self.assertNotIn("generate_plan", result["history"])

    def test_dry_run_path_skips_execution(self):
        dry_run = dict(RUN)
        dry_run["execution_mode"] = "dry_run"
        result = execute_workflow(CONFIG, dry_run)
        self.assertEqual(result["state"], "dry_run_complete")
        self.assertNotIn("execute", result["history"])
