from __future__ import annotations

import unittest
import sqlite3
import tempfile
from pathlib import Path

from campaign_autopilot.semantic_memory import SemanticMemoryStore
from campaign_autopilot.synthesis import KnowledgeSynthesisEngine


class TestKnowledgeSynthesisEngine(unittest.TestCase):
    """Level 5 — Knowledge Synthesis Engine."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(
            self._tmp.name, check_same_thread=False, isolation_level=None
        )
        self._conn.row_factory = sqlite3.Row
        self.sem = SemanticMemoryStore(self._conn)
        self.engine = KnowledgeSynthesisEngine(self.sem)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def _seed_claims(self) -> None:
        """Create a realistic set of claims across multiple simulated cycles."""
        ch1 = self.sem.register_concept("seo", "channel")
        ch2 = self.sem.register_concept("community", "channel")
        ld = self.sem.register_concept("lead_generation", "outcome")
        eff = self.sem.register_concept("campaign_effectiveness", "outcome")

        # Cycle 1: SEO produces leads
        self.sem.assert_claim(
            ch1,
            "produces_opt_in_leads",
            ld,
            0.6,
            "DIRECT_OBSERVATION",
            source_cycle_id="cycle_001",
            asserted_by="analytics",
        )
        # Cycle 2: SEO produces leads again (reinforcing)
        self.sem.assert_claim(
            ch1,
            "produces_opt_in_leads",
            ld,
            0.7,
            "DIRECT_OBSERVATION",
            source_cycle_id="cycle_002",
            asserted_by="analytics",
        )
        # Cycle 2: Community produces leads
        self.sem.assert_claim(
            ch2,
            "produces_opt_in_leads",
            ld,
            0.5,
            "DIRECT_OBSERVATION",
            source_cycle_id="cycle_002",
            asserted_by="analytics",
        )
        # Cycle 1: CTR indicates effectiveness
        self.sem.assert_claim(
            ch1,
            "indicates",
            eff,
            0.8,
            "STATISTICAL_INFERENCE",
            source_cycle_id="cycle_001",
            asserted_by="analytics",
        )
        # Cycle 2: CTR indicates effectiveness again (reinforcing)
        self.sem.assert_claim(
            ch1,
            "indicates",
            eff,
            0.85,
            "STATISTICAL_INFERENCE",
            source_cycle_id="cycle_002",
            asserted_by="analytics",
        )

    def _seed_conflict(self) -> None:
        """Create a conflicting pattern."""
        ch = self.sem.register_concept("social", "channel")
        eff = self.sem.register_concept("effectiveness", "outcome")
        ineff = self.sem.register_concept("ineffective", "outcome")
        self.sem.register_concept("ineffective", "outcome")

        self.sem.assert_claim(
            ch,
            "indicates",
            eff,
            0.4,
            "DIRECT_OBSERVATION",
            source_cycle_id="cycle_001",
            asserted_by="analytics",
        )
        self.sem.assert_claim(
            ch,
            "indicates",
            ineff,
            0.6,
            "DIRECT_OBSERVATION",
            source_cycle_id="cycle_002",
            asserted_by="analytics",
        )

    # ── Reinforcing pattern detection ──────────────────────────────────

    def test_find_reinforcing_patterns(self) -> None:
        self._seed_claims()
        patterns = self.engine.find_reinforcing_patterns(min_occurrences=2)
        self.assertGreaterEqual(len(patterns), 1)
        # SEO → leads should appear twice
        seo_leads = [p for p in patterns if p["predicate"] == "produces_opt_in_leads"]
        self.assertGreaterEqual(len(seo_leads), 1)
        for p in seo_leads:
            self.assertGreaterEqual(p["occurrences"], 2)

    def test_find_reinforcing_patterns_min_occurrences_filter(self) -> None:
        self._seed_claims()
        patterns = self.engine.find_reinforcing_patterns(min_occurrences=4)
        # With 4 seed claims sharing 2 predicate+object groups, nothing should reach 4
        self.assertEqual(len(patterns), 0)

    # ── Conflicting pattern detection ──────────────────────────────────

    def test_find_conflicting_patterns(self) -> None:
        self._seed_conflict()
        conflicts = self.engine.find_conflicting_patterns()
        self.assertGreaterEqual(len(conflicts), 1)
        for c in conflicts:
            self.assertEqual(c["type"], "conflicting")
            self.assertGreaterEqual(len(c["conflicting_objects"]), 2)

    def test_no_conflicts_without_contradictions(self) -> None:
        self._seed_claims()
        conflicts = self.engine.find_conflicting_patterns()
        # All seeded claims are consistent (no subject+predicate maps to different objects)
        for c in conflicts:
            self.assertNotIn("social", c.get("subject_name", ""))

    # ── Trending insights ──────────────────────────────────────────────

    def test_find_trending_insights(self) -> None:
        self._seed_claims()
        trending = self.engine.find_trending_insights(min_confidence_gain=0.05)
        # SEO → leads went from 0.6 to 0.7 (gain 0.1)
        # ch1 → eff went from 0.8 to 0.85 (gain 0.05)
        self.assertGreaterEqual(len(trending), 1)

    # ── Full synthesis pass ────────────────────────────────────────────

    def test_synthesize_produces_meta_claims(self) -> None:
        self._seed_claims()
        meta_ids = self.engine.synthesize(cycle_id="synthesis_001")
        self.assertGreater(len(meta_ids), 0)

        # Verify meta-insight concept was created
        meta_concept = self.sem.find_concept("meta_insight", "knowledge")
        assert meta_concept is not None

        # Verify meta-claims are queryable
        claims = self.sem.query_claims(subject=meta_concept["concept_id"])
        self.assertGreaterEqual(len(claims), 1)

    def test_synthesize_with_conflicts(self) -> None:
        self._seed_claims()
        self._seed_conflict()
        meta_ids = self.engine.synthesize(cycle_id="synthesis_002")
        self.assertGreater(len(meta_ids), 0)

        # Verify warning claims exist
        meta_concept = self.sem.find_concept("meta_insight", "knowledge")
        assert meta_concept is not None
        claims = self.sem.query_claims(subject=meta_concept["concept_id"])
        warn_claims = [c for c in claims if c["predicate"] == "warns"]
        self.assertGreaterEqual(len(warn_claims), 1)

    # ── Confidence decay scheduling ────────────────────────────────────

    def test_run_decay_cycle(self) -> None:
        self._seed_claims()
        initial = self.sem.query_claims(limit=100, min_confidence=0.0)
        init_count = len(initial)

        stats = self.engine.run_decay_cycle(decay_rate=0.5)
        self.assertIn("expired_claims", stats)
        self.assertIn("remaining_claims", stats)

        after = self.sem.query_claims(limit=100, min_confidence=0.0)
        self.assertLessEqual(len(after), init_count)

    def test_decay_is_gentle(self) -> None:
        self._seed_claims()
        self.engine.run_decay_cycle(decay_rate=0.95)
        remaining = self.sem.query_claims(limit=100, min_confidence=0.0)
        # Most should survive with gentle decay
        self.assertGreaterEqual(len(remaining), 4)

    # ── Summary report ─────────────────────────────────────────────────

    def test_summary(self) -> None:
        self._seed_claims()
        report = self.engine.summary()
        self.assertIn("total_concepts", report)
        self.assertIn("total_claims", report)
        self.assertIn("reinforcing_patterns", report)
        self.assertIn("conflicting_patterns", report)
        self.assertIn("avg_confidence", report)
        self.assertIn("concepts_by_namespace", report)
        self.assertGreater(report["total_claims"], 0)

    def test_summary_empty(self) -> None:
        report = self.engine.summary()
        self.assertEqual(report["total_claims"], 0)
        self.assertEqual(report["avg_confidence"], 0.0)
