from __future__ import annotations

import json
from pathlib import Path
import unittest

from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.agents.orchestrator import CampaignOrchestrator


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "workflows" / "campaign_cycle.json"
CONTEXT = ROOT / "examples" / "orchestrator_context.json"


class TestOrchestrator(unittest.TestCase):
    def test_orchestrator_produces_ready_plan(self) -> None:
        payload = json.loads(CONTEXT.read_text(encoding="utf-8"))
        result = CampaignOrchestrator(workflow_path=WORKFLOW).run(
            CampaignContext.from_mapping(payload)
        )
        self.assertEqual(result.status, "success")
        self.assertEqual(result.output["output"]["status"], "ready")
        self.assertEqual(
            set(result.output["step_results"].keys()),
            {
                "analytics",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
            },
        )
        self.assertEqual(
            result.output["output"]["source_steps"],
            [
                "analytics",
                "compliance",
                "memory_lookup",
                "optimization",
                "execution_planning",
            ],
        )

    def test_compliance_block_changes_plan_status(self) -> None:
        payload = json.loads(CONTEXT.read_text(encoding="utf-8"))
        payload["campaign"]["headline"] = "Guaranteed income now"
        payload["policy"]["restricted_terms"] = ["guaranteed income"]
        result = CampaignOrchestrator(workflow_path=WORKFLOW).run(
            CampaignContext.from_mapping(payload)
        )
        self.assertEqual(
            result.output["step_results"]["compliance"]["output"]["status"], "block"
        )
        self.assertEqual(result.output["output"]["status"], "blocked")
