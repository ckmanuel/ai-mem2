# Key Decisions

Append-only log of important decisions and their rationale. Newest entries at
the top. Do not edit or delete past entries — supersede them with a new entry
if a decision is reversed.

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

## 2026-09-08 — Establish GitHub-backed persistent memory
- **Context:** chat.z.ai has no native cross-session memory; the assistant
  loses all context between sessions.
- **Decision:** Use a private GitHub repository (`ckmanuel/ai-memory`) as the
  persistent long-term memory store. Each new session begins by cloning the
  repo, reading relevant files, and committing updates back at the end.
- **Alternatives considered:** Local files only (lost when container resets);
  external SaaS memory services (extra dependency, cost, privacy concerns).
- **Rationale:** GitHub is already trusted infrastructure, supports private
  repos, and gives the user full visibility and control over what is stored.
  Append-only logs + structured files keep memory easy to scan.
- **Implications:** The assistant must (1) never commit the PAT, (2) reset the
  remote URL after cloning so the token is not stored in `.git/config`,
  (3) keep memory files concise and well-organized.
- **Status:** active
