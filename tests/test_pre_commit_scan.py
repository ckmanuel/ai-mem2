#!/usr/bin/env python3
"""Tests for scripts/pre_commit_scan.py.

Run with pytest:
  python3 -m pytest tests/ -v

Or standalone:
  python3 tests/test_pre_commit_scan.py

The scanner is security-critical — if a future PR "improves" the regex
and breaks detection, you'll find out from a leaked PAT, not from CI.
These tests catch that regression before it ships.

Test structure:
  - test_each_prefix_pattern_matches: each known token shape is caught
  - test_fixture_should_match: every line in should_match.txt is caught
  - test_fixture_should_not_match: no line in should_not_match.txt is caught
  - test_shannon_entropy: known strings return expected entropy values
  - test_is_false_positive_md5: md5 hashes don't get flagged
  - test_is_false_positive_sha1: sha1 hashes don't get flagged
  - test_is_false_positive_sha256: sha256 hashes don't get flagged
  - test_is_false_positive_uuid: UUIDs don't get flagged
  - test_is_false_positive_url: URLs don't get flagged
  - test_is_false_positive_path: filesystem paths don't get flagged
  - test_is_false_positive_version: version strings don't get flagged
"""
import math
import sys
from pathlib import Path

# Add scripts/ to path so we can import pre_commit_scan.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pre_commit_scan as scanner  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


# === Helper ===

def scan_line(line):
    """Return list of hits for a single line of text."""
    hits = []
    # Check prefix patterns
    for pat, desc in scanner.PREFIX_PATTERNS:
        for m in pat.finditer(line):
            hits.append((desc, m.group(0)))
    # Check high-entropy
    for m in scanner.HIGH_ENTROPY_RE.finditer(line):
        candidate = m.group(0)
        if len(candidate) < scanner.MIN_LEN:
            continue
        if scanner.is_false_positive(candidate):
            continue
        ent = scanner.shannon_entropy(candidate)
        if ent >= scanner.ENTROPY_THRESHOLD:
            hits.append((f"entropy={ent:.2f}", candidate))
    return hits


# === Pattern tests ===

def test_each_prefix_pattern_matches():
    """Each prefix pattern in PREFIX_PATTERNS should match at least one
    line in should_match.txt."""
    should_match = (FIXTURES_DIR / "should_match.txt").read_text()
    for pat, desc in scanner.PREFIX_PATTERNS:
        # Skip the password=/api_key=/token= patterns since they need quoted values
        if "assignment" in desc:
            continue
        assert pat.search(should_match), (
            f"Pattern for '{desc}' didn't match any line in should_match.txt"
        )


def test_fixture_should_match():
    """Every line in should_match.txt should produce at least one hit."""
    fixtures = (FIXTURES_DIR / "should_match.txt").read_text().splitlines()
    failures = []
    for i, line in enumerate(fixtures, 1):
        if not line.strip() or line.startswith("#"):
            continue
        hits = scan_line(line)
        assert hits, (
            f"Line {i} of should_match.txt was NOT caught by scanner:\n  {line}"
        )


def test_fixture_should_not_match():
    """No line in should_not_match.txt should produce any hits."""
    fixtures = (FIXTURES_DIR / "should_not_match.txt").read_text().splitlines()
    failures = []
    for i, line in enumerate(fixtures, 1):
        if not line.strip() or line.startswith("#"):
            continue
        hits = scan_line(line)
        assert not hits, (
            f"Line {i} of should_not_match.txt was flagged as a secret:\n"
            f"  line: {line}\n"
            f"  hits: {hits}"
        )


# === Shannon entropy tests ===

def test_shannon_entropy_empty():
    assert scanner.shannon_entropy("") == 0.0


def test_shannon_entropy_single_char():
    # All same char → entropy is 0
    assert scanner.shannon_entropy("aaaa") == 0.0


def test_shannon_entropy_uniform_distribution():
    # Each char appears once → entropy is log2(N) where N is string length
    s = "abcd"  # 4 distinct chars, each once
    expected = math.log2(4)
    assert abs(scanner.shannon_entropy(s) - expected) < 0.001


def test_shannon_entropy_english_text_low():
    # English text should have relatively low entropy.
    # Typical English prose: 3.5-4.5 bits/char. Random base64: ~6.0.
    # We assert it stays below the threshold we'd consider "secret-like".
    s = "The quick brown fox jumps over the lazy dog"
    ent = scanner.shannon_entropy(s)
    assert ent < 4.5, f"English text entropy {ent:.2f} should be < 4.5"


def test_shannon_entropy_random_high():
    # Random base64-like string should have high entropy (~5.0+)
    s = "xJ8k2pQ9vN4mZ7tR3wY6bV1cE0fG5hJ9kL2sM3nT8qW4xZ7yB0"
    ent = scanner.shannon_entropy(s)
    assert ent >= 4.5, f"Random string entropy {ent:.2f} should be >= 4.5"


# === False positive tests ===

def test_is_false_positive_md5():
    assert scanner.is_false_positive("5d41402abc4b2a76b9719d911017c592")


def test_is_false_positive_sha1():
    assert scanner.is_false_positive("da39a3ee5e6b4b0d3255bfef95601890afd80709")


def test_is_false_positive_sha256():
    s = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert scanner.is_false_positive(s)


def test_is_false_positive_uuid():
    assert scanner.is_false_positive("550e8400-e29b-41d4-a716-446655440000")


def test_is_false_positive_url():
    assert scanner.is_false_positive("https://github.com/ckmanuel/ai-memory.git")


def test_is_false_positive_path():
    assert scanner.is_false_positive("/home/z/my-project/scripts/redact_token.py")
    assert scanner.is_false_positive("chat_history/GLM/web-dbcfad74-2026-09-08.md")


def test_is_false_positive_version():
    assert scanner.is_false_positive("v1.2.3")


def test_is_false_positive_random_token_not_filtered():
    """A real-looking random token should NOT be filtered as false positive."""
    s = "xJ8k2pQ9vN4mZ7tR3wY6bV1cE0fG5hJ9kL2sM3nT8qW4xZ7yB0"
    assert not scanner.is_false_positive(s)


# === Standalone runner ===

if __name__ == "__main__":
    # Run all test_ functions and report pass/fail counts.
    tests = [name for name in dir(sys.modules[__name__])
             if name.startswith("test_")]
    passed = 0
    failed = 0
    for test_name in tests:
        test_fn = getattr(sys.modules[__name__], test_name)
        try:
            test_fn()
            print(f"  PASS  {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test_name}")
            print(f"        {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test_name}")
            print(f"        {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed.")
    sys.exit(0 if failed == 0 else 1)
