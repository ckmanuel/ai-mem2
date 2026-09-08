# Current Context

Short-term, in-progress state. The assistant reads this file first after
cloning because it points to what is actively being worked on right now.

## Current Focus
- Unified workspace setup is done. One repo (`ckmanuel/ai-memory.git`)
  holds memory files, workspace output, and `chat_history.md`.
- Voice and style rules from `preferences.md` apply to every reply.
- Awaiting the user's first real task. Memory setup is complete.

## Workflow (every feature / fix from here on)
1. Do the work.
2. Append the new exchange to `chat_history.md` (verbatim, with trace_id).
3. Commit with a descriptive message.
4. Push using ephemeral credential helper (token from env var only).
5. Update `context.md` and `decisions.md` if anything material changed.

## Open Threads
- `preferences.md` still has unfilled sections: Tooling & Environment,
  Document & Output Preferences, Coding Style. Capture these as they emerge.
- The PAT cannot create new repos (no Administration scope). Not a blocker
  since we're staying in one repo, but worth remembering if the user asks
  for a new repo later.

## Next Actions
- Wait for the user's actual task.

## Recently Completed
- 2026-09-08 — Initialized `ai-memory` repo structure.
- 2026-09-08 — Stored full writing voice and style spec in `preferences.md`.
- 2026-09-08 — Unified workspace + transcript into the same repo. Added
  `chat_history.md`, `.gitignore`, and the verbatim transcript of this
  session so far.

## Blockers / Waiting On
_None yet._
