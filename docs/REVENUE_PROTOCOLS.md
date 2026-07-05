# Revenue Protocols — Guia E2E para 13 Fontes de Renda

> **Campaign Autopilot v5.2.1** — 13 fontes de renda em paralelo

## Introdução
Este documento define o passo a passo (protocolo) para cada fonte de renda do sistema Lyzer Labs Campaign Autopilot. Siga estes protocolos na ordem para configurar todas as 13 fontes.

---

## 1. Hotmart

### Setup
1. Acesse https://hotmart.com
2. Crie conta como afiliado (gratuito)
3. Vá em Catálogo de Produtos
4. Escolha produtos nos nichos: tecnologia, finanças, saúde, carreira
5. Clique "Pegar link" em cada produto
6. Copie o link COMPLETO (ex: https://hotm.art/produto?aff=abc123)

### Integração
```bash
python scripts/hotmart_wizard.py
```
Ou adicione manualmente em `configs/affiliate_offers.json`.

### Ativação
Os links são inseridos automaticamente nos artigos pelo AffiliateLinkInserterAgent.

---

## 2. Amazon Associates

### Setup
1. Acesse https://associados.amazon.com.br
2. Crie conta (gratuito)
3. Obtenha seu Tracking ID (ex: `seunome-20`)
4. Adicione ao `.env`: `AMAZON_TRACKING_ID=seunome-20`

### Integração
Edite `configs/affiliate_offers.json` e adicione produtos Amazon com links encurtados (https://amzn.to/...).

### Ativação
AffiliateLinkInserterAgent insere links Amazon nos artigos automaticamente.

---

## 3. Monetizze

### Setup
1. Acesse https://monetizze.com.br
2. Crie conta como afiliado
3. Catálogo → Escolha produtos → Copie link com `?afiliado=SEUCODIGO`
4. Adicione ao `configs/affiliate_offers.json`

### Comando
```python
from campaign_autopilot.agents import GenericAffiliateNetworkAgent
agent = GenericAffiliateNetworkAgent(network="monetizze")
```

---

## 4. Kiwify

### Setup
1. Acesse https://kiwify.com.br
2. Crie conta como afiliado
3. Catálogo → Escolha produtos → Copie link com `?afiliado=SEUCODIGO`
4. Adicione ao `configs/affiliate_offers.json`

### Comando
```python
from campaign_autopilot.agents import GenericAffiliateNetworkAgent
agent = GenericAffiliateNetworkAgent(network="kiwify")
```

---

## 5. Eduzz

### Setup
1. Acesse https://eduzz.com
2. Crie conta como afiliado
3. Catálogo → Escolha produtos → Copie link com `?afiliado=SEUCODIGO`
4. Adicione ao `configs/affiliate_offers.json`

### Comando
```python
from campaign_autopilot.agents import GenericAffiliateNetworkAgent
agent = GenericAffiliateNetworkAgent(network="eduzz")
```

---

## 6. Google AdSense

### Setup
1. Acesse https://adsense.google.com
2. Crie conta com seu site
3. Aguarde aprovação (1-2 dias úteis)
4. Crie unidades de anúncio (display, in-feed, in-article)

### Integração
O sistema insere anúncios automaticamente no site gerado.

### Comando
```python
from campaign_autopilot.agents import AdSenseAgent
agent = AdSenseAgent()
```

---

## 7. CPA Networks

### Setup
1. Escolha redes: Lomadee, Awin, PagBank PagSeguro
2. Crie conta como publisher/afiliado
3. Catálogo de ofertas → filtre por nicho
4. Copie links de ofertas

### Integração
Adicione ofertas em `configs/affiliate_offers.json` com `"network": "cpa"`.

### Comando
```python
from campaign_autopilot.agents import CPAAgent
agent = CPAAgent()
```

---

## 8. Produtos Digitais Próprios

### Setup
1. Crie produtos (e-book, template, checklist, mini-curso)
2. H ospede em plataforma (Hotmart, Monetizze, ou próprio site)

### Integração
O DigitalProductAgent gerencia a criação e venda automática.

### Comando
```python
from campaign_autopilot.agents.money import DigitalProductAgent
```

---

## 9. Membership / Assinaturas

### Setup
1. Defina modelo de assinatura (newsletter paga, conteúdo exclusivo)
2. Configure no sistema de pagamento

### Comando
```python
from campaign_autopilot.agents.money import MembershipAgent
```

---

## 10. Email Marketing

### Setup
1. Configure lista de e-mails (lead capture)
2. Crie sequências de e-mails (boas-vindas, nutrição, ofertas)

### Comando
```python
from campaign_autopilot.agents import EmailMarketingAgent
```

---

## 11. Lead Capture

### Setup
1. Crie iscas digitais (e-book grátis, checklist, planilha)
2. Configure formulários de captura no site
3. Conecte ao sistema de e-mail marketing

### Comando
```python
from campaign_autopilot.agents import LeadCaptureAgent
```

---

## 12. Traffic Recycling

### Setup
1. Configure pixels de retargeting nas páginas
2. Crie audiências de visitantes
3. O sistema automaticamente recicla tráfego

### Comando
```python
from campaign_autopilot.agents import TrafficRecyclerAgent
```

---

## 13. Paid Traffic (Reinvestimento)

### Setup
1. Quando houver receita orgânica, o sistema ativa campanhas pagas
2. Google Ads, Meta Ads, Native Ads
3. O budget vem da receita orgânica (autopilot)

### Comando
```python
from campaign_autopilot.agents.paid_traffic import PaidTrafficOrchestratorAgent
```

---

## Orchestrator Central

Para ver o status de todas as fontes:
```python
from campaign_autopilot.agents import RevenueOrchestratorAgent
agent = RevenueOrchestratorAgent()
# action = "dashboard", "setup_all", "next_steps"
result = agent.run(context)
```

## Banco de Dados Unificado

Todas as fontes compartilham o mesmo SQLite:
`.state/revenue.db`

```python
from campaign_autopilot.agents.revenue import RevenueMemory
memory = RevenueMemory()
summary = memory.get_summary()
status = memory.get_status()
```
