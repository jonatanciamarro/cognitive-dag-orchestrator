# Config Updater Agent

## Propósito

Manter configurações de afiliados atualizadas automaticamente, sincronizando com mudanças em redes de afiliados.

## Responsabilidades

- Atualizar códigos de afiliado nas configurações
- Sincronizar mudanças de comissão
- Atualizar links quando IDs mudam
- Verificar validade das configurações atuais
- Notificar sobre mudanças que exigem ação manual

## Inputs

- Configurações atuais de afiliados
- Dados das redes de afiliados
- Histórico de mudanças

## Outputs

- Configurações atualizadas
- Relatório de mudanças aplicadas
- Alertas de mudanças que exigem ação

## Regras

- Mudanças automáticas devem ser registradas em log
- Mudanças críticas devem ser revisadas antes de aplicar
- Configurações anteriores devem ser preservadas para rollback
