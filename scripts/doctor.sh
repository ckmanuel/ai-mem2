#!/bin/sh
# Health check. The verdict is the exit code, not anyone's say-so.
#
# Usage: ./scripts/doctor.sh
# Exit 1 if any FAIL, else 0. WARN lines are advice and never fail the run.
# Run it at session start and again before the final push.

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "FAIL: not inside a git repository."; exit 1; }

FAILS=0
ok()   { echo "OK:   $1"; }
warn() { echo "WARN: $1"; }
fail() { echo "FAIL: $1"; FAILS=$((FAILS + 1)); }

# 1. A token must never be stored in git config or the remote URL.
if grep -qE 'github_pat_|ghp_|gho_|ghs_|ghu_' .git/config 2>/dev/null; then
    fail ".git/config contains a token. Remove it, revoke the token, and use a one-shot credential helper."
elif git remote -v 2>/dev/null | grep -qE '://[^/@ ]+:[^/@ ]+@|://[^/@ ]{20,}@'; then
    fail "a remote URL embeds credentials. Reset it: git remote set-url origin <plain https URL>."
else
    ok "no credentials stored in git config or remote URLs."
fi

# 2. Tracked files must scan clean.
if out=$(python3 scripts/scan_repo.py 2>&1); then
    ok "secret scan clean."
else
    fail "secret scan found possible secrets:"; echo "$out" | sed 's/^/        /'
fi

# 3. The local pre-commit hook should be installed (it is not versioned).
if [ -x .git/hooks/pre-commit ] && grep -q pre_commit_scan .git/hooks/pre-commit 2>/dev/null; then
    ok "pre-commit secret hook installed."
else
    warn "pre-commit hook missing. Run ./scripts/install_hooks.sh."
fi

# 4. Unsaved or unpushed work.
if [ -n "$(git status --porcelain)" ]; then
    warn "uncommitted changes in the working tree."
else
    ok "working tree clean."
fi
if up=$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null); then
    n=$(git rev-list --count "$up..HEAD")
    [ "$n" -eq 0 ] && ok "nothing unpushed." || warn "$n commit(s) not pushed to $up."
else
    warn "no upstream branch set, so unpushed work can't be checked."
fi

# 5. Today's transcript.
today=$(date +%F)
if ls chat_history/*/*"$today"*.md >/dev/null 2>&1; then
    ok "transcript exists for $today."
else
    warn "no transcript for $today. Run ./scripts/new_session.sh."
fi

# 6. Memory file sizes (same limits as CI).
for spec in decisions.md:25600 context.md:15360 preferences.md:12800 knowledge.md:12800 lessons.md:25600; do
    f=${spec%%:*}; max=${spec##*:}
    [ -f "$f" ] || continue
    b=$(wc -c < "$f")
    [ "$b" -gt "$max" ] && warn "$f is $b bytes (limit $max)."
done

echo ""
if [ "$FAILS" -gt 0 ]; then echo "doctor: $FAILS FAIL. Fix before pushing."; exit 1; fi
echo "doctor: no failures."
