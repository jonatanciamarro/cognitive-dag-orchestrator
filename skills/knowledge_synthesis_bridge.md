# Knowledge Synthesis Bridge

## Propósito

Ponte entre o KnowledgeSynthesisEngine e os agentes de execução, traduzindo insights de alto nível em ações concretas.

## Responsabilidades

- Traduzir meta-insights em recomendações acionáveis
- Conectar padrões跨-ciclo a decisões de execução
- Priorizar insights por relevância para o ciclo atual
- Garantir que aprendizados sejam aplicados

## Inputs

- Insights do KnowledgeSynthesisEngine
- Estado atual do ciclo
- Histórico de recomendações aplicadas

## Outputs

- Recomendações acionáveis priorizadas
- Mapeamento insight -> ação
- Status de aplicação de recomendações anteriores

## Regras

- Insights sem ação correspondente são ruído
- Recomendações devem especificar agente responsável
- Aplicação de recomendações deve ser tracking
