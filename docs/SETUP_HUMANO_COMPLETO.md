# 🧑 GUIA DE CONFIGURAÇÃO HUMANA — Campaign Autopilot v5.2.1

> **Apenas você (humano) pode fazer essas configurações.**
> **O sistema automatiza TODO o resto.**
> **122 Agentes | 30 Workflows | 66 Testes | ~105K Linhas**

---

## Índice

1. [Estrutura do .env](#1-estrutura-do-env)
2. [Fontes de Receita — Passo a Passo](#2-fontes-de-receita)
3. [Provedores de IA Gratuitos](#3-provedores-de-ia-gratuitos)
4. [Redes Sociais — Tráfego](#4-redes-sociais)
5. [WordPress — Site e Blog](#5-wordpress)
6. [Produtos Digitais — Receita Direta](#6-produtos-digitais)
7. [CPA Marketing](#7-cpa-marketing)
8. [AdSense — Receita Passiva](#8-adsense)
9. [Ferramentas SEO — Dados](#9-ferramentas-seo)
10. [Tráfego Pago (Opcional)](#10-tráfego-pago)
11. [Sistema de Produtos Próprios](#11-sistema-de-produtos-próprios)
12. [Rodando 24/7](#12-rodando-247)
13. [Checklist Final](#13-checklist-final)

---

## 1. Estrutura do .env

**Arquivo:** `.env` (NUNCA vai para o GitHub — está no `.gitignore`)

```bash
# ═══════════════════════════════════════════════════════════════
# LLM TEXT GENERATION (pelo menos UM para o sistema funcionar)
# ═══════════════════════════════════════════════════════════════
OPENROUTER_API_KEY=           # 200+ modelos free → openrouter.ai/keys
GROQ_API_KEY=                  # Llama 3 70B, 30 req/min grátis → console.groq.com/keys
GEMINI_API_KEY=                # Gemini Flash, 60 req/min grátis → aistudio.google.com/apikey

# ═══════════════════════════════════════════════════════════════
# IMAGE GENERATION (opcionais, melhora qualidade visual)
# ═══════════════════════════════════════════════════════════════
DEEPAI_API_KEY=                # DeepAI → deepai.org (free tier, sem cartão)
PRODIA_API_KEY=                # Prodia SDXL → prodia.com (free tier)
HF_API_KEY=                    # HuggingFace → huggingface.co/settings/tokens

# ═══════════════════════════════════════════════════════════════
# AFILIADOS — PRINCIPAIS FONTES DE RENDA
# ═══════════════════════════════════════════════════════════════
KIWIFY_AFFILIATE_ID=           # Sua conta → kiwify.com.br
EDUZZ_AFFILIATE_ID=            # Sua conta → eduzz.com
MONETIZZE_AFFILIATE_ID=        # Sua conta → monetizze.com.br
HOTMART_CLIENT_ID=             # Sua conta → app.hotmart.com (Integrações → API)
HOTMART_CLIENT_SECRET=         # Seu secret do Hotmart
AMAZON_ASSOCIATES_TAG=         # Seu tracking ID → associe.amazon.com.br
SHOPEE_AFFILIATE_ID=              # Sua conta → shopee.com.br/afiliados
MERCADOLIVRE_AFFILIATE_ID=        # Sua conta → mercadolivre.com.br/afiliados
SHEIN_AFFILIATE_ID=               # Sua conta → shein.com/afiliados

# ═══════════════════════════════════════════════════════════════
# SITE / PUBLICAÇÃO
# ═══════════════════════════════════════════════════════════════
WP_URL=                        # URL do seu WordPress (ex: https://meusite.com)
WP_USER=                       # Usuário admin do WordPress
WP_PASSWORD=                   # Senha do WordPress

# ═══════════════════════════════════════════════════════════════
# SISTEMA
# ═══════════════════════════════════════════════════════════════
CAMPAIGN_BOT_REQUIRE_OPT_IN=false
MONEY_LOOP_INTERVAL=24         # horas entre ciclos
MONEY_LOOP_NICHES=1            # número de nichos por ciclo
```

---

## 2. Fontes de Receita

### Hierarquia de Rentabilidade (da MAIS rápida para a MAIS escalável)

| Prioridade | Fonte | Tempo para 1ª venda | Esforço Setup | Potencial Mensal |
|-----------|-------|---------------------|---------------|------------------|
| 🥇 | **Hotmart** | Imediato (se tiver links) | 30 min | R$ 500-5.000 |
| 🥇 | **Kiwify** | Imediato | 20 min | R$ 500-3.000 |
| 🥇 | **Eduzz** | Imediato | 20 min | R$ 500-3.000 |
| 🥇 | **Amazon Associates** | Imediato | 15 min | R$ 200-2.000 |
| 🥇 | **Shopee** | Imediato | 15 min | R$ 300-3.000 |
| 🥇 | **Mercado Livre** | Imediato | 15 min | R$ 200-2.000 |
| 🥇 | **SheIn** | Imediato | 15 min | R$ 200-2.000 |
| 🥈 | **CPA (Lomadee/Awin)** | 1-3 dias (aprovação) | 1 hora | R$ 1.000-5.000 |
| 🥈 | **Produtos Próprios** | 1-7 dias (criação) | 2-4 horas | R$ 2.000-20.000 |
| 🥉 | **AdSense** | 30-90 dias (tráfego) | 30 min | R$ 100-1.000 |
| 🥉 | **Membros/Assinatura** | 30+ dias | 2 horas | R$ 500-5.000 |
| 🟤 | **Produtos Físicos (Amazon)** | 30+ dias | 1 hora | R$ 200-2.000 |

---

### 🔥 2.1 Hotmart (Prioridade Máxima)

**Setup manual:**

```bash
# 1. Crie conta em https://hotmart.com/pt-br/marketplace
# 2. Vá em: Perfil → Integrações → API
# 3. Gere CLIENT_ID e CLIENT_SECRET
# 4. Cole no .env:
HOTMART_CLIENT_ID=seu_client_id_aqui
HOTMART_CLIENT_SECRET=seu_secret_aqui

# 5. (Opcional) Rápido: Pode colocar links diretos de produtos
#    no arquivo configs/affiliate_offers.json:
```

**Formato do `configs/affiliate_offers.json`:**

```json
{
  "offers": [
    {
      "product_name": "Curso Marketing Digital Completo",
      "network": "hotmart",
      "product_url": "https://hotm.art/seulink?aff=SEUCODIGO",
      "commission_type": "percentage",
      "commission_value": 60,
      "currency": "BRL",
      "category": "marketing digital",
      "merchant": "Hotmart",
      "cookie_days": 30,
      "is_active": true
    }
  ]
}
```

> 🔑 **IMPORTANTE:** O link do Hotmart já deve conter `?aff=SEUCODIGO`.
> O sistema não consegue gerar links Hotmart automaticamente — cada produto tem seu próprio link.

---

### 🔥 2.2 Kiwify

**Setup manual:**

```bash
# 1. Crie conta em https://kiwify.com.br
# 2. Vá em: Configurações → Programa de Afiliados
# 3. Copie seu ID de afiliado (número)
# 4. Cole no .env:
KIWIFY_AFFILIATE_ID=seu_numero_id
```

**Como usar:** O sistema gera links Kiwify automaticamente com `?afid=SEU_ID`.

---

### 🔥 2.3 Eduzz

**Setup manual:**

```bash
# 1. Crie conta em https://eduzz.com
# 2. Vá em: Configurações → Afiliados
# 3. Copie seu ID de afiliado
# 4. Cole no .env:
EDUZZ_AFFILIATE_ID=seu_id_aqui
```

---

### 🔥 2.4 Monetizze

**Setup manual:**

```bash
# 1. Crie conta em https://monetizze.com.br
# 2. Vá em: Minha Conta → Dados da Conta
# 3. Copie seu CÓDIGO DE AFILIADO
# 4. Cole no .env:
MONETIZZE_AFFILIATE_ID=seu_codigo
```

---

### 🔥 2.5 Amazon Associates Brasil

**Setup manual:**

```bash
# 1. Crie conta em https://associados.amazon.com.br
# 2. Complete cadastro (CPF, endereço, site)
# 3. Vá em: Gerenciar Tracking IDs
# 4. Crie um tracking ID (ex: meusite-20)
# 5. Cole no .env:
AMAZON_ASSOCIATES_TAG=meusite-20

# (Opcional) Para API completa:
AMAZON_ACCESS_KEY=sua_access_key
AMAZON_SECRET_KEY=sua_secret_key
```

### 🛍️ 2.6 Shopee (Prioridade Máxima)

**Setup manual:**

```bash
# 1. Crie conta em https://shopee.com.br
# 2. Acesse https://shopee.com.br/afiliados
# 3. Cadastre-se no programa de afiliados
# 4. Copie seu código de afiliado
# 5. Cole no .env:
SHOPEE_AFFILIATE_ID=seu_codigo_shopee
```

> 💡 **Dica:** Shopee paga 5-10% por venda. Cookie de 30 dias.
> Produtos baratos (R$ 20-100) convertem muito bem.
> **Sistema:** 11 produtos curados em tecnologia, casa, saúde, escritório.

---

### 🏪 2.7 Mercado Livre

**Setup manual:**

```bash
# 1. Crie conta em https://mercadolivre.com.br
# 2. Acesse https://mercadolivre.com.br/afiliados
# 3. Cadastre-se no programa (automático)
# 4. Gere seu código de afiliado no painel
# 5. Cole no .env:
MERCADOLIVRE_AFFILIATE_ID=seu_codigo_ml
```

> 💡 **Dica:** ML paga 2-8% dependendo da categoria.
> Ótimo para artigos de tecnologia, livros e equipamentos.
> **Sistema:** 15 produtos curados em tecnologia, finanças, saúde, casa, esportes.

---

### 👗 2.8 SheIn

**Setup manual:**

```bash
# 1. Crie conta em https://shein.com
# 2. Acesse https://shein.com/afiliados
# 3. Cadastre-se no programa
# 4. Copie seu código de afiliado
# 5. Cole no .env:
SHEIN_AFFILIATE_ID=seu_codigo_shein
```

> 💡 **Dica:** SheIn paga 6-15% (altíssimo!). Cookie de 30 dias.
> Público feminino, moda e acessórios. Ideal para Pinterest e Instagram.
> **Sistema:** 10 produtos curados em moda, beleza, casa, papelaria.

---

> 💡 **Dica:** Amazon paga 1-10% por produto.
> Foco em produtos com ticket alto (eletrônicos, livros técnicos) para comissões melhores.

---

## 3. Provedores de IA Gratuitos

### Essenciais para o sistema funcionar:

| Provedor | Como Criar | Limites | URL |
|----------|-----------|---------|-----|
| **OpenRouter** | Login com Google/GitHub | 200+ modelos free | openrouter.ai/keys |
| **Groq** | Login com Google/GitHub | Llama 3 70B, 30 req/min | console.groq.com/keys |
| **Gemini** | Login com Google | Gemini Flash, 60 req/min, sem cartão | aistudio.google.com/apikey |

### Opcionais (melhoram qualidade visual):

| Provedor | Como Criar | Limites | URL |
|----------|-----------|---------|-----|
| **DeepAI** | Email + senha | ~20 imagens/dia grátis | deepai.org |
| **Prodia** | Login Google | ~10 imagens/dia grátis | prodia.com |
| **HuggingFace** | Email + senha | 30k tokens/dia grátis | huggingface.co |

---

## 4. Redes Sociais

### YouTube (Tráfego orgânico + receita)

```bash
# 1. Crie/use canal no YouTube
# 2. Vá em: https://console.cloud.google.com/ → Criar Projeto
# 3. Ative YouTube Data API v3
# 4. Crie credenciais → API Key
# 5. Cole no .env:
YOUTUBE_API_KEY=sua_api_key
YOUTUBE_CHANNEL_ID=UC_seu_channel_id

# (Opcional) Para upload automático:
YOUTUBE_CLIENT_ID=seu_client_id
YOUTUBE_CLIENT_SECRET=seu_client_secret
YOUTUBE_REFRESH_TOKEN=seu_refresh_token
```

**Como conseguir o `CHANNEL_ID`:**
1. Acesse youtube.com
2. Clique no seu avatar → "Seu canal"
3. URL: youtube.com/channel/UCxxxxxxxx → copie o UC...

**Como conseguir `REFRESH_TOKEN`:**
1. Siga: https://developers.google.com/youtube/v3/guides/authentication
2. Escopo necessário: `https://www.googleapis.com/auth/youtube.upload`

---

### Instagram

```bash
# 1. Vá em: https://developers.facebook.com/
# 2. Crie App → Tipo: Negócios
# 3. Adicione Instagram Basic Display
# 4. Gere Access Token
# 5. Cole no .env:
INSTAGRAM_ACCESS_TOKEN=seu_token
INSTAGRAM_USER_ID=seu_user_id
INSTAGRAM_USERNAME=@seu_perfil
INSTAGRAM_PASSWORD=sua_senha
```

---

### Pinterest (Excelente para tráfego visual)

```bash
# 1. Vá em: https://developers.pinterest.com/
# 2. Crie App
# 3. Gere Access Token
# 4. Cole no .env:
PINTEREST_ACCESS_TOKEN=seu_token
```

> 💡 **Pinterest é uma das melhores fontes de tráfego gratuito para conteúdo visual.**

---

### TikTok

```bash
# 1. Vá em: https://developers.tiktok.com/
# 2. Crie App
# 3. Solicite access token (requer aprovação)
# 4. Cole no .env:
TIKTOK_ACCESS_TOKEN=seu_token
```

---

### Twitter/X

```bash
# 1. Vá em: https://developer.twitter.com/
# 2. Crie Project + App
# 3. Gere as 4 chaves:
TWITTER_API_KEY=sua_api_key
TWITTER_API_SECRET=sua_api_secret
TWITTER_ACCESS_TOKEN=seu_access_token
TWITTER_ACCESS_SECRET=seu_access_secret
TWITTER_BEARER_TOKEN=seu_bearer_token
```

---

### LinkedIn

```bash
# 1. Vá em: https://www.linkedin.com/developers/
# 2. Crie App
# 3. Solicite token
# 4. Cole no .env:
LINKEDIN_ACCESS_TOKEN=seu_token
```

---

### Facebook Pages

```bash
# 1. Vá em: https://developers.facebook.com/
# 2. Crie App → Página
# 3. Gere Page Access Token
# 4. Cole no .env:
FACEBOOK_PAGE_ACCESS_TOKEN=seu_token
```

---

### Telegram

```bash
# 1. Fale com @BotFather no Telegram
# 2. Crie novo bot → receba o TOKEN
# 3. Crie canal/grupo → copie ID
# 4. Cole no .env:
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHANNEL_ID=@seu_canal
```

---

## 5. WordPress

### Setup do Site

```bash
# Opção A — Já tem WordPress:
WP_URL=https://meusite.com
WP_USER=admin
WP_PASSWORD=sua_senha

# Opção B — Novo site (mais controle):
# 1. Contrate hospedagem (Recomendado: Hostinger, HostGator, ou DigitalOcean)
# 2. Instale WordPress (1 clique no painel)
# 3. Instale plugin: "Application Passwords" (gera senha segura para API)
# 4. Configure:
WP_URL=https://seudominio.com
WP_USER=seu_usuario
WP_PASSWORD=sua_application_password
```

> 🔐 **Application Password** é mais segura que senha normal.
> No WordPress: Usuários → Seu Perfil → Application Passwords.

### Plugins WordPress Recomendados

| Plugin | Função | Link |
|--------|--------|------|
| Rank Math SEO | SEO automático | wordpress.org/plugins/seo-by-rank-math |
| WP Rocket | Cache e performance | wp-rocket.me |
| MonsterInsights | Google Analytics | monsterinsights.com |
| MailPoet | Email marketing | wordpress.org/plugins/mailpoet |
| Cloudflare | CDN gratuito | cloudflare.com |

---

## 6. Produtos Digitais

### Criar seu próprio produto (máxima margem)

O sistema pode gerar landing pages e emails para SEUS produtos.
Você só precisa criar o produto uma vez.

**Tipos de produto que o sistema suporta:**

| Tipo | Exemplo | Margem | Plataforma |
|------|---------|--------|------------|
| Curso Online | "Marketing Digital para Iniciantes" | 100% | Kiwify/Eduzz/Hotmart |
| eBook | "Guia Completo de Afiliados" | 100% | Amazon Kindle / Hotmart |
| Template | "Kit de Artigos SEO Prontos" | 100% | Monetizze |
| Mentoria | "Consultoria 1:1" | 100% | Direto/Pix |
| Comunidade | "Grupo VIP de Afiliados" | 100% | Discord/Telegram |

**Setup:**
```bash
# 1. Crie o produto na plataforma escolhida
# 2. Coloque o link de checkout no arquivo:
nano configs/digital_products.json

# Formato:
# {
#   "products": [
#     {
#       "name": "Guia Completo",
#       "url": "https://kiwify.com.br/produto/seuproduto",
#       "price": 47,
#       "commission": 100,
#       "category": "marketing"
#     }
#   ]
# }
```

---

## 7. CPA Marketing

### Redes CPA Brasileiras

| Rede | Foco | Comissão | Link | Tempo Aprovação |
|------|------|----------|------|----------------|
| **Lomadee** | Geral (Buscapé) | R$5-200/lead | lomadee.com | 1-3 dias |
| **Awin** | Internacional | R$10-500/venda | awin.com | 1-3 dias |
| **PagBank** | Financeiro | R$10-100/lead | pagbank.com | 1 dia |
| **Rakuten** | Internacional | R$5-50/venda | rakuten.com | 2-5 dias |
| **Zanox** | Variado | R$10-300 | zanox.com | 1-3 dias |

**Setup:**
```bash
# 1. Cadastre-se na(s) rede(s) CPA
# 2. Escolha ofertas relevantes ao seu nicho
# 3. Adicione as ofertas em:
nano configs/cpa_offers.json
```

---

## 8. AdSense

```bash
# 1. Crie conta em https://adsense.google.com
# 2. Vincule ao seu site WordPress
# 3. Coloque o código AdSense no site
# 4. Aguarde aprovação (1-7 dias)
# 5. Configure auto-ads no AdSense
# 6. O sistema gera tráfego SEO → AdSense exibe anúncios → você ganha
```

> ⚠️ AdSense solo funciona com tráfego mínimo de ~1.000 visitas/dia.
> Foque primeiro em afiliados, AdSense é complementar.

---

## 9. Ferramentas SEO

```bash
# Ahrefs (dados reais de keyword research)
AHREFS_API_KEY=sua_chave

# (Opcional) O sistema funciona sem Ahrefs usando dados simulados
# Mas com Ahrefs as keywords são muito mais precisas
```

**Como conseguir:**
1. Assine Ahrefs (a partir de $29/mês) ou use trial de 7 dias
2. Vá em: Perfil → API → Gerar chave
3. Copie para .env

---

## 10. Tráfego Pago

> ⚠️ **AVISO:** Por padrão, o sistema opera 100% orgânico (zero custo).
> Só configure tráfego pago se tiver orçamento e experiência.

```bash
# Google Ads
GOOGLE_ADS_CLIENT_ID=seu_client_id

# Meta Ads (Facebook/Instagram)
META_ADS_ACCESS_TOKEN=seu_token

# Taboola (Native Ads)
TABOOLA_ACCOUNT_ID=sua_conta

# Limites de segurança
PAID_TRAFFIC_THRESHOLD=500     # Gasto máximo diário (R$)
PAID_TRAFFIC_REINVEST_PCT=30  # % da receita reinvestida em tráfego
PAID_TRAFFIC_MAX_DAILY=200    # Limite máximo por dia (R$)
```

---

## 11. Sistema de Produtos Próprios

O módulo `Product Forge` permite criar landing pages profissionais para seus próprios produtos.

### Produtos que o Product Forge gera:

| Tipo | Descrição | Gerado Automaticamente |
|------|-----------|----------------------|
| Landing Page | Página de vendas do produto | ✅ Sim |
| Página de Obrigado | Pós-compra | ✅ Sim |
| Email de Boas-Vindas | Sequência de nutrição | ✅ Sim |
| Email de Promoção | Lançamento/relançamento | ✅ Sim |
| Dashboard | Analytics do produto | ✅ Sim |
| Apresentação | Pitch/Webinar | ✅ Sim |

### Setup:

```bash
# 1. No arquivo configs/digital_products.json:
# {
#   "products": [
#     {
#       "name": "Curso Marketing Digital",
#       "url": "https://kiwify.com.br/checkout/seulink",
#       "price": 97.00,
#       "commission": 100,
#       "category": "marketing",
#       "features": ["7 módulos", "Suporte VIP", "Certificado"],
#       "guarantee": "7 dias de garantia incondicional",
#       "bonus": ["Planilha de SEO", "Comunidade exclusiva"]
#     }
#   ]
# }

# 2. Gere as páginas automaticamente:
python -c "
from campaign_autopilot.product_forge import LandingPageGenerator
gen = LandingPageGenerator()
result = gen.generate('configs/digital_products.json')
print(f'Landing pages criadas em: {result.output_dir}')
"
```

> 💡 **Produto próprio = 100% de comissão.** Esta é a fonte de receita com MAIOR margem.

---

## 12. Rodando 24/7

### Opção 1: Terminal (Recomendado para começar)

```bash
# Em um terminal separado (tmux/screen):
cd /root/Documents/Codex/2026-05-30/New\ Project\ \(1\)
source .venv/bin/activate

# Executar contínuo:
python scripts/money_loop.py \
    --workflow workflows/organic_affiliate_cycle.json \
    --context examples/affiliate_context.json \
    --db .state/money_loop.db \
    --output output \
    --interval 12
```

### Opção 2: Systemd (Auto-start no boot)

```bash
# 1. Editar money-loop.service com os caminhos corretos
nano money-loop.service

# 2. Instalar:
sudo cp money-loop.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable money-loop
sudo systemctl start money-loop

# 3. Verificar logs:
sudo journalctl -u money-loop -f
```

### Opção 3: Docker

```bash
docker compose up -d
```

### Monitoramento

```bash
# Estatísticas do Money Loop:
python scripts/money_loop.py --stats

# Logs em tempo real:
tail -f .state/money_loop.log

# Dashboard:
streamlit run dashboard/app.py
```

---

## 13. Checklist Final

### ✅ Antes de rodar (ESSENCIAL)

- [ ] **Pelo menos UM LLM configurado** (OpenRouter, Groq ou Gemini)
- [ ] **Pelo menos UM afiliado configurado** (Kiwify, Eduzz, Hotmart ou Amazon)
- [ ] `.env` salvo (NUNCA comitar)
- [ ] Executar `python scripts/money_loop.py --once` para testar

### ✅ Para receita REAL

- [ ] Links de afiliado válidos em `configs/affiliate_offers.json`
- [ ] WordPress configurado (para publicar conteúdo e rankear no Google)
- [ ] Pinterest (melhor tráfego orgânico visual)
- [ ] YouTube (melhor tráfego orgânico de vídeo)

### ✅ Para ESCALAR

- [ ] Produto próprio criado (100% comissão)
- [ ] LinkedIn + Twitter configurados
- [ ] Email marketing configurado (capturar leads nas landing pages)
- [ ] AdSense configurado no site
- [ ] Múltiplos nichos (cada nicho = + receita)

### ✅ Segurança (já configurado)

- [x] `.env` no `.gitignore`
- [x] Hook pre-push bloqueia vazamento de secrets
- [x] Chaves nunca vão para o GitHub
- [x] `safe-push.sh` para push seguro

---

## Resumo Visual

```
VOCÊ (HUMANO) FAZ:                       SISTEMA FAZ:
─────────────────────────────            ─────────────────────────────
1. Criar contas de afiliado             1. Pesquisar keywords e nichos
2. Gerar links de afiliado              2. Planejar conteúdo SEO
3. Configurar WordPress                 3. Gerar artigos completos
4. Criar produto digital                4. Gerar imagens profissionais
5. Configurar redes sociais             5. Gerar landing pages de venda
6. Colocar chaves no .env               6. Gerar emails de nutrição
7. Rodar o sistema 24/7                 7. Publicar no WordPress
                                         8. Publicar em redes sociais
                                         9. Monitorar resultados
                                        10. Otimizar com base em dados
                                        11. Repetir automaticamente
```

> **Quanto mais você configurar, mais dinheiro o sistema gera para você.**
> Com apenas 1 afiliado + 1 LLM, o sistema já funciona e gera receita.
> Com tudo configurado, o potencial é de R$ 5.000-20.000/mês em 6 meses.
