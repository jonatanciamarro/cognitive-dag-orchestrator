from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FREE_ROOT = ROOT / "free"
CURRENT_SNAPSHOT = FREE_ROOT / "v2.0.0"
PREVIOUS_SNAPSHOT = FREE_ROOT / "v1.3.0"
LEGACY_SNAPSHOT = FREE_ROOT / "v1.0.0"


class TestFreeVariant(unittest.TestCase):
    def test_free_manifest_exists(self) -> None:
        manifest_path = FREE_ROOT / "VERSION.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "v2.0.0")
        self.assertEqual(manifest["status"], "frozen")

    def test_current_snapshot_is_present(self) -> None:
        self.assertTrue((CURRENT_SNAPSHOT / "README.md").exists())
        self.assertTrue(
            (CURRENT_SNAPSHOT / "src" / "campaign_autopilot" / "cli.py").exists()
        )
        self.assertTrue(
            (CURRENT_SNAPSHOT / "workflows" / "organic_cycle.json").exists()
        )
        self.assertTrue((CURRENT_SNAPSHOT / "configs" / "organic_cycle.json").exists())
        self.assertTrue(
            (CURRENT_SNAPSHOT / "src" / "campaign_autopilot" / "goals.py").exists()
        )
        self.assertTrue((CURRENT_SNAPSHOT / "tests" / "test_epistemic.py").exists())
        self.assertTrue((CURRENT_SNAPSHOT / "tests" / "test_goals.py").exists())
        self.assertTrue(
            (CURRENT_SNAPSHOT / "tests" / "test_meta_cognitive.py").exists()
        )
        self.assertTrue(
            (CURRENT_SNAPSHOT / "tests" / "test_workflow_runner.py").exists()
        )
        self.assertTrue(
            (CURRENT_SNAPSHOT / "src" / "campaign_autopilot" / "affiliate.py").exists()
        )
        self.assertTrue((CURRENT_SNAPSHOT / "tests" / "test_affiliate.py").exists())
        self.assertTrue(
            (CURRENT_SNAPSHOT / "workflows" / "organic_affiliate_cycle.json").exists()
        )

    def test_previous_snapshot_is_preserved(self) -> None:
        self.assertTrue((PREVIOUS_SNAPSHOT / "README.md").exists())
        self.assertTrue(
            (PREVIOUS_SNAPSHOT / "src" / "campaign_autopilot" / "cli.py").exists()
        )

    def test_legacy_snapshot_is_preserved(self) -> None:
        self.assertTrue((LEGACY_SNAPSHOT / "README.md").exists())
        self.assertTrue(
            (LEGACY_SNAPSHOT / "workflows" / "campaign_cycle.json").exists()
        )
