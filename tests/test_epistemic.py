from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from campaign_autopilot.semantic_memory import (
    SemanticMemoryStore,
    VERIFIED,
    INFERRED,
    ASSUMED,
    HYPOTHETICAL,
    epistemic_weight,
)


class TestEpistemicWeight(unittest.TestCase):
    def test_verified_fully_weighted(self) -> None:
        self.assertEqual(epistemic_weight(0.8, VERIFIED), 0.8)

    def test_inferred_discounted(self) -> None:
        self.assertEqual(epistemic_weight(0.8, INFERRED), 0.64)

    def test_assumed_half_weight(self) -> None:
        self.assertEqual(epistemic_weight(0.8, ASSUMED), 0.4)

    def test_hypothetical_low_weight(self) -> None:
        self.assertEqual(epistemic_weight(0.8, HYPOTHETICAL), 0.24)

    def test_invalid_status_defaults(self) -> None:
        self.assertEqual(epistemic_weight(0.8, "UNKNOWN"), 0.64)


class TestEpistemicClaim(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.store = SemanticMemoryStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_assert_with_epistemic_status(self) -> None:
        subj = self.store.register_concept("test_subj", "test")
        obj = self.store.register_concept("test_obj", "test")
        cid = self.store.assert_claim(
            subject=subj,
            predicate="relates_to",
            object=obj,
            confidence=0.9,
            evidence_type="DIRECT_OBSERVATION",
            epistemic_status=VERIFIED,
        )
        claim = self.store.get_claim(cid)
        self.assertIsNotNone(claim)
        self.assertEqual(claim["epistemic_status"], VERIFIED)

    def test_assert_default_status(self) -> None:
        subj = self.store.register_concept("sub_default", "test")
        obj = self.store.register_concept("obj_default", "test")
        cid = self.store.assert_claim(
            subject=subj,
            predicate="relates_to",
            object=obj,
            confidence=0.5,
            evidence_type="STATISTICAL_INFERENCE",
        )
        claim = self.store.get_claim(cid)
        self.assertEqual(claim["epistemic_status"], INFERRED)

    def test_assert_invalid_status_raises(self) -> None:
        subj = self.store.register_concept("sub_inv", "test")
        obj = self.store.register_concept("obj_inv", "test")
        with self.assertRaises(ValueError):
            self.store.assert_claim(
                subject=subj,
                predicate="relates_to",
                object=obj,
                confidence=0.5,
                evidence_type="TEST",
                epistemic_status="INVALID_STATUS",
            )

    def test_claim_has_epistemic_weight(self) -> None:
        subj = self.store.register_concept("sub_w", "test")
        obj = self.store.register_concept("obj_w", "test")
        cid = self.store.assert_claim(
            subject=subj,
            predicate="relates_to",
            object=obj,
            confidence=1.0,
            evidence_type="DIRECT_OBSERVATION",
            epistemic_status=VERIFIED,
        )
        claim = self.store.get_claim(cid)
        self.assertEqual(claim["epistemic_weight"], 1.0)

    def test_query_by_epistemic_status(self) -> None:
        subj = self.store.register_concept("sub_q", "test")
        obj = self.store.register_concept("obj_q", "test")
        self.store.assert_claim(
            subject=subj,
            predicate="a",
            object=obj,
            confidence=0.5,
            evidence_type="T1",
            epistemic_status=VERIFIED,
        )
        self.store.assert_claim(
            subject=subj,
            predicate="b",
            object=obj,
            confidence=0.5,
            evidence_type="T2",
            epistemic_status=HYPOTHETICAL,
        )
        verified = self.store.query_claims(epistemic_status=VERIFIED)
        self.assertEqual(len(verified), 1)
        self.assertEqual(verified[0]["predicate"], "a")

    def test_query_by_min_epistemic_weight(self) -> None:
        subj = self.store.register_concept("sub_ew", "test")
        obj = self.store.register_concept("obj_ew", "test")
        self.store.assert_claim(
            subject=subj,
            predicate="a",
            object=obj,
            confidence=0.9,
            evidence_type="T1",
            epistemic_status=VERIFIED,
        )
        self.store.assert_claim(
            subject=subj,
            predicate="b",
            object=obj,
            confidence=0.9,
            evidence_type="T2",
            epistemic_status=HYPOTHETICAL,
        )
        # epistemic_weight: VERIFIED 0.9*1=0.9, HYPOTHETICAL 0.9*0.3=0.27
        heavy = self.store.query_claims(min_epistemic_weight=0.5)
        self.assertEqual(len(heavy), 1)
        self.assertEqual(heavy[0]["predicate"], "a")


class TestObserverRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.store = SemanticMemoryStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_register_and_get_observer(self) -> None:
        oid = self.store.register_observer(
            observer_id="analytics_agent",
            observer_type="AGENT",
            name="AnalyticsAgent",
            reliability=0.8,
        )
        obs = self.store.get_observer(oid)
        self.assertIsNotNone(obs)
        self.assertEqual(obs["observer_type"], "AGENT")
        self.assertEqual(obs["reliability"], 0.8)

    def test_register_observer_idempotent(self) -> None:
        oid1 = self.store.register_observer("obs_1", "AGENT", "One")
        oid2 = self.store.register_observer("obs_1", "HUMAN", "Two")
        self.assertEqual(oid1, oid2)
        obs = self.store.get_observer("obs_1")
        # Should keep original
        self.assertEqual(obs["name"], "One")

    def test_list_observers(self) -> None:
        self.store.register_observer("obs_a", "AGENT", "A")
        self.store.register_observer("obs_b", "HUMAN", "B")
        observers = self.store.list_observers()
        self.assertGreaterEqual(len(observers), 2)

    def test_claim_with_observer_id(self) -> None:
        self.store.register_observer("test_agent", "AGENT", "TestAgent", 0.7)
        subj = self.store.register_concept("sub_obs", "test")
        obj = self.store.register_concept("obj_obs", "test")
        cid = self.store.assert_claim(
            subject=subj,
            predicate="relates_to",
            object=obj,
            confidence=0.5,
            evidence_type="TEST",
            observer_id="test_agent",
        )
        claim = self.store.get_claim(cid)
        self.assertEqual(claim["observer_id"], "test_agent")

    def test_query_claims_includes_observer_details(self) -> None:
        self.store.register_observer("obs_q", "AGENT", "QueryAgent", 0.9)
        subj = self.store.register_concept("sub_od", "test")
        obj = self.store.register_concept("obj_od", "test")
        self.store.assert_claim(
            subject=subj,
            predicate="relates_to",
            object=obj,
            confidence=0.5,
            evidence_type="TEST",
            observer_id="obs_q",
        )
        claims = self.store.query_claims()
        self.assertGreaterEqual(len(claims), 1)
        claim = next(c for c in claims if c["observer_id"] == "obs_q")
        self.assertEqual(claim["observer_type"], "AGENT")
        self.assertAlmostEqual(claim["observer_reliability"], 0.9)


class TestSelectiveDecay(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.store = SemanticMemoryStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_decay_with_rates_by_status(self) -> None:
        subj = self.store.register_concept("sub_d", "test")
        obj = self.store.register_concept("obj_d", "test")
        cid_v = self.store.assert_claim(
            subject=subj,
            predicate="v",
            object=obj,
            confidence=1.0,
            evidence_type="T",
            epistemic_status=VERIFIED,
        )
        cid_h = self.store.assert_claim(
            subject=subj,
            predicate="h",
            object=obj,
            confidence=1.0,
            evidence_type="T",
            epistemic_status=HYPOTHETICAL,
        )
        # Decay: VERIFIED at 0.5, HYPOTHETICAL at 0.1
        self.store.decay_confidence(rates_by_status={VERIFIED: 0.5, HYPOTHETICAL: 0.1})

        cv = self.store.get_claim(cid_v)
        ch = self.store.get_claim(cid_h)
        # VERIFIED: 1.0 * 0.5 = 0.5
        self.assertAlmostEqual(cv["confidence"], 0.5)
        # HYPOTHETICAL: 1.0 * 0.1 = 0.01 (clamped to 0.01 min)
        self.assertAlmostEqual(ch["confidence"], 0.1)

    def test_decay_with_uniform_rate(self) -> None:
        """Old call pattern with decay_rate should still work."""
        subj = self.store.register_concept("sub_u", "test")
        obj = self.store.register_concept("obj_u", "test")
        cid = self.store.assert_claim(
            subject=subj,
            predicate="relates_to",
            object=obj,
            confidence=1.0,
            evidence_type="T",
            epistemic_status=VERIFIED,
        )
        self.store.decay_confidence(decay_rate=0.5)
        claim = self.store.get_claim(cid)
        self.assertAlmostEqual(claim["confidence"], 0.5)


class TestOntologyDiff(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.store = SemanticMemoryStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_diff_identical_versions(self) -> None:
        self.store.register_concept("a", "ns1")
        self.store.register_concept("b", "ns2")
        self.store.snapshot_ontology("v1")
        self.store.snapshot_ontology("v2")
        diff = self.store.diff_ontology("v1", "v2")
        self.assertEqual(diff["drift_score"], 0.0)
        self.assertEqual(diff["concepts_added"], [])
        self.assertEqual(diff["concepts_removed"], [])

    def test_diff_concepts_added(self) -> None:
        self.store.register_concept("x", "ns1")
        self.store.snapshot_ontology("v1")
        self.store.register_concept("y", "ns2")
        self.store.snapshot_ontology("v2")
        diff = self.store.diff_ontology("v1", "v2")
        self.assertIn("y::ns2", diff["concepts_added"])

    def test_diff_concept_definition_changed(self) -> None:
        cid = self.store.register_concept("changing", "ns1", "original def")
        self.store.snapshot_ontology("v1")
        self.store.update_concept_definition(cid, "updated def")
        self.store.snapshot_ontology("v2")
        diff = self.store.diff_ontology("v1", "v2")
        self.assertEqual(len(diff["concepts_modified"]), 1)
        self.assertEqual(diff["concepts_modified"][0]["key"], "changing::ns1")

    def test_diff_nonexistent_version(self) -> None:
        diff = self.store.diff_ontology("nonexistent", "v2")
        self.assertIn("error", diff)

    def test_diff_drift_score_high(self) -> None:
        self.store.register_concept("only", "ns1")
        self.store.snapshot_ontology("v1")
        for i in range(5):
            self.store.register_concept(f"new_{i}", "ns1")
        self.store.snapshot_ontology("v2")
        diff = self.store.diff_ontology("v1", "v2")
        self.assertEqual(diff["semantic_risk"], "HIGH")
        self.assertGreater(diff["drift_score"], 0.3)

    def test_observer_field_in_extract_cycle_knowledge(self) -> None:
        """extract_cycle_knowledge should accept observer_id parameter."""
        self.store.register_observer("analytics_v2", "AGENT", "Analytics", 0.8)
        cids = self.store.extract_cycle_knowledge(
            cycle_id="cycle_1",
            channel="seo",
            metric_data={"ctr": 0.025, "cpa": 30.0, "spend": 100.0, "conversions": 5},
            all_metrics_passed=True,
            asserted_by="analytics",
            observer_id="analytics_v2",
        )
        self.assertGreater(len(cids), 0)
        for cid in cids:
            claim = self.store.get_claim(cid)
            self.assertEqual(claim["observer_id"], "analytics_v2")
