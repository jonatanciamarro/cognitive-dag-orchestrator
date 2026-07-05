#!/usr/bin/env python3
"""Quality Pipeline — Executa as 7 camadas de qualidade em artefatos.

Uso:
    PYTHONPATH=src python3 scripts/quality_pipeline.py --critic output/landing_pages/*.html
    PYTHONPATH=src python3 scripts/quality_pipeline.py --debate "estratégia marketing 2026"
    PYTHONPATH=src python3 scripts/quality_pipeline.py --benchmark --stats
    PYTHONPATH=src python3 scripts/quality_pipeline.py --rag "marketing digital afiliados"
    PYTHONPATH=src python3 scripts/quality_pipeline.py --cia "campanha marketing digital"
    PYTHONPATH=src python3 scripts/quality_pipeline.py --elo
    PYTHONPATH=src python3 scripts/quality_pipeline.py --full "minha campanha"
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from campaign_autopilot.quality_layers import (
    OutputCritic,
    DebateOrchestrator,
    BenchmarkDB,
    CampaignKnowledge,
    RAGEngine,
    TruthAgent,
    RiskAgent,
    ConsistencyAgent,
    ELORanking,
)

console = Console()


def run_critic(files: list[str]) -> None:
    """Run Output Critic on artifacts."""
    critic = OutputCritic(threshold=85)
    table = Table(title="📊 Output Critic", box=box.ROUNDED)
    table.add_column("Arquivo", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status")
    table.add_column("Sugestões")

    for fpath in files:
        path = Path(fpath)
        if not path.exists():
            table.add_row(path.name, "—", "❌", "Arquivo não encontrado")
            continue
        try:
            content = path.read_text(encoding="utf-8")
            artifact_type = {"html": "landing_page", "md": "article", "txt": "ad"}.get(
                path.suffix.lstrip("."), "landing_page"
            )
            verdict = critic.evaluate(path.stem, artifact_type, content[:2000])
            status = "✅ APROVADO" if verdict.passed else "❌ REJEITADO"
            suggestions = (
                "; ".join(verdict.suggestions[:2]) if verdict.suggestions else "—"
            )
            table.add_row(
                path.name,
                f"{verdict.overall:.0f}/100",
                status,
                suggestions[:40],
            )
        except Exception as e:
            table.add_row(path.name, "—", "❌", str(e)[:40])

    console.print(table)
    rate = critic.approval_rate()
    console.print(
        f"\n📈 Taxa de aprovação: {rate:.0f}%  |  Total: {len(files)} artefatos"
    )


def run_debate(topic: str) -> None:
    """Run multi-agent debate."""
    debate = DebateOrchestrator()

    # Simulated agents
    agents = {
        "designer": lambda t: {
            "output": f"Design strategy: clean, modern layout for '{t}'. "
            f"Use dark theme with accent gradient, large typography, whitespace."
        },
        "marketer": lambda t: {
            "output": f"Marketing campaign: target audience for '{t}'. "
            f"SEO keywords, social proof, urgency, CTA optimization."
        },
        "researcher": lambda t: {
            "output": f"Market research: trends in '{t}'. "
            f"Competitor analysis, gap opportunities, niche validation."
        },
        "conversion": lambda t: {
            "output": f"Conversion optimization: funnel for '{t}'. "
            f"Lead magnet, email sequence, retargeting, A/B testing."
        },
    }

    with console.status(f"🧠 Debating: {topic}..."):
        result = debate.run_debate(topic, agents)

    console.print(Panel("🧠 Multi-Agent Debate", box=box.HEAVY))
    console.print(f"Tópico: [bold]{topic}[/bold]")
    console.print(f"Score de consenso: [bold]{result.final_score}%[/bold]")
    console.print(f"Agentes: {len(result.perspectives)}", "")
    for name, view in result.perspectives.items():
        console.print(f"  [cyan]{name}[/cyan]: {str(view)[:120]}...")
    console.print(f"\nSíntese: {result.synthesis['summary']}")


def run_benchmark(stats: bool = False) -> None:
    """Show benchmark database."""
    db = BenchmarkDB()
    if stats:
        s = db.stats()
        console.print(Panel("📊 Benchmark Database", box=box.HEAVY))
        console.print(f"Total de outputs aprovados: [bold]{s['total']}[/bold]")
        console.print(f"Score médio: [bold]{s['avg_score']:.1f}/100[/bold]")
        if s["by_type"]:
            t = Table(box=box.ROUNDED)
            t.add_column("Tipo")
            t.add_column("Qtd")
            t.add_column("Média")
            for b in s["by_type"]:
                t.add_row(b["type"], str(b["count"]), f"{b['avg_score']:.1f}")
            console.print(t)
    else:
        tops = db.top_outputs(limit=10)
        console.print(f"Top {len(tops)} outputs aprovados:")
        for t in tops[:5]:
            console.print(
                f"  ✅ {t.get('artifact_type', '?')}: score {t.get('score', 0)}"
            )


def run_rag(query: str) -> None:
    """Run RAG retrieval."""
    engine = RAGEngine()
    ctx = engine.retrieve_context(query)
    console.print(Panel(f"🔍 RAG: {query}", box=box.HEAVY))
    console.print(f"Benchmarks encontrados: {ctx['benchmarks_count']}")
    console.print(f"Knowledge entries: {ctx['knowledge_count']}")
    console.print(
        f"Contexto disponível: {'✅ Sim' if ctx['context_available'] else '❌ Não'}"
    )
    for b in ctx.get("benchmarks", [])[:3]:
        console.print(f"  📌 Score {b['score']}: {b.get('why_it_worked', '')[:80]}")


def run_cia(content: str) -> None:
    """Run CIA governance check."""
    truth = TruthAgent()
    risk = RiskAgent()
    consistency = ConsistencyAgent()

    t = truth.verify(content)
    r = risk.assess({"campaign": {"niche": content[:30]}, "goal": content})
    c = consistency.check_brand(content)

    console.print(Panel("🕵️ CIA Governance", box=box.HEAVY))

    t_table = Table(title="Truth Agent", box=box.ROUNDED)
    t_table.add_column("Métrica")
    t_table.add_column("Valor")
    t_table.add_row("Score", f"{t['score']}/100")
    t_table.add_row("Passou", "✅" if t["passed"] else "❌")
    t_table.add_row("Issues", "; ".join(t["issues"][:2]) or "—")
    t_table.add_row("Warnings", "; ".join(t["warnings"][:2]) or "—")
    console.print(t_table)

    r_table = Table(title="Risk Agent", box=box.ROUNDED)
    r_table.add_column("Métrica")
    r_table.add_column("Valor")
    r_table.add_row("Risk Score", f"{r['risk_score']}/100")
    r_table.add_row("Safe", "✅" if r["safe"] else "⚠️")
    for risk_item in r["risks"][:3]:
        r_table.add_row("Risco", risk_item["detail"][:50])
    console.print(r_table)

    console.print(f"🎨 Brand Alignment: {c['brand_alignment']:.0f}%")


def run_elo() -> None:
    """Show ELO rankings."""
    elo = ELORanking()
    ranking = elo.ranking(limit=20)

    table = Table(title="🏆 ELO Ranking de Skills", box=box.ROUNDED)
    table.add_column("#", style="dim")
    table.add_column("Skill")
    table.add_column("ELO", justify="right")
    table.add_column("Partidas")
    table.add_column("Vitórias")

    for i, r in enumerate(ranking, 1):
        icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        table.add_row(
            f"{icon} {i}",
            r["name"],
            f"{r['elo']:.0f}",
            str(r["matches"]),
            str(r["wins"]),
        )

    if ranking:
        console.print(table)
    else:
        console.print(
            "📭 Nenhum skill ranqueado ainda. Execute --critic para gerar dados."
        )


def run_full(campaign: str) -> None:
    """Run full quality pipeline."""
    console.print(Panel(f"🏭 Full Quality Pipeline: {campaign}", box=box.HEAVY))

    with console.status("1/7 Output Critic..."):
        critic = OutputCritic(threshold=85)
        v = critic.evaluate("full-test", "landing_page", campaign, {"context": "test"})
        console.print(
            f"  ✅ Critic: {v.overall}/100 {'Aprovado' if v.passed else 'Rejeitado'}"
        )

    with console.status("2/7 Multi-Agent Debate..."):
        debate = DebateOrchestrator()
        d = debate.run_debate(
            campaign,
            {
                "designer": lambda t: {"output": f"design for {t}"},
                "marketer": lambda t: {"output": f"marketing for {t}"},
            },
        )
        console.print(
            f"  ✅ Debate: {d.final_score}% consenso entre {len(d.perspectives)} agentes"
        )

    with console.status("3/7 RAG Retrieval..."):
        rag = RAGEngine()
        ctx = rag.retrieve_context(campaign)
        console.print(
            f"  ✅ RAG: {ctx['benchmarks_count']} benchmarks, {ctx['knowledge_count']} entries"
        )

    with console.status("4/7 CIA Governance..."):
        truth = TruthAgent().verify(campaign)
        risk = RiskAgent().assess(
            {"campaign": {"niche": campaign[:20]}, "goal": campaign}
        )
        brand = ConsistencyAgent().check_brand(campaign)
        console.print(
            f"  ✅ CIA: Truth={truth['score']} Risk={risk['risk_score']} Brand={brand['brand_alignment']}%"
        )

    with console.status("5/7 Benchmark DB..."):
        db = BenchmarkDB()
        db.record("landing_page", v.overall, v, "quality_pipeline", "test")
        console.print(f"  ✅ Benchmark: {db.count()} registros")

    with console.status("6/7 Campaign Knowledge..."):
        kn = CampaignKnowledge()
        kn.add(
            f"Pipeline: {campaign[:30]}",
            "campaign",
            campaign,
            ["test"],
            "quality_pipeline",
        )
        console.print(f"  ✅ Knowledge: {kn.count()} entradas")

    with console.status("7/7 ELO Ranking..."):
        elo = ELORanking()
        elo.record_match("default-agent", "quality-agent", "a" if v.passed else "b")
        ranking = elo.ranking()
        console.print(f"  ✅ ELO: {len(ranking)} skills ranqueadas")

    console.print("\n" + "=" * 50)
    console.print("[bold green]✅ QUALITY PIPELINE COMPLETA[/bold green]")
    console.print("=" * 50)


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="quality_pipeline")
    parser.add_argument(
        "--critic", nargs="*", default=None, help="Arquivos para criticar"
    )
    parser.add_argument("--debate", type=str, default=None, help="Tópico para debate")
    parser.add_argument("--benchmark", action="store_true", help="Ver benchmark DB")
    parser.add_argument("--stats", action="store_true", help="Stats do benchmark")
    parser.add_argument("--rag", type=str, default=None, help="Query RAG")
    parser.add_argument("--cia", type=str, default=None, help="Conteúdo para CIA")
    parser.add_argument("--elo", action="store_true", help="Ver ELO rankings")
    parser.add_argument("--full", type=str, default=None, help="Full pipeline")
    args = parser.parse_args()

    if args.full:
        run_full(args.full)
    elif args.critic is not None:
        run_critic(
            args.critic
            if args.critic
            else ["output/ui_design/*.html", "output/landing_pages/*.html"]
        )
    elif args.debate:
        run_debate(args.debate)
    elif args.benchmark or args.stats:
        run_benchmark(stats=args.stats or args.benchmark)
    elif args.rag:
        run_rag(args.rag)
    elif args.cia:
        run_cia(args.cia)
    elif args.elo:
        run_elo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# ── Auto-Regeneration ──


def run_fix(campaign: str) -> None:
    """Run quality pipeline with auto-regeneration for failed content."""
    from campaign_autopilot.auto_regenerate import (
        AutoRegenerator,
        cta_injection_regenerator,
    )

    console.print(
        Panel.fit(
            f"[bold yellow]🔄 Auto-Regeneration for: {campaign}[/]",
            border_style="yellow",
        )
    )

    # Simulate generating and testing content
    regenerator = AutoRegenerator(threshold=85.0, max_attempts=3)

    # Try regenerating different content types
    test_contents = [
        (
            "landing_page",
            "Descubra como transformar seus resultados em marketing digital. Aprenda as melhores estrategias.",
        ),
        (
            "article",
            f"Guia completo sobre {campaign}. Este artigo vai te ensinar tudo.",
        ),
        ("email", f"Ola! Temos uma oferta especial para voce sobre {campaign}."),
    ]

    table = Table(title="Auto-Regeneration Results", box=box.ROUNDED)
    table.add_column("Type", style="cyan")
    table.add_column("Attempts", style="yellow")
    table.add_column("Initial Score", style="red")
    table.add_column("Final Score", style="green")
    table.add_column("Status", style="blue")

    for atype, content in test_contents:
        result = regenerator.regenerate(
            artifact_id=f"fix_{atype}_{int(time.time())}",
            artifact_type=atype,
            content=content,
            generate_fn=cta_injection_regenerator,
        )
        initial_score = result["verdicts"][0]["score"] if result["verdicts"] else 0
        table.add_row(
            atype,
            str(result["final_attempt"]),
            f"{initial_score:.1f}",
            f"{result['final_score']:.1f}",
            "✅ Approved" if result["status"] == "approved" else "❌ Failed",
        )

    console.print(table)
    console.print(f"\nApproval rate: [bold]{regenerator.approval_rate():.1f}%[/]")
    console.print(
        f"Total attempts: [bold]{sum(h['final_attempt'] for h in regenerator.history())}[/]"
    )
    console.print("\n[bold green]✅ Auto-regeneration complete[/]")


def run_full_with_fix(campaign: str) -> None:
    """Run full quality pipeline + auto-fix for failed content."""
    run_critic_interactive(campaign)
    run_fix(campaign)


def run_quality_test() -> None:
    """Run comprehensive quality test on existing outputs."""
    from campaign_autopilot.auto_regenerate import quality_test

    console.print(
        Panel.fit(
            "[bold]🧪 Quality Test — Testing existing outputs[/]", border_style="cyan"
        )
    )

    # Test files in output/
    import glob

    output_files = glob.glob("output/**/*.html", recursive=True) + glob.glob(
        "output/**/*.txt", recursive=True
    )

    if not output_files:
        console.print("[yellow]No output files found to test[/]")
        return

    table = Table(title="Quality Test Results", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Score", style="green")
    table.add_column("Status", style="blue")

    approved_count = 0
    total_count = 0

    for fpath in output_files[:20]:  # Max 20 files
        with open(fpath) as f:
            content = f.read()
        ftype = "landing_page" if "landing" in fpath else "article"
        total_count += 1
        result = quality_test(content, artifact_type=ftype, artifact_id=fpath)
        status = "✅" if result["status"] == "approved" else "❌"
        if result["status"] == "approved":
            approved_count += 1
        table.add_row(
            fpath[:50],
            ftype,
            f"{result['final_score']:.1f}",
            f"{status} (attempt {result['attempts']})",
        )

    console.print(table)
    console.print(
        f"\n[bold]Results: {approved_count}/{total_count} approved ({approved_count / total_count * 100:.1f}%)[/]"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="quality_pipeline")
    parser.add_argument("--fix", type=str, help="Auto-regenerate failed content")
    parser.add_argument("--critic", type=str, nargs="*", help="Run critic on files")
    parser.add_argument("--debate", type=str, help="Run multi-agent debate")
    parser.add_argument("--cia", type=str, help="Run CIA governance layer")
    parser.add_argument("--benchmark", action="store_true", help="Show benchmark stats")
    parser.add_argument("--rag", type=str, help="Query campaign knowledge")
    parser.add_argument("--elo", action="store_true", help="Show ELO rankings")
    parser.add_argument("--full", type=str, help="Run full quality pipeline")
    parser.add_argument(
        "--test", action="store_true", help="Run quality test on outputs"
    )
    parser.add_argument("--full-fix", type=str, help="Full pipeline + auto-fix")

    args = parser.parse_args()

    if args.fix:
        run_fix(args.fix)
    elif args.test:
        run_quality_test()
    elif args.full_fix:
        run_full_with_fix(args.full_fix)
    elif args.critic:
        run_critic(args.critic)
    elif args.debate:
        run_debate(args.debate)
    elif args.cia:
        run_cia(args.cia)
    elif args.benchmark:
        show_benchmark_stats()
    elif args.rag:
        query_campaign_knowledge(args.rag)
    elif args.elo:
        show_elo_rankings()
    elif args.full:
        run_full_pipeline(args.full)
    else:
        parser.print_help()
