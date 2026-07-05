# ContentGeneratorAgent

## Função
Gera conteúdo real (artigos, reviews, tutoriais) a partir dos briefings produzidos pelo ContentPlannerAgent.

## Entrada
- Briefings de conteúdo (do ContentPlannerAgent)
- Ofertas de afiliados (do OfferLookupAgent)
- Nicho e canais da campanha

## Saída
- Artigos completos com título, corpo, meta-description
- Estatísticas: word count, estimated reading time
- Sugestão de ordem de publicação

## Regras
- Máximo 3 artigos por ciclo
- Conteúdo informacional primeiro (artigos), depois comercial (reviews)
- Disclosure de afiliado incluído automaticamente
- Slug gerado a partir da keyword

## Modos de Operação
- **Template-based (padrão)**: Usa templates prontos adaptáveis por keyword e nicho. Funciona sem API key.
- **LLM (futuro)**: Quando OPENAI_API_KEY estiver configurada, usará IA para gerar conteúdo único e otimizado para SEO.

## Observações
- Modo template é funcional e produz artigos de 300-800 palavras
- Para produção real com conteúdo único, configurar integração com OpenAI ou similar
- Meta-description gerada automaticamente para SEO
