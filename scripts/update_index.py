#!/usr/bin/env python3
"""Generate or update chat_history/INDEX.md.

For each transcript in chat_history/<model>/<session_id>-<date>.md,
extract a one-line summary and write to INDEX.md.

Summary format:
  - YYYY-MM-DD Model session_id: <first user msg> → <last assistant msg>

Both halves truncated to ~80 chars. The first user message says what
the session opened with; the last assistant message usually summarizes
what was accomplished. Together they give a much better signal than
the first user message alone.

Grep INDEX.md to find which session mentioned X, instead of grepping
every transcript. Run after each new session.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHAT_HISTORY = REPO_ROOT / "chat_history"
INDEX_PATH = CHAT_HISTORY / "INDEX.md"

HEADER = """# Chat History Index

One-line summary per session. Grep this file to find sessions instead
of grepping every transcript. Regenerate after new sessions with:

  python scripts/update_index.py

---

"""

FIRST_USER_RE = re.compile(
    r"\*\*User:\*\*\s*\n+>\s*(.+?)(?:\n>|\n\n|\Z)",
    re.DOTALL,
)
LAST_ASSISTANT_RE = re.compile(
    r"\*\*Assistant:\*\*\s*\n+>\s*(.+?)(?:\n>|\n\n|\Z)",
    re.DOTALL,
)
SESSION_HEADER_RE = re.compile(
    r"^# Session:\s*(.+?)\s*-\s*(\d{4}-\d{2}-\d{2})",
    re.MULTILINE,
)
MODEL_RE = re.compile(r"^\*\*Model:\*\*\s*(.+)$", re.MULTILINE)


def truncate(text, limit=80):
    """Collapse whitespace, truncate to limit chars with ellipsis."""
    text = " ".join(text.split())
    if len(text) > limit:
        return text[:limit - 3] + "..."
    return text


def summarize_transcript(path):
    """Extract a one-line summary from a transcript file."""
    try:
        content = path.read_text(encoding="utf-8")
    except (IOError, OSError) as e:
        return None, f"couldn't read: {e}"

    session_match = SESSION_HEADER_RE.search(content)
    if not session_match:
        return None, "no session header"
    session_id = session_match.group(1)
    date = session_match.group(2)

    model_match = MODEL_RE.search(content)
    model = model_match.group(1).strip() if model_match else "unknown"
    model_short = model.split("(")[0].strip()

    # First user message
    user_match = FIRST_USER_RE.search(content)
    if user_match:
        first_user = truncate(user_match.group(1).strip())
    else:
        first_user = "(no user message found)"

    # Last assistant message — find all matches, take the last one
    assistant_matches = list(LAST_ASSISTANT_RE.finditer(content))
    if assistant_matches:
        last_assistant = truncate(assistant_matches[-1].group(1).strip())
    else:
        last_assistant = "(no assistant message found)"

    summary = f"- {date} {model_short} `{session_id}`: {first_user} → {last_assistant}"
    return summary, None


def find_transcripts():
    """Find all transcript files, sorted by date."""
    transcripts = []
    for path in CHAT_HISTORY.rglob("*.md"):
        if path.name in ("README.md", "INDEX.md"):
            continue
        transcripts.append(path)
    return sorted(transcripts, key=lambda p: p.name)


def main():
    transcripts = find_transcripts()
    if not transcripts:
        print("No transcripts found in chat_history/.")
        if INDEX_PATH.exists():
            print(f"Removing stale index: {INDEX_PATH}")
            INDEX_PATH.unlink()
        return 0

    print(f"Found {len(transcripts)} transcript(s).")

    lines = [HEADER]
    skipped = 0
    for path in transcripts:
        rel = path.relative_to(CHAT_HISTORY)
        summary, err = summarize_transcript(path)
        if summary:
            lines.append(summary)
            print(f"  {rel}")
        else:
            print(f"  {rel} -- SKIP ({err})")
            skipped += 1

    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote: {INDEX_PATH}")
    print(f"  {len(lines) - 1} entries, {skipped} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
