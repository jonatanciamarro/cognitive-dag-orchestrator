# AnalyticsFeedbackAgent

## Função
Fecha o loop de aprendizado do sistema: coleta métricas de todos os agentes, avalia qualidade do ciclo, extrai lições e gera sugestões para o próximo ciclo.

## Entrada
- Outputs de TODOS os agentes do ciclo
- Métricas de SEO, compliance, conteúdo

## Saída
- Sumário do ciclo (artigos, vídeos, emails, pins)
- Score de qualidade (0-100)
- Lições extraídas (alimentam memória semântica)
- Sugestões para próximo ciclo

## Critérios de Score (0-100)
- Volume de artigos: até 15pts
- Volume de vídeos: até 10pts
- Volume de emails: até 10pts
- Volume de pins: até 10pts
- Multi-canais: até 20pts (5pts por canal)
- Qualidade de palavras: até 20pts
- Compliance: penalidade de 50% se bloqueado

## Regras
- Sempre executar por último (após todos os outros agentes)
- Lições são persistidas na memória semântica
- Sugestões são baseadas em gaps observados
- Score alto (80+) indica estratégia saudável

## Observações
- Este agente é o cérebro analítico do sistema
- As lições alimentam o MemoryLookupAgent em ciclos futuros
- Em produção: conectar a dados reais de tráfego e conversão
