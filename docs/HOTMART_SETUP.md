# Guia de Configuração Hotmart — Campaign Autopilot

## DIFERENTE DE OUTRAS REDES

**Hotmart NÃO tem um ID fixo de afiliado para sua conta.**

Cada produto gera um link ÚNICO contendo seu código de afiliado.
Exemplo: `https://hotm.art/produto?aff=SEUCODIGO_12345`

## Como Conseguir os Links

1. Acesse https://hotmart.com/login
2. Faça login na sua conta
3. No menu: **Produtos → Catálogo de Produtos**
4. Navegue pelos nichos (tecnologia, financas, saude, carreira)
5. Encontre um produto e clique em **"Pegar link"**
6. O link gerado é algo como:
   ```
   https://hotm.art/nome-do-produto?aff=abc123&src=HOTMART
   ```
7. Copie o link COMPLETO (incluindo `?aff=...`)

## Como Adicionar no Sistema

Edite o arquivo `configs/affiliate_offers.json`:

```json
{
  "network": "hotmart",
  "product_name": "Nome do Produto",
  "product_url": "https://hotm.art/produto?aff=abc123",
  "commission_type": "percentage",
  "commission_value": 50.0,
  "keywords": ["palavra1", "palavra2"],
  "cookie_days": 30,
  "niche": "tecnologia"
}
```

**IMPORTANTE:** O `product_url` deve ser o link COMPLETO com `?aff=SEUCODIGO`.

## Onde Colocar Cada Link

| Nicho | Sugestão de Produto |
|-------|-------------------|
| tecnologia | Cursos de programação, IA, ferramentas digitais |
| financas | Cursos de investimentos, planilhas, ebooks |
| saude | Cursos de emagrecimento, ebooks de alimentação |
| carreira | Cursos de LinkedIn, mentoria, ebooks |

## Verificar se Está Funcionando

```bash
source .venv/bin/activate
python scripts/validate_affiliate.py
```

O sistema vai usar o `product_url` direto sem modificar.
