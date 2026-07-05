# 🚀 Quickstart — Campaign Autopilot v5.2.1

> De zero a workflow rodando em 5 minutos.

---

## Pré-requisitos

- Python 3.10+
- Git (opcional)
- ~10MB de disco

## Setup

```bash
# 1. Entrar no diretório
cd /root/Documents/Codex/2026-05-30/New\ Project\ \(1\)

# 2. Setup manual (recomendado)
python3 -m venv .venv 2>/dev/null || virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configurar ambiente
cp .env.example .env
nano .env  # preencher com pelo menos OPENROUTER_API_KEY

# 4. Criar diretórios de output
mkdir -p .state output/content output/images
```

## Verificar Instalação

```bash
# Saúde do sistema
PYTHONPATH=src python3 scripts/health_check.py

# Verificar CLI
PYTHONPATH=src python3 -m campaign_autopilot.cli --help

# Verificar providers de mídia
PYTHONPATH=src python3 -m campaign_autopilot.cli --providers

# Verificar agentes
PYTHONPATH=src python3 -c "
import sys; sys.path.insert(0, 'src')
from campaign_autopilot.agents.base import CampaignContext
print('✅ Sistema carregado com sucesso')
"
```

## Executar Workflows

```bash
# 1. Catálogo de produtos (160+)
PYTHONPATH=src python3 scripts/enrich_products.py

# 2. Ciclo único de receita
PYTHONPATH=src python3 scripts/money_loop.py --once

# 3. Árvore paralela de renda (13 fontes)
PYTHONPATH=src python3 scripts/projetar_arvore_paralela.py

# 4. Pipeline completa de mídia
PYTHONPATH=src python3 scripts/run_full_pipeline.py --niche "tecnologia"

# 5. Gerar landing page / email / dashboard
PYTHONPATH=src python3 scripts/generate_site.py --all
```

## Executar 24/7

```bash
# Loop contínuo (12h entre ciclos)
PYTHONPATH=src python3 scripts/money_loop.py --loop

# Seguir logs
PYTHONPATH=src python3 scripts/log_watcher.py

# Dashboard
streamlit run dashboard/app.py
```

## Arquitetura em Camadas

```
Layer 6 — AG-Kit Evolution Phases 11-19   (constraint, world model, economic, evolution, mesh, twin...)
Layer 5 — AG-Kit Evolution Phases 1-10    (trace_store, model_router, capability_registry, evaluation_engine)
Layer 4 — Provider Layer                   (14 LLM + 16 Media Providers)
Layer 3 — Agent Layer                      (122 agentes, DAG WorkflowRunner, 30 workflows)
Layer 2 — Cognitive Layer                  (SemanticMemory, Explanation, Synthesis, OutcomeStore)
Layer 1 — Governance Layer                 (MetaOrchestrator, EvolutionEngine, AgentFactory)
Layer 0 — Ponytail Plugin                  (lazy senior dev mode — YAGNI, stdlib first)
```

## Próximos Passos

1. 📖 Leia `docs/SETUP_HUMANO_COMPLETO.md` — guia de configuração manual
2. 💰 Leia `docs/PROJECOES_FINANCEIRAS.md` — projeções de receita
3. 🤖 Leia `docs/AGENTS_REFERENCE.md` — referência de 122 agentes
4. ⚡ Leia `docs/WORKFLOW_GUIDE.md` — guia de 30 workflows
5. 🔐 Verifique o pre-push hook: `git config core.hooksPath`

## Segurança

- 🔐 Pre-push hook ativo: `.githooks/pre-push` (bloqueia secrets)
- 🔐 `.env` no `.gitignore` (chaves nunca vazam)
- 🔐 Scanner manual: `bash scripts/scan_secrets.sh`

---

*Campaign Autopilot v5.2.1 — Lyzer Labs*
