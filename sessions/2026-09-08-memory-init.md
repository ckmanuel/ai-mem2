# Session: 2026-09-08 — Memory system initialization

**Session start:** 2026-09-08
**Channel:** zai-web (chat.z.ai)
**Goal:** Establish the GitHub-backed persistent memory system.

## What happened
- User provided a private GitHub repository (`ckmanuel/ai-memory`) and a
  Personal Access Token, asking the assistant to use the repo as persistent
  long-term memory across chat sessions.
- The assistant cloned the repository. The repo contained only a placeholder
  `README.md` (`# ai-memory`).
- The assistant created an initial memory structure:
  - `README.md` — overview and conventions
  - `preferences.md` — user preferences (template, to be filled)
  - `projects.md` — active and archived projects (empty)
  - `decisions.md` — append-only decisions log (seeded with the
    "Establish GitHub-backed persistent memory" entry)
  - `context.md` — current focus / open threads
  - `sessions/` — directory for per-session summaries
- The assistant reset the remote URL to strip the PAT from `.git/config`.
- Initial structure committed and pushed back to the repository.

## Key outcomes
- Persistent memory is operational.
- All future sessions should start by cloning this repo and reading
  `context.md` first, then `preferences.md`, then any relevant project /
  decision files.

## Notes for next session
- `preferences.md` is mostly empty — first priority for the next session is
  to capture concrete preferences from the user.
- Treat this session as the template for the `sessions/` directory: one file
  per session, named `YYYY-MM-DD-short-slug.md`.
