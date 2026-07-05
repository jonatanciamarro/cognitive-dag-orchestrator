# KollektivAgent Skill — 4ª Ordem: Inteligência Coletiva Cross-Nicho

## Propósito
Conectar todos os nichos em um barramento de conhecimento compartilhado.
Detectar padrões cross-nicho e distribuir estratégias vencedoras automaticamente.

## Gatilho
Executado automaticamente após TODOS os nichos completarem seus ciclos em `run_all_niches.py`.

## Fluxo de Execução

```
1. COLLECT → Coleta resultados de todos os nichos do ciclo atual
2. RECORD  → Armazena cada ciclo no CrossNicheVault (SQLite)
3. ANALYZE → Detecta padrões que funcionam em MÚLTIPLOS nichos
4. RECOMMEND → Gera recomendações: "isso funciona em financas, testa em tecnologia"
5. REPORT  → Síntese com health do vault e padrões encontrados
```

## CrossNicheVault (Tabelas SQLite)

| Tabela | Propósito |
|--------|-----------|
| `niche_cycles` | Histórico de cada ciclo por nicho |
| `winning_strategies` | Estratégias que provaram funcionar |
| `cross_patterns` | Padrões detectados em múltiplos nichos |
| `shared_ontology` | Conceitos compartilhados entre nichos |

## Como Usar

```python
from campaign_autopilot.agents.kollektiv import KollektivAgent

agent = KollektivAgent()
result = agent.run(context)
```

## Dependências
- SQLite3 (stdlib)
- Nenhuma API externa

## Arquivo de Estado
`.state/kollektiv.db` — criado automaticamente no primeiro ciclo.
