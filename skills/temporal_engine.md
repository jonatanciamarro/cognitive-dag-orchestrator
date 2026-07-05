# TemporalEngine Skill — 5ª Ordem: Inteligência Temporal

## Propósito
Conectar passado, presente e futuro em uma narrativa coerente.
Detectar padrões sazonais, projetar trajetórias e otimizar timing.

## Componentes

| Componente | Função |
|------------|--------|
| **NarrativeSelf** | Quem o sistema foi, onde está, para onde vai |
| **StrategicForesight** | Projeções de receita, artigos, crescimento |
| **SeasonalDetector** | 10 eventos sazonais BR monitorados |
| **TemporalStore** | Timeline persistente (SQLite) |

## Fluxo

```
1. RECORD → Registra ciclo atual na timeline
2. NARRATE → Constrói NarrativeSelf (passado)
3. FORESIGHT → Projeta 30/60/90 dias (futuro)
4. SEASONAL → Detecta eventos sazonais próximos
5. RECOMMEND → Timing de conteúdo + metas estratégicas
```

## Arquivo de Estado
`.state/temporal.db`
