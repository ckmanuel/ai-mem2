#!/usr/bin/env python3
"""Pre-commit hook: scan staged content for secrets.

Catches:
- Known token prefixes: github_pat_, ghp_, gho_, ghs_, ghu_, sk-,
  AKIA (AWS access key), AWS IAM id prefixes, xox[abp]- (Slack),
  glpat- (GitLab), private key blocks, JWTs, password=/api_key=/token=
  assignments.
- High-entropy strings of length >= 32 (Shannon entropy >= 4.0),
  excluding common false positives (md5/sha1/sha256 hashes, uuids,
  version strings, urls).

Exits 1 (block commit) if any secret is found. Prints what was caught
and the file/line. Exits 0 otherwise.

Bypass with `git commit --no-verify` for confirmed false positives.
"""
import math
import re
import subprocess
import sys

# --- Known token prefix patterns ---------------------------------------------
PREFIX_PATTERNS = [
    (re.compile(r"github_pat_[A-Za-z0-9_]{36,}"), "GitHub fine-grained PAT"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub classic PAT"),
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"), "Anthropic Claude key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI / generic API key"),
    (re.compile(r"gla_[A-Za-z0-9]{20,}"), "Google API key (legacy)"),
    (re.compile(r"AIza[A-Za-z0-9_\-]{35}"), "Google API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"\b(AGPA|AIDA|AROA|ANPA|AIPA|ASIA)[0-9A-Z]{16,}"),
     "AWS IAM role/policy id"),
    (re.compile(r"xox[abp]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"glpat-[A-Za-z0-9_\-]{20,}"), "GitLab PAT"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "Private key block"),
    (re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
     "JWT"),
    (re.compile(r"password\s*[=:]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE),
     "password = \"...\" assignment"),
    (re.compile(r"api[_-]?key\s*[=:]\s*['\"][^'\"]{16,}['\"]", re.IGNORECASE),
     "api_key = \"...\" assignment"),
    (re.compile(r"token\s*[=:]\s*['\"][^'\"]{16,}['\"]", re.IGNORECASE),
     "token = \"...\" assignment"),
]

# --- High-entropy string detection -----------------------------------------
HIGH_ENTROPY_RE = re.compile(r"[A-Za-z0-9+/=_\-]{32,}")
MIN_LEN = 32
# 4.5 bits/char: random base64 ~6.0, JWT body ~5.5, GitHub PAT prefix
# portion ~5.0, English text ~3.0, paths and config values ~3.5-4.0.
# 4.0 was too aggressive (caught paths); 4.5 still catches unknown
# random tokens while letting paths and English-ish strings through.
ENTROPY_THRESHOLD = 4.5

# False positives to skip (matched against the candidate string).
FALSE_POSITIVES = [
    re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE),  # md5
    re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE),  # sha1 / git sha
    re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE),  # sha256
    re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
               re.IGNORECASE),  # uuid
    re.compile(r"^sha[0-9]+-", re.IGNORECASE),
    re.compile(r"^[A-F0-9]{40,}$"),  # hex-only long strings
    re.compile(r"^v\d+\.\d+\.\d+"),  # version strings
    re.compile(r"^https?://"),  # urls
]

# Path-like strings: contain at least one `/` separator. Real secrets
# almost never contain `/` (PEM keys, JWTs, and known-token-prefix
# patterns are matched separately by PREFIX_PATTERNS). If a high-
# entropy candidate contains `/`, it's almost certainly a path or URL.
PATH_LIKE_RE = re.compile(r"^[A-Za-z0-9._\-]+/[A-Za-z0-9._\-/]*")


def shannon_entropy(s):
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def is_false_positive(s):
    for pat in FALSE_POSITIVES:
        if pat.match(s):
            return True
    # Path-like strings (checked separately because the candidate may
    # be a prefix of a longer path that ended at a non-charset char).
    if PATH_LIKE_RE.match(s):
        return True
    return False


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


def get_staged_files():
    """Return list of (path, content) for staged files (added or modified)."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    files = []
    for path in out.splitlines():
        if not path:
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
    files = get_staged_files()
    if not files:
        return 0

    hits = []
    for path, content in files:
        for desc, line_no, matched in scan_text(content):
            hits.append((path, desc, line_no, matched))

    if not hits:
        return 0

    print("=" * 60, file=sys.stderr)
    print("PRE-COMMIT: blocked commit, possible secrets detected:", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    for path, desc, line_no, matched in hits:
        preview = matched[:24] + "..." if len(matched) > 24 else matched
        print(f"  {path}:{line_no}  {desc}  matched: {preview}", file=sys.stderr)
    print("", file=sys.stderr)
    print("If real secret: remove it, rotate it, re-commit.", file=sys.stderr)
    print("If false positive: git commit --no-verify to bypass.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
