#!/bin/bash
# API Key scanner for pre-commit
# Detects exposed API keys, tokens, and credentials in staged files

set -e

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

SECRET_PATTERNS="sk-or-|gsk_|AIzaSy|ghp_|gho_|ghu_|ghs_|ghr_|rk_|AKIA|eyJ[A-Za-z0-9_-]+"

SECRETS=$(git diff --cached -U0 | grep -P "$SECRET_PATTERNS" || true)
if [ -n "$SECRETS" ]; then
    echo "❌ API KEY DETECTADA nos arquivos staged!"
    echo "=========================================="
    echo "$SECRETS"
    echo "=========================================="
    echo "Use: git diff --cached para ver os arquivos afetados"
    exit 1
fi

# Check if .env is staged
if echo "$STAGED_FILES" | grep -qE "(^|/)\.env$"; then
    echo "❌ .env file is staged! This would expose API keys."
    echo "   Use: git reset HEAD .env"
    exit 1
fi

exit 0
