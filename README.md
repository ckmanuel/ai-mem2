# ai-mem2

Persistent memory for cross-session chat with AI agents. 

## Structure

| File / Dir | Purpose |
|---|---|
| `preferences.md` | User preferences (kept across fork). |
| `knowledge.md` | Facts the user shares. |
| `projects.md` | Active and past projects. |
| `decisions.md` | Durable decisions, append-only. |
| `context.md` | Current focus. Read first. |
| `chat_history/` | Verbatim transcripts, per session per model. |
| `scripts/` | `pre_commit_scan.py`, `scan_repo.py`, `install_hooks.sh`, `new_session.sh`, `sync_before_work.sh`. |
| `.github/workflows/` | `secret-scan.yml`, `transcript-check.yml`, `size-check.yml`. |

## Setup after cloning

```sh
./scripts/install_hooks.sh
```

Installs the pre-commit hook locally. `.git/hooks/` isn't version-
controlled, so this is required on every fresh clone. Until it runs,
local commits won't be scanned for secrets.

## Token rule

Never commit the PAT. The pre-commit hook scans for token prefixes and
high-entropy strings. CI backstop scans again on push. If a token leaks,
rotate it immediately.

Recommended: store the PAT in an env var (`export GH_PAT=...`) and
reference it as `$GH_PAT` in the opening prompt. Chat never sees the
token.
