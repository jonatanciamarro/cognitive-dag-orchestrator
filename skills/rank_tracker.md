# RankTrackerAgent

## Função
Monitora posições de keywords no Google via scraping. Não requer API key.

## Entrada
- Keywords do SEOScraperAgent ou SEOResearchAgent
- Domínio alvo (para tracking próprio)

## Saída
- Posição atual de cada keyword no Google
- Top 10 resultados com URLs e títulos
- Estimativa de tráfego por posição
- Keywords ranqueadas vs não ranqueadas

## Regras
- Máximo 5 keywords por ciclo (rate limit)
- 3s entre requisições
- Tracking de domínio próprio opcional
- Reporte de top 10 e posição exata

## Observações
- Ideal para acompanhar progresso SEO semana a semana
- Roda junto com autopilot para tracking contínuo
- Concorrência e posições mudam com frequência
