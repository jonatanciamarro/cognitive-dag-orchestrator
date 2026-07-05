# 📋 Guia Prático: Como Obter Seus Links de Afiliado Hotmart

> **Situação:** Você tem 21 produtos da Hotmart no sistema com links de CHECKOUT apenas.
> **Missão:** Converter para links de AFILIADO para ganhar comissão.
> **Tempo estimado:** 15-20 minutos no celular.

---

## 🔍 Entendendo o Problema

- **Hotmart NÃO tem** um ID único de afiliado para sua conta
- **Cada produto** gera um link ÚNICO contendo seu código de afiliado
- Exemplo: `https://go.hotmart.com/PRODUTO?aff=SEU_CODIGO`
- O código normalmente parece: `S12345678` ou `H12345678`

---

## 📱 Método 1 — Pelo Celular (Recomendado)

### Passo 1: Acesse a Hotmart

1. Abra o **Chrome** no seu celular
2. Acesse: **https://app.hotmart.com/products/affiliations**
3. Faça login normalmente (com Google)

### Passo 2: Encontre Seu Código de Afiliado

Para CADA produto que você já é afiliado:

1. Na lista, clique no produto desejado
2. Procure por "Link de Afiliado" ou "Copiar Link"
3. Olhe no link — ele terá algo como:
   ```
   https://go.hotmart.com/S12345678
   ```
   ou
   ```
   https://pay.hotmart.com/PRODUTO_ID?off=CODIGO&aff=SEU_CODIGO
   ```

4. O `SEU_CODIGO` é o que precisamos — ele é IGUAL para todos os produtos

**👉 IMPORTANTE:** Se você achar UM link de afiliado com `?aff=SEU_CODIGO`, esse código serve para TODOS os produtos.

---

## 🚀 Método 2 — Extrair Cookies (Automação)

Se você quiser que o sistema faça TUDO automaticamente, precisa extrair os cookies da sua sessão Hotmart:

### Opção A — Usar Extensão "Cookie-Editor"

1. No Chrome do celular, acesse: **chrome.google.com/webstore**
2. Pesquise por **"Cookie-Editor"**
3. Instale a extensão
4. Vá para: **app.hotmart.com/products/affiliations** (já logado)
5. Abra a extensão Cookie-Editor
6. Clique em **"Export"** (canto inferior direito)
7. Copie o JSON exportado

### Opção B — Usar o DevTools

1. Conecte o celular ao computador via USB
2. No Chrome do computador, acesse: **chrome://inspect**
3. Encontre seu celular e a aba da Hotmart
4. Clique em **"inspect"**
5. No console, cole:
   ```javascript
   console.log(JSON.stringify(document.cookie))
   ```
6. Copie o resultado

---

## ⚡ Depois de Obter o Código

Assim que você tiver seu código de afiliado Hotmart (ex: `S12345678`), execute:

```bash
# Converte TODOS os 21 produtos de uma vez!
cd /root/Documents/Codex/2026-05-30/New\ Project\ \(1\)
python scripts/convert_hotmart_links.py SEU_CODIGO_AQUI
```

**Exemplo real:**
```bash
python scripts/convert_hotmart_links.py S12345678
```

**Para testar primeiro (sem modificar):**
```bash
python scripts/convert_hotmart_links.py S12345678 --dry-run
```

---

## 📊 Verificação

Depois de converter:

```bash
python scripts/manage_links.py stats
python scripts/manage_links.py list
```

Confira se todos os links agora têm `?aff=SEU_CODIGO` no final.

---

## 🔄 Outras Plataformas

| Plataforma | Como obter o link |
|-----------|-------------------|
| **Kiwify** | kiwify.com.br/marketplace → "Promover como Afiliado" |
| **Eduzz** | eduzz.com/marketplace → Solicitar afiliação → Copiar link |
| **Monetizze** | monetizze.com.br → Painel de Afiliados → Copiar link |
| **Amazon** | Só precisa da TAG no .env (funciona automático) |

---

## 💡 Dica Final

Se você encontrar APENAS UM link de afiliado na Hotmart com `?aff=XXXXX`, execute:

```bash
python scripts/convert_hotmart_links.py XXXXX
```

Isso vai aplicar esse código a todos os 21 produtos em segundos!
