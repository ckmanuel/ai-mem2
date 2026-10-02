#!/usr/bin/env python3
"""Pre-commit hook: block commits that change memory files without a transcript.

Memory files change because of conversation. If one is staged and no
transcript under chat_history/<model>/ is staged with it, the exchange that
caused the change may be unrecorded, so the commit is blocked.

Docs, scripts, and workflows are not memory files and are not checked.
Bypass with `git commit --no-verify` for conversation-independent commits.
"""
import subprocess
import sys

MEMORY_FILES = {
    "preferences.md",
    "knowledge.md",
    "decisions.md",
    "context.md",
    "projects.md",
    "lessons.md",
}


def staged_files():
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    return [line for line in out.splitlines() if line]


def is_transcript(path):
    parts = path.split("/")
    return (
        parts[0] == "chat_history"
        and len(parts) >= 3
        and parts[-1] not in ("README.md", "INDEX.md")
    )


def main():
    files = staged_files()
    changed = [f for f in files if f in MEMORY_FILES]
    if changed and not any(is_transcript(f) for f in files):
        print("PRE-COMMIT: memory files changed but no transcript is staged:", file=sys.stderr)
        for f in changed:
            print(f"  {f}", file=sys.stderr)
        print("\nLog the exchange with ./scripts/begin_exchange.sh <trace_id>,", file=sys.stderr)
        print("stage the transcript, and retry. If this commit has nothing to", file=sys.stderr)
        print("do with a conversation, bypass with: git commit --no-verify", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
