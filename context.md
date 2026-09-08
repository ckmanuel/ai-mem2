# Current Context

Short-term, in-progress state. The assistant reads this file first after
cloning because it points to what is actively being worked on right now.

## ⚠️ FIRST ACTION AT SESSION START

Before doing anything else in a new session, create the transcript file:

```sh
./scripts/new_session.sh <session_id> <YYYY-MM-DD> [model]
```

- `session_id`: from the IM gateway metadata JSON in the user's first
  message of the session.
- `YYYY-MM-DD`: today's date.
- `model`: optional. Defaults to `GLM`. Use `Claude`, `ChatGPT`, etc.
  when those models enter use.

This creates `chat_history/<model>/<session_id>-<date>.md` with the
correct header block. Then append each exchange to that file as the
session progresses.

**Do not proceed until this is done.** If the session ends without a
transcript file, the verbatim record is lost. This is the most
important step at session start.

## Current Focus
- Memory + workspace + transcript setup is complete.
- Voice and style rules (including the no-manufactured-criticism rule)
  are active and stored in `preferences.md`.
- Git sync protocol is scoped: commit only inside `ai-memory/`, only
  after meaningful work, descriptive messages, token via env var.
- New session workflow is enforced via `scripts/new_session.sh` +
  this `FIRST ACTION` block + the recommended opening prompt in
  `README.md`. See `decisions.md` for the full chain.
- Awaiting the user's first real task.

## Workflow (every meaningful unit of work)
1. Do the work.
2. Append the new exchange to the current session's transcript file at
   `chat_history/<model>/<session_id>-<YYYY-MM-DD>.md`. Verbatim, with
   trace_id. Redact any PAT or secret that appears in user/assistant text.
3. Update `decisions.md` if a decision was made. Update `context.md` if
   the focus shifted. Add a session summary if the session is wrapping.
4. `git add -A` inside `ai-memory/` only. Commit with a descriptive
   message. Push using ephemeral credential helper (token from env var).
5. Report commit hash + what changed at the end of the response.
6. **Deliverables (PDFs, DOCX, XLSX, PNGs, etc.) are NOT pushed
   automatically.** Default is local-only in
   `/home/z/my-project/download/`. Only push when user explicitly asks
   ("push X", "back up X to GitHub"). Use `git add -f <file>` to
   override .gitignore.
7. **New session = new transcript file.** At the start of a new session,
   create `chat_history/<model>/<new_session_id>-<today>.md`. Don't
   append to a previous session's file.

## Open Threads
- **RESOLVED (partially, see caveat) — Claude sessions skip FIRST ACTION.**
  `scripts/new_session.sh` expects a `session_id` from IM gateway
  metadata. The Claude app interface (claude.ai / mobile) does not
  expose one. A Claude session ran this entire repo-review conversation
  without creating a transcript file at all, violating the "do not
  proceed until this is done" rule, and was only caught when the user
  asked why the chat history didn't show it. Fixed by manually
  assigning a placeholder session_id (`claude-app-mobile-<random>`) and
  backfilling the session from context after the fact. Not a real fix:
  still depends on the assistant remembering to do this unprompted at
  the START of the next Claude session, since no session_id is handed
  to it automatically. Consider: instruct Claude sessions specifically
  to self-generate a session_id (e.g. from user_time_v0 timestamp) and
  run new_session.sh as literally the first tool call, before reading
  any other memory file.
- **RESOLVED — chat_history.md vs sessions/.** Keep verbatim + pre-commit
  hook. Hook implemented at `scripts/pre_commit_scan.py`, invoked by
  `.git/hooks/pre-commit`. Tested, both token-prefix and high-entropy
  detection work.
- **RESOLVED — scope creep in unified repo.** Extended `.gitignore` to
  exclude all deliverable file types. Deliverables live in
  `/home/z/my-project/download/` outside git. Force-add only with
  `git add -f` when a binary truly needs version control here.
- **PARTIALLY RESOLVED — token discipline.** Pre-commit hook done.
  PAT rotates daily on user side (damage control). The actual fix
  — move PAT to env var so opening prompt says "use $GH_PAT"
  instead of pasting the literal value — remains a recommended
  user-side action. Would collapse exposure window to zero. See
  `decisions.md` for the distinction.
- `preferences.md` still has unfilled sections: Tooling & Environment,
  Document & Output Preferences, Coding Style. Capture these as they
  emerge.
- The PAT cannot create new repos (no Administration scope). Not a
  blocker since we're staying in one repo.

## Next Actions
- Wait for the user's actual task.

## Recently Completed
- 2026-09-08 — Initialized memory repo structure.
- 2026-09-08 — Stored writing voice and style spec in `preferences.md`.
- 2026-09-08 — Unified workspace + transcript into one repo. Caught and
  redacted PAT leak in `chat_history.md` before pushing.
- 2026-09-08 — Deleted `scripts/redact_token.py` (leak vector). Added
  "no manufactured criticism" rule to feedback tone. Scoped git sync
  protocol. Logged decisions.
- 2026-09-08 — External critique of repo structure. Logged three open
  decisions: chat_history/sessions overlap, scope creep risk, token
  discipline process fixes.
- 2026-09-08 — Resolved all three open decisions. Built and installed
  pre-commit hook at `scripts/pre_commit_scan.py`. Extended `.gitignore`
  for all deliverable types. Hook tested with fake tokens — works.
- 2026-09-08 — Clarified deliverable backup policy with user. Final
  decision: deliverables stay local-only by default, pushed to GitHub
  only when user explicitly asks. Logged decision, updated workflow.
- 2026-09-08 — Second external critique. Three fixes: (1) added
  `scripts/install_hooks.sh` for one-command hook install on fresh
  clones; (2) raised entropy threshold from 4.0 to 4.5 bits/char
  after re-testing four cases; (3) honestly logged that token
  discipline remains partial — the two real fixes (PAT rotation,
  env var) are user-side actions and still pending.
- 2026-09-08 — Third and fourth critiques. Token discipline framing
  corrected: rotation = damage control, env var = prevention. Not
  equivalent. Install gap acknowledged honestly. CI backstop added
  at `.github/workflows/secret-scan.yml` (runs `scripts/scan_repo.py`
  on every push and PR).
- 2026-09-08 — Migrated `chat_history.md` (single 570-line file) to
  `chat_history/<model>/<session_id>-<date>.md` per-session files.
  Old file deleted. Added `chat_history/README.md` documenting
  folder convention. Workflow updated: new session = new transcript
  file under the model folder.
- 2026-09-08 — Claude session ran an entire repo-review conversation
  (~9 exchanges) without running the FIRST ACTION transcript step,
  because it has no IM gateway session_id available. Caught when user
  asked why chat history didn't show it. Backfilled retroactively at
  `chat_history/Claude/claude-app-mobile-9f3a2c-2026-09-08.md` with a
  manual placeholder session_id. Root cause not fully fixed — see Open
  Threads.
- 2026-09-08 — Verified PAT permissions end-to-end. Read, write,
  push, pull, workflow scope all work for ckmanuel/ai-memory.
  Cannot create new repos (lacks Administration scope). Proved
  PDF push/pull works: created test PDF, force-added (`git add -f`
  overrides .gitignore), pushed at hash 0299bae, cloned fresh, PDF
  landed with readable content, cleaned up at hash caafa48.

## Blockers / Waiting On
_None yet._
