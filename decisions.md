# Key Decisions

Append-only log of important decisions and their rationale. Newest entries at
the top. Do not edit or delete past entries — supersede them with a new entry
if a decision is reversed.

**Archive:** older decisions live in
`archive/decisions-<date-range>.md`. The most recent decisions stay
here. To supersede an archived decision, write a new entry here and
reference the archived one by title.

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

## Structural decisions (durable, applied from repo initialization)

These decisions define how the repo works. They were established in the
parent repo (`ckmanuel/ai-memory`) and inherited by this fork. They
are the architectural baseline, not session-specific choices.

### Three sources of truth, no overlap
1. **`chat_history/<model>/<session_id>-<date>.md`** — verbatim
   transcript. Authoritative record of what was said.
2. **`decisions.md`** — durable decisions and rationale.
   Append-only. Cross-session.
3. **`context.md` Recently Completed** — short-term pointer list
   for the most recent few sessions. Auto-rotates as items age out.

No parallel summary files. They drift.

### Memory file routing — where new info goes
- **Facts** (domain, stack, team, environment) → `knowledge.md`
- **Preferences** (stable rules for how the assistant should behave) → `preferences.md`
- **Decisions** (durable choices with rationale) → `decisions.md`
- **Current focus** (what's being worked on right now) → `context.md`
- **Projects** (active/past work with status) → `projects.md`
- **Verbatim record** (what was said) → `chat_history/`

### Token discipline: prevention over damage control
- The PAT must never be committed. Pre-commit hook
  (`scripts/pre_commit_scan.py`) scans for known token prefixes and
  high-entropy strings, blocks commits that contain suspected secrets.
- CI backstop (`.github/workflows/secret-scan.yml`) runs the scanner
  on every push. Catches leaks that slip past a missing local hook.
- Bypass with `git commit --no-verify` only for confirmed false
  positives. Document the bypass in the commit message.
- **Recommended user-side action:** store the PAT in an env var
  (`export GH_PAT=...` in shell rc file) and reference it as
  `$GH_PAT` in the opening prompt. The chat never sees the token.
  Exposure window collapses to zero regardless of session length.
  PAT rotation is damage control; env var is prevention. Both have
  value. They are not equivalent.

### Local pre-commit hook: install gap is real
- `.git/hooks/` is not version-controlled. A fresh clone does not
  have the hook until `./scripts/install_hooks.sh` is run.
- Git deliberately does not allow repos to ship executable hooks —
  security feature, not bug.
- Run `./scripts/install_hooks.sh` once after cloning. Re-runs are
  safe. Until this runs, local commits will not be scanned.

### Transcript creation: 3-layer enforcement, no true forcing
1. **`scripts/new_session.sh`** — one-command transcript bootstrap.
   All args optional. Auto-generates `auto-<timestamp>-<random6>`
   session_id when IM gateway metadata is unavailable (Claude.ai,
   ChatGPT, etc.).
2. **`context.md` FIRST ACTION block** — bold warning at the top.
3. **Recommended opening prompt in `README.md`** — paste-able
   template.
4. **`.github/workflows/transcript-check.yml`** — CI backstop that
   flags pushes which don't modify a transcript file.

Honest limitation: nothing in the system *forces* the assistant to
run `new_session.sh`. The opening prompt, FIRST ACTION block, script,
and CI check all make it easier and more prominent. None of them make
it impossible to skip. LLMs are non-deterministic. The best we can do
is make skipping hard to do accidentally, and make skips visible when
they happen.

### Alternating sessions: pull before becoming active
If running two sessions on the same repo (Session A finishes, then B
becomes active), B must pull latest before editing. Run
`GH_PAT=$GH_PAT ./scripts/sync_before_work.sh` first. The script
fetches, prints what changed, and warns if any memory files were
modified by the other session. Re-read those files before editing.

True parallel (concurrent edits from two sessions) is risky — push
rejections on every commit, merge conflicts on shared memory files.
Alternating with handoff is the practical pattern.

### Deliverables: local-only by default
PDFs, DOCX, XLSX, PNGs, and other binaries stay in
`/home/z/my-project/download/` outside git. `.gitignore` excludes
them. Push a specific deliverable to GitHub only when the user
explicitly asks ("push X", "back up X to GitHub"). Use
`git add -f <file>` to override `.gitignore`.

Reasoning: every push of a binary stores a new copy in git history.
10MB PDF updated 10 times = 100MB in history. Clone times degrade.
One-off PDFs are fine. Routine large-file backup should use Git LFS
or a separate repo.

### Trim when bloated
When `decisions.md` crosses ~20 active entries or 25KB, archive the
oldest batch to `archive/decisions-<date-range>.md`. Same for
`context.md` Recently Completed at 7 entries. CI size-check workflow
(`size-check.yml`) warns when thresholds are crossed. Doesn't
auto-trim, doesn't block push. Just makes bloat visible.
