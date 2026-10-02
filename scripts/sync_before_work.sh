#!/bin/sh
# Pull the latest origin/main and show what changed.
#
# Run before editing memory files if the session has been idle or another
# session may have committed. Without it you commit on stale state and the
# push gets rejected, or you contradict a decision you never saw.
#
# Usage: GH_PAT=<token> ./scripts/sync_before_work.sh
# The token is passed through a one-shot credential helper and never
# written to .git/config.

set -e

[ -n "$GH_PAT" ] || { echo "Error: GH_PAT is not set." >&2; exit 1; }

cd "$(git rev-parse --show-toplevel)" || exit 1
git remote get-url origin >/dev/null 2>&1 || { echo "Error: no 'origin' remote." >&2; exit 1; }

git_auth() {
    git -c credential.helper='!f() { echo username=x-access-token; echo "password=$GH_PAT"; }; f' "$@"
}

OLD=$(git rev-parse HEAD)

git_auth fetch origin main || {
    echo "Error: fetch failed. Check that GH_PAT is valid and has Contents read/write on this repo." >&2
    exit 1
}

AHEAD=$(git rev-list --count origin/main..HEAD)
BEHIND=$(git rev-list --count HEAD..origin/main)

[ "$AHEAD" -gt 0 ] && echo "Note: $AHEAD unpushed local commit(s)."
if [ "$BEHIND" -eq 0 ]; then
    echo "Up to date with origin/main."
    exit 0
fi

git_auth pull --rebase origin main || {
    echo "Error: rebase failed. Resolve conflicts, or run: git rebase --abort" >&2
    exit 1
}

NEW=$(git rev-parse HEAD)
echo ""
echo "Integrated $BEHIND new commit(s):"
git log --oneline --no-decorate "$OLD..$NEW"
echo ""
echo "Files changed:"
git diff --name-only "$OLD..$NEW" | sort -u | sed 's/^/  /'
echo ""
echo "Re-read any memory file listed above before you edit it."
