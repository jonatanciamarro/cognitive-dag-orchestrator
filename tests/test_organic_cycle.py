from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "organic_cycle.json"
RUN_PATH = ROOT / "examples" / "organic_content_run.json"
WORKFLOW_PATH = ROOT / "workflows" / "organic_cycle.json"
DOC_PATH = ROOT / "examples" / "organic_cycle.md"


class TestOrganicCycle(unittest.TestCase):
    def test_artifacts_exist(self) -> None:
        self.assertTrue(CONFIG_PATH.exists())
        self.assertTrue(RUN_PATH.exists())
        self.assertTrue(WORKFLOW_PATH.exists())
        self.assertTrue(DOC_PATH.exists())

    def test_config_example_and_workflow_are_consistent(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        run = json.loads(RUN_PATH.read_text(encoding="utf-8"))
        workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

        self.assertEqual(config["mode"], "organic_only")
        self.assertEqual(
            config["defaults"],
            {"dry_run": True, "require_approval": True, "record_memory": True},
        )
        self.assertTrue(config["policy"]["requires_explicit_opt_in"])
        self.assertTrue(config["policy"]["requires_consent_record"])
        self.assertTrue(config["policy"]["requires_compliance_pass"])
        self.assertTrue(config["policy"]["allow_execution_only_after_approval"])
        self.assertTrue(config["policy"]["no_paid_media"])
        self.assertEqual(config["workflow"]["states"][-1], "approval")
        self.assertIn("seo", config["channels"])
        self.assertIn("referrals", config["channels"])

        self.assertTrue(run["opt_in"])
        self.assertTrue(run["consent_recorded"])
        self.assertEqual(run["compliance_status"], "pass")
        self.assertEqual(run["approval_status"], "approved")
        self.assertEqual(run["execution_mode"], "execute")
        self.assertEqual(run["constraints"]["allowed_audience"], "opt_in_only")
        self.assertEqual(run["constraints"]["bid_change_limit_pct"], 0)
        self.assertEqual(
            run["constraints"]["channels"], ["seo", "community", "newsletter"]
        )

        self.assertEqual(workflow["name"], "organic_cycle")
        self.assertEqual(workflow["max_workers"], 4)
        self.assertEqual(
            [step["id"] for step in workflow["steps"]],
            [
                "research",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
            ],
        )
        self.assertEqual(
            workflow["steps"][3]["depends_on"],
            ["research", "compliance", "memory_lookup"],
        )
        self.assertEqual(workflow["steps"][4]["depends_on"], ["optimization"])

        self.assertTrue(
            set(run["constraints"]["channels"]).issubset(set(config["channels"]))
        )
        self.assertEqual(
            run["notes"],
            "Representative organic cycle with opt-in capture and no paid media.",
        )
