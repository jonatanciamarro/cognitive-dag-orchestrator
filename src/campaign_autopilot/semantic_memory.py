from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# Epistemic status constants
VERIFIED = "VERIFIED"
INFERRED = "INFERRED"
ASSUMED = "ASSUMED"
HYPOTHETICAL = "HYPOTHETICAL"

_VALID_STATUSES = {VERIFIED, INFERRED, ASSUMED, HYPOTHETICAL}

# Default decay rates per epistemic status
_DEFAULT_DECAY_RATES = {
    VERIFIED: 0.95,
    INFERRED: 0.85,
    ASSUMED: 0.75,
    HYPOTHETICAL: 0.65,
}


def epistemic_weight(confidence: float, status: str) -> float:
    """Compute epistemic weight from confidence and status."""
    multipliers = {VERIFIED: 1.0, INFERRED: 0.8, ASSUMED: 0.5, HYPOTHETICAL: 0.3}
    return round(confidence * multipliers.get(status, 0.8), 6)


class SemanticMemoryStore:
    """Persists conceptual knowledge with confidence, provenance, epistemic status,
    and temporal context.

    Concepts are registered entities or ideas. KnowledgeClaims are asserted
    relationships between concepts, each with confidence, evidence_type,
    epistemic_status, observer, and provenance.
    """

    def __init__(self, conn: Any):
        """Initialize with an existing SQLite connection (from MemoryStore)."""
        self._conn = conn
        self._lock = threading.Lock()
        self._ensure_schema()

    def _execute(self, sql: str, params=None):
        with self._lock:
            if params is not None:
                return self._conn.execute(sql, params)
            return self._conn.execute(sql)

    def _executescript(self, sql: str):
        with self._lock:
            return self._conn.executescript(sql)

    def _ensure_schema(self) -> None:
        # Core tables
        self._execute(
            """CREATE TABLE IF NOT EXISTS semantic_concepts (
                concept_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                namespace TEXT NOT NULL,
                definition TEXT NOT NULL DEFAULT '',
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )"""
        )
        self._execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS idx_concept_name_ns
                ON semantic_concepts(name, namespace)"""
        )
        self._execute(
            """CREATE TABLE IF NOT EXISTS semantic_claims (
                claim_id TEXT PRIMARY KEY,
                subject_concept_id TEXT NOT NULL REFERENCES semantic_concepts(concept_id),
                predicate TEXT NOT NULL,
                object_concept_id TEXT NOT NULL REFERENCES semantic_concepts(concept_id),
                confidence REAL NOT NULL DEFAULT 0.5,
                epistemic_status TEXT NOT NULL DEFAULT 'INFERRED',
                observer_id TEXT,
                evidence_type TEXT NOT NULL,
                source_cycle_id TEXT NOT NULL,
                supporting_data TEXT NOT NULL DEFAULT '{}',
                asserted_by TEXT NOT NULL,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_claims_subject
                ON semantic_claims(subject_concept_id)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_claims_predicate
                ON semantic_claims(predicate)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_claims_object
                ON semantic_claims(object_concept_id)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_claims_confidence
                ON semantic_claims(confidence)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_claims_cycle
                ON semantic_claims(source_cycle_id)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_claims_epistemic
                ON semantic_claims(epistemic_status)"""
        )
        # Observer registry
        self._execute(
            """CREATE TABLE IF NOT EXISTS semantic_observers (
                observer_id TEXT PRIMARY KEY,
                observer_type TEXT NOT NULL DEFAULT 'AGENT',
                name TEXT NOT NULL,
                reliability REAL NOT NULL DEFAULT 0.5,
                bias_profile TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            )"""
        )
        # Evidence store
        self._execute(
            """CREATE TABLE IF NOT EXISTS semantic_evidence (
                evidence_id TEXT PRIMARY KEY,
                claim_id TEXT NOT NULL REFERENCES semantic_claims(claim_id),
                observation_type TEXT NOT NULL,
                observation_data TEXT NOT NULL DEFAULT '{}',
                cycle_id TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_evidence_claim
                ON semantic_evidence(claim_id)"""
        )
        # Relation registry
        self._execute(
            """CREATE TABLE IF NOT EXISTS semantic_relations (
                relation_id TEXT PRIMARY KEY,
                predicate TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                domain_namespace TEXT NOT NULL,
                range_namespace TEXT NOT NULL,
                is_symmetric INTEGER NOT NULL DEFAULT 0
            )"""
        )
        # Ontology versioning
        self._execute(
            """CREATE TABLE IF NOT EXISTS semantic_ontology_versions (
                version_id TEXT PRIMARY KEY,
                concepts_snapshot TEXT NOT NULL DEFAULT '[]',
                relations_snapshot TEXT NOT NULL DEFAULT '[]',
                released_at TEXT NOT NULL
            )"""
        )

    # -- Observer operations --

    def register_observer(
        self,
        observer_id: str,
        observer_type: str = "AGENT",
        name: str = "",
        reliability: float = 0.5,
        bias_profile: dict[str, Any] | None = None,
    ) -> str:
        """Register an observer. Idempotent on observer_id."""
        existing = self._execute(
            "SELECT observer_id FROM semantic_observers WHERE observer_id = ?",
            (observer_id,),
        ).fetchone()
        if existing:
            return existing[0]

        self._execute(
            """INSERT INTO semantic_observers
               (observer_id, observer_type, name, reliability, bias_profile, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                observer_id,
                observer_type,
                name,
                max(0.0, min(1.0, reliability)),
                json.dumps(bias_profile or {}),
                _utc_now(),
            ),
        )
        self._conn.commit()
        return observer_id

    def get_observer(self, observer_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM semantic_observers WHERE observer_id = ?",
            (observer_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_observers(self) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM semantic_observers ORDER BY name"
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Concept operations --

    def register_concept(
        self,
        name: str,
        namespace: str,
        definition: str = "",
    ) -> str:
        """Register a new concept. Returns concept_id. Idempotent on (name, namespace)."""
        existing = self._execute(
            "SELECT concept_id FROM semantic_concepts WHERE name = ? AND namespace = ?",
            (name, namespace),
        ).fetchone()
        if existing:
            return existing[0]

        concept_id = _new_id()
        self._execute(
            """INSERT INTO semantic_concepts
               (concept_id, name, namespace, definition, version, created_at)
               VALUES (?, ?, ?, ?, 1, ?)""",
            (concept_id, name, namespace, definition, _utc_now()),
        )
        self._conn.commit()
        return concept_id

    def get_concept(self, concept_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM semantic_concepts WHERE concept_id = ?",
            (concept_id,),
        ).fetchone()
        return dict(row) if row else None

    def find_concept(self, name: str, namespace: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM semantic_concepts WHERE name = ? AND namespace = ?",
            (name, namespace),
        ).fetchone()
        return dict(row) if row else None

    def list_concepts(self, namespace: str | None = None) -> list[dict[str, Any]]:
        if namespace is not None:
            rows = self._execute(
                "SELECT * FROM semantic_concepts WHERE namespace = ? ORDER BY name",
                (namespace,),
            ).fetchall()
        else:
            rows = self._execute(
                "SELECT * FROM semantic_concepts ORDER BY name"
            ).fetchall()
        return [dict(r) for r in rows]

    def update_concept_definition(
        self, concept_id: str, definition: str
    ) -> dict[str, Any] | None:
        self._execute(
            """UPDATE semantic_concepts
               SET definition = ?, version = version + 1
               WHERE concept_id = ?""",
            (definition, concept_id),
        )
        self._conn.commit()
        return self.get_concept(concept_id)

    # -- Claim operations --

    def assert_claim(
        self,
        subject: str,
        predicate: str,
        object: str,
        confidence: float,
        evidence_type: str,
        supporting_data: dict[str, Any] | None = None,
        source_cycle_id: str = "",
        asserted_by: str = "",
        expires_at: str | None = None,
        epistemic_status: str = INFERRED,
        observer_id: str | None = None,
    ) -> str:
        """Assert a knowledge claim between two concepts with epistemic classification.

        Args:
            subject: Concept ID of the subject.
            predicate: Relationship predicate.
            object: Concept ID of the object.
            confidence: Confidence score 0-1.
            evidence_type: Type of evidence (e.g. DIRECT_OBSERVATION, STATISTICAL_INFERENCE).
            supporting_data: Optional supporting context.
            source_cycle_id: Cycle that produced this claim.
            asserted_by: Who/what asserted this claim.
            expires_at: Optional expiration timestamp.
            epistemic_status: Epistemic classification (VERIFIED, INFERRED, ASSUMED, HYPOTHETICAL).
            observer_id: Optional observer that produced this claim.
        """
        if epistemic_status not in _VALID_STATUSES:
            raise ValueError(
                f"Invalid epistemic_status '{epistemic_status}'. "
                f"Must be one of {_VALID_STATUSES}"
            )
        claim_id = _new_id()
        now = _utc_now()
        self._execute(
            """INSERT INTO semantic_claims
               (claim_id, subject_concept_id, predicate, object_concept_id,
                confidence, epistemic_status, observer_id, evidence_type,
                source_cycle_id, supporting_data, asserted_by, expires_at,
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                claim_id,
                subject,
                predicate,
                object,
                max(0.0, min(1.0, confidence)),
                epistemic_status,
                observer_id,
                evidence_type,
                source_cycle_id,
                json.dumps(supporting_data or {}),
                asserted_by,
                expires_at,
                now,
                now,
            ),
        )
        self._conn.commit()
        return claim_id

    def query_claims(
        self,
        subject: str | None = None,
        predicate: str | None = None,
        object: str | None = None,
        min_confidence: float = 0.0,
        min_epistemic_weight: float = 0.0,
        epistemic_status: str | None = None,
        namespace: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Query knowledge claims with optional filters.

        Returns claims enriched with epistemic_weight and observer details.
        """
        clauses: list[str] = []
        params: list[Any] = []

        if subject is not None:
            clauses.append("c.subject_concept_id = ?")
            params.append(subject)
        if predicate is not None:
            clauses.append("c.predicate = ?")
            params.append(predicate)
        if object is not None:
            clauses.append("c.object_concept_id = ?")
            params.append(object)
        if min_confidence > 0.0:
            clauses.append("c.confidence >= ?")
            params.append(min_confidence)
        if epistemic_status is not None:
            clauses.append("c.epistemic_status = ?")
            params.append(epistemic_status)
        if namespace is not None:
            clauses.append("(sc1.namespace = ? OR sc2.namespace = ?)")
            params.extend([namespace, namespace])

        where = " AND ".join(clauses) if clauses else "1=1"
        query = f"""
            SELECT c.*, sc1.name AS subject_name, sc1.namespace AS subject_ns,
                   sc2.name AS object_name, sc2.namespace AS object_ns,
                   o.observer_type AS observer_type,
                   o.reliability AS observer_reliability
            FROM semantic_claims c
            JOIN semantic_concepts sc1 ON c.subject_concept_id = sc1.concept_id
            JOIN semantic_concepts sc2 ON c.object_concept_id = sc2.concept_id
            LEFT JOIN semantic_observers o ON c.observer_id = o.observer_id
            WHERE {where}
            ORDER BY c.confidence DESC, c.updated_at DESC
            LIMIT ?
        """
        params.append(limit)
        rows = self._execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["epistemic_weight"] = epistemic_weight(
                d.get("confidence", 0.0),
                d.get("epistemic_status", INFERRED),
            )
            if (
                min_epistemic_weight > 0.0
                and d["epistemic_weight"] < min_epistemic_weight
            ):
                continue
            results.append(d)
        return results

    def reinforce_claim(
        self,
        claim_id: str,
        confidence_delta: float = 0.05,
    ) -> dict[str, Any] | None:
        """Increase the confidence of an existing claim (bounded at 1.0)."""
        self._execute(
            """UPDATE semantic_claims
               SET confidence = MIN(1.0, confidence + ?), updated_at = ?
               WHERE claim_id = ?""",
            (max(0.0, confidence_delta), _utc_now(), claim_id),
        )
        self._conn.commit()
        row = self._execute(
            "SELECT * FROM semantic_claims WHERE claim_id = ?",
            (claim_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_claim(self, claim_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM semantic_claims WHERE claim_id = ?",
            (claim_id,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["epistemic_weight"] = epistemic_weight(
            d.get("confidence", 0.0),
            d.get("epistemic_status", INFERRED),
        )
        return d

    # -- Confidence decay with epistemic awareness --

    def decay_confidence(
        self,
        decay_rate: float | None = None,
        rates_by_status: dict[str, float] | None = None,
    ) -> int:
        """Apply exponential confidence decay with per-status decay rates.

        Args:
            decay_rate: Uniform decay rate override (ignored if rates_by_status provided).
            rates_by_status: Dict mapping epistemic_status to decay_rate.
                           Defaults to _DEFAULT_DECAY_RATES if not provided.

        Returns: Count of expired claims removed.
        """
        now = _utc_now()
        if rates_by_status:
            decay_map = rates_by_status
        elif decay_rate is not None:
            decay_map = {s: decay_rate for s in _VALID_STATUSES}
        else:
            decay_map = dict(_DEFAULT_DECAY_RATES)

        for status, rate in decay_map.items():
            rate = max(0.01, min(1.0, rate))
            self._execute(
                """UPDATE semantic_claims
                   SET confidence = MAX(0.01, confidence * ?), updated_at = ?
                   WHERE epistemic_status = ? AND (expires_at IS NULL OR expires_at > ?)""",
                (rate, now, status, now),
            )

        self._conn.commit()

        # Remove expired claims
        result = self._execute(
            "DELETE FROM semantic_claims WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (now,),
        )
        self._conn.commit()
        return result.rowcount

    def reinforce_claim(
        self,
        claim_id: str,
        additional_evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Reinforce an existing claim, increasing confidence and adding evidence."""
        row = self._execute(
            "SELECT confidence, supporting_data FROM semantic_claims WHERE claim_id = ?",
            (claim_id,),
        ).fetchone()
        if row is None:
            return None

        old_conf = row[0]
        new_conf = min(1.0, old_conf + 0.1 * (1.0 - old_conf))
        existing_data = json.loads(row[1])
        if additional_evidence:
            existing_data.setdefault("reinforcements", []).append(additional_evidence)

        self._execute(
            """UPDATE semantic_claims
               SET confidence = ?, supporting_data = ?, updated_at = ?
               WHERE claim_id = ?""",
            (new_conf, json.dumps(existing_data), _utc_now(), claim_id),
        )
        self._conn.commit()

        row = self._execute(
            "SELECT * FROM semantic_claims WHERE claim_id = ?",
            (claim_id,),
        ).fetchone()
        return dict(row) if row else None

    def reinforce_claims_by_observer(
        self,
        observer_id: str,
        boost: float = 0.02,
        status_filter: str | None = None,
    ) -> int:
        """Boost confidence of all claims from a given observer.

        Used for co-observation reinforcement: when an observer consistently
        produces reliable claims, all their claims get a small boost.
        """
        clauses = ["observer_id = ?"]
        params: list[Any] = [observer_id]
        if status_filter is not None:
            clauses.append("epistemic_status = ?")
            params.append(status_filter)

        where = " AND ".join(clauses)
        self._execute(
            f"""UPDATE semantic_claims
                SET confidence = MIN(1.0, confidence + ?), updated_at = ?
                WHERE {where}""",
            (max(0.0, boost), _utc_now(), *params),
        )
        self._conn.commit()

        row = self._execute(
            "SELECT COUNT(*) AS cnt FROM semantic_claims WHERE observer_id = ?",
            (observer_id,),
        ).fetchone()
        return row["cnt"] if row else 0

    # -- Evidence operations --

    def record_evidence(
        self,
        claim_id: str,
        observation_type: str,
        observation_data: dict[str, Any] | None = None,
        cycle_id: str = "",
    ) -> str:
        evidence_id = _new_id()
        self._execute(
            """INSERT INTO semantic_evidence
               (evidence_id, claim_id, observation_type, observation_data, cycle_id, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                evidence_id,
                claim_id,
                observation_type,
                json.dumps(observation_data or {}),
                cycle_id,
                _utc_now(),
            ),
        )
        self._conn.commit()
        return evidence_id

    def get_evidence(self, claim_id: str) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM semantic_evidence WHERE claim_id = ? ORDER BY timestamp ASC",
            (claim_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_provenance_chain(self, claim_id: str) -> list[dict[str, Any]]:
        """Alias for get_evidence. Returns evidence chain for a claim."""
        return self.get_evidence(claim_id)

    # -- Relation operations --

    def register_relation(
        self,
        predicate: str,
        description: str,
        domain_namespace: str,
        range_namespace: str,
        is_symmetric: bool = False,
    ) -> str:
        existing = self._execute(
            "SELECT relation_id FROM semantic_relations WHERE predicate = ?",
            (predicate,),
        ).fetchone()
        if existing:
            return existing[0]

        rel_id = _new_id()
        self._execute(
            """INSERT INTO semantic_relations
               (relation_id, predicate, description, domain_namespace, range_namespace, is_symmetric)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                rel_id,
                predicate,
                description,
                domain_namespace,
                range_namespace,
                int(is_symmetric),
            ),
        )
        self._conn.commit()
        return rel_id

    def list_relations(self) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM semantic_relations ORDER BY predicate"
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Ontology versioning --

    def snapshot_ontology(self, version_id: str) -> None:
        """Capture current ontology as a versioned snapshot."""
        concepts = [
            {"name": r[0], "namespace": r[1], "definition": r[2]}
            for r in self._execute(
                "SELECT name, namespace, definition FROM semantic_concepts ORDER BY name"
            ).fetchall()
        ]
        relations = [
            {
                "predicate": r[0],
                "description": r[1],
                "domain_namespace": r[2],
                "range_namespace": r[3],
                "is_symmetric": bool(r[4]),
            }
            for r in self._execute(
                "SELECT predicate, description, domain_namespace, range_namespace, is_symmetric FROM semantic_relations ORDER BY predicate"
            ).fetchall()
        ]
        self._execute(
            """INSERT OR REPLACE INTO semantic_ontology_versions
               (version_id, concepts_snapshot, relations_snapshot, released_at)
               VALUES (?, ?, ?, ?)""",
            (version_id, json.dumps(concepts), json.dumps(relations), _utc_now()),
        )
        self._conn.commit()

    def get_ontology_version(self, version_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM semantic_ontology_versions WHERE version_id = ?",
            (version_id,),
        ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["concepts_snapshot"] = json.loads(result["concepts_snapshot"])
        result["relations_snapshot"] = json.loads(result["relations_snapshot"])
        return result

    # -- Ontology diff (Sprint 3) --

    def diff_ontology(
        self,
        version_a: str,
        version_b: str,
    ) -> dict[str, Any]:
        """Compare two ontology versions and produce a structured drift report.

        Returns:
            Dict with concepts_added, concepts_removed, concepts_modified,
            relations_added, relations_removed, drift_score, semantic_risk.
        """
        va = self.get_ontology_version(version_a)
        vb = self.get_ontology_version(version_b)

        if va is None:
            return {"error": f"Version '{version_a}' not found"}
        if vb is None:
            return {"error": f"Version '{version_b}' not found"}

        concepts_a = {
            c["name"] + "::" + c["namespace"]: c for c in va["concepts_snapshot"]
        }
        concepts_b = {
            c["name"] + "::" + c["namespace"]: c for c in vb["concepts_snapshot"]
        }

        keys_a = set(concepts_a)
        keys_b = set(concepts_b)

        concepts_added = sorted(keys_b - keys_a)
        concepts_removed = sorted(keys_a - keys_b)

        concepts_modified = []
        for key in keys_a & keys_b:
            ca = concepts_a[key]
            cb = concepts_b[key]
            if ca["definition"] != cb["definition"]:
                concepts_modified.append(
                    {
                        "key": key,
                        "from_definition": ca["definition"],
                        "to_definition": cb["definition"],
                    }
                )

        relations_a = {
            (r["predicate"], r["domain_namespace"], r["range_namespace"])
            for r in va["relations_snapshot"]
        }
        relations_b = {
            (r["predicate"], r["domain_namespace"], r["range_namespace"])
            for r in vb["relations_snapshot"]
        }

        relations_added = sorted(relations_b - relations_a)
        relations_removed = sorted(relations_a - relations_b)

        total_concepts = max(len(keys_a), 1)
        total_changes = (
            len(concepts_added) + len(concepts_removed) + len(concepts_modified)
        )
        drift_score = round(total_changes / total_concepts, 4)

        if drift_score > 0.3:
            semantic_risk = "HIGH"
        elif drift_score > 0.1:
            semantic_risk = "MEDIUM"
        else:
            semantic_risk = "LOW"

        return {
            "version_a": version_a,
            "version_b": version_b,
            "concepts_added": concepts_added,
            "concepts_removed": concepts_removed,
            "concepts_modified": concepts_modified,
            "relations_added": [str(r) for r in relations_added],
            "relations_removed": [str(r) for r in relations_removed],
            "drift_score": drift_score,
            "semantic_risk": semantic_risk,
        }

    # -- Knowledge extraction helper --

    def extract_cycle_knowledge(
        self,
        cycle_id: str,
        channel: str,
        metric_data: dict[str, Any],
        all_metrics_passed: bool,
        asserted_by: str = "analytics",
        observer_id: str | None = None,
    ) -> list[str]:
        """Extract and assert knowledge claims from a completed cycle's metrics.

        Claims are assigned epistemic status based on evidence type:
        - DIRECT_OBSERVATION → VERIFIED
        - STATISTICAL_INFERENCE → INFERRED
        - EXPLICIT_INPUT → ASSUMED
        """
        claim_ids: list[str] = []

        channel_id = self.register_concept(
            channel, "channel", f"Acquisition channel: {channel}"
        )

        lead_id = self.find_concept("lead_generation", "outcome")
        if not lead_id:
            lead_id = self.register_concept(
                "lead_generation", "outcome", "The generation of opt-in leads"
            )
        else:
            lead_id = lead_id["concept_id"]

        eff_id = self.register_concept(
            "campaign_effectiveness", "outcome", "Overall campaign effectiveness score"
        )

        if all_metrics_passed:
            cid = self.assert_claim(
                subject=channel_id,
                predicate="produces_opt_in_leads",
                object=lead_id,
                confidence=0.6,
                evidence_type="DIRECT_OBSERVATION",
                epistemic_status=VERIFIED,
                supporting_data=metric_data,
                source_cycle_id=cycle_id,
                asserted_by=asserted_by,
                observer_id=observer_id,
            )
            claim_ids.append(cid)

        ctr_id = self.find_concept("ctr", "metric")
        if not ctr_id:
            ctr_id = self.register_concept("ctr", "metric", "Click-through rate")
        else:
            ctr_id = ctr_id["concept_id"]

        ctr_val = metric_data.get("ctr", 0)
        if ctr_val > 0:
            cid = self.assert_claim(
                subject=ctr_id,
                predicate="indicates",
                object=eff_id,
                confidence=min(0.9, ctr_val * 10),
                evidence_type="STATISTICAL_INFERENCE",
                epistemic_status=INFERRED,
                supporting_data={"ctr_value": ctr_val, "channel": channel},
                source_cycle_id=cycle_id,
                asserted_by=asserted_by,
                observer_id=observer_id,
            )
            claim_ids.append(cid)

        return claim_ids
