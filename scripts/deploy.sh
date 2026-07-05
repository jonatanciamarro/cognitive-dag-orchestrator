#!/usr/bin/env bash
# Campaign Autopilot — Deploy em Produção
set -e

echo "=========================================="
echo "  Campaign Autopilot — Deploy"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Option 1: Docker
if command -v docker &> /dev/null; then
    echo "🐳 Docker detectado. Deseja usar Docker? [s/N]"
    read -r use_docker
    if [[ "$use_docker" == "s" || "$use_docker" == "S" ]]; then
        echo ""
        echo "Construindo e iniciando containers..."
        docker compose up -d --build
        echo ""
        echo "✅ Containers rodando!"
        echo "   📊 Dashboard: http://localhost:8501"
        echo "   📝 Logs: docker compose logs -f"
        exit 0
    fi
fi

# Option 2: Direct
echo "🚀 Iniciando autopilot em background..."
nohup .venv/bin/python scripts/autopilot.py \
    --workflow workflows/revenue_workflow.json \
    --context examples/content_workflow_context.json \
    --db .state/autopilot.db \
    --loop \
    --interval 48 \
    > .state/autopilot.log 2>&1 &
AUTOPILOT_PID=$!
echo "   ✅ Autopilot PID: $AUTOPILOT_PID"
echo "   📝 Log: .state/autopilot.log"

echo ""
echo "🖥️  Iniciando dashboard em background..."
nohup .venv/bin/streamlit run dashboard/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    > .state/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "   ✅ Dashboard PID: $DASHBOARD_PID"
echo "   📝 Log: .state/dashboard.log"

echo ""
echo "📊 Dashboard: http://localhost:8501"
echo ""
echo "Para parar:"
echo "  kill $AUTOPILOT_PID $DASHBOARD_PID"
echo ""
echo "Para ver logs:"
echo "  tail -f .state/autopilot.log"
