#!/usr/bin/env python3
"""Scan all tracked files in the repo for secrets.

Used by GitHub Actions CI (secret-scan.yml) as a defense-in-depth check
after pushes. Different threat model from pre_commit_scan.py:
- pre_commit_scan.py: local, pre-commit, scans staged content only.
  Protects against leaks before they reach the remote.
- scan_repo.py: CI, post-push, scans all tracked files. Catches leaks
  that slipped past the local hook (e.g., fresh clones without the
  hook installed, or `git commit --no-verify` bypasses).

If this check fails on a push, the commit is already in remote history.
Rotation of any leaked secret is the only remedy. The CI check at least
makes the leak visible rather than silent.
"""
import math
import os
import re
import subprocess
import sys

# Reuse patterns from pre_commit_scan.py to keep detection logic in sync.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pre_commit_scan import (
    PREFIX_PATTERNS,
    HIGH_ENTROPY_RE,
    MIN_LEN,
    ENTROPY_THRESHOLD,
    FALSE_POSITIVES,
    PATH_LIKE_RE,
    shannon_entropy,
    is_false_positive,
)


def scan_text(text):
    """Yield (description, line_number, matched_text) for hits in text."""
    for line_no, line in enumerate(text.splitlines(), start=1):
        for pat, desc in PREFIX_PATTERNS:
            for m in pat.finditer(line):
                yield (desc, line_no, m.group(0))
        for m in HIGH_ENTROPY_RE.finditer(line):
            candidate = m.group(0)
            if len(candidate) < MIN_LEN:
                continue
            if is_false_positive(candidate):
                continue
            ent = shannon_entropy(candidate)
            if ent >= ENTROPY_THRESHOLD:
                yield (
                    f"High-entropy string (entropy={ent:.2f})",
                    line_no,
                    candidate,
                )


def get_tracked_files():
    """Return list of (path, content) for all tracked files in the repo."""
    try:
        out = subprocess.check_output(
            ["git", "ls-files"], text=True
        )
    except subprocess.CalledProcessError:
        return []
    files = []
    for path in out.splitlines():
        if not path:
            continue
        # Skip the scanner scripts themselves (they contain patterns that
        # describe secrets, not actual secrets).
        if path in ("scripts/pre_commit_scan.py", "scripts/scan_repo.py"):
            continue
        try:
            with open(path, "rb") as f:
                chunk = f.read(1024)
            if b"\x00" in chunk:
                continue  # binary
        except (IOError, OSError):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            files.append((path, content))
        except (IOError, OSError):
            continue
    return files


def main():
    files = get_tracked_files()
    if not files:
        print("No tracked files to scan.")
        return 0

    hits = []
    for path, content in files:
        for desc, line_no, matched in scan_text(content):
            hits.append((path, desc, line_no, matched))

    if not hits:
        print(f"CI scan: clean. Scanned {len(files)} tracked files. No secrets detected.")
        return 0

    print("=" * 60)
    print("CI SCAN: possible secrets detected in tracked files:")
    print("=" * 60)
    for path, desc, line_no, matched in hits:
        preview = matched[:24] + "..." if len(matched) > 24 else matched
        print(f"  {path}:{line_no}  {desc}  matched: {preview}")
    print("")
    print("The commit is already in remote history. Rotate any real secrets immediately.")
    print("To suppress false positives, extend FALSE_POSITIVES in scripts/pre_commit_scan.py.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
