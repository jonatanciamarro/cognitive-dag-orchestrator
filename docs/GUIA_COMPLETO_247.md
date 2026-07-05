# 🚀 Guia Completo — Campaign Autopilot 24/7

> "Estou tão feliz agora que o dinheiro vem, em quantidades crescentes, através de múltiplas fontes e de forma contínua."

---

## 📋 Sumário

1. [O Que o Sistema Faz](#-o-que-o-sistema-faz)
2. [O que Acontece Quando Roda](#-o-que-acontece-quando-roda)
3. [Projeções e Estimativas de Ganhos](#-projeções-e-estimativas-de-ganhos)
4. [Como Rodar Agora](#-como-rodar-agora)
5. [Rodar 24/7](#-rodar-247)
6. [Rodar no Celular](#-rodar-no-celular-grátis)
7. [Configurar Links de Afiliado](#-configurar-links-de-afiliado)
8. [Monetização Multi-Fonte](#-monetização-multi-fonte)
9. [Quando Você Precisa Intervir](#-quando-você-precisa-intervir)
10. [O Que Falta Para Executar Hoje](#-o-que-falta-para-executar-hoje)
11. [Solução de Problemas](#-solução-de-problemas)

---

## 🤖 O Que o Sistema Faz

O Campaign Autopilot é um ecossistema de agentes de IA que **gera conteúdo automaticamente** e o distribui para **múltiplas fontes de renda**:

| Fonte de Renda | Como Funciona | Pagamento |
|---|---|---|
| **Links de Afiliado** | Artigos recomendam produtos com links | Comissão por venda |
| **Produtos Digitais** | Gera e oferece e-books/cursos grátis | Venda direta |
| **Assinaturas** | Conteúdo exclusivo para membros | Mensalidade |
| **Google AdSense** | Anúncios no site de notícias | CPM/CPC |
| **Email Marketing** | Captura leads e faz ofertas | Comissão por venda |

### Arquitetura em 3 Ondas

```
🌊 ONDA 1 — SEO & Conteúdo (gera tráfego)
  ├── Pesquisa keywords (sem custo)
  ├── Gera artigos otimizados (via LLM grátis)
  ├── Valida E-E-A-T (qualidade Google)
  ├── Insere links de afiliado
  └── Publica site estático

🌊 ONDA 2 — Múltiplas Fontes de Renda
  ├── Produtos digitais
  ├── Assinaturas
  ├── Email marketing
  └── Cross-selling entre nichos

🌊 ONDA 3 — Evolução e Transcendência
  ├── Agentes melhoram a si mesmos
  ├── Cross-pollination de conhecimento
  └── Sistema auto-otimizante
```

---

## ⚙️ O que Acontece Quando Roda

Quando você executa `python3 scripts/run_all_niches.py`, o sistema:

### 1. 🔍 Pesquisa Keywords (para cada nicho)
```
Tecnologia → "inteligência artificial", "melhores notebooks 2026"
Finanças   → "como economizar dinheiro", "investimentos"
Saúde      → "exercícios em casa", "alimentação saudável"
Carreira   → "cursos online gratuitos", "LinkedIn"
```

### 2. 📝 Gera Artigos (via LLM automática)
Cada artigo tem:
- Título SEO-otimizado
- Introdução, desenvolvimento e conclusão
- Meta-description
- Slug amigável
- Score de qualidade E-E-A-T

### 3. 🔗 Insere Links de Afiliado
Apenas em artigos **comerciais** (ex: "melhor notebook") — zero em conteúdo informacional. Segue as regras do Google:
- `rel="nofollow sponsored"`
- Disclosure visível
- Máx 3 links por artigo

### 4. 🌐 Publica Site Estático
Gera `site/index.html` com todos os artigos organizados por nicho.

### 5. 💰 Análise Financeira
Calcula portfólio, oportunidades de compounding, cross-pollination.

### Tempo Total: ~7 segundos por ciclo (4 nichos × 1 artigo)

---

## 📈 Projeções e Estimativas de Ganhos

### Cenário Conservador (1 ciclo/dia, 4 nichos)

| Métrica | Mês 1 | Mês 3 | Mês 6 | Mês 12 |
|---|---|---|---|---|
| Artigos no ar | 120 | 360 | 720 | 1.440 |
| Visitantes/mês | 21.638 | 64.914 | 129.828 | 259.656 |
| Afiliados (0,5% conv.) | R$ 108 | R$ 325 | R$ 649 | R$ 1.298 |
| AdSense (R$ 5 CPM) | R$ 108 | R$ 325 | R$ 649 | R$ 1.298 |
| Produtos Digitais | R$ 0 | R$ 200 | R$ 500 | R$ 1.000 |
| **Total Estimado** | **R$ 216** | **R$ 850** | **R$ 1.798** | **R$ 3.596** |

> ⚠️ **Aviso**: Projeções são estimativas. Resultados reais dependem de nicho, concorrência, qualidade do conteúdo e esforço de divulgação.

### Fórmula de Crescimento
```
Receita = Tráfego × Taxa de Conversão × Comissão Média

Tráfego = Artigos × Visitas/Artigo × (1 + Compounding)^meses
```

### Multiplicadores de Crescimento
| Alavanca | Impacto | Tempo |
|---|---|---|
| Mais nichos | 2× mais tráfego | Imediato |
| Mais artigos/dia | 3× mais conteúdo | Imediato |
| Backlinks | 2-3× tráfego SEO | 3-6 meses |
| Email marketing | 5× conversão | 1-3 meses |
| Cross-pollination | 1,5× receita | 2-4 meses |

---

## 🚀 Como Rodar Agora

### Pré-requisitos
```bash
# Python 3.10+
python3 --version

# Acessar o diretório do projeto
cd "/root/Documents/Codex/2026-05-30/New Project (1)"
```

### Executar Ciclo Único (recomendado para teste)
```bash
python3 scripts/run_all_niches.py
```

### Executar com Watch (roda a cada 24h)
```bash
python3 scripts/run_all_niches.py --watch
```

### Executar Modo Servidor Diário
```bash
python3 scripts/run_all_niches.py --daily
```

### Ver Status
```bash
python3 scripts/run_all_niches.py --status
```

### Controlar Quantidade de Artigos
```bash
python3 scripts/run_all_niches.py --articles 3
```

---

## 🕐 Rodar 24/7

### Método 1: Screen (Recomendado — Mais Simples)
```bash
# Iniciar sessão
screen -dmS autopilot bash -c "cd '/root/Documents/Codex/2026-05-30/New Project (1)' && python3 scripts/run_all_niches.py --watch"

# Ver status
screen -ls

# Anexar ao terminal (Ctrl+A D para desanexar)
screen -r autopilot

# Parar
screen -S autopilot -X quit
```

### Método 2: Daemon Completo
```bash
# Iniciar daemon
python3 scripts/autopilot_daemon.py

# Ver status
python3 scripts/autopilot_daemon.py --status

# Parar
python3 scripts/autopilot_daemon.py --stop
```

### Método 3: Script de Instalação
```bash
bash scripts/install_247.sh
```
Escolha: `screen` (simples), `systemd` (servidor) ou `docker` (container).

---

## 📱 Rodar no Celular (Grátis)

### Opção 1: Termux (Android — Recomendado)

1. **Instale Termux** (F-Droid) e **Termux:Boot**
2. **Conecte-se ao servidor ou rode local:**
```bash
# No Termux:
pkg install python git

# Clone ou copie o projeto
cd ~
# (copie os arquivos do projeto para o celular)

# Execute
python scripts/run_all_niches.py --watch
```

3. **Para manter rodando após fechar:**
```bash
# Instalar termux-services
pkg install termux-services

# Criar serviço
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/autopilot << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
cd ~/projeto
python scripts/run_all_niches.py --watch
EOF
chmod +x ~/.termux/boot/autopilot
```

### Opção 2: Servidor SSH (Recomendado para 24/7)
Use serviços grátis:
- **Oracle Cloud Free Tier**: VM sempre gratuita (4 ARM cores, 24GB RAM)
- **Google Cloud Free Tier**: VM f1-micro
- **AWS Free Tier**: EC2 t2.micro (12 meses)
- **Fly.io**: 3 VMs free
- **Render.com**: Serviço web free com cron

```bash
# Conectar ao servidor
ssh usuario@seu-servidor.com

# Instalar e rodar
git clone [seu-repo] /opt/autopilot
cd /opt/autopilot
python scripts/run_all_niches.py --daily
```

### Opção 3: GitHub Actions (Grátis — Sem Precisa de Servidor)
Crie `.github/workflows/daily.yml`:
```yaml
name: Daily Content Cycle
on:
  schedule:
    - cron: '0 8 * * *'  # Todo dia às 8h
  workflow_dispatch:       # Manual

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/run_all_niches.py
      - uses: peaceiris/actions-gh-pages@v3
        with:
          publish_dir: ./site
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🔗 Configurar Links de Afiliado

### 1. Edite o arquivo de ofertas
```bash
nano configs/affiliate_offers.json
```

### 2. Coloque seus IDs de afiliado no `.env`
```bash
HOTMART_AFFILIATE_ID=seu_codigo_aqui
AMAZON_TRACKING_ID=seunome-20
```

### 3. Substitua URLs de exemplo
No `configs/affiliate_offers.json`, troque:
- `https://amzn.to/3XABCD1` → seu link real da Amazon
- `https://hotm.art/seu-link-curso` → seu link real da Hotmart

### Redes de Afiliado (Todas Grátis para Cadastrar)

| Rede | Comissão | Cookie | Pagamento |
|---|---|---|---|
| **Amazon Associados** | 3-10% | 1 dia | R$ 100 mínimo |
| **Hotmart** | 50-80% | 30 dias | R$ 60 mínimo |
| **Monetizze** | 50-80% | 30 dias | R$ 80 mínimo |
| **Kiwify** | 50-80% | 30 dias | R$ 50 mínimo |
| **Eduzz** | 50-80% | 30 dias | R$ 60 mínimo |
| **PagSeguro** | 50-70% | 30 dias | R$ 100 mínimo |
| **Awin** | 5-30% | 7-30 dias | R$ 200 mínimo |
| **Tradelia** | 5-50% | 7-30 dias | R$ 150 mínimo |

### Regras Google (Sistema já segue automaticamente)
- ✅ `rel="nofollow sponsored"` em todos os links
- ✅ Disclosure visível no artigo
- ✅ Máximo 3 links por artigo
- ✅ Só em artigos comerciais (nunca informacionais)
- ✅ Links contextuais (relevantes ao conteúdo)

---

## 💰 Monetização Multi-Fonte

O sistema opera **4 fontes de renda simultâneas**:

### 1. Links de Afiliado (Automático)
Artigos comerciais recebem links automaticamente.

### 2. Google AdSense (Site de Notícias)
- Sistema gera site de notícias SEO-friendly
- Necessário criar conta no Google AdSense
- Colocar código do AdSense no template

### 3. Produtos Digitais (Automático)
- E-books, planilhas, templates
- Gerados pelo `DigitalProductAgent`
- Vendidos via Hotmart/Monetizze

### 4. Email Marketing (Automático)
- `LeadCaptureAgent` coleta emails
- `EmailMarketingAgent` envia sequências
- Sequências de conversão automáticas

---

## ⏰ Quando Você Precisa Intervir

| Situação | Precisa de Você? | Frequência |
|---|---|---|
| Sistema rodando | ❌ Não (automático) | — |
| Nova chave de API | ✅ Sim (1 vez) | A cada 3-6 meses |
| Novo produto afiliado | ✅ Sim (configurar) | Mensal |
| Ver resultados | ❌ Não (opcional) | Diário |
| Site caiu | ✅ Sim (redeploy) | Raro |
| Mudar nicho | ✅ Sim (config) | Trimestral |
| Problema técnico | 🤖 Autopilot tenta resolver | Raro |

### O Que o Autopilot Faz Sozinho
- ✅ Gera conteúdo
- ✅ Publica site
- ✅ Insere links de afiliado
- ✅ Monitora saúde do sistema
- ✅ Auto-recovery de falhas
- ✅ Otimiza estratégia
- ✅ Aprende com resultados

### Única Coisa que VOCÊ Precisa Fazer
1. **Configurar os links de afiliado** (1 vez)
2. **Criar contas nas redes** (1 vez)
3. **Ver o dinheiro entrar** 🤑

---

## ✅ O Que Falta Para Executar Hoje

### 🔴 Crítico (Fazer Agora)
- [ ] **Criar contas de afiliado** (Amazon, Hotmart)
- [ ] **Configurar IDs no `.env`** e `configs/affiliate_offers.json`

### 🟡 Importante (Próximos Dias)
- [ ] **Deploy do site** (GitHub Pages ou Cloudflare)
- [ ] **Criar conta Google AdSense**
- [ ] **Configurar email marketing** (opcional)

### 🟢 Legal de Ter
- [ ] **Dashboards de monitoramento**
- [ ] **Mais chaves de API** (Groq, Together, DeepInfra)
- [ ] **Domínio próprio** (ex: meusite.com)

---

## 🔧 Solução de Problemas

### "Chave de API não funciona"
```bash
# Verificar se .env está correto
cat .env

# Testar manualmente
python3 -c "
import sys; sys.path.insert(0, 'src')
from campaign_autopilot.free_llm_providers import generate_text
print(generate_text('diga oi', max_tokens=10))
"
```

### "Site não está sendo gerado"
```bash
python3 scripts/run_all_niches.py --articles 1
ls -la site/
```

### "Links de afiliado não aparecem"
```bash
# Verificar se o artigo é comercial (não insere em informacional)
# Verificar configs/affiliate_offers.json
# Verificar se os produtos mencionados estão cadastrados
```

### "Quero ver o que o sistema produziu"
```bash
# Site completo
open site/index.html

# Relatórios
ls .state/reports/
```

---

## 📊 Dashboard de Monitoramento (Opcional)

```bash
# Iniciar dashboard web
streamlit run dashboard/app.py

# Acessar: http://localhost:8501
```

---

## 🎯 Resumo

```
✅ Sistema funcionando AGORA com OpenRouter (LLM grátis)
✅ 4 nichos rodando em paralelo
✅ Links de afiliado configuráveis
✅ Site estático gerado automaticamente
✅ 24/7 via Screen/Termux/GitHub Actions

🔜 Configurar IDs de afiliado → Começar a ganhar dinheiro
🔜 Deploy do site → Tráfego orgânico do Google
🔜 Adicionar mais nichos → Mais tráfego e receita
```

> A frase se materializa quando o sistema roda **todos os dias**, gerando **conteúdo consistente** que atrai **tráfego orgânico** e converte em **comissões de afiliado** — sem você precisar fazer nada.


---

## 📱 Publicação Automática em Redes Sociais

O sistema gera e publica conteúdo em **8 plataformas** automaticamente. Cada plataforma tem um modo de operação:

### Status Atual: Posts Gerados, Publicação Manual

Neste momento, o sistema gera os posts prontos (em `output/social_posts/`) mas você precisa configurar as chaves de API para publicação automática.

### Para Ativar o AUTOPILOT TOTAL:

| Plataforma | O Que Configurar | Dificuldade | Tempo |
|---|---|---|---|
| **Telegram** 🥇 | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHANNEL_ID` | ⭐ Muito Fácil | 5 min |
| **Twitter/X** | `TWITTER_BEARER_TOKEN` | 🔵 Fácil | 15 min |
| **YouTube** | `YOUTUBE_CLIENT_ID` + OAuth | 🟡 Média | 30 min |
| **Instagram** | `INSTAGRAM_ACCESS_TOKEN` | 🟡 Média | 20 min |
| **Pinterest** | `PINTEREST_ACCESS_TOKEN` | 🔵 Fácil | 15 min |
| **LinkedIn** | `LINKEDIN_ACCESS_TOKEN` | 🟡 Média | 20 min |
| **TikTok** | `TIKTOK_ACCESS_TOKEN` | 🔴 Difícil | 30 min |
| **Facebook** | `FACEBOOK_PAGE_ACCESS_TOKEN` | 🟡 Média | 20 min |

### 📲 Telegram — O Mais Fácil (Faça Primeiro!)

```bash
# 1. Abra o Telegram e procure @BotFather
# 2. Envie /newbot, escolha um nome, copie o TOKEN
# 3. Adicione o bot ao seu canal como ADMIN
# 4. Configure no .env:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmNOPqrstUVwxyz
TELEGRAM_CHANNEL_ID=@meucanal

# Pronto! O sistema vai postar automaticamente todo ciclo.
```

### 🐦 Twitter/X — Fácil e Rápido

```bash
# 1. Acesse developer.twitter.com
# 2. Crie um app → Generate Bearer Token
# 3. Configure:
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAA...
```

### 🎬 YouTube — Upload Automático

```bash
# 1. Google Cloud Console → YouTube Data API v3
# 2. Criar OAuth 2.0 (Desktop app)
# 3. Gerar refresh token (uma vez)
# 4. Configurar:
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...
```

### 🔧 Sem API → Modo Semi-Automático

Se preferir não configurar APIs, o sistema salva **posts prontos** em:

```bash
output/social_posts/
├── telegram/      # Mensagens formatadas em HTML
├── youtube/       # Script + descrição + tags + thumbnail prompt
├── twitter/       # Thread completa
├── instagram/     # Legenda com hashtags
├── tiktok/        # Script de vídeo curto
├── pinterest/     # Pin com descrição SEO
├── linkedin/      # Post profissional
└── facebook/      # Post para página
```

Você só precisa **copiar e colar** em cada plataforma. 5 minutos por post.

### 📊 O que Acontece em Cada Ciclo

```
🚀 Ciclo diário (run_all_niches.py)
  ├── 🔍 Pesquisa keywords (4 nichos)
  ├── 📝 Gera artigos SEO (1-2 por nicho)
  ├── 🔗 Insere links de afiliado
  ├── 🌐 Publica site estático
  ├── 💰 Verifica receita para tráfego pago
  └── 📱 Publica em redes sociais
        ├── 📲 Telegram (se configurado → automático)
        ├── 🐦 Twitter (se configurado → automático)
        ├── 📸 Instagram (se configurado → automático)
        ├── 🎬 YouTube (se configurado → automático)
        └── 📁 Salva posts para as demais plataformas
```

### 🚀 Checklist para Autopilot Total

- [ ] **Telegram** configurado (5 min, mais fácil)
- [ ] **Twitter** configurado (15 min)
- [ ] **YouTube** configurado (30 min)
- [ ] Links de afiliado da **Amazon** e **Hotmart**
- [ ] Site publicado no **GitHub Pages**

Depois disso, o sistema roda **100% sozinho** — você só acompanha os resultados. 🚀
