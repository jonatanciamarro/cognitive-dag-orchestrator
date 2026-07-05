#!/usr/bin/env bash
set -euo pipefail

echo "=== Campaign Autopilot Setup ==="

# Python version check
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "❌ Python 3 not found. Install Python 3.10+ first."
    exit 1
fi

echo "✓ Python: $($PYTHON --version)"

# Create virtual environment
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv
    echo "✓ Virtual environment created"
fi

source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt 2>/dev/null || pip install numpy pillow moviepy gtts pydub streamlit requests
echo "✓ Dependencies installed"

# Create state directory
mkdir -p .state

# Create .env from example if not exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  .env created from .env.example — edit it with your API keys"
    fi
fi

# Verify imports
echo "Verifying system..."
$PYTHON -c "
import sys; sys.path.insert(0, 'src')
from campaign_autopilot.agents.base import CampaignContext
from campaign_autopilot.models import Campaign
from campaign_autopilot.workflow import WorkflowRunner, WorkflowSpec
from campaign_autopilot.semantic_memory import SemanticMemoryStore
from campaign_autopilot.explanation import ExplanationStore
from campaign_autopilot.feedback import OutcomeStore
from campaign_autopilot.synthesis import KnowledgeSynthesisEngine
from campaign_autopilot.goals import GoalRegistry
from campaign_autopilot.api_hub import APIHub
from campaign_autopilot.affiliate import OfferManager
print('✓ All core modules loaded successfully')
" 2>&1

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: .venv/bin/python scripts/autopilot.py --workflow workflows/money_workflow.json --context examples/content_workflow_context.json --db .state/autopilot.db"
echo "  3. Start dashboard: streamlit run dashboard/app.py"
echo ""
