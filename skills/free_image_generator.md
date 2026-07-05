# FreeImageGeneratorAgent

## Função
Gera imagens profissionais gratuitamente usando Pillow. Sem APIs pagas.

## Formatos Suportados

| Tipo | Dimensões | Uso |
|------|-----------|-----|
| Blog Featured | 1200x630 | Open Graph, artigos do blog |
| YouTube Thumbnail | 1280x720 | Thumbnails de vídeos |
| Pinterest Pin | 1000x1500 (2:3) | Pins verticais |
| Instagram Post | 1080x1080 | Feed quadrado |
| Social Card | 1200x630 | Twitter/LinkedIn cards |

## Características
- Gradientes automáticos em 8 paletas de cores
- Elementos decorativos (círculos, linhas, formas)
- Quebra de texto automática
- Sombras para legibilidade
- Formato PNG otimizado
- Zero dependências pagas

## Dependências
```bash
pip install Pillow
```

## Como Usar
```python
from campaign_autopilot.agents.free_image_gen import FreeImageGeneratorAgent
agent = FreeImageGeneratorAgent()
result = agent.run(context)
# Imagens em output/images/
```

## Estrutura de Saída
```json
{
  "images_generated": 12,
  "images": [
    {"type": "blog_featured", "filename": "featured_guia-marketing.png", "path": "output/images/..."},
    {"type": "youtube_thumbnail", "filename": "thumb_como-comecar.png", "path": "...", "width": 1280, "height": 720}
  ],
  "output_directory": "/project/output/images"
}
```
