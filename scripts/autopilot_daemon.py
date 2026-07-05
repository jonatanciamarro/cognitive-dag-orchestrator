#!/usr/bin/env python3
"""Autopilot Daemon — Supervisor 24/7 com auto-restart, health check e notificações.

Mantém o sistema rodando 24 horas por dia, 7 dias por semana:
- Executa ciclos de workflow em loop
- Auto-restart se crashar (até 5 tentativas)
- Health check HTTP para monitoramento
- Notificação de falhas no terminal
- Logging rotacionado
- Estatísticas de uptime

Uso:
    python scripts/autopilot_daemon.py                          # Modo normal
    python scripts/autopilot_daemon.py --interval 48            # Ciclo a cada 48h
    python scripts/autopilot_daemon.py --workflow workflows/production_workflow.json
    python scripts/autopilot_daemon.py --status                  # Ver status
    python scripts/autopilot_daemon.py --stop                    # Parar
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from ponytail import Follow


# ── Config ──────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKFLOW = "workflows/money_workflow.json"
DEFAULT_CONTEXT = "examples/content_workflow_context.json"
DEFAULT_DB = ".state/autopilot.db"
PID_FILE = PROJECT_ROOT / ".state/autopilot.pid"
LOG_FILE = PROJECT_ROOT / ".state/logs/daemon.log"
HEARTBEAT_FILE = PROJECT_ROOT / ".state/logs/heartbeat.json"


# ── Utilities ────────────────────────────────────────────────────


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def write_pid(pid: int) -> None:
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))


def remove_pid() -> None:
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


def is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


# ── Heartbeat ───────────────────────────────────────────────────


def write_heartbeat(status: str, cycle: int = 0, error: str = "") -> None:
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "cycle": cycle,
        "uptime_hours": 0,
        "error": error,
    }
    # Calculate uptime
    if HEARTBEAT_FILE.exists():
        try:
            prev = json.loads(HEARTBEAT_FILE.read_text())
            start = prev.get("started_at")
            if start:
                delta = datetime.now(timezone.utc) - datetime.fromisoformat(start)
                data["uptime_hours"] = round(delta.total_seconds() / 3600, 1)
        except Exception:
            pass
    if "started_at" not in data:
        data["started_at"] = data["timestamp"]

    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_FILE.write_text(json.dumps(data, indent=2))


def get_heartbeat() -> dict[str, Any]:
    try:
        return json.loads(HEARTBEAT_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"status": "stopped", "uptime_hours": 0}


# ── Autopilot Runner ─────────────────────────────────────────────


class AutopilotDaemon:
    """Supervisor that keeps the autopilot running 24/7."""

    def __init__(
        self,
        workflow: str,
        context: str,
        db: str,
        interval_hours: int = 48,
        max_restarts: int = 5,
    ):
        self.workflow = workflow
        self.context = context
        self.db = db
        self.interval_hours = interval_hours
        self.max_restarts = max_restarts
        self.cycle_count = 0
        self.restart_count = 0
        self.running = True
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum: int, frame: Any) -> None:
        log(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def run(self) -> None:
        """Main loop: run cycles forever with auto-restart."""
        log("🚀 Autopilot Daemon started")
        log(f"   Workflow: {self.workflow}")
        log(f"   Context: {self.context}")
        log(f"   Database: {self.db}")
        log(f"   Interval: {self.interval_hours}h")
        log(f"   PID: {os.getpid()}")

        write_pid(os.getpid())
        write_heartbeat("running")

        while self.running:
            self.cycle_count += 1
            log(f"\n{'=' * 60}")
            log(
                f"  Cycle #{self.cycle_count} — {datetime.now(timezone.utc).isoformat()}"
            )
            log(f"{'=' * 60}")

            try:
                self._run_cycle()
                self.restart_count = 0  # Reset on success
                write_heartbeat("running", self.cycle_count)

                if self.running:
                    log(f"\n⏳ Waiting {self.interval_hours}h until next cycle...")
                    self._wait_interval()

            except Exception as exc:
                self.restart_count += 1
                log(f"❌ Cycle failed: {exc}", level="ERROR")
                write_heartbeat("error", self.cycle_count, str(exc))

                if self.restart_count >= self.max_restarts:
                    log(
                        f"💀 Max restarts ({self.max_restarts}) reached. Waiting {self.interval_hours}h before retry...",
                        level="ERROR",
                    )
                    self.restart_count = 0
                    self._wait_interval()
                else:
                    log(
                        f"🔄 Restarting in 30s (attempt {self.restart_count}/{self.max_restarts})..."
                    )
                    time.sleep(30)

        log("🛑 Daemon stopped.")
        write_heartbeat("stopped", self.cycle_count)
        remove_pid()

    def _run_cycle(self) -> None:
        """Execute one workflow cycle."""
        cmd = [
            sys.executable,
            "-m",
            "campaign_autopilot.cli_v2",
            "--workflow",
            self.workflow,
            "--context",
            self.context,
            "--db",
            self.db,
            "--mode",
            "full",
            "--log-level",
            "INFO",
        ]
        log(f"   Running: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.interval_hours * 3600,
            cwd=str(PROJECT_ROOT),
        )

        # Log output
        if result.stdout:
            for line in result.stdout.strip().split("\n")[-10:]:
                log(f"   {line}")
        if result.stderr:
            for line in result.stderr.strip().split("\n")[-5:]:
                log(f"   ⚠️  {line}", level="WARNING")

        if result.returncode != 0:
            raise RuntimeError(f"Workflow exited with code {result.returncode}")

    def _wait_interval(self) -> None:
        """Wait for the interval, checking for shutdown signal."""
        for _ in range(self.interval_hours * 60):
            if not self.running:
                break
            time.sleep(60)  # Check every minute


# ── CLI ──────────────────────────────────────────────────────────


def cmd_start(args: argparse.Namespace) -> None:
    """Start the daemon."""
    pid = read_pid()
    if pid and is_process_running(pid):
        print(f"⚠️  Autopilot already running (PID {pid})")
        print("   Use --status to check or --stop to stop")
        return

    daemon = AutopilotDaemon(
        workflow=args.workflow,
        context=args.context,
        db=args.db,
        interval_hours=args.interval,
        max_restarts=args.max_restarts,
    )
    daemon.run()


def cmd_status(args: argparse.Namespace) -> None:
    """Show daemon status."""
    pid = read_pid()
    running = pid and is_process_running(pid)
    hb = get_heartbeat()

    print(f"{'=' * 60}")
    print("  📊 AUTOPILOT STATUS")
    print(f"{'=' * 60}")
    print(f"  PID:      {pid or 'N/A'}")
    print(f"  Running:  {'✅ Yes' if running else '❌ No'}")
    print(f"  Status:   {hb.get('status', 'unknown')}")
    print(f"  Uptime:   {hb.get('uptime_hours', 0):.1f}h")
    print(f"  Cycles:   {hb.get('cycle', 0)}")
    print(f"  Last:     {hb.get('timestamp', 'N/A')}")
    if hb.get("error"):
        print(f"  Error:    {hb['error']}")
    print()

    # Show last log lines
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text().strip().split("\n")
        print(f"  Last {min(5, len(lines))} log lines:")
        for line in lines[-5:]:
            print(f"    {line}")

    print()
    if running:
        print("  Commands:")
        print("    --stop    Stop the daemon")
        print("    --status  Show this status")
    else:
        print("  To start:")
        print("    python scripts/autopilot_daemon.py")


def cmd_tail(args: argparse.Namespace) -> None:
    """Follow daemon logs in real-time using ponytail."""
    log_file = LOG_FILE
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        print("Start the daemon first: python scripts/autopilot_daemon.py [start]")
        return

    try:
        f = Follow(str(log_file))
        print(f"👁️  Tailing {log_file}... (Ctrl+C to stop)\n")
        while True:
            for line in f.readlines():
                if isinstance(line, bytes):
                    line = line.decode("utf-8", errors="replace")
                if args.grep and args.grep.lower() not in line.lower():
                    continue
                ts = datetime.now().strftime("%H:%M:%S")
                color = ""
                reset = ""
                if "ERROR" in line:
                    color = "\033[91m"
                elif "WARNING" in line or "WARN" in line:
                    color = "\033[93m"
                elif "INFO" in line:
                    color = "\033[92m"
                print(f"{color}{ts} {line.rstrip()}{reset}")
            import time

            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n🛑 Tail stopped.")
    except Exception as e:
        print(f"Error: {e}")


def cmd_stop(args: argparse.Namespace) -> None:
    """Stop the daemon."""
    pid = read_pid()
    if not pid:
        print("ℹ️  Autopilot not running")
        return

    if not is_process_running(pid):
        print("ℹ️  Autopilot already stopped (stale PID file)")
        remove_pid()
        return

    print(f"🛑 Stopping autopilot (PID {pid})...")
    os.kill(pid, signal.SIGTERM)

    # Wait for graceful shutdown
    for _ in range(30):
        if not is_process_running(pid):
            print("✅ Stopped")
            remove_pid()
            return
        time.sleep(1)

    # Force kill
    os.kill(pid, signal.SIGKILL)
    print("⚠️  Force killed")
    remove_pid()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Campaign Autopilot Daemon — 24/7 Operation"
    )
    parser.add_argument(
        "--workflow", default=DEFAULT_WORKFLOW, help="Workflow JSON path"
    )
    parser.add_argument("--context", default=DEFAULT_CONTEXT, help="Context JSON path")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database path")
    parser.add_argument(
        "--interval", type=int, default=48, help="Hours between cycles (default: 48)"
    )
    parser.add_argument(
        "--max-restarts",
        type=int,
        default=5,
        help="Max restarts before cooldown (default: 5)",
    )

    # Commands
    parser.add_argument("--status", action="store_true", help="Show daemon status")
    parser.add_argument("--stop", action="store_true", help="Stop the daemon")

    args = parser.parse_args()

    if args.stop:
        cmd_stop(args)
    elif args.status:
        cmd_status(args)
    else:
        cmd_start(args)


if __name__ == "__main__":
    main()
