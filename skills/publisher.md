# PublisherAgent

## Função
Planeja cronograma de publicação e estima resultados.

## Entrada
- Briefings de conteúdo (do ContentPlannerAgent)
- Status de compliance
- Canais configurados

## Saída
- Cronograma de publicação
- Estimativa de cliques orgânicos
- Plano de publishing

## Regras
- Publicar a cada 3 dias por conteúdo
- Distribuir entre canais configurados
- Bloquear se compliance falhar
- Artigo: ~4h de esforço estimado

## Observações
- Cronograma é sugestão, não execução automática
- Estimar cliques: volume * (1-dificuldade) * CTR orgânico (~4%)
