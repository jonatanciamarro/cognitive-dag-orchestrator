from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agents.base import CampaignContext
from .agents.orchestrator import CampaignOrchestrator
from .memory import MemoryStore
from .metrics import calculate_metrics
from .models import Campaign, Event, Policy
from .policy import PolicyEngine


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_event_timestamp(value: Any) -> datetime:
    if value is None:
        return _utcnow()
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _build_event(payload: dict[str, Any], campaign_id: str) -> Event:
    raw = dict(payload)
    raw_campaign_id = str(raw.get("campaign_id", campaign_id))
    occurred_at = _parse_event_timestamp(raw.get("occurred_at"))
    kind = str(raw.get("kind", "")).strip().lower()
    value = float(raw.get("value", 0.0) or 0.0)
    count = int(raw.get("count", 1) or 1)
    metadata = dict(raw.get("metadata", {}))
    event_id = raw.get("event_id")
    if not event_id:
        stable_payload = {
            "campaign_id": raw_campaign_id,
            "occurred_at": occurred_at.isoformat(),
            "kind": kind,
            "value": value,
            "count": count,
            "metadata": metadata,
        }
        event_id = MemoryStore.stable_event_id(stable_payload)
    return Event(
        event_id=str(event_id),
        campaign_id=raw_campaign_id,
        kind=kind,
        occurred_at=occurred_at,
        value=value,
        count=count,
        metadata=metadata,
    )


def _load_payload(path: Path) -> dict[str, Any] | list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_context(path: Path) -> CampaignContext:
    payload = _load_payload(path)
    if not isinstance(payload, dict):
        raise ValueError("Workflow context must be a JSON object.")
    return CampaignContext.from_mapping(payload)


def _load_input(path: Path) -> tuple[Campaign, list[Event], Policy]:
    payload = _load_payload(path)
    policy = Policy()
    campaign_data: dict[str, Any] | None = None
    events_payload: list[dict[str, Any]] = []

    if isinstance(payload, list):
        events_payload = payload
    elif isinstance(payload, dict):
        policy = (
            Policy.from_dict(payload.get("policy", {}))
            if payload.get("policy")
            else policy
        )
        if isinstance(payload.get("campaign"), dict):
            campaign_data = dict(payload["campaign"])
        elif "campaign_id" in payload:
            campaign_data = {"campaign_id": payload["campaign_id"]}
        events = payload.get("events", [])
        if isinstance(events, list):
            events_payload = events
        elif events:
            raise ValueError("Top-level 'events' must be a list.")
    else:
        raise ValueError("Event file must contain either a JSON object or array.")

    if not events_payload:
        raise ValueError("Event file did not contain any events.")

    first_event = dict(events_payload[0])
    nested_campaign = (
        first_event.get("campaign")
        if isinstance(first_event.get("campaign"), dict)
        else None
    )
    campaign_id = str(
        (campaign_data or {}).get("campaign_id")
        or first_event.get("campaign_id")
        or (nested_campaign or {}).get("campaign_id")
        or ""
    )
    if not campaign_id:
        raise ValueError("Unable to determine campaign_id from input.")

    if campaign_data is None:
        campaign_data = dict(nested_campaign or {})
        campaign_data.setdefault("campaign_id", campaign_id)
    elif nested_campaign:
        merged = dict(nested_campaign)
        merged.update(campaign_data)
        campaign_data = merged

    campaign_data.setdefault("campaign_id", campaign_id)
    campaign_data.setdefault("name", campaign_id)
    campaign_data.setdefault("opt_in", False)
    campaign_data.setdefault("compliance_ok", True)
    campaign_data.setdefault("budget", 0.0)
    campaign_data.setdefault("spend", 0.0)
    campaign_data.setdefault("revenue", 0.0)
    campaign = Campaign.from_dict(campaign_data)

    events = []
    for raw_event in events_payload:
        events.append(_build_event(raw_event, campaign.campaign_id))

    return campaign, events, policy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="campaign-autopilot")
    parser.add_argument(
        "--events", help="Path to a JSON file containing campaign events."
    )
    parser.add_argument(
        "--workflow",
        help="Path to a workflow JSON file. When set, the CLI launches the multi-agent orchestrator.",
    )
    parser.add_argument(
        "--context",
        help="Path to a JSON file containing workflow context. Required with --workflow.",
    )
    parser.add_argument(
        "--db",
        default="campaign_autopilot.sqlite3",
        help="Path to the SQLite memory store.",
    )
    parser.add_argument(
        "--providers",
        action="store_true",
        help="Show available media providers and exit.",
    )
    return parser


def run_cycle(events_path: str | Path, db_path: str | Path) -> dict[str, Any]:
    campaign, events, policy = _load_input(Path(events_path))
    with MemoryStore(db_path) as store:
        store.upsert_campaign(campaign)
        store.record_events(events)
        stored_events = store.list_events(campaign.campaign_id)

    metrics = calculate_metrics(stored_events)
    decision_plan = PolicyEngine(policy).evaluate(campaign, metrics)
    return decision_plan.to_dict()


def run_workflow(
    context_path: str | Path,
    workflow_path: str | Path,
    db_path: str | Path = "campaign_autopilot.sqlite3",
) -> dict[str, Any]:
    context = _load_context(Path(context_path))
    with MemoryStore(db_path) as store:
        orchestrator = CampaignOrchestrator(
            workflow_path=workflow_path,
            memory_store=store,
        )
        result = orchestrator.run(context).to_dict()
    return result


def _show_providers() -> None:
    """Display available media providers using the layered architecture."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

    _console = Console()

    try:
        from campaign_autopilot.media_providers import ProviderManager

        pm = ProviderManager.get_instance()
        report = pm.get_full_report()

        _console.print(
            Panel(
                "[bold]📡 Media Provider Status — Layered Architecture[/bold]",
                box=box.HEAVY,
            )
        )

        # Overview table
        table = Table(box=box.ROUNDED)
        table.add_column("Camada", style="cyan")
        table.add_column("Ativo", style="green")
        table.add_column("Providers", style="yellow")
        table.add_row(
            "[bold]📝 TEXT[/bold]",
            report["text"]["best"],
            str(report["text"]["available"]),
        )
        table.add_row(
            "[bold]🖼️ IMAGE[/bold]",
            report["image"]["best"],
            str(report["image"]["available"]),
        )
        table.add_row(
            "[bold]🎤 AUDIO[/bold]",
            report["audio"]["best"],
            str(report["audio"]["available"]),
        )
        table.add_row(
            "[bold]🎵 MUSIC[/bold]",
            report["music"]["best"],
            str(report["music"]["available"]),
        )
        table.add_row(
            "[bold]🎬 VIDEO[/bold]",
            report["video"]["best"],
            str(report["video"]["available"]),
        )
        _console.print(table)

        cost_stats = report.get("costs", {})
        _console.print("\n[bold]💵 Cost Tracking[/bold]")
        _console.print(f"  Total calls: {cost_stats.get('total_calls', 0)}")

        # Tips panel
        _console.print(
            Panel(
                "[bold]Para instalar providers melhores:[/bold]\n"
                "  pip install litellm          # 100+ LLM models (OpenRouter, Groq, etc.)\n"
                "  pip install replicate        # AI image gen (free tier)\n"
                "  pip install torch diffusers  # Local AI image gen (needs GPU)\n"
                "  pip install audiocraft       # AI music generation (local)\n\n"
                "[dim]Configure LLM API keys in .env:[/dim]\n"
                "    GROQ_API_KEY=...    # Fastest free LLM\n"
                "    OPENROUTER_API_KEY=... # 200+ models\n"
                "    GEMINI_API_KEY=...  # Google Gemini free tier\n\n"
                "[green]Zero config: stdlib template engine sempre funciona como fallback.[/green]",
                title="💡 Dica",
                box=box.SIMPLE,
            )
        )
    except ImportError:
        _console.print("[red]Media providers module not available.[/red]")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.providers:
        _show_providers()
        return 0
    if args.workflow:
        if not args.context:
            raise SystemExit("--context is required when --workflow is provided.")
        plan = run_workflow(args.context, args.workflow, args.db)
    else:
        if not args.events:
            raise SystemExit("--events is required when --workflow is not provided.")
        plan = run_cycle(args.events, args.db)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
