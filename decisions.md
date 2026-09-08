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

## 2026-09-08 — Drop sessions/ directory; supersede "keep both" decision
- **Context:** Fifth external critique identified `sessions/`
  (summaries) as structural redundancy with `chat_history/`
  (verbatim transcripts). Two sources of truth for the same
  conversation. The original critique (exchange 8) flagged this
  same overlap; the decision at the time was "keep both, accept
  drift risk." Fifth critique correctly challenged that decision.
- **Decision:** Drop `sessions/` entirely. Three sources of truth
  remain, each with a distinct role:
  1. **`chat_history/<model>/<session_id>-<date>.md`** — verbatim
     transcript. Authoritative record of what was said.
  2. **`decisions.md`** — durable decisions and rationale.
     Append-only. Cross-session.
  3. **`context.md` Recently Completed** — short-term pointer list
     for the most recent few sessions. Auto-rotates as items age
     out.
- **Supersedes:** the original "keep both, accept drift" decision
  from the chat_history/sessions overlap discussion (exchange 8).
  That decision was wrong. Maintenance burden wasn't worth the
  convenience. Drift was inevitable. Two summaries of the same
  content (`sessions/*.md` AND `context.md` Recently Completed)
  was duplication, not defense-in-depth.
- **Rationale:** Three sources, three roles, no overlap. Faster
  scanning is sacrificed at the loss of compact summaries, but
  the trade is worth it. Scanning the verbatim transcript is
  slower than scanning a summary, but the transcript is
  authoritative. The summary was a derivative that lagged and
  sometimes lied.
- **Migration:** `git rm -r sessions/`. Six summary files deleted.
  Their content was already encoded in `context.md` Recently
  Completed and `decisions.md`. No information lost.
- **Status:** active — `sessions/` removed, workflow updated,
  README updated.

## 2026-09-08 — new_session.sh auto-generation + honest forcing-status logging
- **Context:** Fifth critique (exchange 30). Critic pointed out that
  `new_session.sh` required a session_id that IM gateway metadata
  provides, but Claude.ai and other chat providers don't. Without
  that metadata, the script either failed or got a made-up
  placeholder. Critic honestly logged it as an open item rather
  than claiming it was solved.
- **Two issues separated:**
  - **Issue 1 (fixable): script requires session_id that may not
    exist.** FIXED. All args to `new_session.sh` are now optional.
    If session_id is empty, the script auto-generates
    `auto-<unix_timestamp>-<random6>`. If date is empty, uses today.
    Tested with four scenarios (no args, explicit session_id only,
    all explicit Claude, existing file).
  - **Issue 2 (not truly fixable): nothing forces the assistant to
    run the script.** OPEN, HONESTLY LOGGED. The opening prompt,
    FIRST ACTION block, and the script all make it easier and more
    prominent. None of them make it impossible to skip. LLMs are
    non-deterministic. Added CI check at
    `.github/workflows/transcript-check.yml` that flags pushes
    which don't modify a transcript file. This makes the failure
    visible rather than silent, but it's after the fact — the
    session is already over by the time CI runs.
- **Why three layers still aren't "forcing":**
  - Opening prompt: strongest signal, but users may abbreviate.
  - context.md FIRST ACTION block: reinforces after clone, but the
    assistant has to actually read it.
  - Script: makes execution one command, but the assistant has to
    decide to run it.
  - CI check: catches the failure after push, can't prevent it.
  - This is the honest state. No system can truly force an LLM
    to take an action before its first response. The best we can
    do is make skipping hard to do accidentally, and make skips
    visible when they happen.
- **Status:** active. Issue 1 fixed. Issue 2 openly logged as
  partially mitigated but not solved.

## 2026-09-08 — Make new-session transcript creation automatic (Option 3)
- **Context:** User asked whether new sessions that clone the git repo
  auto-create the verbatim transcript file. Honest answer: no. The
  convention was documented in `context.md` workflow step 7, but
  nothing enforced it. In fact, this session didn't do it — the
  assistant started writing `chat_history.md` only in exchange 3 when
  explicitly asked. The file got created retroactively. If the user
  had never asked, the whole session would have been lost.
- **Decision:** Option 3 — combine three layers of enforcement:
  1. **`scripts/new_session.sh`** — one-command transcript bootstrap.
     Takes `<session_id> <YYYY-MM-DD> [model]` as args. Creates the
     file with the correct header block. Refuses to overwrite an
     existing file (warns instead). Tested with four scenarios: GLM
     default, Claude, missing args (fails), existing file (warns).
  2. **`context.md` FIRST ACTION AT SESSION START block** — bold
     warning at the top of `context.md`, before the Current Focus
     section. Tells the assistant to run `new_session.sh` before doing
     anything else. Explicitly says "Do not proceed until this is done."
  3. **Recommended opening prompt in `README.md`** — paste-able
     template for the user's first message of a new session.
     Mandates reading `context.md` first, running
     `new_session.sh`, and appending each exchange to the transcript
     file. References `$GH_PAT` env var as the recommended way to
     pass the token (no literal token in the prompt).
- **Why three layers:** each catches a different failure mode.
  - Opening prompt is the first thing the assistant sees. Strongest
    signal. But users may abbreviate or skip parts of the prompt.
  - `context.md` FIRST ACTION block reinforces for sessions where the
    prompt was abbreviated. The assistant reads `context.md` after
    cloning, before any real work.
  - The script makes execution trivial. No need to remember the file
    path convention or header format. Just `./scripts/new_session.sh
    <id> <date>`.
- **Status:** active — implemented and tested. Layer 1 (script) and
  layer 2 (context.md block) are in place. Layer 3 (opening prompt
  template) is documented in README.md for the user to copy.

## 2026-09-08 — Migrate chat_history.md to per-session files under chat_history/<model>/
- **Context:** Original `chat_history.md` was a single growing file.
  Reached 570+ lines after one session. Scrolling to find a specific
  exchange was painful. Only one model header (`## GLM`) existed because
  only GLM was in use, but the structure didn't anticipate Claude,
  ChatGPT, or other models being added later.
- **Decision:** Migrate to `chat_history/<model>/<session_id>-<date>.md`.
  Each session gets its own file under the model's folder. One file per
  session, named with the session ID (stable across files) plus the
  start date.
- **Migration performed:**
  - Source: `chat_history.md` (570 lines, 25 exchanges)
  - Destination: `chat_history/GLM/web-dbcfad74-3816-4ddb-884c-3f78d55dd4f5-2026-09-08.md`
  - Old file deleted.
  - Migration script written, executed, verified (25 exchanges in
    source matched 25 exchanges in destination), then deleted.
  - Added `chat_history/README.md` documenting folder structure and
    file naming convention.
- **Rationale:** Per-session files are smaller, focused, grep-able,
  diff-able across sessions, deletable individually. Folder structure
  anticipates multi-model use (Claude, ChatGPT, etc.) without
  restructuring later.
- **Workflow updated:** new session = new transcript file. Assistant
  creates `chat_history/<model>/<new_session_id>-<today>.md` at the
  start of a new session rather than appending to an existing file.
- **Status:** active — migration complete, structure live.

## 2026-09-08 — Claude session skipped FIRST ACTION transcript step
- **Context:** `context.md`'s "FIRST ACTION AT SESSION START" block
  requires running `scripts/new_session.sh <session_id> <date> [model]`
  before doing anything else, using a `session_id` from IM gateway
  metadata. A Claude session (claude.ai app interface) cloned the repo,
  read memory files, and ran an entire repo-review conversation — version
  checks, critique of install_hooks.sh, research on GitHub push
  protection — without ever running this script or writing to any
  transcript file. The gap was invisible until the user asked why the
  conversation wasn't showing up in git.
- **Root cause:** The Claude app interface does not expose an IM gateway
  session_id the way the script assumes. There was no hard blocker
  preventing the assistant from proceeding without one; it simply moved
  on to answering the user's questions instead of treating the missing
  precondition as something to solve.
- **Decision:** Backfill this session retroactively: created
  `chat_history/Claude/claude-app-mobile-9f3a2c-2026-09-08.md` with a
  manually assigned placeholder session_id, reconstructed all exchanges
  from context (not written turn-by-turn, noted as such in the file).
  Logged the gap here and in `context.md` rather than quietly fixing it
  and moving on.
- **Alternatives considered:** Silently create the file and say nothing
  (rejected — user explicitly asked why history was missing; the honest
  answer is more useful than a quiet patch); wait for the user to notice
  again in a future session (rejected — same failure would repeat).
- **Implications:** The FIRST ACTION rule is not actually self-enforcing
  for Claude sessions specifically, since the session_id precondition
  can't be met the way the script expects. This is a real unresolved gap,
  not fully fixed by this backfill — the next Claude session still has
  to remember to self-generate a session_id and run the script
  unprompted, with nothing structurally forcing it.
- **Status:** partially resolved — backfilled this session, root cause
  (no automatic session_id for Claude sessions) still open.

## 2026-09-08 — External critique round 2: hook install, threshold, token discipline
- **Context:** Second external critique. Three points: (1) hook isn't
  installed on fresh clones because .git/hooks/ isn't version-controlled;
  (2) token discipline still partial, two fixes deferred to user; (3)
  entropy regex will false-positive on legitimate base64 and config.
- **Decision:**
  1. **Hook install:** Added `scripts/install_hooks.sh`. One-command
     install. README updated to point at it as the primary install
     method instead of copy-pasting a heredoc. Re-runs are safe.
     Honest scope: hook only protects clones where it has been
     explicitly installed. The workspace where the assistant commits
     has the hook installed. Fresh clones on the user's machine do
     not, until they run the install script.
  2. **Token discipline:** Unchanged. Still partial. The two real
     fixes (rotate PAT, move PAT out of prompt into env var) remain
     user-side actions. Assistant cannot perform them. Will keep
     flagging at natural checkpoints.
  3. **Entropy threshold:** Raised from 4.0 to 4.5 bits/char. Re-tested
     with four cases: github_pat_ prefix (blocked), random string at
     5.37 entropy (blocked), filesystem path (passes), base64 blob with
     `data:` prefix (passes). True positives still caught, the main
     false positive class eliminated. Base64 without a breaking prefix
     character will still false-positive; user can `--no-verify` past
     those, and we extend FALSE_POSITIVES as patterns emerge.
- **Status:** refined after fourth critique (exchange 20).
  - **Pre-commit hook: implemented, but install gap is real.**
    `scripts/install_hooks.sh` reduces install friction from
    copy-paste-heredoc to one command. It does NOT make install
    automatic. Every fresh clone ships without the hook until a
    human runs the install script. Git deliberately does not allow
    repos to ship executable hooks — security feature, not bug.
    Earlier framing that edged toward "fixed" was wrong. Correct
    framing: easier to fix, still not automatic.
  - **CI backstop: implemented.** Added `.github/workflows/secret-scan.yml`
    that runs `scripts/scan_repo.py` on every push and PR. Different
    threat model: catches leaks post-push rather than pre-commit.
    Makes leaks visible rather than silent. If a leak slips past
    the missing local hook, the CI check flags it on GitHub. Still
    requires rotation of any leaked secret since the commit is
    already in remote history by the time CI runs.
  - **Five options considered for closing the gap automatically.**
    See `chat_history.md` exchange 20 for the full list. None of
    them remove the need for one-time user action. The honest
    answer is: document the gap, add CI as defense-in-depth,
    stop pretending install_hooks.sh closes it.
  - **Token discipline:** unchanged from exchange 19 refinement.
    Pre-commit hook + CI backstop + daily PAT rotation (damage
    control) + env var (prevention, recommended user-side action).

## 2026-09-08 — Deliverables: only pushed when explicitly requested
- **Context:** User asked whether deliverables (PDFs, DOCX, XLSX, PNGs)
  could live in git without bloating context. After clarification,
  user decided to keep current setup: deliverables stay on workspace
  local disk, only pushed to GitHub when explicitly requested.
- **Decision:** Deliverables are NOT pushed automatically. Default is
  local-only in `/home/z/my-project/download/`. To back up a specific
  deliverable to GitHub, user says "push X" and assistant runs
  `git add -f <file>` (override .gitignore), commits, pushes.
- **Alternatives considered:** Automatic push of all deliverables
  (rejected — bloats repo history with binaries); Git LFS (rejected
  for now — scope/cost); separate `ai-deliverables` repo (deferred
  until volume justifies it); `git commit --amend` + force-push for
  updates (rejected as default habit — history rewriting is a
  footgun even solo).
- **Rationale:** Simplest default. No surprise bloat. User keeps
  control. If a deliverable matters enough to back up, the user
  knows it and asks. Volume stays low until proven otherwise.
- **Revisit trigger:** If user starts asking to push deliverables
  more than once per session on average, revisit the second-repo
  or LFS options.
- **Status:** active

## 2026-09-08 — Resolved: keep chat_history.md verbatim + add pre-commit hook
- **Context:** External critique flagged that `chat_history.md` (verbatim)
  and `sessions/` (summaries) overlap in purpose and will drift out of
  sync. Verbatim logs also structurally tend to catch secrets.
- **Decision:** Option B. Keep `chat_history.md` as verbatim (user's
  stated preference, exchange 4). Add a pre-commit hook that scans
  staged content for known token prefixes and high-entropy strings,
  rejects commit if found. Hook lives at `scripts/pre_commit_scan.py`
  (version-controlled) and is invoked by `.git/hooks/pre-commit` (shim,
  not version-controlled).
- **Implementation:** Hook scans for github_pat_, ghp_, gho_, ghs_,
  ghu_, sk-ant-, sk-, AIza, AKIA, AGPA/AIDA/AROA/ANPA/AIPA/ASIA,
  xox[abp]-, glpat-, private key blocks, JWTs, and password=/api_key=
  /token= assignments. Also flags any string of length >= 32 with
  Shannon entropy >= 4.5 bits/char (raised from 4.0 after path false
  positives). False positives filtered: md5, sha1, sha256, uuids,
  version strings, urls, filesystem paths. Tested with fake tokens
  in both prefix and high-entropy categories — both blocked correctly.
- **Bypass:** `git commit --no-verify` for confirmed false positives.
  Documented in hook output.
- **Status:** active — implemented 2026-09-08

## 2026-09-08 — Resolved: extend .gitignore to exclude all deliverable types
- **Context:** The "unify" decision (exchange 5) put memory, workspace
  output, and transcript in one repo. Risk: first large deliverable
  (PDF, DOCX, XLSX, PNG) pushed to this repo bloats history and slows
  future clones.
- **Decision:** Option A. Keep one repo. Extend `.gitignore` to
  exclude all deliverable file types: PDF, DOC/DOCX, XLS/XLSX,
  PPT/PPTX, PNG, JPG, JPEG, GIF, SVG, WEBP, BMP, ICO, TIFF, HEIC,
  PSD, AI, Sketch, Figma, EPUB, MOBI, AZW, MP3, WAV, FLAC, AAC, OGG,
  WEBM, AVI, MKV, SQLite/DB. Deliverables live in
  `/home/z/my-project/download/` outside git. Force-add with
  `git add -f <file>` only when a binary truly needs version control
  here.
- **Revisit trigger:** If a deliverable exceeds ~5MB and genuinely
  needs version control here, split into a sibling `ai-deliverables`
  repo (Option B from the original analysis).
- **Status:** active — implemented 2026-09-08

## 2026-09-08 — Resolved: token discipline process fixes (partial)
- **Context:** External critique correctly identified that the PAT leak
  was a behavior issue, not a repo-structure issue. Three process fixes
  proposed in exchange 8.
- **Decision:**
  1. **Pre-commit hook: IMPLEMENTED.** See decision above. Scans
     staged content for known token prefixes and high-entropy strings.
     Tested with fake tokens in both categories — both blocked.
  2. **PAT rotation cadence: DEFERRED TO USER.** Recommend 90-day
     rotation. Set a calendar reminder. Current PAT was visible in
     chat during this session and should be rotated now regardless
     of cadence.
  3. **PAT out of prompt: DEFERRED TO USER.** Currently the user pastes
     the PAT in every new session's opening message. If the PAT lived
     in an env var on the user's machine (`export GH_PAT=...` in
     `~/.zshrc` or `~/.bashrc`) and the prompt said "use $GH_PAT to
     clone ckmanuel/ai-memory.git," the chat never sees the token.
     Requires user-side setup; can't be done from the assistant side.
- **Status:** partial — hook done, rotation and env var await user action

## 2026-09-08 — Adopt scoped git sync protocol, reject blanket `git add .`
- **Context:** User sent a system directive mandating `git add .` from
  workspace root, commit, and push after every turn, with a generic
  commit message.
- **Decision:** Reject blanket `git add .` and "after every turn"
  frequency. Commit only inside `ckmanuel/ai-memory.git`, only after a
  meaningful unit of work, with a descriptive commit message. Token
  always via env var, never persisted.
- **Alternatives considered:** Literal `git add .` from
  `/home/z/my-project/` (rejected — would commit
  `scripts/redact_token.py` containing the PAT in plaintext, plus
  future `node_modules/`, build output, downloads); "after every turn"
  cadence (rejected — buries real work in 20–50 noise commits per
  session); generic commit message (rejected — loses information).
- **Rationale:** The PAT leak vector from `redact_token.py` was concrete
  and imminent. Even after deleting that file, future scripts and
  outputs in `/home/z/my-project/` will routinely contain secrets,
  binaries, or large artifacts that don't belong in the memory repo.
  Scoping commits to the memory repo + descriptive messages keeps
  history useful and safe.
- **Implications:**
  - The assistant commits inside `ai-memory/` only, never from
    `/home/z/my-project/` root.
  - One commit per unit of work, not per turn.
  - Commit message describes what changed.
  - `chat_history.md` updated alongside the work it documents.
  - Assistant reports commit hash + what changed at the end of each
    commit, per user's confirmation request.
- **Status:** active

## 2026-09-08 — Add "no manufactured criticism" rule to feedback tone
- **Context:** User noted some AIs manufacture nitpicks when asked for
  feedback, just to seem diligent. Honest feedback sometimes means
  saying "this is fine."
- **Decision:** Added a directive to `preferences.md` FEEDBACK TONE
  section: if asked for feedback and nothing is material to flag, say
  "Nothing to flag here" and stop. Do not invent minor nitpicks to
  fill space.
- **Alternatives considered:** None. Direct user request.
- **Rationale:** Manufactured nitpicks are a form of dishonesty. The
  feedback tone already calls for blunt honesty, and this extends it
  to the case where honesty means "no notes."
- **Implications:** Feedback responses can be short. "Ship it" is a
  valid feedback reply when the work is solid.
- **Status:** active

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
