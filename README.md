# ai-memory

Persistent long-term memory for cross-session chat with AI Agents.

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
| `knowledge.md`   | Facts and domain info the user has shared (stack, team, environment).    |
| `projects.md`    | Active and past projects, with status and key links.                  |
| `decisions.md`   | Important decisions and their rationale (append-only log).             |
| `context.md`     | Current work-in-progress, open threads, and short-term focus.         |
| `chat_history/`  | Verbatim transcripts, one file per session, organized by AI model. See `chat_history/README.md`. |
| `scripts/`       | `pre_commit_scan.py` (local hook), `scan_repo.py` (CI scanner), `install_hooks.sh` (hook install), `new_session.sh` (transcript bootstrap), `sync_before_work.sh` (pull + summarize before editing in alternating sessions). |
| `.github/workflows/secret-scan.yml` | CI backstop: runs scanner on every push and PR. |
| `.github/workflows/transcript-check.yml` | CI backstop: flags pushes that don't update a transcript file. |

## Conventions

- **Concise over verbose** — each file should be skimmable in under 2 minutes.
- **Append-only where possible** — `decisions.md` is append-only.
- **No secrets** — never store API keys, tokens, passwords, or PII here.
- **Update in place for** `preferences.md`, `projects.md`, `context.md`.
- **Three sources of truth, no overlap:** verbatim transcript
  (`chat_history/`), durable decisions (`decisions.md`), immediate
  focus (`context.md`). No parallel summary files — they drift.
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

**The gap, stated bluntly:** `.git/hooks/` is not version-controlled.
A fresh clone does not have the hook. Every fresh clone ships
unprotected until a human runs the install script. There is no way
around this — git deliberately does not allow repos to ship executable
hooks, because that would let any cloned repo run arbitrary code on
the user's machine.

**Local protection (pre-commit):** run this once after cloning:

```sh
./scripts/install_hooks.sh
```

Creates `.git/hooks/pre-commit` and makes it executable. Re-runs are
safe. Until this runs, your local commits will not be scanned.

**CI backstop (post-push):** a GitHub Actions workflow at
`.github/workflows/secret-scan.yml` runs `scripts/scan_repo.py` on
every push and PR. This catches secrets that slipped past a missing
local hook. Different threat model — it catches leaks after they hit
remote history, not before. If CI fails on a push, the secret is
already in remote history and must be rotated immediately.

## Recommended opening prompt for a new session

Paste this at the start of every new chat session. If the PAT lives in
an env var on your machine (recommended), reference it as `$GH_PAT`
instead of pasting the literal token.

If the chat provider gives you IM gateway metadata with a session_id
(chat.z.ai does), note the session_id for use in step 4 below. If not
(Claude.ai, ChatGPT), step 4 will auto-generate one.

```
I want you to use my private GitHub repository as persistent memory
across chat sessions.

GitHub repository: https://github.com/ckmanuel/ai-memory.git
GitHub Personal Access Token: <paste token, or "use $GH_PAT env var">

At the beginning of this session:
1. Clone the repository to a working directory.
2. Reset the remote URL to clean HTTPS (do NOT leave the token in
   .git/config).
3. Read context.md FIRST. It has a "FIRST ACTION AT SESSION START"
   block at the top.
4. Run ./scripts/new_session.sh to create this session's transcript
   file. Args are all optional:
     - If session_id is available (IM gateway metadata), pass it.
     - If not, run with no args; the script auto-generates one.
   - Read preferences.md, decisions.md, and any relevant project /
     session files.
5. Use the relevant information as context for this session.

During the conversation:
- Save important information about my preferences, projects, decisions,
  and ongoing work.
- Append each exchange to this session's transcript file at
  chat_history/<model>/<session_id>-<YYYY-MM-DD>.md (verbatim, with
  trace_id, redact any token or secret).
- Update existing memories instead of creating duplicates.
- After meaningful work, commit and push using an ephemeral credential
  helper (token from env var, never persisted to .git/config).

NEVER save, commit, or expose my GitHub token inside the repository.
The "never commit token" rule overrides "verbatim transcript."
```

## Troubleshooting

**Memory not updating.** If the agent says memory is loaded but nothing
gets saved, be explicit. Say "Save this to my memory" or "Update
`knowledge.md` with this fact" or "Add this decision to `decisions.md`."
The agent may interpret "remember this" as "acknowledge this" without
writing it down.

**Token rejected on push.** Check GitHub → Settings → Developer
settings → Personal access tokens. Verify the token is still valid and
has `Contents: Read and write` (and `Workflows` scope if pushing
workflow files). If expired, generate a new one and update the env var
or paste it in the next session's opening prompt.

**Repository not found.** Verify the URL is `ckmanuel/ai-memory.git`
and the PAT has access to that specific repo. Fine-grained PATs are
scoped to specific repos — a PAT for one repo won't work on another.

**Pre-commit hook blocks a false positive.** Use `git commit --no-verify`
to bypass. Document the bypass in the commit message so future-you
knows why. If the same false positive recurs, extend
`FALSE_POSITIVES` in `scripts/pre_commit_scan.py`.

**Transcript file not created at session start.** Run
`./scripts/new_session.sh` with no args — it auto-generates a
session_id. If the session already produced exchanges, backfill them
into the transcript file retroactively. Log the gap in `decisions.md`.

**Rate limit exceeded.** GitHub allows 5000 authenticated API
requests/hour. Memory updates are typically minimal (a few commits per
session). If you hit the limit, something is wrong — check for
runaway scripts or repeated clone/push loops.

**Alternating sessions — stale state.** If you're running two sessions
on the same repo (Session A finishes, then B becomes active), B must
pull latest before editing. Run
`GH_PAT=$GH_PAT ./scripts/sync_before_work.sh` first. The script
fetches, prints what changed, and warns if any memory files were
modified by the other session. Re-read those files before editing them.
Without this, B will commit on stale state, the push will get
rejected, and B may produce work that contradicts decisions A just made.
