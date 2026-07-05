# 🎬 Cinematic Media Pipeline Skill

## Visão Geral
Pipeline de produção de mídia cinematográfica usando **apenas ferramentas gratuitas**:
- **Imagens**: Pillow + numpy (color grading, iluminação, composição, tipografia)
- **Vídeos**: MoviePy + Pillow (Ken Burns, transições, slides cinematográficos)
- **Áudio**: gTTS + pydub (narração TTS, música algorítmica, mixagem)

## Arquitetura

### Módulo Core: `src/campaign_autopilot/media_pipeline/`
- `cinematic_engine.py` — Efeitos visuais: blend modes, color grading, lighting, backgrounds
- `image_cinematic.py` — Produção de imagens cinematográficas multi-formato
- `video_cinematic.py` — Produção de vídeos com Ken Burns, transições, animações
- `audio_cinematic.py` — Produção de áudio: TTS, música, mixagem

### Agentes: `src/campaign_autopilot/agents/`
| Agente | Função |
|--------|--------|
| `CinematicImageAgent` | Gera imagens com qualidade cinematográfica (5 estilos, 6 formatos) |
| `CinematicVideoAgent` | Produz vídeos YouTube/TikTok com efeitos cinematográficos |
| `AudioProductionAgent` | Gera narração TTS + música de fundo + mixagem |
| `StoryboardAgent` | Planeja sequências visuais para vídeos e imagens |
| `MediaPipelineAgent` | Orquestra o pipeline completo de mídia |

## Estilos Cinematográficos

### Imagens
| Estilo | Grade | Lighting | Uso |
|--------|-------|----------|-----|
| `CINEMATIC` | Teal/Orange | Vignette | Blog featured, banners |
| `DRAMATIC` | High Contrast | God Rays | YouTube thumbnails |
| `VINTAGE` | Retro/Warm | Film Grain | Pinterest pins |
| `BOLD` | Vibrant | Bloom | Instagram posts |
| `PREMIUM` | Matte | None | Social cards |

### Vídeos
| Efeito | Descrição |
|--------|-----------|
| Ken Burns | Zoom/pan suave em imagens estáticas (8 modos) |
| Transições | Crossfade, fade, slide, zoom, wipe |
| Texto animado | Fade, slide, scale, typewriter |
| Slides | Title, content, CTA com design cinematográfico |

## Workflows

### Pipeline Completo de Mídia
```bash
# Via workflow principal (production_workflow — 39 steps)
make run

# Pipeline de mídia standalone
.venv/bin/python scripts/autopilot.py \
  --workflow workflows/media_pipeline_workflow.json \
  --context examples/affiliate_context.json \
  --db .state/db.sqlite3
```

### Teste Rápido
```python
from src.campaign_autopilot.media_pipeline.image_cinematic import CinematicImageProducer, ImageStyle

producer = CinematicImageProducer("output/images")
result = producer.generate_featured_image(
    "Guia Completo de Marketing Digital",
    "marketing digital",
    ImageStyle.CINEMATIC,
)
print(f"✅ Imagem gerada: {result['path']}")
```

## Dependências (todas gratuitas)
```bash
pip install Pillow moviepy numpy gtts pydub
```

## Output
- `output/images/` — Imagens cinematográficas (PNG)
- `output/videos/` — Vídeos cinematográficos (MP4)
- `output/audio/` — Áudio narração + música (MP3)
- `output/storyboards/` — Storyboards (JSON)
