# GenericAffiliateNetworkAgent — Monetizze, Kiwify, Eduzz

## Propósito
Agente único para redes de afiliados brasileiras que seguem o mesmo protocolo do Hotmart: cada produto gera um link ÚNICO com parâmetro de afiliado.

## Redes Suportadas
- **Monetizze** (monetizze.com.br)
- **Kiwify** (kiwify.com.br)
- **Eduzz** (eduzz.com)

## Protocolo E2E
1. **SETUP** — Criar conta na rede como afiliado
2. **INTEGRATE** — Escolher produtos no catálogo, copiar links com `?afiliado=SEUCODIGO`
3. **ACTIVATE** — Adicionar links ao `configs/affiliate_offers.json`
4. **MONITOR** — RevenueMemory registra cliques e conversões
5. **OPTIMIZE** — Substituir ofertas de baixa performance

## Como Configurar
1. Acesse o site da rede (Monetizze/Kiwify/Eduzz)
2. Crie conta como afiliado
3. Navegue no catálogo de produtos
4. Escolha produtos nos nichos: tecnologia, finanças, saúde, carreira
5. Clique "Pegar link" em cada produto
6. Copie o link COMPLETO (ex: https://monetizze.com.br/produto?afiliado=abc123)
7. Adicione ao `configs/affiliate_offers.json`

## Uso
```python
from campaign_autopilot.agents import GenericAffiliateNetworkAgent

agent = GenericAffiliateNetworkAgent(network="monetizze")
result = agent.run(context)
```
