# BulkPublisherAgent

## Função
Publica TODO o conteúdo gerado no ciclo com agendamento inteligente coordenado entre canais.

## Estratégia de Agendamento
- Blog: 1 artigo a cada 2 dias
- YouTube: 1 vídeo por semana
- Pinterest: 1 pin por dia
- WhatsApp: conforme cronograma semanal
- Email: delays configurados (0, 1, 3, 7, 14 dias)

## Saída
- Calendário completo de publicações
- Arquivos de assets organizados por canal
- Estimativa de semanas/meses de conteúdo
- Recomendação de frequência

## Regras
- Itens ordenados por data de publicação
- Calendário semanal agrupado
- Assets salvos em output/published/{canal}/
- Disclosure mantido em todos os canais

## Observações
- Um ciclo de 48h gera até 30+ dias de conteúdo programado
- Ideal para manter consistência sem esforço diário
- Integração futura: publicar automaticamente via APIs
