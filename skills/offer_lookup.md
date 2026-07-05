# OfferLookupAgent

## Função
Busca ofertas de afiliados compatíveis com o nicho e palavras-chave.

## Entrada
- Nicho (do campaign context)
- Keywords pesquisadas (do SEOResearchAgent)

## Saída
- Lista de ofertas com score de match
- Comissão estimada por venda
- Redes de afiliados disponíveis

## Regras
- Match por categoria e nome do produto
- Priorizar Hotmart (cookie 30 dias, comissão alta)
- Amazon para produtos físicos (comissão menor mas maior conversão)
- Máximo 10 ofertas por ciclo

## Observações
- Atualmente usa catálogo simulado
- Em produção: integrar API da Hotmart, Amazon Associates, Monetizze
