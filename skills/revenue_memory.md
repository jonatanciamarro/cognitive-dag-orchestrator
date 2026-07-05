# RevenueMemory — Banco Unificado de Receitas

## Propósito
Armazena estado e histórico de TODAS as 13 fontes de renda em SQLite. Centraliza métricas, eventos e protocolos.

## Capacidades
- Status de cada fonte (pending, active, paused, error)
- Receita total por fonte
- Cliques e conversões
- Eventos de receita (comissão, lead, venda)
- Protocolos E2E por fonte
- Histórico temporal

## Localização
`.state/revenue.db` (SQLite WAL mode)

## Tabelas
- `revenue_sources` — Estado atual de cada fonte
- `revenue_events` — Histórico de eventos de receita
- `revenue_protocols` — Protocolos de configuração

## Uso
```python
from campaign_autopilot.agents.revenue import RevenueMemory

memory = RevenueMemory()
summary = memory.get_summary()
status = memory.get_status()
```
