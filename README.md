# ai-memory

Persistent long-term memory for cross-session chat with Claude / GLM on chat.z.ai.

## Purpose

This repository serves as a persistent memory store across chat sessions. At the
start of every session, the assistant clones this repo, reads the relevant
files, and uses them as context for the conversation. Important information
learned during the session is committed and pushed back so it persists.

## Structure

| File / Dir       | Purpose                                                                |
|------------------|------------------------------------------------------------------------|
| `README.md`      | This file — overview and usage conventions.                            |
| `preferences.md` | User preferences: communication style, tools, formatting, language.     |
| `projects.md`    | Active and past projects, with status and key links.                  |
| `decisions.md`   | Important decisions and their rationale (append-only log).             |
| `context.md`     | Current work-in-progress, open threads, and short-term focus.         |
| `chat_history.md`| Verbatim transcript of chat sessions (model -> session -> exchanges).   |
| `sessions/`      | Per-session summaries (one file per session, append-only).            |
| `scripts/`       | Tooling. Currently: `pre_commit_scan.py` (secret scanner).            |

## Conventions

- **Concise over verbose** — each file should be skimmable in under 2 minutes.
- **Append-only where possible** — `decisions.md` and `sessions/` are append-only.
- **No secrets** — never store API keys, tokens, passwords, or PII here.
- **Update in place for** `preferences.md`, `projects.md`, `context.md`.
- **Dates** use ISO 8601 (`YYYY-MM-DD`).
- **One topic per file** — split files rather than overloading them.

## Security

- The GitHub Personal Access Token used to clone/push this repo MUST NEVER be
  committed. It is provided in-session only.
- The `.git/config` `origin` URL must NOT contain the token. The assistant
  resets the remote URL to a clean HTTPS URL immediately after cloning.
- If a token is ever accidentally committed, rotate it immediately on GitHub.
- A pre-commit hook (`scripts/pre_commit_scan.py`) scans staged content for
  known token prefixes and high-entropy strings. It blocks commits that
  contain suspected secrets. Bypass with `git commit --no-verify` for
  confirmed false positives.

### Installing the pre-commit hook on a fresh clone

`.git/hooks/` is not version-controlled, so a fresh clone does not include
the hook shim. After cloning:

```sh
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
exec python3 "$(git rev-parse --show-toplevel)/scripts/pre_commit_scan.py" "$@"
EOF
chmod +x .git/hooks/pre-commit
```

The script itself (`scripts/pre_commit_scan.py`) is version-controlled and
travels with the repo.
