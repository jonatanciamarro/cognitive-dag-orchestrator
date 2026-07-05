---
name: campaign-autopilot
description: Sistema de marketing de afiliados 100% orgânico com workflow DAG multi-agente (128 agentes), Quality Layers, UI/UX 21st.dev, geração de conteúdo, site estático e meta-cognição. Use para tarefas de marketing digital, SEO, geração de conteúdo, UI/UX design, análise de concorrência e automação de marketing.
---

# Campaign Autopilot Skill

> Skill para IA agents trabalharem no projeto Campaign Autopilot.

## Visão Geral

Campaign Autopilot é um sistema completo de marketing de afiliados que opera **sem tráfego pago**. Ele usa 29 agentes especialistas orquestrados por um workflow DAG paralelo, com camada cognitiva (memória semântica, explicações, feedback, síntese) e meta-cognitiva (detecção de drift, metas, epistemologia).

## Estrutura do Projeto

```
├── src/campaign_autopilot/     # Core (40 módulos, ~12K linhas)
│   ├── agents/                 # 128 agentes (~30K linhas)
│   ├── quality_layers.py       # 7 Quality Layers (Critic, Debate, CIA, RAG, ELO)
│   ├── enterprise_kernel.py    # AG-Kit Phase 20
│   ├── auto_regenerate.py      # Auto-regeneration engine
│   ├── ui_component_registry.py # 21st.dev-style UI components
│   └── ui_design_memory.py     # UI design SQLite tracking
├── workflows/                  # 31 DAG definitions (inclui ui_design_workflow)
├── configs/                    # Cycle configuration profiles
├── skills/                     # Skill docs
├── skills_warehouse/           # 252 skills (SkillsMP + Garden + Lyzer Labs)
├── docs/                       # 28 documentation files
├── scripts/                    # autopilot.py, quality_pipeline.py, deploy.sh
├── site_generator/             # Static site generator
├── dashboard/                  # Streamlit dashboard (quality tab)
├── tests/                      # 66 test files
└── site/                       # Generated static site
```

## Workflows Principais

| Workflow | Steps | Objetivo |
|----------|-------|----------|
| `production_workflow.json` | 23 | Completo: 9 canais de tráfego |
| `final_workflow.json` | 17 | Completo com rank tracking |
| `money_workflow.json` | 14 | Foco em dinheiro |
| `revenue_workflow.json` | 13 | Foco em receita |
| `deploy_workflow.json` | 15 | Geração de site |
| `ultimate_workflow.json` | 19 | 9 canais sociais |

## Agentes Disponíveis (29)

**Core (5):** analytics, compliance, memory_lookup, optimization, execution_planning
**SEO (4):** seo_research, seo_scraper, competitor_analysis, rank_tracker
**Conteúdo (5):** content_planner, content_generator, content_optimizer, content_repurposer, publisher, bulk_publisher
**Publicação (2):** wp_publisher, site_deploy
**Marketing (8):** youtube_marketing, email_marketing, pinterest_marketing, instagram_marketing, tiktok_marketing, twitter_marketing, whatsapp_marketing, lead_capture
**Monitoria (3):** revenue_monitor, analytics_feedback, offer_lookup

## Como Executar

```bash
# Setup
make setup

# Workflow de produção
campaign-autopilot --workflow workflows/production_workflow.json --context examples/affiliate_context.json --db .state/db.sqlite3

# Gerar site
python3 -c "from site_generator.generator import SiteGenerator; SiteGenerator('site').generate([...])"

# Dashboard
make dashboard

# Testes
make test
```

## Convenções de Código

- Stdlib only (Python 3.10+) — zero dependências externas
- `AgentBase` → `run(context) → AgentResult` para todos os agentes
- Workflows em JSON com DAG (depends_on)
- SQLite WAL para persistência
- camelCase para step IDs, snake_case para arquivos
- Documentação em português (público brasileiro)
- Código em inglês (padrão internacional)


## Provider Layer (v2)

## Módulos Principais

### Core
- `src/campaign_autopilot/workflow.py`: DAG WorkflowRunner
- `src/campaign_autopilot/agents/`: all 105 agents
- `src/campaign_autopilot/cli.py`: CLI interface

### Provider Layer (AG-Kit Evolution)
- `src/campaign_autopilot/media_providers.py`: **ProviderManager** + **MediaRouter** (image/audio/video/music)
- `src/campaign_autopilot/model_router.py`: **Multi-Model Router** (cost-aware LLM routing)
- `src/campaign_autopilot/free_llm_providers.py`: 13 free LLM providers with auto-failover
- `src/campaign_autopilot/free_content_generator.py`: stdlib fallback engine

### Tracing & Resilience
- `src/campaign_autopilot/trace_store.py`: **TraceStore** SQLite + **TraceRecorder**
- `src/campaign_autopilot/workflow_checkpoint.py`: **CheckpointWorkflowRunner** (crash recovery)

### Registry & Evaluation
- `src/campaign_autopilot/capability_registry.py`: **CapabilityRegistry** + MCP tools
- `src/campaign_autopilot/evaluation_engine.py`: **EvaluationEngine** (scorecard, benchmark)

### Key Integrations
- Pollinations.AI: free AI images, zero API key
- Edge-TTS: Microsoft neural voices (gratis)
- LiteLLM: 100+ models via unified API
- OpenRouter: 200+ free models
