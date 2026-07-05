# 🖼️ Media Providers — Camada Unificada de Mídia

> Gerencie texto, imagem, áudio, música e vídeo através de uma API única com failover automático.
> **v5.2.3** — 16+ providers em 5 camadas

---

## Visão Geral

A camada `media_providers` (`src/campaign_autopilot/media_providers.py`) fornece uma abstração unificada sobre múltiplos providers de mídia com fallback automático, rastreamento de custo e ranking de qualidade.

## Arquitetura

---

## 🆕 CTO Media Prompt Architect (v5.2.3)

O sistema agora inclui o **CTO Media Prompt Architect** que aplica o meta-prompt do CTO Executive Director para gerar prompts cinematográficos validados antes de qualquer geração de mídia.

### Pipeline CTO para Mídia

```
PHASE 0  — Executive Input Validation (validação do brief de mídia)
PHASE 0.5 — Epistemic Review (classificação do que sabemos sobre o nicho)
PHASE 1  — Technical Classification (tipo de mídia, formato, resolução, codec)
PHASE 2  — Domain Modeling (conceitos visuais/auditivos específicos do nicho)
PHASE 3  — Architectural Design (composição, iluminação, paleta, mood, transições)
PHASE 4  — Quality Check (revisão epistemológica do prompt antes da geração)
PHASE 5  — Prompt Output (prompt final otimizado por provider)
```

### 9 Nichos Mapeados

| Nicho | Conceitos Visuais | Moods | Paletas |
|-------|-------------------|-------|---------|
| marketing digital | dados, gráficos, painéis | profissional, moderno | corporate_blue |
| empreendedorismo | escritório, crescimento | inspirador, ambicioso | warm_premium |
| finanças | candles, moedas, cofre | sério, sofisticado | dark_green |
| inteligência artificial | redes neurais, hologramas | futurista, inovador | cyberpunk |
| marketing afiliados | funil, comissões, home office | profissional, dinâmico | corporate_blue |
| saúde e bem-estar | meditação, natureza, spa | calmo, equilibrado | green_nature |
| desenvolvimento pessoal | horizonte, livros, escada | inspirador, reflexivo | warm_premium |
| moda e beleza | fashion, maquiagem, studio | elegante, sofisticado | rose_gold |
| viagens e turismo | destinos, mapas, aventura | aventureiro, livre | warm_sunset |

### Scripts

```bash
# Gerar mídia completa com prompts CTO
PYTHONPATH=src python3 scripts/gerar_midia_cto.py --all

# Gerar apenas prompts CTO (sem consumir API)
PYTHONPATH=src python3 -c "
from campaign_autopilot.prompt_architect import MediaPromptArchitect
a = MediaPromptArchitect()
prompt = a.build_image_prompt(niche='saude e bem-estar', keyword='meditacao', format_type='blog_featured')
print(prompt['prompt'][:300])
"
```


```
ProviderManager (singleton, lazy discovery, ~0.3s init)
│
├── TextProvider (3)
│   ├── LiteLLMTextProvider    (100+ modelos via OpenRouter/Anthropic/Gemini/Groq)
│   ├── FreeLLMTextProvider    (13 provedores gratuitos com failover automático)
│   └── StdlibFallbackProvider (fallback final sem dependências)
│
├── ImageProvider (8)
│   ├── PollinationsImageProvider  (grátis, zero dependências) ✅
│   ├── ReplicateImageProvider     (FLUX via Replicate) ❌ sem créditos
│   ├── DeepAIImageProvider        (DeepAI text2img) ❌ precisa Pro
│   ├── ProdiaImageProvider        (Stable Diffusion XL) ❌ sem chave
│   ├── OpenRouterImageProvider    (FLUX + SD via OpenRouter) ✅ funcional
│   ├── HFFastImageProvider        (SDXL/FLUX via HF Inference) ❌ sem chave
│   ├── DiffusersImageProvider     (local, requer torch) ⚠️ GPU only
│   └── PillowImageProvider        (fallback local, sem API) ✅ funcional
│
├── AudioProvider (4)
│   ├── KokoroTTSProvider          (modelo leve ~82M params) ❌ não instalado
│   ├── EdgeTTSProvider            (TTS neural, ~400 vozes) ✅ funcional
│   ├── OpenAITTSSpeechProvider    (TTS via OpenRouter) ❌ sem chave
│   └── GttsProvider               (Google TTS) ✅ funcional
│
├── MusicProvider (2)
│   ├── AudioCraftProvider         (MusicGen local, GPU) ⚠️ GPU only
│   └── AlgorithmicMusicProvider   (stdlib, geração procedural) ✅ funcional
│
├── VideoProvider (2)
│   └── MoviePyVideoProvider       (MoviePy, slideshow) ✅ funcional
│
└── MediaRouter
    ├── Auto Failover              (próximo provider se falhar)
    ├── Cost Tracking              (custo por chamada)
    ├── Quality Ranking            (rank interno de qualidade)
    └── Capability Detection       (discovery automático via importlib.metadata)
```

## Status Atual dos Providers

### ✅ Funcionando Imediatamente (sem chave)

| Provider | Tipo | Qualidade | Como usar |
|----------|------|-----------|-----------|
| **Pollinations** | Imagem | ⭐⭐⭐ | Sem chave, gera via URL HTTP |
| **Pillow** | Imagem | ⭐⭐ | Fallback local, composição manual |
| **Edge-TTS** | Áudio | ⭐⭐⭐⭐ | Vozes neurais Microsoft (~400 vozes) |
| **gTTS** | Áudio | ⭐⭐⭐ | Google TTS, 52 idiomas |
| **MoviePy** | Vídeo | ⭐⭐⭐ | Slideshow com transições (requer ffmpeg) |
| **Algorithmic Music** | Música | ⭐⭐ | Geração procedural de música |
| **OpenRouter (texto)** | Texto | ⭐⭐⭐⭐⭐ | 4 modelos funcionando (llama-3.3-70b, gpt-4o-mini, etc) |
| **OpenRouter (imagem)** | Imagem | ⭐⭐⭐⭐ | FLUX + SD via mesma chave |

### ❌ Requerem Chaves Novas

| Provider | Tipo | Problema | Solução |
|----------|------|----------|---------|
| **Groq (LLM)** | Texto | Chave expirada (403) | console.groq.com → nova API key |
| **Gemini (LLM)** | Texto | Chave inválida (400) | aistudio.google.com → nova API key |
| **Replicate** | Imagem | Sem créditos (402) | replicate.com → nova chave |
| **HuggingFace** | Imagem | Inválida (401) | huggingface.co → nova chave |
| **DeepAI** | Imagem | Precisa Pro (402) | deepai.org → upgrade ou nova chave |
| **Prodia** | Imagem | Sem chave | prodia.com → free tier |
| **Kokoro TTS** | Áudio | Não instalado | `pip install kokoro` |
| **OpenAI TTS** | Áudio | Sem chave | OPENAI_API_KEY válida |

## Uso Básico

```python
from campaign_autopilot.media_providers import (
    get_best_image_provider,
    get_best_audio_provider,
    get_provider_report,
)

# Melhor provider de imagem disponível
provider = get_best_image_provider()
img_bytes = provider.generate("gato astronauta no espaço", width=1024, height=1024)

# Melhor provider de áudio
audio = get_best_audio_provider().generate("Olá, mundo!", voice="pt-BR")

# Relatório completo
report = get_provider_report()
```

## Integração com Agentes

Os agentes `FreeImageGeneratorAgent` e `FreeVideoProducerAgent` usam o `MediaRouter` automaticamente:

```python
from campaign_autopilot.agents.free_image_gen import FreeImageGeneratorAgent
from campaign_autopilot.agents.base import CampaignContext

agent = FreeImageGeneratorAgent()
result = agent.run(CampaignContext(campaign={"niche": "gatos", "artifacts": {"prompt": "gato astronauta"}}))
```

## CLI

```bash
# Ver status de todos os providers
PYTHONPATH=src python3 -m campaign_autopilot.cli --providers
```

---

*Parte da documentação do Campaign Autopilot v5.2.3 — Atualizado em 2026-06-25.*
