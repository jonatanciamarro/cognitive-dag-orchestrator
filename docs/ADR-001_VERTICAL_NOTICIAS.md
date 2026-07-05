# ADR-001: Vertical de Notícias — Site Jornalístico com Monetização AdSense

> **Status:** Proposed
> **Data:** 2026-06-22
> **Autor:** Chief Intelligence Architect — Lyzer Labs
> **Domínio:** Expansão do Campaign Autopilot para vertical editorial
> **Modelo de Referência:** The New York Times (estrutura editorial)

---

## Sumário

1. [Contexto](#1-contexto)
2. [Decisão](#2-decisão)
3. [Consequências](#3-consequências)
4. [Arquitetura Detalhada](#4-arquitetura-detalhada)
5. [Modelo NYT — Análise Estrutural](#5-modelo-nyt)
6. [Pipeline Editorial](#6-pipeline-editorial)
7. [Monetização AdSense](#7-monetização-adsense)
8. [Ontologia de Domínio](#8-ontologia-de-domínio)
9. [Agentes do Sistema](#9-agentes-do-sistema)
10. [Workflow DAG](#10-workflow-dag)
11. [Métricas e KPIs](#11-métricas-e-kpis)
12. [Riscos e Mitigações](#12-riscos-e-mitigações)
13. [Roadmap de Implementação](#13-roadmap-de-implementação)
14. [Perguntas em Aberto](#14-perguntas-em-aberto)

---

## 1. Contexto

### 1.1 Situação Atual

O Campaign Autopilot é um sistema cognitivo de marketing com 122 agentes, 30 workflows, focado em **marketing de afiliados** (Hotmart, Amazon, CPA) com tráfego orgânico. Opera com:

- 13 provedores LLM gratuitos com failover automático
- Motor de workflow DAG com execução paralela
- Memória persistente (SQLite) + Memória semântica (grafo de conhecimento)
- Motor de síntese que aprende com ciclos anteriores
- Geração de conteúdo, imagens, vídeos, áudio (tudo gratuito)
- Publicação em WordPress, redes sociais, email

### 1.2 Oportunidade

Adicionar uma **vertical de notícias** com:

- Site jornalístico nos moldes do NYT (seções, editorias, manchetes)
- Monetização via **Google AdSense** (CPM, CPC)
- Tráfego 100% orgânico via SEO jornalístico
- Conteúdo evergreen + notícias quentes
- Sem custo de tráfego pago

### 1.3 Fricções e Riscos Identificados

| Fricção | Impacto | Mitigação |
|---------|---------|-----------|
| Google AdSense pode rejeitar conteúdo gerado por IA | ⚠️ Alto | Fact-checking, fonte citada, curadoria editorial |
| E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) | ⚠️ Alto | Perfis de autor, biografias, citações de fontes |
| Conteúdo duplicado ou thin content | ⚠️ Médio | Originalidade, profundidade, revisão humana simulada |
| Misturar tom promocional (afiliados) com jornalístico | ⚠️ Médio | Domínios separados, prompts diferentes |
| NYT tem estrutura complexa (mais de 20 seções) | 🔷 Baixo | Começar com 5 seções, expandir gradualmente |

---

## 2. Decisão

### 2.1 Opções Consideradas

| Opção | Vantagens | Desvantagens | Veredito |
|-------|-----------|--------------|----------|
| **A — Projeto separado** (novo repo) | Isolamento total | Perde infra LLM, workflow, memória | ❌ |
| **B — Mesmo código, mesmo domínio** | Simplicidade | Conflito AdSense × afiliados, penalidade Google | ❌ |
| **C — Mesma plataforma, domínio separado** (escolhida) | Compartilha cognição, isola compliance | Complexidade moderada de configuração | ✅ |
| **D — Como módulo opcional (plugin)** | Desacoplamento máximo | Sobrecarga de engenharia | 🔷 Futuro |

### 2.2 Decisão Final

> **Opção C** — Adicionar vertical de notícias como **segunda vertical** dentro da mesma arquitetura cognitiva, com:
> - **Domínio próprio** (ex: `news.lyzer.com` ou `seunoticias.com`)
> - **Diretório de agentes separado** (`agents/news/`)
> - **Workflow próprio** (`workflows/news_workflow.json`)
> - **Configuração isolada** (`configs/news_cycle.json`)
> - **Infra compartilhada**: LLM providers, memória, síntese, motor de workflow

### 2.3 Princípios da Decisão

1. **Isolamento de Compliance** — Regras do AdSense não se misturam com regras de afiliados
2. **Compartilhamento Cognitivo** — Memory + Synthesis aprendem com ambos os domínios
3. **Separação de Domínio** — Google não pode associar conteúdo promocional ao jornalístico
4. **Aproveitamento de Infra** — 13 LLMs com failover, motor DAG, SQLite, tudo reusado

---

## 3. Consequências

### 3.1 Positivas ✅

| Consequência | Detalhe |
|-------------|---------|
| Receita diversificada | Afiliados (CPA) + AdSense (CPM/CPC) |
| Infra compartilhada | Zero custo adicional de LLM/infraestrutura |
| Aprendizado cruzado | Síntese de conhecimento entre domínios |
| Sinergia de conteúdo | Artigos de notícias podem linkar para reviews de afiliados (com cuidado) |
| Time-to-market rápido | Reuso de 90% do código existente |

### 3.2 Negativas ❌

| Consequência | Detalhe |
|-------------|---------|
| Complexidade de configuração | Duas verticais com regras diferentes |
| Risco de contaminação cross-domain | Um erro no prompt pode misturar tons |
| Manutenção de compliance duplicada | Monitorar regras do AdSense + regras de afiliados |
| Conteúdo pode canibalizar SEO | Se estiver no mesmo domínio (evitado com domínios separados) |

### 3.3 Neutras 🔷

| Consequência | Detalhe |
|-------------|---------|
| Mais agentes para gerenciar | ~12 novos agentes de notícias |
| Mais workflows | 1 novo workflow principal + variações |
| Mais skills | 5+ novos documentos de skill |

---

## 4. Arquitetura Detalhada

### 4.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    COGNITIVE LAYER (Shared)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Memory  │  │ Semantic │  │ Synthesis│  │  Policy  │   │
│  │  Store   │  │  Memory  │  │  Engine  │  │  Engine  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    INFRA LAYER (Shared)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 13 LLM   │  │ Workflow │  │  SQLite  │  │   CLI    │   │
│  │Providers │  │  Engine  │  │   WAL    │  │ Daemon   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────┬──────────────────────────────────────┐
│   VERTICAL AFFILIATE │   VERTICAL NEWS (NOVO)              │
│   (existente)        │                                      │
│                      │                                      │
│  agents/             │  agents/news/                        │
│  ├── seo_research    │  ├── news_editor                    │
│  ├── content_gen     │  ├── news_reporter                  │
│  ├── email_mkt       │  ├── news_headline_writer           │
│  ├── social_media    │  ├── news_fact_checker              │
│  ├── affiliate       │  ├── news_seo_specialist            │
│  └── ... (62 total)  │  ├── news_nytimes_modeler           │
│                      │  ├── news_trend_scanner             │
│  workflows/          │  ├── news_evergreen_scorer          │
│  ├── money_workflow  │  ├── news_adsense_compliance        │
│  ├── organic_cycle   │  ├── news_photographer              │
│  └── ...             │  ├── news_newsletter_writer         │
│                      │  ├── news_social_teaser             │
│  site (domínio A)    │  └── news_publisher                 │
│                      │                                      │
│  Monetização:        │  workflows/                          │
│  Hotmart + Amazon    │  ├── news_workflow.json             │
│  + CPA               │  ├── news_evergreen.json            │
│                      │  └── news_trending.json             │
│                      │                                      │
│                      │  site (domínio B — NOVO)             │
│                      │  themes/nytimes/                     │
│                      │                                      │
│                      │  Monetização:                        │
│                      │  Google AdSense                      │
└──────────────────────┴──────────────────────────────────────┘
```

### 4.2 Estrutura de Diretórios (Adições)

```
src/campaign_autopilot/
├── agents/
│   └── news/                          ← NOVO
│       ├── __init__.py
│       ├── base.py                    ← NewsAgentBase (extends AgentBase)
│       ├── news_editor.py
│       ├── news_reporter.py
│       ├── news_headline_writer.py
│       ├── news_fact_checker.py
│       ├── news_seo_specialist.py
│       ├── news_nytimes_modeler.py
│       ├── news_trend_scanner.py
│       ├── news_evergreen_scorer.py
│       ├── news_adsense_compliance.py
│       ├── news_photographer.py
│       ├── news_newsletter_writer.py
│       ├── news_social_teaser.py
│       └── news_publisher.py

skills/news/                           ← NOVO
├── nytimes_architecture.md
├── adsense_compliance.md
├── journalistic_writing.md
├── news_seo.md
└── google_eeat.md

workflows/                             ← NOVO
├── news_workflow.json
├── news_evergreen.json
└── news_trending.json

configs/                               ← NOVO
└── news_cycle.json

site_generator/
├── themes/
│   └── nytimes/                       ← NOVO
│       ├── template.html
│       ├── article.html
│       ├── section.html
│       ├── homepage.html
│       ├── css/nytimes.css
│       ├── js/nytimes.js
│       └── assets/

docs/                                  ← NOVO
├── ADR-001_VERTICAL_NOTICIAS.md       (este documento)
└── NEWS_PIPELINE.md                   ← Detalhamento técnico
```

### 4.3 Compartilhamento vs Isolamento

| Componente | Estratégia | Justificativa |
|-----------|------------|---------------|
| free_llm_providers.py | ✅ Compartilhado | 13 provedores com failover servem ambos |
| workflow.py (DAG engine) | ✅ Compartilhado | Motor genérico, workflows separados |
| MemoryStore | ✅ Compartilhado | Memória enriquece ambos os domínios |
| SemanticMemoryStore | ✅ Compartilhado | Grafos de conhecimento se alimentam |
| KnowledgeSynthesisEngine | ✅ Compartilhado | Síntese cross-domínio gera insights |
| PolicyEngine | 🔷 Namespace separado | Regras diferentes por vertical |
| GoalRegistry | 🔷 Namespace separado | Metas diferentes por vertical |
| Logging | ✅ Compartilhado | StructuredLogger com tag de vertical |
| .env | ✅ Compartilhado | Chaves LLM servem ambos |
| Site Generator | 🔷 Tema separado | Mesmo gerador, template diferente |
| Dashboard | 🔷 Visão unificada | Streamlit com abas por vertical |

---

## 5. Modelo NYT — Análise Estrutural

### 5.1 Seções do NYT Mapeadas

Aplicando o modelo do NYT ao contexto brasileiro com 5 fases de rollout:

| Fase | Seção | Exemplo de Conteúdo | Prioridade |
|------|-------|---------------------|------------|
| 🚀 **Fase 1** | Tecnologia | Reviews, guias, tendências tech | 🥇 |
| 🚀 **Fase 1** | Negócios | Finanças, empreendedorismo, mercado | 🥇 |
| 🚀 **Fase 1** | Saúde/Bem-estar | Dicas, pesquisas, guias | 🥇 |
| 🚀 **Fase 2** | Carreira | Mercado de trabalho, desenvolvimento | 🥈 |
| 🚀 **Fase 2** | Educação | Cursos, dicas de estudo, carreira acadêmica | 🥈 |
| 🚀 **Fase 3** | Lifestyle | Casa, viagem, cultura, comida | 🥉 |
| 🚀 **Fase 3** | Ciência | Descobertas, explicações científicas | 🥉 |
| 🚀 **Fase 4** | Política | Análise política (cuidado: polarização) | 🔷 |
| 🚀 **Fase 4** | Opinião | Artigos de opinião (cuidado: responsabilidade) | 🔷 |
| 🚀 **Fase 5** | Esportes | Cobertura esportiva | 🔷 |

### 5.2 Padrões Editoriais do NYT para Adotar

| Padrão NYT | Implementação no Sistema |
|-----------|------------------------|
| **Lead (Lide)** — Primeiro parágrafo responde: O quê, Quem, Quando, Onde, Por quê, Como | Template de artigo com lide obrigatório |
| **Pirâmide Invertida** — Informação mais importante primeiro | Estrutura de artigo com seções obrigatórias |
| **Manchete + Subheading** — Título principal + subtítulo descritivo | Gerador de headline + dek |
| **Créditos de Autor** — Byline com biografia | Perfil de autor gerado (humano simulado) |
| **Data de Publicação** — Timestamp visível | Metadados de publicação |
| **Seções e Tags** — Categorização hierárquica | Tags + categorias no frontmatter |
| **Artigo Relacionado** — Links internos no final | Agente de linking interno |
| **Fact Check** — Verificação de informações | Agente fact_checker obrigatório |
| **Citações e Fontes** — "Segundo [fonte]" | Template com campo de fontes |
| **Imagem Destacada** — Foto/arte no topo | Agente news_photographer gera imagem |

### 5.3 O que NÃO Copiar do NYT (por enquanto)

- Paywall (nosso modelo é AdSense, não assinatura)
- Cobertura ao vivo (breaking news em tempo real)
- Investigação jornalística profunda
- Conteúdo opinativo (risco de responsabilidade)
- Cobertura política polarizante

---

## 6. Pipeline Editorial

### 6.1 Ciclo de Vida do Artigo

```
TREND SCAN → PAUTA → REDAÇÃO → REVISÃO → SEO → COMPLIANCE → PUBLICAÇÃO → DISTRIBUIÇÃO
    │          │         │         │        │        │            │            │
    ▼          ▼         ▼         ▼        ▼        ▼            ▼            ▼
 trends    editor    reporter  fact-    seo-     adsense-     publisher    social-
 scanner   aprova    escreve   checker  writer   compliance               teaser
                                                                          email
```

### 6.2 Tipos de Artigo

| Tipo | Frequência | Tamanho | SEO | Evergreen |
|------|-----------|---------|-----|-----------|
| **Guia Completo** | Semanal | 2000-3000 palavras | 🥇 Máximo | ✅ Sim |
| **Notícia/Atualidade** | Diário | 500-800 palavras | 🥈 Médio | ❌ Não |
| **Tutorial/How-to** | 2x/semana | 1200-2000 palavras | 🥇 Máximo | ✅ Sim |
| **Lista** | 2x/semana | 800-1200 palavras | 🥇 Alto | ✅ Sim |
| **Opinião/Análise** | Semanal | 1000-1500 palavras | 🥈 Médio | 🔷 Depende |
| **Entrevista** | Quinzenal | 1500-2500 palavras | 🥈 Médio | 🔷 Depende |
| **Newsletter** | Diário | 300-500 palavras | 🥉 Baixo | ❌ Não |

### 6.3 Critérios de Aprovação (Editor Agent)

Cada artigo deve passar por 5 gates antes de publicar:

| Gate | Critério | Responsável |
|------|----------|-------------|
| G1 | Tema tem potencial de busca? (volume de pesquisa > 100/mês) | trend_scanner |
| G2 | Conteúdo é original? (similaridade < 30% com top 5 resultados) | reporter + checker |
| G3 | Fatos verificados? (mínimo 3 fontes citadas) | fact_checker |
| G4 | SEO otimizado? (score > 80/100 em critérios on-page) | seo_specialist |
| G5 | AdSense compliant? (sem violações de política) | adsense_compliance |

---

## 7. Monetização AdSense

### 7.1 Requisitos do Google AdSense

| Requisito | Implementação |
|-----------|--------------|
| Conteúdo original e de valor | Agente fact_checker + plágio detector |
| Navegação clara | Template NYT com menu, breadcrumbs, busca |
| Política de privacidade | Página gerada automaticamente |
| Contato/Sobre | Página "Sobre" + "Contato" com email |
| Design responsivo | CSS mobile-first (NYT theme) |
| Velocidade de carregamento | Site estático (HTML puro, sem JS pesado) |
| Domínio próprio | Domínio .com.br próprio |
| HTTPS | Cloudflare Pages (grátis) ou GitHub Pages |
| Conteúdo atualizado | Ciclo diário de publicação |
| Tráfego mínimo | SEO agressivo desde o primeiro artigo |

### 7.2 Estratégia de Otimização de RPM

| Tática | Ganho Estimado | Implementação |
|--------|---------------|---------------|
| Artigos longos (2000+ palavras) | +40% RPM | Guias completos semanais |
| Palavras-chave de alto CPC | +60% RPM | Pesquisar "seguro de vida", "cartão de crédito", "consórcio" |
| Conteúdo evergreen | +30% RPM acumulativo | Recycling de artigos antigos |
| Links internos | +15% RPM | Agente de linking automático |
| Imagens otimizadas | +10% RPM | WebP, alt text, lazy loading |
| Velocidade de página | +20% RPM | Site estático puro |
| Densidade de anúncios | +25% RPM | Teste A/B de posicionamento |

### 7.3 Bloqueios Comuns do AdSense e Prevenção

| Bloqueio | Prevenção |
|----------|-----------|
| "Conteúdo insuficiente" | Artigos com mínimo 500 palavras |
| "Conteúdo gerado automaticamente" | Revisão obrigatória (humano simulada) + fontes |
| "Direitos autorais" | Todo conteúdo original, imagens geradas ou domínio público |
| "Conteúdo enganoso" | Fact-checking em cada artigo |
| "Experiência do usuário pobre" | Mobile-first, carregamento rápido |
| "Conteúdo adulto/violento" | Filtro de tópicos proibidos |
| "Conteúdo médico sem qualificação" | Disclaimer médico em artigos de saúde |

---

## 8. Ontologia de Domínio

### 8.1 Conceitos

```
Domínio News
├── Artigo
│   ├── tipo: {guia, noticia, tutorial, lista, opiniao, entrevista, newsletter}
│   ├── status: {pauta, redacao, revisao, seo, compliance, publicado, arquivado}
│   ├── seção: {tecnologia, negocios, saude, carreira, educacao, lifestyle, ciencia}
│   ├── autoria: string (nome do autor gerado)
│   ├── fontes: list[string] (mínimo 3 para notícias)
│   └── palavras_chave: list[string] (extraídas do SEO)
│
├── Seção
│   ├── nome: string
│   ├── descricao: string
│   ├── cor_tema: hex
│   └── editor_responsavel: string
│
├── Autor
│   ├── nome: string (seudônimo profissional)
│   ├── biografia: string (gerada, contexto brasileiro)
│   ├── especialidades: list[string]
│   └── foto: path (imagem gerada)
│
├── Pauta
│   ├── tema: string
│   ├── justificativa: string (potencial de busca)
│   ├── aprovada: bool
│   └── data_sugerida: datetime
│
├── Fonte
│   ├── nome: string
│   ├── url: string
│   └── relevancia: {alta, media, baixa}
│
└── Metrica
    ├── visualizacoes: int
    ├── tempo_leitura: float
    ├── rpm: float
    └── compartilhamentos: int
```

### 8.2 Relacionamentos

```
Seção 1──N Artigo
Artigo 1──N Fonte
Artigo 1──1 Autor
Artigo N──N Tag
Seção 1──1 Editor (Agente)
Artigo 1──1 Pauta (origem)
Artigo 1──N ArtigoRelacionado (self-referencial)
```

### 8.3 Entidades no Banco (SQLite)

```sql
-- Nova tabela para artigos de notícias
CREATE TABLE news_articles (
    id TEXT PRIMARY KEY,
    section TEXT NOT NULL,
    article_type TEXT NOT NULL,
    title TEXT NOT NULL,
    dek TEXT,                          -- Subtítulo
    body TEXT NOT NULL,
    author TEXT NOT NULL,
    sources TEXT,                      -- JSON array
    tags TEXT,                         -- JSON array
    keywords TEXT,                     -- JSON array (SEO)
    seo_score REAL DEFAULT 0,
    compliance_status TEXT DEFAULT 'pending',
    status TEXT DEFAULT 'pauta',
    word_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    published_at TEXT,
    updated_at TEXT,
    workflow_run_id TEXT,
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(id)
);

-- Nova tabela para seções
CREATE TABLE news_sections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    theme_color TEXT DEFAULT '#1a1a1a',
    editor_agent TEXT,
    slug TEXT UNIQUE NOT NULL,
    is_active INTEGER DEFAULT 1,
    article_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Nova tabela para autores
CREATE TABLE news_authors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    biography TEXT,
    specialties TEXT,                   -- JSON array
    avatar_path TEXT,
    articles_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
);

-- Nova tabela para pautas
CREATE TABLE news_pautas (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    section TEXT NOT NULL,
    article_type TEXT NOT NULL,
    rationale TEXT,
    search_volume INTEGER DEFAULT 0,
    approved INTEGER DEFAULT 0,
    suggested_date TEXT,
    created_at TEXT NOT NULL,
    approved_at TEXT
);
```

---

## 9. Agentes do Sistema

### 9.1 Catálogo de Agentes

| # | Agente | Classe | Função | LLM Calls | Gatilho |
|---|--------|--------|--------|-----------|---------|
| 1 | **Editor Chefe** | `NewsEditorAgent` | Define pauta do dia, aprova/rejeita temas | 2-3 | Início do ciclo |
| 2 | **Apurador** | `NewsReporterAgent` | Pesquisa, redige artigo completo | 3-5 | Pauta aprovada |
| 3 | **Mancheteiro** | `NewsHeadlineWriterAgent` | Gera manchete + dek + variações para teste A/B | 2 | Artigo redigido |
| 4 | **Verificador** | `NewsFactCheckerAgent` | Verifica afirmações, sugere fontes | 2-3 | Artigo redigido |
| 5 | **Especialista SEO** | `NewsSEOSpecialistAgent` | Otimiza on-page, sugere palavras-chave | 2 | Artigo verificado |
| 6 | **Modelador NYT** | `NewsNYTModelerAgent` | Aplica padrões editoriais NYT | 1 | Artigo otimizado |
| 7 | **Scanner de Trends** | `NewsTrendScannerAgent` | Monitora trending topics, sugere pautas | 2 | Início do ciclo |
| 8 | **Classificador Evergreen** | `NewsEvergreenScorerAgent` | Pontua potencial de longo prazo | 1 | Artigo publicado |
| 9 | **Analista AdSense** | `NewsAdsenseComplianceAgent` | Valida políticas do Google | 1-2 | Antes de publicar |
| 10 | **Fotojornalista** | `NewsPhotographerAgent** | Gera imagem destacada, infográficos | 1 (prompt p/ API) | Antes de publicar |
| 11 | **Redator de Newsletter** | `NewsNewsletterWriterAgent` | Resume artigos em newsletter | 2 | Fim do ciclo |
| 12 | **Social Teaser** | `NewsSocialTeaserAgent** | Gera posts para redes sociais | 1 | Artigo publicado |

### 9.2 Herança (AgentBase)

```python
class NewsAgentBase(AgentBase):
    """Base para todos os agentes de notícias."""

    vertical: str = "news"

    def get_news_prompt(self, template_name: str, **kwargs) -> str:
        """Carrega template de prompt jornalístico."""
        ...

    def validate_compliance(self, text: str) -> bool:
        """Valida se texto segue políticas do AdSense."""
        ...

    def get_author_profile(self) -> dict:
        """Retorna perfil do autor associado."""
        ...

class NewsEditorAgent(NewsAgentBase):
    """Define pauta do dia baseado em trends e calendário editorial."""

    async def run(self, context: CampaignContext) -> AgentResult:
        # 1. Coletar trends do momento
        # 2. Verificar calendário editorial
        # 3. Sugerir 3-5 pautas
        # 4. Cada pauta com justificativa de busca
        # 5. Retornar pauta aprovada
        ...

class NewsReporterAgent(NewsAgentBase):
    """Apura e redige artigo jornalístico completo."""

    async def run(self, context: CampaignContext) -> AgentResult:
        # 1. Receber pauta
        # 2. Pesquisar fontes
        # 3. Redigir artigo com estrutura NYT
        # 4. Incluir lide, corpo, conclusão
        # 5. Citar fontes
        ...
```

### 9.3 Estratégia de Prompts

Cada agente tem um sistema de prompts específico para seu papel. Exemplo do `NewsReporterAgent`:

```
SYSTEM: Você é um repórter de [seção] do [nome do site], um veículo jornalístico
brasileiro. Seu estilo é sóbrio, informativo e preciso, similar ao The New York Times
em português. Você NUNCA usa linguagem promocional, superlativa ou sensacionalista.
Você SEMPRE:
- Começa com um lide que responde: O quê, Quem, Quando, Onde, Por quê, Como
- Cita fontes confiáveis
- Mantém tom neutro e objetivo
- Estrutura em pirâmide invertida
- Termina com conclusão ou perspectiva futura

TÓPICO: {topic}
SEÇÃO: {section}
PALAVRAS-CHAVE: {keywords}
TOM: {tone} (informativo, analítico, explicativo)
EXTENSÃO: {word_count} palavras
FONTES SUGERIDAS: {sources}

Escreva o artigo completo em português brasileiro.
```

---

## 10. Workflow DAG

### 10.1 Workflow Principal (`news_workflow.json`)

```json
{
  "id": "news_daily_cycle",
  "name": "Ciclo Diário de Notícias",
  "description": "Gera, revisa e publica artigos jornalísticos com estilo NYT",
  "vertical": "news",
  "schedule": {
    "type": "interval",
    "hours": 24
  },
  "steps": [
    {
      "id": "trend_scanner",
      "agent": "news.NewsTrendScannerAgent",
      "description": "Escaneia trending topics e oportunidades",
      "dependencies": [],
      "timeout": 300,
      "retry": 2,
      "config": {
        "sections": ["tecnologia", "negocios", "saude", "carreira", "educacao"],
        "max_suggestions": 5
      }
    },
    {
      "id": "editor_approval",
      "agent": "news.NewsEditorAgent",
      "description": "Editor aprova pauta do dia",
      "dependencies": ["trend_scanner"],
      "timeout": 120,
      "config": {
        "max_pautas": 3,
        "approval_threshold": 0.7
      }
    },
    {
      "id": "article_writer",
      "agent": "news.NewsReporterAgent",
      "description": "Redige artigo(s) da pauta aprovada",
      "dependencies": ["editor_approval"],
      "timeout": 600,
      "config": {
        "target_word_count": 1500,
        "min_sources": 3,
        "language": "pt-BR"
      },
      "foreach": "pautas_aprovadas"
    },
    {
      "id": "headline_generator",
      "agent": "news.NewsHeadlineWriterAgent",
      "description": "Gera manchete + dek + variações",
      "dependencies": ["article_writer"],
      "timeout": 120,
      "config": {
        "variations": 5
      }
    },
    {
      "id": "fact_checker",
      "agent": "news.NewsFactCheckerAgent",
      "description": "Verifica fatos e fontes do artigo",
      "dependencies": ["headline_generator"],
      "timeout": 180,
      "config": {
        "require_sources": true,
        "min_confidence": 0.8
      }
    },
    {
      "id": "seo_optimizer",
      "agent": "news.NewsSEOSpecialistAgent",
      "description": "Otimiza artigo para SEO on-page",
      "dependencies": ["fact_checker"],
      "timeout": 120,
      "config": {
        "target_score": 85
      }
    },
    {
      "id": "adsense_compliance",
      "agent": "news.NewsAdsenseComplianceAgent",
      "description": "Valida políticas do Google AdSense",
      "dependencies": ["seo_optimizer"],
      "timeout": 60,
      "config": {
        "strict_mode": true
      }
    },
    {
      "id": "image_generator",
      "agent": "news.NewsPhotographerAgent",
      "description": "Gera imagem destacada e infográficos",
      "dependencies": ["fact_checker"],
      "timeout": 120,
      "parallel": true
    },
    {
      "id": "nytm_modeler",
      "agent": "news.NewsNYTModelerAgent",
      "description": "Aplica padrões editoriais NYT no artigo final",
      "dependencies": ["adsense_compliance", "image_generator"],
      "timeout": 60
    },
    {
      "id": "publisher",
      "agent": "news.NewsPublisherAgent",
      "description": "Publica artigo no site estático",
      "dependencies": ["nytm_modeler"],
      "timeout": 60
    },
    {
      "id": "evergreen_scorer",
      "agent": "news.NewsEvergreenScorerAgent",
      "description": "Classifica artigo para reciclo futuro",
      "dependencies": ["publisher"],
      "timeout": 30
    },
    {
      "id": "newsletter_generator",
      "agent": "news.NewsNewsletterWriterAgent",
      "description": "Gera newsletter do dia",
      "dependencies": ["publisher"],
      "timeout": 120
    },
    {
      "id": "social_teaser",
      "agent": "news.NewsSocialTeaserAgent",
      "description": "Gera teasers para redes sociais",
      "dependencies": ["publisher"],
      "timeout": 60,
      "parallel": true
    },
    {
      "id": "metrics_collector",
      "agent": "metrics.NewsMetricsAgent",
      "description": "Coleta métricas do ciclo",
      "dependencies": [
        "evergreen_scorer",
        "newsletter_generator",
        "social_teaser"
      ],
      "timeout": 30
    }
  ]
}
```

### 10.2 Workflow Evergreen (`news_evergreen.json`)

Para reciclar artigos antigos com alto potencial:

```json
{
  "id": "news_evergreen_refresh",
  "name": "Refresh de Artigos Evergreen",
  "schedule": {
    "type": "weekly",
    "day": "sunday"
  },
  "steps": [
    { "id": "evergreen_selector",   "agent": "news.NewsEvergreenScorerAgent",    "deps": [] },
    { "id": "content_refresher",    "agent": "news.NewsReporterAgent",           "deps": ["evergreen_selector"], "config": {"mode": "refresh"} },
    { "id": "date_updater",         "agent": "news.NewsPublisherAgent",          "deps": ["content_refresher"], "config": {"update_date": true} },
    { "id": "seo_reoptimizer",      "agent": "news.NewsSEOSpecialistAgent",      "deps": ["date_updater"], "config": {"mode": "refresh"} }
  ]
}
```

### 10.3 Workflow Trending (`news_trending.json`)

Para capturar momentos oportunistas:

```json
{
  "id": "news_trending_capture",
  "name": "Captura de Trending Topics",
  "schedule": {
    "type": "interval",
    "hours": 4
  },
  "steps": [
    { "id": "trend_detector",       "agent": "news.NewsTrendScannerAgent",    "deps": [], "config": {"urgency": "high"} },
    { "id": "quick_article",        "agent": "news.NewsReporterAgent",        "deps": ["trend_detector"], "config": {"word_count": 600, "mode": "rapid"} },
    { "id": "express_compliance",   "agent": "news.NewsAdsenseComplianceAgent", "deps": ["quick_article"] },
    { "id": "express_publish",      "agent": "news.NewsPublisherAgent",       "deps": ["express_compliance"] }
  ]
}
```

---

## 11. Métricas e KPIs

### 11.1 Métricas de Conteúdo

| Métrica | Alvo | Frequência | Fonte |
|---------|------|-----------|-------|
| Artigos publicados/dia | 3-5 | Diário | Workflow |
| Palavras totais/dia | 5000+ | Diário | Banco |
| Score SEO médio | > 80 | Por artigo | Agente SEO |
| Artigos aprovados no compliance | 100% | Por artigo | Agente Compliance |
| Artigos com 3+ fontes | 100% | Por artigo | Fact Checker |
| Artigos evergreen | > 60% | Semanal | Evergreen Scorer |

### 11.2 Métricas de Performance (Google)

| Métrica | Alvo | Prazo | Fonte |
|---------|------|-------|-------|
| Artigos indexados no Google | 100% | 1 semana | Google Search Console |
| Posição média no Google | Top 10 | 3 meses | GSC / Rank Tracker |
| Cliques orgânicos/dia | 100+ | 3 meses | GSC |
| Pageviews/dia | 500+ | 6 meses | Analytics |
| RPM (Receita por 1000 views) | > $5 | 6 meses | AdSense |
| Receita mensal | > $100 | 6 meses | AdSense |
| Taxa de rejeição | < 60% | Sempre | Analytics |
| Tempo médio na página | > 2 min | Sempre | Analytics |

### 11.3 Métricas de Sistema

| Métrica | Alvo | Fonte |
|---------|------|-------|
| Ciclos completos sem erro | > 95% | Daemon |
| Uso de LLM (chamadas/dia) | < 100 | Manager |
| Fallback para stdlib | < 5% | Manager |
| Tempo médio do ciclo | < 30 min | Workflow |
| Memória RAM | < 500MB | System |

---

## 12. Riscos e Mitigações

### 12.1 Matriz de Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|:-----------:|:-------:|-----------|
| Google rejeitar site no AdSense | Média | Alto | Conteúdo original, 50+ artigos antes de aplicar |
| Google penalizar conteúdo AI | Média | Alto | Revisão, fontes, E-E-A-T |
| Conteúdo gerado soar não-natural | Média | Médio | Melhoria contínua de prompts |
| Concorrência em nichos de alto CPC | Alta | Médio | Nichos de cauda longa |
| Domínio ficar com baixa autoridade | Média | Médio | Link building orgânico, guest posts |
| LLM rate limits durante pico | Média | Baixo | 13 provedores com failover |
| Custo de domínio/hospedagem | Baixa | Baixo | Cloudflare Pages grátis + domínio .com.br ~R$30/ano |
| Plágio acidental pela LLM | Baixa | Alto | Fact checker + detector de similaridade |

### 12.2 Plano de Resposta a Incidentes

| Incidente | Ação | Tempo de Resposta |
|-----------|------|-------------------|
| AdSense rejeita site | Revisar 100% do conteúdo, ajustar compliance, reaplicar | 1 semana |
| Google desindexa artigos | Revisar quality, remover thin content, submit reconsideration | 48h |
| Conta AdSense banida | Apelar, migrar para rede alternativa (Mediavine, Taboola) | 72h |
| LLM cai (todos) | stdlib assume automaticamente, notificar | 5 min |
| Workflow quebra | Auto-restart (até 5 tentativas), notificar | 1 min |

---

## 13. Roadmap de Implementação

### Fase 1 — MVP News (Dias 1-3)

| Dia | Tarefa | Entrega |
|:---:|--------|---------|
| 1 | Criar agentes base (NewsAgentBase) + Editor + Reporter + Headline | 3 agentes |
| 1 | Criar workflow diário + skill NYT | 1 workflow + 1 skill |
| 2 | Criar SEO + FactChecker + Compliance | 3 agentes |
| 2 | Criar tema NYT (template + CSS) | Site funcional |
| 3 | Criar Publisher + Photographer + métricas | 3 agentes |
| 3 | Publicar 10 artigos de teste | 10 artigos no ar |

### Fase 2 — Validação (Dias 4-7)

| Dia | Tarefa | Entrega |
|:---:|--------|---------|
| 4 | Configurar domínio + Cloudflare Pages | Site no ar oficial |
| 4 | Aplicar para Google AdSense | Conta criada |
| 5 | Criar Evergreen + Newsletter + Social | 3 agentes |
| 5-7 | Publicar 30+ artigos | 30 artigos indexados |

### Fase 3 — Otimização (Semanas 2-4)

| Semana | Tarefa | Entrega |
|:------:|--------|---------|
| 2 | Monitorar Search Console, ajustar SEO | Posições melhorando |
| 2 | Adicionar Trending Workflow (4h) | Captura de oportunidades |
| 3 | Testar posicionamento de anúncios | RPM > $3 |
| 3 | Criar página Sobre + Contato + Política | Páginas estáticas |
| 4 | 100+ artigos publicados | Base de conteúdo sólida |

### Fase 4 — Escala (Meses 2-3)

| Mês | Tarefa | Entrega |
|:---:|--------|---------|
| 2 | Novas seções (Lifestyle, Ciência) | 7 seções ativas |
| 2 | Link building orgânico + guest posts | Autoridade de domínio |
| 2 | Primeiro paycheck do AdSense | $50-100 |
| 3 | 500+ artigos no ar | Tráfego orgânico consistente |

---

## 14. Perguntas em Aberto

| Pergunta | Status | Impacto na Decisão |
|----------|--------|-------------------|
| Domínio próprio ou subdomínio do site atual? | 🔷 **Decidir agora** | SEO: domínio próprio ganha |
| Nome do site de notícias? (ex: "Jornal Tech", "Info Décadas", etc) | 🔷 **Decidir agora** | Marca e identidade |
| Autor simulado com IA ou autor humano real? | 🔷 **Decidir agora** | E-E-AAT: humano é melhor |
| Começar com quantas seções? | 🔷 **Decidir agora** | 3-5 sugerido |
| Aplicar para AdSense imediatamente ou esperar conteúdo? | 🔷 **Decidir agora** | 50+ artigos recomendado |
| Precisa de página "Sobre" com CNPJ? | 🔷 **Verificar** | Pode usar CPF como pessoa física |
| Analytics: Google Analytics ou alternativa gratuita? | 🔷 **Decidir agora** | GA4 é grátis |
| Imagens: geradas (grátis) ou banco de imagens? | 🔷 **Decidir agora** | Geradas (já temos o pipeline) |

---

## Apêndice A — Glossário

| Termo | Significado |
|-------|------------|
| **ADR** | Architecture Decision Record |
| **AdSense** | Programa de anúncios do Google |
| **CPC** | Custo Por Clique |
| **CPM** | Custo Por Mil impressões |
| **DAG** | Directed Acyclic Graph (modelo de workflow) |
| **Dek** | Subtítulo de artigo (jornalismo) |
| **E-E-A-T** | Experience, Expertise, Authoritativeness, Trustworthiness |
| **Evergreen** | Conteúdo que permanece relevante por longo tempo |
| **Lide** | Lead, primeiro parágrafo que resume a notícia |
| **NYT** | The New York Times |
| **RPM** | Receita por Mil impressões |
| **SEO** | Search Engine Optimization |
| **Vertical** | Domínio de negócio (ex: afiliados, notícias) |

---

## Apêndice B — Referências

1. [Google AdSense Program Policies](https://support.google.com/adsense/answer/48182)
2. [Google Search Essentials](https://developers.google.com/search/docs/essentials)
3. [Google E-E-A-T Guidelines](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
4. [The New York Times — Journalistic Guidelines](https://www.nytco.com/company/business-and-standards/)
5. [ADR Template — Michael Nygard](https://github.com/joelparkerhenderson/architecture-decision-record)
