# 📡 Media Providers — Guia de Configuração

> Status atual dos provedores de mídia no Campaign Autopilot v5.2.1
> 16 providers em 5 camadas (texto, imagem, áudio, música, vídeo)

---

## ✅ JÁ FUNCIONAM (Zero Configuração)

| Provedor | Tipo | Qualidade | Como ativa |
|---|---|---|---|
| **Pollinations.ai** | Imagem | Média | ✅ Já funciona — gera imagens via URL sem chave |
| **gTTS** | Áudio (TTS) | Boa | ✅ Instalado — Google TTS, 52 idiomas |
| **edge-tts** | Áudio (TTS) | Excelente | ✅ Instalado — Microsoft Neural TTS, vozes pt-BR Francisca/Antonio |
| **Pillow** | Imagem | Baixa | ✅ Fallback local — composição manual |
| **Algorithmic Music** | Música | Média | ✅ Já funciona — música procedural |
| **MoviePy** | Vídeo | Média | ✅ Instalado — slideshow com transições |
| **OpenRouter** | Texto + Imagem | Alta | ✅ 4 modelos LLM + FLUX via OpenRouter |

---

## 🟡 PRECISAM DE CHAVE NOVA (Melhora Qualidade)

| Provedor | Tipo | Onde pegar a chave | Status da Chave Atual |
|---|---|---|---|
| **Groq** | LLM (Llama 3 70B) | https://console.groq.com/keys | ❌ **Expirada (403)** |
| **Gemini** | LLM (Gemini Flash) | https://aistudio.google.com/apikey | ❌ **Inválida (400)** |
| **Replicate** | Imagem (FLUX.1) | https://replicate.com/account/api-tokens | ❌ **Sem créditos (402)** |
| **DeepAI** | Imagem | https://deepai.org (free tier) | ❌ **Precisa Pro (402)** |
| **Prodia** | Imagem (SDXL) | https://prodia.com (free tier) | ❌ Vazia |
| **HuggingFace** | Imagem + Texto | https://huggingface.co/settings/tokens | ❌ **Inválida (401)** |
| **Kokoro TTS** | Áudio (TTS leve) | `pip install kokoro` | ❌ Não instalado |

---

## 🔴 PRECISAM DE CONFIGURAÇÃO MANUAL (Só Você Pode Fazer)

| Provedor | O que fazer | Tempo |
|---|---|---|
| **Hotmart** | Criar conta → Integrações → API → Gerar CLIENT_ID + SECRET | 5 min |
| **Kiwify** | Criar conta → Configurações → Programa de Afiliados → Copiar ID | 3 min |
| **Eduzz** | Criar conta → Configurações → Afiliados → Copiar ID | 3 min |
| **ML/Shopee/SheIn** | Criar conta no programa de afiliados → Copiar ID | 5 min cada |
| **Amazon Associates** | https://associe.amazon.com.br → Criar tracking ID | 5 min |
| **WordPress** | Instalar WP + criar usuário admin | 10 min |

---

## 📊 Sumário: O que funciona AGORA sem chaves

```
TEXTO:   ✅ OpenRouter (4 modelos) + Stdlib Fallback
IMAGEM:  ✅ Pollinations.ai + Pillow (local)
ÁUDIO:   ✅ gTTS + edge-tts (vozes neurais pt-BR)
MÚSICA:  ✅ Algorithmic Music (procedural)
VÍDEO:   ✅ MoviePy (slideshow com transições)
```

### Testar Geração de Imagem

```bash
PYTHONPATH=src python3 -c "
from campaign_autopilot.media_providers import PollinationsImageProvider
p = PollinationsImageProvider()
img = p.generate('Banner marketing digital dark theme', width=1200, height=630)
open('output/test_image.jpg', 'wb').write(img)
print('✅ Imagem gerada em output/test_image.jpg')
"
```

### Testar Geração de Áudio

```bash
PYTHONPATH=src python3 -c "
from campaign_autopilot.media_providers import EdgeTTSProvider
p = EdgeTTSProvider()
audio = p.generate('Olá, esta é uma mensagem do Campaign Autopilot', voice='pt-BR-FranciscaNeural')
open('output/test_audio.mp3', 'wb').write(audio)
print('✅ Áudio gerado em output/test_audio.mp3')
"
```

---

## Wireframe da Arquitetura de Providers

```
Campaign Autopilot
    ↓
ProviderManager (singleton)
    ↓
MediaRouter
    ├── Auto Failover
    ├── Cost Tracking
    ├── Quality Ranking
    └── Capability Detection
    ↓
┌─────────────────────────────────────────────┐
│  Texto    │  Imagem   │  Áudio   │  Vídeo   │
├───────────┼───────────┼──────────┼──────────┤
│ OpenRouter│ Pollinat. │ EdgeTTS  │ MoviePy  │
│ Stdlib    │ Pillow    │ gTTS     │          │
└───────────┴───────────┴──────────┴──────────┘
```

---

*Atualizado em 2026-06-25 — Campaign Autopilot v5.2.1*
