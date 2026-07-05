# WhatsAppMarketingAgent

## Função
Gera estratégia completa de marketing no WhatsApp: mensagens de boas-vindas, dicas, ofertas, engajamento e resumo semanal.

## Entrada
- Keywords e oportunidades (do SEOResearchAgent)
- Ofertas de afiliados (do OfferLookupAgent)
- Artigos gerados (do ContentGeneratorAgent)

## Saída
- 5 tipos de mensagem: boas-vindas, dica, oferta, engajamento, resumo semanal
- Agendamento semanal (~7 mensagens/semana)
- Estratégia de crescimento

## Tipos de Mensagem
- **Boas-Vindas**: Imediata ao entrar na lista
- **Dica Rápida**: Segunda, quarta, sexta (3x/semana)
- **Oferta Exclusiva**: Quinta-feira
- **Pergunta de Engajamento**: Sábado
- **Resumo Semanal**: Domingo

## Regras
- Disclosure de afiliado obrigatório em ofertas
- Tom educacional e não agressivo
- Mensagens curtas para mobile

## Integração
- Em produção: WhatsApp Business API, WATI, Z-API, Evolution API
- Link de convite para captura: wa.me/55...
