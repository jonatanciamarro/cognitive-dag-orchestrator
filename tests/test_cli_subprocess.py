from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORGANIC_WORKFLOW = ROOT / "workflows" / "organic_cycle.json"
ORGANIC_CONTEXT = ROOT / "examples" / "organic_context.json"
CAMPAIGN_EVENTS = ROOT / "examples" / "campaign_events.json"


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = {
        **{k: v for k, v in vars(subprocess).items() if k == "OS"},
        **{"PYTHONPATH": str(ROOT / "src")},
    }
    # Proper way: extend current env
    import os as _os

    _env = {**_os.environ.copy(), "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "campaign_autopilot.cli", *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=_env,
    )


class TestCLISubprocess(unittest.TestCase):
    """Verify the CLI works as a subprocess (full stack integration)."""

    def test_campaign_cycle_via_subprocess(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        try:
            result = _run_cli("--events", str(CAMPAIGN_EVENTS), "--db", db_path)
            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            data = json.loads(result.stdout)
            self.assertIn("campaign_id", data)
            self.assertIn("decisions", data)
            self.assertIn("metrics", data)
            self.assertGreater(len(data["decisions"]), 0)
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_organic_cycle_via_subprocess(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        try:
            result = _run_cli(
                "--workflow",
                str(ORGANIC_WORKFLOW),
                "--context",
                str(ORGANIC_CONTEXT),
                "--db",
                db_path,
            )
            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            data = json.loads(result.stdout)
            self.assertEqual(data["agent"], "orchestrator")
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["output"]["output"]["status"], "ready")
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_missing_context_raises(self) -> None:
        result = _run_cli("--workflow", str(ORGANIC_WORKFLOW))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--context is required", result.stderr)

    def test_missing_events_raises(self) -> None:
        result = _run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--events is required", result.stderr)
