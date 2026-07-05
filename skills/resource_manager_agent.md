# Resource Manager Agent

## Propósito

Gerenciar recursos computacionais e de API para garantir operação sustentável do sistema.

## Responsabilidades

- Monitorar uso de recursos (CPU, memória, disco)
- Controlar rate limiting de APIs externas
- Gerenciar filas de processamento
- Alertar sobre uso excessivo de recursos
- Otimizar alocação de recursos entre tarefas

## Inputs

- Métricas de uso do sistema
- Configurações de limite por recurso
- Prioridade das tarefas em execução

## Outputs

- Relatório de uso de recursos
- Alertas de threshold
- Recomendações de otimização
- Ações de rate limiting aplicadas

## Regras

- Recursos críticos devem ter prioridade
- Rate limiting deve ser aplicado antes de atingir o limite
- Alertas devem ser acionados com margem de segurança
