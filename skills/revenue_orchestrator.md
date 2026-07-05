# RevenueOrchestratorAgent — Orquestrador de 13 Fontes de Renda

## Propósito
Coordena TODAS as 13 fontes de renda do sistema. Mantém estado de cada fonte, recomenda próximos passos e garante que todas estejam gerando receita.

## Fontes Gerenciadas
1. **Hotmart** — Produtos digitais (cursos, e-books)
2. **Amazon Associates** — Links da Amazon
3. **Monetizze** — Rede afiliada brasileira
4. **Kiwify** — Rede afiliada brasileira
5. **Eduzz** — Rede afiliada brasileira
6. **Google AdSense** — Anúncios contextuais
7. **CPA Networks** — Custo por ação/lead
8. **Digital Products** — Produtos digitais próprios
9. **Memberships** — Assinaturas
10. **Email Marketing** — Sequências de e-mail
11. **Lead Capture** — Captura de leads
12. **Traffic Recycling** — Reciclagem de tráfego
13. **Paid Traffic** — Tráfego pago (reinvestimento)

## Ações
- `dashboard` — Mostra status atual de todas as fontes
- `setup_all` — Guia de configuração para cada fonte
- `next_steps` — Recomenda próximos passos baseado no estado

## Uso
```python
from campaign_autopilot.agents import RevenueOrchestratorAgent

agent = RevenueOrchestratorAgent()
result = agent.run(context)
```
