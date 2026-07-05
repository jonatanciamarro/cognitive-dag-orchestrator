# CPAAgent — Redes CPA (Cost Per Action)

## Propósito
Gerenciar ofertas CPA (Cost Per Action) — ganhe por lead, download, cadastro ou venda.

## Redes CPA Brasileiras
- **Lomadee** (maior rede CPA do Brasil)
- **Awin** (internacional com foco em BR)
- **PagBank PagSeguro** (afiliados)
- **Rakuten Advertising** (internacional)
- **LeadLovers** (parcerias)

## Protocolo E2E
1. **SETUP** — Criar conta nas redes CPA
2. **INTEGRATE** — Escolher ofertas por nicho, copiar links
3. **ACTIVATE** — Adicionar ofertas ao sistema
4. **MONITOR** — RevenueMemory registra leads e comissões
5. **OPTIMIZE** — Rotacionar ofertas, focar nas que convertem

## Como Configurar
1. Escolha 2-3 redes CPA (Lomadee, Awin, etc)
2. Crie conta como afiliado/publisher
3. Navegue no catálogo de ofertas
4. Filtre por nicho (tecnologia, finanças, saúde, carreira)
5. Copie o link de cada oferta
6. Adicione ao `configs/affiliate_offers.json` com `network: "cpa"`

## Uso
```python
from campaign_autopilot.agents import CPAAgent

agent = CPAAgent()
result = agent.run(context)
```
