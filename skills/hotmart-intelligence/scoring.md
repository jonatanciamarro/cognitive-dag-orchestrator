# Hotmart scoring Agent

## Descrição
Fase 3 — Calcular OpportunityScore (0-100) com 5 critérios

## Input
- Product list from previous phase
- ProductIntelligenceStore (SQLite WAL)

## Output
- Phase results stored in ProductIntelligenceStore
- Updated product status

## Critérios de Qualidade
- Dados consistentes e completos
- Decisões rastreáveis via SQLite
- Falhas registradas sem interromper o pipeline

## Integração
Este agente faz parte do HotmartIntelligenceAgent coordinator que orquestra todas as 10 fases sequencialmente via ProductIntelligenceStore compartilhada.
