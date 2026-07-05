# FreeVideoProducerAgent

## Função
Produz vídeos gratuitamente usando moviepy + Pillow. Sem APIs pagas.

## Formatos Suportados

| Tipo | Dimensões | Uso |
|------|-----------|-----|
| YouTube Slideshow | 1920x1080 (16:9) | Vídeos educativos |
| TikTok/Reels | 1080x1920 (9:16) | Vídeos curtos verticais |

## Características
- Slides animados com gradientes
- Transições fade in/out
- Quebra de texto automática
- Vídeos em MP4 (H.264)
- Totalmente gratuito

## Dependências
```bash
pip install moviepy Pillow
```

## Como Usar
Os vídeos são gerados automaticamente quando o agente executa no workflow.
Arquivos em output/videos/.

## Estrutura de Saída
```json
{
  "videos_generated": 5,
  "videos": [
    {"type": "youtube_slideshow", "filename": "yt_guia-marketing.mp4", "duration_sec": 30},
    {"type": "tiktok_short", "filename": "tt_marketing-afiliados.mp4", "duration_sec": 15}
  ],
  "output_directory": "/project/output/videos"
}
```

## Limitações Atuais
- Sem áudio (futuro: TTS gratuito como gTTS)
- Sem cenas complexas (apenas slides)
- Sem legendas automáticas (futuro)
