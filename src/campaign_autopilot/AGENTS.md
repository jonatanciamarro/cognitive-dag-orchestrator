# Campaign Autopilot — Core Package

## Arquitetura

```
src/campaign_autopilot/
├── agents/           # 64 agentes de IA + sub-pacotes
│   ├── base.py       # AgentBase, CampaignContext, AgentResult
│   ├── money/        # Monetizacao (afiliados, produtos, membresia)
│   ├── news/         # SEO + noticias (algoritmo-centrado)
│   ├── meta/         # Meta-cognicao (otimizacao, evolução)
│   ├── paid_traffic/ # Trafego pago (Google Ads, Meta, Native)
│   └── social_publishers/ # Publicacao social (8 plataformas)
├── execution/        # Schedulers, calendar, orchestracao
├── free_llm_providers.py  # 13 providers LLM gratuitos com failover
├── memory.py         # SQLite MemoryStore
├── semantic_memory.py     # SemanticMemoryStore (conceitos + claims)
└── workflow.py       # DAG workflow engine
```

## Convenções

- Todos os agentes extendem `AgentBase` e implementam `run(context) -> AgentResult`
- Workflows sao DAGs JSON carregados por `WorkflowRunner`
- Zero dependencias externas (stdlib only) — Streamlit separado
- Thread-safety com `threading.RLock()`
- Persistencia: SQLite (WAL) + JSON files em `.state/`
- Codigo em ingles, skills/docs em portugues

## Para adicionar novo agente

1. Criar em `src/campaign_autopilot/agents/`
2. Estender `AgentBase`, implementar `run()`
3. Exportar em `agents/__init__.py`
4. Criar skill em `skills/` e workflow em `workflows/`
5. Adicionar testes em `tests/`
