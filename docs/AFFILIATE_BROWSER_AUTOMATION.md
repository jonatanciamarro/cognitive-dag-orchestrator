# 🤖 Affiliate Browser Automation — Descoberta Automática de Produtos

> **Data:** 2026-06-28 | **Status:** ✅ Implementado
> **Tecnologia:** Playwright (Chromium headless)

---

## 📋 Visão Geral

O **AffiliateBrowserAgent** permite que o sistema:

1. **Navegue automaticamente** até sua conta no Hotmart, Kiwify, Eduzz, etc.
2. **Varra categorias/nichos** em busca de produtos para promover
3. **Extraia links de afiliado REAIS** (cada produto tem seu link único)
4. **Registre automaticamente** no ProductLinkRegistry
5. **Aplique scoring** do Hotmart Intelligence Protocol

---

## 🔧 Setup Inicial

### 1. Login Único por Plataforma

Cada plataforma exige **UM login manual** para salvar a sessão. Depois disso, o sistema reusa os cookies automaticamente.

```bash
# Hotmart (abre navegador para login manual)
python scripts/affiliate_browser.py login hotmart

# Kiwify
python scripts/affiliate_browser.py login kiwify

# Eduzz
python scripts/affiliate_browser.py login eduzz
```

O navegador abre, você faz login **uma vez**, e o sistema salva os cookies em `.state/browser_sessions/`.

### 2. Verificar Sessões Salvas

```bash
python scripts/affiliate_browser.py status
```

---

## 🎯 Uso Diário

### Varrer uma Plataforma por Nicho

```bash
python scripts/affiliate_browser.py scan hotmart --niche "marketing digital" --max 20
```

Isso:
1. Abre o Hotmart Marketplace
2. Busca por "marketing digital"
3. Extrai até 20 produtos
4. Registra links no ProductLinkRegistry

### Scan Completo (Todas as Plataformas + Todos os Nichos)

```bash
python scripts/affiliate_browser.py full-scan
```

Fluxo completo:
```
Para cada plataforma (Hotmart, Kiwify, Eduzz...)
  Para cada nicho (marketing, finanças, IA, saúde...)
    → Descobre produtos
    → Aplica scoring
    → Registra no ProductLinkRegistry
```

---

## 🔄 Integração com o Sistema

### Workflow: `affiliate_discovery_pipeline`

```
niche_strategy (SEO Research)
  ├→ hotmart_browser_scan (HotmartDiscoveryAgent)
  ├→ kiwify_browser_scan (OfferLookupAgent)
  ↓
hotmart_scoring (scoring agent)
  ↓
hotmart_due_diligence (due diligence agent)
  ↓
register_links (OfferLookupAgent → ProductLinkRegistry)
  ↓
report (Analytics)
```

### OfferLookupAgent atualizado

O `OfferLookupAgent` agora:
1. Tenta primeiro o **ProductLinkRegistry** (links reais registrados)
2. Depois o **affiliate_offers.json** (links genéricos do config)
3. Usa o que tiver melhor qualidade

---

## 🌐 Plataformas Suportadas

| Plataforma | Login | Scan | Status |
|-----------|-------|------|--------|
| **Hotmart** | ✅ `login hotmart` | ✅ `scan hotmart` | Implementado |
| **Kiwify** | ✅ `login kiwify` | ✅ `scan kiwify` | Implementado |
| **Eduzz** | ✅ `login eduzz` | ⏳ Parcial | Esboço |
| **Monetizze** | ✅ `login monetizze` | ⏳ Parcial | Esboço |
| **Mercado Livre** | ⏳ Pendente | ⏳ Pendente | A implementar |
| **Shopee** | ⏳ Pendente | ⏳ Pendente | A implementar |
| **Shein** | ⏳ Pendente | ⏳ Pendente | A implementar |
| **AliExpress** | ⏳ Pendente | ⏳ Pendente | A implementar |

---

## 🔐 Segurança

- **Cookies salvos localmente** em `.state/browser_sessions/` (no `.gitignore`)
- **Nenhuma senha é armazenada** — apenas cookies de sessão
- **Login manual necessário** apenas uma vez por plataforma
- Sessões expiram com o tempo — basta refazer o login

---

## 📊 Fluxo Completo Ideal

```
1. python scripts/affiliate_browser.py login hotmart   (1x)
2. python scripts/affiliate_browser.py login kiwify     (1x)
3. python scripts/affiliate_browser.py login eduzz      (1x)

4. python scripts/affiliate_browser.py full-scan        (diário/semanal)

5. python scripts/manage_links.py stats                 (verificar)
6. python scripts/manage_links.py list                  (ver links registrados)

7. python -m campaign_autopilot.cli_v2 run teamworker_preview  (validar)
8. python -m campaign_autopilot.cli_v2 run production_workflow (produzir)
```

A partir desse fluxo, o sistema:
- Descobre produtos automaticamente ✅
- Extrai links reais ✅
- Registra no banco ✅
- Gera conteúdo com links corretos ✅
- Publica e monetiza ✅
