# 🔍 Investigação Completa — Campaign Autopilot v5.2.2

> **Data:** 2026-06-25
> **Versão:** v5.2.2
> **Módulos Core:** 40 Python (~12.000 linhas)
> **Agentes:** 128 implementações (~30.000 linhas)
> **Testes:** 66 arquivos (~6.500 linhas)
> **Total Python:** 210+ arquivos, ~60.000 linhas de código
> **Workflows:** 31 definições DAG (inclui ui_design_workflow)
> **Skills Docs:** 252 skills (Skills Warehouse)
> **Quality Layers:** 7 camadas (Critic, Debate, Benchmark, CIA, RAG, ELO, Auto-Regeneration)
> **UI/UX System:** 5 agents 21st.dev + memory + registry
> **AG-Kit Evolution:** 20 fases + Quality Layers 21+
> **Plugin:** Ponytail (lazy senior dev mode) + Product Forge (Open Design)
> **Money Loop:** 24/7 revenue generation em produção
> **Propósito:** Sistema de marketing de afiliados 100% orgânico, multi-agente, com engine de workflow DAG paralelo, camada cognitiva, meta-cognitiva, gerador de site estático, dashboard Streamlit, Quality Layers e Product Forge.

---

## Índice

1. [Visão Arquitetural](#1-visão-arquitetural)
2. [Inventário Completo de Artefatos](#2-inventário-completo-de-artefatos)
3. [Camada Core (src/campaign_autopilot/)](#3-camada-core-srccampaign_autopilot)
4. [Camada de Agentes (26 especialistas)](#4-camada-de-agentes-26-especialistas)
5. [Workflows DAG (27 definições)](#5-workflows-dag-12-definições)
6. [Configs e Exemplos](#6-configs-e-exemplos)
7. [Gerador de Site Estático](#7-gerador-de-site-estático)
8. [Dashboard Streamlit](#8-dashboard-streamlit)
9. [API Integration Hub](#9-api-integration-hub)
10. [Scripts de Operação](#10-scripts-de-operação)
11. [Infraestrutura (Docker)](#11-infraestrutura-docker)
12. [Cognitive Stores](#12-cognitive-stores)
13. [Meta-Cognitive Layer](#13-meta-cognitive-layer)
14. [Módulo de Afiliados](#14-módulo-de-afiliados)
15. [Testes](#15-testes)
16. [Snapshots (free/)](#16-snapshots-free)
17. [Skills Docs](#17-skills-docs)
18. [Análise Semântica e Ontologia](#18-análise-semântica-e-ontologia)
19. [Riscos e Dívida Técnica](#19-riscos-e-dívida-técnica)
20. [Recomendações Estratégicas](#20-recomendações-estratégicas)
21. [Mapa de Decisões Arquiteturais](#26-mapa-de-decisões-arquiteturais)

---

## 1. Visão Arquitetural

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      PONYTAIL PLUGIN (Lazy Senior Dev Mode)               │
│  YAGNI · stdlib first · deletion over addition · shortest working diff   │
├──────────────────────────────────────────────────────────────────────────┤
│                      AG-KIT EVOLUTION (AGENTIC LAYER)                     │
│  TraceStore | ModelRouter | CapabilityRegistry | EvalEngine | Checkpoint│
├──────────────────────────────────────────────────────────────────────────┤
│                      PROVIDER LAYER (Media Unificada)                     │
│  ProviderManager | MediaRouter | CostTracking | Auto Failover             │
│  Texto: 3 providers | Imagem: 4 | Áudio: 2 | Música: 2 | Vídeo: 1       │
├──────────────────────────────────────────────────────────────────────────┤
│                      INFRAESTRUTURA                                       │
│  Docker Compose | Streamlit | SQLite WAL | GitHub Actions CI              │
├──────────────────────────────────────────────────────────────────────────┤
│                      SCRIPTS DE OPERAÇÃO                                   │
│  scripts/autopilot.py | safe-push.sh | deploy.sh | setup.sh               │
├──────────────────────────────────────────────────────────────────────────┤
│                      SERVIÇOS DE SAÍDA                                     │
│  SiteGenerator | RSS/XML | Dashboard Streamlit | WordPress | Social       │
├──────────────────────────────────────────────────────────────────────────┤
│                      META-COGNITIVE LAYER (3ª Ordem)                      │
│  EpistemicEngine | ObserverFusion | RecursiveObserver | ValueSystem       │
├──────────────────────────────────────────────────────────────────────────┤
│                      GOVERNANCE LAYER (2ª Ordem)                          │
│  MetaOrchestrator | EvolutionEngine | AgentFactory | GovernanceAgent      │
│  ResourceManager | QualityAssurance | RiskManager | RollbackManager       │
├──────────────────────────────────────────────────────────────────────────┤
│                      KNOWLEDGE SYNTHESIS                                   │
│  KnowledgeSynthesisEngine (patterns, trends, decay, conflicts)            │
├──────────────────────────────────────────────────────────────────────────┤
│                      COGNITIVE STORES                                      │
│  SemanticMemoryStore | ExplanationStore | OutcomeStore | MemoryStore      │
├──────────────────────────────────────────────────────────────────────────┤
│                      WORKFLOW ENGINE                                       │
│  WorkflowRunner (DAG, ThreadPoolExecutor, Checkpoint, Recovery)           │
├──────────────────────────────────────────────────────────────────────────┤
│                      API HUB + MCP LAYER                                   │
│  APIHub | MCPClient | MCPRegistry | MCPToolAdapter                        │
├──────────────────────────────────────────────────────────────────────────┤
│                      AGENT LAYER (99 especialistas)                        │
│  7 Core · 11 SEO · 13 Content · 6 Media · 26 Revenue · 8 Paid            │
│  5 Publishing · 15 Social · 9 Governance · 6 Intelligence · 3 Extra       │
├──────────────────────────────────────────────────────────────────────────┤
│                      PERSISTENCE (SQLite WAL)                              │
│  MemoryStore | SemanticMemory | TraceStore | Checkpoint | GoalRegistry    │
├──────────────────────────────────────────────────────────────────────────┤
│                      CLI INTERFACE + SECURITY                              │
│  campaign-autopilot | --providers flag | Pre-push hook (secret scan)      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| Módulos Core (src/) | 28 arquivos, ~8.000 linhas |
| Agentes (agents/) | 117 arquivos, ~20.000 linhas |
| Total Módulos Python | 184 arquivos, ~43.600 linhas |
| Testes | 65 arquivos, ~6.000 linhas |
| Workflows DAG | 27 definições JSON |
| Configs | 3 perfis de configuração |
| Exemplos | 9 payloads (JSON + MD) |
| Skills Docs | 50+ documentos de agente |
| Providers Layer | Texto, Imagem, Áudio, Música, Vídeo |
| AG-Kit Evolution | 10 fases (Trace, Checkpoint, Router, MCP, Eval, etc.) |
| Agentes especialistas | 99 classes (consolidados) |
| Frameworks de referência | LangGraph, OpenAI SDK, CrewAI, Microsoft Agent Framework |
| Dependências externas | Streamlit (dashboard only) |
| Plugin instalado | Ponytail (lazy senior dev mode) |
| Segurança | Pre-push hook (bloqueia vazamento de secrets) |
| Python mínimo | 3.10 |

---

## 2. Inventário Completo de Artefatos

### 2.1 Arquivos Raiz

| Arquivo | Linhas | Função |
|---------|--------|--------|
| `pyproject.toml` | 21 | Setup setuptools, entry point `campaign-autopilot`, Python ≥3.10 |
| `.env.example` | 21 | Variáveis de ambiente para runtime, compliance, métricas, integrações |
| `.gitignore` | 16 | Ignora `__pycache__/`, `.venv/`, `*.sqlite3`, `.state/`, `.vscode/` |
| `README.md` | ~120 | README do projeto: descrição, comandos, arquitetura, evolução |
| `ARCHITECTURE.md` | 650 | Documentação de arquitetura gerada automaticamente |
| `INVESTIGACAO_COMPLETA.md` | 1150 | Este documento |
| `Makefile` | 31 | Comandos: setup, test, run, loop, stats, dashboard, docker, deploy, clean |
| `Dockerfile` | 17 | Imagem Docker baseada em python:3.12-slim |
| `docker-compose.yml` | 33 | Orquestração: autopilot scheduler + dashboard | |
| `SKILL.md` | ~100 | Skill do Codex para o projeto |
| `AGENTS.md` | ~100 | Instruções para agentes de IA |
| `META_PROMPT.md` | ~470 | CTO metaprompt — LYZER LABS |
| `.codex-plugin/plugin.json` | — | Plugin Ponytail config |
| `.githooks/pre-push` | ~50 | Hook de segurança (bloqueia secrets) |
| `scripts/safe-push.sh` | ~50 | Script de push seguro |

### 2.2 Código Fonte Core (`src/campaign_autopilot/`)

| Arquivo | Linhas | Tipo | Responsabilidade |
|---------|--------|------|------------------|
| `__init__.py` | 75 | Módulo | `__all__` com 22 exportações públicas |
| `models.py` | 147 | Modelos | Campaign, Event, Metrics, Decision, Policy (dataclasses) |
| `memory.py` | 139 | Persistência | MemoryStore (SQLite WAL, upsert, context manager) |
| `workflow.py` | 350 | Motor | WorkflowSpec, WorkflowStepSpec, WorkflowRunner (DAG), ExecutionPlan |
| `policy.py` | 155 | Engine | PolicyEngine (opt-in, compliance, scale, pause) |
| `metrics.py` | 82 | Métricas | calculate_metrics, anomaly_flags |
| `cli.py` | 193 | Interface | argparse CLI, run_cycle, run_workflow |
| `semantic_memory.py` | 802 | Cognitivo | SemanticMemoryStore (conceitos, claims, ontologia, observers) |
| `explanation.py` | 511 | Cognitivo | ExplanationStore (decisões, regras, contra-factuais, render) |
| `feedback.py` | 245 | Cognitivo | OutcomeStore (expected/actual/delta, lições) |
| `synthesis.py` | 310 | Meta | KnowledgeSynthesisEngine (padrões, conflitos, tendências, decay) |
| `goals.py` | 252 | Meta | GoalRegistry (registro, avaliação, auto-evaluation) |
| `affiliate.py` | 427 | Negócio | OfferManager, AffiliateLink, ContentBrief, redes de afiliados |
| `api_hub.py` | 347 | Integração | APIHub, APICredentials, retry, rate limiting, fallback | |
| `api_hub_v2.py` | — | API Hub v2 com mais integrações |
| `media_providers.py` | 1291 | ProviderManager, MediaRouter, 5 layers de mídia |
| `free_llm_providers.py` | 831 | 13 LLM providers gratuitos com failover automático |
| `free_content_generator.py` | — | Gerador de conteúdo gratuito (stdlib fallback) |
| `trace_store.py` | 548 | AgentTraceStore, TraceRecorder, TraceViewer (AG-Kit) |
| `workflow_checkpoint.py` | 453 | Crash recovery, resume, approval gates (AG-Kit) |
| `model_router.py` | 286 | ModelRouter com fallback e cost-aware routing (AG-Kit) |
| `capability_registry.py` | 314 | MCPClient, MCPRegistry, CapabilityRegistry (AG-Kit) |
| `evaluation_engine.py` | 210 | EvaluationEngine, BenchmarkRunner (AG-Kit) |
| `cli_v2.py` | — | CLI v2 com flag --providers |
| `orchestrator_v2.py` | — | Orchestrator v2 com governança |
| `logging_utils.py` | — | StructuredLogger para todo o sistema |
| `seo_article_template.py` | — | Template de artigo SEO |
| `governance/` (6 files) | 656 | ResourceManager, QA, Risk, External, Analytics, Rollback |
| `execution/` (6 files) | — | ABTesting, AffiliateLinks, Scheduler, Email, Notifications, SEO |
| `content_pipeline/` (7 files) | 2308 | Archetype, Communication, Copywriting, Neuro, Psycho, Storytelling |
| `media_pipeline/` (4 files) | 2601 | CinematicEngine, Audio, Image, Video producers |
| `third_order/` (4 files) | — | EpistemicEngine, ObserverFusion, RecursiveObserver, ValueSystem |

### 2.3 Agentes (`src/campaign_autopilot/agents/`)

#### Agentes Core (5)

| Arquivo | Linhas | Agente | Responsabilidade |
|---------|--------|--------|------------------|
| `base.py` | 148 | AgentBase (ABC) | Classe base, CampaignContext, AgentResult, AgentTrace |
| `analytics.py` | 162 | AnalyticsAgent | Sinais de performance, tendências, oportunidades |
| `compliance.py` | 145 | ComplianceAgent | Validação de conteúdo contra regras e políticas |
| `memory_agent.py` | 133 | MemoryLookupAgent | Busca de padrões e lições de ciclos anteriores |
| `optimization.py` | 164 | OptimizationAgent | Síntese de ações de otimização |
| `orchestrator.py` | 358 | ExecutionPlanningAgent + CampaignOrchestrator | Plano de execução, orquestração central, cognitive stores, drift |

#### Agentes de SEO e Pesquisa (4)

| Arquivo | Linhas | Agente | Responsabilidade |
|---------|--------|--------|------------------|
| `seo_research.py` | 178 | SEOResearchAgent | Pesquisa SEO (keywords, volume, dificuldade, intent) |
| `seo_scraper.py` | 351 | SEOScraperAgent | Dados reais de SEO do Google via scraping simulado |
| `competitor_analysis.py` | 213 | CompetitorAnalysisAgent | Análise de concorrentes, gaps, oportunidades |
| `rank_tracker.py` | 232 | RankTrackerAgent | Tracking de rankings no Google |

#### Agentes de Conteúdo (5)

| Arquivo | Linhas | Agente | Responsabilidade |
|---------|--------|--------|------------------|
| `content_planner.py` | 179 | ContentPlannerAgent | Briefings combinando SEO + ofertas + memória |
| `content_generator.py` | 379 | ContentGeneratorAgent | Geração de artigos otimizados (LLM + template) |
| `content_optimizer.py` | 268 | ContentOptimizerAgent | Otimização SEO do conteúdo |
| `content_repurposer.py` | 186 | ContentRepurposerAgent | Multiplicação para 5+ canais |
| `publisher.py` | 103 | PublisherAgent | Cronograma de publicação |
| `bulk_publisher.py` | 219 | BulkPublisherAgent | Agendamento em lote |

#### Agentes de Publicação (2)

| Arquivo | Linhas | Agente | Responsabilidade |
|---------|--------|--------|------------------|
| `wp_publisher.py` | 275 | WordPressPublisherAgent | Publicação no WordPress via API XML-RPC |
| `site_deploy.py` | 124 | SiteDeployAgent | Geração e deploy de site estático |

#### Agentes de Marketing Multicanal (5)

| Arquivo | Linhas | Agente | Responsabilidade |
|---------|--------|--------|------------------|
| `youtube_marketing.py` | 326 | YouTubeMarketingAgent | Scripts, SEO, descrições para YouTube |
| `email_marketing.py` | 378 | EmailMarketingAgent | Sequências de email marketing |
| `pinterest_marketing.py` | 248 | PinterestMarketingAgent | Pins otimizados para Pinterest |
| `whatsapp_marketing.py` | 210 | WhatsAppMarketingAgent | Mensagens para WhatsApp Marketing |
| `lead_capture.py` | 270 | LeadCaptureAgent | Lead magnets, landing pages, formulários |

#### Agentes de Monitoria e Feedback (3)

| Arquivo | Linhas | Agente | Responsabilidade |
|---------|--------|--------|------------------|
| `revenue_monitor.py` | 271 | RevenueMonitorAgent | Projeção de receita e ROI |
| `analytics_feedback.py` | 287 | AnalyticsFeedbackAgent | Feedback e aprendizado do ciclo |
| `offer_lookup.py` | 125 | OfferLookupAgent | Busca de ofertas de afiliados |

### 2.4 Workflows (`workflows/`)

| Arquivo | Steps | Max Workers | Descrição |
|---------|-------|-------------|-----------|
| `campaign_cycle.json` | 5 | 4 | Ciclo CPA legado |
| `organic_cycle.json` | 5 | 4 | Ciclo orgânico básico |
| `organic_affiliate_cycle.json` | 6 | 4 | Ciclo principal de afiliados orgânico |
| `organic_content_workflow.json` | - | - | Conteúdo orgânico |
| `multi_channel_workflow.json` | - | - | Distribuição multicanal |
| `full_distribution_workflow.json` | - | - | Distribuição completa |
| `money_workflow.json` | 11 | 10 | Workflow focado em dinheiro |
| `revenue_workflow.json` | 10 | 8 | Workflow focado em receita |
| `final_workflow.json` | 14 | 10 | Workflow final completo |
| `ultimate_workflow.json` | 13 | 10 | 6 canais de tráfego orgânico |
| `deploy_workflow.json` | 12 | 8 | Geração e deploy de site |
| `ultimate_workflow.json` | 13 | 10 | Definitivo multicanal | |
| `celular_workflow.json` | — | — | Workflow otimizado para mobile |
| `news_workflow.json` | — | — | Workflow de vertical de notícias |
| `revenue_workflow.json` | — | 8 | Workflow de 13 fontes de renda |
| `organic_integration_workflow.json` | — | — | Workflow de integração orgânica |
| `content_revenue_workflow.json` | — | — | Conteúdo + receita combinados |
| `ciclo_completo_7_canais.json` | — | — | 7 canais de distribuição |
| `ciclo_completo_11_canais.json` | — | — | 11 canais com paid traffic |
| `monetizze_ciclo.json` | — | — | Ciclo Monetizze |
| `kiwify_ciclo.json` | — | — | Ciclo Kiwify |
| `eduzz_ciclo.json` | — | — | Ciclo Eduzz |
| `hotmart_ads_ciclo.json` | — | — | Ciclo Hotmart Ads |
| (mais 5 workflows de campanhas específicas) | — | — | — |

### 2.5 Configs (`configs/`)

| Arquivo | Modo | Policy | Descrição |
|---------|------|--------|-----------|
| `opt_in_cycle.json` | `opt_in_only` | Rigoroso | Requer opt-in explícito, consentimento, compliance |
| `organic_cycle.json` | `organic_only` | Moderado | Requer opt-in, compliance, sem mídia paga |
| `organic_affiliate_cycle.json` | `organic_only` | Leve | Sem opt-in obrigatório, no_paid_media, disclosure obrigatório |

### 2.6 Exemplos (`examples/`)

| Arquivo | Tipo | Conteúdo |
|---------|------|----------|
| `affiliate_context.json` | Contexto | Nicho "marketing digital para iniciantes", 3 canais, política com restricted_terms |
| `organic_context.json` | Contexto | Lead growth orgânico, 3 canais, sem termos restritos |
| `campaign_events.json` | Eventos | 3 eventos (impressions, clicks, conversions) para ciclo CPA |
| `orchestrator_context.json` | Contexto | Opt-in leads, email + sms, budget $1000 |
| `organic_content_run.json` | Run | Estado de execução orgânica (opt_in, consent, compliance) |
| `opt_in_cycle_run.json` | Run | Estado de execução opt-in (sample_size 280, cpa 41.25) |
| `content_workflow_context.json` | Contexto | Contexto para workflow de distribuição de conteúdo |
| `opt_in_cycle.md` | Documentação | Fluxo esperado para ciclo opt-in |
| `organic_cycle.md` | Documentação | Fluxo esperado para ciclo orgânico |

### 2.7 Skills Docs (`skills/`)

| Arquivo | Agente | Idioma |
|---------|--------|--------|
| `analytics.md` | Analytics | EN |
| `analytics_feedback.md` | AnalyticsFeedback | PT-BR |
| `bulk_publisher.md` | BulkPublisher | PT-BR |
| `competitor_analysis.md` | CompetitorAnalysis | PT-BR |
| `compliance.md` | Compliance | EN |
| `content_generator.md` | ContentGenerator | PT-BR |
| `content_optimizer.md` | ContentOptimizer | PT-BR |
| `content_planner.md` | ContentPlanner | PT-BR |
| `content_repurposer.md` | ContentRepurposer | PT-BR |
| `email_marketing.md` | EmailMarketing | PT-BR |
| `lead_capture.md` | LeadCapture | PT-BR |
| `memory.md` | MemoryLookup | EN |
| `offer_lookup.md` | OfferLookup | PT-BR |
| `optimization.md` | Optimization | EN |
| `orchestrator.md` | Orchestrator | EN |
| `pinterest_marketing.md` | PinterestMarketing | PT-BR |
| `publisher.md` | Publisher | PT-BR |
| `rank_tracker.md` | RankTracker | PT-BR |
| `revenue_monitor.md` | RevenueMonitor | PT-BR |
| `seo_research.md` | SEOResearch | PT-BR |
| `seo_scraper.md` | SEOScraper | PT-BR |
| `site_deploy.md` | SiteDeploy | PT-BR |
| `whatsapp_marketing.md` | WhatsAppMarketing | PT-BR |
| `wp_publisher.md` | WordPressPublisher | PT-BR |
| `youtube_marketing.md` | YouTubeMarketing | PT-BR |

### 2.8 Site Gerado (`site/`)

| Arquivo | Conteúdo |
|---------|----------|
| `index.html` | Home com últimos artigos |
| `lead-capture.html` | Landing page de captura |
| `robots.txt` | Instruções para crawlers |
| `rss.xml` | Feed RSS |
| `sitemap.xml` | Sitemap XML |
| `blog/gerar-receita-com-marketing-de-afiliados.html` | Artigo de exemplo |
| `pages/sobre.html` | Página "Sobre" |
| `pages/contato.html` | Página de contato |
| `pages/disclosure.html` | Página de disclosure de afiliados |
| `pages/privacidade.html` | Política de privacidade |
| `assets/css/style.css` | Estilo CSS |

### 2.9 Snapshots (`free/`)

| Versão | Data (estimada) | Características |
|--------|-----------------|-----------------|
| v1.0.0 | Anterior | Versão inicial (4 testes, opt-in cycle) |
| v1.1.0 | Intermediária | Ciclo orgânico adicionado |
| v1.2.0 | Intermediária | Affiliate, semantic, epistemology, feedback, synthesis |
| v2.0.0 | Atual free | Completo com meta-cognitive, goals, ontology drift |

### 2.10 Gerador de Site (`site_generator/`)

| Arquivo | Linhas | Função |
|---------|--------|--------|
| `__init__.py` | 5 | Exportação |
| `generator.py` | 543 | SiteGenerator |

### 2.11 Dashboard (`dashboard/`)

| Arquivo | Linhas | Função |
|---------|--------|--------|
| `app.py` | ~250 | Streamlit dashboard com mais métricas |

### 2.12 Scripts (`scripts/`)

| Arquivo | Linhas | Função |
|---------|--------|--------|
| `autopilot.py` | 350 | Scheduler cíclico com estado persistente |
| `deploy.sh` | 53 | Deploy em produção |
| `setup.sh` | 74 | Setup completo |

### 2.13 Output Gerado (`output/`)

| Arquivo | Conteúdo |
|---------|----------|
| `content/gerar-receita-com-marketing-de-afiliados.md` | Conteúdo gerado de exemplo |
| `published/blog/` | Site publicado de exemplo |

---

## 3. Camada Core (src/campaign_autopilot/)

### 3.1 models.py — Modelos de Domínio

Dataclasses com slots para performance:

- **`Campaign`**: campaign_id, name, status, budget, spend, revenue, target_cpa, target_roas, opt_in, compliance_ok
- **`Event`**: event_id, campaign_id, kind (impression, click, conversion), occurred_at, value, count, metadata
- **`Metrics`**: impressions, clicks, conversions, ctr, cpa, revenue, roas, anomaly_flags
- **`Decision`**: decision_id, campaign_id, kind, status, rationale, parameters, risk_score
- **`Policy`**: requires_opt_in, requires_compliance, min_sample_size, max_cpa, dry_run

### 3.2 memory.py — Persistência SQLite

- **`MemoryStore`**: SQLite WAL mode, context manager, upsert, list, stable_event_id
- Tabelas: `campaigns`, `events`, `metrics`, `decisions`, `memory_records`
- Thread-safe com lock

### 3.3 workflow.py — Workflow Engine DAG

- **`WorkflowSpec`**: Carrega definição JSON de workflow (nome, steps, dependências)
- **`WorkflowStepSpec`**: Step individual com id, agent, depends_on
- **`WorkflowRunner`**: Scheduler DAG com ThreadPoolExecutor
  - Steps sem dependências rodam em paralelo
  - Steps iniciam quando TODAS dependências concluídas
  - Falha não bloqueia o workflow
  - Output final = output do último step
- **`StepResult`**: step_id, agent, status, output, error, timing
- **`WorkflowRunResult`**: trace completo, erros, outputs
- **`ExecutionPlan`**: Plano de ação serializável
- **`ExecutionAction`**: Ação individual

### 3.4 policy.py — Policy Engine

- **`PolicyEngine`**: Portão determinístico para ciclo CPA
- Verifica: opt-in status, compliance, anomaly flags, scale/test/pause thresholds
- Decisões: `continue`, `pause`, `stop`, `scale`, `test`

### 3.5 metrics.py — Métricas

- **`calculate_metrics()`**: Calcula CTR, CVR, CPA, ROAS a partir de eventos
- **`check_anomalies()`**: Flags de anomalia (zero conversions, CTR異常, CPA alto, gasto excessivo)

### 3.6 cli.py — Interface de Linha de Comando

- Dois modos de operação:
  - `--events`: Ciclo CPA legado (events → metrics → policy → decision)
  - `--workflow`: Ciclo workflow DAG (JSON → agents → resultado)
- Suporte a `--db`, `--context`, `--output`
- Parsing de eventos, execução de workflow, output formatado

---

## 4. Camada de Agentes (99 especialistas)

### 4.1 AgentBase (base.py)

Classe base abstrata para todos os agentes:

```python
class AgentBase(ABC):
    def run(self, context: CampaignContext) -> AgentResult: ...
    def record_explanation(self, store, input_state, ...): ...
```

- **`CampaignContext`**: Contexto completo (campaign, signals, memory, policy, step_results, artifacts)
- **`AgentResult`**: output, trace, explanation_ref
- **`AgentTrace`**: agent, step_id, status, started_at, finished_at, duration_ms

### 4.2 Agentes Originais (5)

**AnalyticsAgent**: Deriva sinais de performance, médias, tendências, oportunidades e riscos a partir de séries temporais de spend, conversões, CTR, CPA.

**ComplianceAgent**: Valida conteúdo contra regras de compliance (termos restritos, disclosures obrigatórias, canais bloqueados). Pode bloquear execução.

**MemoryLookupAgent**: Busca memórias de ciclos anteriores similares ao contexto atual e extrai lições relevantes.

**OptimizationAgent**: Síntese de analytics + compliance + memory em ações priorizadas de otimização com riscos e guardrails.

**CampaignOrchestrator + ExecutionPlanningAgent**: Orquestrador central que gerencia workflow, cognitive stores, meta-cognitive layer, detecção de drift ontológico. Converte otimização em plano de execução serializável.

### 4.3 Agentes de SEO e Pesquisa (4)

**SEOResearchAgent**: Pesquisa palavras-chave com volume, dificuldade e intenção (simulado, 35 keywords em 7 nichos).

**SEOScraperAgent**: Scraping de SERP do Google (simulado), extrai rankings, featured snippets, perguntas relacionadas.

**CompetitorAnalysisAgent**: Análise de concorrentes: domínios, estratégias, gaps de conteúdo, oportunidades.

**RankTrackerAgent**: Tracking de posições no Google para keywords alvo (simulado).

### 4.4 Agentes de Conteúdo (5)

**ContentPlannerAgent**: Gera briefings de conteúdo combinando pesquisa SEO + ofertas de afiliados + memória de ciclos.

**ContentGeneratorAgent**: Gera artigos completos usando templates ou LLM (OpenAI opcional), com SEO on-page.

**ContentOptimizerAgent**: Otimiza conteúdo existente para SEO (palavras-chave, heading structure, meta, links).

**ContentRepurposerAgent**: Multiplica conteúdo para 5+ formatos (blog, YouTube, email, Pinterest, WhatsApp).

**PublisherAgent**: Cronograma de publicação com estimativas de cliques e engajamento.

**BulkPublisherAgent**: Agendamento em lote de múltiplos conteúdos.

### 4.5 Agentes de Publicação (2)

**WordPressPublisherAgent**: Publicação automática no WordPress via XML-RPC. Suporte a tags, categorias, featured image.

**SiteDeployAgent**: Gera site estático completo via SiteGenerator.

### 4.6 Agentes de Marketing Multicanal (5)

**YouTubeMarketingAgent**: Scripts de vídeo, títulos SEO, descrições com links de afiliado, tags.

**EmailMarketingAgent**: Sequências de email, linhas de assunto, corpo, CTAs, segmentação.

**PinterestMarketingAgent**: Pins otimizados, descrições SEO, links de afiliado.

**WhatsAppMarketingAgent**: Mensagens para WhatsApp Marketing, CTAs, links rastreados.

**LeadCaptureAgent**: Lead magnets, landing pages, formulários de captura, iscas digitais.

### 4.7 Agentes de Monitoria e Feedback (3)

**RevenueMonitorAgent**: Projeção de receita, ROI, comissões, cenários (otimista, realista, pessimista).

**AnalyticsFeedbackAgent**: Feedback completo do ciclo, lições aprendidas, recomendações para próximo ciclo.

**OfferLookupAgent**: Busca ofertas de afiliados compatíveis com keywords e nicho (simulado, 8 ofertas em 2 redes).

---

## 5. Workflows DAG (27 definições)

### 5.1 campaign_cycle.json (Legado CPA)
```
analytics ──┐
compliance ─┼──→ optimization ──→ execution_planning
memory   ───┘
```

### 5.2 organic_cycle.json (Orgânico Básico)
```
research ───┐
compliance ─┼──→ optimization ──→ execution_planning
memory   ───┘
```

### 5.3 organic_affiliate_cycle.json (Afiliados Orgânico - Principal)
```
seo_research ──┐
               ├──→ offer_lookup ──┐
compliance ────┤                   ├──→ content_planner ──→ publisher
memory_lookup ─┘                   │
              ┌────────────────────┘
              │ (depends_on: seo_research, offer_lookup, memory_lookup)
```

### 5.4 money_workflow.json (Foco em Dinheiro - 11 steps)
```
competitor_analysis ──┐
seo_scraper ──────────┼──→ offer_lookup ──┐
compliance ───────────┤                   ├──→ content_planner ──→ content_generator ──┐
memory_lookup ────────┘                   │                                            │
                                          └── (depends_on: seo_scraper,                 ├──→ content_repurposer ──┐
                                              competitor_analysis,                      │                        │
                                              offer_lookup, memory_lookup)              │                        ├──→ revenue_monitor ──┐
                                                                                        │                        │                     │
                                                                                        └──→ wp_publisher ──────┘                     ├──→ analytics_feedback
                                                                                              (depends_on: content_generator,          │
                                                                                               compliance)                             │
                                                                                                                                       └── (depends_on: content_repurposer,
                                                                                                                                           offer_lookup, wp_publisher)
```

### 5.5 revenue_workflow.json (Foco em Receita - 10 steps)
Similar ao money_workflow, mas começa com seo_research em vez de competitor_analysis.

### 5.6 final_workflow.json (Workflow Final - 14 steps)
```
competitor_analysis ──┐
seo_scraper ──────────┼──→ offer_lookup ──┐
compliance ───────────┤                   ├──→ content_planner ──→ content_generator ──┐
memory_lookup ────────┘                   │                                            │
                                          └── ...                                      ├──→ content_repurposer ──┐
                                                                                        │                        │
                                                                                        ├──→ content_optimizer  │
                                                                                        │                        │
                                                                                        └──→ wp_publisher ──────┼──→ rank_tracker ──┐
                                                                                                                  │                  │
                                                                                                                  └── bulk_publisher ─┘
                                                                                                                                      │
                                                                                                                                      └──→ revenue_monitor ──→ analytics_feedback
```

### 5.7 ultimate_workflow.json (6 Canais - 13 steps)
```
seo_research ──→ offer_lookup ──→ content_planner ──→ content_generator ──┬──→ youtube_marketing
                                                                           ├──→ email_marketing
                                                                           ├──→ pinterest_marketing
                                                                           ├──→ whatsapp_marketing
                                                                           ├──→ lead_capture
                                                                           └──→ wp_publisher → analytics_feedback
```

### 5.8 deploy_workflow.json (Deploy - 12 steps)
```
competitor_analysis ──┐
seo_scraper ──────────┼──→ offer_lookup ──┐
compliance ───────────┤                   ├──→ content_planner ──→ content_generator ──┐
memory_lookup ────────┘                   │                                            │
                                          └── ...                                      ├──→ content_repurposer ──┐
                                                                                        │                        │
                                                                                        └──→ lead_capture ──────┼──→ site_deploy ──→ analytics_feedback
                                                                                                                  │
                                                                                                                  └──→ revenue_monitor
```

### 5.9 Outros Workflows
- **organic_content_workflow.json**: Conteúdo orgânico simplificado
- **multi_channel_workflow.json**: Distribuição multicanal
- **full_distribution_workflow.json**: Distribuição completa

---

## 6. Configs e Exemplos

### 6.1 Configs

Três perfis de configuração que definem o comportamento do ciclo:

**organic_affiliate_cycle.json** (principal):
- Modo: `organic_only` (sem tráfego pago)
- Policy: não requer opt-in explícito, requer compliance
- Disclosures obrigatórias: `disclosure_afiliado`
- Canais: SEO, community, newsletter, YouTube
- Frequência de publicação: a cada 3 dias

**opt_in_cycle.json** (legado CPA):
- Modo: `opt_in_only`
- Policy rigorosa: opt-in explícito, consentimento, compliance
- Stop conditions: missing_opt_in, missing_consent, policy_failure

**organic_cycle.json** (orgânico gratuito):
- Modo: `organic_only`
- Requer opt-in e compliance
- Canais: SEO, community, newsletter, social, referrals

### 6.2 Exemplos

Oito payloads de exemplo que demonstram o uso do sistema:
- Contextos de campanha (affiliate, organic, orchestrator)
- Runs de ciclo (opt-in, organic_content)
- Eventos de campanha
- Documentação de fluxo (opt-in_cycle.md, organic_cycle.md)

---

## 7. Gerador de Site Estático

**Arquivo:** `site_generator/generator.py` (543 linhas)

A classe `SiteGenerator` produz um site HTML5 completo a partir do output dos agentes:

### Funcionalidades
- **index.html**: Home com últimos artigos, hero section, CTA
- **blog/artigo-slug.html**: Página individual para cada artigo
- **pages/**: Sobre, Contato, Privacidade, Disclosure
- **lead-capture.html**: Landing page com lead magnet
- **sitemap.xml**: Sitemap XML para SEO
- **robots.txt**: Instruções para crawlers
- **rss.xml**: Feed RSS
- **assets/css/style.css**: CSS responsivo (Tailwind-like minimal)
- Design responsivo, meta tags SEO, Open Graph

### Output Example
O diretório `site/` contém um site completo gerado:
- Nicho: marketing digital para iniciantes
- 1 artigo publicado
- Páginas institucionais completas
- Feed RSS e sitemap

---

## 8. Dashboard Streamlit

**Arquivo:** `dashboard/app.py` (193 linhas)

Dashboard web interativo construído com Streamlit:

### Funcionalidades
- Visão geral com métricas (ciclos, palavras, vídeos, emails, tempo médio)
- Tabela de últimos ciclos com status, duração, palavras geradas
- Sidebar com links rápidos (arquitetura, README)
- Configuração de caminho do banco de dados
- Botão de atualização manual

### Como Executar
```bash
make dashboard
# ou
streamlit run dashboard/app.py --server.port=8501
```

---

## 9. API Integration Hub

**Arquivo:** `src/campaign_autopilot/api_hub.py` (347 linhas)

Ponte entre o sistema simulado e APIs reais:

### Credenciais Gerenciadas
| API | Env Var | Funcionalidade |
|-----|---------|----------------|
| Hotmart | HOTMART_CLIENT_ID/SECRET | Busca de ofertas |
| Amazon PA-API | AMAZON_ACCESS/SECRET/ASSOCIATE_TAG | Produtos e comissões |
| Ahrefs | AHREFS_API_KEY | Pesquisa SEO |
| WordPress | WP_URL/USER/PASSWORD | Publicação |
| OpenAI | OPENAI_API_KEY | Geração de conteúdo |
| Pinterest | PINTEREST_ACCESS_TOKEN | Publicação de pins |

### Características
- Fallback automático para dados simulados quando sem credenciais
- Rate limiting com janela de tempo
- Retry com backoff exponencial
- Cache de respostas

---

## 10. Scripts de Operação

### 10.1 autopilot.py (Scheduler Cíclico)

**Arquivo:** `scripts/autopilot.py` (350 linhas)

Executor automático de workflows em loop com estado persistente:

**Modos de Operação:**
- `--loop`: Loop contínuo com intervalo configurável (--interval)
- `--cron`: Execução única para agendamento cron
- `--stats`: Estatísticas do banco de dados

**Funcionalidades:**
- Banco de dados próprio (.state/autopilot.db)
- Tabela `autopilot_cycles` com histórico completo
- Extração de métricas (palavras, vídeos, emails por ciclo)
- Integração com MemoryStore, SemanticMemoryStore, KnowledgeSynthesisEngine

### 10.2 setup.sh (Setup Completo)

**Arquivo:** `scripts/setup.sh` (74 linhas)

Automação de setup inicial:
1. Verifica Python 3.10+
2. Cria virtual environment
3. Instala dependências (pip install -e . + streamlit)
4. Cria diretórios (.state, output/content, reports)
5. Configura .env a partir de .env.example
6. Valida instalação com testes
7. Instruções para agendamento cron

### 10.3 deploy.sh (Deploy em Produção)

**Arquivo:** `scripts/deploy.sh` (53 linhas)

Deploy automatizado:
- **Opção 1 (Docker)**: docker-compose up -d --build
- **Opção 2 (Direto)**: autopilot em background + dashboard

---

## 11. Infraestrutura (Docker)

### Dockerfile
- Base: python:3.12-slim
- Instala dependências do sistema (ca-certificates)
- pip install -e . + streamlit
- Cria diretórios de estado

### docker-compose.yml
```yaml
services:
  autopilot:           # Scheduler em loop (48h)
    build: .
    volumes: .state, output, reports
    restart: unless-stopped

  dashboard:           # Streamlit web UI
    build: .
    ports: 8501:8501
    depends_on: autopilot
    restart: unless-stopped
```

### Makefile
| Comando | Ação |
|---------|------|
| `make setup` | Setup completo |
| `make test` | Rodar testes |
| `make run` | Executar autopilot |
| `make loop` | Executar em loop |
| `make dashboard` | Iniciar dashboard |
| `make docker` | Docker compose up |
| `make deploy` | Deploy em produção |
| `make clean` | Limpar tudo |

---

## 12. Cognitive Stores

### 12.1 MemoryStore (SQLite WAL)

Persistência base do sistema. Tabelas:
- `campaigns`, `events`, `metrics`, `decisions`, `memory_records`
- WAL mode para concorrência
- Thread-safe

### 12.2 SemanticMemoryStore

**Arquivo:** `semantic_memory.py` (802 linhas)

Grafo de conhecimento persistente com:

**Conceitos**: Entidades registradas por namespace
- `channel`, `niche`, `keyword`, `offer`, `meta`, `knowledge`

**KnowledgeClaims**: Relações entre conceitos
- subject + predicate + object
- confidence (0.0-1.0)
- epistemic_status (VERIFIED, INFERRED, ASSUMED, HYPOTHETICAL)
- observer, source_cycle_id, provenance

**Ontology**: Versões de ontologia com diff
- `ontology_snapshots`: snapshot completo
- `ontology_diffs`: diferenças entre versões
- `ontology_alerts`: alertas de drift semântico

**Observers**: analytics, compliance, memory_lookup, optimization, execution_planning, seo_research, offer_lookup, content_planner, publisher, ontology_steward, orchestrator

### 12.3 ExplanationStore

**Arquivo:** `explanation.py` (511 linhas)

Proveniência completa de decisões:

- `input_state`: Estado na entrada
- `reasoning`: Regras e lógica aplicadas
- `applied_rules`: Regras específicas usadas
- `counterfactuals`: "O que aconteceria se..."
- `rendered`: Explicação em linguagem natural para operadores/compliance/CTO

### 12.4 OutcomeStore

**Arquivo:** `feedback.py` (245 linhas)

Captura de resultados e aprendizado:

- `expected`: Resultado esperado
- `actual`: Resultado real
- `delta`: Diferença
- `lesson`: Lição aprendida
- `lesson_tags`: Tags para categorização
- Suporte a consulta por ciclo

### 12.5 KnowledgeSynthesisEngine

**Arquivo:** `synthesis.py` (310 linhas)

Síntese de conhecimento entre ciclos:

- `find_reinforcing_patterns()`: Padrões que se repetem em múltiplos ciclos
- `find_conflicting_patterns()`: Conflitos entre claims de diferentes observers
- `compute_trend()`: Tendência de confiança (rising/stable/declining)
- `schedule_decay()`: Decaimento temporal de confiança por status epistêmico
- `generate_meta_insights()`: "Conhecimento sobre o conhecimento"

---

## 13. Meta-Cognitive Layer

### 13.1 EpistemicMonitor

Sistema de classificação epistêmica embutido no SemanticMemoryStore:

**Status Epistêmicos:**
| Status | Peso | Descrição |
|--------|------|-----------|
| VERIFIED | 1.0 | Verificado por múltiplos observers |
| INFERRED | 0.8 | Inferido a partir de evidências |
| ASSUMED | 0.5 | Assumido como verdadeiro |
| HYPOTHETICAL | 0.3 | Hipótese não confirmada |

**Decaimento Padrão:**
| Status | Decaimento por ciclo |
|--------|---------------------|
| VERIFIED | 0.95 |
| INFERRED | 0.85 |
| ASSUMED | 0.75 |
| HYPOTHETICAL | 0.65 |

### 13.2 OntologySteward

Gerenciamento de versões de ontologia com detecção de drift:

- `ontology_snapshots`: Estado completo da ontologia em um momento
- `ontology_diffs`: Diferenças entre snapshots consecutivos
- `ontology_alerts`: Alertas quando drift é detectado

### 13.3 GoalRegistry

**Arquivo:** `goals.py` (252 linhas)

Registro e avaliação de metas estratégicas:

- `register_goal()`: Cria nova meta com critérios de sucesso
- `evaluate_goal()`: Avalia meta contra resultado medido
- `evaluate_from_outcome()`: Auto-avaliação a partir de dados do ciclo
- `get_goal_status()`: Status completo com última avaliação
- Suporte a métricas inversas (CPA, CPC: menor é melhor)

### 13.4 Semantic Drift Detection

O orquestrador executa `_check_ontology_drift()` automaticamente após cada ciclo:
1. Cria snapshot da ontologia atual
2. Compara com snapshot anterior (se existir)
3. Gera diff (conceitos adicionados/removidos, claims alterados)
4. Registra alertas semânticos

---

## 14. Provider Layer (Media Unificada)

> `src/campaign_autopilot/media_providers.py` — 1291 linhas

Camada de abstração sobre múltiplos providers de mídia com failover automático.

### Providers Implementados

| Camada | Providers | Gratuito? |
|--------|-----------|-----------|
| Texto | LiteLLM, FreeLLM (13 providers), Stdlib Fallback | ✅ (FreeLLM) |
| Imagem | Pollinations, Replicate, Diffusers, Pillow | ✅ (Pollinations, Pillow) |
| Áudio | Edge-TTS (neural, ~400 vozes), gTTS | ✅ Ambos |
| Música | AlgorithmicMusic (stdlib), AudioCraft | ✅ (Algorithmic) |
| Vídeo | MoviePy | ✅ |

### Arquitetura

```
ProviderManager (singleton, lazy discovery)
├── TextProvider      → LiteLLM / FreeLLM / Stdlib
├── ImageProvider     → Pollinations / Replicate / Diffusers / Pillow
├── AudioProvider     → Edge-TTS / gTTS
├── MusicProvider     → Algorithmic / AudioCraft
└── VideoProvider     → MoviePy
```

### CLI

```bash
PYTHONPATH=src .venv/bin/python -m campaign_autopilot.cli --providers
```

---

## 15. AG-Kit Evolution Program

> 6 novos arquivos, ~1.800 linhas — capacidades agentic de nova geração

| Capacidade | Arquivo | Status |
|-----------|---------|--------|
| Agent Tracing | `trace_store.py` (548 linhas) | ✅ |
| Workflow Checkpoint | `workflow_checkpoint.py` (453 linhas) | ✅ |
| Multi-Model Router | `model_router.py` (286 linhas) | ✅ |
| MCP Integration | `capability_registry.py` (314 linhas) | ✅ |
| Evaluation Engine | `evaluation_engine.py` (210 linhas) | ✅ |
| Governance Agent | `governance_agent.py` (~160 linhas) | ✅ |
| Agent Factory | `agent_factory.py` (~490 linhas) | ✅ |
| Autonomous Evolution | `evolution_engine.py` | ✅ |

### Princípio

**Adotar capacidades, não frameworks.** LangGraph, OpenAI Agents SDK, CrewAI e Microsoft Agent Framework são arquiteturas de referência, não dependências de runtime.

---

## 16. Ponytail Plugin (Lazy Senior Dev Mode)

> `.codex-plugin/` — Plugin Codex para forçar código minimalista

Princípios aplicados em toda a base:
- **YAGNI:** Não construir o que não foi pedido
- **stdlib first:** Preferir a biblioteca padrão sobre dependências
- **Deletion over addition:** Remover código morto antes de adicionar novo
- **Shortest working diff:** A menor mudança que funciona

### Simplificações Aplicadas

| Antes | Depois | Economia |
|-------|--------|----------|
| 7 agentes de governança individuais | 1 GovernanceAgent com 7 delegates | -6 arquivos, -120 linhas |

---

## 17. Segurança

### Pre-push Hook (`.githooks/pre-push`)

Escaneia automaticamente arquivos staged antes de cada push:
- Bloqueia se detectar: `ghp_*`, `sk-*`, chaves AWS, Bearer tokens, chaves privadas
- Não bloqueia tokens na URL do remote (autenticação padrão do git)
- Configurado via `git config core.hooksPath .githooks`

### Proteções
- `.env` no `.gitignore`
- `.env.example` com placeholders (`sua_chave_aqui`)
- Remote URL sem token após push
- Affiliate IDs sanitizados do histórico
- Histórico git limpo (filter-branch aplicado)

---

## 18. Módulo de Afiliados

**Arquivo:** `affiliate.py` (427 linhas)

### Modelos
- **`AffiliateOffer`**: offer_id, network (amazon, hotmart, monetizze, awin), product_name, commission_type/value, cookie_days, category
- **`AffiliateLink`**: link_id, offer_id, base_url, tracked_url, source, content_id
- **`ContentBrief`**: Planner output combinando oferta + keyword + call_to_action

### OfferManager
- Gerenciamento de ofertas em SQLite
- CRUD de ofertas e links
- Consulta por categoria, rede, comissão
- Tracking de cliques por link

### Redes Suportadas
- Amazon Associates
- Hotmart
- Monetizze
- Awin
- (Extensível via API Hub)

---

## 19. Testes

**37 arquivos, 4.588 linhas, 279+ testes (todos passando)**

### Cobertura por Camada

| Categoria | Arquivos | Cobertura |
|-----------|----------|-----------|
| Core (models, memory, metrics, policy, cli) | 6 | Cobertura completa de CRUD, serialização, edge cases |
| Workflow Engine | 2 | DAG execution, paralelismo, dependências, falhas |
| Cognitive Stores (semantic, epistemic, synthesis) | 5 | 31+ testes de semantic memory, epistemic weight, decay, ontology diff |
| Feedback & Goals | 3 | OutcomeStore (expected/actual/delta), GoalRegistry (auto-evaluation) |
| Affiliate | 2 | OfferManager, links, redes, ContentBrief, integração workflow |
| Agentes Individuais | 18 | Cada agente com testes de run(), output, edge cases |
| Ciclos (CPA, orgânico, afiliado) | 3 | Integração workflow completo |
| CLI | 2 | Parsing, run_cycle, run_workflow, subprocess full stack |
| Snapshots (free/) | 1 | Existência, versão correta, consistência |

### Destaques
- Testes de integração com workflow completo (CPA + orgânico + afiliados)
- Testes de subprocess (CLI como processo externo)
- Testes de epistemic status, weight, decay, ontology diff
- Testes de meta-cognitive (observers, epistemic claims, goals, ontology)

---

## 20. Snapshots (free/)

### Estrutura
```
free/
├── README.md          — Manifesto free/mit
├── VERSION.json       — v2.0.0 (último snapshot congelado)
├── v1.0.0/            — Versão inicial (4 testes, opt-in cycle)
├── v1.1.0/            — Versão orgânica (organic cycle)
├── v1.2.0/            — Versão affiliate + cognitive stores
└── v2.0.0/            — Versão completa (meta-cognitive, goals, drift)
```

### Evolução
| Versão | Principais Adições |
|--------|-------------------|
| v1.0.0 | Baseline: opt-in campaign autopilot |
| v1.1.0 | Organic acquisition: content, SEO, community, opt-in capture |
| v1.2.0 | Cognitive: semantic memory, explanation provenance, outcome feedback, knowledge synthesis |
| v2.0.0 | Meta-cognitive: epistemic-aware reasoning, confidence decay, ontology drift detection, goal tracking |

### Nota
Os snapshots free/ são versões congeladas (read-only). O projeto principal (raiz) evoluiu significativamente além do v2.0.0 com 26 agentes, 12 workflows, site generator e dashboard.

---

## 21. Skills Docs

24 documentos de skill, um para cada agente, misturando inglês (5) e português (19):

**Em inglês (5):**
- `analytics.md`, `compliance.md`, `memory.md`, `optimization.md`, `orchestrator.md`

**Em português (19):**
- `analytics_feedback.md`, `bulk_publisher.md`, `competitor_analysis.md`, `content_generator.md`, `content_optimizer.md`, `content_planner.md`, `content_repurposer.md`, `email_marketing.md`, `lead_capture.md`, `offer_lookup.md`, `pinterest_marketing.md`, `publisher.md`, `rank_tracker.md`, `revenue_monitor.md`, `seo_research.md`, `seo_scraper.md`, `site_deploy.md`, `whatsapp_marketing.md`, `wp_publisher.md`, `youtube_marketing.md`

Cada documento contém: Função, Responsabilidades, Input/Output Esperado, Regras e Guardrails.

---

## 22. Análise Semântica e Ontologia

### Observer Modeling

Observers registrados no sistema:
- Core: `analytics`, `compliance`, `memory_lookup`, `optimization`, `execution_planning`, `orchestrator`
- SEO: `seo_research`, `seo_scraper`, `competitor_analysis`, `rank_tracker`
- Conteúdo: `content_planner`, `content_generator`, `content_optimizer`, `content_repurposer`, `publisher`, `bulk_publisher`
- Publicação: `wp_publisher`, `site_deploy`
- Marketing: `youtube_marketing`, `email_marketing`, `pinterest_marketing`, `whatsapp_marketing`, `lead_capture`
- Monitoria: `revenue_monitor`, `analytics_feedback`, `offer_lookup`
- Meta: `ontology_steward`

### Cadeia Epistêmica

```
Dados Brutos (EVENTOS)
    ↓ calculate_metrics()
Métricas Agregadas (INFERRED, conf=0.6-0.8)
    ↓ Analytics Agent
Sinais de Performance (INFERRED, conf=0.3-0.6)
    ↓ PolicyEngine / Optimization Agent
Decisões / Ações (INFERRED/ASSUMED)
    ↓ OutcomeStore
Feedback (VERIFIED, conf=0.7-1.0)
    ↓ KnowledgeSynthesisEngine
Padrões Reforçados / Conflitos (INFERRED, conf=0.3-0.9)
    ↓ EpistemicMonitor
Meta-Conhecimento (decaimendo temporal)
```

### Ontologia de Domínio

| Namespace | Exemplos |
|-----------|---------|
| `channel` | seo, newsletter, youtube, email, sms, pinterest, whatsapp |
| `niche` | marketing digital, finanças, tecnologia, saúde |
| `keyword` | Keywords com volume, dificuldade, intent |
| `offer` | Ofertas de afiliados por rede |
| `content` | Artigos, briefings, scripts, emails, pins |
| `meta` | semantic_drift, ontology_alerts |
| `knowledge` | feedback_lessons, padrões, conflitos |

---

## 23. Riscos e Dívida Técnica

### 🟡 Risco Médio — Dados Simulados

**Arquivos afetados:**
- `agents/seo_research.py`: 35 keywords simuladas em 7 nichos
- `agents/seo_scraper.py`: SERP scraping simulado
- `agents/competitor_analysis.py`: Análise simulada
- `agents/offer_lookup.py`: 8 ofertas simuladas

**Impacto:** Sistema funciona end-to-end mas não gera valor real sem integração com APIs de SEO (Ahrefs/Semrush) e redes de afiliados (Hotmart/Amazon).

**Mitigação:** `api_hub.py` já fornece a estrutura de integração. Basta configurar credenciais.

### 🟢 Risco Baixo — Sem Execução Automática

Por design, agente propõe ações mas requer aprovação humana. Explícito nas skills: "Requires human approval."

### 🟢 Risco Baixo — Zero Dependências (Core)

Stdlib only (Python 3.10+). Streamlit é dependência apenas para dashboard. SQLite built-in.

### 🟡 Risco Médio — Compartilhamento de Conexão SQLite

`MemoryStore._conn` compartilhado entre todas as camadas cognitivas. `threading.Lock` mitiga parcialmente.

### 🟢 Risco Baixo — Sem Rate Limiting / Retry (Core)

Sistema simulado não precisa. `api_hub.py` já implementa rate limiting e retry para APIs reais.

### 🟡 Risco Médio — Documentação Bilíngue

Skills em EN (5) e PT-BR (19). Código em inglês. Configurações em português. Pode causar confusão.

### 🟢 Risco Baixo — Snapshot Desatualizado

free/ está em v2.0.0 mas o projeto atual é v5.0.0. Snapshots são apenas referência histórica.

### 🟡 Risco Baixo — Sem Testes de Carga

Workflow DAG com 14 steps e 10 workers paralelos não foi testado sob carga.

---

## 24. Recomendações Estratégicas

### Imediatas (Ordem de Prioridade)

1. **🔴 Conectar API Hub** — Configurar credenciais reais (Hotmart, Amazon, Ahrefs) para substituir dados simulados
2. **🔴 Configurar WordPress Real** — WP_URL, WP_USER, WP_PASSWORD para publicação automática
3. **🔴 Configurar OpenAI** — OPENAI_API_KEY para geração de conteúdo real via LLM

### Curto Prazo (Próximos Ciclos)

4. **🟡 SEO Real** — Conectar Ahrefs API para pesquisa de keywords real
5. **🟡 Hotmart Integration** — Configurar Hotmart API para ofertas reais
6. **🟡 Monitoramento de Resultados** — Acompanhar cliques, conversões e receita real
7. **🟡 Loop Automático 48h** — Configurar cron ou --loop para execução contínua

### Médio Prazo

8. **🟢 Health Checks nos Agentes** — Timeout, error rate, latency monitoring
9. **🟢 Observabilidade** — Prometheus metrics + structured logging
10. **🟢 Testes de Carga** — Validar DAG executor com N agents em paralelo
11. **🟢 Canal Adicional: TikTok** — Novo agente para marketing no TikTok
12. **🟢 Canal Adicional: Instagram** — Agente para marketing no Instagram

### Estratégico

13. **💰 Google AdSense** — Monetizar o tráfego orgânico com anúncios display
14. **💰 Produto Próprio** — Criar infoproduto (curso, ebook) com margem maior que afiliados
15. **💰 Lista de Email** — Capturar leads e nutrir com sequências automatizadas
16. **📊 Data-Driven** — Usar dados reais de tráfego para alimentar o ciclo de aprendizado
17. **🤖 Full Autopilot** — Uma vez conectado a APIs reais, o sistema opera 100% autônomo

---

## 25. AG-Kit Evolution — Phases 11-20 (Strategic Roadmap)

> O projeto ultrapassou frameworks de agentes tradicionais. As próximas 10 fases transformam o Campaign Autopilot em um Sistema Operacional Cognitivo Verticalizado.

### Phase 11 — Constraint Intelligence Layer ✅ IMPLEMENTED

`src/campaign_autopilot/constraint_intelligence.py` (469 linhas)

Camada que modela explicitamente as restrições que governam a realidade do sistema. Hoje as constraints estão implícitas em `policy.py`, `compliance.py` e `governance/`. Agora elas são centralizadas em um `ConstraintGraph` consultável.

**Componentes:**
- `ConstraintGraph` — grafo de 12 constraints default
- `ConstraintAwareWorkflow` — bloqueia steps quando constraints críticas são violadas
- `ConstraintDetector` — detecta mudanças em constraints baseado em sinais externos
- `CausalLink` — modela relações causa-efeito entre constraints e outcomes

### Phases 12-20 (Roadmap)

| Phase | Component | Descrição | Prioridade |
|-------|-----------|-----------|------------|
| 12 | World Model Engine | Sistema simula cenários ("what if Google atualizar o algoritmo?") | P1 |
| 13 | Economic Intelligence | Alocação de capital como hedge fund interno | P2 |
| 14 | Agent Evolution Engine | Agentes sofrem mutação, competem e evoluem | P3 |
| 15 | Cognitive Mesh | Agentes compartilham crenças sem orquestrador central | P5 |
| 16 | Digital Twin Layer | Cópia do sistema para experimentos antes do deploy | P4 |
| 17 | Self-Improvement Engine | Sistema gera seus próprios PRs | P6 |
| 18 | Constraint Genealogy | Árvore genealógica de decisões e constraints | P7 |
| 19 | Organization-as-Agent | 1 organização ao invés de 99 agentes | P8 |
| 20 | Autonomous Enterprise Kernel | Pilha completa: auto-sustentável, auto-evolutiva | P9 |

### Competitive Position

Campaign Autopilot é o único projeto open source que combina simultaneamente:
- ✅ Governança (GovernanceAgent + ConstraintGraph)
- ✅ Meta-governança (MetaOrchestrator)
- ✅ Ontologia (SemanticMemory + ObserverFusion)
- ✅ Epistemologia (EpistemicEngine)
- ✅ Evolution (EvolutionEngine + AgentFactory)
- ⬜ Digital Twin (Phase 16)
- ⬜ Economic Allocation (Phase 13)

Nenhum concorrente (CrewAI, LangGraph, AutoGen, OpenAI Agents SDK, Mastra, OpenHands, Agent Zero) possui essa combinação.

---

## 26. Mapa de Decisões Arquiteturais

| Decisão | Alternativa Rejeitada | Razão |
|---------|----------------------|-------|
| SQLite (não PostgreSQL) | Banco externo | Zero dependências, portátil, WAL para concorrência |
| ThreadPoolExecutor (não asyncio) | asyncio, Celery | Simplicidade, stdlib, paralelismo suficiente |
| DAG em JSON (não código) | DSL própria, YAML | Serializável, versionável, editável por não-programadores |
| AgentBase + ABC | Protocol, Callable | Type safety, extensibilidade, interface clara |
| Simulação (não mock library) | unittest.mock, VCR.py | Transparente, demonstrável, sem dependências |
| EpistemicStatus no SQLite | Dict em RAM | Persistente, consultável, auditável |
| Snapshot free/ (não git tag) | Git tags | Autossuficiente, distribuível, sem dependência de git |
| Dois modos CLI (events/workflow) | Um modo unificado | Backward compatibility, evolução gradual |
| SiteGenerator em Python | SSG externo (Hugo, Jekyll) | Integração direta com output dos agentes |
| API Hub com fallback | API calls diretas | Robustez, desenvolvimento offline |
| Streamlit Dashboard | Flask/React SPA | Rápido de implementar, SQLite integration nativa |
| Docker Compose | K8s, Swarm | Simplicidade para MVP, deploy em VPS única |

---

## 27. Apêndice: Comandos Úteis

```bash
# Setup completo
make setup

# Executar workflow de afiliados (principal)
campaign-autopilot --workflow workflows/organic_affiliate_cycle.json \
  --context examples/affiliate_context.json --db .state/db.sqlite3

# Executar workflow de receita (recomendado)
python scripts/autopilot.py \
  --workflow workflows/revenue_workflow.json \
  --context examples/content_workflow_context.json \
  --db .state/autopilot.db

# Executar em loop a cada 48h
python scripts/autopilot.py \
  --workflow workflows/revenue_workflow.json \
  --context examples/content_workflow_context.json \
  --db .state/autopilot.db --loop --interval 48

# Iniciar dashboard
make dashboard

# Rodar todos os testes
make test

# Rodar testes de um módulo específico
python -m unittest tests.test_semantic_memory

# Gerar site estático
python -c "from site_generator.generator import SiteGenerator; SiteGenerator().generate([{'title':'test','content':'hello'}])"

# Deploy completo (Docker)
make deploy

# Docker compose
make docker

# Limpar tudo
make clean
```

---

## Glossário

| Termo | Definição |
|-------|-----------|
| **DAG** | Directed Acyclic Graph — grafo de dependências sem ciclos |
| **Workflow** | Sequência de steps executados por agentes |
| **Step** | Unidade atômica de trabalho executada por um agente |
| **Agente** | Especialista que processa contexto e produz output |
| **Cognitive Store** | Camada de memória persistente com significado semântico |
| **Meta-Cognitive** | Camada que observa e regula o próprio processo cognitivo |
| **Epistemic Status** | Classificação da confiabilidade do conhecimento |
| **Ontology Drift** | Mudança na estrutura de conceitos ao longo do tempo |
| **Semantic Memory** | Memória de longo prazo baseada em significado, não dados brutos |
| **Explanation Store** | Registro de decisões com proveniência completa |
| **Outcome Store** | Captura de resultados esperados vs reais |
| **Knowledge Synthesis** | Geração de meta-conhecimento a partir de padrões |
| **API Hub** | Ponte entre dados simulados e APIs reais |
| **Site Generator** | Conversor de output de agentes em site HTML estático |
| **Lead Magnet** | Isca digital para captura de leads (ebook, checklist, etc.) |
| **Disclosure** | Aviso de transparência sobre links de afiliado |
| **Organic Only** | Estratégia sem tráfego pago, apenas SEO e conteúdo |
| **Provider Layer** | Camada de abstração sobre múltiplos providers de mídia |
| **MediaRouter** | Roteador com failover automático, cost tracking e qualidade |
| **AG-Kit Evolution** | Programa para incorporar padrões agentic modernos |
| **GovernanceAgent** | Agente único que consolida 7 delegates de governança |
| **Ponytail** | Plugin Codex para lazy senior dev mode (YAGNI, stdlib first) |
| **TraceStore** | Persistência SQLite WAL de traces de agentes |
| **ModelRouter** | Roteamento inteligente entre LLMs com fallback |
| **MCP** | Model Context Protocol — interoperabilidade universal de ferramentas |

---

*Documento gerado em 2026-06-22 | Atualizado em 2026-06-24. Investigação completa do projeto Campaign Autopilot v5.1.0 — ~43.600 linhas de código, 99 agentes, 27 workflows, 65 testes (404+), 50+ skills docs, Provider Layer, AG-Kit Evolution, Ponytail Plugin.*

---

## ⚡ Product Forge — Lyzer Labs Visual Generation Layer (Open Design Integration)

**Status:** ✅ Integrado (2026-06-24)

### O que é
Camada de geração visual que conecta o Design System Lyzer Labs (no formato Open Design) com os dados de campanha do Campaign Autopilot. Gera landing pages, dashboards, emails e apresentações em HTML puro — sem dependências externas.

### Componentes

| Módulo | Arquivo | Função |
|--------|---------|--------|
| Design System | `product_forge/design_system.py` | Spec Open Design com tokens, componentes e layouts |
| Color Palette | `product_forge/color_palette.py` | 59 cores, 8 gradientes, 7 shadows, tipografia completa |
| Artifact Generator | `product_forge/artifact_generator.py` | Core engine — renderiza HTML/CSS de qualquer artefato |
| Landing Page Gen | `product_forge/landing_page_generator.py` | Landing pages otimizadas para afiliados |
| Dashboard Gen | `product_forge/dashboard_generator.py` | Dashboards com KPIs, gráficos e tabelas |
| Email Template Gen | `product_forge/email_template_generator.py` | Templates de email marketing responsivos |
| Presentation Gen | `product_forge/presentation_generator.py` | Apresentações em slides HTML |

### DESIGN.md
Arquivo `DESIGN.md` na raiz do projeto — design system portável no formato Open Design. Contém especificação completa de cores, tipografia, componentes, layouts e breakpoints.

### Integração
```
Campaign Autopilot Agents
    ↓ (dados de campanha)
Product Forge
    ├── DesignSystem (DESIGN.md)
    ├── ArtifactGenerator
    └── Generators (LandingPage, Dashboard, Email, Presentation)
    ↓
Output/ → HTML, CSS
```

### Uso Rápido
```python
from campaign_autopilot.product_forge import LandingPageGenerator

gen = LandingPageGenerator()
path = gen.generate_affiliate_landing(
    product_name="Curso X",
    product_description="Descrição",
    affiliate_link="https://hotmart.com/...",
    output_dir="output",
)
```

### Documentação
- `docs/PRODUCT_FORGE.md` — Arquitetura completa
- `DESIGN.md` — Design system (Open Design format)
- `skills/product_forge.md` — Guia rápido de uso

### Próximos Passos
1. Integrar agentes do Campaign Autopilot com geração automática de landing pages
2. Workflow que gera landing page + email + social card em pipeline única
3. Template marketplace


## Money Loop — 24/7 Revenue Generation

### Arquitetura de Receita

```
┌──────────────────────────────────────────────────────────────┐
│                    MONEY LOOP (24/7)                          │
│  scripts/money_loop.py — Ciclo contínuo de geração de receita│
├──────────────────────────────────────────────────────────────┤
│  1. Pesquisa SEO (Free LLM Providers)                         │
│  2. Ofertas de afiliado (Kiwify, Eduzz, Hotmart, Amazon)      │
│  3. Landing pages (Product Forge)                              │
│  4. Emails de nutrição (Product Forge)                         │
│  5. Métricas e tracking (SQLite WAL)                           │
│  6. Repetir a cada N horas                                     │
└──────────────────────────────────────────────────────────────┘
```

### Como Executar

```bash
# Modo contínuo 24/7
nohup python scripts/money_loop.py > .state/money_loop.log 2>&1 &

# Modo systemd (auto-start no boot)
sudo systemctl enable money-loop.service
sudo systemctl start money-loop.service

# Apenas um ciclo
python scripts/money_loop.py --once

# Ver estatísticas acumuladas
python scripts/money_loop.py --stats
```

### Resultado do Teste (2026-06-24)

| Métrica | Valor |
|---------|-------|
| Keywords encontradas | 4 |
| Ofertas de afiliado | 2 |
| Landing pages geradas | 2 |
| Emails gerados | 2 |
| Cliques estimados/mês | ~400 |
| Receita estimada/mês | R$ 985.52 |
| Duração do ciclo | 240ms |

### Projeção de Ganhos (12 meses)

Com 1 nicho, 1 artigo/dia, visitas por artigo e conversão realista de afiliados:

| Mês | Artigos | Visitas | Receita Afiliados | AdSense | Email | Produtos | **Total** |
|-----|---------|---------|-------------------|---------|-------|----------|-----------|
| 1 | 30 | 900 | R$ 48 | R$ 3 | R$ 0 | R$ 0 | **R$ 51** |
| 3 | 90 | 6.750 | R$ 364 | R$ 20 | R$ 9 | R$ 0 | **R$ 393** |
| 6 | 180 | 26.117 | R$ 1.410 | R$ 78 | R$ 73 | R$ 6 | **R$ 1.567** |
| 12 | 360 | 79.941 | R$ 4.316 | R$ 240 | R$ 319 | R$ 55 | **R$ 4.930** |

### Para Máxima Receita Imediata

1. Preencha os IDs de afiliado no `.env`:
   - `KIWIFY_AFFILIATE_ID`, `EDUZZ_AFFILIATE_ID`, `MONETIZZE_AFFILIATE_ID`
   - `HOTMART_CLIENT_ID`, `HOTMART_CLIENT_SECRET`
   - `AMAZON_ASSOCIATES_TAG`
2. Configure `WP_URL`, `WP_USER`, `WP_PASSWORD` para WordPress real
3. Execute `python scripts/money_loop.py` em modo contínuo
4. Aumente o número de nichos com `--interval 12` (12 horas)
