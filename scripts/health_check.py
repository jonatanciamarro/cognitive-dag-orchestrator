#!/usr/bin/env python3
"""🏥 Health Check — Campaign Autopilot System Monitor

Verifica todos os componentes do sistema e reporta status.
Uso:
    python scripts/health_check.py              # Check completo
    python scripts/health_check.py --quick      # Apenas componentes críticos
    python scripts/health_check.py --json       # Output JSON
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich import box

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
console = Console()


def check(label: str, ok: bool, detail: str = "") -> dict:
    icon = "✅" if ok else "❌"
    style = "green" if ok else "red"
    console.print(f"  [{style}]{icon} {label}[/{style}]")
    if detail:
        console.print(f"     [dim]{detail}[/dim]")
    return {"label": label, "ok": ok, "detail": detail}


def run_health_check(quick: bool = False) -> list[dict]:
    results = []
    console.print(
        Panel(
            f"[bold]🏥 Campaign Autopilot — Health Check[/bold]\n"
            f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            box=box.HEAVY,
        )
    )

    # ── Python environment ──
    console.print("\n[bold]📦 Ambiente[/bold]")
    results.append(
        check(
            "Python 3.10+",
            sys.version_info >= (3, 10),
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
    )
    venv = os.environ.get("VIRTUAL_ENV", "") or os.environ.get("CONDA_DEFAULT_ENV", "")
    results.append(
        check(
            "Virtualenv ativo", bool(venv), venv or "Nenhum ambiente virtual detectado"
        )
    )

    # ── .env ──
    console.print("\n[bold]🔑 Chaves de API[/bold]")
    env_path = Path(".env")
    results.append(
        check(
            "Arquivo .env existe",
            env_path.exists(),
            "OK" if env_path.exists() else "Crie .env copiando .env.example",
        )
    )

    if env_path.exists():
        from src.campaign_autopilot.free_llm_providers import get_config

        has_or = bool(get_config("OPENROUTER_API_KEY"))
        has_groq = bool(get_config("GROQ_API_KEY"))
        has_gemini = bool(get_config("GEMINI_API_KEY"))
        has_llm = has_or or has_groq or has_gemini
        results.append(
            check(
                "LLM Provider configurado (OpenRouter/Groq/Gemini)",
                has_llm,
                f"OpenRouter={'✅' if has_or else '❌'} Groq={'✅' if has_groq else '❌'} Gemini={'✅' if has_gemini else '❌'}",
            )
        )

        aff_keys = [
            "KIWIFY_AFFILIATE_ID",
            "EDUZZ_AFFILIATE_ID",
            "MONETIZZE_AFFILIATE_ID",
            "HOTMART_CLIENT_ID",
            "AMAZON_ASSOCIATES_TAG",
        ]
        configured_affs = [k for k in aff_keys if get_config(k)]
        results.append(
            check(
                "Afiliados configurados",
                len(configured_affs) > 0,
                f"{len(configured_affs)}/{len(aff_keys)}: {', '.join(configured_affs) or 'nenhum'}",
            )
        )

        has_wp = bool(get_config("WP_URL") and get_config("WP_USER"))
        results.append(
            check(
                "WordPress configurado",
                has_wp,
                f"URL={'✅' if get_config('WP_URL') else '❌'} User={'✅' if get_config('WP_USER') else '❌'}",
            )
        )

    if quick:
        total = len(results)
        passed = sum(1 for r in results if r["ok"])
        failed = total - passed
        console.print(
            f"\n[bold]📊 Resumo: [green]{passed} ✅[/green] / [red]{failed} ❌[/red] / {total} total[/bold]"
        )
        return results

    # ── Core Modules ──
    console.print("\n[bold]🧩 Módulos Core[/bold]")
    modules = [
        ("models", "Modelos de dados"),
        ("memory", "MemoryStore (SQLite)"),
        ("workflow", "WorkflowEngine DAG"),
        ("policy", "PolicyEngine"),
        ("metrics", "Calculadora de métricas"),
        ("semantic_memory", "Memória semântica"),
        ("explanation", "ExplanationStore"),
        ("feedback", "OutcomeStore"),
        ("synthesis", "KnowledgeSynthesis"),
        ("goals", "GoalRegistry"),
        ("affiliate", "OfferManager"),
        ("api_hub", "API Integration Hub"),
        ("free_llm_providers", "Free LLM Providers (13)"),
        ("media_providers", "Media Providers (16)"),
        ("trace_store", "Agent Trace Store"),
        ("model_router", "Model Router"),
        ("evaluation_engine", "Evaluation Engine"),
        ("constraint_intelligence", "Constraint Intelligence"),
        ("world_model", "World Model"),
        ("self_improvement", "Self-Improvement Engine"),
    ]
    for mod_name, mod_desc in modules:
        try:
            exec(f"from campaign_autopilot import {mod_name}")
            results.append(check(f"{mod_desc}", True, f"{mod_name}.py OK"))
        except Exception as e:
            results.append(check(f"{mod_desc}", False, str(e)[:80]))

    # ── Agents ──
    console.print("\n[bold]🤖 Agentes[/bold]")
    agent_count = len(
        [
            f
            for f in (Path("src/campaign_autopilot/agents").glob("*.py"))
            if f.name != "__init__.py" and f.name != "base.py"
        ]
    )
    sub_agent_count = 0
    for d in Path("src/campaign_autopilot/agents").iterdir():
        if d.is_dir() and not d.name.startswith("_"):
            sub_agent_count += len(
                [f for f in d.glob("*.py") if f.name != "__init__.py"]
            )
    total_agents = agent_count + sub_agent_count
    try:
        results.append(
            check(
                f"AgentBase + LoggedAgent ({total_agents} agentes)",
                True,
                f"{agent_count} principais + {sub_agent_count} sub-agentes",
            )
        )
    except Exception as e:
        results.append(check("AgentBase", False, str(e)[:80]))

    # ── Workflows ──
    console.print("\n[bold]⚡ Workflows[/bold]")
    wf_count = len(list(Path("workflows").glob("*.json")))
    results.append(
        check(
            f"Workflows DAG ({wf_count})", wf_count > 0, f"{wf_count} definições JSON"
        )
    )

    # ── Tests ──
    console.print("\n[bold]🧪 Testes[/bold]")
    test_count = len(list(Path("tests").glob("*.py"))) - 1
    results.append(
        check(
            f"Test files ({test_count})",
            test_count > 0,
            f"{test_count} arquivos de teste",
        )
    )

    # ── Output ──
    console.print("\n[bold]📁 Output[/bold]")
    output_dir = Path("output")
    if output_dir.exists():
        dirs = [d.name for d in output_dir.iterdir() if d.is_dir()]
        results.append(
            check(
                "Diretórios de output",
                bool(dirs),
                f"{', '.join(dirs[:10])}{'...' if len(dirs) > 10 else ''}",
            )
        )
    else:
        results.append(check("Diretório output", False, "output/ não existe"))

    # ── Security ──
    console.print("\n[bold]🔒 Segurança[/bold]")
    has_githooks = Path(".githooks/pre-push").exists()
    results.append(
        check(
            "Pre-push hook (anti-secret leak)",
            has_githooks,
            ".githooks/pre-push" if has_githooks else "NÃO INSTALADO",
        )
    )

    has_gitignore_env = ".env" in Path(".gitignore").read_text()
    results.append(
        check(".env no .gitignore", has_gitignore_env, "Protege chaves de vazar")
    )

    try:
        result = subprocess.run(
            ["bash", ".githooks/pre-push"], capture_output=True, text=True, timeout=5
        )
        secrets_clean = result.returncode == 0
        results.append(
            check(
                "Secrets scan (pre-push)",
                secrets_clean,
                "Nenhum secret detectado"
                if secrets_clean
                else "⚠️  Secrets detectados!",
            )
        )
    except Exception:
        results.append(check("Secrets scan", False, "Não foi possível executar o scan"))

    total = len(results)
    passed = sum(1 for r in results if r["ok"])
    failed = total - passed
    console.print(
        f"\n[bold]📊 Resumo: [green]{passed} ✅[/green] / [red]{failed} ❌[/red] / {total} total[/bold]"
    )

    return results


def main():
    parser = argparse.ArgumentParser(description="🏥 Health Check")
    parser.add_argument(
        "--quick", action="store_true", help="Apenas componentes críticos"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = run_health_check(quick=args.quick)

    if args.json:
        print(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total": len(results),
                    "passed": sum(1 for r in results if r["ok"]),
                    "failed": sum(1 for r in results if not r["ok"]),
                    "checks": results,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
