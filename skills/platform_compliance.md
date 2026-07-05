# PlatformComplianceAgent

## Função
Valida conteúdo contra regras específicas de cada plataforma (YouTube, Instagram, TikTok, Twitter, Pinterest, WhatsApp, Email, Site) para minimizar bloqueios, bans e penalidades.

## Entrada
- Step results de todos os agentes de marketing
- Canais configurados na campanha
- Política de compliance

## Saída
- Status geral (pass/warn/block)
- Relatório por plataforma com issues e gravidade
- Sugestões de correção para cada problema

## Plataformas Verificadas

| Plataforma | Regras | Criticidade |
|------------|--------|-------------|
| YouTube | Termos restritos, copyright, affiliate disclosure, conteúdo proibido | Alta |
| Instagram | Community guidelines, hashtags, link policy, bots | Alta |
| TikTok | Community guidelines, áudio, desafios perigosos, faixa etária | Alta |
| Twitter/X | Spam, hate speech, manipulation, affiliate rules | Média |
| Pinterest | Spam, copyright, pin quality, link integrity | Média |
| WhatsApp | Opt-in, LGPD, spam, horário comercial | Alta |
| Email | CAN-SPAM, LGPD, opt-out, required elements | Alta |
| Site/Blog | LGPD, affiliate disclosure, SEO guidelines | Média |

## Regras Gerais

1. **Disclosure de Afiliado**: Obrigatório em TODAS as plataformas
2. **LGPD**: Consentimento explícito para coleta de dados no Brasil
3. **Opt-Out**: Link de descadastro obrigatório em emails
4. **Conteúdo Original**: Plágio e cópia são proibidos em todas as plataformas
5. **Termos Restritos**: "Garantido", "dinheiro fácil", "milagroso" são bandeiras vermelhas
6. **Práticas Proibidas**: Bots, comprar seguidores, engajamento artificial

## Fluxo de Trabalho Recomendado

```
ContentGenerator → PlatformComplianceAgent → Ajustes → Publicação
                        ↓
               Se block: corrigir conteúdo
               Se warn: revisar recomendações
               Se pass: publicar com segurança
```
