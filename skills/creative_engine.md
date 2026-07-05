# CreativeEngine Skill — 6ª Ordem: Inteligência Criativa

## Propósito
Descobrir automaticamente novos nichos de mercado que ninguém está explorando,
criar configurações completas de nicho, e gerar produtos/ ofertas para monetização.

## Componentes

| Componente | Função |
|------------|--------|
| **MarketGapDetector** | Escaneia 15 domínios de mercado, rankeia por potencial |
| **NicheGenesisAgent** | Cria autor, persona, keywords, config completa do nicho |
| **NovelValueGenerator** | Gera produtos digitais, serviços, ângulos de conteúdo |
| **CreativeEngine** | Coordena detecção → gênese → monetização |

## Fluxo

```
1. SCAN → MarketGapDetector escaneia 15+ domínios
2. RANK → Ordena por score de oportunidade (0-1)
3. GENESIS → Cria configuração completa do nicho
4. VALUE → Gera produtos e ofertas para o nicho
5. LAUNCH → Se viabilidade > 0.5, adiciona ao ciclo
```

## Exemplo de Saída
```
Novo nicho detectado: "educacao_online" (score: 0.87)
  → Label: "Educacao Online Blog"
  → Autor: "Prof. Dr. Educacao Online"
  → Keywords: 6 iniciais geradas
  → Produtos: Ebook (R$27), Curso (R$97), Template (R$37)
```

## Dependências
- Nenhuma API externa
- SQLite para estado (planejado)
