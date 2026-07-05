# 🏆 Guia Completo: Afiliados, CPA e Redes de Monetização

> Como criar contas, conectar ao sistema e configurar cada rede para começar a ganhar dinheiro.

---

## 📋 Sumário

1. [Tipos de Monetização](#-tipos-de-monetização)
2. [Redes de Afiliado (Orgânico)](#-redes-de-afiliado-orgânico)
3. [Redes de CPA (Tráfego Pago)](#-redes-de-cpa-tráfego-pago)
4. [Redes de Ad Network (Anúncios)](#-redes-de-ad-network-anúncios)
5. [Como Ligar Cada Rede no Sistema](#-como-ligar-cada-rede-no-sistema)
6. [Configuração no .env](#-configuração-no-env)
7. [Configuração no affiliate_offers.json](#-configuração-no-affiliate_offersjson)
8. [Produtos Recomendados por Nicho](#-produtos-recomendados-por-nicho)
9. [Estratégia de Comissões](#-estratégia-de-comissões)
10. [Otimização de Conversão](#-otimização-de-conversão)
11. [Checklist de Configuração](#-checklist-de-configuração)

---

## 💰 Tipos de Monetização

O sistema suporta **6 modelos de receita simultâneos**:

| Modelo | Descrição | Ticket Médio | Cookie | Ideal Para |
|---|---|---|---|---|
| **Afiliado (comissão)** | Você ganha % da venda | R$ 27-497 | 7-365 dias | Cursos, e-books, SaaS |
| **CPA (custo por ação)** | Ganha por lead/instalação | R$ 2-50 | 30-90 dias | Apps, cadastros, formulários |
| **CPL (custo por lead)** | Ganha por lead gerado | R$ 1-15 | 30-90 dias | Seguros, financeiro, educação |
| **AdSense (CPM/CPC)** | Anúncios no site | R$ 0,50-5 CPM | — | Site com tráfego |
| **Produto Digital** | Seu próprio produto | R$ 27-197 | — | Authority no nicho |
| **Assinatura** | Receita recorrente | R$ 17-97/mês | — | Conteúdo exclusivo |

---

## 🌐 Redes de Afiliado (Orgânico)

### 1. 🥇 Hotmart — A Principal (Infoprodutos)

**Comissão:** 50-80% | **Cookie:** 7-30 dias | **Pagamento:** R$ 60 mínimo

```
Cadastro: https://hotmart.com/pt-br/register
Produtos: Cursos online, e-books, mentorias, assinaturas
Nichos: Todos (tecnologia, finanças, saúde, carreira)
```

**Configuração no sistema:**
```bash
# .env
HOTMART_AFFILIATE_ID=seu_codigo_aqui
# Seu código fica nos links: https://hotm.art/seu-produto?aff=SEU_CODIGO
```

**Como conseguir seu código:**
1. Crie conta na Hotmart (grátis)
2. Acesse o **Marketplace** → encontre um produto
3. Clique em **"Divulgar"** → copie o link com seu código de afiliado
4. O código aparece no link: `...?aff=SEUCODIGO123`

### 2. 🥈 Amazon Associates — (Produtos Físicos)

**Comissão:** 3-10% | **Cookie:** 24h | **Pagamento:** R$ 100 mínimo

```
Cadastro: https://associados.amazon.com.br/
Produtos: Eletrônicos, livros, casa, escritório
Nichos: Tecnologia, saúde, casa
```

**Configuração no sistema:**
```bash
# .env
AMAZON_TRACKING_ID=seunome-20
AMAZON_ACCESS_KEY=sua_chave_api
```

**Como conseguir:**
1. Crie conta no [Amazon Associates](https://associados.amazon.com.br/)
2. Faça seu primeiro link de afiliado
3. Seu Tracking ID aparece no link: `?tag=SEUTRACKINGID-20`
4. Cole este Tracking ID no `.env`

### 3. 🥉 Monetizze — (Infoprodutos Brasileiros)

**Comissão:** 50-80% | **Cookie:** 30-365 dias | **Pagamento:** R$ 80 mínimo

```
Cadastro: https://monetizze.com.br/cadastro-afiliado
Produtos: Infoprodutos nacionais
Nichos: Todos
```

### 4. Kiwify — (Infoprodutos, Crescendo Rápido)

**Comissão:** 50-85% | **Cookie:** 30-365 dias | **Pagamento:** R$ 50 mínimo

```
Cadastro: https://kiwify.com.br/
Produtos: Cursos, e-books, PDFs
Nichos: Todos
```

### 5. Eduzz — (Infoprodutos Internacionais)

**Comissão:** 50-80% | **Cookie:** 30-365 dias | **Pagamento:** R$ 60 mínimo

```
Cadastro: https://eduzz.com/
Produtos: Cursos, mentorias

### 6. 🏪 Mercado Livre — (Marketplace Brasileiro, Tráfego Orgânico)

**Comissão:** 2-8% | **Cookie:** 1 dia | **Pagamento:** A cada 2 semanas | **Destaque:** Maior e-commerce da América Latina

```
Cadastro: https://mercadolivre.com.br/afiliados
Produtos: Eletrônicos, livros, moda, casa, esportes, brinquedos
Nichos: Tecnologia, finanças (livros), saúde (equipamentos), casa, esportes
```

**Configuração no sistema:**
```bash
# .env
MERCADOLIVRE_AFFILIATE_ID=seu_codigo_ml
```

**Como conseguir seu código:**
1. Crie conta no [Mercado Livre](https://mercadolivre.com.br) (se já tiver, use a mesma)
2. Acesse [Programa de Afiliados ML](https://mercadolivre.com.br/afiliados)
3. Cadastre-se no programa (gratuito, aprovação automática)
4. Gere seu código de afiliado no painel
5. Cole no .env como `MERCADOLIVRE_AFFILIATE_ID`

**Produtos no sistema:** 15 produtos curados em 5 nichos
**Comissões médias:** Tecnologia 2-3% | Livros 4-6% | Esportes 3-5%

---

### 7. 🛍️ Shopee — (Marketplace Asiático, Alto Crescimento no BR)

**Comissão:** 5-10% | **Cookie:** 30 dias | **Pagamento:** Mensal | **Destaque:** Frete grátis, preços baixos, alta conversão

```
Cadastro: https://shopee.com.br/afiliados
Produtos: Eletrônicos, acessórios, casa, moda, beleza
Nichos: Tecnologia, casa, saúde, escritório, papelaria
```

**Configuração no sistema:**
```bash
# .env
SHOPEE_AFFILIATE_ID=seu_codigo_shopee
```

**Como conseguir seu código:**
1. Crie conta na [Shopee](https://shopee.com.br) (se já tiver, use a mesma)
2. Acesse [Shopee Afiliados](https://shopee.com.br/afiliados)
3. Cadastre-se (rápido, gratuito)
4. Copie seu código de afiliado do painel
5. Cole no .env como `SHOPEE_AFFILIATE_ID`

**Produtos no sistema:** 11 produtos curados em 6 nichos
**Comissões médias:** 5-8% dependendo da categoria

---

### 8. 👗 SheIn — (Moda e Acessórios, Público Feminino)

**Comissão:** 6-15% | **Cookie:** 30 dias | **Pagamento:** Mensal | **Destaque:** Alta comissão, público comprador por impulso

```
Cadastro: https://shein.com/afiliados
Produtos: Roupas, acessórios, bolsas, calçados, maquiagem
Nichos: Moda, beleza, casa (decoração), papelaria
```

**Configuração no sistema:**
```bash
# .env
SHEIN_AFFILIATE_ID=seu_codigo_shein
```

**Como conseguir seu código:**
1. Crie conta na [SheIn](https://shein.com) (se já tiver, use a mesma)
2. Acesse [SheIn Afiliados](https://shein.com/afiliados)
3. Cadastre-se no programa
4. Copie seu código de afiliado
5. Cole no .env como `SHEIN_AFFILIATE_ID`

**Produtos no sistema:** 10 produtos curados em 5 nichos
**Comissões médias:** 8-15% (excelente para artigos de moda e beleza)

---

### 6. Awin — (Marketplace Global)
Nichos: Todos
```

### 6. Awin — (Marketplace Global)

**Comissão:** 5-30% | **Cookie:** 7-30 dias | **Pagamento:** R$ 200 mínimo

```
Cadastro: https://www.awin.com/br/afiliados
Produtos: Grandes marcas (Netshoes, Americanas, etc.)
Nichos: Variados
```

### 7. Lomadee — (Marketplace Brasileiro)

**Comissão:** 3-15% | **Cookie:** 7-30 dias

```
Cadastro: https://www.lomadee.com/
Produtos: Magazine Luiza, Casas Bahia, etc.
Nichos: Tecnologia, casa
```

### 8. ClickBank — (Internacional, Altas Comissões)

**Comissão:** 50-75% | **Cookie:** 60 dias | **Pagamento:** USD

```
Cadastro: https://www.clickbank.com/
Produtos: Infoprodutos internacionais
Nichos: Saúde, finanças, desenvolvimento pessoal
```

---

## 🎯 Redes de CPA (Tráfego Pago)

> Quando você tiver receita suficiente e ativar tráfego pago, estas redes pagam por leads/ações.

### 1. 🔥 CPABuild — (CPA Internacional)

**Modelo:** CPL/CPI | **Pagamento:** USD | **Mínimo:** $50

```
Cadastro: https://cpabuild.com/
Ofertas: Instalação de apps, cadastros, formulários
Nichos: Tecnologia, games
```

### 2. 🔥 RevContent — (Native Ads + CPA)

**Modelo:** CPM/CPC | **Mínimo:** $100

```
Cadastro: https://revcontent.com/
Ofertas: Conteúdo patrocinado
Nichos: Finanças, saúde
```

### 3. 🔥 MaxBounty — (CPA Premium)

**Modelo:** CPL/CPA | **Pagamento:** USD | **Mínimo:** $100

```
Cadastro: https://www.maxbounty.com/
Ofertas: Financeiro, tecnologia, lead gen
Nichos: Finanças
```

### 4. 🔥 ShareASale — (CPA + Afiliado)

**Modelo:** CPA/% | **Pagamento:** USD

```
Cadastro: https://www.shareasale.com/
Ofertas: Milhares de programas
Nichos: Todos
```

### 5. 🔥 PagBrasil — (CPA Brasileiro)

**Modelo:** CPA/CPL | **Pagamento:** R$ | **Mínimo:** R$ 100

```
Cadastro: https://www.pagbrasil.com/
Ofertas: Lead gen para empresas brasileiras
Nichos: Financeiro, educação
```

### 6. 🔥 Veriente — (CPA Brasileiro)

**Modelo:** CPA/CPL | **Pagamento:** R$

```
Cadastro: https://veriente.com/
Ofertas: Cartões, crédito, seguros
Nichos: Finanças
```

---

## 📺 Redes de Ad Network (Anúncios)

### 1. Google AdSense

**Modelo:** CPC/CPM | **Pagamento:** R$ 100 mínimo

```
Cadastro: https://adsense.google.com/
Requisito: Site com conteúdo original (6+ meses recomendado)
```

### 2. Google Ad Manager (Premium)

**Modelo:** CPM | **Pagamento:** R$ 100 mínimo

```
Cadastro: https://admanager.google.com/
Requisito: 5M+ impressões/mês
```

### 3. Media.net (Contextual)

**Modelo:** CPC | **Pagamento:** $100

```
Cadastro: https://www.media.net/
Requisito: Tráfego qualificado
```

### 4. Taboola (Native Ads)

**Modelo:** CPM | **Pagamento:** $50

```
Cadastro: https://www.taboola.com/
Requisito: 500K+ visitas/mês
```

---

## 🔌 Como Ligar Cada Rede no Sistema

### Passo 1: Configure o `.env`

```bash
# Edite o arquivo .env na raiz do projeto
nano .env
```

Adicione todas as redes que você criou conta:

```env
# === REDES DE AFILIADO ===
HOTMART_AFFILIATE_ID=seu_codigo_aqui
AMAZON_TRACKING_ID=seunome-20
MONETIZZE_AFFILIATE_ID=seu_codigo
KIWIFY_AFFILIATE_ID=seu_codigo
EDUZZ_AFFILIATE_ID=seu_codigo

# === REDES DE CPA (para tráfego pago) ===
CPABUILD_API_KEY=sua_key
MAXBOUNTY_API_KEY=sua_key

# === AD NETWORKS ===
ADSENSE_PUBLISHER_ID=ca-pub-xxxxxxxxxx
```

### Passo 2: Configure o `configs/affiliate_offers.json`

Este arquivo mapeia **produtos** para **nichos**. O sistema usa isso para inserir links de afiliado nos artigos certos.

```bash
nano configs/affiliate_offers.json
```

**Estrutura:**
```json
{
  "affiliate_ids": {
    "hotmart": "${HOTMART_AFFILIATE_ID}",
    "amazon": "${AMAZON_TRACKING_ID}",
    "monetizze": "${MONETIZZE_AFFILIATE_ID}",
    "kiwify": "${KIWIFY_AFFILIATE_ID}",
    "eduzz": "${EDUZZ_AFFILIATE_ID}"
  },
  "offers_by_niche": {
    "tecnologia": [
      {
        "network": "amazon",
        "product_name": "Notebook Dell XPS 15",
        "product_url": "https://amzn.to/SEU_LINK_AQUI",
        "commission_value": 3.0,
        "keywords": ["notebook", "dell", "laptop"],
        "cookie_days": 1
      },
      {
        "network": "hotmart",
        "product_name": "Curso de Programação Completo",
        "product_url": "https://hotm.art/SEU_LINK?aff=${HOTMART_AFFILIATE_ID}",
        "commission_value": 60.0,
        "keywords": ["programação", "curso", "aprender codigo"],
        "cookie_days": 30
      }
    ],
    "financas": [...],
    "saude": [...],
    "carreira": [...]
  }
}
```

> 💡 **Dica:** As `keywords` são usadas para encontrar menções no artigo. Se o artigo mencionar "notebook", o sistema insere automaticamente o link do Notebook Dell.

### Passo 3: Sistema Usa Automaticamente

Quando você roda `run_all_niches.py`:

```
1. 🔍 Pesquisa keyword "melhor notebook 2026"
2. 📝 Gera artigo mencionando "notebook Dell"
3. 🔗 AffiliateLinkInserterAgent detecta "notebook" → insere link de afiliado
4. 🌐 Publica no site com disclosure
5. 📱 Publica nas redes sociais com link de afiliado
```

---

## 📦 Configuração no affiliate_offers.json

### Template Completo para Todos os Nichos

```json
{
  "_instructions": "Substitua SEU_LINK_AQUI pelos seus links reais de afiliado",
  "affiliate_ids": {
    "hotmart": "${HOTMART_AFFILIATE_ID}",
    "amazon": "${AMAZON_TRACKING_ID}",
    "monetizze": "${MONETIZZE_AFFILIATE_ID}",
    "kiwify": "${KIWIFY_AFFILIATE_ID}",
    "eduzz": "${EDUZZ_AFFILIATE_ID}"
  },
  "offers_by_niche": {
    "tecnologia": [
      { "network": "amazon", "product_name": "Notebook Dell", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 3.0, "keywords": ["notebook", "dell", "laptop"], "cookie_days": 1 },
      { "network": "amazon", "product_name": "Smartphone Samsung Galaxy", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 2.5, "keywords": ["smartphone", "celular", "samsung", "galaxy"], "cookie_days": 1 },
      { "network": "hotmart", "product_name": "Curso de Programação", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 60.0, "keywords": ["programação", "curso", "desenvolvedor"], "cookie_days": 30 },
      { "network": "hotmart", "product_name": "Ferramenta de IA", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 40.0, "keywords": ["inteligencia artificial", "ia", "automacao"], "cookie_days": 30 },
      { "network": "amazon", "product_name": "Mouse Logitech MX Master", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 4.0, "keywords": ["mouse", "logitech", "acessorio"], "cookie_days": 1 },
      { "network": "amazon", "product_name": "Monitor 4K Samsung", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 3.5, "keywords": ["monitor", "4k", "tela"], "cookie_days": 1 },
      { "network": "hotmart", "product_name": "Curso de Excel Avançado", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 70.0, "keywords": ["excel", "planilha", "escritorio"], "cookie_days": 30 }
    ],
    "financas": [
      { "network": "hotmart", "product_name": "Curso de Educação Financeira", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 50.0, "keywords": ["educação financeira", "financas", "dinheiro", "investir"], "cookie_days": 30 },
      { "network": "hotmart", "product_name": "Planilha de Orçamento", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 70.0, "keywords": ["planilha", "orcamento", "gastos", "controle"], "cookie_days": 30 },
      { "network": "amazon", "product_name": "Livro: Pai Rico Pai Pobre", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 10.0, "keywords": ["livro", "educação financeira", "riqueza"], "cookie_days": 1 },
      { "network": "hotmart", "product_name": "Curso de Investimentos", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 60.0, "keywords": ["investimento", "bolsa", "acoes", "renda"], "cookie_days": 30 }
    ],
    "saude": [
      { "network": "hotmart", "product_name": "Guia de Alimentação Saudável", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 60.0, "keywords": ["alimentação", "saudavel", "dieta", "nutricao", "emagrecer"], "cookie_days": 30 },
      { "network": "hotmart", "product_name": "Curso de Exercícios em Casa", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 50.0, "keywords": ["exercicio", "treino", "casa", "academia"], "cookie_days": 30 },
      { "network": "amazon", "product_name": "Tapete de Yoga", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 5.0, "keywords": ["yoga", "tapete", "alongamento"], "cookie_days": 1 },
      { "network": "hotmart", "product_name": "Curso de Meditação", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 60.0, "keywords": ["meditação", "ansiedade", "estresse", "bem estar"], "cookie_days": 30 }
    ],
    "carreira": [
      { "network": "hotmart", "product_name": "Curso de LinkedIn", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 60.0, "keywords": ["linkedin", "curriculo", "emprego", "carreira"], "cookie_days": 30 },
      { "network": "hotmart", "product_name": "Guia de Entrevista", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 70.0, "keywords": ["entrevista", "emprego", "selecao", "rh"], "cookie_days": 30 },
      { "network": "amazon", "product_name": "Livro: Como Fazer Amigos", "product_url": "https://amzn.to/SEU_LINK", "commission_value": 10.0, "keywords": ["livro", "carreira", "networking"], "cookie_days": 1 },
      { "network": "hotmart", "product_name": "Curso de Oratória", "product_url": "https://hotm.art/SEU_LINK", "commission_value": 60.0, "keywords": ["oratoria", "comunicação", "apresentação"], "cookie_days": 30 }
    ]
  }
}
```

---

## 🎯 Produtos Recomendados por Nicho

### 💻 Tecnologia
| Produto | Rede | Comissão | Ticket | Keywords |
|---|---|---|---|---|
| Notebook Dell/Alienware | Amazon | 3% | R$ 5.000+ | notebook, laptop, dell |
| Smartphone Samsung/Motorola | Amazon | 2,5% | R$ 2.000+ | celular, smartphone |
| Curso de Programação | Hotmart | 60% | R$ 197 | aprender programação |
| Curso de IA | Hotmart | 40% | R$ 97 | inteligencia artificial |
| Hospedagem de Site | Hotmart/Awin | 30% | R$ 19/mês | hospedagem, site |
| Plano de Internet | CPA (Veriente) | R$ 15/lead | — | internet fibra |

### 💰 Finanças
| Produto | Rede | Comissão | Ticket | Keywords |
|---|---|---|---|---|
| Curso de Investimentos | Hotmart | 60% | R$ 497 | investir, bolsa, ações |
| Planilha Financeira | Hotmart | 70% | R$ 47 | planilha, orçamento |
| Cartão de Crédito | CPA (Veriente) | R$ 20/lead | — | cartão, crédito |
| Seguro de Vida | CPA (PagBrasil) | R$ 10/lead | — | seguro, proteção |
| Livro Educação Financeira | Amazon | 10% | R$ 50 | livro finanças |

### 🏥 Saúde
| Produto | Rede | Comissão | Ticket | Keywords |
|---|---|---|---|---|
| Curso de Emagrecimento | Hotmart | 60% | R$ 197 | emagrecer, dieta |
| Curso de Exercícios | Hotmart | 50% | R$ 97 | treino, exercício |
| Suplementos | Amazon | 5% | R$ 100 | whey, creatina |
| Plano de Saúde | CPA | R$ 15/lead | — | plano de saúde |
| Curso de Meditação | Hotmart | 60% | R$ 47 | meditação, ansiedade |

### 🚀 Carreira
| Produto | Rede | Comissão | Ticket | Keywords |
|---|---|---|---|---|
| Curso de LinkedIn | Hotmart | 60% | R$ 97 | linkedin, perfil |
| Curso de Oratória | Hotmart | 60% | R$ 197 | oratória, falar bem |
| Curso de Inglês | Hotmart/CPA | 50% | R$ 497 | inglês, curso |
| Certificação Profissional | Amazon | 4% | R$ 300 | certificação |
| Curso de Excel | Hotmart | 70% | R$ 47 | excel, planilha |

---

## 💵 Estratégia de Comissões

### Ticket Alto vs Baixo

```
Ticket Alto (R$ 100-500): Hotmart, Eduzz, Monetizze
  → Menos vendas, mais dinheiro por venda
  → Ideal para conteúdo de fundo de funil (reviews, comparações)

Ticket Baixo (R$ 20-50): Amazon, Kiwify
  → Mais vendas, menos por venda
  → Ideal para conteúdo de topo de funil (listas, guias)

CPA (R$ 2-20/lead): Veriente, CPABuild
  → Conversão mais fácil (só cadastro)
  → Ideal para tráfego pago
```

### Combinando Redes no Mesmo Artigo

```
Artigo: "Melhores Notebooks 2026"
  ├── Amazon: Link para Notebook Dell (comissão 3%)
  ├── Hotmart: Link para Curso de Programação (comissão 60%)
  └── AdSense: Anúncios display no artigo
```

### Taxas de Conversão Realistas

| Tipo de Conteúdo | CTR no Link | Taxa de Conversão | Receita por 1000 visitas |
|---|---|---|---|
| Topo de funil (informativo) | 1-3% | 0,3-1% | R$ 5-20 |
| Meio de funil (comparativo) | 3-8% | 1-3% | R$ 20-80 |
| Fundo de funil (review) | 8-15% | 3-8% | R$ 80-300 |

---

## ✅ Checklist de Configuração

### 🔴 Passo 1: Criar Contas (Hoje)

- [ ] **Hotmart** — https://hotmart.com/ (imperdível)
- [ ] **Amazon Associates** — https://associados.amazon.com.br/ (imperdível)
- [ ] **Google AdSense** — https://adsense.google.com/ (para site)

### 🟡 Passo 2: Configurar no Sistema (Hoje)

- [ ] Editar `.env` com seus IDs de afiliado
- [ ] Editar `configs/affiliate_offers.json` com seus links
- [ ] Rodar teste: `python3 scripts/run_all_niches.py`
- [ ] Verificar se links aparecem nos artigos comerciais

### 🟢 Passo 3: Criar Contas Adicionais (Próximos Dias)

- [ ] **Monetizze** — https://monetizze.com.br/ (backup Hotmart)
- [ ] **Kiwify** — https://kiwify.com.br/ (altas comissões)
- [ ] **Awin** — https://www.awin.com/br (grandes marcas)
- [ ] **Lomadee** — https://www.lomadee.com/ (Magalu, Casas Bahia)

### 🔵 Passo 4: Para Tráfego Pago (Quando Tiver Receita)

- [ ] **Veriente** — https://veriente.com/ (CPA, cartões, seguros)
- [ ] **PagBrasil** — https://www.pagbrasil.com/ (CPA Brasil)
- [ ] **CPABuild** — https://cpabuild.com/ (CPA internacional)

---

## 🚀 Fluxo Completo de Monetização

```
📝 Artigo gerado → intenção comercial?
  ├── ❌ Informativo → AdSense (anúncios) → receita passiva
  └── ✅ Comercial → AffiliateLinkInserterAgent
        ├── 🔗 Amazon → link de produto físico
        ├── 🔗 Hotmart → link de infoproduto
        ├── 🔗 CPA → link de lead gen (se tráfego pago)
        └── 📱 Redes sociais → posts com links

💰 Receita gerada → RevenueMonitorAgent
  ├── < R$ 500/mês → continuar orgânico
  └── ≥ R$ 500/mês por 2 meses → ATIVAR TRÁFEGO PAGO
        ├── Google Ads → links de CPA + afiliado
        ├── Meta Ads → remarketing + ofertas
        └── Native Ads → reconhecimento de marca
```

> 💡 **Dica de Ouro:** Comece com **Hotmart + Amazon**. São as redes mais fáceis de aprovar e com maior variedade de produtos. Configure essas duas primeiro, depois adicione as outras.
