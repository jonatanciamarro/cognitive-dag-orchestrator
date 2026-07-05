# AdSenseAgent — Google AdSense

## Propósito
Monetizar o site de notícias e blogs com anúncios contextuais do Google AdSense.

## Protocolo E2E
1. **SETUP** — Criar conta no Google AdSense
2. **INTEGRATE** — Vincular site ao AdSense, configurar unidades de anúncio
3. **ACTIVATE** — Sistema insere anúncios automaticamente no site
4. **MONITOR** — RevenueMemory registra impressões e receita
5. **OPTIMIZE** — Testar posições e formatos de anúncio

## Como Configurar
1. Acesse https://adsense.google.com
2. Crie conta com seu site
3. Aguarde aprovação (1-2 dias úteis)
4. Crie unidades de anúncio (display, in-feed, in-article)
5. Cole o código do AdSense no site
6. O sistema gerencia a inserção automática

## Uso
```python
from campaign_autopilot.agents import AdSenseAgent

agent = AdSenseAgent()
result = agent.run(context)
```
