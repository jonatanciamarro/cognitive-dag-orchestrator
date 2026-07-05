# ContentRepurposerAgent

## Função
Multiplica conteúdo automaticamente: 1 artigo do blog → YouTube + Pinterest + WhatsApp + Email + Social. Elimina trabalho duplicado entre canais.

## Entrada
- Artigos gerados (do ContentGeneratorAgent)
- Ofertas de afiliados (do OfferLookupAgent)
- Keywords (do SEOResearchAgent)

## Saída
Para cada artigo, gera automaticamente:
- 🎬 YouTube: título + descrição com links + tags
- 📌 Pinterest: título + descrição SEO + board
- 📱 WhatsApp: mensagem pronta para broadcast
- 📧 Email: assunto + preview + CTA
- 🐦 Social: post para Twitter/LinkedIn

## Métrica
Multiplicador 5x: cada artigo vira 5 formatos diferentes.

## Regras
- Links de afiliado incluídos em todos os formatos
- Conteúdo adaptado ao formato de cada canal
- Disclosure mantido em todos os canais
- Tags e SEO otimizados por plataforma

## Observações
- Este agente roda após content_generator
- Substitui youtube_marketing, pinterest_marketing, whatsapp_marketing, email_marketing se usado sozinho
- Economia massiva de tempo: 1 artigo → 5 canais
