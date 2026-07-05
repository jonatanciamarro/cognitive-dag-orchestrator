#!/bin/bash
# safe-push.sh — Push to GitHub without exposing tokens
# Usage: ./scripts/safe-push.sh [remote] [branch]

REMOTE="${1:-origin}"
BRANCH="${2:-master}"

# Get current remote URL
ORIG_URL=$(git remote get-url "$REMOTE" 2>/dev/null)

# Check if token is embedded in URL
case "$ORIG_URL" in
    *ghp_*|*gho_*|*ghu_*|*ghs_*|*ghr_*)
        echo "⚠️  Token detected in remote URL. Cleaning before push..."
        # Extract the clean URL (remove token)
        CLEAN_URL=$(echo "$ORIG_URL" | sed -E 's|https://[^:]+:[^@]+@|https://|')
        git remote set-url "$REMOTE" "$CLEAN_URL"
        echo "   Clean URL set. Token removed."
        NEED_RESTORE=1
        ;;
    *)
        NEED_RESTORE=0
        ;;
esac

# Run the pre-push hook check (dry-run)
echo "🔍 Running secret scan..."
git push --dry-run "$REMOTE" "$BRANCH" 2>&1
DRY_EXIT=$?

if [ $DRY_EXIT -ne 0 ]; then
    echo "❌ Dry-run failed. Fix issues before pushing."
    exit 1
fi

echo "✅ Dry-run passed. Pushing..."
git push "$REMOTE" "$BRANCH"
PUSH_EXIT=$?

if [ $PUSH_EXIT -eq 0 ]; then
    echo "✅ Push successful!"
else
    echo "❌ Push failed."
fi

exit $PUSH_EXIT
