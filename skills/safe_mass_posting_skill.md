# 📢 Safe Mass Posting — Publicação Segura em Massa

## Propósito
Maximizar a quantidade de conteúdo postado em **múltiplas plataformas** sem ativar flags de spam, shadowban ou bloqueio de conta.

## Limites Máximos Seguros por Plataforma

| Plataforma | Por Dia | Por Semana | Intervalo Mínimo | Melhores Horários |
|------------|---------|------------|------------------|-------------------|
| **Blog/Site** | 10 artigos | 50 | 30min | 6-12h, 17-20h |
| **YouTube** | 2 vídeos | 7 | 4h | 11-19h (ter-sex) |
| **Instagram** | 3 posts | 15 | 3h | 8-12h, 17-21h |
| **TikTok** | 5 vídeos | 20 | 1h | 7-14h, 18-22h |
| **Twitter/X** | 15 posts | 80 | 15min | 7-12h, 17-20h |
| **Pinterest** | 25 pins | 100 | 10min | 8-12h, 19-22h |
| **LinkedIn** | 2 posts | 10 | 4h | 7-12h (ter-sex) |
| **Facebook** | 5 posts | 25 | 2h | 8-12h, 17-20h |
| **Telegram** | 20 posts | 100 | 5min | 7-22h |
| **WhatsApp** | 3 mensagens | 15 | 1h | 9-18h (seg-sex) |
| **Email** | 1 campanha | 5 | 24h | 8-12h (ter-qui) |

## Fatores de Segurança

### Maturidade da Conta
| Idade da Conta | Multiplicador | Ex: YouTube |
|----------------|--------------|-------------|
| < 30 dias | 0.3x | 0.6 vídeos/dia |
| 30-90 dias | 0.5x | 1 vídeo/dia |
| 3-12 meses | 0.7x | 1.4 vídeos/dia |
| 1+ ano | 1.0x | 2 vídeos/dia |
| Verificada | 1.2x | 2.4 vídeos/dia |

### Padrões Anti-Spam Detectados
- **Conteúdo idêntico**: Máximo 3 repetições em 7 dias
- **Mesma imagem**: Máximo 2 em 30 dias
- **Links repetidos**: Máximo 5 plataformas em 24h
- **Rapid fire**: Máximo 5 posts/hora, depois 30min de pausa
- **Hashtags repetidas**: Máximo 10 usos a cada 20 posts

## Estratégia de Warm-Up

| Dias | Volume | Risco |
|------|--------|-------|
| 1-7 | 30% do máximo | Mínimo |
| 8-14 | 50% do máximo | Baixo |
| 15-30 | 70% do máximo | Moderado |
| 31+ | 100% (se sem restrições) | Normal |

## Ordem de Prioridade por Volume

### Alto Volume (prioridade máxima)
1. **Pinterest** → 25 pins/dia (maior volume seguro)
2. **Telegram** → 20 posts/dia (mais tolerante)
3. **Twitter/X** → 15 posts/dia
4. **Blog/Site** → 10 artigos/dia

### Médio Volume
5. **TikTok** → 5 vídeos/dia
6. **Facebook** → 5 posts/dia
7. **Instagram** → 3 posts/dia + 10 stories

### Baixo Volume (qualidade > quantidade)
8. **YouTube** → 2 vídeos/dia
9. **LinkedIn** → 2 posts/dia
10. **WhatsApp** → 3 mensagens/dia
11. **Email** → 1 campanha/dia

## Como Usar

```python
from campaign_autopilot.agents.safe_mass_posting import SafeMassPostingAgent

agent = SafeMassPostingAgent()

# Validar se um post pode ser publicado
result = agent.validate_post("instagram", {
    "title": "Meu post",
    "body": "Conteudo do post",
    "hashtags": ["#dica", "#tecnologia"],
}, account_age_days=90)

if result["status"] == "pass":
    print("Pode publicar!")
    agent.log_post("instagram", content, result)
elif result["status"] == "warn":
    print(f"Atencao: {result['warnings']}")
    # Publica mesmo assim, mas com cuidado
else:
    print(f"Bloqueado: {result['issues']}")
    # Espera e tenta depois

# Gerar plano de postagem segura
plan = agent.generate_posting_plan(articles, {
    "platforms": ["blog", "pinterest", "telegram"],
    "account_age_days": 180,
})
```

## Integração com o Pipeline

O SafeMassPostingAgent deve rodar **após** a geração de conteúdo e **antes** da publicação, como um gatekeeper que valida cada post contra as regras de spam.
