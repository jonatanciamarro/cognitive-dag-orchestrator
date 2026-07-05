# ADR-002: Arquitetura Algoritmo-Centrada — Conteúdo Otimizado para Múltiplos Buscadores

> **Status:** Approved
> **Data:** 2026-06-23
> **Autor:** Chief Intelligence Architect — Lyzer Labs
> **Substitui:** ADR-001 (modelo NYT)
> **Motivação:** "Quero o que o Google quer — e Bing, Yahoo, etc"

---

## 1. Decisão

> **Não modelar nenhum veículo jornalístico específico.**
> **Modelar o algoritmo dos buscadores.**

Ao invés de copiar o NYT (forma), vamos otimizar para o que Google, Bing e Yahoo **realmente recompensam** (função).

A diferença é crítica:

| Abordagem | Foco | Risco | Resultado |
|-----------|------|-------|-----------|
| **Modelo NYT** | Aparência de jornalismo | Google penaliza se for "só aparência" | ❌ Pode parecer genérico |
| **Modelo Algorítmico** | Sinais que os buscadores querem | Nenhum — segue as regras do jogo | ✅ Máximo tráfego orgânico |

---

## 2. O Que os Buscadores Realmente Querem

### 2.1 Google — Helpful Content System (2024-2026)

O Google não quer "conteúdo jornalístico".
O Google quer **conteúdo útil, original e feito por humanos (ou que pareça)**.

Os sinais específicos que o sistema do Google avalia:

```
HELPFUL CONTENT SYSTEM — SINAIS AVALIADOS
│
├── 📝 Utilidade
│   ├── O conteúdo responde à intenção de busca do usuário?
│   ├── O usuário sai satisfeito ou precisa buscar de novo?
│   └── O conteúdo entrega o que o título promete?
│
├── 🎯 Expertise (E-E-A-T)
│   ├── Quem escreveu tem conhecimento no assunto?
│   ├── O conteúdo cita fontes confiáveis?
│   ├── Tem data de publicação e atualização?
│   └── O site tem página "Sobre" com credenciais?
│
├── 🏆 Autoridade
│   ├── Outros sites confiáveis linkam para este conteúdo?
│   ├── O conteúdo é citado como referência?
│   └── O domínio tem histórico de conteúdo de qualidade?
│
├── 🔐 Confiança (Trustworthiness)
│   ├── O conteúdo é factualmente preciso?
│   ├── As afirmações podem ser verificadas?
│   ├── Não engana o usuário?
│   └── Informações de contato claras?
│
├�── 💎 Originalidade
│   ├── O conteúdo adiciona valor novo?
│   ├── Não é reescrita de conteúdo existente?
│   └── Tem insights, dados, perspectivas únicas?
│
└── 📄 Legibilidade
    ├── Estrutura clara (títulos, parágrafos, listas)
    ├── Tom apropriado para o assunto
    ├── Sem jargão desnecessário
    └── Multimídia (imagens, vídeos, exemplos)
```

### 2.2 Bing — Copilot + Search

O Bing (2026) fundiu busca com IA. O Copilot do Microsoft lê e resume páginas.
Sinais específicos que o Bing avalia:

```
BING/COPILOT — SINAIS ADICIONAIS
│
├── 🤖 Amigável para IA
│   ├── O conteúdo é fácil de resumir em bullet points?
│   ├── Tem estrutura semântica clara (schema.org)?
│   └── As respostas podem ser extraídas em featured snippets?
│
├── 🔗 Authority Score
│   ├── Backlinks de sites .gov, .edu, Wikipedia
│   ├── Menções em redes sociais
│   └── Idade do domínio
│
├── 📱 Mobile optimization
│   ├── Core Web Vitals (LCP, FID, CLS)
│   ├── Design responsivo
│   └── Carregamento rápido
│
└── 📍 Local relevance (para conteúdo regional)
    ├── Geolocalização explícita
    ├── Referências regionais
    └── Idioma natural
```

### 2.3 Yahoo — Parceiro Bing + Diretórios

Yahoo usa Bing nos bastidores, mas tem sinais próprios:

```
YAHOO — SINAIS ESPECÍFICOS
│
├── 📰 Yahoo News Publisher Network
│   ├── Conteúdo indexado no Yahoo News
│   ├── Categorias editoriais claras
│   └── Conteúdo "jornalístico" tradicional
│
├── 🏢 Yahoo Finance (se aplicável)
│   ├── Dados financeiros, cotações
│   └── Análise de mercado
│
└── 📋 Yahoo Directory (legado)
    ├── Categorização hierárquica
    └── Metadados descritivos
```

---

## 3. Arquitetura Revisada — Conteúdo Algoritmo-Centrado

### 3.1 Princípio Central

> **O conteúdo não é modelado para parecer com nada.**
> **O conteúdo é modelado para MAXIMIZAR os sinais que os buscadores avaliam.**

Cada artigo é um **vetor de features**, onde cada feature é um sinal que um buscador usa:

```
ARTIGO = VETOR DE 20 SINAIS

Sinais Obrigatórios (score mínimo 8/10 cada):
├── 01. Title match: título corresponde à intenção de busca
├── 02. Meta description: clara, acionável, com palavra-chave
├── 03. Heading structure: H1→H2→H3 hierárquico
├── 04. Content depth: cobre o tópico completamente
├── 05. Readability: parágrafos curtos, linguagem clara
├── 06. Multimedia: 1+ imagem, vídeo ou infográfico
├── 07. Internal links: 3+ links para conteúdo relacionado
├── 08. External links: 2+ links para fontes autoritativas
├── 09. Schema markup: Article, FAQ, HowTo (o que aplicar)
├── 10. Freshness: data de publicação + data de atualização

Sinais de Diferenciação (aumentam exponencialmente o tráfego):
├── 11. Original research: dados, pesquisas, experimentos
├── 12. Expert quotes: citações de especialistas (reais ou simuladas com verificação)
├── 13. Case studies: exemplos reais com resultados
├── 14. Visual data: gráficos, tabelas, infográficos
├── 15. Interactive elements: calculadoras, quizzes, ferramentas

Sinais Técnicos (infraestrutura):
├── 16. Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
├── 17. Mobile friendly: 100% responsivo
├── 18. HTTPS + SSL
├── 19. Sitemap.xml + robots.txt
└── 20. Open Graph + Twitter Cards
```

### 3.2 Template de Artigo Algorítmico

Cada artigo gerado segue um **template de scoring** onde cada seção é avaliada:

```json
{
  "title": {
    "content": "string",
    "seo_score": 0-100,
    "requirements": [
      "palavra-chave principal nos primeiros 60 caracteres",
      "gancho emocional ou numérico",
      "máximo 60 caracteres",
      "sem clickbait (Google penaliza)"
    ]
  },
  "meta_description": {
    "content": "string",
    "seo_score": 0-100,
    "requirements": [
      "120-158 caracteres",
      "palavra-chave natural",
      "call-to-action implícito"
    ]
  },
  "introduction": {
    "content": "string",
    "seo_score": 0-100,
    "requirements": [
      "lide informativo (O quê, Para quem, Por que ler)",
      "palavra-chave nos primeiros 100 caracteres",
      "gancho que prende o leitor"
    ]
  },
  "body": {
    "sections": [
      {
        "heading": "string (H2)",
        "content": "string",
        "seo_score": 0-100,
        "requirements": [
          "cobre um aspecto do tópico",
          "200-400 palavras por seção",
          "links internos quando relevante",
          "imagem ou exemplo quando possível"
        ]
      }
    ],
    "overall_requirements": [
      "mínimo 4 H2s para artigos de 1500+ palavras",
      "FAQ section com 3-5 perguntas (schema)",
      "bullet points ou listas quando apropriado"
    ]
  },
  "conclusion": {
    "content": "string",
    "seo_score": 0-100,
    "requirements": [
      "recapitulação dos pontos principais",
      "call-to-action: comentar, compartilhar, ler mais",
      "link para artigo relacionado"
    ]
  },
  "technical": {
    "schema_type": "Article | FAQPage | HowTo | ListItem",
    "open_graph": {
      "title": "string",
      "description": "string",
      "image": "path"
    },
    "canonical_url": "string",
    "word_count": 1500,
    "reading_time": "7 min"
  }
}
```

### 3.3 Intenção de Busca — O Coração do Sistema

O foco principal não é o formato, é a **intenção de busca**. Cada artigo é classificado em:

| Intenção | Tipo de Conteúdo | Chance de Snippet | CPC Médio |
|----------|-----------------|:-----------------:|:---------:|
| **Informacional** | Guia, tutorial, explicação | 🟢 Alta | 🟢 Alto |
| **Comercial** | Review, comparação, "melhor" | 🟡 Média | 🔴 Muito alto |
| **Transacional** | "Comprar", "preço", "desconto" | 🟢 Alta | 🔴 Altíssimo |
| **Navegacional** | "[Marca] + review" | 🟡 Média | 🟢 Alto |

O sistema prioriza **conteúdo informacional + comercial** porque:
1. Google recompensa mais (útil, responde perguntas)
2. CPC mais alto (intenção de compra)
3. Mais chances de featured snippet
4. Evergreen (rende por meses/anos)

---

## 4. Perfil de Autor E-E-A-T (Google-Friendly)

Ao invés de um autor anônimo, cada artigo tem um **perfil de autor otimizado para E-E-A-T**:

```yaml
autor:
  nome: "Carlos Andrade"  # Nome brasileiro, profissional
  biografia: >
    Carlos Andrade é especialista em [nicho] há 8 anos.
    Já ajudou mais de 2.000 pessoas a [benefício].
    Fundador do [site], referência em [assunto] no Brasil.
  foto: /assets/authors/carlos-andrade.jpg  # Foto gerada (realista, profissional)
  credenciais:
    - "Certificação em [assunto relevante]"
    - "Membro da [associação profissional]"
    - "Palestrante em [evento relevante]"
  redes:
    linkedin: "https://linkedin.com/in/carlos-andrade"
    instagram: "https://instagram.com/carlosandrade"
  artigos_publicados: 150+
  ultima_atualizacao: "2026-06-23"
```

Cada seção/nicho tem seu próprio autor-persona, com biografia consistente.

---

## 5. Agentes Revisados (Pós-ADR-002)

### 5.1 Substituições

| ADR-001 (NYT) | ADR-002 (Algoritmo) | Motivo |
|--------------|-------------------|--------|
| `news.NewsNYTModelerAgent` | ❌ Removido | Não vamos modelar NYT |
| `news.NewsFactCheckerAgent` | ➡️ `news.EEATValidatorAgent` | E-E-A-T é mais amplo que fact-check |
| `news.NewsPhotographerAgent` | ➡️ `media.SEOMultimediaAgent` | Foco em multimodal que ajuda SEO |

### 5.2 Agentes Finais (Versão Algoritmo-Centrada)

```
FASE 1 — CONTEÚDO (7 agentes)
├── 01. ContentResearchAgent      — Pesquisa palavras-chave + intenção + concorrência
├── 02. ContentStrategistAgent    — Define pauta com base em dados
├── 03. SEOContentWriterAgent     — Escreve artigo otimizado para múltiplos buscadores
├── 04. EEATValidatorAgent        — Valida E-E-A-T, fontes, credibilidade
├── 05. SEOTechnicalAgent         — Schema markup, meta tags, Open Graph
├── 06. SEMultimediaAgent         — Gera imagens, gráficos, infográficos SEO-friendly
└── 07. InternalLinkerAgent       — Cria malha de links internos entre artigos

FASE 2 — PUBLICAÇÃO (3 agentes)
├── 08. SitePublisherAgent        — Publica site estático SEO-otimizado
├── 09. SearchConsoleAgent        — Submete sitemap, monitora indexação
└── 10. RankTrackerAgent          — Monitora posições no Google/Bing/Yahoo

FASE 3 — MONETIZAÇÃO (5 agentes)
├── 11. AdSenseOptimizerAgent     — Posicionamento de anúncios que não prejudica UX
├── 12. AffiliateMatcherAgent     — Matching de conteúdo × oferta de afiliado
├── 13. SEOMonetizationAgent      — Equilíbrio entre SEO e monetização
├── 14. RPMOptimizerAgent         — Maximiza receita por visita sem sacrificar tráfego
└── 15. CrossDomainAgent          — Sinergia entre site de conteúdo e site de afiliados

FASE 4 — ORQUESTRAÇÃO (3 agentes)
├── 16. SEOAnalyticsAgent         — Analisa Google Search Console + Bing Webmaster
├── 17. ContentAuditorAgent       — Auditoria de conteúdo existente vs concorrência
└── 18. AlgorithmUpdateAgent      — Monitora atualizações de algoritmos e ajusta estratégia
```

---

## 6. Workflow Revisado — News Algorítmico

### 6.1 Ciclo Diário (Conteúdo Novo)

```json
{
  "id": "algorithmic_content_daily",
  "name": "Ciclo Diário de Conteúdo SEO-Otimizado",
  "schedule": { "type": "interval", "hours": 24 },
  "steps": [
    {
      "id": "keyword_research",
      "agent": "ContentResearchAgent",
      "description": "Pesquisa palavras-chave com potencial, analisa concorrência, identifica intenção de busca",
      "dependencies": [],
      "timeout": 300,
      "config": {
        "sources": ["Google Trends", "AnswerThePublic", "Google Autocomplete", "PAA", "Bing API"],
        "min_search_volume": 100,
        "max_difficulty": 60,
        "preferred_intents": ["informational", "commercial"]
      }
    },
    {
      "id": "content_strategy",
      "agent": "ContentStrategistAgent",
      "description": "Define pauta: título, estrutura, ângulo, diferenciação da concorrência",
      "dependencies": ["keyword_research"],
      "timeout": 120,
      "config": {
        "content_gap_analysis": true,
        "competitor_differentiation": true
      }
    },
    {
      "id": "seo_content_writing",
      "agent": "SEOContentWriterAgent",
      "description": "Escreve artigo completo otimizado para Google + Bing + Yahoo",
      "dependencies": ["content_strategy"],
      "timeout": 600,
      "config": {
        "target_word_count": 2000,
        "include_paa": true,
        "include_schema": true,
        "include_faq": true
      },
      "foreach": "pautas_aprovadas"
    },
    {
      "id": "eeat_validation",
      "agent": "EEATValidatorAgent",
      "description": "Valida E-E-A-T: fontes, autoridade, confiança, originalidade",
      "dependencies": ["seo_content_writing"],
      "timeout": 180,
      "config": {
        "min_sources": 2,
        "require_author_profile": true,
        "score_threshold": 85
      }
    },
    {
      "id": "seo_technical",
      "agent": "SEOTechnicalAgent",
      "description": "Aplica schema markup, meta tags, Open Graph, URLs amigáveis",
      "dependencies": ["eeat_validation"],
      "timeout": 60,
      "config": {
        "schema_types": ["Article", "FAQPage", "BreadcrumbList"],
        "generate_sitemap_entry": true
      }
    },
    {
      "id": "multimedia_generation",
      "agent": "SEOMultimediaAgent",
      "description": "Gera imagens com alt text otimizado, infográficos leves, gráficos",
      "dependencies": ["seo_content_writing"],
      "timeout": 120,
      "parallel": true
    },
    {
      "id": "internal_linking",
      "agent": "InternalLinkerAgent",
      "description": "Cria links internos entre artigos existentes e novo artigo",
      "dependencies": ["seo_technical", "multimedia_generation"],
      "timeout": 30
    },
    {
      "id": "publish",
      "agent": "SitePublisherAgent",
      "description": "Publica artigo, submete ao Search Console, notifica Bing",
      "dependencies": ["internal_linking"],
      "timeout": 60,
      "config": {
        "ping_google": true,
        "ping_bing": true,
        "generate_sitemap": true
      }
    }
  ]
}
```

### 6.2 Ciclo Semanal (Auditoria + Otimização)

```json
{
  "id": "algorithmic_audit_weekly",
  "name": "Auditoria Semanal de Performance nos Buscadores",
  "schedule": { "type": "weekly", "day": "sunday" },
  "steps": [
    {
      "id": "rank_analysis",
      "agent": "RankTrackerAgent",
      "description": "Analisa posições no Google, Bing, Yahoo dos artigos publicados",
      "dependencies": []
    },
    {
      "id": "search_console_analysis",
      "agent": "SEOAnalyticsAgent",
      "description": "Analisa GSC: impressões, cliques, CTR, posição média, queries",
      "dependencies": ["rank_analysis"]
    },
    {
      "id": "content_audit",
      "agent": "ContentAuditorAgent",
      "description": "Identifica artigos com baixa performance, sugere melhorias",
      "dependencies": ["search_console_analysis"]
    },
    {
      "id": "content_refresh",
      "agent": "SEOContentWriterAgent",
      "description": "Atualiza artigos com baixa performance (data, informações, links)",
      "dependencies": ["content_audit"],
      "config": { "mode": "refresh" }
    },
    {
      "id": "algorithm_monitor",
      "agent": "AlgorithmUpdateAgent",
      "description": "Verifica se houve atualizações de algoritmo, ajusta estratégia",
      "dependencies": [],
      "config": {
        "sources": ["Google Search Status Dashboard", "SEO news", "Bing Webmaster Blog"]
      }
    }
  ]
}
```

---

## 7. Schema Markup — Implementação por Tipo de Conteúdo

### 7.1 Artigo Padrão (Article)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Título do Artigo com Palavra-Chave",
  "description": "Meta description otimizada",
  "image": "https://dominio.com/imagens/artigo.jpg",
  "author": {
    "@type": "Person",
    "name": "Carlos Andrade",
    "url": "https://dominio.com/autor/carlos-andrade",
    "knowsAbout": ["Nicho principal", "Sub-nicho específico"]
  },
  "publisher": {
    "@type": "Organization",
    "name": "Nome do Site",
    "logo": {
      "@type": "ImageObject",
      "url": "https://dominio.com/logo.png"
    }
  },
  "datePublished": "2026-06-23T08:00:00-03:00",
  "dateModified": "2026-06-23T08:00:00-03:00",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://dominio.com/artigo"
  },
  "wordCount": 2000,
  "timeRequired": "PT7M",
  "inLanguage": "pt-BR",
  "isAccessibleForFree": true,
  "hasPart": [
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Pergunta frequente 1?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Resposta completa e útil."
          }
        }
      ]
    }
  ]
}
```

### 7.2 Guia/HowTo

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Como [ação desejada]",
  "description": "Guia completo para [benefício]",
  "step": [
    {
      "@type": "HowToStep",
      "position": 1,
      "name": "Primeiro passo",
      "text": "Descrição detalhada do primeiro passo.",
      "image": "https://dominio.com/images/passo1.jpg"
    }
  ],
  "totalTime": "PT30M",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "BRL",
    "value": "0"
  },
  "tool": ["Ferramenta 1", "Ferramenta 2"],
  "yield": "Resultado esperado"
}
```

---

## 8. Estratégia de Conteúdo para Múltiplos Buscadores

### 8.1 Google — Foco em Utilidade e E-E-A-T

| Tática | Implementação | Impacto |
|--------|--------------|---------|
| Helpful Content | Artigo responde COMPLETAMENTE à intenção | 🟢 Essencial |
| E-E-A-T | Perfil de autor + fontes + biografia | 🟢 Essencial |
| Featured Snippet | Parágrafos de 40-50 palavras que respondem diretamente | 🟢 Alto |
| People Also Ask | FAQ section com schema | 🟢 Alto |
| Core Web Vitals | Site estático, carregamento instantâneo | 🟢 Alto |
| Mobile First | Design 100% responsivo | 🟢 Essencial |

### 8.2 Bing — Foco em Autoridade e Schema

| Tática | Implementação | Impacto |
|--------|--------------|---------|
| Schema.org completo | Todo artigo com markup | 🟢 Essencial |
| Bing Webmaster | Submeter sitemap, monitorar | 🟢 Alto |
| Backlinks de qualidade | Guest posts, parcerias | 🟡 Médio |
| Redes sociais (Bing indexa) | Compartilhar automaticamente | 🟡 Médio |
| Conteúdo multimídia | Imagens com alt text | 🟡 Médio |

### 8.3 Yahoo — Foco em Categorização (via Bing)

| Tática | Implementação | Impacto |
|--------|--------------|---------|
| Categorias claras | Seções hierárquicas | 🟢 Essencial |
| Yahoo News Network | Submissão manual após 50+ artigos | 🟡 Médio |
| Conteúdo evergreen | Artigos perenes com data atualizada | 🟡 Médio |

---

## 9. Receita: Conteúdo + Afiliados + AdSense (Harmonizado)

A grande vantagem desta abordagem: **o mesmo artigo pode ter múltiplas formas de monetização** sem conflito:

```python
MONETIZAÇÃO POR TIPO DE ARTIGO:

Artigo Informacional (ex: "Como escolher notebook em 2026")
├── AdSense (display ads) → R$ por mil visualizações
├── Link de afiliado Amazon → comissão se comprar
├── Newsletter opt-in → captura de lead
└── Conteúdo relacionado → mais páginas vistas

Artigo Comercial (ex: "Melhor notebook custo-benefício 2026")
├── Links de afiliado Amazon (comparação de preços)
├── Tabela comparativa (schema Table)
├── AdSense (menos intrusivo, mais conteúdo)
└── Guia complementar → mais páginas

Artigo Tutorial (ex: "Como configurar notebook novo")
├── AdSense (display)
├── Link de afiliado (produtos recomendados)
├── eBook relacionado → venda direta
└——— YouTube embed → receita de visualização
```

---

## 10. Métricas de Sucesso — Algoritmo-Centrado

### 10.1 Métricas de Busca (Semana 1-4)

| Métrica | Google | Bing | Yahoo |
|---------|:-----:|:----:|:----:|
| Artigos indexados | 100% | 90%+ | 80%+ |
| Posição média (30 dias) | < 30 | < 30 | < 30 |
| CTR médio | > 3% | > 2% | > 2% |
| Featured snippets | 5%+ dos artigos | — | — |

### 10.2 Métricas de Conteúdo (Mês 1-3)

| Métrica | Alvo | Frequência |
|---------|:----:|:----------:|
| Score E-E-A-T médio | > 85/100 | Por artigo |
| Schema validation | 100% válido | Por artigo |
| Artigos com featured snippet | 10%+ | Semanal |
| Palavras-chave no top 10 | 50+ | Semanal |
| Tráfego orgânico total | 1000+ visitas/mês | Mensal |

---

## 11. Próximos Passos (Onda 1 — Implementação Imediata)

### Dia 1 — Base

| Tarefa | Responsável | Duração |
|--------|-------------|:-------:|
| Criar `ContentResearchAgent` | Implementação | 2h |
| Criar `SEOContentWriterAgent` | Implementação | 3h |
| Criar template de artigo com scoring SEO | Implementação | 1h |
| Criar `EEATValidatorAgent` | Implementação | 2h |

### Dia 2 — Técnico + Multimídia

| Tarefa | Responsável | Duração |
|--------|-------------|:-------:|
| Criar `SEOTechnicalAgent` (schema + meta) | Implementação | 2h |
| Criar `SEOMultimediaAgent` (imagens SEO) | Implementação | 2h |
| Criar `InternalLinkerAgent` | Implementação | 1h |
| Workflow `algorithmic_content_daily.json` | Implementação | 1h |

### Dia 3 — Site + Publicação

| Tarefa | Responsável | Duração |
|--------|-------------|:-------:|
| Criar `SitePublisherAgent` | Implementação | 2h |
| Tema SEO-otimizado (mobile-first, Core Web Vitals) | Implementação | 3h |
| Sitemap + robots.txt + Search Console submission | Implementação | 1h |
| Publicar 5 artigos de teste | Implementação | 2h |

---

## 12. ADR-001 → ADR-002: Changes Summary

| Item | ADR-001 (NYT) | ADR-002 (Algoritmo) |
|------|:------------:|:-------------------:|
| **Modelo** | The New York Times | Algoritmos Google/Bing/Yahoo |
| **Autor** | Genérico | Perfil E-E-A-T completo |
| **Seções** | Fixas (Política, Tech...) | Dinâmicas (baseado em keyword research) |
| **Tom** | Jornalístico | Informativo-útil (Helpful Content) |
| **NYTModelerAgent** | ✅ Incluído | ❌ Removido |
| **FactCheckerAgent** | Fact-check básico | ➡️ EEATValidator (mais abrangente) |
| **Schema** | Article básico | Article + FAQ + HowTo + BreadcrumbList |
| **Intenção de busca** | Ignorada | **Central** (define tudo) |
| **Featured snippet** | Não priorizado | **Prioridade máxima** |
| **Multi-buscador** | Só Google implícito | Google + Bing + Yahoo explícito |
| **Content gap analysis** | Não | Sim (diferenciação da concorrência) |

---

*Fim do ADR-002*
