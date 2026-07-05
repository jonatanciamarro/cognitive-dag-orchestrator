# 🧬 AG-Kit Evolution Program

> **Campaign Autopilot v5.2.1** — Fases 1-10 documentadas | Fases 11-19 em `AG_KIT_EVOLUTION_PHASE_11_20.md`

> Campaign Autopilot como plataforma agentic de nova geração — incorporando padrões de LangGraph, OpenAI Agents SDK, CrewAI e Microsoft Agent Framework.

## Princípio

**Adotar capacidades, não frameworks.** AG-Kit, LangGraph, OpenAI Agents SDK, CrewAI e Microsoft Agent Framework são arquiteturas de referência, não dependências de runtime.

## Capacidades Implementadas

### Fase 1 — Agent Runtime Layer ✅
- `AgentBase` com descoberta dinâmica
- `AgentFactory` para criação autônoma de agentes
- Registro automático em `__init__.py` e orchestrator

### Fase 2 — Durable Workflow Engine ✅
- `WorkflowRunner` com DAG checkpointing
- Persistência SQLite WAL
- Suporte a dry-run e execução parcial
- ThreadPoolExecutor para paralelismo

### Fase 3 — Agent Tracing System ✅
Arquivo: `src/campaign_autopilot/trace_store.py` (548 linhas)

- `AgentTraceStore` — SQLite WAL para persistência de traces
- `TraceRecorder` — gravação automática de inputs, outputs, tool/model calls
- `TraceViewer` — consulta de traces por agente, sessão, status
- Métricas: duração, custo, erros por execução

### Fase 4 — MCP Layer ✅
Arquivo: `src/campaign_autopilot/capability_registry.py` (314 linhas)

- `MCPClient` — cliente para servidores MCP locais e remotos
- `MCPRegistry` — descoberta e registro de ferramentas MCP
- `MCPToolAdapter` — adaptação de ferramentas MCP para agentes
- `CapabilityRegistry` — prevenção de agentes duplicados

### Fase 5 — Multi-Model Router ✅
Arquivo: `src/campaign_autopilot/model_router.py` (286 linhas)

- `ModelRouter` — roteamento inteligente entre providers
- `RoutingPolicy` — políticas de roteamento (custo, qualidade, latência)
- `CostPolicy` — orçamento por provider/modelo
- `FallbackPolicy` — fallback automático em cadeia
- Providers: OpenAI, Anthropic, Google, Groq, OpenRouter, Ollama

### Fase 6 — Agent Memory Upgrade ✅
- `MemoryStore` — SQLite WAL
- `SemanticMemoryStore` — grafo de conhecimento
- Memória episódica, procedural, semântica e de trabalho
- Consolidação automática entre ciclos

### Fase 7 — Evaluation Layer ✅
Arquivo: `src/campaign_autopilot/evaluation_engine.py` (210 linhas)

- `EvaluationEngine` — benchmark de agentes
- `BenchmarkRunner` — execução de benchmarks
- `AgentScorecard` — métricas por agente (acurácia, custo, latência, confiabilidade)

### Fase 8 — Agent Marketplace ✅
- `CapabilityRegistry` — declaração de capacidades por agente
- Prevenção de agentes duplicados via capability map
- Declaração obrigatória: capacidades, dependências, inputs, outputs, owner

### Fase 9 — Autonomous Optimization ✅
- `MetaOrchestrator` — orquestrador de segunda ordem
- `EvolutionEngine` — mutação de workflows, scoring, rollback
- Detecção de regressão de performance

### Fase 10 — Governance Layer ✅
- `GovernanceAgent` — 7 delegates de governança em um único agente
- `PolicyEngine` — políticas de compliance
- `ADRStore` — registro de decisões arquiteturais

## Comparação com AG-Kit

| Capacidade | AG-Kit | Campaign Autopilot |
|-----------|--------|-------------------|
| Agent Runtime | ✅ | ✅ (AgentBase + AgentFactory) |
| Workflow DAG | ✅ | ✅ (WorkflowRunner + Checkpoint) |
| Agent Tracing | ✅ | ✅ (TraceStore + TraceViewer) |
| MCP Integration | ✅ | ✅ (MCPClient + MCPRegistry) |
| Multi-Model Router | ✅ | ✅ (ModelRouter + Fallback) |
| Agent Memory | ✅ | ✅ (3 tipos de memória) |
| Evaluation | ✅ | ✅ (EvaluationEngine) |
| Marketplace | ✅ | ✅ (CapabilityRegistry) |
| Autonomous Evolution | ✅ | ✅ (EvolutionEngine) |
| Governance | ✅ | ✅ (GovernanceAgent) |
| Zero Dep Core | — | ✅ (stdlib-only core) |
| Ponytail Mode | — | ✅ (YAGNI enforcement) |

## Arquivos do Programa

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `src/campaign_autopilot/trace_store.py` | 548 | Tracing e observabilidade |
| `src/campaign_autopilot/workflow_checkpoint.py` | 453 | Checkpoint e recovery de workflows |
| `src/campaign_autopilot/model_router.py` | 286 | Roteamento multi-modelo |
| `src/campaign_autopilot/capability_registry.py` | 314 | Registro de capacidades e MCP |
| `src/campaign_autopilot/evaluation_engine.py` | 210 | Benchmark e scorecard |
| `src/campaign_autopilot/agents/governance_agent.py` | ~160 | Governance agent consolidado |
| `src/campaign_autopilot/agents/evolution_engine.py` | — | Mutação e evolução |
| `src/campaign_autopilot/agents/agent_factory.py` | ~490 | Fábrica autônoma de agentes | |
| `src/campaign_autopilot/constraint_intelligence.py` | 469 | ConstraintGraph, ConstraintAwareWorkflow (F11) |

---

| Governance | ✅ (GovernanceAgent + ConstraintGraph F11) |

## Next: Phases 11-20

The AG-Kit Evolution continues beyond Phase 10. See the full roadmap:

📄 [AG_KIT_EVOLUTION_PHASE_11_20.md](AG_KIT_EVOLUTION_PHASE_11_20.md)

| Phase | Component | Status |
|-------|-----------|--------|
| 11 | Constraint Intelligence Layer | ✅ **IMPLEMENTED** |
| 12 | World Model Engine | ✅ **IMPLEMENTED** |
| 13 | Economic Intelligence Layer | ✅ **IMPLEMENTED** |
| 14 | Agent Evolution Engine | ✅ **IMPLEMENTED** |
| 15 | Cognitive Mesh | ✅ **IMPLEMENTED** |
| 16 | Digital Twin Layer | ✅ **IMPLEMENTED** |
| 17 | Self-Improvement Engine | ✅ **IMPLEMENTED** |
| 18 | Constraint Genealogy Engine | ✅ **IMPLEMENTED** |
| 19 | Organization-as-Agent | ✅ **IMPLEMENTED** |
| 20 | Autonomous Enterprise Kernel | 🌌 Vision (F19 complete) |

---

*Parte da documentação do Campaign Autopilot v5.2.0 — Atualizado em 2026-06-24.*
