# Current Context

Short-term, in-progress state. The assistant reads this file first after
cloning because it points to what is actively being worked on right now.

## ⚠️ FIRST ACTION AT SESSION START

Before doing anything else in a new session, create the transcript file:

```sh
./scripts/new_session.sh [session_id] [YYYY-MM-DD] [model]
```

All args are optional. If you have IM gateway metadata (chat.z.ai),
use the session_id from there. If not (Claude.ai, ChatGPT, etc.), run
`./scripts/new_session.sh` with no args — the script auto-generates
a session_id (`auto-<timestamp>-<random6>`) and uses today's date.

This creates `chat_history/<model>/<session_id>-<date>.md` with the
correct header block. Then append each exchange to that file as the
session progresses.

**Do not proceed until this is done.** If the session ends without a
transcript file, the verbatim record is lost. This is the most
important step at session start.

**Honest limitation:** nothing in the system *forces* this step. The
opening prompt, this block, and the script all make it easier and more
prominent, but the assistant can still skip it. The CI check at
`.github/workflows/transcript-check.yml` will flag pushes that don't
modify a transcript file, but that's after the fact — it makes the
failure visible, not prevented.

## Current Focus
- Fresh repo. No prior session work to continue.
- Awaiting the user's first task.

## Workflow (every meaningful unit of work)
1. **If your session has been idle or another session may have
   committed, run `GH_PAT=$GH_PAT ./scripts/sync_before_work.sh`
   BEFORE making any memory file edits.** It pulls latest from origin,
   prints what changed, and warns if any memory files were modified by
   the other session. Re-read those files before editing.
2. Do the work.
3. Append the new exchange to the current session's transcript file at
   `chat_history/<model>/<session_id>-<YYYY-MM-DD>.md`. Verbatim, with
   trace_id. Redact any PAT or secret that appears in user/assistant text.
4. Update `decisions.md` if a decision was made. Update `context.md` if
   the focus shifted. Update `knowledge.md` if the user shared a fact
   (domain info, stack, team, environment). Update `preferences.md`
   if a stable preference emerged.
5. `git add -A` inside the repo only. Commit with a descriptive
   message. Push using ephemeral credential helper (token from env var).
6. Report commit hash + what changed at the end of the response.
7. **Deliverables (PDFs, DOCX, XLSX, PNGs, etc.) are NOT pushed
   automatically.** Default is local-only in
   `/home/z/my-project/download/`. Only push when user explicitly asks
   ("push X", "back up X to GitHub"). Use `git add -f <file>` to
   override .gitignore.
8. **New session = new transcript file.** At the start of a new session,
   create `chat_history/<model>/<new_session_id>-<today>.md` via
   `./scripts/new_session.sh`. Don't append to a previous session's
   file.

**Memory file routing — where new info goes:**
- **Facts** (domain, stack, team, environment) → `knowledge.md`
- **Preferences** (stable rules for how the assistant should behave)
  → `preferences.md`
- **Decisions** (durable choices with rationale) → `decisions.md`
- **Current focus** (what's being worked on right now) → `context.md`
- **Projects** (active/past work with status) → `projects.md`
- **Verbatim record** (what was said) → `chat_history/`

## Open Threads
_None yet._

## Next Actions
- Wait for the user's first task.

## Recently Completed
_(Capped at 5 entries. Older items live in `decisions.md` and the
verbatim transcript at `chat_history/`.)_

_None yet._

## Blockers / Waiting On
_None yet._
