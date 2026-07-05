# ContentOptimizerAgent

## Função
Analisa conteúdo gerado e sugere melhorias SEO, legibilidade e conversão.

## Entrada
- Artigos (do ContentGeneratorAgent)
- Conteúdo repurpado (do ContentRepurposerAgent)
- Keywords alvo

## Saída
- Score SEO (0-100) por artigo
- Issues encontradas (heading, keyword, disclosure, CTA, links)
- Sugestões globais de melhoria
- Recomendação final

## Critérios de Avaliação
- Título: 5-15 palavras
- Meta description: 10-25 palavras
- Tamanho: mínimo 300 palavras (artigo), 200 (review)
- Keyword density: 2-20 ocorrências
- Headings: H2/H3 presentes
- Disclosure de afiliado: obrigatório
- Call to action: presente
- Links externos: presentes
- Legibilidade: frases < 30 palavras

## Observações
- Score começa em 70 e deduz por issues
- Score > 80: conteúdo bem otimizado
- Score < 50: precisa revisão antes de publicar
- Global issues mostra padrões entre artigos
