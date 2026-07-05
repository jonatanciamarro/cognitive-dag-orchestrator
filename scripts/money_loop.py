#!/usr/bin/env python3
"""Money Loop — Ciclo contínuo de geração de receita.

Executa em loop:
  1. Workflow de marketing de afiliados (pesquisa → ofertas → conteúdo → plano)
  2. Gera landing pages para cada produto encontrado
  3. Gera templates de email para nutrição
  4. Salva tudo em output/ com relatório
  5. Repete a cada N horas

Uso:
    # Modo contínuo (24/7)
    nohup python scripts/money_loop.py > .state/money_loop.log 2>&1 &

    # Um ciclo
    python scripts/money_loop.py --once

    # Ver estatísticas
    python scripts/money_loop.py --stats
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.campaign_autopilot.cli import run_workflow
from src.campaign_autopilot.free_llm_providers import _load_env_file

_load_env_file()
console = Console()


class MoneyLoop:
    """Loop de geração de receita — workflow + landing pages + emails."""

    def __init__(
        self,
        workflow_path: str | Path,
        context_path: str | Path,
        db_path: str | Path = ".state/money_loop.db",
        output_dir: str | Path = "output",
        interval_hours: int = 24,
    ):
        self.workflow_path = str(workflow_path)
        self.context_path = str(context_path)
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.interval_hours = interval_hours
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                finished_at TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                status TEXT NOT NULL,
                keywords_found INTEGER DEFAULT 0,
                offers_found INTEGER DEFAULT 0,
                articles_planned INTEGER DEFAULT 0,
                landing_pages_generated INTEGER DEFAULT 0,
                emails_generated INTEGER DEFAULT 0,
                estimated_monthly_clicks INTEGER DEFAULT 0,
                revenue_estimate REAL DEFAULT 0.0,
                error TEXT DEFAULT ''
            )
        """)
        conn.commit()
        conn.close()

    def _record_cycle(self, data: dict) -> int:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            """INSERT INTO cycles
               (started_at, finished_at, duration_ms, status,
                keywords_found, offers_found, articles_planned,
                landing_pages_generated, emails_generated,
                estimated_monthly_clicks, revenue_estimate, error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["started_at"],
                data["finished_at"],
                data["duration_ms"],
                data["status"],
                data.get("keywords_found", 0),
                data.get("offers_found", 0),
                data.get("articles_planned", 0),
                data.get("landing_pages_generated", 0),
                data.get("emails_generated", 0),
                data.get("estimated_monthly_clicks", 0),
                data.get("revenue_estimate", 0.0),
                data.get("error", ""),
            ),
        )
        cycle_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()
        return cycle_id

    def _next_cycle_id(self) -> int:
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute("SELECT MAX(id) FROM cycles").fetchone()
        conn.close()
        return row[0] if row and row[0] else 0

    def run_cycle(self) -> dict:
        started_at = datetime.now(timezone.utc).isoformat()
        t0 = time.time()
        errors = []

        # ── FASE 1: Workflow ──
        cycle_id = self._next_cycle_id() + 1
        console.print(
            Panel(
                f"[bold]🚀 CICLO #{cycle_id}[/bold] — {started_at[:19]}",
                box=box.HEAVY,
            )
        )

        try:
            result = run_workflow(
                context_path=self.context_path,
                workflow_path=self.workflow_path,
                db_path=str(self.db_path),
            )
        except Exception as e:
            errors.append(f"Workflow failed: {e}")
            result = {}

        output = result.get("output", {}) if isinstance(result, dict) else {}
        step_results = (
            output.get("step_results", {}) if isinstance(output, dict) else {}
        )
        seo = (
            step_results.get("seo_research", {}).get("output", {})
            if isinstance(step_results.get("seo_research"), dict)
            else {}
        )
        opportunities = (
            seo.get("top_opportunities", []) if isinstance(seo, dict) else []
        )
        keywords_found = len(opportunities)

        offers_step = (
            step_results.get("affiliate_offers", {}).get("output", {})
            if isinstance(step_results.get("affiliate_offers"), dict)
            else {}
        )
        offers_list = (
            offers_step.get("offers", []) if isinstance(offers_step, dict) else []
        )
        offers_found = len(offers_list)

        plan_step = (
            step_results.get("content_planning", {}).get("output", {})
            if isinstance(step_results.get("content_planning"), dict)
            else {}
        )
        articles = plan_step.get("articles", []) if isinstance(plan_step, dict) else []
        articles_planned = len(articles)

        # ── FASE 2: Landing Pages ──
        console.print("[bold]📄 Gerando landing pages...[/bold]")
        landing_pages = 0
        for article in articles:
            title = (
                article.get("title", "untitled")
                if isinstance(article, dict)
                else str(article)
            )
            safe_title = "".join(
                c if c.isalnum() or c in " -_" else "_" for c in title
            )[:40]
            lp_dir = self.output_dir / "landing_pages" / safe_title
            lp_dir.mkdir(parents=True, exist_ok=True)
            lp_html = lp_dir / "index.html"
            try:
                lp_html.write_text(f"""<!DOCTYPE html><html lang="pt-BR">
<head><meta charset="UTF-8"><title>{title}</title></head>
<body><h1>{title}</h1><p>Landing page gerada em {datetime.now().isoformat()}</p></body></html>""")
                landing_pages += 1
            except Exception as e:
                errors.append(f"LP {title}: {e}")

        # ── FASE 3: Emails ──
        console.print("[bold]📧 Gerando emails de nutrição...[/bold]")
        emails = 0
        for article in articles:
            title = (
                article.get("title", "untitled")
                if isinstance(article, dict)
                else str(article)
            )
            safe_title = "".join(
                c if c.isalnum() or c in " -_" else "_" for c in title
            )[:40]
            email_dir = self.output_dir / "emails" / safe_title
            email_dir.mkdir(parents=True, exist_ok=True)
            email_file = email_dir / "email.txt"
            try:
                email_file.write_text(
                    f"Assunto: {title}\n\nOlá! Confira nosso artigo sobre {title}.\n\n[Link para o artigo]\n\nAtenciosamente,\nEquipe"
                )
                emails += 1
            except Exception as e:
                errors.append(f"Email {title}: {e}")

        duration_ms = int((time.time() - t0) * 1000)
        estimated_clicks = keywords_found * 50 + offers_found * 30
        revenue_est = estimated_clicks * 0.05

        status = "success" if not errors else "partial"
        cycle_data = {
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "status": status,
            "keywords_found": keywords_found,
            "offers_found": offers_found,
            "articles_planned": articles_planned,
            "landing_pages_generated": landing_pages,
            "emails_generated": emails,
            "estimated_monthly_clicks": estimated_clicks,
            "revenue_estimate": revenue_est,
            "error": "; ".join(errors[:3]) if errors else "",
        }

        cycle_id = self._record_cycle(cycle_data)

        # ── Relatório ──
        table = Table(title=f"📊 Resumo do Ciclo #{cycle_id}", box=box.ROUNDED)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        table.add_row("Keywords", str(keywords_found))
        table.add_row("Ofertas", str(offers_found))
        table.add_row("Artigos planejados", str(articles_planned))
        table.add_row("Landing pages", str(landing_pages))
        table.add_row("Emails", str(emails))
        table.add_row("Cliques estimados/mês", f"~{estimated_clicks}")
        table.add_row("Receita estimada/mês", f"R$ {revenue_est:.2f}")
        table.add_row("Duração", f"{duration_ms}ms")
        table.add_row(
            "Status", f"✅ {status}" if status == "success" else f"⚠️ {status}"
        )
        console.print(table)

        if errors:
            console.print("\n[red]⚠️ Erros:[/red]")
            for err in errors[:5]:
                console.print(f"  [red]• {err}[/red]")

        return cycle_data

    def run_loop(self):
        """Loop infinito com intervalo configurado."""
        console.print(
            Panel(
                f"[bold]💰 MONEY LOOP — CAMPAIGN AUTOPILOT[/bold]\n"
                f"  Workflow:  {self.workflow_path}\n"
                f"  Contexto:  {self.context_path}\n"
                f"  Database:  {self.db_path}\n"
                f"  Output:    {self.output_dir}\n"
                f"  Intervalo: {self.interval_hours}h\n"
                f"  Inicio:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"  Ctrl+C para parar",
                box=box.HEAVY,
            )
        )

        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                self.run_cycle()

                conn = sqlite3.connect(str(self.db_path))
                rows = conn.execute("""
                    SELECT COUNT(*),
                           COALESCE(SUM(landing_pages_generated), 0),
                           COALESCE(SUM(emails_generated), 0),
                           COALESCE(SUM(estimated_monthly_clicks), 0),
                           COALESCE(SUM(revenue_estimate), 0.0)
                    FROM cycles WHERE status='success'
                """).fetchone()
                conn.close()

                console.print(
                    Panel(
                        f"[bold]📈 ACUMULADO ({rows[0]} ciclos)[/bold]\n"
                        f"  Landing pages: {rows[1]} | Emails: {rows[2]}\n"
                        f"  Cliques totais/mês: ~{rows[3]} | Receita/mês: R$ {rows[4]:.2f}",
                        box=box.SIMPLE,
                    )
                )

            except KeyboardInterrupt:
                console.print(
                    f"\n[bold yellow]🛑 Money Loop parado após {cycle_count} ciclos.[/bold yellow]"
                )
                break
            except Exception as e:
                console.print(f"\n[red]⚠️ Erro (continuando): {e}[/red]")

            console.print(f"\n[dim]⏳ Próximo ciclo em {self.interval_hours}h...[/dim]")
            try:
                time.sleep(self.interval_hours * 3600)
            except KeyboardInterrupt:
                console.print(
                    f"\n[bold yellow]🛑 Money Loop parado após {cycle_count} ciclos.[/bold yellow]"
                )
                break

    def show_stats(self):
        """Mostra estatísticas acumuladas."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute("""
            SELECT COUNT(*),
                   COALESCE(SUM(landing_pages_generated), 0),
                   COALESCE(SUM(emails_generated), 0),
                   COALESCE(SUM(estimated_monthly_clicks), 0),
                   COALESCE(SUM(revenue_estimate), 0.0),
                   COALESCE(AVG(duration_ms), 0),
                   COALESCE(SUM(keywords_found), 0),
                   COALESCE(SUM(offers_found), 0)
            FROM cycles
        """).fetchone()
        last = conn.execute("SELECT * FROM cycles ORDER BY id DESC LIMIT 1").fetchone()
        last_24h = conn.execute("""
            SELECT COUNT(*), COALESCE(SUM(revenue_estimate), 0.0)
            FROM cycles WHERE started_at > datetime('now', '-1 day')
        """).fetchone()
        conn.close()

        table = Table(title="💰 MONEY LOOP — ESTATÍSTICAS", box=box.ROUNDED)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        table.add_row("Ciclos totais", str(rows[0]))
        table.add_row("Keywords pesquisadas", str(rows[6]))
        table.add_row("Ofertas encontradas", str(rows[7]))
        table.add_row("Landing pages geradas", str(rows[1]))
        table.add_row("Emails gerados", str(rows[2]))
        table.add_row("Cliques acumulados/mês", f"~{rows[3]}")
        table.add_row("Receita estimada/mês", f"R$ {rows[4]:.2f}")
        table.add_row("Tempo médio por ciclo", f"{rows[5]:.0f}ms")
        if last:
            table.add_row("Último ciclo", f"#{last[0]} — {last[3]} ({last[4]})")
        table.add_row("Últimas 24h", f"{last_24h[0]} ciclos, R$ {last_24h[1]:.2f}")
        console.print(table)


def main():
    parser = argparse.ArgumentParser(
        prog="money_loop", description="Money Loop — geração contínua de receita"
    )
    parser.add_argument(
        "--workflow",
        default="workflows/organic_affiliate_cycle.json",
        help="Workflow JSON",
    )
    parser.add_argument(
        "--context", default="examples/affiliate_context.json", help="Context JSON"
    )
    parser.add_argument("--db", default=".state/money_loop.db", help="Database path")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--interval", type=int, default=24, help="Hours between cycles")
    parser.add_argument("--once", action="store_true", help="Run single cycle and exit")
    parser.add_argument("--stats", action="store_true", help="Show statistics and exit")
    args = parser.parse_args()

    loop = MoneyLoop(
        workflow_path=args.workflow,
        context_path=args.context,
        db_path=args.db,
        output_dir=args.output,
        interval_hours=args.interval,
    )

    if args.stats:
        loop.show_stats()
    elif args.once:
        loop.run_cycle()
    else:
        loop.run_loop()


if __name__ == "__main__":
    main()
