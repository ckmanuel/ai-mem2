#!/bin/sh
# Pull latest from origin/main and summarize what changed.
#
# Run this BEFORE making any memory file edits if your session has been
# idle or if another session may have committed since you last pulled.
#
# Why: in alternating-session setups, Session A pushes commits while
# Session B is idle. When B becomes active, B's local clone is behind.
# Without a pull, B will commit on stale state and the next push gets
# rejected. Even worse: B might miss decisions A made and produce
# contradictory work.
#
# Usage:
#   GH_PAT=<your_pat> ./scripts/sync_before_work.sh
#
# Or if GH_PAT is already exported in your shell:
#   ./scripts/sync_before_work.sh
#
# Behavior:
#   - Fetches latest from origin/main (using $GH_PAT for auth).
#   - If local is up-to-date: prints "Up to date." and exits 0.
#   - If local is behind: pulls (rebase), prints list of files changed
#     since local HEAD, prints commit subjects of new commits. Exits 0.
#   - If local is ahead: prints warning, does NOT push. Exits 0.
#   - If auth fails: prints clear error, exits 1.
#   - If merge conflict during rebase: prints error, exits 1. Resolve
#     manually with `git rebase --abort` or `git rebase --continue`.

set -e

# Check for GH_PAT.
if [ -z "$GH_PAT" ]; then
    echo "Error: GH_PAT env var not set." >&2
    echo "Set it with: export GH_PAT=<your_pat>" >&2
    echo "Or inline:  GH_PAT=<your_pat> $0" >&2
    exit 1
fi

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}
cd "$REPO_ROOT"

# Make sure origin is set.
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "Error: no 'origin' remote configured." >&2
    exit 1
fi

# Helper: run a git command with the PAT as a one-shot credential helper.
git_auth() {
    git -c credential.helper="!f() { echo \"username=ckmanuel\"; echo \"password=\${GH_PAT}\"; }; f" "$@"
}

# Capture local HEAD before pull.
LOCAL_HEAD=$(git rev-parse HEAD)

# Fetch latest.
echo "Fetching origin..."
if ! git_auth fetch origin main 2>&1 | sed 's/^/  /'; then
    echo ""
    echo "ERROR: fetch failed. Likely auth issue." >&2
    echo "Verify GH_PAT is valid and has 'Contents: Read and write' scope" >&2
    echo "on ckmanuel/ai-memory." >&2
    exit 1
fi

# Compare local to remote.
REMOTE_HEAD=$(git rev-parse origin/main)

if [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
    echo ""
    echo "Up to date. Local HEAD matches origin/main ($LOCAL_HEAD)."
    exit 0
fi

# Check if local is ahead, behind, or diverged.
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)

if [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -eq 0 ]; then
    echo ""
    echo "WARNING: Local is $AHEAD commit(s) ahead of origin/main."
    echo "You have unpushed commits. Push them first with:"
    echo "  GH_PAT=\$GH_PAT git -c credential.helper=\"!f() { echo \\\"username=ckmanuel\\\"; echo \\\"password=\\\$GH_PAT\\\"; }; f\" push origin main"
    echo ""
    echo "Or, if you want to see what's ahead:"
    echo "  git log origin/main..HEAD --oneline"
    exit 0
fi

if [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -gt 0 ]; then
    echo ""
    echo "WARNING: Local and origin have diverged."
    echo "  Local ahead by: $AHEAD commit(s)"
    echo "  Local behind by: $BEHIND commit(s)"
    echo ""
    echo "Pull --rebase will replay your local commits on top of remote."
    echo "If conflicts occur, abort with: git rebase --abort"
    echo ""
fi

# Behind only, or diverged — pull with rebase.
echo "Pulling latest (rebase)..."
if ! git_auth pull --rebase origin main 2>&1; then
    echo ""
    echo "ERROR: rebase failed. Likely merge conflict." >&2
    echo "Resolve manually:" >&2
    echo "  git status                  # see conflicted files" >&2
    echo "  git rebase --abort          # bail out, return to pre-pull state" >&2
    echo "  git rebase --continue       # after resolving conflicts" >&2
    exit 1
fi

NEW_HEAD=$(git rev-parse HEAD)

if [ "$NEW_HEAD" = "$LOCAL_HEAD" ]; then
    echo "Rebase complete. No new commits to integrate."
    exit 0
fi

echo ""
echo "Rebase complete. New commits integrated since $LOCAL_HEAD:"
echo ""
git log --oneline --no-decorate ${LOCAL_HEAD}..${NEW_HEAD}

echo ""
echo "Files changed in those commits:"
echo ""
git diff --name-only ${LOCAL_HEAD}..${NEW_HEAD} | sort -u | sed 's/^/  /'

echo ""
echo "ACTION REQUIRED: if any of these are memory files you're about to"
echo "edit (context.md, decisions.md, preferences.md, knowledge.md,"
echo "README.md), re-read them before making your own edits. Otherwise"
echo "you risk working on stale state."
