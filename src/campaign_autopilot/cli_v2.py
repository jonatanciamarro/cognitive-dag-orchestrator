"""CLI v2 — Interface de linha de comando com OrchestratorV2.

Usa o novo orchestrator que fecha todos os loops (1ª, 2ª e 3ª ordem).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .memory import MemoryStore
from .logging_utils import StructuredLogger, configure_logging

log = StructuredLogger("cli_v2")


def _load_context(path: str | Path) -> dict[str, Any]:
    """Load campaign context from JSON file."""
    p = Path(path)
    if not p.exists():
        log.error("context_not_found", path=str(p))
        print(f"❌ Context file not found: {p}")
        sys.exit(1)
    with open(p) as f:
        return json.load(f)


def run_workflow_v2(
    context_path: str | Path,
    workflow_path: str | Path,
    db_path: str | Path = ".state/autopilot.db",
    mode: str = "full",
) -> dict[str, Any]:
    """Run a complete cycle with OrchestratorV2 (all 3 orders)."""
    context_data = _load_context(context_path)
    from .agents.base import CampaignContext

    ctx = CampaignContext.from_mapping(context_data)

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with MemoryStore(str(db_path)) as store:
        from .orchestrator_v2 import create_orchestrator

        orch = create_orchestrator(
            workflow_path=workflow_path,
            memory_store=store,
            mode=mode,
        )
        log.info("orchestrator_started", workflow=str(workflow_path), mode=mode)
        result = orch.run(ctx)
        log.info("orchestrator_completed", status=result.status)

        # Save result to disk
        result_path = db_path.parent / f"result_{ctx.run_id[:8]}.json"
        result_dict = result.to_dict() if hasattr(result, "to_dict") else result
        with open(result_path, "w") as f:
            json.dump(result_dict, f, indent=2, default=str)

        return (
            result_dict
            if isinstance(result_dict, dict)
            else {"status": str(result.status)}
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="campaign-autopilot-v2",
        description="Campaign Autopilot v2 — Sistema de Marketing 100% Orgânico com Auto-Evolução",
    )
    parser.add_argument("--workflow", required=True, help="Workflow JSON file")
    parser.add_argument("--context", required=True, help="Context JSON file")
    parser.add_argument(
        "--db", default=".state/autopilot.db", help="SQLite database path"
    )
    parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "first_order", "first_second", "first_third"],
        help="Orchestration mode (default: full = all 3 orders)",
    )
    parser.add_argument(
        "--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    os.environ["AUTOPILOT_LOG_LEVEL"] = args.log_level.upper()
    configure_logging(level=args.log_level, component="cli_v2")

    print(f"🚀 Campaign Autopilot v2 — Mode: {args.mode}")
    print(f"   Workflow: {args.workflow}")
    print(f"   Context: {args.context}")
    print(f"   Database: {args.db}")
    print()

    result = run_workflow_v2(
        context_path=args.context,
        workflow_path=args.workflow,
        db_path=args.db,
        mode=args.mode,
    )

    print(json.dumps(result, indent=2, default=str)[:2000])
    print()
    status = result.get("status", "unknown")
    if status == "success":
        print("✅ Cycle completed successfully")
    else:
        print(f"⚠️  Cycle completed with status: {status}")

    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
