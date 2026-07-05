# ContentPlannerAgent

## Função
Combina pesquisa SEO com ofertas de afiliados para produzir briefings de conteúdo.

## Entrada
- Keywords e oportunidades (do SEOResearchAgent)
- Ofertas disponíveis (do OfferLookupAgent)
- Lições da memória (do MemoryLookupAgent)

## Saída
- Lista de briefings com outline
- Estratégia de conteúdo
- Ofertas de afiliados vinculadas

## Regras
- Match keyword → oferta por categoria
- Outline adaptado à intenção de busca
- Máximo 5 briefings por ciclo
- Priorizar keywords com maior volume e menor dificuldade

## Observações
- Links de afiliado devem ser inseridos naturalmente no conteúdo
- Disclosure de afiliado obrigatório
