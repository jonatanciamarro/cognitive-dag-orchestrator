# Hotmart Product Selection Skill

## Objetivo
Selecionar automaticamente os melhores produtos Hotmart para se afiliar, maximizando velocidade de ganhos.

## Agentes
- **HotmartProductResearcherAgent** — Pesquisa e ranqueia produtos por nicho
- **HotmartAffiliateSelectorAgent** — Seleciona os melhores com base em criterios de ganho rapido

## Workflow
1. `research_products` → Pesquisa todos os nichos
2. `select_best` → Seleciona top 3 por criterio de velocidade
3. `generate_hunt_list` → Gera lista para o usuario coletar links

## Criterios de Selecao
1. **Velocidade de conversao** (preco baixo + alta demanda)
2. **Comissao alta** (>50%)
3. **Baixa concorrencia** (produtos menos saturados)
4. **Cookie longo** (30 dias ideal)

## Como Usar
```bash
# Via CLI
python scripts/hotmart_wizard.py --smart-select

# Via workflow
python -c "
from campaign_autopilot.agents.hotmart import HotmartAffiliateSelectorAgent
from campaign_autopilot.agents.base import CampaignContext
agent = HotmartAffiliateSelectorAgent()
result = agent.run(CampaignContext(campaign={'budget_tier': 'rapido'}))
print(result.output['hunt_list'])
"
```
