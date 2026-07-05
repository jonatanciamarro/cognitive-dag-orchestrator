# YouTubeMarketingAgent

## Função
Gera materiais completos para vídeos no YouTube: título SEO, descrição com links de afiliado, roteiro, tags.

## Entrada
- Keywords e oportunidades (do SEOResearchAgent)
- Ofertas de afiliados (do OfferLookupAgent)
- Nicho e canais da campanha

## Saída
- Título SEO do vídeo
- Descrição completa com timestamps e links de afiliado
- Roteiro com seções e timestamps
- Tags para descoberta no YouTube
- Disclosure de afiliado na descrição

## Regras
- Máximo 3 vídeos por ciclo
- Tipo de vídeo baseado na intenção de busca (informational → educational, commercial → review)
- Timestamps automáticos baseados no template
- Disclosure obrigatório na descrição
- Tags extraídas do nicho + keyword

## Tipos de Vídeo
- **Tutorial**: Passo a passo prático (~10min)
- **Review**: Análise de produto com prós e contras (~8min)
- **Educational**: Conteúdo informativo com tendências (~10min)

## Observações
- Roteiro gerado por template (pronto para gravação)
- Em produção com OPENAI_API_KEY: roteiros únicos e otimizados
- YouTube é a segunda maior ferramenta de busca — ideal para tráfego orgânico
