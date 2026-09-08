#!/usr/bin/env python3
"""Pre-commit hook: enforce transcript updates when memory files change.

If the staged content includes changes to memory files (preferences.md,
knowledge.md, decisions.md, context.md, projects.md, README.md) or
scripts/, but does NOT include any change to chat_history/<model>/*.md,
print a loud warning and exit 1 (block the commit).

Bypass with `git commit --no-verify` for legitimate cases (e.g.,
initial setup, README typo fix, pure script changes with no conversation
context).

This addresses the forcing problem: the assistant can be busy with
implementation work and forget to append the current exchange to the
transcript. Without this check, the exchange is lost. With it, the
commit is blocked until the transcript is updated.
"""
import subprocess
import sys

# Files that, if changed, require a transcript update.
# These are the "memory files" — they change as a result of conversation.
MEMORY_FILES = {
    "preferences.md",
    "knowledge.md",
    "decisions.md",
    "context.md",
    "projects.md",
    "README.md",
    "RETRIEVAL.md",
}

# Directories where changes typically imply conversation context.
MEMORY_DIRS = {
    "scripts/",
    ".github/workflows/",
}


def get_staged_files():
    """Return list of file paths staged for commit (added or modified)."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    return [line for line in out.splitlines() if line]


def is_memory_file(path):
    """Check if a staged file is a memory file or in a memory directory."""
    # Direct match against memory files
    if path in MEMORY_FILES:
        return True
    # In a memory directory
    for prefix in MEMORY_DIRS:
        if path.startswith(prefix):
            return True
    return False


def is_transcript_file(path):
    """Check if a staged file is a transcript under chat_history/<model>/."""
    if not path.startswith("chat_history/"):
        return False
    # Exclude chat_history/README.md and chat_history/INDEX.md
    parts = path.split("/")
    if len(parts) < 3:
        return False  # chat_history/README.md or similar
    if parts[-1] in ("README.md", "INDEX.md"):
        return False
    return True


def main():
    files = get_staged_files()
    if not files:
        return 0

    memory_changed = [f for f in files if is_memory_file(f)]
    transcript_changed = [f for f in files if is_transcript_file(f)]

    if memory_changed and not transcript_changed:
        print("=" * 60, file=sys.stderr)
        print("PRE-COMMIT: memory files changed but no transcript update.", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("", file=sys.stderr)
        print("Changed memory files:", file=sys.stderr)
        for f in memory_changed:
            print(f"  {f}", file=sys.stderr)
        print("", file=sys.stderr)
        print("No file under chat_history/<model>/ was staged.", file=sys.stderr)
        print("", file=sys.stderr)
        print("If you had a conversation that led to these memory changes,", file=sys.stderr)
        print("append the exchange to the transcript first:", file=sys.stderr)
        print("  ./scripts/begin_exchange.sh <trace_id>", file=sys.stderr)
        print("Then add the transcript file and retry the commit.", file=sys.stderr)
        print("", file=sys.stderr)
        print("If this commit is genuinely conversation-independent", file=sys.stderr)
        print("(README typo, script refactor, CI workflow update),", file=sys.stderr)
        print("bypass with: git commit --no-verify", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
