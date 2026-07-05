# 🏆 Kiwify + Eduzz — Guia de Integração de Afiliados

> **Data:** 2026-06-27 | **Status:** ✅ Configurado no sistema
> **Total de Ofertas:** 13 Kiwify + 10 Eduzz + 6 Monetizze = **29 ofertas em 4 nichos**

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Kiwify](#kiwify)
3. [Eduzz](#eduzz)
4. [Monetizze](#monetizze)
5. [Ofertas Disponíveis por Nicho](#ofertas-disponíveis-por-nicho)
6. [Configuração no Sistema](#configuração-no-sistema)
7. [Como o Sistema Usa Essas Redes](#como-o-sistema-usa-essas-redes)
8. [Estratégia de Comissões](#estratégia-de-comissões)
9. [Próximos Passos](#próximos-passos)

---

## Visão Geral

O Campaign Autopilot suporta **9 redes de afiliados simultaneamente**:

| Rede | Tipo | Comissão | Cookie | Ofertas |
|---|---|---|---|---|
| **Hotmart** | Infoprodutos | 50-80% | 7-30 dias | 14 |
| **Amazon** | Produtos físicos | 3-10% | 1 dia | 6 |
| **Kiwify** | Infoprodutos | 50-85% | 30-365 dias | 13 |
| **Eduzz** | Infoprodutos | 50-80% | 30-365 dias | 10 |
| **Monetizze** | Infoprodutos | 50-80% | 30-365 dias | 6 |
| **Mercado Livre** | Marketplace | 2-8% | 1 dia | 15 |
| **Shopee** | Marketplace | 5-10% | 30 dias | 11 |
| **Shein** | Moda | 5-15% | 30 dias | 10 |
| **AliExpress** | Produtos importados | 3-10% | 30 dias | 10 |

**Total: 95 ofertas em 4 nichos** (tecnologia, finanças, saúde, carreira)

---

## Kiwify

### Sobre

A Kiwify é uma plataforma brasileira de infoprodutos que vem crescendo rapidamente. 
Oferece as maiores comissões do mercado (até 85%) e prazos de cookie longos (até 365 dias).

### URL Pattern

```
Formato: https://kiwify.app/NOME-DO-PRODUTO?aff={affiliate_id}
Exemplo: https://kiwify.app/curso-javascript?aff=SEUCODIGO
```

### Cadastro

1. Acesse [kiwify.com.br](https://kiwify.com.br)
2. Clique em "Criar conta" (grátis)
3. Complete o cadastro como **Afiliado**
4. Acesse o **Marketplace** → escolha produtos
5. Seu código de afiliado aparece no link gerado

### Configuração

```bash
# .env
KIWIFY_AFFILIATE_ID=seu_codigo_aqui
```

O sistema substitui automaticamente `{affiliate_id}` nas URLs pelo valor do `.env`.

---

## Eduzz

### Sobre

A Eduzz é uma plataforma internacional de infoprodutos com forte presença no Brasil. 
Oferece comissões de 50-80% com cookie de até 365 dias.

### URL Pattern

```
Formato: https://eduzz.com/NOME-DO-PRODUTO?af={affiliate_id}
Exemplo: https://eduzz.com/curso-fullstack?af=SEUCODIGO
```

### Cadastro

1. Acesse [eduzz.com](https://eduzz.com)
2. Crie conta como **Afiliado** (grátis)
3. Navegue pelo **Marketplace**
4. Escolha produtos → gere seu link de afiliado
5. Copie o código de afiliado

### Configuração

```bash
# .env
EDUZZ_AFFILIATE_ID=seu_codigo_aqui
```

---

## Monetizze

### Sobre

Monetizze é uma plataforma brasileira consolidada de infoprodutos. 
Cookie de até 365 dias, comissões de 50-80%.

### URL Pattern

```
Formato: https://monetizze.com.br/NOME-DO-PRODUTO?af={affiliate_id}
```

### Configuração

```bash
# .env
MONETIZZE_AFFILIATE_ID=seu_codigo_aqui
```

✅ Monetizze já está configurada com API key ativa no `.env`.

---

## Ofertas Disponíveis por Nicho

### 💻 Tecnologia (10 ofertas Kiwify+Eduzz)

| Produto | Rede | Comissão | Preço | Cookie |
|---|---|---|---|---|
| Curso de JavaScript Completo | Kiwify | 70% | R$ 97 | 365d |
| Pacote de Cursos de TI | Kiwify | 75% | R$ 147 | 365d |
| Curso de Inteligência Artificial c/ Python | Kiwify | 80% | R$ 127 | 365d |
| Pacote Premium Excel VBA | Kiwify | 70% | R$ 67 | 365d |
| Curso Desenvolvimento Web Full Stack | Eduzz | 60% | R$ 197 | 365d |
| Pacote Microsoft Office Completo | Eduzz | 55% | R$ 97 | 365d |

### 💰 Finanças (7 ofertas Kiwify+Eduzz)

| Produto | Rede | Comissão | Preço | Cookie |
|---|---|---|---|---|
| Guia de Renda Passiva | Kiwify | 80% | R$ 47 | 365d |
| Planilha de Gastos Inteligente | Kiwify | 70% | R$ 27 | 365d |
| Método Renda Extra Urgente | Kiwify | 85% | R$ 97 | 365d |
| Curso de Bolsa de Valores | Eduzz | 65% | R$ 197 | 365d |
| Método de Renda Extra Online | Eduzz | 60% | R$ 97 | 365d |

### 🏥 Saúde (5 ofertas Kiwify+Eduzz)

| Produto | Rede | Comissão | Preço | Cookie |
|---|---|---|---|---|
| Curso de Meditação Guiada | Kiwify | 75% | R$ 47 | 365d |
| Guia de Sono Reparador | Kiwify | 70% | R$ 37 | 365d |
| Protocolo Emagrecimento Rápido | Kiwify | 80% | R$ 67 | 365d |
| Guia de Emagrecimento Saudável | Eduzz | 65% | R$ 97 | 365d |
| Guia de Yoga e Meditação | Eduzz | 60% | R$ 67 | 365d |

### 🚀 Carreira (7 ofertas Kiwify+Eduzz)

| Produto | Rede | Comissão | Preço | Cookie |
|---|---|---|---|---|
| Curso de Marketing Digital | Kiwify | 75% | R$ 97 | 365d |
| Guia de Freelancer de Sucesso | Kiwify | 70% | R$ 47 | 365d |
| Carreira Blindada com LinkedIn | Kiwify | 80% | R$ 67 | 365d |
| Curso de Oratória e Comunicação | Eduzz | 65% | R$ 197 | 365d |
| Curso de Oratória e Persuasão | Eduzz | 60% | R$ 147 | 365d |

---

## Configuração no Sistema

### Passo 1: Configurar IDs no .env

```bash
# Edite o .env e preencha:
KIWIFY_AFFILIATE_ID=seu_codigo_aqui
EDUZZ_AFFILIATE_ID=seu_codigo_aqui
MONETIZZE_AFFILIATE_ID=seu_codigo_aqui
```

### Passo 2: Verificar Ofertas

```bash
# Testar se as ofertas estão carregando corretamente
python3 -c "
from src.campaign_autopilot.agents.money.affiliate_link_inserter import AffiliateLinkInserterAgent
agent = AffiliateLinkInserterAgent()
offers = agent.offers
kiwify_offers = [o for n in offers.get('offers_by_niche',{}).values() for o in n if o['network']=='kiwify']
eduzz_offers = [o for n in offers.get('offers_by_niche',{}).values() for o in n if o['network']=='eduzz']
print(f'Kiwify: {len(kiwify_offers)} ofertas')
print(f'Eduzz: {len(eduzz_offers)} ofertas')
print(f'Total: {len(kiwify_offers)+len(eduzz_offers)} ofertas integradas')
"
```

### Passo 3: Executar Ciclo Completo

```bash
python3 scripts/run_all_niches.py
```

---

## Como o Sistema Usa Essas Redes

### Fluxo de Inserção de Links

```
Artigo gerado pelo sistema
    ↓
AffiliateLinkInserterAgent analisa o conteúdo
    ↓
Detecta palavras-chave de produtos
    ↓
Escolhe ofertas compatíveis (máx 3 por artigo)
    ↓
Insere links com {affiliate_id} → valor real do .env
    ↓
Adiciona disclosure de afiliado
    ↓
Artigo pronto para publicação
```

### Regras de Inserção

- **Artigos informacionais**: só anúncios (AdSense), sem links de afiliado
- **Artigos comerciais**: 1-3 links de afiliado + disclosure
- **Artigos transacionais**: 2-3 links de afiliado + CTA forte
- **Máximo 3 links por artigo** (protege SEO)
- Links usam `rel="nofollow sponsored"` (conformidade Google)

### Distribuição por Artigo

```
Artigo de tecnologia:
  ├── Kiwify: Curso de JavaScript (70% comissão)
  ├── Eduzz: Curso Full Stack (60% comissão)
  └── Amazon: Notebook Dell (3% comissão)
```

---

## Estratégia de Comissões

### Por Tipo de Conteúdo

| Tipo de Conteúdo | Rede Ideal | CTR | Conversão | Receita/1k visitas |
|---|---|---|---|---|
| Tutoriais ("Como aprender X") | Kiwify (70-85%) | 2-5% | 1-3% | R$ 15-50 |
| Comparativos ("X vs Y") | Eduzz (55-65%) | 3-8% | 2-5% | R$ 30-100 |
| Reviews ("Vale a pena?") | Kiwify (80%+) | 8-15% | 5-10% | R$ 80-300 |
| Listas ("Melhores cursos") | Kiwify + Eduzz | 4-10% | 2-5% | R$ 40-150 |

### Por Ticket

```
Ticket Baixo (R$ 27-47): Kiwify
  → Alta comissão % → muita receita por venda
  → Ideal para conteúdo de topo de funil

Ticket Médio (R$ 97-197): Eduzz + Kiwify
  → Bom equilíbrio entre volume e valor
  → Ideal para conteúdo de meio de funil

Ticket Alto (R$ 197-497): Eduzz
  → Menos vendas, mas cada venda paga muito
  → Ideal para conteúdo de fundo de funil
```

---

## Próximos Passos

- [ ] **Criar contas** na Kiwify (kiwify.com.br) e Eduzz (eduzz.com)
- [ ] **Configurar .env** com KIWIFY_AFFILIATE_ID e EDUZZ_AFFILIATE_ID
- [ ] **Testar links** — executar um ciclo e verificar se os links aparecem
- [ ] **Verificar comissões reais** — ajustar ofertas conforme performance
- [ ] **Adicionar mais produtos** conforme encontrar ofertas melhores
- [ ] **Configurar Monetizze API** — já tem chave, ativar integração

---

> 💡 **Dica:** Kiwify tem as maiores comissões (até 85%) — priorize produtos Kiwify em conteúdo de topo e meio de funil. Eduzz é excelente para produtos de ticket mais alto (R$ 197+) em conteúdo de fundo de funil.
