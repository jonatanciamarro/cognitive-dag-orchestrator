# EmailMarketingAgent

## Função
Gera sequências completas de email marketing automatizadas com ofertas de afiliados.

## Entrada
- Keywords e oportunidades (do SEOResearchAgent)
- Ofertas de afiliados (do OfferLookupAgent)
- Nicho da campanha

## Saída
- Múltiplas sequências de emails (boas-vindas, promoção, nutrição)
- Assunto, preheader e corpo para cada email
- Delay em dias para automação
- Ofertas de afiliados incorporadas naturalmente

## Sequências Disponíveis
- **Boas-Vindas** (3 emails): Aquecimento → Educação → Conversão
- **Promocional** (2 emails): Apresentação → Urgência
- **Nutrição** (4 emails): Engajamento → Inspiração → Recomendação → Relacionamento

## Regras
- Disclosure de afiliado incluído nos emails com ofertas
- Delay configurável entre emails (dias)
- Lead magnet sugerido para captura
- Tom educacional e de valor, nunca agressivo

## Observações
- Conteúdo gerado por template com placeholders personalizáveis
- Em produção: integrar com Mailchimp, ConvertKit ou SendGrid API
- Placeholders como {{nome}} e {{nome_remetente}} substituídos pela plataforma de email
