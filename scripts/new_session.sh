#!/bin/sh
# Create a new chat history transcript file for the current session.
#
# Usage:
#   ./scripts/new_session.sh <session_id> <YYYY-MM-DD> [model]
#
# Example:
#   ./scripts/new_session.sh web-abc123-def456 2026-09-09 GLM
#
# If model is omitted, defaults to GLM (the current primary model).
#
# This script is meant to be run as the FIRST action at the start of
# a new session, per context.md's "FIRST ACTION AT SESSION START" block.
# It creates an empty transcript file with the correct header so the
# assistant can append exchanges as the session progresses.

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <session_id> <YYYY-MM-DD> [model]" >&2
    echo "" >&2
    echo "Example:" >&2
    echo "  $0 web-abc123-def456 2026-09-09 GLM" >&2
    exit 1
fi

SESSION_ID="$1"
DATE="$2"
MODEL="${3:-GLM}"

# Resolve repo root regardless of where this is invoked from.
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}

# Map model name to channel. Extend as new models enter use.
case "$MODEL" in
    GLM)
        CHANNEL="zai-web"
        MODEL_FULL="GLM (chat.z.ai)"
        ;;
    Claude)
        CHANNEL="claude.ai"
        MODEL_FULL="Claude (Anthropic)"
        ;;
    ChatGPT)
        CHANNEL="chat.openai.com"
        MODEL_FULL="ChatGPT (OpenAI)"
        ;;
    *)
        CHANNEL="unknown"
        MODEL_FULL="$MODEL"
        ;;
esac

MODEL_DIR="$REPO_ROOT/chat_history/$MODEL"
FILENAME="$SESSION_ID-$DATE.md"
FILEPATH="$MODEL_DIR/$FILENAME"

if [ -f "$FILEPATH" ]; then
    echo "Transcript file already exists: $FILEPATH" >&2
    echo "Appending to existing file. If this is a new session, check the session_id." >&2
    exit 0
fi

mkdir -p "$MODEL_DIR"

cat > "$FILEPATH" <<EOF
# Session: $SESSION_ID - $DATE

**Model:** $MODEL_FULL
**Channel:** $CHANNEL
**Started:** $DATE

Verbatim transcript of user-visible messages. Tool calls and tool output
omitted. PAT and other secrets redacted before writing (the "never commit
token" rule overrides "verbatim").

---

EOF

echo "Created: $FILEPATH"
echo ""
echo "Next: append exchanges to this file as the session progresses."
echo "Convention: #### Exchange N - trace <trace_id>"
