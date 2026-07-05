# SelfHealingAgent

## Função
Auto-reparo do sistema. Monitora a saúde dos agentes e componentes, e executa ações corretivas automáticas.

## Health Checks Realizados
| Check | Severidade | Auto-Fix |
|-------|------------|----------|
| Diretórios de output | Média | ✅ Recria automaticamente |
| Arquivos temporários | Baixa | ✅ Limpa automaticamente |
| Diretórios de estado | Alta | ✅ Recria automaticamente |
| Integridade SQLite | Crítica | ✅ VACUUM + recovery |
| Históricos de agentes | Média | ✅ Reinicializa se vazio |

## Health Score
- **90-100%**: ✅ Sistema saudável
- **70-89%**: ⚠️ Pequenos ajustes
- **50-69%**: 🔶 Sistema degradado
- **<50%**: 🔴 Intervenção necessária

## Ações Corretivas Automáticas
- Recria diretórios ausentes
- Limpa temporários órfãos
- Executa VACUUM em bancos SQLite
- Reinicializa arquivos de histórico corrompidos
