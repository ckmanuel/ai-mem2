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
| `sessions/`      | Per-session summaries (one file per session, append-only).            |

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
