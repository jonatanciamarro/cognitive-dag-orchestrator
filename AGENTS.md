# Campaign Autopilot — Agent Instructions for AI Coding Agents

## Skill Warehouse
This project includes a **Skill Warehouse** at `skills_warehouse/` with 250+ reusable skills:
- `skills_warehouse/community/` — Skills from SkillsMP (marketing, design, seo, automation, copywriting)
- `skills_warehouse/garden/` — Garden Skills (web design, articles, image gen)
- `skills_warehouse/lyzer-labs/` — Proprietary Lyzer Labs skills (CTO, CIA, marketing, UI/UX design, automation)

### Key Skills to Load
When working on this project, consider loading these skills:
1. `skills_warehouse/lyzer-labs/cto-cia/cto-executive-director.md` — CTO operating protocol
2. `skills_warehouse/lyzer-labs/automation/ponytail-lazy-dev-mode.md` — Engineering philosophy
3. `skills_warehouse/lyzer-labs/governance/system-governance.md` — Governance patterns
4. `skills_warehouse/lyzer-labs/ui-design/21st-dev-component-system.md` — UI/UX component generation
5. `skills_warehouse/lyzer-labs/agent-orchestration/agent-factory-evolution.md` — Agent evolution

## Quality Layers (AG-Kit Phase 21+)
The system has 7 quality layers for artifact validation:
- `src/campaign_autopilot/quality_layers.py` — OutputCritic, DebateOrchestrator, BenchmarkDB, CampaignKnowledge, CIA Agents, RAGEngine, ELORanking
- `src/campaign_autopilot/auto_regenerate.py` — Auto-regeneration engine (3 attempts with feedback)
- `scripts/quality_pipeline.py` — CLI with --critic, --debate, --cia, --benchmark, --rag, --elo, --fix, --test

## UI/UX Component System (21st.dev Style)
New agents for generating UI components:
- `src/campaign_autopilot/agents/ui_hero_agent.py` — Hero sections
- `src/campaign_autopilot/agents/ui_pricing_agent.py` — Pricing tables
- `src/campaign_autopilot/agents/ui_faq_agent.py` — FAQ accordions
- `src/campaign_autopilot/agents/ui_testimonial_agent.py` — Testimonial cards
- `src/campaign_autopilot/agents/ui_full_page_agent.py` — Full page composer
- `src/campaign_autopilot/ui_component_registry.py` — 9 built-in components
- `src/campaign_autopilot/ui_design_memory.py` — SQLite tracking
- `workflows/ui_design_workflow.json` — 7-step DAG workflow

## Project Structure
See `docs/SISTEMA_COMPLETO.md` for full architecture documentation.

## Key Principles
- Stdlib first, zero external dependencies in core
- Thread-safe with threading.Lock
- SQLite WAL for persistence
- Brazilian Portuguese for docs, English for code
- API keys in .env only (NEVER commit)
- Ponytail: compact, lazy, senior-dev mode
