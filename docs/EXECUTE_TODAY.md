# 🚀 Execute Today — Guia Prático de Implantação

> Como colocar o Campaign Autopilot v5.2.1 em produção e começar a gerar receita em horas.

---

## Pré-requisitos

```bash
python3 --version  # 3.10+
git --version       # opcional
```

## Passo 1 — Configuração do Ambiente

```bash
cd /root/Documents/Codex/2026-05-30/New\ Project\ \(1\)

# Ambiente virtual
python3 -m venv .venv 2>/dev/null || virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
nano .env  # PELO MENOS: OPENROUTER_API_KEY
```

### Variáveis Obrigatórias

| Variável | Obrigatória? | Como obter |
|----------|-------------|------------|
| `OPENROUTER_API_KEY` | ✅ Sim | https://openrouter.ai/keys |
| `GROQ_API_KEY` | 🟡 Opcional (expirada) | https://console.groq.com/keys |
| `GEMINI_API_KEY` | 🟡 Opcional (inválida) | https://aistudio.google.com/apikey |
| IDs de Afiliado | 🔴 9 pendentes | docs/SETUP_HUMANO_COMPLETO.md |

## Passo 2 — Verificar que o Sistema Funciona

```bash
# Teste rápido
PYTHONPATH=src python3 -c "
import sys; sys.path.insert(0, 'src')
from campaign_autopilot.agents.base import CampaignContext
print('✅ Sistema carregado')
"

# Health check completo
PYTHONPATH=src python3 scripts/health_check.py

# Gerar catálogo de produtos
PYTHONPATH=src python3 scripts/enrich_products.py
```

## Passo 3 — Executar Ciclo de Receita

### Opção A: Árvore Paralela (13 fontes)
```bash
PYTHONPATH=src python3 scripts/money_loop.py --once
```

### Opção B: Pipeline Completa de Mídia
```bash
PYTHONPATH=src python3 scripts/run_full_pipeline.py --niche "tecnologia"
```

### Opção C: Gerar Landing Pages + Emails + Dashboards
```bash
PYTHONPATH=src python3 scripts/generate_site.py --all
```

## Passo 4 — Rodar 24/7

```bash
# Loop contínuo (intervalo padrão: 12h)
PYTHONPATH=src python3 scripts/money_loop.py --loop

# Em segundo plano com screen
screen -S autopilot
PYTHONPATH=src python3 scripts/money_loop.py --loop
# Ctrl+A, D para desanexar

# Seguir logs
PYTHONPATH=src python3 scripts/log_watcher.py
```

## Passo 5 — Projeções Financeiras

```bash
# Projeção rápida dos 5 cenários
PYTHONPATH=src python3 scripts/projetar_arvore_paralela.py

# Detalhamento por fonte
PYTHONPATH=src python3 scripts/projetar_arvore_paralela.py --detalhado

# Output JSON
PYTHONPATH=src python3 scripts/projetar_arvore_paralela.py --json
```

## Fluxo de 12h (Autopilot Completo)

```
Hora 0:  🔍 Competitor Analysis + SEO Scraper
Hora 1:  📝 Content Planner + Excellence Pipeline
Hora 2:  ✍️ Content Generator + Repurposer
Hora 3:  🎬 Media Pipeline (imagem, áudio, vídeo)
Hora 4:  🖌️ UI Design (landing pages, emails)
Hora 5:  ✅ Compliance Check
Hora 6:  📤 Publicação (WP + site)
Hora 7:  📢 Distribuição (YouTube, Email, Pinterest, Instagram, TikTok, Twitter)
Hora 8:  📊 Rank Tracker + Content Optimizer
Hora 9:  💰 Revenue Monitor + Analytics
Hora 10: 🔬 Meta-Orchestrator (auto-observação)
Hora 11: 🔧 Evolution Engine (auto-modificação)
Hora 12: 🧬 Third-Order (auto-transcendência)
```

## Segurança

```bash
# Verificar pre-push hook
git config core.hooksPath
# Deve retornar: .githooks

# Escanear secrets manualmente
bash scripts/scan_secrets.sh
```

## Troubleshooting

| Erro | Solução |
|------|---------|
| `No module named 'campaign_autopilot'` | Use `PYTHONPATH=src` antes do comando |
| APIs retornando dados simulados | Comportamento esperado sem chaves reais |
| Groq 403 / Gemini 400 | Chaves expiradas — renovar em console.groq.com / aistudio.google.com |

## Checklist de Execução

- [ ] Python 3.10+ instalado
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas
- [ ] .env configurado (OPENAI_API_KEY pelo menos)
- [ ] Health check passa (mesmo com ❌ parciais)
- [ ] Catálogo de produtos gerado
- [ ] Money loop executado com sucesso
- [ ] Projeção financeira gerada
- [ ] (Opcional) Dashboard rodando
- [ ] (Opcional) Deploy em VPS com screen/tmux

---

*Guia de execução — Campaign Autopilot v5.2.1 — Lyzer Labs*
