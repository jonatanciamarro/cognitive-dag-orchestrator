# Hotmart Agent System — Automacao de Coleta de Links

## Propósito
Automatizar o processo de coleta, validacao e configuracao de links de afiliado Hotmart.

## Agentes

| Agente | Funcao |
|--------|--------|
| **HotmartLinkManagerAgent** | Armazena links em SQLite, organiza por nicho, evita duplicatas |
| **ProductMatcherAgent** | Analisa nome do produto, sugere keywords e comissao |
| **LinkValidatorAgent** | Valida formato, presenca de ?aff=, detecta placeholders |
| **AffiliateConfigUpdaterAgent** | Atualiza configs/affiliate_offers.json com links coletados |

## Fluxo

```
Usuario coleta link no Hotmart
  → HotmartLinkManagerAgent armazena no SQLite
  → ProductMatcherAgent sugere keywords + comissao
  → LinkValidatorAgent valida o link
  → AffiliateConfigUpdaterAgent atualiza config JSON
  → AffiliateLinkInserterAgent usa nas proximas geracoes de conteudo
```

## CLI Wizard
```bash
python scripts/hotmart_wizard.py              # Modo interativo
python scripts/hotmart_wizard.py --status      # Status da colecao
python scripts/hotmart_wizard.py --validate    # Validar todos os links
python scripts/hotmart_wizard.py --add-link    # Adicionar link manual
```

## Estado
`.state/hotmart_links.db` — banco SQLite com todos os links coletados.
