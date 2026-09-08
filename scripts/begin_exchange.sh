#!/bin/sh
# Append a placeholder exchange entry to the current session's transcript.
#
# Usage:
#   ./scripts/begin_exchange.sh <trace_id> [exchange_num]
#
# Reads user message from stdin (or skips user message if stdin is empty).
# Appends:
#
#   #### Exchange N — trace <trace_id>
#
#   **User:**
#
#   > <user message from stdin, or "(see chat log)">
#
#   **Assistant:**
#
#   > (in progress...)
#
# The assistant later replaces "(in progress...)" with the actual reply.
# If the assistant forgets, the transcript shows an incomplete exchange —
# visible failure that the next session can backfill.
#
# Auto-detects the current session's transcript file by looking for the
# most recently modified .md file under chat_history/<model>/ (excluding
# README.md and INDEX.md). If no transcript exists yet, exits with an
# error (run ./scripts/new_session.sh first).

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <trace_id> [exchange_num]" >&2
    echo "" >&2
    echo "Example:" >&2
    echo "  echo 'what did I say about X?' | $0 1a07fabc123" >&2
    echo "  $0 1a07fabc123 42   # explicit exchange number" >&2
    exit 1
fi

TRACE_ID="$1"
EXCHANGE_NUM="${2:-}"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}
cd "$REPO_ROOT"

# Find the current session's transcript file.
# Strategy: most recently modified .md file under chat_history/<model>/
# (excluding README.md and INDEX.md).
TRANSCRIPT=$(find chat_history -type f -name "*.md" \
    -not -name "README.md" \
    -not -name "INDEX.md" \
    -printf '%T@ %p\n' 2>/dev/null \
    | sort -rn | head -1 | awk '{print $2}')

# Fallback for BSD find (no -printf)
if [ -z "$TRANSCRIPT" ]; then
    TRANSCRIPT=$(ls -t $(find chat_history -type f -name "*.md" \
        -not -name "README.md" \
        -not -name "INDEX.md" 2>/dev/null) 2>/dev/null | head -1)
fi

if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
    echo "Error: no transcript file found in chat_history/." >&2
    echo "Run ./scripts/new_session.sh first." >&2
    exit 1
fi

# Determine exchange number if not provided.
if [ -z "$EXCHANGE_NUM" ]; then
    # Count existing "#### Exchange" headers and add 1.
    EXISTING=$(grep -c "^#### Exchange " "$TRANSCRIPT" 2>/dev/null || echo 0)
    EXCHANGE_NUM=$((EXISTING + 1))
fi

# Read user message from stdin if available.
USER_MSG=""
if [ ! -t 0 ]; then
    USER_MSG=$(cat)
fi

if [ -z "$USER_MSG" ]; then
    USER_MSG="(see chat log)"
fi

# Indent user message as a blockquote (prefix each line with "> ").
INDENTED_USER_MSG=$(echo "$USER_MSG" | sed 's/^/> /')

# Append the exchange entry.
cat >> "$TRANSCRIPT" <<EOF

#### Exchange $EXCHANGE_NUM — trace $TRACE_ID

**User:**

$INDENTED_USER_MSG

**Assistant:**

> (in progress...)
EOF

echo "Appended exchange $EXCHANGE_NUM (trace $TRACE_ID) to:"
echo "  $TRANSCRIPT"
echo ""
echo "Replace '(in progress...)' with the actual reply when done."
