# Current Context

Read this file first after cloning.

## FIRST ACTION AT SESSION START

```sh
./scripts/new_session.sh [session_id] [YYYY-MM-DD] [model]
```

All args optional. Creates `chat_history/<model>/<session_id>-<date>.md`
with the right header. Don't proceed until this is done.

If your session was idle and another session may have committed, run
`GH_PAT=$GH_PAT ./scripts/sync_before_work.sh` first to pull and see
what changed.

## CRITICAL: Append user message to transcript IMMEDIATELY

**Read `TRANSCRIPT_REMINDER.md` if you haven't already.** It's the
persistent failsafe for this step — survives context truncation.

When you receive a user message, append it to the transcript file
**before** you start working on the response. Don't wait until the
end. If you skip this and the session ends or context truncates, the
exchange is lost forever.

Two ways to do this:

**Option A — use begin_exchange.sh (recommended):**

```sh
echo "the user's message" | ./scripts/begin_exchange.sh <trace_id>
```

Appends a placeholder entry with the user message and an `(in progress...)`
marker for your reply. Replace the marker with your actual reply when
done. If you forget, the transcript shows an incomplete exchange —
visible failure that the next session can backfill.

**Option B — append manually:**

Append to `chat_history/<model>/<session_id>-<date>.md`:

```
#### Exchange N — trace <trace_id>

**User:**

> <user message verbatim, redact any PAT>

**Assistant:**

> <your reply, appended after you finish>
```

Either way: the user half must be captured BEFORE you start working.
The assistant half can be filled in after.

## Why this matters

Memory file changes (preferences.md, decisions.md, knowledge.md,
context.md, projects.md, README.md) without a transcript update will
be blocked by the pre-commit hook (`scripts/pre_commit_transcript_check.py`).
Bypass with `git commit --no-verify` only for genuinely conversation-
independent commits (README typos, script refactors, CI updates).

CI also warns on push when memory files change without a transcript
update. Doesn't block, but makes the failure visible.

## Current Focus
- Transcript enforcement implemented (pre-commit block, CI warning,
  begin_exchange.sh). Awaiting user's next task.

## Open Threads
- `preferences.md` still has unfilled sections: Tooling & Environment,
  Document & Output Preferences, Coding Style. Capture these as they
  emerge.
- The PAT cannot create new repos (no Administration scope). Not a
  blocker since we're staying in one repo.
- **PAT in opening prompt: known limitation, do not flag.** Web agents
  run in ephemeral workspaces. No persistent shell, no SSH, no env var
  that survives between sessions. The PAT must enter the opening prompt
  to reach the workspace. This is a known limitation, not a user error.
  Do not flag it as a leak — flag only if the PAT lands in a commit or
  memory file. Daily rotation is the mitigation for chat-log exposure.
  See README "Token rule" note.

## Recently Completed
_(Capped at 5 entries. Older items live in `decisions.md` and the
verbatim transcript at `chat_history/`.)_

- 2026-09-08 — Fixed `begin_exchange.sh` "Illegal number: 0" bug.
  Root cause: `grep -c` prints "0" and exits 1 on zero matches; the
  `|| echo 0` fallback fired anyway and duplicated the output to
  "0\n0", breaking arithmetic. Fixed with `|| true` + `${EXISTING:-0}`.
  Verified against a clean fresh-transcript case.
- 2026-09-08 — Transcript enforcement: pre_commit_transcript_check.py
  blocks commits when memory files change without transcript update.
  begin_exchange.sh appends placeholder exchange entry. CI warning
  tightened. context.md workflow updated to append user message at
  start of response. install_hooks.sh now calls both scanners.
  Implemented on both repos.
- 2026-09-08 — Critique round 4 hardening: prune uses git commit date,
  embeddings warns on non-conforming transcripts, PATH false-positive
  regex fixed, update_index uses first user + last assistant, MIT
  LICENSE added, RETRIEVAL.md added, 16-test suite, CI INDEX.md
  staleness check, README "Files outside the repo" section.
- 2026-09-08 — Retrieval tools: prune_chat_history.sh, update_index.py,
  embeddings.py. Tested on 3 transcripts. INDEX.md generated.
- 2026-09-08 — Clean-slate fork `ckmanuel/ai-mem2` set up.

## Blockers
_None._
