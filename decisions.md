# Key Decisions

Append-only log of important decisions and their rationale. Newest entries at
the top. Do not edit or delete past entries — supersede them with a new entry
if a decision is reversed.

**Archive:** older decisions live in
`archive/decisions-2026-09-08-session-1.md`. The most recent decisions
stay here. To supersede an archived decision, write a new entry here
and reference the archived one by title.

<!--
Entry template:

## YYYY-MM-DD — <Short title>
- **Context:** <what situation triggered this decision>
- **Decision:** <what was decided>
- **Alternatives considered:** <briefly>
- **Rationale:** <why this option>
- **Implications:** <what changes because of this>
- **Status:** active | superseded by <YYYY-MM-DD entry>
-->

## 2026-09-08 — Lean trim: archive older decisions, cap context.md Recently Completed
- **Context:** After 45 exchanges in one session, `decisions.md` had
  grown to 498 lines (28KB) and `context.md` Recently Completed had
  12 entries. Repository getting bloated. User asked for lean trim
  before forking to a clean-slate repo, so the fork starts lean.
- **Decision:**
  1. **`decisions.md` trimmed.** Kept 5 most recent entries in
     active file. Moved 13 older entries to
     `archive/decisions-2026-09-08-session-1.md`. Archive pointer
     added at top of active file. Full rationale preserved in
     archive; only location changed.
  2. **`context.md` Recently Completed capped at 5 entries.** Older
     entries dropped (they're already in `decisions.md` and
     `chat_history/`).
  3. **`README.md` structure table** includes `archive/` row.
  4. **Convention added:** when `decisions.md` crosses ~20 active
     entries or 25KB, archive the oldest batch to
     `archive/decisions-<date-range>.md`. Same for `context.md`
     Recently Completed crossing 7 entries.
- **Alternatives considered:** Leave as-is (rejected — bloat
  degrades readability and clone speed over time); rewrite older
  entries more tersely (rejected — destroys rationale, which is
  the whole point of the log); delete older entries (rejected —
  rationale should be preserved, just moved).
- **Rationale:** Decision log grows linearly with session activity.
  Without a trim mechanism, it becomes unreadable within a few
  sessions. Archive preserves rationale; active file stays scannable
  in under 2 minutes per the README convention.
- **Status:** active — trim done, convention documented.

## 2026-09-08 — Add sync_before_work.sh for alternating-session safety
- **Context:** User asked how to enforce "Session B must pull before
  becoming active" in alternating-session setups. Existing workflow
  doc mentioned pulling before push but didn't enforce pulling before
  *editing*. Session B idle while Session A commits, then B becomes
  active on stale state — risks push rejection and contradictory work.
- **Decision:** Layer 1 + Layer 3 enforcement (Layer 2 redundant —
  git's built-in rejection already catches this with worse messaging):
  1. **`scripts/sync_before_work.sh`** — one-command pull + summarize.
     Requires `GH_PAT` env var. Fetches latest, compares local HEAD
     to `origin/main`, prints new commits + files changed since
     local HEAD. Warns if any memory files were modified. Tested
     with three scenarios: missing GH_PAT (clear error), behind
     (pulls, lists 2 new commits + 2 changed files, prints ACTION
     REQUIRED warning), up to date (clean message).
  2. **`context.md` workflow step 1** now mandates running
     `sync_before_work.sh` before any memory file edits if the
     session has been idle or another session may have committed.
  3. **`README.md` troubleshooting** adds "Alternating sessions —
     stale state" entry pointing at the script.
- **First version had two bugs:** (1) `git fetch` failed without
  credentials because origin URL is clean HTTPS (PAT stripped for
  security). (2) Error message said "merge conflict" when the real
  failure was auth. Both fixed by requiring `GH_PAT` env var and
  using the ephemeral credential helper pattern for fetch and pull.
  Error reporting now distinguishes auth failures from rebase
  conflicts.
- **Status:** active — script implemented and tested, workflow
  updated, README updated.

## 2026-09-08 — Add knowledge.md; reject conversations/ from external guide
- **Context:** User shared two external guides (CLAW blog tutorial at
  claw.rommark.dev, persistent-memory guide at
  persistent-memory-deploy.vercel.app). Asked to add whatever is
  relevant.
- **Assessment of guides:**
  - **CLAW tutorial:** mostly reproduces what we have, with less
    secure defaults. Recommends `git remote set-url origin
    https://ghp_...@...` (embedding PAT in `.git/config` — we
    rejected this in exchange 6 as a security hole). Recommends
    `git add .` and generic commit messages (we pushed back on
    this in exchange 6). Nothing new to adopt.
  - **Persistent Memory guide:** opening prompt template is
    essentially identical to what we use. File structure proposed:
    `preferences.md`, `projects.md`, `conversations/`,
    `knowledge.md`, `README.md`.
- **Decision:**
  - **Adopt:** `knowledge.md`. New file for facts the user shares
    (domain expertise, stack, team, environment, conventions).
    Previously we had no equivalent. Created with template sections.
  - **Reject:** `conversations/` directory. We already removed
    `sessions/` for the same redundancy reason.
  - **Adopt:** troubleshooting section in README. Pulled the "be
    explicit when asking agent to remember" note from the memory
    guide.
- **Memory file routing clarified in `context.md`:** Facts →
  `knowledge.md`, Preferences → `preferences.md`, Decisions →
  `decisions.md`, Current focus → `context.md`, Projects →
  `projects.md`, Verbatim record → `chat_history/`.
- **Status:** active — `knowledge.md` added, README updated,
  troubleshooting section added, routing clarified.

## 2026-09-08 — Drop sessions/ directory; supersede "keep both" decision
- **Context:** Fifth external critique identified `sessions/`
  (summaries) as structural redundancy with `chat_history/`
  (verbatim transcripts). Two sources of truth for the same
  conversation. The original critique (exchange 8) flagged this
  same overlap; the decision at the time was "keep both, accept
  drift risk." Fifth critique correctly challenged that decision.
- **Decision:** Drop `sessions/` entirely. Three sources of truth
  remain, each with a distinct role:
  1. **`chat_history/<model>/<session_id>-<date>.md`** — verbatim
     transcript. Authoritative record of what was said.
  2. **`decisions.md`** — durable decisions and rationale.
     Append-only. Cross-session.
  3. **`context.md` Recently Completed** — short-term pointer list
     for the most recent few sessions. Auto-rotates as items age
     out.
- **Supersedes:** the original "keep both, accept drift" decision
  from the chat_history/sessions overlap discussion (exchange 8).
  That decision was wrong. Maintenance burden wasn't worth the
  convenience. Drift was inevitable. Two summaries of the same
  content (`sessions/*.md` AND `context.md` Recently Completed)
  was duplication, not defense-in-depth.
- **Rationale:** Three sources, three roles, no overlap. Faster
  scanning is sacrificed at the loss of compact summaries, but
  the trade is worth it. Scanning the verbatim transcript is
  slower than scanning a summary, but the transcript is
  authoritative. The summary was a derivative that lagged and
  sometimes lied.
- **Migration:** `git rm -r sessions/`. Six summary files deleted.
  Their content was already encoded in `context.md` Recently
  Completed and `decisions.md`. No information lost.
- **Status:** active — `sessions/` removed, workflow updated,
  README updated.

## 2026-09-08 — new_session.sh auto-generation + honest forcing-status logging
- **Context:** Fifth critique (exchange 30). Critic pointed out that
  `new_session.sh` required a session_id that IM gateway metadata
  provides, but Claude.ai and other chat providers don't. Without
  that metadata, the script either failed or got a made-up
  placeholder. Critic honestly logged it as an open item rather
  than claiming it was solved.
- **Two issues separated:**
  - **Issue 1 (fixable): script requires session_id that may not
    exist.** FIXED. All args to `new_session.sh` are now optional.
    If session_id is empty, the script auto-generates
    `auto-<unix_timestamp>-<random6>`. If date is empty, uses today.
    Tested with four scenarios (no args, explicit session_id only,
    all explicit Claude, existing file).
  - **Issue 2 (not truly fixable): nothing forces the assistant to
    run the script.** OPEN, HONESTLY LOGGED. The opening prompt,
    FIRST ACTION block, and the script all make it easier and more
    prominent. None of them make it impossible to skip. LLMs are
    non-deterministic. Added CI check at
    `.github/workflows/transcript-check.yml` that flags pushes
    which don't modify a transcript file. This makes the failure
    visible rather than silent, but it's after the fact — the
    session is already over by the time CI runs.
- **Why three layers still aren't "forcing":**
  - Opening prompt: strongest signal, but users may abbreviate.
  - context.md FIRST ACTION block: reinforces after clone, but the
    assistant has to actually read it.
  - Script: makes execution one command, but the assistant has to
    decide to run it.
  - CI check: catches the failure after push, can't prevent it.
  - This is the honest state. No system can truly force an LLM
    to take an action before its first response. The best we can
    do is make skipping hard to do accidentally, and make skips
    visible when they happen.
- **Status:** active. Issue 1 fixed. Issue 2 openly logged as
  partially mitigated but not solved.
