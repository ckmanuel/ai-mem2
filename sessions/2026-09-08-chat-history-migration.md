# Session: 2026-09-08 — Chat history migration to per-session files

**Session start:** 2026-09-08
**Channel:** zai-web (chat.z.ai)
**Goal:** Migrate `chat_history.md` to a per-session, per-model folder
structure.

## What happened
- User noted `chat_history.md` was getting long (570+ lines after one
  session) and asked why only GLM was listed. The structure didn't
  anticipate multi-model use or per-session files.
- User proposed the structure:
  ```
  chat_history/
    GLM/
      <session>.md
    Claude/
      <session>.md
  ```
- Assistant agreed, asked for confirmation, user said "do it."
- Assistant wrote a migration script that:
  - Read the existing `chat_history.md`
  - Extracted the preamble (transcript conventions)
  - Stripped the old top-level `## GLM` and `### Session` headers
    (now encoded in the file path)
  - Wrote the transformed content to
    `chat_history/GLM/web-dbcfad74-3816-4ddb-884c-3f78d55dd4f5-2026-09-08.md`
  - Verified exchange count: 25 in source, 25 in destination.
  - Deleted the old `chat_history.md` and the migration script.
- Added `chat_history/README.md` documenting the folder structure and
  file naming convention.
- Updated top-level `README.md` structure table.
- Updated `context.md` workflow: new session = new transcript file at
  `chat_history/<model>/<session_id>-<YYYY-MM-DD>.md`.
- Added decision entry in `decisions.md`.

## Key outcomes
- Chat history is now per-session, per-model. Easy to scan, grep, diff.
- Multi-model use anticipated: add `Claude/`, `ChatGPT/`, etc. folders
  when those models enter use. No restructuring needed.
- Migration script deleted after use. Not committed. (One-time tool,
  not a recurring artifact.)

## Notes for next session
- At the start of a new session, create
  `chat_history/GLM/<new_session_id>-<today>.md`. Don't append to the
  existing file.
- Same convention applies if you start using Claude or ChatGPT: create
  the model folder if it doesn't exist, then put the session file there.
- The per-session file should start with the header block (Model,
  Channel, Started, brief conventions note), then `---`, then the
  exchanges in order.
