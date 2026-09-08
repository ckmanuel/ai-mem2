#!/bin/sh
# Create a new chat history transcript file for the current session.
#
# Usage:
#   ./scripts/new_session.sh [session_id] [YYYY-MM-DD] [model]
#
# All arguments are optional. If omitted:
#   - session_id: auto-generated as 'auto-<unix_timestamp>-<random6>'
#   - date: today's date (system local time)
#   - model: GLM (the current primary model)
#
# Examples:
#   # IM gateway metadata available (chat.z.ai):
#   ./scripts/new_session.sh web-abc123-def456 2026-09-09 GLM
#
#   # No IM gateway (Claude.ai, ChatGPT, etc.) — let it auto-generate:
#   ./scripts/new_session.sh
#   ./scripts/new_session.sh "" 2026-09-09 Claude
#
# This script is meant to be run as the FIRST action at the start of
# a new session, per context.md's "FIRST ACTION AT SESSION START" block.
# It creates an empty transcript file with the correct header so the
# assistant can append exchanges as the session progresses.

set -e

# Generate today's date if not provided.
if [ -z "$2" ]; then
    DATE=$(date +%Y-%m-%d)
else
    DATE="$2"
fi

# Generate session_id if not provided. Uses unix timestamp + 6 random
# alphanumeric chars to reduce collision risk across sessions on the
# same day.
if [ -z "$1" ]; then
    TS=$(date +%s)
    RAND=$(head -c 3 /dev/urandom | od -An -tx1 | tr -d ' \n')
    SESSION_ID="auto-${TS}-${RAND}"
else
    SESSION_ID="$1"
fi

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
