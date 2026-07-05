# Cinematic Video Agent

## Propósito

Produzir vídeos com qualidade cinematográfica usando ferramentas gratuitas (MoviePy + Pillow).

## Responsabilidades

- Criar slideshow videos com transições profissionais
- Aplicar efeitos Ken Burns em imagens estáticas
- Adicionar color grading cinematográfico
- Inserir narração e música de fundo
- Renderizar nos formatos YouTube e TikTok

## Inputs

- Imagens e conteúdo de origem
- Formato alvo (16:9 YouTube, 9:16 TikTok)
- Script/roteiro de narração
- Música de fundo (opcional)

## Outputs

- Vídeo renderizado em MP4
- Metadados do vídeo (duração, resolução)
- Caminho do arquivo salvo

## Requer

- MoviePy + Pillow instalados (`pip install moviepy Pillow`)
- ffmpeg disponível no sistema

## Regras

- Transições devem ser suaves e profissionais
- Áudio deve ser normalizado para volume consistente
- Legendas devem ser sincronizadas com a narração
