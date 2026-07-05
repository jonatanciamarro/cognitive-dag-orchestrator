from __future__ import annotations

import threading
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KnowledgeSynthesisEngine:
    """Scans accumulated knowledge claims and produces higher-order meta-insights.

    Capabilities:
    - Cross-cycle pattern detection (reinforcing / conflicting claims)
    - Confidence trend analysis (rising / declining claims)
    - Meta-insight generation (knowledge about knowledge)
    - Confidence decay scheduling
    """

    def __init__(self, semantic_memory: Any):
        self.sem = semantic_memory
        self._lock = threading.Lock()

    # ── Pattern detection ──────────────────────────────────────────────

    def find_reinforcing_patterns(
        self, min_occurrences: int = 2
    ) -> list[dict[str, Any]]:
        """Find predicate+object combinations that appear across multiple cycles.
        These indicate stable, reinforced knowledge.
        """
        claims = self.sem.query_claims(limit=500, min_confidence=0.0)

        # Group by (predicate, object_concept_id)
        groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for c in claims:
            key = (c["predicate"], c["object_concept_id"])
            groups[key].append(c)

        patterns: list[dict[str, Any]] = []
        for (predicate, obj_id), group in groups.items():
            if len(group) >= min_occurrences:
                cycles = [c.get("source_cycle_id", "?") for c in group]
                avg_conf = sum(c["confidence"] for c in group) / len(group)
                patterns.append(
                    {
                        "type": "reinforcing",
                        "predicate": predicate,
                        "object_concept_id": obj_id,
                        "object_name": group[0].get("object_name", "?"),
                        "occurrences": len(group),
                        "cycles": list(set(cycles)),
                        "avg_confidence": round(avg_conf, 4),
                        "max_confidence": round(max(c["confidence"] for c in group), 4),
                        "trend": self._compute_trend(group),
                    }
                )

        patterns.sort(key=lambda p: -p["avg_confidence"])
        return patterns

    def find_conflicting_patterns(self) -> list[dict[str, Any]]:
        """Find subject+predicate where objects disagree across cycles.
        These indicate semantic conflict or drift.
        """
        claims = self.sem.query_claims(limit=500, min_confidence=0.0)

        # Group by (subject_concept_id, predicate)
        groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for c in claims:
            key = (c["subject_concept_id"], c["predicate"])
            groups[key].append(c)

        conflicts: list[dict[str, Any]] = []
        for (subj_id, predicate), group in groups.items():
            objects = set(c["object_concept_id"] for c in group)
            if len(objects) > 1:
                object_details = [
                    {
                        "object_id": oid,
                        "object_name": next(
                            (
                                c.get("object_name", "?")
                                for c in group
                                if c["object_concept_id"] == oid
                            ),
                            "?",
                        ),
                        "confidence": next(
                            (
                                c["confidence"]
                                for c in group
                                if c["object_concept_id"] == oid
                            ),
                            0,
                        ),
                        "cycle": next(
                            (
                                c.get("source_cycle_id", "?")
                                for c in group
                                if c["object_concept_id"] == oid
                            ),
                            "?",
                        ),
                    }
                    for oid in objects
                ]
                conflicts.append(
                    {
                        "type": "conflicting",
                        "subject_concept_id": subj_id,
                        "subject_name": group[0].get("subject_name", "?"),
                        "predicate": predicate,
                        "conflicting_objects": object_details,
                        "occurrences": len(group),
                        "resolution_needed": True,
                    }
                )

        conflicts.sort(key=lambda p: -len(p["conflicting_objects"]))
        return conflicts

    def find_trending_insights(
        self, min_confidence_gain: float = 0.1
    ) -> list[dict[str, Any]]:
        """Find claims whose confidence has increased over time (reinforced by feedback)."""
        claims = self.sem.query_claims(limit=500, min_confidence=0.0)

        # Group by (subject_concept_id, predicate, object_concept_id) to track over cycles
        groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for c in claims:
            key = (c["subject_concept_id"], c["predicate"], c["object_concept_id"])
            groups[key].append(c)

        trending: list[dict[str, Any]] = []
        for key, group in groups.items():
            if len(group) >= 2:
                sorted_group = sorted(group, key=lambda x: x.get("updated_at", ""))
                first_conf = sorted_group[0]["confidence"]
                last_conf = sorted_group[-1]["confidence"]
                gain = last_conf - first_conf
                if gain >= min_confidence_gain:
                    trending.append(
                        {
                            "type": "trending_up",
                            "subject_name": group[0].get("subject_name", "?"),
                            "predicate": key[1],
                            "object_name": group[0].get("object_name", "?"),
                            "initial_confidence": round(first_conf, 4),
                            "current_confidence": round(last_conf, 4),
                            "gain": round(gain, 4),
                            "occurrences": len(group),
                        }
                    )

        trending.sort(key=lambda p: -p["gain"])
        return trending

    # ── Meta-insight generation ────────────────────────────────────────

    def synthesize(self, cycle_id: str = "") -> list[str]:
        """Run full synthesis pass: detect patterns, generate meta-insights,
        store them as knowledge claims. Returns list of meta-claim IDs.
        """
        meta_claim_ids: list[str] = []

        # Ensure meta-insight concept exists
        meta_concept = self.sem.find_concept("meta_insight", "knowledge")
        if not meta_concept:
            meta_concept_id = self.sem.register_concept(
                "meta_insight",
                "knowledge",
                "Higher-order insight synthesized from multiple knowledge claims",
            )
        else:
            meta_concept_id = meta_concept["concept_id"]

        # Find and store reinforcing patterns
        reinforcers = self.find_reinforcing_patterns(min_occurrences=2)
        for p in reinforcers:
            insight_text = (
                f"Reinforced pattern: {p['predicate']} → {p['object_name']} "
                f"(observed {p['occurrences']} times across {len(p['cycles'])} cycles, "
                f"avg confidence {p['avg_confidence']:.2f})"
            )
            insight_concept_id = self.sem.register_concept(
                f"meta_reinforce_{p['predicate']}_{p['object_name'][:20]}",
                "knowledge",
                insight_text[:200],
            )
            cid = self.sem.assert_claim(
                subject=meta_concept_id,
                predicate="identifies",
                object=insight_concept_id,
                confidence=min(0.95, p["avg_confidence"] * 1.1),
                evidence_type="STATISTICAL_INFERENCE",
                supporting_data={
                    "pattern_type": "reinforcing",
                    "predicate": p["predicate"],
                    "object_name": p["object_name"],
                    "occurrences": p["occurrences"],
                    "cycles": p["cycles"],
                    "trend": p.get("trend", "stable"),
                },
                source_cycle_id=cycle_id,
                asserted_by="knowledge_synthesis",
            )
            meta_claim_ids.append(cid)

        # Find and store conflicting patterns
        conflicts = self.find_conflicting_patterns()
        for p in conflicts:
            objects_str = ", ".join(
                f"{o['object_name']}@{o['cycle']}({o['confidence']:.2f})"
                for o in p["conflicting_objects"]
            )
            insight_text = (
                f"Conflicting pattern: {p['subject_name']} {p['predicate']} "
                f"resolves to different objects: {objects_str}"
            )
            insight_concept_id = self.sem.register_concept(
                f"meta_conflict_{p['predicate']}_{p['subject_name'][:15]}",
                "knowledge",
                insight_text[:200],
            )
            cid = self.sem.assert_claim(
                subject=meta_concept_id,
                predicate="warns",
                object=insight_concept_id,
                confidence=0.8,
                evidence_type="STATISTICAL_INFERENCE",
                supporting_data={
                    "pattern_type": "conflicting",
                    "subject_name": p["subject_name"],
                    "predicate": p["predicate"],
                    "objects": p["conflicting_objects"],
                },
                source_cycle_id=cycle_id,
                asserted_by="knowledge_synthesis",
            )
            meta_claim_ids.append(cid)

        # Find and store trending insights
        trending = self.find_trending_insights()
        for p in trending[:5]:
            insight_text = (
                f"Trending: {p['subject_name']} {p['predicate']} {p['object_name']} "
                f"confidence rose from {p['initial_confidence']:.2f} to {p['current_confidence']:.2f}"
            )
            insight_concept_id = self.sem.register_concept(
                f"meta_trend_{p['predicate']}_{p['subject_name'][:15]}",
                "knowledge",
                insight_text[:200],
            )
            cid = self.sem.assert_claim(
                subject=meta_concept_id,
                predicate="tracks",
                object=insight_concept_id,
                confidence=min(0.95, p["current_confidence"]),
                evidence_type="STATISTICAL_INFERENCE",
                supporting_data={
                    "pattern_type": "trending_up",
                    "subject_name": p["subject_name"],
                    "predicate": p["predicate"],
                    "object_name": p["object_name"],
                    "gain": p["gain"],
                },
                source_cycle_id=cycle_id,
                asserted_by="knowledge_synthesis",
            )
            meta_claim_ids.append(cid)

        return meta_claim_ids

    # ── Confidence decay scheduling ───────────────────────────────────

    def run_decay_cycle(self, decay_rate: float = 0.85) -> dict[str, Any]:
        """Run a full confidence decay pass. Returns stats about what changed."""
        expired = self.sem.decay_confidence(decay_rate=decay_rate)

        # Count remaining claims
        remaining = self.sem.query_claims(limit=1000, min_confidence=0.0)

        return {
            "expired_claims": expired,
            "remaining_claims": len(remaining),
            "decay_rate": decay_rate,
            "timestamp": _utc_now(),
        }

    # ── Summary report ─────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        """Produce a human-readable summary of the synthesis state."""
        claims = self.sem.query_claims(limit=1000, min_confidence=0.0)
        concepts = self.sem.list_concepts()
        reinforcers = self.find_reinforcing_patterns(min_occurrences=2)
        conflicts = self.find_conflicting_patterns()
        trending = self.find_trending_insights()

        return {
            "total_concepts": len(concepts),
            "total_claims": len(claims),
            "reinforcing_patterns": len(reinforcers),
            "conflicting_patterns": len(conflicts),
            "trending_insights": len(trending),
            "avg_confidence": round(
                sum(c["confidence"] for c in claims) / len(claims), 4
            )
            if claims
            else 0.0,
            "concepts_by_namespace": dict(Counter(c["namespace"] for c in concepts)),
            "cycle_coverage": len(
                set(
                    c.get("source_cycle_id", "")
                    for c in claims
                    if c.get("source_cycle_id")
                )
            ),
        }

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _compute_trend(claim_group: list[dict[str, Any]]) -> str:
        """Determine if a group of claims shows rising, stable, or declining confidence."""
        if len(claim_group) < 2:
            return "stable"
        sorted_g = sorted(claim_group, key=lambda x: x.get("updated_at", ""))
        first = sorted_g[0]["confidence"]
        last = sorted_g[-1]["confidence"]
        diff = last - first
        if diff > 0.05:
            return "rising"
        if diff < -0.05:
            return "declining"
        return "stable"
