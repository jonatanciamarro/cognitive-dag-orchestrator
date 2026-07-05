#!/usr/bin/env python3
"""Autopilot Scheduler — executa workflows em ciclo contínuo com estado persistente.

Uso:
    python scripts/autopilot.py --workflow workflows/multi_channel_workflow.json \\
        --context examples/content_workflow_context.json \\
        --db .state/autopilot.db --interval 48

Modo cron (recomendado):
    0 */48 * * * cd /caminho/projeto && .venv/bin/python scripts/autopilot.py \\
        --workflow workflows/multi_channel_workflow.json \\
        --context examples/content_workflow_context.json \\
        --db .state/autopilot.db --cron
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Add project to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.campaign_autopilot.cli import run_workflow
from src.campaign_autopilot.memory import MemoryStore
from src.campaign_autopilot.synthesis import KnowledgeSynthesisEngine
from src.campaign_autopilot.semantic_memory import SemanticMemoryStore


class AutopilotRunner:
    """Gerencia execução cíclica de workflows com estado persistente e aprendizado."""

    def __init__(
        self,
        db_path: str | Path,
        workflow_path: str | Path,
        context_path: str | Path,
    ):
        self.db_path = Path(db_path)
        self.workflow_path = str(workflow_path)
        self.context_path = str(context_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize autopilot state table."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS autopilot_cycles (
                cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                steps_completed INTEGER NOT NULL,
                status TEXT NOT NULL,
                output_summary TEXT NOT NULL DEFAULT '{}',
                error_count INTEGER NOT NULL DEFAULT 0,
                total_words_generated INTEGER NOT NULL DEFAULT 0,
                total_videos_generated INTEGER NOT NULL DEFAULT 0,
                total_emails_generated INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def _record_cycle(
        self,
        started_at: str,
        finished_at: str,
        duration_ms: int,
        status: str,
        output: dict[str, Any],
        errors: list[str],
    ) -> int:
        """Record a completed cycle in the database."""
        conn = sqlite3.connect(str(self.db_path))

        # Extract metrics from output
        steps_completed = len(output.get("step_results", {}))
        total_words = 0
        total_videos = 0
        total_emails = 0

        for step_id, step_result in output.get("step_results", {}).items():
            if isinstance(step_result, dict):
                step_out = step_result.get("output", {})
                if isinstance(step_out, dict):
                    total_words += (
                        step_out.get("total_words", 0)
                        if isinstance(step_out.get("total_words"), (int, float))
                        else 0
                    )
                    vids = step_out.get("videos", [])
                    if vids:
                        total_videos += len(vids)
                    total_emails += (
                        step_out.get("total_emails", 0)
                        if isinstance(step_out.get("total_emails"), (int, float))
                        else 0
                    )

        # Also check nested in orchestrator output
        inner_output = output.get("output", {})
        if isinstance(inner_output, dict):
            pubs = inner_output.get("publications", [])
            for pub in pubs if pubs else []:
                total_words += pub.get("word_count", 0)
            total_videos += len(inner_output.get("videos", []))

        conn.execute(
            """INSERT INTO autopilot_cycles
               (workflow, started_at, finished_at, duration_ms, steps_completed,
                status, output_summary, error_count, total_words_generated,
                total_videos_generated, total_emails_generated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                self.workflow_path,
                started_at,
                finished_at,
                duration_ms,
                steps_completed,
                status,
                json.dumps(
                    {
                        "publications": len(inner_output.get("publications", [])),
                        "videos": total_videos,
                        "emails": total_emails,
                        "steps": steps_completed,
                    }
                ),
                len(errors),
                total_words,
                total_videos,
                total_emails,
            ),
        )
        cycle_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()
        return cycle_id

    def _run_feedback_cycle(self, cycle_id: int, output: dict[str, Any]) -> None:
        """Feed outcomes back into semantic memory for learning."""
        try:
            with MemoryStore(str(self.db_path)) as store:
                sem = SemanticMemoryStore(store._conn)

                # Run knowledge synthesis
                engine = KnowledgeSynthesisEngine(sem)
                engine.synthesize(cycle_id=f"autopilot_{cycle_id}")

                # Extract lessons from analytics_feedback
                sr = output.get("step_results", {})
                fb = sr.get("analytics_feedback", {})
                if isinstance(fb, dict):
                    fb_out = fb.get("output", {})
                    if isinstance(fb_out, dict):
                        lessons = fb_out.get("lessons", [])
                        suggestions = fb_out.get("suggestions", [])
                        score = fb_out.get("cycle_summary", {}).get(
                            "cycle_quality_score", 0
                        )
                        if lessons:
                            lessons_concept = sem.find_concept(
                                "autopilot_lessons", "knowledge"
                            )
                            if not lessons_concept:
                                lid = sem.register_concept(
                                    "autopilot_lessons",
                                    "knowledge",
                                    "Lessons from autopilot cycles",
                                )
                            else:
                                lid = lessons_concept["concept_id"]

                            for i, lesson in enumerate(lessons):
                                lc = sem.register_concept(
                                    f"auto_lesson_{cycle_id}_{i}",
                                    "knowledge",
                                    lesson[:200],
                                )
                                sem.assert_claim(
                                    subject=lid,
                                    predicate="includes",
                                    object=lc,
                                    confidence=min(0.9, score / 100.0 + 0.3),
                                    evidence_type="DIRECT_OBSERVATION",
                                    epistemic_status="VERIFIED",
                                    supporting_data={
                                        "cycle_id": cycle_id,
                                        "score": score,
                                    },
                                    source_cycle_id=f"autopilot_{cycle_id}",
                                    asserted_by="autopilot",
                                    observer_id="autopilot",
                                )

        except Exception as exc:
            print(f"  ⚠ Feedback cycle warning: {exc}")

    def _generate_report(
        self, output: dict[str, Any], duration_ms: int, cycle_id: int
    ) -> str:
        """Generate a human-readable report of the cycle."""
        sr = output.get("step_results", {})
        errors = output.get("errors", [])

        report_parts = [
            f"🤖 Autopilot Cycle #{cycle_id}",
            f"   Workflow: {self.workflow_path}",
            f"   Duration: {duration_ms}ms",
            f"   Steps: {len(sr)} completed, {len(errors)} errors",
        ]

        for step_id, result in sr.items():
            if isinstance(result, dict):
                report_parts.append(
                    f"   ✓ {step_id}: {result.get('status', '?')} ({result.get('duration_ms', '?')}ms)"
                )

        if errors:
            report_parts.append(f"\n   ❌ Errors: {len(errors)}")
            for err in errors[:3]:
                report_parts.append(f"      - {err}")

        # Content summary
        inner = (
            output.get("output", {})
            if isinstance(output.get("output"), dict)
            else output
        )
        pubs = (
            inner.get("publications", inner.get("output", {}).get("publications", []))
            if isinstance(inner, dict)
            else []
        )
        if pubs:
            report_parts.append(f"\n   📝 Published: {len(pubs)} articles")
        if inner.get("total_emails", 0) or inner.get("videos", []):
            report_parts.append(f"   🎬 Videos: {len(inner.get('videos', []))}")
            report_parts.append(f"   📧 Emails: {inner.get('total_emails', 0)}")

        return "\n".join(report_parts)

    def run(self) -> dict[str, Any]:
        """Execute one cycle."""
        started_at = datetime.now(timezone.utc).isoformat()
        print(f"\n{'=' * 50}")
        print(f"🚀 Autopilot Cycle — {started_at}")
        print(f"{'=' * 50}")

        try:
            result = run_workflow(
                self.context_path, self.workflow_path, str(self.db_path)
            )
            finished_at = datetime.now(timezone.utc).isoformat()

            # Calculate duration from the orchestrator output
            output_data = result.get("output", {})
            if isinstance(output_data, dict):
                duration_ms = output_data.get("duration_ms", 0)
                status = output_data.get("status", "completed")
                step_results = output_data.get("step_results", {})
                errors = output_data.get("errors", [])
            else:
                duration_ms = 0
                status = "completed"
                step_results = {}
                errors = []

            cycle_id = self._record_cycle(
                started_at, finished_at, duration_ms, status, output_data, errors
            )

            # Run feedback cycle
            self._run_feedback_cycle(cycle_id, output_data)

            # Generate report
            report = self._generate_report(output_data, duration_ms, cycle_id)
            print(report)

            # Save report to file
            report_dir = self.db_path.parent / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            report_file = report_dir / f"cycle_{cycle_id}.txt"
            report_file.write_text(
                report + f"\n\n(Full output: {json.dumps(result, indent=2)[:2000]}...)"
            )

            return {"cycle_id": cycle_id, "status": "success", "report": report}

        except Exception as exc:
            finished_at = datetime.now(timezone.utc).isoformat()
            print(f"\n❌ Cycle failed: {exc}")
            return {"cycle_id": -1, "status": "failed", "error": str(exc)}

    def run_loop(self, interval_hours: int) -> None:
        """Run continuously with interval."""
        print(f"🔄 Autopilot loop started — interval: {interval_hours}h")
        print(f"   Workflow: {self.workflow_path}")
        print(f"   Context: {self.context_path}")
        print(f"   Database: {self.db_path}")
        print("   Ctrl+C to stop\n")

        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                result = self.run()

                if cycle_count % 5 == 0:
                    # Show summary every 5 cycles
                    conn = sqlite3.connect(str(self.db_path))
                    row = conn.execute(
                        "SELECT COUNT(*), SUM(total_words_generated), SUM(total_videos_generated), SUM(total_emails_generated) FROM autopilot_cycles"
                    ).fetchone()
                    conn.close()
                    print(f"\n📊 Autopilot Stats ({cycle_count} cycles):")
                    print(f"   Total cycles: {row[0]}")
                    print(f"   Words generated: {row[1] or 0}")
                    print(f"   Videos generated: {row[2] or 0}")
                    print(f"   Emails generated: {row[3] or 0}")

            except KeyboardInterrupt:
                print(f"\n🛑 Autopilot stopped after {cycle_count} cycles.")
                break
            except Exception as exc:
                print(f"\n⚠️ Cycle error (continuing): {exc}")

            print(f"\n⏳ Next cycle in {interval_hours}h...")
            try:
                time.sleep(interval_hours * 3600)
            except KeyboardInterrupt:
                print(f"\n🛑 Autopilot stopped after {cycle_count} cycles.")
                break


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autopilot", description="Campaign Autopilot Scheduler"
    )
    parser.add_argument("--workflow", required=True, help="Workflow JSON file")
    parser.add_argument("--context", required=True, help="Context JSON file")
    parser.add_argument(
        "--db", default=".state/autopilot.db", help="State database path"
    )
    parser.add_argument(
        "--interval", type=int, default=48, help="Hours between cycles (default: 48)"
    )
    parser.add_argument(
        "--cron",
        action="store_true",
        help="Run single cycle (for cron). Default mode is single cycle.",
    )
    parser.add_argument(
        "--loop", action="store_true", help="Run in continuous loop mode"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show autopilot stats and exit"
    )
    return parser


def show_stats(db_path: str) -> None:
    """Show autopilot statistics."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(duration_ms), 0), COALESCE(SUM(total_words_generated), 0), COALESCE(SUM(total_videos_generated), 0), COALESCE(SUM(total_emails_generated), 0), COALESCE(AVG(duration_ms), 0) FROM autopilot_cycles"
        ).fetchone()
        last = conn.execute(
            "SELECT * FROM autopilot_cycles ORDER BY cycle_id DESC LIMIT 1"
        ).fetchone()

        print("📊 Autopilot Statistics")
        print(f"   Total cycles: {rows[0]}")
        print(f"   Total time: {rows[1] / 1000:.1f}s")
        print(f"   Words generated: {rows[2]}")
        print(f"   Videos generated: {rows[3]}")
        print(f"   Emails generated: {rows[4]}")
        print(f"   Avg cycle time: {rows[5]:.0f}ms")
        if last:
            print(f"\n   Last cycle: #{last[0]} at {last[3]} ({last[6]})")
    finally:
        conn.close()


def main() -> None:
    args = build_parser().parse_args()

    runner = AutopilotRunner(
        db_path=args.db,
        workflow_path=args.workflow,
        context_path=args.context,
    )

    if args.stats:
        show_stats(args.db)
    elif args.loop:
        runner.run_loop(interval_hours=args.interval)
    else:
        # Single cycle mode (used by cron or CLI)
        runner.run()


if __name__ == "__main__":
    main()
