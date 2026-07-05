# RevenueProtocolAgent — Protocolo E2E por Fonte de Renda

## Propósito
Define o passo a passo detalhado (protocolo) para configurar cada uma das 13 fontes de renda do sistema. Inclui checklists, links, comandos e verificação de configuração.

## Ações
- `list` — Lista todas as fontes com status
- `show` — Mostra protocolo completo de uma fonte (requer `source`)
- `checklist` — Gera checklist verificável (requer `source`)
- `status` — Mostra progresso geral de configuração
- `verify` — Verifica se fonte está configurada corretamente (requer `source`)

## Fontes Suportadas
1. Hotmart, Amazon, Monetizze, Kiwify, Eduzz
2. Google AdSense, CPA Networks
3. Produtos Digitais, Memberships
4. Email Marketing, Lead Capture
5. Traffic Recycling, Paid Traffic

## Uso
```python
from campaign_autopilot.agents.revenue import RevenueProtocolAgent

agent = RevenueProtocolAgent()
# Listar todas: campaign={"action": "list"}
# Mostrar protocolo: campaign={"action": "show", "source": "hotmart"}
# Verificar: campaign={"action": "verify", "source": "amazon"}
result = agent.run(context)
```
