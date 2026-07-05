# SEOScraperAgent

## Função
Coleta dados reais de SEO via web scraping do Google. Não requer API key.

## Entrada
- Nicho da campanha

## Saída
- Keywords com dificuldade estimada
- URLs e títulos dos concorrentes
- Related searches do Google
- "People also ask" questions
- Recomendação de oportunidades

## Como funciona
1. Faz 5 buscas no Google relacionadas ao nicho
2. Parseia resultados orgânicos do HTML
3. Extrai "People also ask" e related searches
4. Estima dificuldade baseada em concorrência
5. Estima volume de busca baseado em características da keyword

## Regras
- Rate limit de 2s entre requisições (evitar bloqueio)
- User-Agent realista (Chrome desktop)
- Timeout de 15s por requisição
- Dados têm precisão limitada (scraping público)

## Observações
- Precisão menor que Ahrefs/Semrush, mas não requer API paga
- Ideal para estágio inicial (validação de nicho)
- Para precisão profissional, configurar AHREFS_API_KEY
