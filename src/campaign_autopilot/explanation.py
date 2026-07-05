from __future__ import annotations

import json
import uuid
import threading
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


EXPLANATION_TEMPLATES: dict[str, dict[str, str]] = {
    "operator": {
        "policy_gate": ("Blocked at {gate_name}: {reason}. Required by {rule_source}."),
        "metrics_gate": ("Metrics {outcome}: {summary}. {threshold_detail}"),
        "optimization_proposal": (
            "Proposed {change}. Based on {evidence_count} observation(s). "
            "Confidence: {confidence:.0%}."
        ),
        "approval_gate": ("Cycle {outcome}. {detail}"),
        "compliance_gate": (
            "Compliance {outcome}: {reason}. Counterfactual: {counterfactual}"
        ),
        "default": ("Decision by {agent_id}: {outcome}. {detail}"),
    },
    "compliance": {
        "policy_gate": (
            "Compliance check at {timestamp}: {outcome}. "
            "Rule: {rule_source}. "
            "Expected: {rule_value}. Actual: {actual_value}. "
            "Provenance: {decision_id}"
        ),
        "compliance_gate": (
            "Compliance gate at {timestamp}: {outcome}. "
            "Audience: {audience}. Consent scope: {consent_scope}. "
            "Blocking rules: {failed_rules}. "
            "Decision ID: {decision_id}"
        ),
        "default": (
            "Decision: {outcome}. Agent: {agent_id}. "
            "Timestamp: {timestamp}. Decision ID: {decision_id}"
        ),
    },
    "cto": {
        "default": (
            "Decision: {output_decision}. "
            "Input state: {input_state}. "
            "Rules evaluated: {rules_count}. "
            "Failed rules: {failed_rules}. "
            "Duration: {duration_ms}ms. "
            "Decision ID: {decision_id}"
        ),
    },
}


def _render_template(
    template: str,
    **kwargs: Any,
) -> str:
    """Safely render a template string with keyword args, falling back to '?' for missing keys."""
    try:
        return template.format(**kwargs)
    except KeyError:
        # Fall back to partial rendering for missing keys
        import re

        def _replace(match: re.Match) -> str:
            key = match.group(1)
            return str(kwargs.get(key, "?"))

        return re.sub(r"\{(\w+)\}", _replace, template)


class ExplanationStore:
    """Records and queries structured explanations for every decision point.

    Each decision produces a DecisionPoint record with input state, output decision,
    rule applications, and rendered explanations for each observer role.
    """

    def __init__(self, conn: Any):
        self._conn = conn
        self._lock = threading.Lock()
        self._ensure_schema()

    def _execute(self, sql: str, params=None):
        with self._lock:
            if params is not None:
                return self._conn.execute(sql, params)
            return self._conn.execute(sql)

    def _ensure_schema(self) -> None:
        # Each statement is executed individually with autocommit
        self._execute(
            """CREATE TABLE IF NOT EXISTS explanation_decisions (
                decision_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                cycle_id TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                input_state TEXT NOT NULL DEFAULT '{}',
                output_decision TEXT NOT NULL DEFAULT '{}',
                parent_decision_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (parent_decision_id) REFERENCES explanation_decisions(decision_id)
            )"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_exp_decisions_cycle
                ON explanation_decisions(cycle_id)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_exp_decisions_agent
                ON explanation_decisions(agent_id)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_exp_decisions_type
                ON explanation_decisions(decision_type)"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_exp_decisions_parent
                ON explanation_decisions(parent_decision_id)"""
        )
        self._execute(
            """CREATE TABLE IF NOT EXISTS explanation_rule_applications (
                rule_app_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL REFERENCES explanation_decisions(decision_id),
                rule_source TEXT NOT NULL,
                rule_value TEXT NOT NULL,
                actual_value TEXT NOT NULL,
                comparison_result INTEGER NOT NULL,
                rule_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_exp_rules_decision
                ON explanation_rule_applications(decision_id)"""
        )
        self._execute(
            """CREATE TABLE IF NOT EXISTS explanation_counterfactuals (
                counterfactual_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL REFERENCES explanation_decisions(decision_id),
                changed_field TEXT NOT NULL,
                changed_from TEXT,
                changed_to TEXT,
                predicted_outcome TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 0.8,
                created_at TEXT NOT NULL
            )"""
        )
        self._execute(
            """CREATE INDEX IF NOT EXISTS idx_exp_counterfactuals_decision
                ON explanation_counterfactuals(decision_id)"""
        )

    # -- Decision recording --

    def record_decision(
        self,
        agent_id: str,
        cycle_id: str,
        decision_type: str,
        input_state: dict[str, Any] | None = None,
        output_decision: dict[str, Any] | None = None,
        parent_decision_id: str | None = None,
    ) -> str:
        """Record a decision point. Returns decision_id."""
        decision_id = _new_id()
        self._execute(
            """INSERT INTO explanation_decisions
               (decision_id, agent_id, cycle_id, decision_type, input_state,
                output_decision, parent_decision_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                decision_id,
                agent_id,
                cycle_id,
                decision_type,
                json.dumps(input_state or {}),
                json.dumps(output_decision or {}),
                parent_decision_id,
                _utc_now(),
            ),
        )
        self._conn.commit()
        return decision_id

    def update_decision_output(
        self,
        decision_id: str,
        output_decision: dict[str, Any],
    ) -> None:
        """Update the output decision after it's been computed."""
        self._execute(
            "UPDATE explanation_decisions SET output_decision = ? WHERE decision_id = ?",
            (json.dumps(output_decision), decision_id),
        )
        self._conn.commit()

    # -- Rule application recording --

    def record_rule_application(
        self,
        decision_id: str,
        rule_source: str,
        rule_value: Any,
        actual_value: Any,
        comparison_result: bool,
        rule_order: int = 0,
    ) -> str:
        """Record a specific rule application within a decision. Returns rule_app_id."""
        rule_app_id = _new_id()
        self._execute(
            """INSERT INTO explanation_rule_applications
               (rule_app_id, decision_id, rule_source, rule_value, actual_value,
                comparison_result, rule_order, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                rule_app_id,
                decision_id,
                rule_source,
                json.dumps(rule_value)
                if not isinstance(rule_value, str)
                else rule_value,
                json.dumps(actual_value)
                if not isinstance(actual_value, str)
                else actual_value,
                int(bool(comparison_result)),
                rule_order,
                _utc_now(),
            ),
        )
        self._conn.commit()
        return rule_app_id

    # -- Counterfactual recording --

    def record_counterfactual(
        self,
        decision_id: str,
        changed_field: str,
        changed_from: Any,
        changed_to: Any,
        predicted_outcome: str,
        confidence: float = 0.8,
    ) -> str:
        """Record a counterfactual for a decision."""
        cf_id = _new_id()
        self._execute(
            """INSERT INTO explanation_counterfactuals
               (counterfactual_id, decision_id, changed_field, changed_from,
                changed_to, predicted_outcome, confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cf_id,
                decision_id,
                changed_field,
                json.dumps(changed_from)
                if not isinstance(changed_from, str)
                else str(changed_from),
                json.dumps(changed_to)
                if not isinstance(changed_to, str)
                else str(changed_to),
                predicted_outcome,
                min(1.0, max(0.0, confidence)),
                _utc_now(),
            ),
        )
        self._conn.commit()
        return cf_id

    def _try_json_load(self, value: str) -> Any:
        """Try to parse a value as JSON, falling back to the raw string."""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError, ValueError):
            return value

    def compute_counterfactual(
        self,
        decision_id: str,
    ) -> dict[str, Any] | None:
        """Compute what single change would flip the decision outcome.

        Inspects failed rules and determines the minimal change needed.
        """
        rules = self._execute(
            """SELECT rule_source, rule_value, actual_value, comparison_result, rule_order
               FROM explanation_rule_applications
               WHERE decision_id = ? ORDER BY rule_order ASC""",
            (decision_id,),
        ).fetchall()

        # Find first failed rule
        for rule in rules:
            if not rule[3]:  # comparison_result is False
                rule_val = self._try_json_load(rule[1])
                actual_val = self._try_json_load(rule[2])

                predicted = "pass"
                if isinstance(rule_val, bool):
                    predicted = "pass"
                elif isinstance(rule_val, (int, float)):
                    predicted = f"would change to {rule_val}"
                else:
                    predicted = "changed"

                return {
                    "decision_id": decision_id,
                    "changed_field": rule[0],
                    "changed_from": actual_val,
                    "changed_to": rule_val,
                    "predicted_outcome": predicted,
                    "confidence": 0.8,
                }

        return None

    # -- Explanation rendering --

    def render_explanation(
        self,
        decision_id: str,
        observer_role: str = "operator",
    ) -> str:
        """Render a human-readable explanation for a given decision and observer."""
        decision = self._execute(
            "SELECT * FROM explanation_decisions WHERE decision_id = ?",
            (decision_id,),
        ).fetchone()
        if decision is None:
            return f"Decision {decision_id} not found."

        decision = dict(decision)
        rules = [
            dict(r)
            for r in self._execute(
                "SELECT * FROM explanation_rule_applications WHERE decision_id = ? ORDER BY rule_order",
                (decision_id,),
            ).fetchall()
        ]

        failed_rules = [r for r in rules if not r["comparison_result"]]
        output = json.loads(decision["output_decision"])
        outcome = output.get("status", output.get("outcome", "completed"))

        # Override outcome based on failed rules if output doesn't have a status
        if "status" not in output and failed_rules:
            outcome = "blocked"
        elif "status" not in output and not failed_rules:
            outcome = "passed"

        templates = EXPLANATION_TEMPLATES.get(
            observer_role, EXPLANATION_TEMPLATES["operator"]
        )
        template_key = (
            decision["decision_type"]
            if decision["decision_type"] in templates
            else "default"
        )
        template = templates.get(template_key, templates["default"])

        # Build context for template
        ctx: dict[str, Any] = {
            "decision_id": decision["decision_id"],
            "agent_id": decision["agent_id"],
            "cycle_id": decision["cycle_id"],
            "decision_type": decision["decision_type"],
            "timestamp": decision["created_at"],
            "outcome": outcome,
            "gate_name": decision["decision_type"].replace("_", " ").title(),
            "reason": failed_rules[0]["rule_source"] if failed_rules else "None",
            "rule_source": failed_rules[0]["rule_source"] if failed_rules else "N/A",
            "rule_value": failed_rules[0]["rule_value"] if failed_rules else "N/A",
            "actual_value": failed_rules[0]["actual_value"] if failed_rules else "N/A",
            "rules_count": len(rules),
            "failed_rules": ", ".join(r["rule_source"] for r in failed_rules)
            if failed_rules
            else "None",
            "summary": f"{len(rules)} rule(s) evaluated, {len(failed_rules)} failed",
            "threshold_detail": (
                f"Failed rules: {', '.join(r['rule_source'] for r in failed_rules)}"
                if failed_rules
                else "All thresholds met."
            ),
            "detail": (
                f"{len(rules)} rule(s) applied. "
                f"{'Blocked by: ' + failed_rules[0]['rule_source'] if failed_rules else 'All checks passed.'}"
            ),
            "input_state": decision.get("input_state", "{}"),
            "output_decision": decision.get("output_decision", "{}"),
            "duration_ms": 0,
            "evidence_count": len(rules),
            "change": output.get("proposal", output.get("action", "N/A")),
            "confidence": output.get("confidence", 0.5),
            # Compliance-specific
            "audience": json.loads(decision["input_state"]).get("audience", "unknown"),
            "consent_scope": json.loads(decision["input_state"]).get(
                "consent_scope", "unknown"
            ),
            "counterfactual": "N/A",
        }

        # Try to get counterfactual
        cf_row = self._execute(
            "SELECT * FROM explanation_counterfactuals WHERE decision_id = ? LIMIT 1",
            (decision_id,),
        ).fetchone()
        if cf_row:
            cf = dict(cf_row)
            ctx["counterfactual"] = (
                f"If {cf['changed_field']} was {cf['changed_to']}, outcome would be {cf['predicted_outcome']}"
            )

        return _render_template(template, **ctx)

    def render_provenance_chain(
        self,
        decision_id: str,
        fmt: str = "text",
    ) -> str:
        """Render full provenance chain for a decision."""
        if fmt == "json":
            chain = self._build_provenance_chain(decision_id)
            return json.dumps(chain, indent=2)

        lines: list[str] = []
        current_id: str | None = decision_id
        depth = 0
        while current_id:
            decision = self._execute(
                "SELECT * FROM explanation_decisions WHERE decision_id = ?",
                (current_id,),
            ).fetchone()
            if decision is None:
                break
            d = dict(decision)
            indent = "  " * depth
            lines.append(f"{indent}├─ Decision: {d['decision_id']}")
            lines.append(f"{indent}│  Agent: {d['agent_id']}")
            lines.append(f"{indent}│  Type: {d['decision_type']}")
            lines.append(
                f"{indent}│  Outcome: {json.loads(d['output_decision']).get('status', '?')}"
            )
            lines.append(f"{indent}│  Time: {d['created_at']}")

            rules = self._execute(
                "SELECT * FROM explanation_rule_applications WHERE decision_id = ? ORDER BY rule_order",
                (current_id,),
            ).fetchall()
            for rule in rules:
                r = dict(rule)
                mark = "✓" if r["comparison_result"] else "✗"
                lines.append(f"{indent}│  {mark} {r['rule_source']}")

            current_id = d.get("parent_decision_id")
            depth += 1

        if not lines:
            return f"Decision {decision_id} not found."

        lines.insert(0, "Provenance Chain:")
        return "\n".join(lines)

    # -- Querying --

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        row = self._execute(
            "SELECT * FROM explanation_decisions WHERE decision_id = ?",
            (decision_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_decisions_for_cycle(self, cycle_id: str) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM explanation_decisions WHERE cycle_id = ? ORDER BY created_at ASC",
            (cycle_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_rules_applied(self, decision_id: str) -> list[dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM explanation_rule_applications WHERE decision_id = ? ORDER BY rule_order",
            (decision_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_failed_rules(self, decision_id: str) -> list[dict[str, Any]]:
        rows = self._execute(
            """SELECT * FROM explanation_rule_applications
               WHERE decision_id = ? AND comparison_result = 0
               ORDER BY rule_order""",
            (decision_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Helpers --

    def _build_provenance_chain(
        self,
        decision_id: str,
    ) -> list[dict[str, Any]]:
        chain: list[dict[str, Any]] = []
        current_id: str | None = decision_id
        while current_id:
            decision = self.get_decision(current_id)
            if decision is None:
                break
            rules = self.get_rules_applied(current_id)
            decision["rules"] = rules
            chain.append(decision)
            current_id = decision.get("parent_decision_id")
        return chain
