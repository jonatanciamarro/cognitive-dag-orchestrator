from __future__ import annotations

import unittest
import sqlite3
import tempfile
from pathlib import Path

from campaign_autopilot.feedback import OutcomeStore
from campaign_autopilot.semantic_memory import SemanticMemoryStore


class TestOutcomeStore(unittest.TestCase):
    """Directive 3 — Feedback Loop Protocol."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(
            self._tmp.name, check_same_thread=False, isolation_level=None
        )
        self._conn.row_factory = sqlite3.Row
        self.store = OutcomeStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    # ── Expected outcome recording ─────────────────────────────────────

    def test_record_expected(self) -> None:
        oid = self.store.record_expected(
            cycle_id="cycle_001",
            expected_outcome={"status": "executed", "action_count": 3},
            source_step_id="execution_planning",
        )
        feedback = self.store.get_feedback(oid)
        assert feedback is not None
        self.assertEqual(feedback["cycle_id"], "cycle_001")
        self.assertIn("expected_outcome", feedback)

    def test_get_cycle_feedback(self) -> None:
        self.store.record_expected("cycle_001", {"status": "ready"})
        self.store.record_expected("cycle_001", {"status": "approved"})
        self.store.record_expected("cycle_002", {"status": "ready"})
        results = self.store.get_cycle_feedback("cycle_001")
        self.assertEqual(len(results), 2)

    # ── Actual outcome recording with delta ────────────────────────────

    def test_record_actual_computes_delta(self) -> None:
        oid = self.store.record_expected(
            "cycle_001",
            {"cpa": 5.0, "conversions": 100, "ctr": 2.0},
        )
        result = self.store.record_actual(
            oid,
            {"cpa": 3.5, "conversions": 120, "ctr": 2.5},
        )
        self.assertIn("delta", result)
        delta = result["delta"]
        self.assertAlmostEqual(delta["cpa"], -1.5)  # improved (lower)
        self.assertAlmostEqual(delta["conversions"], 20)  # improved (higher)
        self.assertAlmostEqual(delta["ctr"], 0.5)  # improved (higher)

    def test_record_actual_success_evaluation(self) -> None:
        oid = self.store.record_expected(
            "cycle_001",
            {"cpa": 5.0, "conversions": 100},
        )
        result = self.store.record_actual(
            oid,
            {"cpa": 3.0, "conversions": 150},
        )
        self.assertTrue(result["success"])

    def test_record_actual_failure_evaluation(self) -> None:
        oid = self.store.record_expected(
            "cycle_001",
            {"cpa": 3.0, "conversions": 100},
        )
        result = self.store.record_actual(
            oid,
            {"cpa": 8.0, "conversions": 50},
        )
        self.assertFalse(result["success"])

    def test_record_actual_missing_outcome(self) -> None:
        result = self.store.record_actual("nonexistent", {"cpa": 5.0})
        self.assertIn("error", result)

    def test_record_actual_lessons_extracted(self) -> None:
        oid = self.store.record_expected(
            "cycle_001",
            {"cpa": 10.0, "ctr": 1.5},
        )
        result = self.store.record_actual(
            oid,
            {"cpa": 7.0, "ctr": 2.0},
        )
        self.assertIn("lessons", result)
        lessons = result["lessons"]
        self.assertGreater(len(lessons), 0)
        for lesson in lessons:
            self.assertIn("improved", lesson)

    def test_record_actual_missing_expected_fields(self) -> None:
        """When actual has fields not in expected, delta should handle gracefully."""
        oid = self.store.record_expected("cycle_001", {"cpa": 5.0})
        result = self.store.record_actual(
            oid,
            {"cpa": 4.0, "revenue": 1000},
        )
        self.assertIn("delta", result)
        self.assertIn("revenue", result["delta"])

    # ── Feed lessons to semantic memory ────────────────────────────────

    def test_feed_lessons_to_semantic_memory(self) -> None:
        sem = SemanticMemoryStore(self._conn)

        # Record an outcome with known delta
        oid = self.store.record_expected(
            "cycle_001",
            {"cpa": 10.0, "ctr": 1.5},
        )
        self.store.record_actual(oid, {"cpa": 7.0, "ctr": 2.0})

        # Feed to semantic memory
        claim_ids = self.store.feed_lessons_to_semantic_memory(
            oid,
            sem,
            cycle_id="cycle_001",
        )
        self.assertGreater(len(claim_ids), 0)

        # Verify claims exist
        feedback_concept = sem.find_concept("feedback_lessons", "knowledge")
        assert feedback_concept is not None
        claims = sem.query_claims(subject=feedback_concept["concept_id"])
        self.assertGreaterEqual(len(claims), 1)


class TestOntologySnapshotAutomation(unittest.TestCase):
    """Directive 4 — Ontology versioning automation."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(
            self._tmp.name, check_same_thread=False, isolation_level=None
        )
        self._conn.row_factory = sqlite3.Row
        self.sem = SemanticMemoryStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_snapshot_includes_registered_concepts(self) -> None:
        self.sem.register_concept("channel_test", "channel", "Test channel")
        self.sem.snapshot_ontology("test_v1")
        snapshot = self.sem.get_ontology_version("test_v1")
        assert snapshot is not None
        names = [c["name"] for c in snapshot["concepts_snapshot"]]
        self.assertIn("channel_test", names)

    def test_multiple_snapshots_preserved(self) -> None:
        self.sem.register_concept("c1", "ns1")
        self.sem.snapshot_ontology("v1")
        self.sem.register_concept("c2", "ns2")
        self.sem.snapshot_ontology("v2")

        v1 = self.sem.get_ontology_version("v1")
        v2 = self.sem.get_ontology_version("v2")
        assert v1 is not None and v2 is not None

        v1_names = [c["name"] for c in v1["concepts_snapshot"]]
        v2_names = [c["name"] for c in v2["concepts_snapshot"]]
        self.assertIn("c1", v1_names)
        self.assertIn("c1", v2_names)  # c1 persists
        self.assertIn("c2", v2_names)  # c2 is new
        self.assertNotIn("c2", v1_names)  # c2 wasn't in v1

    def test_ontology_version_has_relations(self) -> None:
        self.sem.register_relation("test_predicate", "Test", "domain", "range")
        self.sem.snapshot_ontology("v1")
        snapshot = self.sem.get_ontology_version("v1")
        assert snapshot is not None
        preds = [r["predicate"] for r in snapshot["relations_snapshot"]]
        self.assertIn("test_predicate", preds)

    def test_snapshot_version_id_is_queryable(self) -> None:
        self.sem.snapshot_ontology("v1.0.0")
        result = self.sem.get_ontology_version("v1.0.0")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["version_id"], "v1.0.0")

    def test_nonexistent_ontology_version(self) -> None:
        result = self.sem.get_ontology_version("nonexistent")
        self.assertIsNone(result)
