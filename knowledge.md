# Knowledge

Facts and information the user has shared that don't fit elsewhere.
Update in place — replace outdated info rather than appending.

This file holds:
- Domain expertise and context the user works in.
- Stack, tools, and frameworks the user uses day-to-day.
- Team, organization, or business context.
- Stable facts about the user's environment, conventions, or workflow.
- Anything that's a "fact" rather than a "preference" (which goes in
  `preferences.md`) or a "decision" (which goes in `decisions.md`).

## Domain & Work Context
- (to be filled as facts emerge)

## Stack & Tools
- (to be filled as facts emerge)

## Team & Organization
- (to be filled as facts emerge)

## Environment
- Timezone: Asia/Manila (from gateway metadata)
- Primary chat platform: chat.z.ai (GLM)
- Other chat platforms used: (to be confirmed — Claude, ChatGPT, etc.)

## Conventions & Workflow
- PAT rotates daily (user-side).
- Deliverables stay local unless explicitly pushed.
- One repo for memory + transcript (no separate repo).
- **Parallel sessions on the same repo: risky.** Push rejections
  happen when both sessions commit and push concurrently (one wins,
  the other gets rejected and must `git pull --rebase`). Merge
  conflicts happen when both sessions edit the same shared memory
  file (`context.md`, `preferences.md`, `decisions.md`,
  `knowledge.md`, `README.md`). Transcript files don't conflict
  because each session has a unique session_id. Practical guidance:
  pull before every push, don't edit the same shared file from two
  sessions simultaneously, never force-push. Cleanest pattern for
  parallel work: one session writes, the other reads-only. Or
  separate repos per project.
- **Alternating sessions (serial with handoff) works cleanly.**
  Session A active, B idle. A commits + pushes, signals done. B
  pulls, becomes active, A goes idle. No push conflicts, no merge
  conflicts, no `.git/index.lock` contention. Each session uses its
  own workspace clone. Handoff signal can be a chat message or just
  behavioral agreement. Subtle gotcha: when B becomes active after
  A's commits, B's LLM context is frozen at whatever it last saw.
  B must pull AND re-read `context.md` + `decisions.md` + relevant
  transcript files before working, otherwise it operates on stale
  state.

## Tools Worth Knowing About
Adjacent tools the user has asked about or that may be useful in future
sessions. Not currently installed. Logged here so future sessions have
context without re-fetching.

- **bex-co/bex-security** — Open-source AI security scanner. Upstream
  fork of OpenAI Codex Security. Scans code repositories for
  vulnerabilities (CWEs, injection flaws, auth bugs) using AI agents.
  Supports Codex, Claude Code, Kimi Code, Muse Code, Qwen Code, MiMo
  Code. Different category from our setup: we scan for secrets in
  commits; Bex scans for vulnerabilities in code. Worth evaluating if
  the user starts building real code projects in this workspace.

- **romangalaxys10-spec/memtrant** — Open-source multi-agent
  coordination server. Same author as the persistent-memory guide
  reviewed in exchange 35 (Roman / rommark.dev). Self-hosted
  TypeScript/Next.js 16/Prisma. Provides a transit memory server for
  distributed AI agent teams — shared memory, agent roles (Team Lead,
  Worker, Observer), instruction boards, heartbeats. Designed for
  multi-agent scenarios. Different model from ours: we use GitHub as
  persistence, one agent per session. Memtrant is a database-backed
  server, multiple agents read/write simultaneously. Worth evaluating
  if the user starts building multi-agent workflows.

## Notes
- When the user says "remember this" or "save this to memory," add the
  fact here (or to `preferences.md` if it's a preference, or to
  `decisions.md` if it's a decision). Be explicit about where the
  fact belongs.
