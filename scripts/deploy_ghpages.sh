#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Deploy para GitHub Pages (Manual)
# ═══════════════════════════════════════════════════════════════
# Uso:
#   bash scripts/deploy_ghpages.sh "Mensagem do commit"
#
# Pré-requisitos:
#   git init já rodado no projeto
#   git remote add origin git@github.com:seuuser/seurepo.git
# ═══════════════════════════════════════════════════════════════

set -euo pipefail
cd "$(dirname "$0")/.."

MSG="${1:-Atualização automática $(date '+%d/%m/%Y %H:%M')}"

echo "🚀 Deploying to GitHub Pages..."
echo "   Message: $MSG"

# Generate content first
echo ""
echo "📝 Generating content..."
python3 scripts/run_all_niches.py --articles 2

# Deploy to gh-pages branch
echo ""
echo "📤 Deploying site/ to gh-pages..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    git init
    git remote add origin "$(git config --get remote.origin.url 2>/dev/null || echo 'https://github.com/seuuser/seurepo.git')"
fi

# Use peaceiris action or manual gh-pages
if command -v gh &>/dev/null; then
    # GitHub CLI
    gh pages deploy --dist site/ --message "$MSG"
else
    echo "⚠️  gh CLI not found. Use GitHub Actions for auto-deploy."
    echo "   Push to main branch: git add . && git commit -m '$MSG' && git push"
fi

echo "✅ Deploy complete!"
