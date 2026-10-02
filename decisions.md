# Key Decisions

Append-only log of design decisions and the reasoning behind them. Newest at
the top. Don't edit past entries. Supersede them with a new one that names
the old one. Older entries move to `archive/decisions-<range>.md` once this
file passes about 20 entries or 25KB. Move them whole, never rewrite them.

<!--
Entry template:

## YYYY-MM-DD: <Short title>
- **Decision:** <what was decided>
- **Why:** <the reasoning>
- **Rejected:** <alternatives and why not>
-->

## 2026-10-02: CLAUDE.md imports AGENTS.md instead of copying it
- **Decision:** `AGENTS.md` holds the instructions. `CLAUDE.md` is one line,
  `@AGENTS.md`.
- **Why:** Claude Code reads `CLAUDE.md` and not `AGENTS.md`, but a
  `CLAUDE.md` can import another file with `@path`, and that is documented.
  The identical copies I made first were a guess that the import might not
  work, and they would have drifted apart. Other tools read `AGENTS.md`
  directly.
- **Rejected:** A symlink. It needs admin rights on Windows and leaves no
  room for Claude-only additions.
- **Supersedes:** the "identical copies" part of "Front-door files and a
  paste pack".

## 2026-10-02: Script verdicts over model claims
- **Decision:** `doctor.sh` reports health through its exit code, run at
  session start and before the final push. Scanner reports show only 4
  characters of a match plus its length.
- **Why:** An agent saying "all clean" proves nothing, and the protocol
  already admits an LLM can skip steps. A script can't be talked out of a
  FAIL. CI logs on a public repo are public, so a 24-character prefix of a
  real token was too much to print.

## 2026-10-02: Front-door files and a paste pack
- **Decision:** `AGENTS.md` and `CLAUDE.md` point desktop agents at
  `context.md`. `paste_pack.sh` makes a size-capped bundle for chats with no
  sandbox and names what it omitted.
- **Why:** Desktop agents look for these file names on their own, so nobody
  has to paste the opening prompt. The pack covers the case where the repo
  can't be reached. The two front-door files are identical copies because I
  couldn't confirm that every tool follows an include from one to the other.
- **Rejected:** One file importing the other.

## 2026-10-02: Session end, duplicate check, forgetting
- **Decision:** `context.md` gains an end-of-session checklist, a
  search-before-save rule, an `applied lesson:` notice, and a forgetting
  rule.
- **Why:** The protocol covered starting and working but not ending, so
  durable items stayed buried in transcripts. Searching first keeps one entry
  per fact. The notice makes lessons auditable. Deletion in git never erases
  history, so the user should hear that before they rely on it.

## 2026-10-01: Zero-dependency search ahead of embeddings
- **Decision:** `scripts/search.sh` is the default retrieval tool: literal,
  case-insensitive, capped, lessons first, and it states how many results
  are hidden and says plainly when there are none.
- **Why:** The embeddings tool needs torch and a model download, which
  sandboxed web agents often can't run. A search that fails silently is
  worse than none, so a zero result and a truncated result are both made
  explicit. Matching is literal because the caller is usually an agent
  passing free text. Borrowed from create-ai-memory's search design.
- **Rejected:** Fuzzy matching and regex (wrong answers on free text).
  Making embeddings the default.

## 2026-10-01: lessons.md, separate from decisions
- **Decision:** Mistakes and their fixes live in `lessons.md`, one entry each
  with a "Doesn't apply when" line. Lessons are never archived.
- **Why:** A decision records a choice. A lesson records a failure and its
  fix, and it is what you need months later when the same problem returns.
  Archiving by age would delete exactly those. The "Doesn't apply when" line
  keeps lessons from hardening into rigid rules. Pattern taken from gitmem
  and create-ai-memory.
- **Rejected:** Folding lessons into `decisions.md`, where they'd be archived
  with it.

## 2026-09-08: Size limits warn, never block
- **Decision:** `size-check.yml` flags oversized memory files on push. It
  doesn't trim anything or block the push.
- **Why:** CI can flag but can't fix. Auto-archiving needs a split point
  chosen by heuristic, which won't match judgment, and committing back from
  CI is fragile. The decision log is trimmed by moving old entries whole,
  because shortening them destroys the rationale, which is the point of the
  log.
- **Rejected:** Rewriting old entries tersely. Deleting them.

## 2026-09-08: Retrieval in three layers, adopted as the corpus grows
- **Decision:** Prune, index, and embeddings search, each for a different
  scale. The embeddings DB lives outside the repo at
  `~/.cache/ai-memory-embeddings.db`.
- **Why:** Pruning shrinks the active corpus. The index gives grep a smaller
  target. Embeddings answer "what did I say about X?", which grep can't. The
  DB is derived, regenerable, and user-specific, so it doesn't belong in git
  history.

## 2026-09-08: sync_before_work.sh for alternating sessions
- **Decision:** A one-command pull that lists new commits and changed files,
  run before editing when a session has been idle.
- **Why:** An idle session works on stale state. Best case the push is
  rejected. Worst case it contradicts a decision it never saw. Git's own
  rejection only fires at push time, with poor messaging.

## 2026-09-08: Commits are scoped and meaningful
- **Decision:** Commit only inside the memory repo, once per unit of work,
  with a descriptive message.
- **Why:** A blanket `git add .` from the workspace root sweeps in scripts
  holding tokens, binaries, and build output. Committing every turn buries
  real work in noise, and generic messages lose information.
- **Rejected:** `git add .`, per-turn commits, generic messages.

## 2026-09-08: Binaries stay out of git
- **Decision:** `.gitignore` blocks PDFs, images, office files, and media.
  A binary is pushed only on explicit request, with `git add -f`.
- **Why:** Every pushed binary stays in history forever, which bloats the
  repo and slows every future clone.
- **Rejected:** Auto-pushing deliverables. Git LFS and a separate repo until
  volume justifies them. Amend plus force-push as a habit. Revisit if
  deliverables are pushed more than once per session on average.

## 2026-09-08: Secrets never touch the repo or `.git/config`
- **Decision:** The token reaches git through a one-shot credential helper
  that reads an environment variable. Two scanners run: a local pre-commit
  hook and a CI scan of all tracked files.
- **Why:** Embedding the token in the remote URL writes it to `.git/config`.
  `.git/hooks/` isn't version controlled, so fresh clones have no hook until
  `install_hooks.sh` runs. The CI scan covers that gap after the fact. The
  entropy threshold is 4.5 bits per character, since 4.0 flagged ordinary
  paths and base64. Remaining false positives get `--no-verify` or an entry
  in `FALSE_POSITIVES`. Prevention is the env var. Rotation is damage
  control.
- **Rejected:** Token in the remote URL.

## 2026-09-08: Transcript logging is layered, not forced
- **Decision:** `new_session.sh` creates the transcript at session start
  (session_id is optional, since not every platform provides one).
  `begin_exchange.sh` logs each message before the reply. The pre-commit
  hook blocks memory-file changes without a transcript. CI warns after push.
  `TRANSCRIPT_REMINDER.md` stays on disk as a failsafe.
- **Why:** Nothing can force an LLM to act before its first reply. Each layer
  makes skipping harder to do by accident, and CI makes a skip visible after
  the fact. This is partial mitigation, not a guarantee. The hook covers the
  five memory files only, since docs and scripts don't come from
  conversation.

## 2026-09-08: One transcript file per session, per model
- **Decision:** `chat_history/<model>/<session_id>-<date>.md`, verbatim,
  with secrets redacted. The "never commit the token" rule overrides
  "verbatim".
- **Why:** A single running file grows without bound, collides across
  sessions, and can't be pruned or indexed by session.

## 2026-09-08: Three sources of truth, no overlap
- **Decision:** `chat_history/` holds the verbatim record. `decisions.md`
  holds durable decisions. `context.md` Recently Completed is a short
  pointer list. `knowledge.md` holds facts that have no other home. No
  parallel summary files.
- **Why:** A per-session summary directory duplicated the transcript and
  `context.md`. The summaries lagged and sometimes lied, so drift was
  inevitable. Scanning a transcript is slower than scanning a summary, but
  the transcript is authoritative.
- **Rejected:** Keeping both a transcript and summaries. A `conversations/`
  directory from an external guide, for the same redundancy.
- **Supersedes:** an earlier "keep both, accept the drift" decision, which
  was wrong.

## 2026-09-08: One repo for memory, workspace output, and transcripts
- **Decision:** A single repo holds all three.
- **Why:** One repo is one mental model, easier to scan, and a fresh clone
  gets everything. The token already has access to it, so no scope grows.
- **Rejected:** A separate workspace repo.
