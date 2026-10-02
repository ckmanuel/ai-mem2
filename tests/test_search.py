#!/usr/bin/env python3
"""Tests for scripts/search.sh. Run: python3 tests/test_search.py"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "search.sh"


def make_repo(files):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", d], check=True)
    for rel, text in files.items():
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


def run(repo, term, limit=None):
    env = dict(os.environ)
    if limit is not None:
        env["MEM_SEARCH_LIMIT"] = str(limit)
    return subprocess.run(["sh", str(SCRIPT), term], cwd=repo, env=env,
                          capture_output=True, text=True)


def test_case_insensitive_literal():
    r = make_repo({"knowledge.md": "Uses PostgreSQL for storage.\n"})
    out = run(r, "postgresql")
    assert out.returncode == 0 and "knowledge.md:1" in out.stdout


def test_regex_chars_are_literal():
    r = make_repo({"knowledge.md": "file is a.b(c) here\nunrelated axb line\n"})
    out = run(r, "a.b(c)")
    assert out.returncode == 0 and "1 match(es)" in out.stdout


def test_zero_is_explicit_and_exits_1():
    r = make_repo({"knowledge.md": "nothing relevant\n"})
    out = run(r, "zzzz")
    assert out.returncode == 1 and "0 matches" in out.stdout


def test_lessons_rank_first():
    r = make_repo({"knowledge.md": "token rotation note\n",
                   "lessons.md": "token rotation lesson\n",
                   "chat_history/Claude/s-1.md": "token rotation chat\n"})
    lines = [l for l in run(r, "rotation").stdout.splitlines() if ":" in l and not l.startswith("--")]
    assert lines[0].startswith("lessons.md"), lines


def test_cap_reports_hidden_and_spreads_across_files():
    files = {f"chat_history/Claude/s-{i}.md": "needle\n" * 5 for i in range(4)}
    out = run(make_repo(files), "needle", limit=4).stdout
    shown = [l for l in out.splitlines() if l.startswith("chat_history/")]
    assert len(shown) == 4 and len({l.split(":")[0] for l in shown}) == 4, out
    assert "16 hidden" in out, out


def test_skips_archive_tests_and_git():
    r = make_repo({"archive/old.md": "needle\n", "tests/x.md": "needle\n"})
    assert run(r, "needle").returncode == 1


def test_bad_usage():
    r = make_repo({"knowledge.md": "x\n"})
    assert subprocess.run(["sh", str(SCRIPT)], cwd=r, capture_output=True).returncode == 2
    assert run(r, "x", limit="abc").returncode == 2


if __name__ == "__main__":
    passed = failed = 0
    for name in [n for n in dir(sys.modules[__name__]) if n.startswith("test_")]:
        try:
            getattr(sys.modules[__name__], name)()
            print(f"  PASS  {name}"); passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}\n        {e}"); failed += 1
    print(f"\n{passed} passed, {failed} failed.")
    sys.exit(0 if failed == 0 else 1)
