import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "configs" / "opt_in_cycle.json").read_text(encoding="utf-8")
)


def policy_gate(run, policy):
    if policy["requires_explicit_opt_in"] and not run.get("opt_in", False):
        return False, "missing_explicit_opt_in"
    if policy["requires_consent_record"] and not run.get("consent_recorded", False):
        return False, "missing_consent_record"
    if policy["requires_compliance_pass"] and run.get("compliance_status") != "pass":
        return False, "compliance_failed"
    return True, "pass"


class TestPolicy(unittest.TestCase):
    def test_missing_opt_in_blocks(self):
        ok, reason = policy_gate(
            {"opt_in": False, "consent_recorded": True, "compliance_status": "pass"},
            CONFIG["policy"],
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "missing_explicit_opt_in")

    def test_missing_consent_record_blocks(self):
        ok, reason = policy_gate(
            {"opt_in": True, "consent_recorded": False, "compliance_status": "pass"},
            CONFIG["policy"],
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "missing_consent_record")

    def test_compliance_failure_blocks(self):
        ok, reason = policy_gate(
            {"opt_in": True, "consent_recorded": True, "compliance_status": "fail"},
            CONFIG["policy"],
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "compliance_failed")

    def test_full_policy_passes(self):
        ok, reason = policy_gate(
            {"opt_in": True, "consent_recorded": True, "compliance_status": "pass"},
            CONFIG["policy"],
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "pass")
