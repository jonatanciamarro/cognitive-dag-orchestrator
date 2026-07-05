# CompetitorAnalysisAgent

## Função
Analisa concorrentes no nicho, encontra gaps de conteúdo e oportunidades de diferenciação.

## Entrada
- Dados do SEOScraperAgent (real) ou SEOResearchAgent (simulado)
- Nicho da campanha

## Saída
- Lista de concorrentes ranqueados por relevância
- Gaps de conteúdo (keywords com baixa cobertura)
- Padrões de conteúdo dos concorrentes
- Oportunidades de alta diferenciação

## Métricas
- Concorrentes encontrados e páginas analisadas
- Keywords cobertas por cada concorrente
- Gaps classificados por nível (high/medium/low)
- Padrões comuns de conteúdo (guias, reviews, tutoriais)

## Regras
- Priorizar gaps high (1 ou 0 concorrentes cobrindo)
- Sugerir conteúdo aprofundado para gaps
- Analisar padrões para diferenciar conteúdo

## Observações
- Usa dados reais quando SEOScraperAgent disponível
- Cai para dados simulados como fallback
- Ideal para encontrar nichos com baixa concorrência
