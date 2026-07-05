# 🧠 Cognitive Architecture — Campaign Autopilot v5.2.1

> Como o sistema pensa, aprende e evolui.
> **3 Ordens Cognitivas | AG-Kit Evolution Fases 1-19 | ~105K Linhas**

## Filosofia

O Campaign Autopilot não é apenas um workflow engine. Ele incorpora uma **arquitetura cognitiva** inspirada em sistemas de memória humana, epistemologia e meta-cognição.

## Camadas Cognitivas

```
                    ┌──────────────────────────┐
                    │    META-COGNIÇÃO          │
                    │  "Pensar sobre pensar"    │
                    │  Drift, Metas, Episteme   │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │    SÍNTESE                │
                    │  "Aprender com o tempo"   │
                    │  Padrões, Conflitos       │
                    └──────────┬───────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
  ┌─────▼──────┐       ┌──────▼──────┐       ┌───────▼─────┐
  │ Memória    │       │ Explicações │       │ Resultados  │
  │ Semântica  │       │ (Proveniên- │       │ (Esperado   │
  │ (Conceitos,│       │  cia)       │       │ vs Real)    │
  │  Claims)   │       │             │       │             │
  └─────┬──────┘       └──────┬──────┘       └───────┬─────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │    WORKFLOW ENGINE        │
                    │  "Coordenar agents"       │
                    │  DAG + ThreadPoolExecutor │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │    26 AGENTES             │
                    │  "Especialistas"          │
                    │  SEO, Conteúdo, Canais    │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │    PERSISTÊNCIA           │
                    │  "Memória de longo prazo" │
                    │  SQLite WAL               │
                    └──────────────────────────┘
```

## 1. Percepção (Dados → Informação)

```
Eventos brutos (impressions, clicks, conversions)
    │
    ▼
calculate_metrics() → CTR, CVR, CPA, ROAS
    │
    ▼
Agentes especialistas processam em paralelo
```

## 2. Memória de Curto Prazo (Working Memory)

**Armazenamento:** `CampaignContext` (objeto em memória durante execução do workflow)

**Conteúdo:**
- campaign: configuração atual
- signals: métricas do ciclo
- memory: lições de ciclos anteriores
- step_results: outputs de cada agente

**Duração:** Duração do ciclo (segundos a minutos)

## 3. Memória de Longo Prazo (SQLite)

### 3.1 Memória Procedural (`MemoryStore`)
- Tabelas: campaigns, events, metrics, decisions, memory_records
- O quê: dados brutos de campanhas
- Como: SQLite WAL, upsert, query por campaign_id

### 3.2 Memória Semântica (`SemanticMemoryStore`)
- O quê: conhecimento estruturado (conceitos + claims)
- Como: Grafo de conhecimento com confiança e proveniência
- Exemplo: `keyword("marketing afiliados") --has_volume--> 2400`

### 3.3 Memória Episódica (`OutcomeStore`)
- O quê: resultados de ciclos anteriores
- Como: expected → actual → delta → lesson
- Exemplo: `cycle_42: CPA esperado 30, real 25, lição "aumentar lances"`

## 4. Raciocínio (Agentes)

Cada agente implementa `AgentBase.run(context) → AgentResult`:

1. **Recebe** o CampaignContext completo
2. **Processa** com sua especialidade
3. **Registra** explicação no ExplanationStore
4. **Retorna** output + trace

O DAG scheduler coordena a ordem baseada em dependências.

## 5. Epistemologia (Confiabilidade do Conhecimento)

Cada `KnowledgeClaim` no `SemanticMemoryStore` tem:

| Atributo | Descrição |
|----------|-----------|
| **confidence** | 0.0 - 1.0 (quão certo estamos) |
| **epistemic_status** | VERIFIED / INFERRED / ASSUMED / HYPOTHETICAL |
| **observer** | Quem fez a afirmação |
| **source_cycle_id** | Em qual ciclo |
| **evidence_type** | direct_measurement / statistical_inference / expert_opinion / assumption |

**Fórmula de peso epistêmico:**
```
epistemic_weight = confidence × multiplier(status)
  VERIFIED:    1.0
  INFERRED:    0.8
  ASSUMED:     0.5
  HYPOTHETICAL: 0.3
```

## 6. Meta-Cognição

### 6.1 Detecção de Drift Semântico
O orchestrator compara snapshots de ontologia entre ciclos e gera alertas quando conceitos mudam.

### 6.2 Síntese de Conhecimento
`KnowledgeSynthesisEngine` analisa múltiplos ciclos para encontrar:
- **Padrões Reforçados**: Mesma conclusão em vários ciclos → conhecimento estável
- **Padrões Conflitantes**: Mesmo sujeito com objetos diferentes → possível drift
- **Tendências**: Confiança rising/stable/declining

### 6.3 Decaimento Temporal
Conhecimento não verificado perde confiança ao longo do tempo:
```
VERIFIED:     0.95/ciclo
INFERRED:     0.85/ciclo
ASSUMED:      0.75/ciclo
HYPOTHETICAL: 0.65/ciclo
```

### 6.4 Goal Registry
Metas estratégicas persistem entre ciclos e são auto-avaliadas:
```python
goal = goals.register_goal(
    objective="Reduzir CPA para < 30",
    success_criteria={"cpa": 30}
)
# Auto-avaliação no fim do ciclo:
goals.evaluate_from_outcome(cycle_id, outcome_data)
```

## 7. Ciclo de Aprendizado

```
Ciclo N:
  1. Executar workflow
  2. Registrar claims no SemanticMemoryStore
  3. Registrar explicações no ExplanationStore
  4. Registrar outcomes no OutcomeStore
  5. Avaliar metas no GoalRegistry
  6. Verificar drift ontológico
  7. Sintetizar padrões

Ciclo N+1:
  1. Buscar lições relevantes na memória
  2. Aplicar conhecimento acumulado
  3. Repetir
```

## 8. Diagrama de Fluxo de Conhecimento

```
[INPUT]                    [PROCESS]                    [OUTPUT]

Eventos ──────────→ AnalyticsAgent ──────→ Performance Signals
                                                    │
Pesquisa SEO ─────→ SEOResearchAgent ────→ Keywords + Volumes
                                                    │
Ofertas ──────────→ OfferLookupAgent ────→ Produtos para promover
                                                    │
                                                    ▼
                                           ContentPlanner
                                                    │
                                                    ▼
                                           ContentGenerator ───→ Artigos
                                                    │
                                                    ├──→ YouTube Scripts
                                                    ├──→ Email Sequences
                                                    ├──→ Pinterest Pins
                                                    └──→ WhatsApp Msgs
                                                    │
                                                    ▼
                                           RevenueMonitor ─────→ Projeções
                                                    │
                                                    ▼
                                           AnalyticsFeedback ──→ Lições
                                                    │
                                                    ▼
                                           SemanticMemory ─────→ Conhecimento
```

## 9. Tracking de Decisões (ExplanationStore)

Cada decisão de agente é registrada com:
```json
{
  "explanation_id": "uuid",
  "agent": "optimization",
  "decision_id": "uuid",
  "input_state": { ... },
  "reasoning": "R1: CPA acima do alvo → realocar orçamento",
  "applied_rules": ["budget_reallocation", "cpa_threshold"],
  "counterfactuals": [
    "Se CPA estivesse dentro do alvo, manutenção de rota"
  ],
  "rendered": {
    "operator": "CPA de R$45 acima do alvo de R$30...",
    "compliance": "Decisão dentro das políticas de compliance...",
    "cto": "Otimização orçamentária baseada em performance..."
  }
}
```

## 10. Métricas Cognitivas

| Métrica | Onde | O que mede |
|---------|------|------------|
| Nº de conceitos | SemanticMemoryStore | Tamanho do conhecimento |
| Nº de claims | SemanticMemoryStore | Quantidade de relações |
| Confiança média | SemanticMemoryStore | Qualidade do conhecimento |
| Nº de padrões | KnowledgeSynthesisEngine | Maturidade do aprendizado |
| Nº de conflitos | KnowledgeSynthesisEngine | Inconsistências |
| Nº de metas atingidas | GoalRegistry | Eficácia estratégica |
| Drift detections | OntologySteward | Estabilidade semântica |
| Decisões registradas | ExplanationStore | Proveniência |
| Lições aprendidas | OutcomeStore | Experiência acumulada |

---

*Parte da documentação do Campaign Autopilot v5.2.0 — A arquitetura cognitiva do sistema.*
