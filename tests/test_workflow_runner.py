from __future__ import annotations

import unittest

from campaign_autopilot.agents.base import (
    AgentBase,
    AgentResult,
    AgentTrace,
    CampaignContext,
    utc_now_iso,
)
from campaign_autopilot.workflow import (
    WorkflowRunner,
    WorkflowSpec,
    WorkflowStepSpec,
)


class _SimpleAgent(AgentBase):
    """A test agent that returns a fixed output."""

    def __init__(self, name: str, output: object = None, fail: bool = False) -> None:
        super().__init__(name)
        self._output = output or {"status": "ok"}
        self._fail = fail

    def run(self, context: CampaignContext) -> AgentResult:
        started_at = utc_now_iso()
        trace = AgentTrace(
            agent=self.name,
            step_id=self.name,
            status="failed" if self._fail else "success",
            started_at=started_at,
            finished_at=started_at,
            duration_ms=0,
            thread_name="test",
            error="Intentional failure" if self._fail else None,
        )
        return AgentResult(
            agent=self.name,
            status="failed" if self._fail else "success",
            output=self._output,
            trace=trace,
        )


class TestWorkflowRunner(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = WorkflowRunner(max_workers=2)
        self.context = CampaignContext(campaign={"campaign_id": "test"})

    def test_single_step_workflow(self) -> None:
        spec = WorkflowSpec(
            name="single",
            steps=[
                WorkflowStepSpec(id="step1", agent="test_agent"),
            ],
        )
        registry = {"test_agent": _SimpleAgent("test_agent", {"done": True})}
        result = self.runner.run(spec, self.context, registry)

        self.assertEqual(result.workflow_name, "single")
        self.assertEqual(result.status, "success")
        self.assertIn("step1", result.step_results)
        self.assertEqual(result.step_results["step1"].output, {"done": True})
        self.assertEqual(result.step_results["step1"].status, "success")

    def test_sequential_steps(self) -> None:
        spec = WorkflowSpec(
            name="sequential",
            steps=[
                WorkflowStepSpec(id="a", agent="agent_a"),
                WorkflowStepSpec(id="b", agent="agent_b", depends_on=["a"]),
                WorkflowStepSpec(id="c", agent="agent_c", depends_on=["b"]),
            ],
        )
        registry = {
            "agent_a": _SimpleAgent("agent_a", {"step": "a"}),
            "agent_b": _SimpleAgent("agent_b", {"step": "b"}),
            "agent_c": _SimpleAgent("agent_c", {"step": "c"}),
        }
        result = self.runner.run(spec, self.context, registry)

        self.assertEqual(result.status, "success")
        self.assertEqual(
            list(result.step_results.keys()),
            ["a", "b", "c"],
        )
        self.assertEqual(result.step_results["a"].output["step"], "a")
        self.assertEqual(result.step_results["c"].output["step"], "c")

    def test_parallel_steps_run(self) -> None:
        """Steps without dependencies should execute (no deadlock)."""
        spec = WorkflowSpec(
            name="parallel",
            max_workers=4,
            steps=[
                WorkflowStepSpec(id="x", agent="agent_x"),
                WorkflowStepSpec(id="y", agent="agent_y"),
                WorkflowStepSpec(id="z", agent="agent_z"),
            ],
        )
        registry = {
            "agent_x": _SimpleAgent("agent_x"),
            "agent_y": _SimpleAgent("agent_y"),
            "agent_z": _SimpleAgent("agent_z"),
        }
        result = self.runner.run(spec, self.context, registry)

        self.assertEqual(result.status, "success")
        self.assertEqual(set(result.step_results.keys()), {"x", "y", "z"})

    def test_diamond_dependency(self) -> None:
        """A -> B, C -> D (diamond shape)."""
        spec = WorkflowSpec(
            name="diamond",
            steps=[
                WorkflowStepSpec(id="a", agent="agent_a"),
                WorkflowStepSpec(id="b", agent="agent_b", depends_on=["a"]),
                WorkflowStepSpec(id="c", agent="agent_c", depends_on=["a"]),
                WorkflowStepSpec(id="d", agent="agent_d", depends_on=["b", "c"]),
            ],
        )
        registry = {
            f"agent_{ch}": _SimpleAgent(f"agent_{ch}") for ch in ("a", "b", "c", "d")
        }
        result = self.runner.run(spec, self.context, registry)
        self.assertEqual(result.status, "success")
        self.assertEqual(set(result.step_results.keys()), {"a", "b", "c", "d"})

    def test_agent_not_found(self) -> None:
        spec = WorkflowSpec(
            name="missing",
            steps=[
                WorkflowStepSpec(id="s1", agent="nonexistent"),
            ],
        )
        result = self.runner.run(spec, self.context, {})
        self.assertEqual(result.step_results["s1"].status, "failed")
        self.assertIn("Unknown agent", result.step_results["s1"].error or "")

    def test_agent_raises_exception(self) -> None:
        class _CrashAgent(AgentBase):
            def __init__(self) -> None:
                super().__init__("crash")

            def run(self, context: CampaignContext) -> AgentResult:
                raise RuntimeError("Something went wrong")

        spec = WorkflowSpec(
            name="crash",
            steps=[
                WorkflowStepSpec(id="s1", agent="crash"),
            ],
        )
        result = self.runner.run(spec, self.context, {"crash": _CrashAgent()})
        self.assertEqual(result.step_results["s1"].status, "failed")
        self.assertIn("Something went wrong", result.step_results["s1"].error or "")

    def test_step_result_trace_populated(self) -> None:
        spec = WorkflowSpec(
            name="trace_check",
            steps=[
                WorkflowStepSpec(id="s1", agent="ta"),
            ],
        )
        registry = {"ta": _SimpleAgent("ta", {"result": 42})}
        result = self.runner.run(spec, self.context, registry)
        sr = result.step_results["s1"]
        self.assertGreaterEqual(sr.duration_ms, 0)
        self.assertEqual(sr.thread_name, "test")
        self.assertEqual(sr.dependencies, [])

    def test_callable_in_registry(self) -> None:
        def custom_agent(context: CampaignContext) -> AgentResult:
            return AgentResult(
                agent="custom", status="success", output={"custom": True}
            )

        spec = WorkflowSpec(
            name="callable",
            steps=[
                WorkflowStepSpec(id="s1", agent="custom"),
            ],
        )
        result = self.runner.run(spec, self.context, {"custom": custom_agent})
        self.assertEqual(result.step_results["s1"].output, {"custom": True})

    def test_callable_returns_dict(self) -> None:
        """A callable that returns a plain dict (not AgentResult) should be wrapped."""

        def plain_dict_agent(context: CampaignContext) -> dict:
            return {"plain": True}

        spec = WorkflowSpec(
            name="plain_dict",
            steps=[
                WorkflowStepSpec(id="s1", agent="plain_dict"),
            ],
        )
        result = self.runner.run(spec, self.context, {"plain_dict": plain_dict_agent})
        self.assertEqual(result.step_results["s1"].output, {"plain": True})

    def test_final_step_output_is_returned(self) -> None:
        spec = WorkflowSpec(
            name="final_output",
            steps=[
                WorkflowStepSpec(id="s1", agent="ta1"),
                WorkflowStepSpec(id="s2", agent="ta2", depends_on=["s1"]),
            ],
        )
        registry = {
            "ta1": _SimpleAgent("ta1", {"phase": "one"}),
            "ta2": _SimpleAgent("ta2", {"phase": "two"}),
        }
        result = self.runner.run(spec, self.context, registry)
        self.assertEqual(result.output, {"phase": "two"})

    def test_load_spec_from_path(self) -> None:
        from pathlib import Path
        import json
        import tempfile

        spec_data = {
            "name": "loaded",
            "steps": [{"id": "s1", "agent": "ta"}],
        }
        path = Path(tempfile.mktemp(suffix=".json"))
        try:
            path.write_text(json.dumps(spec_data), encoding="utf-8")
            spec = self.runner.load_spec(path)
            self.assertEqual(spec.name, "loaded")
            self.assertEqual(len(spec.steps), 1)
        finally:
            path.unlink(missing_ok=True)
