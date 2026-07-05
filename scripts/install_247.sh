#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Install Campaign Autopilot as 24/7 Service
# ═══════════════════════════════════════════════════════════════
# Este script configura o sistema para rodar 24/7 de 3 formas:
#   1. systemd service (recomendado para servidores Linux)
#   2. Docker Compose (recomendado para qualquer ambiente)
#   3. Screen/Tmux (simples, qualquer ambiente)
#
# Uso:
#   bash scripts/install_247.sh          # Menu interativo
#   bash scripts/install_247.sh systemd  # Instalar como serviço
#   bash scripts/install_247.sh docker   # Instalar com Docker
#   bash scripts/install_247.sh screen   # Modo screen simples
#   bash scripts/install_247.sh status   # Verificar status
#   bash scripts/install_247.sh stop     # Parar serviço
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
header(){ echo -e "\n${CYAN}$1${NC}\n${CYAN}$(printf '═%.0s' $(seq 1 60))${NC}"; }

WORKFLOW="${WORKFLOW:-workflows/money_workflow.json}"
CONTEXT="${CONTEXT:-examples/content_workflow_context.json}"
DB="${DB:-.state/autopilot.db}"
INTERVAL="${INTERVAL:-48}"

# ═══════════════════════════════════════════════════════════════
# 1. SYSTEMD
# ═══════════════════════════════════════════════════════════════

install_systemd() {
    header "📦 Installing as systemd service"

    # Create log directory
    mkdir -p .state/logs

    # Copy service file
    sudo cp campaign-autopilot.service /etc/systemd/system/

    # Update paths in service file
    sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|" /etc/systemd/system/campaign-autopilot.service
    sudo sed -i "s|ExecStart=.*|ExecStart=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/scripts/autopilot_daemon.py --workflow $WORKFLOW --context $CONTEXT --db $DB --interval $INTERVAL --max-restarts 5|" /etc/systemd/system/campaign-autopilot.service
    sudo sed -i "s|ExecStop=.*|ExecStop=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/scripts/autopilot_daemon.py --stop|" /etc/systemd/system/campaign-autopilot.service
    sudo sed -i "s|StandardOutput=append:.*|StandardOutput=append:$PROJECT_DIR/.state/logs/systemd.log|" /etc/systemd/system/campaign-autopilot.service
    sudo sed -i "s|StandardError=append:.*|StandardError=append:$PROJECT_DIR/.state/logs/systemd-error.log|" /etc/systemd/system/campaign-autopilot.service

    # Reload and enable
    sudo systemctl daemon-reload
    sudo systemctl enable campaign-autopilot
    sudo systemctl restart campaign-autopilot

    info "✅ Service installed and started!"
    echo ""
    echo "   Commands:"
    echo "     sudo systemctl status campaign-autopilot   # Ver status"
    echo "     sudo systemctl stop campaign-autopilot     # Parar"
    echo "     sudo systemctl start campaign-autopilot    # Iniciar"
    echo "     sudo systemctl restart campaign-autopilot  # Reiniciar"
    echo "     sudo journalctl -u campaign-autopilot -f   # Ver logs"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# 2. DOCKER
# ═══════════════════════════════════════════════════════════════

install_docker() {
    header "🐳 Deploying with Docker Compose"

    if ! command -v docker &>/dev/null; then
        error "Docker not found. Install: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi

    # Create state directories
    mkdir -p .state output content reports

    # Build and start
    docker compose up --build -d

    info "✅ Docker containers started!"
    echo ""
    echo "   Commands:"
    echo "     docker compose ps           # Ver status"
    echo "     docker compose logs -f      # Ver logs"
    echo "     docker compose down         # Parar"
    echo "     docker compose up -d        # Iniciar"
    echo "     docker compose restart      # Reiniciar"
    echo "     http://localhost:8501        # Dashboard"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# 3. SCREEN
# ═══════════════════════════════════════════════════════════════

install_screen() {
    header "📺 Starting in Screen session"

    if ! command -v screen &>/dev/null; then
        warn "Screen not found. Installing..."
        apt-get install -y screen 2>/dev/null || yum install -y screen 2>/dev/null || true
    fi

    SESSION_NAME="autopilot"

    # Kill existing session
    screen -S "$SESSION_NAME" -X quit 2>/dev/null || true

    # Create new session
    screen -dmS "$SESSION_NAME" bash -c "
        cd $PROJECT_DIR
        source .venv/bin/activate
        python scripts/autopilot_daemon.py \
            --workflow $WORKFLOW \
            --context $CONTEXT \
            --db $DB \
            --interval $INTERVAL \
            --max-restarts 5
    "

    info "✅ Autopilot running in Screen session '$SESSION_NAME'"
    echo ""
    echo "   Commands:"
    echo "     screen -r autopilot          # Anexar ao terminal"
    echo "     Ctrl+A, D                   # Desanexar (deixa rodando)"
    echo "     pkill -f autopilot_daemon   # Parar"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════

check_status() {
    header "📊 Autopilot Status Check"

    # Check systemd
    if systemctl is-active --quiet campaign-autopilot 2>/dev/null; then
        echo -e "${GREEN}✅ systemd:${NC} Active"
        systemctl status campaign-autopilot --no-pager | head -15
    else
        echo -e "${YELLOW}⬜ systemd:${NC} Not installed"
    fi

    # Check screen
    if screen -ls 2>/dev/null | grep -q autopilot; then
        echo -e "${GREEN}✅ Screen:${NC} Session running"
        screen -ls | grep autopilot
    else
        echo -e "${YELLOW}⬜ Screen:${NC} No session"
    fi

    # Check Docker
    if docker compose ps 2>/dev/null | grep -q "autopilot"; then
        echo -e "${GREEN}✅ Docker:${NC} Running"
        docker compose ps
    else
        echo -e "${YELLOW}⬜ Docker:${NC} Not running"
    fi

    # Check daemon heartbeat
    if [ -f .state/logs/heartbeat.json ]; then
        echo -e "${GREEN}✅ Heartbeat:${NC}"
        python3 -c "import json; d=json.load(open('.state/logs/heartbeat.json')); [print(f'    {k}: {v}') for k,v in d.items()]"
    fi
}

# ═══════════════════════════════════════════════════════════════
# STOP
# ═══════════════════════════════════════════════════════════════

stop_service() {
    header "🛑 Stopping Autopilot"

    # systemd
    if systemctl is-active --quiet campaign-autopilot 2>/dev/null; then
        sudo systemctl stop campaign-autopilot
        info "✅ systemd service stopped"
    fi

    # Docker
    if docker compose ps 2>/dev/null | grep -q "autopilot"; then
        docker compose down
        info "✅ Docker containers stopped"
    fi

    # Screen
    screen -S autopilot -X quit 2>/dev/null || true
    info "✅ Screen session stopped"

    # Daemon stop command
    python3 scripts/autopilot_daemon.py --stop 2>/dev/null || true

    # Kill any remaining
    pkill -f "autopilot_daemon" 2>/dev/null || true
    info "✅ All processes stopped"
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

# Ensure .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        warn "⚠️  .env created from .env.example — edit it with your API keys"
    fi
fi

# Ensure .venv exists
if [ ! -d .venv ]; then
    info "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt 2>/dev/null || true
fi

case "${1:-menu}" in
    systemd)
        install_systemd ;;
    docker)
        install_docker ;;
    screen)
        install_screen ;;
    status)
        check_status ;;
    stop)
        stop_service ;;
    menu|*)
        header "🚀 Campaign Autopilot — 24/7 Installation"
        echo "Escolha como instalar:"
        echo ""
        echo "  1) systemd — Serviço nativo Linux (recomendado para servidor)"
        echo "  2) Docker — Containerizado (recomendado para qualquer ambiente)"
        echo "  3) Screen — Sessão simples (qualquer ambiente)"
        echo "  4) Status — Verificar status atual"
        echo "  5) Stop — Parar tudo"
        echo ""
        read -rp "Escolha [1-5]: " choice
        case "$choice" in
            1) install_systemd ;;
            2) install_docker ;;
            3) install_screen ;;
            4) check_status ;;
            5) stop_service ;;
            *) error "Opção inválida" ;;
        esac
        ;;
esac
