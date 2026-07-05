# 🤖 Agents Reference — Campaign Autopilot v5.2.3

> Catálogo completo dos **128+ agentes especialistas** do ecossistema Campaign Autopilot.
> Atualizado em 2026-06-25.

---

## Índice

1. [Core Cycle (7)](#1-core-cycle)
2. [SEO & Research (11)](#2-seo--research)
3. [Content & Creative (14)](#3-content--creative)
4. [Media Production (7)](#4-media-production)
5. [Publishing (5)](#5-publishing)
6. [Social Media (19)](#6-social-media)
7. [Revenue & Affiliates (18)](#7-revenue--affiliates)
8. [Paid Traffic (8)](#8-paid-traffic)
9. [Intelligence — 2ª Ordem (9)](#9-intelligence--2ª-ordem)
10. [Intelligence — 3ª Ordem (5)](#10-intelligence--3ª-ordem)
11. [Compliance & Risk (6)](#11-compliance--risk)
12. [News Agents (3)](#12-news-agents)
13. [Money Agents (4)](#13-money-agents)
14. [Meta Agents (5)](#14-meta-agents)
15. [UI & Design (2)](#15-ui--design)
16. [Outros (4)](#16-outros)

---

## 1. Core Cycle

Agentes fundamentais que formam o ciclo de execução principal.

| Agente | Step ID | Dependências | Função |
|--------|---------|--------------|--------|
| `CampaignOrchestrator` | — | Todos | Orquestrador central do sistema |
| `AgentBase` | — | — | ABC base para todos os agentes |
| `AnalyticsAgent` | `analytics` | Nenhuma | Deriva sinais de performance |
| `ComplianceAgent` | `compliance` | Nenhuma | Valida conteúdo contra regras |
| `MemoryLookupAgent` | `memory_lookup` | Nenhuma | Busca lições de ciclos anteriores |
| `OptimizationAgent` | `optimization` | analytics, compliance, memory_lookup | Síntese em ações priorizadas |
| `ExecutionPlanningAgent` | `execution_planning` | optimization | Converte em ExecutionPlan |

## 2. SEO & Research

Agentes de pesquisa e otimização para mecanismos de busca.

| Agente | Step ID | Função |
|--------|---------|--------|
| `SEOResearchAgent` | `seo_research` | Pesquisa palavras-chave |
| `SEOScraperAgent` | `seo_scraper` | Scraping de SERP do Google |
| `RankTrackerAgent` | `rank_tracker` | Simula trackeamento de rank |
| `CompetitorAnalysisAgent` | `competitor_analysis` | Análise competitiva |
| `ContentResearchAgent` | — | Pesquisa de conteúdo e tendências |
| `SEOContentWriterAgent` | — | Escrita de conteúdo SEO |
| `EEATValidatorAgent` | — | Validação E-E-A-T |
| `SEOTechnicalAgent` | — | SEO técnico (meta tags, schema) |
| `SEOMultimediaAgent` | — | Otimização de mídia para SEO |
| `InternalLinkerAgent` | — | Estratégia de links internos |
| `SitePublisherAgent` | — | Publicação com formatação SEO |

## 3. Content & Creative

Agentes de planejamento, geração e otimização de conteúdo.

| Agente | Step ID | Função |
|--------|---------|--------|
| `ContentPlannerAgent` | `content_planner` | Combina SEO com ofertas |
| `ContentGeneratorAgent` | `content_generator` | Gera conteúdo completo |
| `ContentOptimizerAgent` | `content_optimizer` | Otimiza conteúdo existente |
| `ContentRepurposerAgent` | `content_repurposer` | Reproposita entre formatos |
| `ContentExcellenceAgent` | — | Padrão de excelência |
| `StorytellingSpecialistAgent` | — | Estruturas narrativas |
| `PsychologySpecialistAgent` | — | Psicologia aplicada |
| `NeuromarketingSpecialistAgent` | — | Neuromarketing |
| `CreativeEngine` | — | Motor criativo |
| `NicheGenesisAgent` | — | Geração de novos nichos |
| `NovelValueGenerator` | — | Propostas de valor únicas |
| `StoryboardAgent` | — | Storyboards multimídia |
| `TemporalEngineAgent` | — | Planejamento temporal |
| `FreeContentGenerator` | — | Geração de conteúdo gratuita (stdlib) |

## 4. Media Production
### 4.8 — CTO Media Prompt Agent
`cto_media_prompt_agent.py`
| Campo | Valor |
|-------|-------|
| Descrição | Aplica meta-prompt CTO Executive Director v3 para gerar prompts de imagem, áudio e vídeo |
| Input | `niche`, `keyword`, `script_text` |
| Output | Prompts CTO validados (imagem + áudio + vídeo) |
| Integração | `prompt_architect.py` — 9 nichos, 52 formatos, 3 tipos de mídia |
| Quality | Passa pelo OutputCritic (≥85/100) |



Agentes de produção de mídia visual e áudio.

| Agente | Função |
|--------|--------|
| `CinematicImageAgent` | Imagens cinematográficas (Pillow) |
| `CinematicVideoAgent` | Vídeos com efeitos (MoviePy) |
| `AudioProductionAgent` | Áudio com TTS e composição |
| `MediaPipelineAgent` | Orquestração do pipeline de mídia |
| `FreeImageGeneratorAgent` | Imagens gratuitas (Pollinations + Pillow) |
| `FreeVideoProducerAgent` | Vídeos gratuitos (MoviePy) |
| `FreeAudioProducerAgent` | Áudio gratuito (gTTS + edge-tts) |

## 5. Publishing

Agentes de publicação e deploy.

| Agente | Função |
|--------|--------|
| `PublisherAgent` | Cronograma de publicação |
| `WordPressPublisherAgent` | Publicação no WordPress |
| `BulkPublisherAgent` | Publicação em massa |
| `SiteDeployAgent` | Deploy do site estático |
| `EmailMarketingAgent` | Sequências de email |

## 6. Social Media

Agentes de distribuição em redes sociais.

| Agente | Função |
|--------|--------|
| `YouTubeMarketingAgent` | Scripts e estratégia YouTube |
| `PinterestMarketingAgent` | Pins e boards |
| `WhatsAppMarketingAgent` | Mensagens e listas |
| `InstagramMarketingAgent` | Conteúdo visual |
| `TikTokMarketingAgent` | Vídeos curtos |
| `TwitterMarketingAgent` | Threads e posts |
| `LeadCaptureAgent` | Iscas digitais |
| `SocialPublisherAgent` | Publicação multi-plataforma |

(Total: 19 agentes de redes sociais)

## 7. Revenue & Affiliates

Agentes de receita e marketing de afiliados.

| Agente | Função |
|--------|--------|
| `OfferLookupAgent` | Busca ofertas de afiliados |
| `RevenueMonitorAgent` | Projeções de receita |
| `PlatformAffiliateAgent` | Configuração de redes |
| `GenericAffiliateNetwork` | Rede genérica de afiliados |
| `CPAAgent` | Ofertas CPA |
| `AdSenseAgent` | Google AdSense |
| `RevenueProtocolAgent` | Protocolos de monetização |
| `RevenueMemory` | Armazenamento de eventos |
| `RevenueOrchestrator` | Coordenação entre fontes |
| `DigitalProductsAgent` | Catálogo de produtos digitais |
| `AllPlatformsSetupAgent` | Setup automatizado |
| `RevenueBranchAgent` | Step para cada fonte (13 instâncias) |

### Hotmart Agents (6)

| Agente | Função |
|--------|--------|
| `ProductMatcherAgent` | Matching de produtos |
| `ProductResearcherAgent` | Pesquisa de produtos |
| `MarketplacesCollectorAgent` | Coleta de dados |
| `LinkManagerAgent` | Gestão de links |
| `LinkValidatorAgent` | Validação de links |
| `ConfigUpdaterAgent` | Atualização de configs |

## 8. Paid Traffic

Agentes de tráfego pago (requerem orçamento).

| Agente | Função |
|--------|--------|
| `TrafficManagerAgent` | Gestão de campanhas |
| `AdOptimizerAgent` | Otimização de anúncios |
| `BudgetAllocatorAgent` | Alocação de orçamento |
| `ConversionTrackerAgent` | Rastreamento de conversões |
| `AudienceBuilderAgent` | Construção de audiências |
| `RetargetingAgent` | Remarketing |
| `ROIAnalyzerAgent` | Análise de ROI |
| `BidManagerAgent` | Gestão de lances |

## 9. Intelligence — 2ª Ordem
### 9.10 — CTO Media Prompt Architect (Módulo)
`prompt_architect.py` (612 linhas)
| Campo | Valor |
|-------|-------|
| Descrição | Implementa PHASE 0-5 do meta-prompt CTO para prompts cinematográficos validados |
| Nichos | 9 nichos mapeados com conceitos visuais, moods, paletas, áudio e transições |
| Formatos | blog_featured, youtube_thumbnail, pinterest_pin, instagram_post, social_card |
| Providers | Pollinations, gTTS, MoviePy |
| Qualidade | Revisão epistemológica antes da saída |
| Dependências | stdlib-only (Ponytail) |



Agentes de meta-cognição e governança.

| Agente | Função |
|--------|--------|
| `MetaOrchestratorAgent` | Auto-modifica workflows |
| `StrategyEvolutionAgent` | Planejamento multi-ciclo |
| `AgentPerformanceMonitor` | Analytics de agentes |
| `SelfHealingAgent` | Detecção e reparo |
| `CircuitBreaker` | Resiliência progressiva |
| `EvolutionEngine` | Aplica mudanças estruturais |
| `AgentFactory` | Cria agentes novos |
| `ExternalMonitorAgent` | Mudanças em plataformas |
| `GovernanceAgent` | Consolida 7 delegates (QA, risk, rollback, perf, resource, AB) |

## 10. Intelligence — 3ª Ordem

Agentes de auto-transcendência.

| Agente | Função |
|--------|--------|
| `EpistemicAgent` | O que o sistema sabe/não sabe |
| `ObserverFusionAgent` | Múltiplas perspectivas |
| `ValueEvolutionAgent` | Evolução de valores |
| `RecursiveObserverAgent` | Meta-meta-cognição |
| `ThirdOrderOrchestrator` | Orquestra terceira ordem |

## 11. Compliance & Risk

Agentes de conformidade e gestão de risco.

| Agente | Função |
|--------|--------|
| `PlatformComplianceAgent` | Regras de cada plataforma |
| `YouTubeRulesAgent` | Regras do YouTube |
| `InstagramRulesAgent` | Regras do Instagram |
| `RiskManagementAgent` | Gestão de riscos |
| `QualityAssuranceAgent` | Validação de qualidade |
| `RollbackManagerAgent` | Rollback de mudanças |

## 12. News Agents

Agentes especializados em conteúdo de notícias.

| Agente | Função |
|--------|--------|
| `ContentResearchAgent` | Pesquisa de pautas |
| `SEOContentWriterAgent` | Escrita otimizada |
| `EEATValidatorAgent` | Validação de autoridade |

## 13. Money Agents

Agentes de gestão financeira e revenue.

| Agente | Função |
|--------|--------|
| `RevenueBranchAgent` | Executa uma fonte de renda específica |
| `RevenueAggregatorAgent` | Agrega resultados de todas as fontes |
| `CompoundingEngine` | Engine de compounding |
| `PortfolioOptimizer` | Otimização de portfólio |

## 14. Meta Agents

Agentes de meta-orquestração e evolução.

| Agente | Função |
|--------|--------|
| `AgentFactory` | Criação de agentes |
| `CompoundingEngine` | Compounding de resultados |
| `CrossPollinationHub` | Polinização cruzada entre nichos |
| `KnowledgeSynthesisBridge` | Ponte para KnowledgeSynthesisEngine |
| `OpportunityDetector` | Detecção de oportunidades |

## 15. UI & Design

Agentes de geração visual (Product Forge / Open Design).

| Agente | Função |
|--------|--------|
| `UIDesignAgent` | Geração de landing pages, emails, dashboards |
| `SiteDeployAgent` | Deploy do site gerado |

## 16. Outros

| Agente | Função |
|--------|--------|
| `PerformanceAnalyticsAgent` | Análise temporal |
| `ResourceManagerAgent` | Alocação de recursos |
| `ABTestingAgent` | Testes A/B |
| `ExternalMonitorAgent` | Monitoramento externo |

---

---

## UI/UX Design Agents (21st.dev Style)

Novos agentes de componentes UI responsivos:

| Agent | Arquivo | Função |
|-------|---------|--------|
| UIHeroAgent | `agents/ui_hero_agent.py` | Hero sections com badge, CTA, social proof |
| UIPricingAgent | `agents/ui_pricing_agent.py` | Pricing tables com 3 planos, destaque, features |
| UIFAQAgent | `agents/ui_faq_agent.py` | FAQ accordion com schema.org, JS puro |
| UITestimonialAgent | `agents/ui_testimonial_agent.py` | Testimonial cards com estrelas, avatar |
| UIFullPageAgent | `agents/ui_full_page_agent.py` | Landing page completa componível |
| UIComponentDesignAgent | `agents/ui_component_design.py` | Component-based landing page generator |

### Quality Infrastructure

| Componente | Arquivo | Função |
|-----------|---------|--------|
| OutputCritic | `quality_layers.py` | 8 critérios de avaliação (threshold 85/100) |
| DebateOrchestrator | `quality_layers.py` | Multi-agent debate + synthesis |
| BenchmarkDB | `quality_layers.py` | SQLite approved-only storage |
| CampaignKnowledge | `quality_layers.py` | FTS5 retrieval para RAG |
| TruthAgent | `quality_layers.py` | Hallucination detection |
| RiskAgent | `quality_layers.py` | Strategic risk assessment |
| ConsistencyAgent | `quality_layers.py` | Brand alignment check |
| RAGEngine | `quality_layers.py` | Retrieve → Reason → Generate |
| ELORanking | `quality_layers.py` | Skill competition rankings |
| AutoRegenerator | `auto_regenerate.py` | 3 attempts with critic feedback |
| UIDesignMemory | `ui_design_memory.py` | SQLite tracking for UI components |

## Product Forge — Open Design Integration

Módulo de geração visual em `src/campaign_autopilot/product_forge/`:

| Componente | Arquivo | Função |
|------------|---------|--------|
| Design System | `design_system.py` | Sistema de design Open Design compatível |
| Landing Page Generator | `landing_page_generator.py` | Landing pages responsivas |
| Dashboard Generator | `dashboard_generator.py` | Dashboards de campanha |
| Email Template Generator | `email_template_generator.py` | Templates de email |
| Presentation Generator | `presentation_generator.py` | Slides HTML |
| Artifact Generator | `artifact_generator.py` | Motor genérico |
| Color Palette | `color_palette.py` | 59 tokens de cor |

---

*Parte da documentação do Campaign Autopilot v5.2.2 — Atualizado em 2026-06-25*
