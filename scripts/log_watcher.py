#!/usr/bin/env python3
"""👁️ Log Watcher — Monitor de logs 24/7 com ponytail

Segue arquivos de log em tempo real, detecta rotação, truncamento,
e exibe com filtros por nível, componente e palavras-chave.

Uso:
    python scripts/log_watcher.py                              # Segue todos os logs
    python scripts/log_watcher.py --level ERROR                # Só erros
    python scripts/log_watcher.py --component money_loop       # Só money_loop
    python scripts/log_watcher.py --grep "receita"             # Filtra por palavra
    python scripts/log_watcher.py --once                       # Lê e sai
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from ponytail import Follow

console = Console()

# ── Configuration ────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIRS = [
    PROJECT_ROOT / ".state/logs",
    PROJECT_ROOT / ".state",
    PROJECT_ROOT,
]


def discover_logs() -> list[Path]:
    """Discover all .log, .jsonl files in project state directories."""
    logs = []
    for d in LOG_DIRS:
        if d.exists():
            logs.extend(sorted(d.glob("*.log")))
            logs.extend(sorted(d.glob("*.jsonl")))
    # Also check project root for autopilot logs
    logs.extend(sorted(PROJECT_ROOT.glob("*.log")))
    # Deduplicate and filter
    seen = set()
    unique = []
    for p in logs:
        if p.name not in seen:
            seen.add(p.name)
            unique.append(p)
    return unique


def parse_jsonl(line: str) -> dict | None:
    """Try to parse a JSONL log line."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def format_log_line(
    line: str,
    level_filter: str | None = None,
    grep: str | None = None,
    component_filter: str | None = None,
) -> str | None:
    """Format a log line with colors, applying filters."""
    parsed = parse_jsonl(line)

    if parsed:
        level = parsed.get("level", "INFO")
        component = parsed.get("component", "?")

        # Apply filters
        if level_filter and level.upper() != level_filter.upper():
            return None
        if component_filter and component_filter.lower() not in component.lower():
            return None

        msg = parsed.get("message", "")
        text = f"[{level}] [{component}] {msg}"

        if grep and grep.lower() not in text.lower():
            return None

        # Color by level
        if level == "ERROR":
            return f"[red]{text}[/red]"
        elif level == "WARNING":
            return f"[yellow]{text}[/yellow]"
        elif level == "DEBUG":
            return f"[dim]{text}[/dim]"
        else:
            return f"[green]{text}[/green]"
    else:
        # Plain text log line
        if grep and grep.lower() not in line.lower():
            return None
        if level_filter:
            if level_filter.upper() == "ERROR" and "ERROR" not in line:
                return None
        return line.rstrip()


def watch_logs(
    level: str | None = None,
    grep: str | None = None,
    component: str | None = None,
    once: bool = False,
):
    """Watch all project logs using ponytail Follow."""
    log_files = discover_logs()

    if not log_files:
        console.print("[yellow]⚠️ Nenhum arquivo de log encontrado.[/yellow]")
        console.print(
            "[dim]Execute o sistema primeiro: python scripts/autopilot_daemon.py[/dim]"
        )
        return

    console.print(
        Panel(
            f"[bold]👁️ Log Watcher[/bold] — Seguindo [cyan]{len(log_files)}[/cyan] arquivo(s)\n"
            + (f"  Nível: [green]{level}[/green]\n" if level else "")
            + (f"  Filtro: [yellow]{grep}[/yellow]\n" if grep else "")
            + (f"  Componente: [blue]{component}[/blue]" if component else "")
            + (f"\n  [dim]{', '.join(f.name for f in log_files)}[/dim]"),
            box=box.HEAVY,
        )
    )

    # Create Follow instances for each log file
    followers = {}
    for lf in log_files:
        try:
            f = Follow(str(lf))
            followers[lf.name] = f
        except Exception as e:
            console.print(f"[dim]  {lf.name}: {e}[/dim]")

    if once:
        # Read existing content
        for lf in log_files:
            try:
                with open(lf) as fh:
                    for line in fh:
                        formatted = format_log_line(line, level, grep, component)
                        if formatted:
                            console.print(formatted)
            except Exception:
                pass
        return

    # Continuous following — poll all files
    console.print("[dim]Pressione Ctrl+C para parar[/dim]\n")
    try:
        while True:
            for name, follower in followers.items():
                for line in follower.readlines():
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    formatted = format_log_line(line, level, grep, component)
                    if formatted:
                        ts = datetime.now().strftime("%H:%M:%S")
                        console.print(f"[dim]{ts}[/dim] {formatted}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]🛑 Log Watcher parado.[/bold yellow]")


def show_log_stats():
    """Show statistics about log files."""
    log_files = discover_logs()

    if not log_files:
        console.print("[yellow]⚠️ Nenhum arquivo de log encontrado.[/yellow]")
        return

    table = Table(title="📊 Estatísticas de Log", box=box.ROUNDED)
    table.add_column("Arquivo", style="cyan")
    table.add_column("Tamanho", style="blue")
    table.add_column("Linhas", style="green")
    table.add_column("Última modificação", style="yellow")
    table.add_column("Erros", style="red")

    for lf in sorted(log_files, key=lambda p: p.stat().st_mtime, reverse=True):
        size = lf.stat().st_size
        mtime = datetime.fromtimestamp(lf.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        try:
            lines = sum(1 for _ in lf.open())
            errors = 0
            if lf.suffix == ".jsonl":
                errors = sum(1 for line in lf.open() if '"level": "ERROR"' in line)
            elif lf.suffix == ".log":
                errors = sum(1 for line in lf.open() if "ERROR" in line)
        except Exception:
            lines = 0
            errors = 0

        size_str = f"{size:,} bytes" if size < 1024 else f"{size / 1024:.1f} KB"
        table.add_row(lf.name, size_str, str(lines), mtime, str(errors))

    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="👁️ Log Watcher - ponytail")
    parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Filtrar por nível",
    )
    parser.add_argument("--component", help="Filtrar por componente")
    parser.add_argument("--grep", help="Filtrar por palavra-chave")
    parser.add_argument(
        "--once", action="store_true", help="Ler logs existentes e sair"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Mostrar estatísticas dos logs"
    )
    args = parser.parse_args()

    if args.stats:
        show_log_stats()
    else:
        watch_logs(args.level, args.grep, args.component, args.once)


if __name__ == "__main__":
    main()
