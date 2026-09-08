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

## Open Threads
- **UNRESOLVED — chat_history.md vs sessions/.** External critique
  flagged overlap and drift risk. Verbatim was a user choice. Three
  options on the table (cut, keep+hook, keep+document). Awaiting user
  decision. See `decisions.md`.
- **UNRESOLVED — scope creep in unified repo.** `.gitignore` doesn't
  cover PDFs, DOCX, XLSX, PNGs, scripts/, download/. First large
  deliverable bloats history. Three options on the table. Awaiting
  user decision. See `decisions.md`.
- **UNRESOLVED — token discipline process fixes.** Three proposed:
  pre-commit hook, 90-day rotation, move PAT out of prompt into env
  var. Awaiting user pick. See `decisions.md`.
- `preferences.md` still has unfilled sections: Tooling & Environment,
  Document & Output Preferences, Coding Style. Capture these as they
  emerge.
- The PAT cannot create new repos (no Administration scope). Not a
  blocker since we're staying in one repo.
- User has not yet rotated the PAT after the near-miss in exchange 5.
  Strongly recommended.

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

## Blockers / Waiting On
_None yet._
