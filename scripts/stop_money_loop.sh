#!/usr/bin/env bash
# Stop Money Loop
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$SCRIPT_DIR/.state/money_loop.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill "$PID" 2>/dev/null; then
        echo "✅ Money Loop parado (PID: $PID)"
    else
        echo "⚠️ Processo $PID nao encontrado"
    fi
    rm -f "$PID_FILE"
else
    echo "❌ PID file nao encontrado. Tente: pkill -f money_loop.py"
fi
