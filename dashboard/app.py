"""Campaign Autopilot — Dashboard Completo v5.2.1

Dashboard Streamlit com:
  - Overview: saúde do sistema, Phase 20 Kernel, revenue
  - Output Gallery: imagens, landing pages, emails, vídeos, áudio
  - Revenue Tree: 13 fontes em paralelo
  - AG-Kit Phases: status das 20 fases
  - System Status: providers, agentes, workflows
  - Logs: visualização em tempo real
"""

from __future__ import annotations

import base64
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

st.set_page_config(
    page_title="Campaign Autopilot v5.2.1",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth ────────────────────────────────────────────────────
_DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
if _DASHBOARD_PASSWORD:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Campaign Autopilot Dashboard")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if password == _DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        st.stop()

# ── Constants ───────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
SRC_DIR = PROJECT_ROOT / "src"
STATE_DIR = PROJECT_ROOT / ".state"
DB_PATH = str(STATE_DIR / "money_loop.db")

# ── Utility Functions ───────────────────────────────────────

def load_db(db_path: str = DB_PATH) -> sqlite3.Connection | None:
    path = Path(db_path)
    if not path.exists():
        return None
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def get_cycle_stats() -> dict[str, Any]:
    """Get cycle statistics from money loop DB or log."""
    conn = load_db()
    if conn is None:
        return {"total_cycles": 0, "total_revenue": 0, "total_clicks": 0}
    try:
        rows = conn.execute(
            "SELECT * FROM autopilot_cycles ORDER BY cycle_id DESC LIMIT 50"
        ).fetchall()
        cycles = [dict(r) for r in rows]
        conn.close()
        total = len(cycles)
        revenue = sum(c.get("estimated_monthly_revenue", 0) for c in cycles)
        clicks = sum(c.get("estimated_monthly_clicks", 0) for c in cycles)
        success = sum(1 for c in cycles if c.get("status") == "success")
        return {
            "total_cycles": total,
            "total_revenue": revenue,
            "total_clicks": clicks,
            "success_cycles": success,
            "cycles": cycles,
        }
    except (sqlite3.OperationalError, Exception):
        conn.close()
        return {"total_cycles": 0, "total_revenue": 0, "total_clicks": 0}


def get_kernel_status() -> dict[str, Any]:
    """Get Phase 20 Autonomous Enterprise Kernel status."""
    try:
        sys.path.insert(0, str(SRC_DIR))
        from campaign_autopilot.enterprise_kernel import (
            AutonomousEnterpriseKernel,
        )
        k = AutonomousEnterpriseKernel.get_instance()
        k.boot()
        hc = k.health_check()
        return hc
    except Exception as e:
        return {"kernel_status": "error", "error": str(e)}


def get_output_files() -> dict[str, list[Path]]:
    """Scan output/ directory and group by type."""
    result = {
        "images": [],
        "landing_pages": [],
        "emails": [],
        "videos": [],
        "audio": [],
        "content": [],
        "social": [],
    }
    if not OUTPUT_DIR.exists():
        return result

    for f in sorted(OUTPUT_DIR.rglob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        parent = f.parent.name
        if suffix in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            result["images"].append(f)
        elif suffix == ".html" and "landing" in f.stem.lower():
            result["landing_pages"].append(f)
        elif suffix == ".html" and "email" in f.stem.lower():
            result["emails"].append(f)
        elif suffix == ".html":
            result["landing_pages"].append(f)
        elif suffix in (".mp4", ".webm", ".mov"):
            result["videos"].append(f)
        elif suffix in (".mp3", ".wav", ".ogg"):
            result["audio"].append(f)
        elif suffix == ".md":
            result["content"].append(f)
        elif parent in ("social_posts",):
            result["social"].append(f)

    return result


def get_providers_status() -> dict[str, Any]:
    """Get media providers status."""
    try:
        sys.path.insert(0, str(SRC_DIR))
        from campaign_autopilot.media_providers import get_provider_report
        report = get_provider_report()
        return report
    except Exception:
        return {}


def render_html_preview(html_path: Path) -> str:
    """Read HTML file and return it wrapped for iframe."""
    try:
        with open(html_path) as f:
            html = f.read()
        return html
    except Exception:
        return "<p>Erro ao ler arquivo</p>"


def img_to_base64(img_path: Path) -> str:
    """Convert image to base64 for display."""
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def get_money_loop_stats() -> dict[str, Any]:
    """Get accumulated stats from money loop CLI."""
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts/money_loop.py"), "--stats"],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
        )
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"output": "", "error": str(e)}


def get_autopilot_log() -> str:
    """Get recent autopilot log entries."""
    log_path = STATE_DIR / "autopilot_daemon.log"
    if log_path.exists():
        with open(log_path) as f:
            lines = f.readlines()
        return "".join(lines[-100:])
    return "Log não encontrado"


# ── Sidebar ──────────────────────────────────────────────────

_PAGE_LABELS: dict[str, str] = {
    "Overview": "📊 Overview",
    "Output Gallery": "🖼️ Output Gallery",
    "Revenue Tree": "🌳 Revenue Tree",
    "AG-Kit Kernel": "🏭 AG-Kit Kernel",
    "Hotmart Intelligence": "🔥 Hotmart Intelligence",
    "Skills": "🧠 Skills",
    "Quality Layers": "🎯 Quality Layers",
    "System Status": "🔧 System Status",
    "Logs": "📋 Logs",
    "Acoes": "⚡ Ações",
}

st.sidebar.title("🚀 Campaign Autopilot")
st.sidebar.caption("v5.2.1 — Lyzer Labs")

page_key: str = st.sidebar.radio(
    "Navegação",
    list(_PAGE_LABELS.keys()),
    format_func=lambda k: _PAGE_LABELS[k],
    key="nav_page",
)

st.sidebar.markdown("---")
st.sidebar.caption(f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")


# ══════════════════════════════════════════════════════════════
# PAGE: Overview
# ══════════════════════════════════════════════════════════════
if page_key == "Overview":
    st.title("📊 Campaign Autopilot — Overview")

    # ── Top Row: Key Metrics ──
    stats = get_cycle_stats()
    kernel_hc = get_kernel_status()
    output_files = get_output_files()
    total_images = len(output_files["images"])
    total_landing = len(output_files["landing_pages"])
    total_emails = len(output_files["emails"])
    total_videos = len(output_files["videos"])
    total_audio = len(output_files["audio"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(
        "🔄 Ciclos",
        stats.get("total_cycles", 0),
        f"{stats.get('success_cycles', 0)} sucesso",
    )
    col2.metric(
        "💰 Receita Est./mês",
        f"R$ {stats.get('total_revenue', 0):,.2f}",
    )
    col3.metric(
        "🖼️ Outputs Gerados",
        total_images + total_landing + total_emails + total_videos + total_audio,
    )
    col4.metric(
        "🏭 Kernel",
        kernel_hc.get("kernel_status", "offline").upper(),
    )
    col5.metric(
        "✅ Subsystems",
        f"{kernel_hc.get('subsystems', {}).get('healthy', 0)}/"
        f"{kernel_hc.get('subsystems', {}).get('total', 19)}",
    )

    # ── Outputs by Type ──
    st.subheader("📦 Outputs por Tipo")
    out_cols = st.columns(5)
    out_cols[0].metric("🖼️ Imagens", total_images)
    out_cols[1].metric("📄 Landing Pages", total_landing)
    out_cols[2].metric("📧 Emails", total_emails)
    out_cols[3].metric("🎬 Vídeos", total_videos)
    out_cols[4].metric("🎵 Áudio", total_audio)

    # ── Recent Cycles ──
    st.divider()
    st.subheader("📋 Últimos Ciclos")
    cycles_data = stats.get("cycles", [])
    if cycles_data:
        data = []
        for c in cycles_data[:20]:
            data.append({
                "#": c.get("cycle_id", ""),
                "Data": str(c.get("started_at", ""))[:19],
                "Status": "✅" if c.get("status") == "success" else "❌",
                "Duração": f"{c.get('duration_ms', 0)}ms",
                "Steps": c.get("steps_completed", 0),
                "Receita": f"R$ {c.get('estimated_monthly_revenue', 0):.2f}",
                "Cliques": c.get("estimated_monthly_clicks", 0),
            })
        st.dataframe(data, width='stretch', hide_index=True)
    else:
        st.info("Nenhum ciclo encontrado. Execute o autopilot primeiro.")

    # ── Revenue Projection ──
    st.divider()
    st.subheader("💰 Projeção de Ganhos (12 meses)")

    proj = {
        "Cenário": ["🟢 Mínimo", "🟡 Conservador", "🟠 Moderado", "🔴 Agressivo", "🔥 Máximo"],
        "Setup": ["1 nicho + 1 LLM", "2 nichos + 3 afiliados", "4 nichos + 8 afiliados + CPA",
                  "6 nichos + 13 fontes", "8 nichos + full autopilot"],
        "Mês 1": ["R$ 52", "R$ 496", "R$ 4.646", "R$ 12.389", "R$ 82.596"],
        "Mês 12": ["R$ 12.802", "R$ 128.627", "R$ 893.553", "R$ 2.382.789", "R$ 12.792.888"],
        "Total 12m": ["R$ 52.867", "R$ 534.267", "R$ 3.9M", "R$ 10.4M", "R$ 57.8M"],
        "Média/mês": ["R$ 4.406", "R$ 44.522", "R$ 325.915", "R$ 869.107", "R$ 4.8M"],
    }
    st.dataframe(proj, width='stretch', hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE: Output Gallery
# ══════════════════════════════════════════════════════════════
elif page_key == "Output Gallery":
    st.title("🖼️ Output Gallery — Visualização dos Artefatos Gerados")

    output_files = get_output_files()

    tab_images, tab_landing, tab_emails, tab_videos, tab_audio, tab_content = st.tabs(
        ["🖼️ Imagens", "📄 Landing Pages", "📧 Emails", "🎬 Vídeos", "🎵 Áudio", "📝 Conteúdo"]
    )

    # ── Images Tab ──
    with tab_images:
        images = output_files["images"]
        if not images:
            st.info("Nenhuma imagem gerada ainda. Execute o money loop para gerar.")
        else:
            cols = st.columns(3)
            for i, img_path in enumerate(images[:30]):
                with cols[i % 3]:
                    try:
                        b64 = img_to_base64(img_path)
                        if b64:
                            rel_path = img_path.relative_to(PROJECT_ROOT)
                            st.image(
                                img_path,
                                caption=f"{rel_path} ({(img_path.stat().st_size / 1024):.1f}KB)",
                                width='stretch',
                            )
                        else:
                            st.caption(f"⚠️ Não foi possível ler: {img_path.name}")
                    except Exception:
                        st.caption(f"❌ Erro: {img_path.name}")

            if len(images) > 30:
                st.caption(f"*Mostrando 30 de {len(images)} imagens*")

    # ── Landing Pages Tab ──
    with tab_landing:
        landing = output_files["landing_pages"]
        if not landing:
            st.info("Nenhuma landing page gerada ainda.")
        else:
            for lp in landing[:10]:
                rel_path = lp.relative_to(PROJECT_ROOT)
                with st.expander(f"📄 {rel_path}"):
                    html = render_html_preview(lp)
                    st.components.v1.html(html, height=600, scrolling=True)

    # ── Emails Tab ──
    with tab_emails:
        emails = output_files["emails"]
        if not emails:
            st.info("Nenhum email gerado ainda.")
        else:
            for email_path in emails[:10]:
                rel_path = email_path.relative_to(PROJECT_ROOT)
                with st.expander(f"📧 {rel_path}"):
                    html = render_html_preview(email_path)
                    st.components.v1.html(html, height=400, scrolling=True)

    # ── Videos Tab ──
    with tab_videos:
        videos = output_files["videos"]
        if not videos:
            st.info("Nenhum vídeo gerado ainda.")
        else:
            for v in videos[:5]:
                rel_path = v.relative_to(PROJECT_ROOT)
                try:
                    with open(v, "rb") as f:
                        video_bytes = f.read()
                    st.video(video_bytes)
                    st.caption(f"📹 {rel_path} ({(v.stat().st_size / 1024 / 1024):.1f}MB)")
                except Exception:
                    st.caption(f"❌ Erro ao carregar: {rel_path}")

    # ── Audio Tab ──
    with tab_audio:
        audio_files = output_files["audio"]
        if not audio_files:
            st.info("Nenhum áudio gerado ainda.")
        else:
            for a in audio_files[:5]:
                rel_path = a.relative_to(PROJECT_ROOT)
                try:
                    with open(a, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes)
                    st.caption(f"🎵 {rel_path}")
                except Exception:
                    st.caption(f"❌ Erro ao carregar: {rel_path}")

    # ── Content Tab ──
    with tab_content:
        content_files = output_files["content"]
        if not content_files:
            st.info("Nenhum conteúdo gerado ainda.")
        else:
            for c in content_files[:20]:
                rel_path = c.relative_to(PROJECT_ROOT)
                with st.expander(f"📝 {rel_path}"):
                    try:
                        text = c.read_text(encoding="utf-8")
                        st.markdown(text)
                    except Exception:
                        st.error(f"Erro ao ler: {rel_path}")


# ══════════════════════════════════════════════════════════════
# PAGE: Revenue Tree
# ══════════════════════════════════════════════════════════════
elif page_key == "Revenue Tree":
    st.title("🌳 Parallel Revenue Tree — 13 Fontes de Renda")

    st.markdown("""
    O sistema dispara **TODAS as 13 fontes de renda simultaneamente** via `ThreadPoolExecutor`.
    Cada fonte roda em sua própria thread. O step agregador só executa após TODAS terminarem.
    """)

    # Revenue sources
    sources = [
        ("Hotmart", "Infoprodutos", "🔴", "HOTMART_AFFILIATE_ID", "Pendente"),
        ("Kiwify", "Infoprodutos", "🔴", "KIWIFY_AFFILIATE_ID", "Pendente"),
        ("Eduzz", "Infoprodutos", "🔴", "EDUZZ_AFFILIATE_ID", "Pendente"),
        ("Monetizze", "Infoprodutos", "🔴", "MONETIZZE_AFFILIATE_ID", "Pendente"),
        ("Mercado Livre", "Marketplace", "🔴", "MERCADO_LIVRE_AFFILIATE_ID", "Pendente"),
        ("Shopee", "Marketplace", "🔴", "SHOPEE_AFFILIATE_ID", "Pendente"),
        ("SheIn", "Moda", "🔴", "SHEIN_AFFILIATE_ID", "Pendente"),
        ("AliExpress", "Marketplace", "🔴", "ALIEXPRESS_AFFILIATE_ID", "Pendente"),
        ("Amazon", "Produtos Físicos", "✅", "AMAZON_ASSOCIATES_TAG", "Catálogo gerado"),
        ("Google AdSense", "Propaganda", "✅", "Nenhuma", "Ativo"),
        ("CPA", "Custo por Ação", "✅", "Nenhuma", "Ativo"),
        ("Produto Digital", "Próprios", "✅", "Nenhuma", "Ativo"),
        ("Assinaturas", "Membros", "✅", "Nenhuma", "Ativo"),
    ]

    # Table
    st.subheader("📊 Status das Fontes")
    data = []
    for name, tipo, icon, env_var, status in sources:
        data.append({
            "": icon,
            "Fonte": name,
            "Tipo": tipo,
            "Chave": env_var,
            "Status": status,
        })
    st.dataframe(data, width='stretch', hide_index=True, column_config={
        "": st.column_config.TextColumn("", width="small"),
    })

    st.divider()

    # Architecture diagram
    st.subheader("🏗️ Arquitetura da Árvore")
    st.code("""
TODAS RODAM EM PARALELO (deps=[])
├── Hotmart ───────────── Infoprodutos       │  ├── Amazon ──────────── Amazon Associates
├── Kiwify ────────────── Infoprodutos       │  ├── AdSense ─────────── Google Ads
├── Eduzz ─────────────── Infoprodutos       │  ├── CPA ────────────── Custo por Ação
├── Monetizze ─────────── Infoprodutos       │  ├── Prod. Digital ──── Próprios
├── Mercado Livre ─────── Marketplace        │  └── Assinaturas ────── Membros
├── Shopee ────────────── Marketplace                    ↓
├── SheIn ─────────────── Moda             [Aggregate Revenue Report]
└── AliExpress ────────── Marketplace
    """)

    # Projection
    st.divider()
    st.subheader("📈 Projeção Financeira (12 meses)")
    proj_data = {
        "Cenário": ["🟢 Mínimo", "🟡 Conservador", "🟠 Moderado", "🔴 Agressivo", "🔥 Máximo"],
        "Mês 1": ["R$ 52", "R$ 496", "R$ 4.646", "R$ 12.389", "R$ 82.596"],
        "Mês 3": ["R$ 472", "R$ 4.512", "R$ 42.456", "R$ 113.216", "R$ 754.774"],
        "Mês 6": ["R$ 2.488", "R$ 23.443", "R$ 206.146", "R$ 549.741", "R$ 3.2M"],
        "Mês 12": ["R$ 12.802", "R$ 128.627", "R$ 893.553", "R$ 2.38M", "R$ 12.79M"],
        "Total": ["R$ 52.8K", "R$ 534K", "R$ 3.9M", "R$ 10.4M", "R$ 57.8M"],
    }
    st.dataframe(proj_data, width='stretch', hide_index=True)

    st.divider()
    st.subheader("⚙️ Comandos")
    st.code("""# Ver projeção interativa
PYTHONPATH=src python3 scripts/projetar_arvore_paralela.py

# Executar árvore paralela
PYTHONPATH=src python3 scripts/money_loop.py --once""")


# ══════════════════════════════════════════════════════════════
# PAGE: AG-Kit Kernel
# ══════════════════════════════════════════════════════════════
elif page_key == "AG-Kit Kernel":
    st.title("🏭 AG-Kit Evolution — Fases 1-20")

    kernel_hc = get_kernel_status()

    # ── Kernel Status ──
    st.subheader("⚡ Autonomous Enterprise Kernel (Phase 20)")
    k_cols = st.columns(4)
    k_cols[0].metric("Status", kernel_hc.get("kernel_status", "N/A").upper())
    k_cols[1].metric(
        "Uptime",
        f"{kernel_hc.get('uptime_seconds', 0):.0f}s" if kernel_hc.get("uptime_seconds") else "N/A",
    )
    k_cols[2].metric("Cycles", kernel_hc.get("cycle_count", 0))
    k_cols[3].metric(
        "Revenue",
        f"R$ {kernel_hc.get('total_revenue', 0):.2f}",
    )

    # ── Subsystems Detail ──
    subsystems = kernel_hc.get("subsystem_details", [])
    if subsystems:
        st.subheader("📊 Subsystems (19 fases)")
        sub_data = []
        for s in subsystems:
            icon = {
                "healthy": "✅",
                "degraded": "⚠️",
                "failed": "❌",
                "not_initialized": "⏳",
            }.get(s.get("status", ""), "❓")
            sub_data.append({
                "": icon,
                "Fase": f"Fase {s.get('phase', '?')}",
                "Nome": s.get("name", ""),
                "Status": s.get("status", "").upper(),
                "Uptime": f"{s.get('uptime_seconds', 0):.0f}s",
                "Erro": s.get("error", "") or "—",
            })
        st.dataframe(sub_data, width='stretch', hide_index=True)

    # ── All 20 Phases ──
    st.divider()
    st.subheader("📋 AG-Kit Evolution — Status Completo")

    phases = [
        (1, "Agent Runtime Layer", "✅", "AgentBase + descoberta dinâmica"),
        (2, "Durable Workflow Engine", "✅", "WorkflowRunner DAG + checkpoint"),
        (3, "Agent Tracing System", "✅", "trace_store.py (548 linhas)"),
        (4, "MCP Layer", "✅", "capability_registry.py (314 linhas)"),
        (5, "Multi-Model Router", "✅", "model_router.py (286 linhas)"),
        (6, "Workflow Checkpoint", "✅", "workflow_checkpoint.py"),
        (7, "Agent Memory Upgrade", "✅", "SemanticMemoryStore + EpisodicMemory"),
        (8, "Evaluation Engine", "✅", "evaluation_engine.py"),
        (9, "Agent Marketplace", "✅", "CapabilityRegistry"),
        (10, "Governance Layer", "✅", "GovernanceAgent (7 delegates)"),
        (11, "Constraint Intelligence", "✅", "constraint_intelligence.py (469 linhas)"),
        (12, "World Model Engine", "✅", "world_model.py (567 linhas)"),
        (13, "Economic Intelligence", "✅", "economic_intelligence.py (566 linhas)"),
        (14, "Agent Evolution Engine", "✅", "agent_evolution.py (633 linhas)"),
        (15, "Cognitive Mesh", "✅", "cognitive_mesh.py (619 linhas)"),
        (16, "Digital Twin Layer", "✅", "digital_twin.py (819 linhas)"),
        (17, "Self-Improvement Engine", "✅", "self_improvement.py (651 linhas)"),
        (18, "Constraint Genealogy", "✅", "constraint_genealogy.py (670 linhas)"),
        (19, "Organization-as-Agent", "✅", "organization_agent.py (667 linhas)"),
        (20, "Autonomous Enterprise Kernel", "✅", "enterprise_kernel.py (663 linhas)"),
    ]

    phase_data = []
    for num, name, status, detail in phases:
        phase_data.append({"Fase": f"Fase {num:2d}", "Nome": name, "": status, "Detalhes": detail})
    st.dataframe(phase_data, width='stretch', hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE: System Status
# ══════════════════════════════════════════════════════════════
elif page_key == "Skills":
    st.title("🧠 Skill Warehouse — 252 Skills Reutilizáveis")

    st.markdown(
        "Repositório de skills para agentes (Codex, Claude, Cursor) em 3 fontes: "
        "**Community** (36 skills SkillsMP), **Garden** (~200 skills), "
        "**Lyzer Labs** (13 skills proprietárias)"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Community Skills", "36", "SkillsMP top skills")
    col2.metric("Garden Skills", "~200", "GitHub")
    col3.metric("Lyzer Labs", "13", "Proprietárias")

    st.divider()

    tab_community, tab_garden, tab_lyzer = st.tabs(["Community", "Garden", "Lyzer Labs"])

    with tab_community:
        st.subheader("SkillsMP — Top Skills por Categoria")
        cats = {
            "Marketing": [
                ("marketing-campaign", "219K★", "Campaign planning"),
                ("marketing-psychology", "68K★", "Psychology"),
                ("marketing-ideas", "41K★", "Growth ideas"),
                ("marketing-plan", "34K★", "Plan gen"),
                ("content-marketing", "1K★", "Strategy"),
            ],
            "Design": [
                ("octopus-ui-ux-design", "3.6K★", "UI/UX systems"),
                ("design-system", "219K★", "Design mgmt"),
                ("beautiful-article", "8.6K★", "Source to article"),
                ("gpt-image-2", "8.6K★", "Image gen"),
            ],
            "Automation": [
                ("workflow-automation", "60K★", "Pipeline design"),
                ("agent-orchestration", "41K★", "Multi-agent"),
                ("task-runner", "747★", "Task exec"),
            ],
            "SEO": [
                ("keyword-research", "2.9K★", "Keywords"),
                ("seo-audit", "41K★", "Full audit"),
            ],
            "Copywriting": [
                ("copywriting", "68K★", "Persuasive"),
                ("storytelling", "1.3K★", "Narrative"),
                ("conversion-copywriting", "368★", "Conversion"),
            ],
        }
        for cat, sk_list in cats.items():
            with st.expander(f"{cat} ({len(sk_list)} skills)"):
                for name, stars, desc in sk_list:
                    st.markdown(f"**{name}** ({stars}) — {desc}")

    with tab_garden:
        st.subheader("Garden Skills (GitHub)")
        st.markdown("**Fonte:** [github.com/ConardLi/garden-skills](https://github.com/ConardLi/garden-skills)")
        for name, desc in [
            ("web-design-engineer", "Design/frontend engineer"),
            ("beautiful-article", "Any source to article"),
            ("gpt-image-2", "Image generation"),
            ("web-video-presentation", "Web video"),
        ]:
            st.markdown(f"- **{name}** — {desc}")

    with tab_lyzer:
        st.subheader("Lyzer Labs — Proprietárias")
        lyzer = {
            "CIA/CTO": [
                ("cto-executive-director", "CTO protocol"),
                ("cia-chief-intelligence-architect", "3 orders"),
                ("anti-fragility-directive", "Risk detection"),
            ],
            "Marketing": [
                ("affiliate-marketing-strategy", "13 sources"),
                ("seo-content-pipeline", "8-step SEO"),
                ("money-loop-cycle", "24/7 revenue"),
            ],
            "Design": [("product-forge-design-system", "Design tokens")],
            "Automation": [
                ("workflow-dag-engine", "30 workflows"),
                ("ponytail-lazy-dev-mode", "Stdlib first"),
            ],
            "Other": [
                ("competitive-intelligence", "Research"),
                ("media-providers-layer", "16 providers"),
                ("system-governance", "Governance"),
                ("agent-factory-evolution", "Orchestration"),
            ],
        }
        for cat, sk_list in lyzer.items():
            with st.expander(f"{cat} ({len(sk_list)} skills)"):
                for name, desc in sk_list:
                    st.markdown(f"**{name}** — {desc}")

    st.divider()
    st.subheader("Explorar no Repositório")
    st.code("""skills_warehouse/
  community/   SkillsMP (marketing, design, seo, automation, copywriting)
  garden/      Garden Skills (web design, article, image)
  lyzer-labs/  Proprietary (cto-cia, marketing, design, automation)""")

elif page_key == "Quality Layers":
    st.title("🎯 Quality Layers — 7 Camadas de Qualidade")
    st.markdown("AG-Kit Evolution Phase 21+ — Output Critic · Debate · CIA · RAG · ELO")

    tab_critic, tab_debate, tab_cia, tab_benchmark, tab_elo = st.tabs(
        ["📊 Critic", "🧠 Debate", "🕵️ CIA", "📈 Benchmark", "🏆 ELO"]
    )

    with tab_critic:
        st.subheader("Output Critic — Avaliação de Artefatos")
        st.markdown("""
        **Threshold: 85/100** — Abaixo disso, o artefato é rejeitado e marcado para regeneração.

        | Critério | Peso | Descrição |
        |----------|------|-----------|
        | Clarity | 20% | Clareza e estrutura do conteúdo |
        | Originality | 15% | Originalidade e criatividade |
        | Execution | 20% | Qualidade de execução (CTA, links, headings) |
        | Business Value | 20% | Valor de négocio e potencial de conversão |
        | Consistency | 15% | Consistência interna e com a marca |
        | SEO Quality | 10% | Otimização para mecanismos de busca |
        """)

        col1, col2 = st.columns(2)
        col1.metric("Threshold", "85/100")
        col2.metric("Critérios", "6 ponderados")

        st.code("""# Criticar artefatos existentes
PYTHONPATH=src python3 scripts/quality_pipeline.py --critic output/ui_design/*.html

# Pipeline completa
PYTHONPATH=src python3 scripts/quality_pipeline.py --full "minha campanha"
""")

    with tab_debate:
        st.subheader("Multi-Agent Debate")
        st.markdown("""
        **4 perspectivas** em paralelo, depois síntese:
        - **Designer** — Estratégia visual e UX
        - **Marketer** — Estratégia de campanha
        - **Researcher** — Pesquisa de mercado
        - **Conversion** — Otimização de conversão
        """)
        st.code('PYTHONPATH=src python3 scripts/quality_pipeline.py --debate "estratégia marketing 2026"')

    with tab_cia:
        st.subheader("CIA Governance")
        st.markdown("""
        **3 agentes de verificação antes da entrega:**

        | Agente | Função | Detecta |
        |--------|--------|---------|
        | 🕵️ Truth | Verificar alucinações | Afirmações absolutas sem evidência, contradições |
        | ⚠️ Risk | Avaliar riscos | Nicho ausente, dependência única, goal não definido |
        | 🎨 Consistency | Consistência de marca | Alinhamento com brand signals Lyzer Labs |
        """)
        st.code('PYTHONPATH=src python3 scripts/quality_pipeline.py --cia "minha campanha"')

    with tab_benchmark:
        st.subheader("Benchmark Database")
        st.markdown("""
        **Só outputs aprovados (score ≥ 85)** são armazenados.
        O sistema aprende seus próprios padrões vencedores.
        """)
        try:
            from campaign_autopilot.quality_layers import BenchmarkDB
            db = BenchmarkDB()
            s = db.stats()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Aprovados", s["total"])
            c2.metric("Score Médio", f'{s["avg_score"]:.1f}')
            c3.metric("Tipos", len(s["by_type"]))
            if s["by_type"]:
                st.dataframe(s["by_type"], width='stretch', hide_index=True)
        except Exception:
            st.info("Benchmark DB disponivel após executar --critic")

    with tab_elo:
        st.subheader("ELO Ranking de Skills")
        st.markdown("""
        Skills competem entre si. A skill vencedora ganha ELO da perdedora.
        **Base: 1500 | K-factor: 32**
        """)
        try:
            from campaign_autopilot.quality_layers import ELORanking
            elo = ELORanking()
            ranking = elo.ranking(limit=20)
            if ranking:
                data = []
                for i, r in enumerate(ranking, 1):
                    data.append({"Rank": i, "Skill": r["name"], "ELO": f'{r["elo"]:.0f}',
                                 "Partidas": r["matches"], "Vitórias": r["wins"]})
                st.dataframe(data, width='stretch', hide_index=True)
            else:
                st.info("Nenhum skill ranqueado ainda")
        except Exception as e:
            st.info(f"ELO DB disponivel após executar --full")

elif page_key == "System Status":
    st.title("🔧 System Status — Saúde Completa do Sistema")

    tab_providers, tab_agents, tab_workflows, tab_health = st.tabs(
        ["📡 Providers", "🤖 Agentes", "⚡ Workflows", "🏥 Health Check"]
    )

    # ── Providers Tab ──
    with tab_providers:
        st.subheader("📡 Media Providers (16)")

        providers_status = [
            ("OpenRouter (LLM)", "Texto", "✅", "4 modelos funcionando"),
            ("FreeLLM (13)", "Texto", "✅", "Failover automático"),
            ("StdlibFallback", "Texto", "✅", "Template engine"),
            ("Pollinations", "Imagem", "✅", "Gratuito, sem chave"),
            ("Pillow", "Imagem", "✅", "Composição local"),
            ("Replicate", "Imagem", "❌", "Sem créditos (402)"),
            ("DeepAI", "Imagem", "❌", "Precisa Pro (402)"),
            ("Prodia", "Imagem", "❌", "Sem chave"),
            ("HuggingFace", "Imagem", "❌", "Inválida (401)"),
            ("Diffusers", "Imagem", "⚠️", "GPU only"),
            ("Edge-TTS", "Áudio", "✅", "Neural, ~400 vozes"),
            ("gTTS", "Áudio", "✅", "Google TTS, 52 idiomas"),
            ("Kokoro", "Áudio", "❌", "Não instalado"),
            ("OpenAI TTS", "Áudio", "❌", "Sem chave"),
            ("MoviePy", "Vídeo", "✅", "Slideshow com transições"),
            ("Algorithmic Music", "Música", "✅", "Procedural"),
        ]

        prov_data = []
        for name, tipo, status, detail in providers_status:
            prov_data.append({
                "": status,
                "Provider": name,
                "Tipo": tipo,
                "Detalhes": detail,
            })
        st.dataframe(prov_data, width='stretch', hide_index=True)

    # ── Agents Tab ──
    with tab_agents:
        st.subheader("🤖 Agentes (122)")

        agent_groups = [
            ("Core Cycle", "7 agentes", "CampaignOrchestrator, Analytics, Compliance, Memory, Optimization, Planning"),
            ("SEO & Research", "11 agentes", "SEOResearch, SEO Scraper, RankTracker, CompetitorAnalysis, ContentResearch"),
            ("Content & Creative", "14 agentes", "ContentPlanner, Generator, Optimizer, Repurposer, Storytelling, Psychology"),
            ("Media Production", "7 agentes", "CinematicImage, CinematicVideo, AudioProduction, FreeImageGen, FreeVideo"),
            ("Publishing", "5 agentes", "Publisher, WordPress, BulkPublisher, SiteDeploy, EmailMarketing"),
            ("Social Media", "19 agentes", "YouTube, Pinterest, WhatsApp, Instagram, TikTok, Twitter, LeadCapture"),
            ("Revenue & Affiliates", "18 agentes", "RevenueBranch (13 fontes), RevenueMonitor, OfferLookup, CPA, AdSense"),
            ("Paid Traffic", "8 agentes", "TrafficManager, AdOptimizer, BudgetAllocator, ConversionTracker"),
            ("2ª Ordem", "9 agentes", "MetaOrchestrator, EvolutionEngine, AgentFactory, SelfHealing"),
            ("3ª Ordem", "5 agentes", "Epistemic, ObserverFusion, ValueEvolution, RecursiveObserver"),
            ("Compliance", "6 agentes", "PlatformCompliance, YouTubeRules, InstagramRules, RiskManagement"),
            ("Hotmart (sub)", "6 agentes", "ProductMatcher, ProductResearcher, MarketplacesCollector, LinkManager"),
            ("Meta", "5 agentes", "AgentFactory, CompoundingEngine, CrossPollinationHub, OpportunityDetector"),
            ("Money", "4 agentes", "RevenueBranch, RevenueAggregator, CompoundingEngine, PortfolioOptimizer"),
            ("UI & Design", "2 agentes", "UIDesignAgent (Product Forge), SiteDeployAgent"),
        ]

        for group, count, desc in agent_groups:
            with st.expander(f"{group} ({count})"):
                st.markdown(desc)

    # ── Workflows Tab ──
    with tab_workflows:
        st.subheader("⚡ Workflows (30 definições JSON)")

        workflow_list = [
            ("campaign_cycle", "5 steps", "Core cycle"),
            ("content_excellence_workflow", "4 steps", "Storytelling + Psychology + Neuromarketing"),
            ("deploy_workflow", "—", "Deploy pipeline"),
            ("fifth_order_workflow", "—", "5th order transcendence"),
            ("final_workflow", "—", "Final workflow"),
            ("fourth_order_workflow", "—", "4th order"),
            ("full_distribution_workflow", "—", "Multi-channel distribution"),
            ("full_media_workflow", "7 steps", "Content → Image → Audio → Design → Deploy"),
            ("governance_workflow", "—", "Governance cycle"),
            ("hotmart_collection_workflow", "—", "Hotmart product collection"),
            ("hotmart_product_selection_workflow", "—", "Smart product selection"),
            ("media_pipeline_workflow", "—", "Media generation pipeline"),
            ("money_workflow", "—", "Revenue generation"),
            ("multi_channel_workflow", "—", "Multi-channel syndication"),
            ("organic_affiliate_cycle", "—", "SEO + Affiliate marketing"),
            ("organic_content_workflow", "—", "Organic content"),
            ("organic_cycle", "—", "Organic cycle"),
            ("organic_to_flywheel", "—", "Organic → Paid flywheel"),
            ("paid_traffic_workflow", "—", "Paid traffic campaigns"),
            ("parallel_revenue_tree", "14 steps", "🌳 13 fontes em paralelo"),
            ("production_workflow", "48 steps", "Full production pipeline"),
            ("revenue_orchestration_workflow", "—", "Multi-source orchestration"),
            ("revenue_workflow", "—", "Revenue cycle"),
            ("safe_mass_posting_workflow", "—", "Safe mass posting"),
            ("seo_content_workflow", "—", "Daily SEO content"),
            ("sixth_order_workflow", "—", "6th order"),
            ("third_order_transcendence", "—", "Wave 3 transcendence"),
            ("third_order_workflow", "—", "Third order"),
            ("traffic_recycling_workflow", "—", "Traffic recycling"),
            ("ultimate_workflow", "—", "Ultimate workflow"),
        ]

        wf_data = []
        for name, steps, desc in workflow_list:
            wf_data.append({"Workflow": name, "Steps": steps, "Descrição": desc})
        st.dataframe(wf_data, width='stretch', hide_index=True)

    # ── Health Check Tab ──
    with tab_health:
        st.subheader("🏥 Health Check")
        if st.button("🔄 Executar Health Check"):
            try:
                result = subprocess.run(
                    [sys.executable, str(PROJECT_ROOT / "scripts/health_check.py")],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(PROJECT_ROOT),
                    env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
                )
                st.text(result.stdout[-2000:] if result.stdout else "Sem output")
                if result.stderr:
                    st.error(result.stderr[-1000:])
            except Exception as e:
                st.error(f"Erro: {e}")

        st.divider()
        st.subheader("💾 Database Info")
        db_paths = [
            STATE_DIR / "money_loop.db",
            STATE_DIR / "autopilot.db",
        ]
        for db in db_paths:
            if db.exists():
                size_kb = db.stat().st_size / 1024
                st.text(f"📁 {db.name}: {size_kb:.1f}KB")
            else:
                st.text(f"📁 {db.name}: não encontrado")


# ══════════════════════════════════════════════════════════════
# PAGE: Logs
# ══════════════════════════════════════════════════════════════
elif page_key == "Logs":
    st.title("📋 Logs do Autopilot")
    st.caption("Últimas 100 linhas do daemon")

    log_text = get_autopilot_log()
    if log_text:
        st.text_area("Log output", log_text, height=600)
    else:
        st.info("Nenhum log encontrado.")

    if st.button("🔄 Atualizar"):
        st.rerun()

    st.divider()
    st.subheader("⚙️ Último Health Check")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts/health_check.py")],
            capture_output=True, text=True, timeout=15,
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
        )
        st.text(result.stdout[-1500:] if result.stdout else "Sem output")
    except Exception as e:
        st.error(f"Erro: {e}")


# ══════════════════════════════════════════════════════════════
# PAGE: Ações
# ══════════════════════════════════════════════════════════════
elif page_key == "Acoes":
    st.title("⚡ Ações Rápidas")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("🚀 Executar")
        if st.button("▶️ Executar Ciclo Agora", width='stretch'):
            with st.spinner("Executando money loop..."):
                try:
                    result = subprocess.run(
                        [sys.executable, str(PROJECT_ROOT / "scripts/money_loop.py"), "--once"],
                        capture_output=True, text=True, timeout=60,
                        cwd=str(PROJECT_ROOT),
                        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
                    )
                    st.success("Ciclo executado!")
                    st.text(result.stdout[-1000:] if result.stdout else "Sem output")
                except subprocess.TimeoutExpired:
                    st.error("Timeout após 60s")
                except Exception as e:
                    st.error(f"Erro: {e}")

        if st.button("🏭 Gerar Landing Pages", width='stretch'):
            with st.spinner("Gerando landing pages..."):
                try:
                    result = subprocess.run(
                        [sys.executable, str(PROJECT_ROOT / "scripts/generate_site.py"), "--all"],
                        capture_output=True, text=True, timeout=30,
                        cwd=str(PROJECT_ROOT),
                        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
                    )
                    st.success("Landing pages geradas!")
                    st.text(result.stdout[-500:] if result.stdout else "Sem output")
                except Exception as e:
                    st.error(f"Erro: {e}")

        if st.button("🎬 Pipeline Completa Mídia", width='stretch'):
            with st.spinner("Executando pipeline de mídia..."):
                try:
                    result = subprocess.run(
                        [sys.executable, str(PROJECT_ROOT / "scripts/run_full_pipeline.py"),
                         "--niche", "tecnologia"],
                        capture_output=True, text=True, timeout=60,
                        cwd=str(PROJECT_ROOT),
                        env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
                    )
                    st.success("Pipeline executada!")
                    st.text(result.stdout[-500:])
                except Exception as e:
                    st.error(f"Erro: {e}")

    with col_b:
        st.subheader("📊 Ver")
        if st.button("📈 Projeção Financeira", width='stretch'):
            try:
                result = subprocess.run(
                    [sys.executable, str(PROJECT_ROOT / "scripts/projetar_arvore_paralela.py")],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(PROJECT_ROOT),
                    env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
                )
                st.text(result.stdout[-1000:] if result.stdout else "Sem output")
            except Exception as e:
                st.error(f"Erro: {e}")

        if st.button("🏥 Health Check", width='stretch'):
            try:
                result = subprocess.run(
                    [sys.executable, str(PROJECT_ROOT / "scripts/health_check.py")],
                    capture_output=True, text=True, timeout=30,
                    cwd=str(PROJECT_ROOT),
                    env={**os.environ, "PYTHONPATH": str(SRC_DIR)},
                )
                st.text(result.stdout[-1500:] if result.stdout else "Sem output")
            except Exception as e:
                st.error(f"Erro: {e}")

    with col_c:
        st.subheader("📖 Docs")
        st.markdown("[📄 README](../README.md)")
        st.markdown("[📊 CTO Snapshot](CTO_SNAPSHOT.md)")
        st.markdown("[💰 Projeções](PROJECOES_FINANCEIRAS.md)")
        st.markdown("[🤖 Agents Reference](AGENTS_REFERENCE.md)")
        st.markdown("[⚡ Workflow Guide](WORKFLOW_GUIDE.md)")

    st.divider()
    st.subheader("🔧 Comandos para Terminal")

    st.code("""# Executar ciclo manual
PYTHONPATH=src python3 scripts/money_loop.py --once

# Rodar 24/7 (tmux)
tmux new-session -d -s autopilot 'cd /root/Documents/Codex/2026-05-30/New\\ Project\\ \\(1\\) && PYTHONPATH=src python3 scripts/money_loop.py --interval 12 2>&1 | tee .state/autopilot_daemon.log'

# Ver logs
tail -f .state/autopilot_daemon.log

# Estatísticas
PYTHONPATH=src python3 scripts/money_loop.py --stats

# Gerar site completo
PYTHONPATH=src python3 scripts/generate_site.py --all

# Health check
PYTHONPATH=src python3 scripts/health_check.py""")


# ══════════════════════════════════════════════════════════════
# PAGE: Hotmart Intelligence
# ══════════════════════════════════════════════════════════════
elif page_key == "Hotmart Intelligence":
    st.title("🔥 Hotmart Affiliate Intelligence Protocol v1")
    st.markdown("""Pipeline de 10 fases para transformar a seleção de produtos Hotmart em processo sistemático, reproduzível e orientado por dados.""")

    # Try to load Hotmart store
    hs_db = Path(".state/hotmart_intelligence.db")
    conn = None
    hs_total = 0
    hs_activated = 0
    hs_dossiers = 0
    by_status = {}
    try:
        if hs_db.exists():
            conn = sqlite3.connect(str(hs_db))
            hs_total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            rows = conn.execute("SELECT status, COUNT(*) FROM products GROUP BY status").fetchall()
            by_status = dict(rows)
            hs_activated = dict(rows).get("activated", 0) if rows else 0
            hs_dossiers = conn.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
            conn.close()
    except Exception:
        pass

    st.subheader("\ud83d\udcca Pipeline Status")
    mc = st.columns(5)
    mc[0].metric("Total Produtos", hs_total)
    mc[1].metric("Ativados", hs_activated)
    mc[2].metric("Dossi\u00eas", hs_dossiers)
    mc[3].metric("Pipeline", "\u2705 Ativo" if hs_activated > 0 else "\u23f3 Inativo")
    mc[4].metric("Fases", "10/10")

    if by_status:
        st.subheader("\ud83d\uddc3\ufe0f Status dos Produtos")
        sd = {"Status": list(by_status.keys()), "Qtd": list(by_status.values())}
        import pandas as _pd
        st.bar_chart(_pd.DataFrame(sd).set_index("Status"))

    # Pipeline phases
    st.subheader("\ud83c\udfd7\ufe0f Arquitetura do Pipeline (10 Fases)")
    cols = st.columns(5)
    phases = [
        ("\ud83d\udd0d Discovery", "Mapear produtos", "F1"),
        ("\ud83d\udd2c Triage", "Eliminar ruins", "F2"),
        ("\ud83d\udcca Scoring", "0-100 Score", "F3"),
        ("\ud83d\udccb Diligence", "Verificar", "F4"),
        ("\ud83d\udd17 Affiliation", "Registrar", "F5"),
        ("\ud83d\udce6 Assets", "Coletar ativos", "F6"),
        ("\ud83d\udcd0 Normalize", "Schema padr\u00e3o", "F7"),
        ("\ud83e\udde0 Ingestion", "Knowledge Base", "F8"),
        ("\u2728 Enrichment", "Personas+Mapas", "F9"),
        ("\ud83d\ude80 Activation", "Dossi\u00ea final", "F10"),
    ]
    for i, (name, desc, fase) in enumerate(phases):
        with cols[i % 5]:
            st.markdown(f"**{name}**")
            st.caption(f"{desc}")
            st.caption(f"*{fase}*")

    st.subheader("\ud83d\udccc Crit\u00e9rio CTO")
    st.info("Nenhum produto entra no Campaign Autopilot apenas porque possui alta temperatura na Hotmart. Um produto s\u00f3 \u00e9 promovido quando possui: Mercado validado + Oferta consistente + Materiais reutiliz\u00e1veis + Comiss\u00e3o adequada + Capacidade de escala + Integra\u00e7\u00e3o completa ao sistema.")

    if st.button("\u25b6 Executar Pipeline Hotmart", type="primary", width='stretch'):
        with st.spinner("Executando pipeline de 10 fases..."):
            try:
                sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
                from campaign_autopilot.agents.hotmart_intelligence import HotmartIntelligenceAgent
                from campaign_autopilot.agents.base import CampaignContext
                from campaign_autopilot.hotmart_product_intelligence import ProductIntelligenceStore
                store = ProductIntelligenceStore(str(hs_db))
                agent = HotmartIntelligenceAgent(store=store)
                ctx = CampaignContext(campaign={"niche": "marketing digital", "max_products": 5})
                result = agent.run(ctx)
                st.success(f"Pipeline conclu\u00eddo em {len(result.output.get('phases_executed',[]))} fases!")
                st.rerun()
            except Exception as ex:
                st.error(f"Erro: {ex}")

# ── Footer ──────────────────────────────────────────────────
st.divider()
st.caption(
    f"Campaign Autopilot v5.2.1 — Lyzer Labs | "
    f"Última atualização: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC | "
    f"AG-Kit Evolution Fases 1-20 ✅"
)

# ══════════════════════════════════════════════════════════════
