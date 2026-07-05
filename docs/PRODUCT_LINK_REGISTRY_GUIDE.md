# 🔗 Product Link Registry — Guia de Links de Afiliado

> **Data:** 2026-06-28 | **Status:** ✅ Implementado
> **Problema resolvido:** Cada plataforma de afiliados usa links ÚNICOS por produto, não um ID genérico de usuário.

---

## 📋 O Problema

Diferente do Amazon Associates (que usa uma tag única `?tag=SEU_TAG`), plataformas como **Hotmart, Kiwify, Eduzz, Monetizze, Mercado Livre, Shopee e Shein** geram um **link diferente para cada produto** que você promove.

**Exemplo Hotmart:**
- Produto A → `https://go.hotmart.com/PRODUTO_A?aff=SEU_CODIGO_A`
- Produto B → `https://go.hotmart.com/PRODUTO_B?aff=SEU_CODIGO_B`

Não existe um ID único que funcione para todos os produtos.

---

## ✅ A Solução: Product Link Registry

O **Product Link Registry** é um banco SQLite onde você registra manualmente o link REAL de cada produto que promove.

### Como funciona:

```
1. Você pega o link de afiliado no site da plataforma (Hotmart, Kiwify, etc)
2. Registra no sistema via CLI
3. O sistema SEMPRE usa seu link real em vez de placeholders
```

### Prioridade de resolução de links:

| Prioridade | Fonte | Exemplo |
|-----------|-------|---------|
| 1° | ProductLinkRegistry (seu link real) | `https://go.hotmart.com/PRODUTO?aff=SEUCODIGO` |
| 2° | affiliate_offers.json (link genérico) | `https://go.hotmart.com/TEST123` |
| 3° | Nenhum | String vazia |

---

## 🚀 Como Usar

### 1. Listar produtos disponíveis no sistema

```bash
python scripts/manage_links.py import-config
```

Isso importa TODOS os produtos do config com links genéricos e mostra quais precisam ser atualizados com seus links REAIS.

### 2. Registrar um link manualmente (modo interativo)

```bash
python scripts/manage_links.py add -i
```

Preencha:
- **Rede**: `hotmart`, `kiwify`, `eduzz`, `mercadolivre`, `shopee`, `shein`, `aliexpress`, `monetizze`, `amazon`
- **Produto**: Nome exato do produto (igual ao do config)
- **Link**: Link COMPLETO de afiliado (com seu código)
- **Categoria**: Opcional

### 3. Registrar via comando direto

```bash
python scripts/manage_links.py add \
  --network hotmart \
  --product "Curso de Programação Completo" \
  --link "https://go.hotmart.com/SEU_PRODUTO?aff=SEU_CODIGO" \
  --category tecnologia
```

### 4. Ver estatísticas

```bash
python scripts/manage_links.py stats
```

### 5. Buscar um produto

```bash
python scripts/manage_links.py search "programação"
```

### 6. Atualizar link de um produto

```bash
python scripts/manage_links.py update <LINK_ID> --link "https://novo.link.com?aff=CODIGO"
```

Para ver o LINK_ID:
```bash
python scripts/manage_links.py list
```

### 7. Remover um produto

```bash
python scripts/manage_links.py unregister <LINK_ID>
```

---

## 🌐 Onde Pegar os Links de Cada Plataforma

### Hotmart
1. Acesse `https://hotmart.com/pt-br/marketplace`
2. Busque o produto que quer promover
3. Clique em "Virar Afiliado" ou "Promover"
4. Copie o link gerado (ex: `https://go.hotmart.com/PRODUTO?aff=SEUCODIGO`)

### Kiwify
1. Acesse `https://kiwify.com.br/marketplace`
2. Encontre o produto
3. Clique em "Promover como Afiliado"
4. Copie o link (ex: `https://pay.kiwify.com.br/PRODUTO?aff=SEUCODIGO`)

### Eduzz
1. Acesse `https://eduzz.com/marketplace`
2. Busque o produto
3. Solicite afiliação
4. Copie o link gerado

### Amazon
- **Use o AMAZON_ASSOCIATES_TAG no .env** — essa plataforma funciona com tag única
- O sistema adiciona automaticamente `?tag=SEU_TAG` a qualquer link de produto Amazon

### Monetizze
1. Acesse `https://monetizze.com.br`
2. Encontre o produto no painel de afiliados
3. Copie seu link personalizado

### Mercado Livre / Shopee / Shein / AliExpress
1. Acesse o programa de afiliados de cada plataforma
2. Gere o link para o produto específico
3. Registre no sistema

---

## 🧪 Verificação

Para confirmar que o sistema está usando seus links REAIS:

```bash
python3 -c "
import sys, os
sys.path.insert(0, 'src')
os.environ['CAMPAIGN_BOT_REQUIRE_OPT_IN'] = 'false'
from campaign_autopilot.agents.offer_lookup import OfferLookupAgent
from campaign_autopilot.agents.base import CampaignContext
agent = OfferLookupAgent()
ctx = CampaignContext(run_id='verify', campaign={'niche': 'tecnologia', 'objective': 'test'}, step_results={})
result = agent.run(ctx)
for o in result.output['available_offers'][:5]:
    print(f'{o[\"product_name\"]}: {o[\"affiliate_link\"][:60]}')
"
```

Se aparecerem links com seus códigos reais, está funcionando! ✅
