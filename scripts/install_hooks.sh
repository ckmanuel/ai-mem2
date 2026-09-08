#!/bin/sh
# Install the pre-commit hook for this clone.
# Run once after cloning. Safe to re-run.
#
# Usage:
#   ./scripts/install_hooks.sh

set -e

# Resolve repo root regardless of where this is invoked from.
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "Error: not inside a git repository." >&2
    exit 1
}

HOOK="$REPO_ROOT/.git/hooks/pre-commit"

cat > "$HOOK" <<'EOF'
#!/bin/sh
exec python3 "$(git rev-parse --show-toplevel)/scripts/pre_commit_scan.py" "$@"
EOF

chmod +x "$HOOK"

echo "Pre-commit hook installed at: $HOOK"
echo "Scanner: $REPO_ROOT/scripts/pre_commit_scan.py"
echo ""
echo "Test it with: python3 $REPO_ROOT/scripts/pre_commit_scan.py"
echo "Bypass with: git commit --no-verify (for confirmed false positives)"
