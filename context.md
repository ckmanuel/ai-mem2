# Current Context

Short-term, in-progress state. The assistant reads this file first after
cloning because it points to what is actively being worked on right now.

## Current Focus
- Memory + workspace + transcript setup is complete.
- Voice and style rules (including the no-manufactured-criticism rule)
  are active and stored in `preferences.md`.
- Git sync protocol is scoped: commit only inside `ai-memory/`, only
  after meaningful work, descriptive messages, token via env var.
- Awaiting the user's first real task.

## Workflow (every meaningful unit of work)
1. Do the work.
2. Append the new exchange to `chat_history.md` (verbatim, with trace_id;
   redact any PAT or secret that appears in user/assistant text).
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

## Open Threads
- **RESOLVED — chat_history.md vs sessions/.** Keep verbatim + pre-commit
  hook. Hook implemented at `scripts/pre_commit_scan.py`, invoked by
  `.git/hooks/pre-commit`. Tested, both token-prefix and high-entropy
  detection work.
- **RESOLVED — scope creep in unified repo.** Extended `.gitignore` to
  exclude all deliverable file types. Deliverables live in
  `/home/z/my-project/download/` outside git. Force-add only with
  `git add -f` when a binary truly needs version control here.
- **PARTIAL — token discipline.** Pre-commit hook implemented and
  tested. Two remaining user-side actions:
  - Rotate current PAT now (visible in chat earlier this session).
  - Move PAT out of opening prompt into env var on user's machine.
    See `decisions.md` for the how-to.
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

## Blockers / Waiting On
_None yet._
