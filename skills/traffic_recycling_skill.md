# ♻️ Traffic Recycling — Skill do TrafficRecyclerAgent v2.0

## Propósito
Reaproveitar **cada visitante** que chega no conteúdo para **múltiplas camadas de monetização**,
transformando tráfego que seria "perdido" em receita adicional. Funciona como um funil de 8+ camadas.

## Filosofia: 8+ Camadas de Monetização por Visitante

```
Visitante chega no artigo → 8+ oportunidades:

1️⃣ Conteúdo: Links de afiliado + AdSense (já funciona)
2️⃣ Lead Magnet: PDF/checklist em troca do email (R$0,025/vis)
3️⃣ Interstitial: Oferta sutil após 30s de leitura (R$0,025/vis)
4️⃣ Exit-Intent: Popup quando vai sair (R$0,06/vis)
5️⃣ Cross-Niche: Artigo de outro nicho com afiliado (R$0,012/vis)
6️⃣ Telegram/WhatsApp: Canal exclusivo (R$0,03-0,045/vis)
7️⃣ Email: Sequência de conversão automática (R$0,035/vis)
8️⃣ Produto Digital / Membresia: Upgrade (R$0,14-0,38/vis)
```

## Arquitetura

```
TrafficRecyclerAgent
├── get_paths()        → 14 caminhos de conversão, scorados por intent + nicho
├── estimate()         → Estimativa sequencial com diminishing returns
├── gen_html()         → 6 tipos de HTML embeddável (lead, exit, tg, wa, cross, interstitial)
├── _sync_to_semantic_memory() → Aprendizado persistente
└── MEMORY_FILE        → .state/traffic_recycling_memory.json
```

## Como Usar

### 1. Copiar HTML para o Site
O agente gera HTML pronto em `output/traffic_recycling/`:
```html
<!-- lead_magnet.html → Final do artigo -->
<!-- exit_intent_popup.html → Script + popup -->
<!-- telegram.html → CTA do canal -->
<!-- whatsapp.html → CTA do grupo -->
<!-- interstitial.html → Oferta contextual -->
```

### 2. Configurar Captura de Email (Grátis)
| Serviço | Grátis até | Link |
|---------|-----------|------|
| MailerLite | 1.000 leads | https://www.mailerlite.com |
| Brevo | 300 emails/dia | https://www.brevo.com |
| Mailchimp | 2.000 leads | https://mailchimp.com |

### 3. Configurar Canais
- **Telegram**: Crie canal por nicho → @username
- **WhatsApp**: Crie grupo → Convite
- **Pixel**: Meta Pixel + TikTok Pixel no `<head>`

## Gatilhos de Conversão

| Gatilho | Timing | Taxa Conversão | RPV |
|---------|--------|----------------|-----|
| Lead Magnet | Fim do artigo | 5-8% | R$0,025 |
| Interstitial | 30s de leitura | 1-3% | R$0,025 |
| Exit-Intent | Mouse sai da tela | 2-5% | R$0,060 |
| Cross-Niche | Meio do artigo | 3-5% | R$0,012 |
| Telegram | Fim do artigo | 2-4% | R$0,030 |
| WhatsApp | Fim do artigo | 3-5% | R$0,045 |
| Popup Oferta | 45s de leitura | 1-2% | R$0,025 |

## Memorização
O agente salva em `.state/traffic_recycling_memory.json`:
- Performance histórica de cada caminho
- RPV ajustado por aprendizado empírico
- Total de receita reciclada
- Contagem de ciclos

Sincroniza com `SemanticMemoryStore` para persistência跨-sessão.

## Métricas de Sucesso
- **RPV (Revenue Per Visitor)**: R$ por visitante (target: R$0,10+)
- **Revenue Multiplier**: Quantas vezes a receita base foi multiplicada (target: 3x+)
- **Conversion Rate**: % de visitantes que convertem em cada camada
- **Lead Capture Rate**: % de visitantes que viram leads
- **HTML Elements**: Quantos elementos de conversão foram gerados

## Integração

```python
from campaign_autopilot.agents.traffic_recycler import TrafficRecyclerAgent

agent = TrafficRecyclerAgent(semantic_memory=memory_store)
result = agent.run(context)

# HTML pronto
for el in result.output["interstitial_elements"]:
    print(el["html"])

# Top caminhos
for p in result.output["top_paths"][:5]:
    print(f"{p['icon']} {p['name']}: R${p['estimated_revenue']:.2f}")
```
