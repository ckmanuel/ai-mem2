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

## 2026-09-08 — Unify memory, workspace, and transcript in one repo
- **Context:** User originally asked for a separate repo for workspace +
  chat transcript backup. Then reversed course: only `ckmanuel/ai-memory`
  is used for AI chats, so a second repo would fragment the setup.
- **Decision:** Use `ckmanuel/ai-memory.git` as the single repo for memory
  files, workspace output, and the verbatim chat transcript. No separate
  `ai-workspace` repo.
- **Alternatives considered:** Separate `ai-workspace` repo (rejected —
  user wants one repo for all AI chat setup); PAT-embedded remote URL
  (rejected — security hole, token in `.git/config`).
- **Rationale:** One repo = one mental model. Easier to scan, easier to
  clone fresh each session. The PAT already has read/write on this repo,
  no scope escalation needed.
- **Implications:**
  - `chat_history.md` lives at repo root.
  - `.gitignore` excludes `node_modules/`, build output, env files, logs,
    large binaries, editor configs.
  - After each feature or fix: append the new exchange to
    `chat_history.md`, commit, push.
  - Token pulled from env var at push time via ephemeral credential
    helper. Never persisted to disk or `.git/config`.
- **Status:** active

## 2026-09-08 — Adopt explicit writing voice and style rules
- **Context:** User provided a detailed spec for how the assistant should
  write — favoring natural human thought over polished AI-prose, with
  targeted guardrails against common weak habits.
- **Decision:** Apply the spec as the primary writing-voice preference for
  every response. Store it in `preferences.md`. Default to Analysis Mode
  (evidence leads) unless the user asks for an opinion, in which case be
  blunt with no softening.
- **Alternatives considered:** Treat the spec as session-only (rejected —
  too valuable to lose between sessions); store as a separate `voice.md`
  file (rejected — better to keep a single source of truth in
  `preferences.md` so it's always read first).
- **Rationale:** The spec is precise and self-aware — it explicitly says
  uniform polish works against natural voice. Embedding it as the default
  ensures every future session inherits this voice without re-prompting.
- **Implications:** All future responses follow these rules. Periods over
  em dashes. No filler, no meta-commentary. Praise sparingly. Call
  mediocre work mediocre. Push back on weak reasoning.
- **Status:** active

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
