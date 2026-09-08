# Session: 2026-09-08 — Git protocol negotiation + feedback rule

**Session start:** 2026-09-08
**Channel:** zai-web (chat.z.ai)
**Goal:** Negotiate a safe git sync protocol and add a feedback rule.

## What happened
- **Exchange 6:** User sent a system directive mandating `git add .`
  from workspace root, commit, push after every turn, generic commit
  message. Assistant pushed back: (1) critical — `git add .` would
  commit `scripts/redact_token.py` containing the PAT in plaintext;
  (2) excessive frequency; (3) generic message loses information.
  Proposed safer protocol: scoped to `ai-memory/`, meaningful units
  only, descriptive messages, token via env var.
- **Exchange 7:** User confirmed. Added a new feedback rule: don't
  manufacture nitpicks. If feedback is clean, say so.
- Assistant:
  - Deleted `/home/z/my-project/scripts/redact_token.py`.
  - Verified no PAT anywhere in `/home/z/my-project/` outside `.git/`.
  - Added "Don't manufacture criticism" directive to FEEDBACK TONE in
    `preferences.md`. Mirrored it in "What the Assistant Should Always
    Do."
  - Appended exchanges 6 and 7 to `chat_history.md` (with PAT redacted
    from user messages, per the override rule that "never commit token"
    beats "verbatim").
  - Added two decision entries: scoped git sync protocol, and the no-
    manufactured-criticism rule.
  - Updated `context.md`.
  - Committed and pushed.

## Key outcomes
- Git sync protocol is scoped and safe. No blanket `git add .`.
- Feedback rule extended: honesty includes "no notes" when there's
  nothing material to flag.
- `redact_token.py` leak vector removed.

## Notes for next session
- Read `context.md` first. Then `preferences.md`. Voice rules apply to
  every reply.
- Commit inside `ai-memory/` only, never from `/home/z/my-project/`
  root.
- One commit per unit of work, not per turn. Descriptive message.
- Report commit hash + what changed at end of each commit.
- Watch own output for warned habits. Default to periods.
- PAT still hasn't been rotated. Recommend again at next opportunity.
