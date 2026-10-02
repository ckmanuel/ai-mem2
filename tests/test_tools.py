#!/usr/bin/env python3
"""Tests for redact(), scripts/paste_pack.sh and scripts/doctor.sh.
Run: python3 tests/test_tools.py"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import pre_commit_scan as scanner  # noqa: E402


def make_repo(files, with_scripts=False):
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", d], check=True)
    subprocess.run(["git", "-C", d, "config", "user.email", "a@b"], check=True)
    subprocess.run(["git", "-C", d, "config", "user.name", "t"], check=True)
    for rel, text in files.items():
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    if with_scripts:
        shutil.copytree(ROOT / "scripts", Path(d, "scripts"))
    return d


def sh(repo, script, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(["sh", str(ROOT / "scripts" / script)], cwd=repo,
                          env=e, capture_output=True, text=True)


# --- redact ---

def test_redact_never_shows_a_usable_prefix():
    secret = "github_pat_" + "A1b2C3d4E5" * 8
    out = scanner.redact(secret)
    assert secret[:8] not in out and out.startswith("gith"), out
    assert f"{len(secret)} chars" in out


# --- paste_pack ---

def test_pack_strips_template_comments_and_keeps_content():
    r = make_repo({"preferences.md": "# Prefs\nbe brief\n",
                   "lessons.md": "# Lessons\n<!--\nTEMPLATE\n-->\n## Real lesson\n"})
    out = sh(r, "paste_pack.sh").stdout
    assert "be brief" in out and "Real lesson" in out and "TEMPLATE" not in out, out


def test_pack_cap_drops_from_the_end_and_names_it():
    r = make_repo({"preferences.md": "# Prefs\n" + "x" * 300 + "\n",
                   "knowledge.md": "# Knowledge\n" + "y" * 300 + "\n"})
    out = sh(r, "paste_pack.sh", {"MEM_PACK_LIMIT": "400"}).stdout
    assert "xxx" in out and "yyy" not in out, out
    assert "Omitted" in out and "Knowledge" in out, out


def test_pack_bad_limit():
    r = make_repo({"preferences.md": "x\n"})
    assert sh(r, "paste_pack.sh", {"MEM_PACK_LIMIT": "abc"}).returncode == 2


# --- doctor ---

def test_doctor_clean_repo_passes():
    r = make_repo({"README.md": "hello\n"}, with_scripts=True)
    subprocess.run(["git", "-C", r, "add", "-A"], check=True)
    subprocess.run(["git", "-C", r, "commit", "-qm", "init"], check=True)
    out = sh(r, "doctor.sh")
    assert out.returncode == 0 and "no failures" in out.stdout, out.stdout


def test_doctor_fails_on_token_in_git_config():
    r = make_repo({"README.md": "hello\n"}, with_scripts=True)
    with open(Path(r, ".git", "config"), "a") as f:
        f.write('[remote "origin"]\n\turl = https://github.com/x/y.git\n'
                "\t# github_pat_" + "Z9y8X7w6V5" * 6 + "\n")
    out = sh(r, "doctor.sh")
    assert out.returncode == 1 and "FAIL" in out.stdout, out.stdout


def test_doctor_fails_on_credentialed_remote_url():
    r = make_repo({"README.md": "hello\n"}, with_scripts=True)
    subprocess.run(["git", "-C", r, "remote", "add", "origin",
                    "https://user:secretvalue@github.com/x/y.git"], check=True)
    out = sh(r, "doctor.sh")
    assert out.returncode == 1 and "embeds credentials" in out.stdout, out.stdout


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
