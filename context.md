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
- Fresh repo. Awaiting first task.

## Open Threads
_None._

## Recently Completed
_None yet._

## Blockers
_None._
