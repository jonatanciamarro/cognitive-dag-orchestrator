from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.cli import (
    _load_input,
    _load_context,
    build_parser,
    run_cycle,
    run_workflow,
)


ROOT = Path(__file__).resolve().parents[1]
ORGANIC_WORKFLOW = ROOT / "workflows" / "organic_cycle.json"
CAMPAIGN_WORKFLOW = ROOT / "workflows" / "campaign_cycle.json"
CAMPAIGN_EVENTS = ROOT / "examples" / "campaign_events.json"
ORGANIC_CONTEXT = ROOT / "examples" / "organic_context.json"
ORCHESTRATOR_CONTEXT = ROOT / "examples" / "orchestrator_context.json"


class TestCLIBuildParser(unittest.TestCase):
    def test_parser_defaults(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args([])
        self.assertEqual(parsed.db, "campaign_autopilot.sqlite3")
        self.assertIsNone(parsed.events)
        self.assertIsNone(parsed.workflow)
        self.assertIsNone(parsed.context)

    def test_parser_with_events(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["--events", "events.json", "--db", "test.db"])
        self.assertEqual(parsed.events, "events.json")
        self.assertEqual(parsed.db, "test.db")

    def test_parser_with_workflow(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["--workflow", "wf.json", "--context", "ctx.json"])
        self.assertEqual(parsed.workflow, "wf.json")
        self.assertEqual(parsed.context, "ctx.json")


class TestCLILoadInput(unittest.TestCase):
    def test_load_input_from_events_file(self) -> None:
        campaign, events, policy = _load_input(CAMPAIGN_EVENTS)
        self.assertEqual(campaign.campaign_id, "cmp_1024")
        self.assertTrue(campaign.opt_in)
        self.assertEqual(len(events), 3)
        self.assertIsNotNone(policy)

    def test_load_input_with_list_format(self) -> None:
        data = [
            {
                "campaign_id": "cmp_list",
                "kind": "impression",
                "occurred_at": "2026-06-19T00:00:00Z",
                "value": 10,
                "count": 50,
            },
            {
                "campaign_id": "cmp_list",
                "kind": "click",
                "occurred_at": "2026-06-19T00:05:00Z",
                "value": 5,
                "count": 10,
            },
        ]
        path = Path(tempfile.mktemp(suffix=".json"))
        try:
            path.write_text(json.dumps(data), encoding="utf-8")
            campaign, events, policy = _load_input(path)
            self.assertEqual(campaign.campaign_id, "cmp_list")
            self.assertEqual(len(events), 2)
        finally:
            path.unlink(missing_ok=True)

    def test_load_input_raises_on_empty_events(self) -> None:
        data = {"campaign_id": "cmp_1", "events": []}
        path = Path(tempfile.mktemp(suffix=".json"))
        try:
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                _load_input(path)
        finally:
            path.unlink(missing_ok=True)

    def test_load_input_raises_without_campaign_id(self) -> None:
        data = {
            "events": [{"kind": "impression", "occurred_at": "2026-06-19T00:00:00Z"}]
        }
        path = Path(tempfile.mktemp(suffix=".json"))
        try:
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                _load_input(path)
        finally:
            path.unlink(missing_ok=True)

    def test_load_input_list_format_infers_campaign_id(self) -> None:
        """A single-event list with campaign_id in the event should work."""
        data = [
            {
                "campaign_id": "cmp_inferred",
                "kind": "conversion",
                "occurred_at": "2026-06-19T00:00:00Z",
                "value": 50,
            },
        ]
        path = Path(tempfile.mktemp(suffix=".json"))
        try:
            path.write_text(json.dumps(data), encoding="utf-8")
            campaign, events, policy = _load_input(path)
            self.assertEqual(campaign.campaign_id, "cmp_inferred")
            self.assertEqual(len(events), 1)
        finally:
            path.unlink(missing_ok=True)


class TestCLILoadContext(unittest.TestCase):
    def test_load_context_from_organic_file(self) -> None:
        context = _load_context(ORGANIC_CONTEXT)
        self.assertEqual(context.campaign["campaign_id"], "org_1001")
        self.assertEqual(context.campaign["objective"], "organic lead growth")
        self.assertIn("seo", context.campaign["channels"])
        self.assertEqual(len(context.memory), 1)

    def test_load_context_from_orchestrator_file(self) -> None:
        context = _load_context(ORCHESTRATOR_CONTEXT)
        self.assertEqual(context.campaign["campaign_id"], "cmp_1024")
        self.assertEqual(len(context.signals.get("daily_spend", [])), 3)

    def test_load_context_raises_on_list(self) -> None:
        path = Path(tempfile.mktemp(suffix=".json"))
        try:
            path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            with self.assertRaises(ValueError):
                _load_context(path)
        finally:
            path.unlink(missing_ok=True)


class TestCLIRunCycle(unittest.TestCase):
    def test_run_cycle_produces_decision_plan(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        try:
            result = run_cycle(str(CAMPAIGN_EVENTS), str(db_path))
            self.assertIn("campaign_id", result)
            self.assertIn("decisions", result)
            self.assertIn("metrics", result)
            self.assertGreater(len(result["decisions"]), 0)
        finally:
            db_path.unlink(missing_ok=True)

    def test_run_cycle_persists_to_db(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        try:
            run_cycle(str(CAMPAIGN_EVENTS), str(db_path))
            from campaign_autopilot.memory import MemoryStore

            with MemoryStore(db_path) as store:
                campaign = store.get_campaign("cmp_1024")
                self.assertIsNotNone(campaign)
                events = store.list_events("cmp_1024")
                self.assertEqual(len(events), 3)
        finally:
            db_path.unlink(missing_ok=True)


class TestCLIRunWorkflow(unittest.TestCase):
    def test_run_workflow_with_campaign_cycle(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        try:
            result = run_workflow(
                str(ORCHESTRATOR_CONTEXT),
                str(CAMPAIGN_WORKFLOW),
                str(db_path),
            )
            # run_workflow returns AgentResult.to_dict():
            # result["output"] is the WorkflowRunResult.to_dict()
            self.assertEqual(result["agent"], "orchestrator")
            self.assertEqual(result["status"], "success")
            wr = result["output"]
            self.assertEqual(wr["status"], "success")
            self.assertIn("step_results", wr)
            self.assertEqual(
                set(wr["step_results"].keys()),
                {
                    "analytics",
                    "compliance",
                    "memory_lookup",
                    "optimization",
                    "execution_planning",
                },
            )
        finally:
            db_path.unlink(missing_ok=True)

    def test_run_workflow_with_organic_cycle(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        try:
            result = run_workflow(
                str(ORGANIC_CONTEXT),
                str(ORGANIC_WORKFLOW),
                str(db_path),
            )
            self.assertEqual(result["agent"], "orchestrator")
            self.assertEqual(result["status"], "success")
            wr = result["output"]
            self.assertEqual(wr["status"], "success")
            self.assertIn("step_results", wr)
            self.assertEqual(
                set(wr["step_results"].keys()),
                {
                    "research",
                    "compliance",
                    "memory_lookup",
                    "optimization",
                    "execution_planning",
                },
            )
        finally:
            db_path.unlink(missing_ok=True)
