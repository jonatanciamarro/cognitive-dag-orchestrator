# RevenueMonitorAgent

## Função
Monitora receita de afiliados, taxas de conversão e ROI por canal. É o 'financeiro' do sistema.

## Entrada
- Ofertas de afiliados (do OfferLookupAgent)
- Conteúdo produzido (todos os agentes de conteúdo)
- Dados históricos (do autopilot database)

## Saída
- Projeções de receita mensal por canal
- Top ofertas por potencial de comissão
- Estimativas de tráfego, cliques e conversões
- Recomendação estratégica de onde focar

## Métricas Calculadas
- Tráfego mensal estimado (blog + YouTube + email)
- Cliques mensais (CTR 3-5% sobre tráfego)
- Conversões mensais (taxa 2% sobre cliques)
- Receita mensal estimada (conversões × comissão média)
- Comissão média por venda

## Regras
- Projeções conservadoras (iniciante)
- Disclaimer de que são estimativas
- Requer APIs reais para dados precisos
- Benchmarks de mercado como base

## Configuração para Dados Reais
```
HOTMART_CLIENT_ID=seu_id
HOTMART_CLIENT_SECRET=seu_secret
AMAZON_ACCESS_KEY=sua_key
AMAZON_SECRET_KEY=sua_secret
AMAZON_ASSOCIATE_TAG=seu_tag
```
