# 📱 Campaign Autopilot no Celular — Guia 100% Grátis

> Como rodar e gerenciar o sistema inteiro do seu celular, sem gastar nada.

---

## Opção 1: Servidor Grátis na Nuvem (RECOMENDADO)

Você roda na nuvem (gratuito) e acessa do celular via navegador ou SSH.

### 1.1 Oracle Cloud — Always Free (melhor opção)

```bash
# O Oracle Cloud tem um tier gratuito que NUNCA expira:
# - 4 ARM cores + 24GB RAM
# - 200GB armazenamento
# - Banda larga ilimitada

# Isso roda o Campaign Autopilot COMPLETO sem problemas
# Inclusive modelos LLM locais via Ollama!
```

**Passo a passo:**
1. Criar conta: https://cloud.oracle.com (cartão de crédito para verificação, mas nunca cobra)
2. Criar VM "Always Free" (Ubuntu 22.04, ARM, 4 cores, 24GB RAM)
3. SSH do celular via Termux → `ssh ubuntu@seu_ip`
4. Instalar o sistema → `bash scripts/install_247.sh screen`

### 1.2 Google Cloud — Free Tier

```bash
# VM e2-micro (1 core, 1GB RAM) — GRÁTIS
# Suficiente para rodar o pipeline stdlib + LLM via API

# google-cloud-shell é ainda mais fácil — terminal no próprio navegador
# https://shell.cloud.google.com
```

### 1.3 PythonAnywhere — Free Tier

```bash
# Hospedagem Python grátis, já vem com Flask/Django
# Perfeito para dashboard e API leve
# https://www.pythonanywhere.com/
```

### 1.4 Cloudflare Workers + Pages — Free Tier

```bash
# Para deploy do site estático gerado (DE GRAÇA)
# Domínio próprio incluso
# https://pages.cloudflare.com/
```

---

## Opção 2: Rodar Direto no Celular (Termux)

O sistema funciona nativamente no Android via **Termux**.

### 2.1 Instalar Termux

```bash
# 1. Baixar Termux: https://f-droid.org/packages/com.termux/
#    (NÃO usar Play Store — versão desatualizada)

# 2. Baixar Termux:API para recursos extras
#    https://f-droid.org/packages/com.termux.api/
```

### 2.2 Instalar Python + Dependências

```bash
pkg update && pkg upgrade -y
pkg install python python-pip git -y
pkg install openssh -y  # Para SSH

# Instalar dependências essenciais
pkg install libxml2 libxslt clang make -y
```

### 2.3 Clonar o Projeto e Instalar

```bash
cd ~
git clone https://github.com/seu-usuario/campaign-autopilot
cd campaign-autopilot

python -m venv .venv
source .venv/bin/activate

# Instalar apenas o core (sem media pesada)
pip install numpy pillow requests

# .env com só chave da LLM (GROQ é o mais leve)
echo 'GROQ_API_KEY=sua_chave' > .env
echo 'GROQ_MODEL=gemma4-1b-it' >> .env  # Modelo 1B - rápido no celular
```

### 2.4 Rodar o Sistema

```bash
# Ciclo manual
python -m campaign_autopilot.cli_v2 \
  --workflow workflows/money_workflow.json \
  --context examples/content_workflow_context.json \
  --db .state/autopilot.db \
  --mode full

# Ou em background (mesmo fechando o Termux)
python scripts/autopilot_daemon.py &
```

### 2.5 Ollama no Celular (LLM Local)

```bash
# Instalar Ollama no Termux (experimental)
pkg install ollama -y  # Se disponível

# Ou baixar APK:
# https://github.com/ollama/ollama/releases

# Rodar modelo pequeno (Gemma 4 1B ~700MB)
ollama pull gemma4:1b
OLLAMA_MODEL=gemma4:1b

# Consumo: ~2GB RAM, ~700MB storage
# Velocidade: ~10-20 tokens/s em celular médio
```

### 2.6 Limitações no Celular

| Componente | Funciona? | Observação |
|-----------|-----------|------------|
| Workflow Engine | ✅ Completo | 122 agentes, stdlib puro |
| LLM via API | ✅ | Groq/Gemini/OpenRouter |
| Ollama local | ✅ Limitado | Modelos 1B-4B apenas |
| Imagens (Pillow) | ✅ Leve | 800x600 máximo |
| Vídeos (MoviePy) | ⚠️ Pesado | Processamento lento |
| Áudio (gTTS) | ✅ Leve | Só texto-para-fala |
| Dashboard | ⚠️ | Streamlit pesado no celular |
| Site Generator | ✅ | Gera HTML estático |

---

## Opção 3: Acessar a Dashboard do Celular

### 3.1 Dashboard via Streamlit (LAN)

```bash
# No servidor (VPS ou PC):
streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0

# No celular (mesma rede WiFi):
# http://192.168.1.X:8501
# (substitua X pelo IP do servidor)
```

### 3.2 Dashboard via Túnel Grátis (Ngrok)

```bash
# No servidor, instalar ngrok
# https://ngrok.com/download

# Expor dashboard:
ngrok http 8501

# URL gerada (ex: https://abc123.ngrok.io)
# Acessar de QUALQUER LUGAR pelo celular
```

### 3.3 Dashboard via Cloudflare Tunnel (recomendado)

```bash
# Cloudflare Tunnel é grátis e mais seguro que ngrok
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/

cloudflared tunnel --url http://localhost:8501
```

---

## Opção 4: Acesso SSH do Celular

```bash
# Termux + SSH = terminal completo no celular

# No servidor:
sudo apt install openssh-server -y

# No Termux (celular):
pkg install openssh -y
ssh usuario@ip_do_servidor

# Comandos úteis:
python scripts/autopilot_daemon.py --status   # Status do sistema
screen -r autopilot                            # Ver logs ao vivo
sudo journalctl -u campaign-autopilot -f       # Logs do serviço
```

---

## Resumo: Melhor Setup Grátis para Celular

```
📱 CELULAR (cliente)
  │
  ├── Termux → SSH → Servidor na nuvem
  │           → python scripts/autopilot_daemon.py --status
  │           → screen -r autopilot
  │
  ├── Navegador → Ngrok/Cloudflare → Dashboard Streamlit
  │             → http://seu-tunel-gratis.ngrok.io
  │             → Métricas, status, ciclos
  │
  └── Navegador → Cloudflare Pages → Site Estático
                → https://seu-site.pages.dev
                → Conteúdo gerado publicamente

🖥️ SERVIDOR GRÁTIS (Oracle Cloud)
  │
  ├── 4 ARM cores + 24GB RAM → NUNCA expira
  ├── Campaign Autopilot completo
  ├── Dashboard Streamlit
  ├── Site Generator
  └── 13 provedores LLM com failover
```

### Instalação Completa (4 comandos)

```bash
# 1. Conectar ao servidor (do Termux):
ssh ubuntu@ip_do_servidor

# 2. Baixar e instalar:
git clone <seu-repo> && cd campaign-autopilot
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configurar (opcional — sem chaves funciona com stdlib):
echo 'GROQ_API_KEY=sua_chave' > .env

# 4. Iniciar 24/7:
bash scripts/install_247.sh screen

# 5. (Opcional) Expor dashboard:
# ngrok http 8501
```

---

## Comparação de Custos

| Método | Custo Mensal | Hardware | LLM | Esforço Setup |
|--------|-------------|----------|-----|---------------|
| Oracle Cloud Free | **R$ 0** | 4 cores + 24GB | API ou local | 30 min |
| PythonAnywhere Free | **R$ 0** | 1 core + 512MB | API apenas | 10 min |
| Google Cloud Free | **R$ 0** | 1 core + 1GB | API apenas | 20 min |
| Celular (Termux) | **R$ 0** | Snapdragon + 6GB | API apenas | 15 min |
| VPS Paga | R$ 30-50 | 2 cores + 4GB | Qualquer | 5 min |

**Recomendação:** Oracle Cloud Always Free + Groq API = sistema completo rodando 24/7, acessível do celular, **custo ZERO**.

---

## Comandos Rápidos para o Celular

```bash
# Via Termux — atalhos para monitorar:

# Status rápido
alias autopilot-status='python scripts/autopilot_daemon.py --status'
# Últimos logs
alias autopilot-logs='tail -20 .state/logs/daemon.log'
# Heartbeat
alias autopilot-hb='cat .state/logs/heartbeat.json | python -m json.tool'
# Dashboard (se rodando local)
alias autopilot-dash='echo "http://localhost:8501"'
```

---

*Guia Mobile — Campaign Autopilot v5.2.1*
*13 provedores LLM + failover + stdlib = 100% grátis em qualquer lugar*
