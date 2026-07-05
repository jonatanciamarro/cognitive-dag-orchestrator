# AgentPerformanceMonitor

## Função
Monitora e analisa a performance individual de cada agente. Analytics de segunda ordem.

## O que faz
- Rastreia taxa de sucesso, tempo médio e output quality por agente
- Identifica agentes com degradação de performance
- Gera ranking de agentes por contribuição
- Detecta anomalias (falhas recorrentes, degradação, erros)

## Métricas por Agente
- Runs: total de execuções
- Success Rate: taxa de sucesso
- Avg Duration: tempo médio
- Output Score: qualidade do output
- Performance Trend: evolução nos últimos 10 ciclos

## Anomalias Detectadas
| Tipo | Severidade | Ação |
|------|------------|------|
| Alta taxa de falha | Crítica | Revisar agente |
| Degradação de performance | Alta | Verificar parâmetros |
| Erro de execução | Média/Alta | Investigar |

## Saída
- Métricas do ciclo atual
- Ranking de agentes
- Anomalias detectadas
- Recomendações
