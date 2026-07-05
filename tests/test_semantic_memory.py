from __future__ import annotations

import json
import unittest
import sqlite3
import tempfile
from pathlib import Path

from campaign_autopilot.semantic_memory import SemanticMemoryStore
from campaign_autopilot.explanation import ExplanationStore


class TestSemanticMemoryStore(unittest.TestCase):
    """SemanticMemoryStore — Directive 1 verification."""

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

    # ── Concept operations ─────────────────────────────────────────────

    def test_register_and_get_concept(self) -> None:
        cid = self.store.register_concept(
            "seo", "channel", "Search engine optimization"
        )
        concept = self.store.get_concept(cid)
        assert concept is not None
        self.assertEqual(concept["name"], "seo")
        self.assertEqual(concept["namespace"], "channel")

    def test_register_concept_is_idempotent(self) -> None:
        cid1 = self.store.register_concept("ctr", "metric")
        cid2 = self.store.register_concept("ctr", "metric")
        self.assertEqual(cid1, cid2)

    def test_find_concept_by_name_namespace(self) -> None:
        self.store.register_concept("lead_generation", "outcome", "Opt-in lead gen")
        found = self.store.find_concept("lead_generation", "outcome")
        assert found is not None
        self.assertEqual(found["namespace"], "outcome")

    def test_find_concept_nonexistent(self) -> None:
        self.assertIsNone(self.store.find_concept("nonexistent", "void"))

    def test_list_concepts_all(self) -> None:
        self.store.register_concept("seo", "channel")
        self.store.register_concept("ctr", "metric")
        concepts = self.store.list_concepts()
        self.assertGreaterEqual(len(concepts), 2)

    def test_list_concepts_by_namespace(self) -> None:
        self.store.register_concept("email", "channel")
        channels = self.store.list_concepts(namespace="channel")
        self.assertGreaterEqual(len(channels), 1)
        for c in channels:
            self.assertEqual(c["namespace"], "channel")

    # ── Knowledge claim operations ─────────────────────────────────────

    def test_assert_and_query_claim(self) -> None:
        ch_id = self.store.register_concept("seo", "channel")
        ld_id = self.store.register_concept("lead_generation", "outcome")
        claim_id = self.store.assert_claim(
            subject=ch_id,
            predicate="produces_opt_in_leads",
            object=ld_id,
            confidence=0.7,
            evidence_type="DIRECT_OBSERVATION",
            supporting_data={"ctr": 2.5},
            source_cycle_id="cycle_001",
            asserted_by="analytics",
        )
        results = self.store.query_claims(subject=ch_id, min_confidence=0.5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["predicate"], "produces_opt_in_leads")

    def test_query_claims_no_match(self) -> None:
        results = self.store.query_claims(
            subject="nonexistent",
            min_confidence=0.9,
        )
        self.assertEqual(len(results), 0)

    def test_query_claims_limit(self) -> None:
        ch_id = self.store.register_concept("seo", "channel")
        ld_id = self.store.register_concept("lead_generation", "outcome")
        for i in range(5):
            self.store.assert_claim(
                subject=ch_id,
                predicate=f"test_predicate_{i}",
                object=ld_id,
                confidence=0.5,
                evidence_type="DIRECT_OBSERVATION",
                source_cycle_id=f"cycle_{i}",
                asserted_by="test",
            )
        results = self.store.query_claims(subject=ch_id, limit=3)
        self.assertLessEqual(len(results), 3)

    def test_confidence_clamping(self) -> None:
        ch_id = self.store.register_concept("test", "domain")
        ld_id = self.store.register_concept("lead", "outcome")
        cid = self.store.assert_claim(
            subject=ch_id,
            predicate="indicates",
            object=ld_id,
            confidence=2.0,  # above max
            evidence_type="TEST",
            source_cycle_id="c1",
            asserted_by="test",
        )
        results = self.store.query_claims(subject=ch_id)
        assert len(results) == 1
        self.assertLessEqual(results[0]["confidence"], 1.0)

    def test_confidence_decay(self) -> None:
        ch_id = self.store.register_concept("test_ch", "channel")
        ld_id = self.store.register_concept("test_ld", "outcome")
        self.store.assert_claim(
            subject=ch_id,
            predicate="produces",
            object=ld_id,
            confidence=0.8,
            evidence_type="TEST",
            source_cycle_id="c1",
            asserted_by="test",
        )
        self.store.decay_confidence(decay_rate=0.5)
        results = self.store.query_claims(subject=ch_id)
        assert len(results) == 1
        self.assertLess(results[0]["confidence"], 0.8)

    def test_reinforce_claim_increases_confidence(self) -> None:
        ch_id = self.store.register_concept("ch", "channel")
        ld_id = self.store.register_concept("ld", "outcome")
        cid = self.store.assert_claim(
            subject=ch_id,
            predicate="produces",
            object=ld_id,
            confidence=0.5,
            evidence_type="TEST",
            source_cycle_id="c1",
            asserted_by="test",
        )
        self.store.reinforce_claim(cid, {"new_evidence": "more data"})
        results = self.store.query_claims(subject=ch_id)
        assert len(results) == 1
        self.assertGreater(results[0]["confidence"], 0.5)

    # ── Evidence operations ────────────────────────────────────────────

    def test_record_and_get_provenance(self) -> None:
        ch_id = self.store.register_concept("ch", "channel")
        ld_id = self.store.register_concept("ld", "outcome")
        cid = self.store.assert_claim(
            subject=ch_id,
            predicate="produces",
            object=ld_id,
            confidence=0.6,
            evidence_type="TEST",
            source_cycle_id="c1",
            asserted_by="test",
        )
        eid = self.store.record_evidence(
            claim_id=cid,
            observation_type="METRIC_SNAPSHOT",
            observation_data={"ctr": 2.1},
            cycle_id="c1",
        )
        chain = self.store.get_provenance_chain(cid)
        self.assertGreaterEqual(len(chain), 1)
        self.assertEqual(chain[0]["observation_type"], "METRIC_SNAPSHOT")

    # ── Relation operations ────────────────────────────────────────────

    def test_register_and_list_relations(self) -> None:
        rid = self.store.register_relation(
            predicate="produces_opt_in_leads",
            description="A channel that generates opt-in leads",
            domain_namespace="channel",
            range_namespace="outcome",
        )
        relations = self.store.list_relations()
        ids = [r["relation_id"] for r in relations]
        self.assertIn(rid, ids)

    # ── Ontology versioning ────────────────────────────────────────────

    def test_snapshot_and_get_ontology(self) -> None:
        self.store.register_concept("test_concept", "test_ns")
        self.store.snapshot_ontology("v1.0.0")
        snapshot = self.store.get_ontology_version("v1.0.0")
        assert snapshot is not None
        self.assertEqual(snapshot["version_id"], "v1.0.0")
        concepts = snapshot["concepts_snapshot"]
        names = [c["name"] for c in concepts]
        self.assertIn("test_concept", names)

    # ── Knowledge extraction helper ────────────────────────────────────

    def test_extract_cycle_knowledge(self) -> None:
        claim_ids = self.store.extract_cycle_knowledge(
            cycle_id="cycle_001",
            channel="seo",
            metric_data={"ctr": 2.5, "cpa": None, "spend": 100, "conversions": 10},
            all_metrics_passed=True,
            asserted_by="analytics",
        )
        self.assertGreater(len(claim_ids), 0)
        # Verify the claims are queryable
        ch_concept = self.store.find_concept("seo", "channel")
        assert ch_concept is not None
        results = self.store.query_claims(subject=ch_concept["concept_id"])
        self.assertGreaterEqual(len(results), 1)


class TestExplanationStore(unittest.TestCase):
    """ExplanationStore — Directive 2 verification."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.store = ExplanationStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    # ── Decision recording ─────────────────────────────────────────────

    def test_record_decision(self) -> None:
        did = self.store.record_decision(
            agent_id="compliance",
            cycle_id="cycle_001",
            decision_type="policy_gate",
            input_state={"opt_in": False},
        )
        decision = self.store.get_decision(did)
        assert decision is not None
        self.assertEqual(decision["agent_id"], "compliance")
        self.assertEqual(decision["decision_type"], "policy_gate")

    def test_record_decision_with_parent(self) -> None:
        parent = self.store.record_decision("orchestrator", "c1", "orchestration")
        child = self.store.record_decision(
            "compliance",
            "c1",
            "policy_gate",
            parent_decision_id=parent,
        )
        child_dec = self.store.get_decision(child)
        assert child_dec is not None
        self.assertEqual(child_dec["parent_decision_id"], parent)

    def test_update_decision_output(self) -> None:
        did = self.store.record_decision("compliance", "c1", "policy_gate")
        self.store.update_decision_output(
            did, {"status": "blocked", "reason": "missing_opt_in"}
        )
        decision = self.store.get_decision(did)
        assert decision is not None
        output = json.loads(decision["output_decision"])
        self.assertEqual(output["status"], "blocked")

    # ── Rule application recording ─────────────────────────────────────

    def test_record_rule_application(self) -> None:
        did = self.store.record_decision("compliance", "c1", "policy_gate")
        rid = self.store.record_rule_application(
            decision_id=did,
            rule_source="config.policy.requires_explicit_opt_in",
            rule_value=True,
            actual_value=False,
            comparison_result=False,
            rule_order=1,
        )
        rules = self.store.get_rules_applied(did)
        self.assertEqual(len(rules), 1)
        self.assertFalse(rules[0]["comparison_result"])

    def test_get_failed_rules(self) -> None:
        did = self.store.record_decision("compliance", "c1", "policy_gate")
        self.store.record_rule_application(did, "rule_1", True, False, False, 1)
        self.store.record_rule_application(did, "rule_2", True, True, True, 2)
        failed = self.store.get_failed_rules(did)
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["rule_source"], "rule_1")

    # ── Counterfactual operations ──────────────────────────────────────

    def test_record_and_compute_counterfactual(self) -> None:
        did = self.store.record_decision("compliance", "c1", "policy_gate")
        self.store.record_rule_application(
            did,
            "config.policy.requires_explicit_opt_in",
            True,
            False,
            False,
            1,
        )
        cf = self.store.compute_counterfactual(did)
        assert cf is not None
        self.assertEqual(cf["changed_field"], "config.policy.requires_explicit_opt_in")
        self.assertEqual(cf["predicted_outcome"], "pass")

    def test_counterfactual_no_failed_rules(self) -> None:
        did = self.store.record_decision("compliance", "c1", "policy_gate")
        self.store.record_rule_application(did, "rule_1", True, True, True, 1)
        cf = self.store.compute_counterfactual(did)
        self.assertIsNone(cf)

    # ── Explanation rendering ──────────────────────────────────────────

    def test_render_explanation_operator_default(self) -> None:
        did = self.store.record_decision(
            "compliance",
            "c1",
            "compliance_gate",
            input_state={"opt_in": False, "consent": False},
        )
        self.store.record_rule_application(
            did,
            "config.policy.requires_explicit_opt_in",
            True,
            False,
            False,
            1,
        )
        explanation = self.store.render_explanation(did, observer_role="operator")
        self.assertIn("blocked", explanation)
        self.assertIn("config.policy", explanation)

    def test_render_explanation_compliance_role(self) -> None:
        did = self.store.record_decision(
            "compliance",
            "c1",
            "compliance_gate",
            input_state={"opt_in": False, "audience": "all", "consent_scope": "email"},
        )
        self.store.record_rule_application(
            did,
            "policy.requires_explicit_opt_in",
            True,
            False,
            False,
            1,
        )
        explanation = self.store.render_explanation(did, observer_role="compliance")
        self.assertIn("Compliance gate", explanation)
        self.assertIn(did, explanation)

    def test_render_explanation_unknown_decision(self) -> None:
        explanation = self.store.render_explanation("nonexistent")
        self.assertIn("not found", explanation)

    def test_render_explanation_cto_role(self) -> None:
        did = self.store.record_decision(
            "analytics",
            "c1",
            "metrics_gate",
            input_state={"ctr": 1.5, "minimum_ctr": 2.0},
        )
        self.store.record_rule_application(
            did,
            "metrics.ctr_minimum",
            ">= 2.0",
            1.5,
            False,
            1,
        )
        explanation = self.store.render_explanation(did, observer_role="cto")
        self.assertIn("Decision", explanation)
        self.assertIn("Input state", explanation)

    # ── Provenance chain ───────────────────────────────────────────────

    def test_render_provenance_chain_text(self) -> None:
        parent = self.store.record_decision("orchestrator", "c1", "orchestration")
        child = self.store.record_decision(
            "compliance",
            "c1",
            "policy_gate",
            parent_decision_id=parent,
        )
        chain = self.store.render_provenance_chain(child, fmt="text")
        self.assertIn("Provenance Chain", chain)
        self.assertIn(child, chain)
        self.assertIn(parent, chain)

    def test_render_provenance_chain_json(self) -> None:
        did = self.store.record_decision("compliance", "c1", "policy_gate")
        chain_json = self.store.render_provenance_chain(did, fmt="json")
        parsed = json.loads(chain_json)
        self.assertGreaterEqual(len(parsed), 1)

    # ── Cycle queries ──────────────────────────────────────────────────

    def test_get_decisions_for_cycle(self) -> None:
        self.store.record_decision("compliance", "cycle_1", "policy_gate")
        self.store.record_decision("analytics", "cycle_1", "metrics_gate")
        self.store.record_decision("optimization", "cycle_2", "proposal")
        decisions = self.store.get_decisions_for_cycle("cycle_1")
        self.assertEqual(len(decisions), 2)


class TestSemanticMemoryIntegration(unittest.TestCase):
    """End-to-end: SemanticMemory + Explanation stores working together."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()  # Libera lock no Windows
        self._conn = sqlite3.connect(self._tmp.name)
        self._conn.row_factory = sqlite3.Row
        self.sem = SemanticMemoryStore(self._conn)
        self.exp = ExplanationStore(self._conn)

    def tearDown(self) -> None:
        self._conn.close()
        try:
            Path(self._tmp.name).unlink(missing_ok=True)
        except Exception:
            pass

    def test_knowledge_claim_with_explanation_provenance(self) -> None:
        """A knowledge claim from analytics should be traceable to a decision explanation."""
        # 1. Analytics records a decision
        did = self.exp.record_decision(
            agent_id="analytics",
            cycle_id="cycle_001",
            decision_type="metrics_gate",
            input_state={"ctr": 2.5, "channels": ["seo"]},
        )
        self.exp.record_rule_application(
            did, "metrics.ctr_minimum", ">=2.0", 2.5, True, 1
        )
        self.exp.update_decision_output(did, {"status": "pass"})

        # 2. Analytics extracts cycle knowledge
        ch_id = self.sem.register_concept("seo", "channel")
        ld_id = self.sem.register_concept("lead_generation", "outcome")
        cid = self.sem.assert_claim(
            subject=ch_id,
            predicate="produces_opt_in_leads",
            object=ld_id,
            confidence=0.6,
            evidence_type="DIRECT_OBSERVATION",
            supporting_data={"source_decision": did, "ctr": 2.5},
            source_cycle_id="cycle_001",
            asserted_by="analytics",
        )

        # 3. Verify claim exists
        results = self.sem.query_claims(subject=ch_id)
        self.assertGreaterEqual(len(results), 1)

        # 4. Verify explanation exists for the decision that produced the claim
        decision = self.exp.get_decision(did)
        assert decision is not None
        self.assertEqual(decision["agent_id"], "analytics")

        # 5. Verify provenance chain from explanation
        explanation = self.exp.render_explanation(did, observer_role="operator")
        self.assertIn("Metrics", explanation)
        self.assertIn("pass", explanation)
