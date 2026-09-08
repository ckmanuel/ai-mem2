#!/bin/sh
# Move transcripts older than N days to archive/chat-history-<date>/.
#
# Usage:
#   ./scripts/prune_chat_history.sh [days]
#
# Default: 180 days (6 months). Edit to suit.
#
# Transcripts aren't deleted — moved to archive/ so they're still
# accessible if needed. The archive folder keeps the model subfolder
# structure. After moving, commit and push.

set -e

DAYS="${1:-180}"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}
cd "$REPO_ROOT"

ARCHIVE_DIR="archive/chat-history-$(date +%Y-%m-%d)"

# Find transcripts older than DAYS.
# -not -name README.md and -not -name INDEX.md: skip the convention docs.
OLD_FILES=$(find chat_history -type f -name "*.md" \
    -not -name "README.md" \
    -not -name "INDEX.md" \
    -mtime +$DAYS 2>/dev/null || true)

if [ -z "$OLD_FILES" ]; then
    echo "No transcripts older than $DAYS days found."
    exit 0
fi

echo "Pruning transcripts older than $DAYS days..."
echo "Archive destination: $ARCHIVE_DIR"
echo ""

echo "$OLD_FILES" | while IFS= read -r file; do
    # Preserve model folder structure under archive/
    rel=$(echo "$file" | sed 's|^chat-history/||' | sed 's|^chat_history/||')
    dest="$ARCHIVE_DIR/$rel"
    mkdir -p "$(dirname "$dest")"

    # Use git mv if the file is tracked, else plain mv
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        git mv "$file" "$dest"
    else
        mv "$file" "$dest"
    fi
    echo "  archived: $file -> $dest"
done

echo ""
echo "Done. If any files were moved, commit the change:"
echo "  git add -A && git commit -m \"archive old chat history\""
