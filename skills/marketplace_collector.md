# Marketplace Collector Agent

## Propósito

Coletar automaticamente ofertas do marketplace Hotmart, extraindo produtos, preços e comissões para o catálogo do sistema.

## Responsabilidades

- Pesquisar marketplace Hotmart por nicho
- Extrair códigos de produto e URLs de afiliado
- Coletar preços e comissões
- Registrar ofertas no catálogo do sistema
- Atualizar ofertas existentes com novos dados

## Inputs

- Nichos configurados para busca
- Código de afiliado Hotmart
- Configuração de coleta

## Outputs

- Ofertas coletadas e registradas
- Estatísticas de produtos encontrados
- Status da coleta

## Requer

- requests (`pip install requests`)

## Regras

- Respeitar rate limits do marketplace
- Validar URLs antes de registrar
- Não duplicar ofertas já existentes
