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
#
# Uses git commit date (not file mtime) — mtime resets on every
# checkout, so a re-clone would defeat pruning. Commit date is stable
# across clones and branch switches.

set -e

DAYS="${1:-180}"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}
cd "$REPO_ROOT"

ARCHIVE_DIR="archive/chat-history-$(date +%Y-%m-%d)"

# Compute the cutoff timestamp (DAYS ago, in seconds since epoch).
CUTOFF_TS=$(date -d "-$DAYS days" +%s 2>/dev/null || date -v-${DAYS}d +%s 2>/dev/null)
if [ -z "$CUTOFF_TS" ]; then
    echo "Error: couldn't compute cutoff date. Try GNU date or BSD date." >&2
    exit 1
fi

# Find tracked transcripts older than the cutoff, by git commit date.
# Use git log to get the last commit date for each file, then compare.
# -not -name README.md and -not -name INDEX.md: skip convention docs.
TRANSCRIPTS=$(find chat_history -type f -name "*.md" \
    -not -name "README.md" \
    -not -name "INDEX.md" 2>/dev/null || true)

if [ -z "$TRANSCRIPTS" ]; then
    echo "No transcripts found in chat_history/."
    exit 0
fi

PRUNED=0
echo "Checking transcripts older than $DAYS days (by commit date)..."
echo "Archive destination: $ARCHIVE_DIR"
echo ""

echo "$TRANSCRIPTS" | while IFS= read -r file; do
    # Get last commit date for this file (ISO format).
    commit_date=$(git log -1 --format=%ai -- "$file" 2>/dev/null || echo "")
    if [ -z "$commit_date" ]; then
        # Untracked file — fall back to mtime.
        commit_date=$(stat -c %y "$file" 2>/dev/null || stat -f %Sm "$file" 2>/dev/null || echo "")
    fi

    if [ -z "$commit_date" ]; then
        echo "  skip (no date): $file"
        continue
    fi

    # Parse the date to epoch seconds (handle both GNU and BSD).
    file_ts=$(date -d "$commit_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$commit_date" +%s 2>/dev/null || echo "")
    if [ -z "$file_ts" ]; then
        echo "  skip (date parse failed): $file"
        continue
    fi

    if [ "$file_ts" -lt "$CUTOFF_TS" ]; then
        # Preserve model folder structure under archive/
        rel=$(echo "$file" | sed 's|^chat_history/||')
        dest="$ARCHIVE_DIR/$rel"
        mkdir -p "$(dirname "$dest")"

        # Use git mv if tracked, else plain mv
        if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
            git mv "$file" "$dest"
        else
            mv "$file" "$dest"
        fi
        echo "  archived: $file -> $dest (last commit: $commit_date)"
        PRUNED=$((PRUNED + 1))
    fi
done

echo ""
echo "Done. If any files were moved, commit the change:"
echo "  git add -A && git commit -m \"archive old chat history\""
