# WordPressPublisherAgent

## Função
Publica conteúdo gerado em sites WordPress, suportando modos simulado e real via REST API.

## Entrada
- Artigos gerados (do ContentGeneratorAgent)
- Status de compliance
- Canais configurados

## Saída
- Resultados da publicação (local ou WordPress)
- Estatísticas: total de artigos, palavras, erros
- Plano de publishing

## Modos de Operação
- **file (padrão)**: Salva artigos como arquivos .md no diretório `output/content/`. Não requer credenciais.
- **api**: Publica via WordPress REST API. Requer WP_URL, WP_USER e WP_PASSWORD no .env.
- **dry_run**: Apenas registra o que seria publicado, sem escrever arquivos.

## Regras
- Bloquear se compliance falhar
- Fallback automático para modo file se credenciais ausentes
- Cronograma: 1 artigo a cada 3 dias
- Status inicial: draft (rascunho) para revisão manual

## Configuração (.env.example)
```
WP_URL=https://meusite.com
WP_USER=seu_usuario
WP_PASSWORD=sua_senha_de_aplicativo
```

## Observações
- Application Password é gerada no perfil do WordPress (Users → Application Passwords)
- Modo file é ideal para revisão manual antes de publicar
- Em produção: agendar publicação automática após aprovação
