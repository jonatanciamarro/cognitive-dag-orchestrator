# Browser Automation Agent

## Propósito

Automatizar interações com plataformas que não possuem API pública, usando Selenium WebDriver.

## Responsabilidades

- Publicar conteúdo em plataformas sem API
- Extrair dados de plataformas sem API
- Automatizar interações repetitivas
- Gerenciar sessões de login
- Respeitar rate limits das plataformas

## Inputs

- Plataforma alvo e credenciais
- Conteúdo a ser publicado
- Ação a ser executada

## Outputs

- Status da automação
- Comprovante de execução (screenshot)
- Dados extraídos (se aplicável)

## Requer

- Selenium + webdriver-manager (`pip install selenium webdriver-manager`)
- Chrome/Chromium instalado

## Regras

- Respeitar termos de serviço das plataformas
- Rate limiting para evitar bloqueio
- Credenciais devem ser armazenadas seguramente
