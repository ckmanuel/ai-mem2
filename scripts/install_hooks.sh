#!/bin/sh
# Install the pre-commit hook for this clone.
# Run once after cloning. Safe to re-run.
#
# Usage:
#   ./scripts/install_hooks.sh
#
# This installs a pre-commit shim that calls two scanners in sequence:
#   1. scripts/pre_commit_scan.py        — secret scanner (blocks
#                                          commits with suspected tokens)
#   2. scripts/pre_commit_transcript_check.py — transcript enforcement
#                                          (blocks commits that change
#                                          memory files without updating
#                                          the transcript)

set -e

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}

HOOK="$REPO_ROOT/.git/hooks/pre-commit"

cat > "$HOOK" <<'EOF'
#!/bin/sh
# Pre-commit hook: calls secret scanner, then transcript-enforcement
# scanner. Either can block the commit. Bypass with --no-verify for
# confirmed false positives or conversation-independent commits.

set -e

# 1. Secret scanner — blocks commits containing suspected tokens.
python3 "$(git rev-parse --show-toplevel)/scripts/pre_commit_scan.py" "$@"
SECRET_EXIT=$?
if [ $SECRET_EXIT -ne 0 ]; then
    exit $SECRET_EXIT
fi

# 2. Transcript enforcement — blocks commits that change memory files
#    without also updating the transcript. Bypass with --no-verify
#    for legitimate cases (initial setup, pure script changes).
python3 "$(git rev-parse --show-toplevel)/scripts/pre_commit_transcript_check.py" "$@"
exit $?
EOF

chmod +x "$HOOK"

echo "Pre-commit hook installed at: $HOOK"
echo ""
echo "Calls two scanners in sequence:"
echo "  1. scripts/pre_commit_scan.py        — secret scanner"
echo "  2. scripts/pre_commit_transcript_check.py — transcript enforcement"
echo ""
echo "Bypass with: git commit --no-verify"
echo "  (for confirmed false positives or conversation-independent commits)"
