#!/usr/bin/env bash
# ============================================================
# start_money_loop.sh — Inicia o Money Loop 24/7
# ============================================================
# Uso: bash scripts/start_money_loop.sh
# Logs: tail -f .state/money_loop.log
# Parar: kill $(cat .state/money_loop.pid)
# ============================================================
set -e

cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "============================================================"
echo "💰 MONEY LOOP — Campaign Autopilot"
echo "============================================================"
echo "Projeto: $PROJECT_ROOT"
echo "Inicio:  $(date)"
echo ""

# Verificar .env
if [ ! -f .env ]; then
    echo "❌ .env nao encontrado. Copie .env.example para .env e configure as chaves."
    exit 1
fi

# Verificar Python
if [ ! -d .venv ]; then
    echo "📦 Criando virtualenv..."
    python3 -m venv .venv
    .venv/bin/pip install -q numpy pillow gtts pydub streamlit 2>/dev/null || true
fi

# Criar diretorios
mkdir -p .state output/landing_pages output/emails output/reports

# Verificar permissão de execução
echo "✅ Ambiente verificado"
echo ""

# Iniciar Money Loop
echo "🚀 Iniciando Money Loop em background..."
echo "   Log: .state/money_loop.log"
echo "   PID: .state/money_loop.pid"
echo ""

nohup .venv/bin/python scripts/money_loop.py \
    --workflow workflows/organic_affiliate_cycle.json \
    --context examples/affiliate_context.json \
    --db .state/money_loop.db \
    --output output \
    --interval 24 \
    >> .state/money_loop.log 2>&1 &

PID=$!
echo $PID > .state/money_loop.pid
echo "✅ Money Loop rodando (PID: $PID)"

echo ""
echo "   Comandos uteis:"
echo "   tail -f .state/money_loop.log     # Ver logs"
echo "   python scripts/money_loop.py --stats  # Ver estatisticas"
echo "   kill \$(cat .state/money_loop.pid)    # Parar"
echo "============================================================"
