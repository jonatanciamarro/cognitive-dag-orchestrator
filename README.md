# Cognitive Workflow Orchestrator & Autonomous Multi-Agent Kernel

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat-square&logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-DAG%20Workflow%20Engine-informational.svg?style=flat-square)
![Scale](https://img.shields.io/badge/Scale-134%20Specialized%20Agents-orange.svg?style=flat-square)
![Workflows](https://img.shields.io/badge/Workflows-36%20Parallel%20DAGs-blueviolet.svg?style=flat-square)
![Storage](https://img.shields.io/badge/Storage-SQLite%20(WAL%20Tracing)-success.svg?style=flat-square&logo=sqlite&logoColor=white)
![UI](https://img.shields.io/badge/Telemetry-Streamlit%20Dashboard-red.svg?style=flat-square&logo=streamlit&logoColor=white)

Sistema operacional cognitivo e plataforma de orquestração autônoma de fluxos de trabalho distribuídos em larga escala. Com mais de **72.000 linhas de código** em Python, a arquitetura coordena **134 agentes autônomos especializados**, executando **36 fluxos paralelos baseados em Grafos Acíclicos Dirigidos (DAGs)** com persistência de alta concorrência em SQLite WAL e roteamento dinâmico entre múltiplos provedores de LLMs.

---

## 🏛️ Arquitetura do Sistema

```text
COGNITIVE WORKFLOW ORCHESTRATOR
│
├── 🧠 Executive Governance Layer
│   ├── Consistency & Factuality Guards
│   └── Architectural Enforcement
│
├── 🧬 Agent Runtime & Evolution Engine
│   ├── Agent Registry & Lifecycle Manager
│   ├── DAG Workflow Engine (ThreadPoolExecutor, Checkpoint & Resume)
│   ├── Tracing System com persistência SQLite WAL
│   ├── Multi-Model Router (6 provedores cognitivos com auto-failover)
│   ├── Memory Layer (Memória Semântica, Episódica e Procedural)
│   └── Quality Layers (Critic, Multi-Agent Debate, ELO Benchmark, RAG)
│
├── ⚙️ Parallel Execution Tree
│   ├── 36 Workflows concorrentes orientados a eventos
│   └── Execução resiliente desacoplada com tolerância a falhas
│
├── 🌐 Content & Data Syndication Pipeline
│   ├── Normalização e enriquecimento estruturado de dados
│   ├── Roteamento de distribuição para múltiplos endpoints REST/Webhooks
│   └── Mecanismo de auto-regeneração com feedback em loop fechado
│
└── 📊 Telemetria & Painel de Controle
    ├── Dashboard analítico em Streamlit com métricas cognitivas
    └── Monitoramento de latência, taxa de sucesso e consumo de tokens
```

---

## ⚙️ Principais Módulos de Engenharia

| Módulo | Escopo | Detalhes Técnicos |
|---|---|---|
| **DAG Workflow Engine** | Orquestração | 36 fluxos de trabalho com resolução topológica de dependências e `ThreadPoolExecutor`. |
| **Agent Runtime** | Execução | 134 agentes especializados com papéis determinísticos e ferramentas dedicadas. |
| **Multi-Model Router** | Resiliência de IA | Balanceamento de carga e *failover* automático entre 6 provedores de modelos de linguagem. |
| **SQLite WAL Tracing** | Concorrência | Rastreabilidade granular de eventos e checkpoints com *Write-Ahead Logging* para evitar locks. |
| **Quality & Self-Correction** | Governança | Avaliação de outputs em 7 etapas com limiar de qualidade e auto-regeneração em caso de desvio. |
| **Streamlit Telemetry** | Observabilidade | Visualização em tempo real de estados de execução, tempos de resposta e métricas de desempenho. |

---

## 🚀 Quick Start & Execução Local

### Pré-requisitos
- Python 3.11 ou superior
- Git

### Instalação
```powershell
# 1. Clonar repositório e preparar ambiente
git clone https://github.com/jonatanciamarro/campaign-autopilot.git
cd campaign-autopilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Configurar variáveis de ambiente
copy .env.example .env

# 3. Executar o dashboard de telemetria
streamlit run dashboard/app.py
```

---

## 🔒 Segurança e Práticas de Dados

- **Isolamento de Credenciais:** Variáveis sensíveis e tokens gerenciados estritamente via `.env` protegido por `.gitignore`.
- **Rastreabilidade Auditável:** Cada execução de agente é registrada com trace ID único para auditoria forense.
- **Armazenamento Local:** Dados de sessão e checkpoints mantidos em armazenamento transacional isolado.

---

## ⚖️ Licença
Distribuído sob licença proprietária de pesquisa e desenvolvimento — Jonatan Augusto Ciamarro.
