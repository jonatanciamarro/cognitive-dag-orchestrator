# Link Validator Agent

## Propósito

Validar periodicamente que todos os links de afiliado no sistema estão funcionando e redirecionando corretamente.

## Responsabilidades

- Verificar se links de afiliado estão ativos
- Checar redirecionamentos (status HTTP)
- Identificar links quebrados ou expirados
- Alertar sobre links que precisam ser atualizados
- Gerar relatório de saúde dos links

## Inputs

- Base de dados de links de afiliado
- Periodicidade de validação configurada

## Outputs

- Status de cada link (válido/quebrado/expirado)
- Relatório de saúde dos links
- Recomendações de substituição

## Regras

- Links quebrados devem ser identificados em até 24h
- Links expirados devem ser substituídos automaticamente
- Relatório deve priorizar links com alto tráfego
