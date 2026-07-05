# Campaign Autopilot — Documentação Completa de Arquitetura

> Documento gerado automaticamente. Inventário completo de todos os artefatos do projeto.
> Versão atual: **v5.0.0** — 279 testes passando, 24 módulos, 5291 linhas de código

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura em Camadas](#arquitetura-em-camadas)
- [Workflow Engine](#workflow-engine)
- [Workflows Disponíveis](#workflows-disponíveis)
- [Agentes](#agentes)
- [Cognitive Stores](#cognitive-stores)
- [Meta-Cognitive Layer](#meta-cognitive-layer)
- [Módulo de Afiliados](#módulo-de-afiliados)
- [CLI e Interface](#cli-e-interface)
- [Testes](#testes)
- [Snapshots (free/)](#snapshots-free)
- [Configs e Workflows Detalhado](#configs-e-workflows--detalhado)
- [Inventário Completo de Arquivos](#inventário-completo-de-arquivos)

---
## Visão Geral

**Campaign Autopilot** é um sistema de otimização de campanhas de marketing com arquitetura cognitiva,
execução multi-agente paralela, e suporte a marketing de afiliados 100% orgânico (sem tráfego pago).

O sistema opera em 5 camadas:

1. **CLI** — interface de linha de comando (argparse)
2. **Workflow Engine** — executor DAG com paralelismo via ThreadPoolExecutor
3. **Agentes** — 9 especialistas que processam o contexto da campanha
4. **Cognitive Stores** — memória semântica, explicações, feedback, síntese
5. **Meta-Cognitive Layer** — classificação epistêmica, detecção de drift, registro de metas

### Estatísticas do Projeto

- **Módulos Python (src/)**: 24 arquivos, 5291 linhas
- **Testes (tests/)**: 22 arquivos, 3112 linhas
- **Workflows**: 3 definições DAG
- **Configs**: 3 perfis de configuração
- **Exemplos**: 8 payloads JSON/MD
- **Skills Docs**: 9 documentos de agente
- **Snapshots congelados**: 4 versões (v1.0.0 a v2.0.0)
- **Total de testes**: 279 (todos passando)

---
## Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────┐
│               META-COGNITIVE LAYER                   │
│  EpistemicMonitor | OntologySteward | GoalRegistry   │
├─────────────────────────────────────────────────────┤
│              KNOWLEDGE SYNTHESIS                      │
│  KnowledgeSynthesisEngine (patterns, trends, decay)   │
├─────────────────────────────────────────────────────┤
│              COGNITIVE STORES                         │
│  SemanticMemoryStore | ExplanationStore | Outcome     │
├─────────────────────────────────────────────────────┤
│              WORKFLOW ENGINE                          │
│  WorkflowRunner (DAG scheduler, ThreadPoolExecutor)   │
├─────────────────────────────────────────────────────┤
│              AGENT LAYER                              │
│  9 especialistas: analytics, compliance, seo, etc.    │
├─────────────────────────────────────────────────────┤
│              PERSISTENCE                              │
│  MemoryStore (SQLite WAL) | OfferManager (SQLite)     │
├─────────────────────────────────────────────────────┤
│              CLI INTERFACE                            │
│  campaign-autopilot (argparse, --events | --workflow) │
└─────────────────────────────────────────────────────┘
```

---
## Workflow Engine

Arquivo: `src/campaign_autopilot/workflow.py`

O **WorkflowRunner** é o motor de execução. Ele recebe um `WorkflowSpec` (definição DAG em JSON),
um `CampaignContext` (dados de entrada), e um `registry` (mapeamento nome → agente).

### Componentes

| Classe | Função |
|--------|--------|
| `WorkflowSpec` | Definição do workflow (nome, max_workers, steps) |
| `WorkflowStepSpec` | Definição de um step (id, agent, depends_on) |
| `WorkflowRunner` | Executor do DAG com ThreadPoolExecutor |
| `StepResult` | Resultado de um step (status, output, error, trace) |
| `WorkflowRunResult` | Resultado completo (trace, erros, outputs) |
| `ExecutionPlan` | Plano de ação serializável (actions, risks) |
| `ExecutionAction` | Ação individual no plano |

### Regras de Execução

1. Steps sem `depends_on` rodam em paralelo na inicialização
2. Steps só iniciam quando **todas** as dependências foram concluídas
3. Se um step falha, o workflow continua (erro registrado no trace)
4. O output final do workflow é o output do **último step**
5. `_resolve_agent()` faz lookup no registry (nome → instância AgentBase ou callable)
6. Agentes não encontrados → StepResult status=failed com erro descritivo

### Formato do WorkflowSpec (JSON)

```json
{
  "name": "meu_workflow",
  "description": "...",
  "max_workers": 4,
  "steps": [
    {"id": "step1", "agent": "agente_x", "depends_on": [], "description": "..."},
    {"id": "step2", "agent": "agente_y", "depends_on": ["step1"], "description": "..."}
  ]
}
```

---
## Workflows Disponíveis

| Workflow | Steps | Descrição |
|----------|-------|-----------|
| `campaign_cycle.json` | 5 | Parallel analytics/compliance/memory lookups followed by optimization and execution planning. |
| | Steps: | `analytics`, `compliance`, `memory_lookup`, `optimization`, `execution_planning` |
| `organic_affiliate_cycle.json` | 6 | Ciclo completo de marketing de afiliados orgânico: pesquisa SEO → ofertas → conteúdo → compliance → publicação. |
| | Steps: | `seo_research`, `compliance`, `memory_lookup`, `offer_lookup`, `content_planner`, `publisher` |
| `organic_cycle.json` | 5 | Free organic acquisition workflow with parallel research and content planning. |
| | Steps: | `research`, `compliance`, `memory_lookup`, `optimization`, `execution_planning` |

---
## Agentes

Todos os agentes herdam de `AgentBase` (`src/campaign_autopilot/agents/base.py`) e implementam:

```python
class MeuAgente(AgentBase):
    def __init__(self, **kwargs):
        super().__init__('meu_agente', **kwargs)
    def run(self, context: CampaignContext) -> AgentResult:
        # Lógica aqui
        return AgentResult(agent=self.name, status='success', output=output, trace=trace)
```

### Interface AgentBase

| Método/Atributo | Descrição |
|-----------------|-----------|
| `name` | Nome do agente (usado no registry) |
| `semantic_memory` | Referência opcional ao SemanticMemoryStore |
| `explanation_store` | Referência opcional ao ExplanationStore |
| `run(context)` | Método principal — recebe CampaignContext, retorna AgentResult |

### AgentResult

| Campo | Descrição |
|-------|-----------|
| `agent` | Nome do agente |
| `status` | 'success' ou 'failed' |
| `output` | Dados produzidos (dict) |
| `trace` | AgentTrace com metadados de execução |
| `warnings` | Lista de avisos |

### Tabela de Agentes

| Nome | Arquivo | Step IDs | Função Principal |
|------|---------|----------|-----------------|
| **AnalyticsAgent** | `analytics.py` | `analytics`, `research` | Análise de performance: CPA, CTR, tendências, oportunidades. Extrai conhecimento semântico. |
| **ComplianceAgent** | `compliance.py` | `compliance` | Valida conteúdo contra política, termos restritos, disclosures obrigatórias. |
| **MemoryLookupAgent** | `memory_agent.py` | `memory_lookup` | Busca padrões históricos em campanhas anteriores por token matching. |
| **OptimizationAgent** | `optimization.py` | `optimization` | Sintetiza ações de otimização dos agentes upstream. Consulta memória semântica. |
| **ExecutionPlanningAgent** | `orchestrator.py` | `execution_planning` | Converte recomendação em ExecutionPlan serializável com ações e riscos. |
| **SEOResearchAgent** | `seo_research.py` | `seo_research` | Pesquisa palavras-chave com volume de busca e dificuldade. Gera oportunidades. |
| **OfferLookupAgent** | `offer_lookup.py` | `offer_lookup` | Busca ofertas de afiliados compatíveis com o nicho por score de match. |
| **ContentPlannerAgent** | `content_planner.py` | `content_planner` | Combina keywords + ofertas em briefings de conteúdo com outline. |
| **PublisherAgent** | `publisher.py` | `publisher` | Cria cronograma de publicação e estima cliques orgânicos. |
| **CampaignOrchestrator** | `orchestrator.py` | `orchestrator` | Coordena workflow, cognitive stores, observers, metas e detecção de drift. |

### Registro de Agentes no Orchestrator

O `CampaignOrchestrator.__init__()` constrói o dicionário `self.registry` mapeando nomes
para instâncias. Cada agente recebe referências opcionais para:

- `semantic_memory`: SemanticMemoryStore (para extrair/consultar conhecimento)
- `explanation_store`: ExplanationStore (para registrar decisões e regras)

Para adicionar um novo agente, basta:
1. Criar a classe do agente em `agents/`
2. Importar e instanciar no `registry` do orchestrator
3. Referenciar pelo nome no workflow JSON

### Observers

Cada agente é registrado como **observer** no SemanticMemoryStore na primeira execução
do ciclo (`_ensure_observers_registered()`). Isso permite rastrear qual agente produziu
cada claim de conhecimento.

Observers registrados:
`analytics`, `compliance`, `memory_lookup`, `optimization`, `execution_planning`,
`seo_research`, `offer_lookup`, `content_planner`, `publisher`, `ontology_steward`, `orchestrator`.

---
## Cognitive Stores

Quando um `MemoryStore` (SQLite) é passado para o `CampaignOrchestrator`, 4 camadas
cognitivas são inicializadas automaticamente.

### 1. SemanticMemoryStore (`src/campaign_autopilot/semantic_memory.py`)

Grafo de conhecimento persistente. Principais capacidades:

| Operação | Descrição |
|----------|-----------|
| `register_concept(name, namespace)` | Registra um conceito (idempotente) |
| `assert_claim(subj, pred, obj, conf, ...)` | Cria relação entre conceitos com status epistêmico |
| `query_claims(...)` | Busca claims com filtros (status, peso, namespace) |
| `get_claim(id)` | Retorna claim com epistemic_weight computado |
| `reinforce_claim(id, evidence)` | Aumenta confiança e adiciona evidência |
| `decay_confidence(rates_by_status)` | Decaimento seletivo por status epistêmico |
| `register_observer(id, type, reliability)` | Registra um produtor de conhecimento |
| `snapshot_ontology(version_id)` | Captura estado atual do grafo |
| `diff_ontology(vA, vB)` | Compara snapshots e mede drift semântico |
| `extract_cycle_knowledge(...)` | Extrai claims de métricas de campanha |

**Epistemic Status:**
- `VERIFIED` (peso 1.0) — Observação direta
- `INFERRED` (peso 0.8) — Inferência estatística
- `ASSUMED` (peso 0.5) — Entrada explícita sem validação
- `HYPOTHETICAL` (peso 0.3) — Hipótese não testada

### 2. ExplanationStore (`src/campaign_autopilot/explanation.py`)

Registro completo de decisões com proveniência:

- `record_decision()`: cria DecisionPoint com input_state
- `record_rule_application()`: registra regra aplicada e resultado
- `record_counterfactual()`: simula "e se X fosse Y?"
- `update_decision_output()`: registra a decisão final
- `render_explanation()`: gera explicação legível para operator/compliance/CTO
- `render_provenance_chain()`: cadeia completa de decisões (árvore)

### 3. OutcomeStore (`src/campaign_autopilot/feedback.py`)

Loop de feedback entre ciclos:
- `record_expected()`: registra resultado esperado do ExecutionPlan
- `record_actual()`: registra resultado real, calcula delta
- `feed_lessons_to_semantic_memory()`: extrai lições do delta e alimenta o grafo

### 4. KnowledgeSynthesisEngine (`src/campaign_autopilot/synthesis.py`)

Síntese entre ciclos:
- `find_reinforcing_patterns()`: claims que se repetem em múltiplos ciclos
- `find_conflicting_patterns()`: claims contraditórios sobre mesmo sujeito
- `find_trending_insights()`: confiança aumentando ao longo do tempo
- `synthesize()`: produz meta-claims sobre padrões encontrados
- `run_decay_cycle()`: decaimento programado

---
## Meta-Cognitive Layer

Adicionada na v1.3.0. Opera acima dos agentes e cognitive stores.

### EpistemicMonitor (embutido no SemanticMemoryStore)

- `assert_claim()` exige `epistemic_status` válido (padrão: INFERRED)
- `epistemic_weight()` = confidence × status_multiplier
- `query_claims()` filtra por `epistemic_status` e `min_epistemic_weight`

### OntologySteward (embutido no SemanticMemoryStore)

- `diff_ontology(version_a, version_b)`: compara dois snapshots de ontologia
- Retorna: concepts_added, concepts_removed, concepts_modified, drift_score, semantic_risk
- `_check_ontology_drift()` no orchestrator: executa diff automático entre últimos 2 snapshots
- Drift alto (HIGH/MEDIUM) registrado como claim semântico de alerta

### GoalRegistry (`src/campaign_autopilot/goals.py`)

- Metas persistentes: objective, owner, success_criteria, achieved
- `evaluate_goal()`: compara measured_value vs target_value
- `evaluate_from_outcome()`: avalia metas ativas contra dados de outcome
- Suporte a métricas inversas (CPA, CPC — menor é melhor)
- Histórico de avaliações vinculado a cycle_id

---
## Módulo de Afiliados

Adicionado na v2.0.0. Arquivo: `src/campaign_autopilot/affiliate.py`

### Modelos de Dados

| Modelo | Campos Principais |
|--------|------------------|
| `AffiliateOffer` | offer_id, network, product_name, product_url, commission_type/value, category, tags, cookie_days |
| `AffiliateLink` | link_id, offer_id, base_url, tracked_url, source, content_id, clicks, conversions, revenue |
| `ContentBrief` | brief_id, topic, keyword, content_type, offers, outline, estimated_volume, difficulty, status |

### Redes de Afiliados Suportadas

| Classe | Rede | Parâmetro de Tracking |
|--------|------|----------------------|
| `AmazonAssociates` | Amazon Associates | `tag=TRACKING_ID` |
| `Hotmart` | Hotmart | `aff=AFFILIATE_ID` |
| `GenericAffiliate` | Qualquer rede | Configurável (`ref=ID`) |

### OfferManager

Gerencia o catálogo de ofertas e links em SQLite:

| Método | Descrição |
|--------|-----------|
| `register_offer(offer)` | Registra oferta (idempotente) |
| `get_offer(offer_id)` | Busca oferta por ID |
| `list_offers(network, category, active_only)` | Lista ofertas com filtros |
| `create_link(offer, network, source, ...)` | Cria link rastreado |
| `track_click(link_id)` | Registra clique |
| `track_conversion(link_id, revenue)` | Registra conversão |
| `save_brief(brief)` | Persiste briefing de conteúdo |
| `list_briefs(status)` | Lista briefings |
| `get_affiliate_metrics()` | Métricas agregadas (clicks, revenue, CR) |

### Workflow de Afiliados

O workflow `organic_affiliate_cycle.json` executa 6 steps:

```
seo_research ─┬─> offer_lookup ─┐
compliance ───┤                ├─> content_planner ─> publisher
memory_lookup ─┘               ┘
```

1. **seo_research** (paralelo): pesquisa keywords, volume, dificuldade, intent
2. **compliance** (paralelo): valida disclosures e termos restritos
3. **memory_lookup** (paralelo): busca lições de ciclos anteriores
4. **offer_lookup** (após SEO): encontra ofertas compatíveis por score de match
5. **content_planner** (após SEO+Offers+Memory): gera briefings com outline e ofertas
6. **publisher** (após Content+Compliance): cronograma de publicação + estimativas

---
## CLI e Interface

Arquivo: `src/campaign_autopilot/cli.py`

### Comandos

```bash
# Modo CPA (legado)
campaign-autopilot --events examples/campaign_events.json --db .state/db.sqlite3

# Modo multi-agente (workflow principal)
campaign-autopilot --workflow workflows/organic_affiliate_cycle.json \
  --context examples/affiliate_context.json --db .state/db.sqlite3

# Modo orgânico
campaign-autopilot --workflow workflows/organic_cycle.json \
  --context examples/organic_context.json --db .state/db.sqlite3
```

### Argumentos

| Argumento | Descrição | Padrão |
|-----------|-----------|--------|
| `--events` | Arquivo JSON de eventos (modo CPA) | — |
| `--workflow` | Arquivo JSON de workflow (modo multi-agente) | — |
| `--context` | Contexto do workflow (obrigatório com --workflow) | — |
| `--db` | Caminho do banco SQLite | campaign_autopilot.sqlite3 |

### Fluxo de Dados

```
main()
  ├─ --events: run_cycle()
  │    → _load_input() (JSON → Campaign + Events + Policy)
  │    → MemoryStore.upsert_campaign() + record_events()
  │    → calculate_metrics()
  │    → PolicyEngine.evaluate()
  │    → DecisionPlan.to_dict() → JSON stdout
  │
  └─ --workflow: run_workflow()
       → _load_context() (JSON → CampaignContext)
       → MemoryStore (abre/fecha)
       → CampaignOrchestrator.run()
            → WorkflowRunner.run() (DAG executor)
            → Cognitive Stores (semantic, explanation, outcome)
            → Meta-Cognitive (observers, goals, drift)
       → AgentResult.to_dict() → JSON stdout
```

---
## Testes

Total: **194 testes** em 22 arquivos, todos passando.

| Arquivo | Linhas | Cobertura |
|---------|--------|-----------|
| `__init__.py` | 10 |  |
| `test_affiliate.py` | 203 | OfferManager, AffiliateLink, redes, métricas, ContentBrief |
| `test_affiliate_integration.py` | 94 | Workflow afiliados + OfferManager + cognitive stores |
| `test_campaign_integration.py` | 104 | Ciclo CPA + memory stores + compliance block |
| `test_cli.py` | 198 | CLI parsing, run_cycle, run_workflow, input validation, load_context |
| `test_cli_subprocess.py` | 68 | CLI como subprocesso (full stack, ambas as rotas) |
| `test_epistemic.py` | 308 | EpistemicWeight, status, observers, ontology diff, decay rates |
| `test_feedback.py` | 194 | OutcomeStore (expected/actual/delta), OntologySnapshot |
| `test_free_variant.py` | 43 | Snapshots free/ (existência, versão correta) |
| `test_goals.py` | 129 | GoalRegistry, evaluate, auto-evaluation from outcome |
| `test_memory.py` | 137 | MemoryStore CRUD, upsert, list, context manager, stable_event_id |
| `test_meta_cognitive.py` | 163 | Observers, epistemic claims, goals, ontology versions |
| `test_metrics.py` | 45 | calculate_metrics, anomaly flags |
| `test_models.py` | 237 | Campaign, Event, Metrics, Decision, Policy (serialização) |
| `test_orchestrator.py` | 37 | CampaignOrchestrator + workflow campaign_cycle |
| `test_organic_cycle.py` | 57 | Artefatos do ciclo orgânico (arquivos + consistência) |
| `test_organic_integration.py` | 100 | Workflow orgânico + memory stores |
| `test_policy.py` | 51 | PolicyEngine (opt-in, compliance, scale, pause) |
| `test_semantic_memory.py` | 416 | SemanticMemoryStore + ExplanationStore (31 testes) |
| `test_synthesis.py` | 184 | KnowledgeSynthesisEngine (patterns, conflicts, decay) |
| `test_workflow.py` | 104 | Workflow sintético (execute_workflow local) |
| `test_workflow_runner.py` | 230 | WorkflowRunner real (DAG, erros, callables, parallel) |

---
## Snapshots (free/)

O diretório `free/` contém snapshots congelados do projeto em versões específicas.
Cada snapshot é uma cópia completa e read-only do projeto naquele ponto no tempo.

| Snapshot | Descrição |
|----------|-----------|
| `v1.0.0` | CPA campaign autopilot baseline (3 agents, policy engine, metrics) |
| `v1.1.0` | Organic acquisition variant (content, SEO, community, opt-in capture) |
| `v1.2.0` | Cognitive memory stores, explanation provenance, outcome feedback, synthesis |
| `v1.3.0` | Epistemic-aware reasoning, selective decay, ontology drift detection, goals |
| `v2.0.0` | Organic affiliate marketing autopilot (SEO, offers, content planning, publishing) |

### Regras dos Snapshots

1. Snapshots são **read-only** uma vez publicados
2. O projeto principal fica na raiz; snapshots em `free/`
3. Novo snapshot = novo diretório versionado (ex: `free/v2.1.0/`)
4. `free/VERSION.json` sempre aponta para o snapshot mais recente
5. Comparação entre snapshots mostra evolução do projeto

---
## Skills Docs

O diretório `skills/` contém documentação markdown para cada agente.
Estes arquivos funcionam como **skill notes** — instruções sobre como cada agente opera,
quais são suas entradas, saídas, regras e observações.

- `analytics.md`: _Analytics Agent_
- `compliance.md`: _Compliance Agent_
- `content_planner.md`: _ContentPlannerAgent_
- `memory.md`: _Memory Agent_
- `offer_lookup.md`: _OfferLookupAgent_
- `optimization.md`: _Optimization Agent_
- `orchestrator.md`: _Orchestrator Agent_
- `publisher.md`: _PublisherAgent_
- `seo_research.md`: _SEOResearchAgent_

---
## Configs e Workflows — Detalhado

### Arquivos de Configuração (configs/)

Cada config define o comportamento de um ciclo:
- `mode`: tipo de ciclo (organic_only, cpa)
- `defaults`: configurações padrão (dry_run, require_approval, record_memory)
- `policy`: regras de compliance (opt-in, consent, no_paid_media, disclosures)
- `metrics`: thresholds (sample_size, lead_rate, ctr, cpa)
- `workflow.states`: máquina de estados do ciclo
- `channels`: canais disponíveis para distribuição

- **`opt_in_cycle.json`**: Campaign optimization cycle that only runs for explicit opt-in traffic.
  - no_paid_media: False, disclosures: []
- **`organic_affiliate_cycle.json`**: Ciclo de marketing de afiliados 100% orgânico — pesquisa SEO, ofertas, conteúdo, publicação.
  - no_paid_media: True, disclosures: ['disclosure_afiliado']
- **`organic_cycle.json`**: Local-only organic acquisition loop for opt-in growth.
  - no_paid_media: True, disclosures: []

### Workflows (workflows/)

#### `campaign_cycle.json`
_Parallel analytics/compliance/memory lookups followed by optimization and execution planning._

| Step | Agente | Dependências |
|------|--------|-------------|
| `analytics` | `analytics` | (início) |
| `compliance` | `compliance` | (início) |
| `memory_lookup` | `memory_lookup` | (início) |
| `optimization` | `optimization` | analytics, compliance, memory_lookup |
| `execution_planning` | `execution_planning` | optimization |

#### `organic_affiliate_cycle.json`
_Ciclo completo de marketing de afiliados orgânico: pesquisa SEO → ofertas → conteúdo → compliance → publicação._

| Step | Agente | Dependências |
|------|--------|-------------|
| `seo_research` | `seo_research` | (início) |
| `compliance` | `compliance` | (início) |
| `memory_lookup` | `memory_lookup` | (início) |
| `offer_lookup` | `offer_lookup` | seo_research |
| `content_planner` | `content_planner` | seo_research, offer_lookup, memory_lookup |
| `publisher` | `publisher` | content_planner, compliance |

#### `organic_cycle.json`
_Free organic acquisition workflow with parallel research and content planning._

| Step | Agente | Dependências |
|------|--------|-------------|
| `research` | `analytics` | (início) |
| `compliance` | `compliance` | (início) |
| `memory_lookup` | `memory_lookup` | (início) |
| `optimization` | `optimization` | research, compliance, memory_lookup |
| `execution_planning` | `execution_planning` | optimization |

---
## Inventário Completo de Arquivos

### Módulos Core (src/campaign_autopilot/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `src/campaign_autopilot/__init__.py` | 47 | `"""Campaign Autopilot package."""` |
| `src/campaign_autopilot/affiliate.py` | 427 | `"""Módulo de afiliados — gestão de ofertas, links, tracking e redes."""` |
| `src/campaign_autopilot/agents/__init__.py` | 16 | `from .base import AgentBase, AgentResult, AgentTrace, CampaignContext` |
| `src/campaign_autopilot/agents/analytics.py` | 162 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/base.py` | 148 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/compliance.py` | 145 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/content_planner.py` | 179 | `"""Agente de Planejamento de Conteúdo — combina pesquisa SEO com ofertas de afiliados."""` |
| `src/campaign_autopilot/agents/memory_agent.py` | 133 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/offer_lookup.py` | 125 | `"""Agente de Busca de Ofertas — encontra ofertas de afiliados para o nicho."""` |
| `src/campaign_autopilot/agents/optimization.py` | 164 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/orchestrator.py` | 278 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/publisher.py` | 103 | `"""Agente de Publicação — planeja cronograma, sugere canais e formata conteúdo."""` |
| `src/campaign_autopilot/agents/seo_research.py` | 178 | `"""Agente de pesquisa SEO — palavras-chave, tópicos, volume, dificuldade."""` |
| `src/campaign_autopilot/cli.py` | 193 | `from __future__ import annotations` |
| `src/campaign_autopilot/explanation.py` | 511 | `from __future__ import annotations` |
| `src/campaign_autopilot/feedback.py` | 245 | `from __future__ import annotations` |
| `src/campaign_autopilot/goals.py` | 252 | `from __future__ import annotations` |
| `src/campaign_autopilot/memory.py` | 139 | `from __future__ import annotations` |
| `src/campaign_autopilot/metrics.py` | 82 | `from __future__ import annotations` |
| `src/campaign_autopilot/models.py` | 147 | `from __future__ import annotations` |
| `src/campaign_autopilot/policy.py` | 155 | `from __future__ import annotations` |
| `src/campaign_autopilot/semantic_memory.py` | 802 | `from __future__ import annotations` |
| `src/campaign_autopilot/synthesis.py` | 310 | `from __future__ import annotations` |
| `src/campaign_autopilot/workflow.py` | 350 | `from __future__ import annotations` |

**Total: 24 arquivos, 5291 linhas**

### Agentes (src/campaign_autopilot/agents/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `src/campaign_autopilot/agents/__init__.py` | 16 | `from .base import AgentBase, AgentResult, AgentTrace, CampaignContext` |
| `src/campaign_autopilot/agents/analytics.py` | 162 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/base.py` | 148 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/compliance.py` | 145 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/content_planner.py` | 179 | `"""Agente de Planejamento de Conteúdo — combina pesquisa SEO com ofertas de afiliados."""` |
| `src/campaign_autopilot/agents/memory_agent.py` | 133 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/offer_lookup.py` | 125 | `"""Agente de Busca de Ofertas — encontra ofertas de afiliados para o nicho."""` |
| `src/campaign_autopilot/agents/optimization.py` | 164 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/orchestrator.py` | 278 | `from __future__ import annotations` |
| `src/campaign_autopilot/agents/publisher.py` | 103 | `"""Agente de Publicação — planeja cronograma, sugere canais e formata conteúdo."""` |
| `src/campaign_autopilot/agents/seo_research.py` | 178 | `"""Agente de pesquisa SEO — palavras-chave, tópicos, volume, dificuldade."""` |


### Testes (tests/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `tests/__init__.py` | 10 | `from __future__ import annotations` |
| `tests/test_affiliate.py` | 203 | `from __future__ import annotations` |
| `tests/test_affiliate_integration.py` | 94 | `from __future__ import annotations` |
| `tests/test_campaign_integration.py` | 104 | `from __future__ import annotations` |
| `tests/test_cli.py` | 198 | `from __future__ import annotations` |
| `tests/test_cli_subprocess.py` | 68 | `from __future__ import annotations` |
| `tests/test_epistemic.py` | 308 | `from __future__ import annotations` |
| `tests/test_feedback.py` | 194 | `from __future__ import annotations` |
| `tests/test_free_variant.py` | 43 | `from __future__ import annotations` |
| `tests/test_goals.py` | 129 | `from __future__ import annotations` |
| `tests/test_memory.py` | 137 | `from __future__ import annotations` |
| `tests/test_meta_cognitive.py` | 163 | `from __future__ import annotations` |
| `tests/test_metrics.py` | 45 | `import json` |
| `tests/test_models.py` | 237 | `from __future__ import annotations` |
| `tests/test_orchestrator.py` | 37 | `from __future__ import annotations` |
| `tests/test_organic_cycle.py` | 57 | `from __future__ import annotations` |
| `tests/test_organic_integration.py` | 100 | `from __future__ import annotations` |
| `tests/test_policy.py` | 51 | `import json` |
| `tests/test_semantic_memory.py` | 416 | `from __future__ import annotations` |
| `tests/test_synthesis.py` | 184 | `from __future__ import annotations` |
| `tests/test_workflow.py` | 104 | `import json` |
| `tests/test_workflow_runner.py` | 230 | `from __future__ import annotations` |

**Total: 22 arquivos, 3112 linhas**

### Workflows (workflows/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `workflows/campaign_cycle.json` | 44 | `{` |
| `workflows/organic_affiliate_cycle.json` | 43 | `{` |
| `workflows/organic_cycle.json` | 43 | `{` |


### Configs (configs/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `configs/opt_in_cycle.json` | 50 | `{` |
| `configs/organic_affiliate_cycle.json` | 35 | `{` |
| `configs/organic_cycle.json` | 49 | `{` |


### Exemplos (examples/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `examples/affiliate_context.json` | 36 | `{` |
| `examples/campaign_events.json` | 56 | `{` |
| `examples/opt_in_cycle.md` | 29 | `# Opt-In Only Cycle` |
| `examples/opt_in_cycle_run.json` | 21 | `{` |
| `examples/orchestrator_context.json` | 35 | `{` |
| `examples/organic_content_run.json` | 27 | `{` |
| `examples/organic_context.json` | 35 | `{` |
| `examples/organic_cycle.md` | 14 | `# Organic Free Cycle` |


### Skills Docs (skills/)

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `skills/analytics.md` | 29 | `# Analytics Agent` |
| `skills/compliance.md` | 29 | `# Compliance Agent` |
| `skills/content_planner.md` | 24 | `# ContentPlannerAgent` |
| `skills/memory.md` | 28 | `# Memory Agent` |
| `skills/offer_lookup.md` | 23 | `# OfferLookupAgent` |
| `skills/optimization.md` | 29 | `# Optimization Agent` |
| `skills/orchestrator.md` | 31 | `# Orchestrator Agent` |
| `skills/publisher.md` | 24 | `# PublisherAgent` |
| `skills/seo_research.md` | 23 | `# SEOResearchAgent` |


### Arquivos Raiz

| Arquivo | Linhas | Primeira Linha |
|---------|--------|----------------|
| `.env.example` | 21 | `# Core runtime` |
| `ARCHITECTURE.md` | 263 | `# Campaign Autopilot — Documentação Completa de Arquitetura` |
| `README.md` | 95 | `# Campaign Autopilot` |
| `pyproject.toml` | 21 | `[build-system]` |


---
*Documento gerado em 2026-06-22. Última versão: v2.0.0 — 279 testes passando.*
