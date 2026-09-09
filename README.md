# ai-mem2

Persistent memory for cross-session chat with AI agents.

## Structure

| File / Dir | Purpose |
|---|---|
| `preferences.md` | User preferences (kept across fork). |
| `knowledge.md` | Facts the user shares. |
| `projects.md` | Active and past projects. |
| `decisions.md` | Durable decisions, append-only. |
| `context.md` | Current focus. Read first. |
| `chat_history/` | Verbatim transcripts, per session per model. |
| `scripts/` | `pre_commit_scan.py`, `scan_repo.py`, `install_hooks.sh`, `new_session.sh`, `sync_before_work.sh`, `prune_chat_history.sh`, `update_index.py`, `embeddings.py`, `requirements.txt`. |
| `.github/workflows/` | `secret-scan.yml`, `transcript-check.yml`, `size-check.yml`. |

## Setup (first time)

If you're forking or cloning this repo to start your own persistent
memory, follow these steps in order.

### 1. Create a private GitHub repository

Go to [github.com/new](https://github.com/new):
- Repository name: `ai-memory` (or any name you want)
- Visibility: **Private** (important — your memory contains personal context)
- Don't initialize with README (this repo already has one)
- Click "Create repository"

### 2. Generate a GitHub Personal Access Token (PAT)

Go to [github.com/settings/tokens](https://github.com/settings/tokens)
→ "Fine-grained tokens" → "Generate new token":

- **Token name:** `ai-memory access` (or any descriptive name)
- **Expiration:** 90 days (rotate regularly)
- **Repository access:** "Only select repositories" → pick the repo
  you just created
- **Repository permissions:**
  - **Contents:** Read and write (required for clone/push/pull)
  - **Workflows:** Read and write (required for CI workflows to push)
- Click "Generate token"
- **Copy the token immediately.** You won't see it again.

### 3. (Recommended) Store the PAT in an env var

Don't paste the token into chat prompts. Store it in your shell:

```sh
echo 'export GH_PAT="github_pat_YOUR_TOKEN_HERE"' >> ~/.bashrc
# or ~/.zshrc on macOS
source ~/.bashrc
```

Now you can reference `$GH_PAT` in any command or prompt without the
literal token appearing in chat logs, shell history, or git config.

### 4. Clone the repo and install the pre-commit hook

```sh
git clone "https://github.com/YOUR_USERNAME/ai-memory.git"
cd ai-memory
./scripts/install_hooks.sh
```

The hook scans every commit for leaked tokens and blocks them. Until
it runs, local commits won't be scanned.

### 5. Use the opening prompt at the start of every new chat session

Paste this at the start of every new chat with your AI agent. The
prompt tells the assistant to run `./scripts/new_session.sh` at
session start. That script defaults to `GLM` as the model — pass a
different name (`Claude`, `ChatGPT`, etc.) as the third arg if you're
using a different chat platform.

```
I want you to use my private GitHub repository as persistent memory
across chat sessions.

GitHub repository: https://github.com/YOUR_USERNAME/ai-memory.git
GitHub Personal Access Token: use $GH_PAT env var

At the beginning of this session:
1. Clone the repository to a working directory.
2. Reset the remote URL to clean HTTPS (do NOT leave the token in
   .git/config).
3. Read context.md FIRST. It has a "FIRST ACTION AT SESSION START"
   block at the top.
4. Run ./scripts/new_session.sh to create this session's transcript
   file. Args are all optional — auto-generates session_id if needed.
5. Read preferences.md, decisions.md, and any relevant project /
   session files.
6. Use the relevant information as context for this session.

During the conversation:
- Save important information about my preferences, projects, decisions,
  and ongoing work.
- For each user message you receive, IMMEDIATELY append the user
  message to the transcript file BEFORE working on the response.
  Use: echo "the user's message" | ./scripts/begin_exchange.sh <trace_id>
  Then fill in your reply when done. If you skip this step, the
  exchange is lost forever if the session truncates.
- Append each exchange to chat_history/<model>/<session_id>-<YYYY-MM-DD>.md
  (verbatim, with trace_id, redact any token or secret).
- Update existing memories instead of creating duplicates.
- After meaningful work, commit and push using an ephemeral credential
  helper (token from env var, never persisted to .git/config).
- Pre-commit hook blocks commits that change memory files without
  updating the transcript. Bypass with --no-verify only for genuinely
  conversation-independent commits (README typos, script refactors).

NEVER save, commit, or expose my GitHub token inside the repository.
The "never commit token" rule overrides "verbatim transcript."
```

## Setup after cloning

If you already have the repo and just need to set up a fresh clone:

```sh
./scripts/install_hooks.sh
```

Installs the pre-commit hook locally. `.git/hooks/` isn't version-
controlled, so this is required on every fresh clone. Until it runs,
local commits won't be scanned for secrets.

## Retrieval tools

As `chat_history/` grows, finding what was said in past sessions gets
harder. Three tools, ordered from cheapest to most powerful:

**1. Prune old transcripts.** Move transcripts older than N days to
`archive/chat-history-<date>/`.

```sh
./scripts/prune_chat_history.sh        # default: 180 days
./scripts/prune_chat_history.sh 90     # custom threshold
```

**2. Generate a session index.** One-line summary per session, written
to `chat_history/INDEX.md`. Grep this file instead of grepping every
transcript.

```sh
python3 scripts/update_index.py
```

Run after each new session. The index is a derived artifact — safe to
delete and regenerate.

**3. Embeddings-based search.** Builds a local SQLite DB of exchange
embeddings, provides semantic search across all transcripts. Handles
the "what did I say about X last month?" case that grep can't.

```sh
pip install -r scripts/requirements.txt        # one-time
python3 scripts/embeddings.py build            # build/update DB
python3 scripts/embeddings.py status           # show DB status
python3 scripts/embeddings.py search "token rotation"
python3 scripts/embeddings.py search "test query" -k 10
```

DB lives at `~/.cache/ai-memory-embeddings.db` (outside the repo,
regeneratable, user-specific). First run downloads the
`all-MiniLM-L6-v2` model (~80MB).

## Token rule

Never commit the PAT. The pre-commit hook scans for token prefixes and
high-entropy strings. CI backstop scans again on push. If a token leaks,
rotate it immediately.

Recommended: store the PAT in an env var (`export GH_PAT=...`) and
reference it as `$GH_PAT` in the opening prompt. Chat never sees the
token.

**Note for web agents (chat.z.ai, Claude.ai, etc.):** the env var
approach requires a persistent machine where the shell rc file
survives. Web agents run in ephemeral workspaces — `~/.bashrc` resets
each session, no SSH access, no persistent filesystem. There is no
workaround. The PAT must be entered in the opening prompt to reach
the workspace. This is a known limitation, not a user error. Do not
flag the PAT in the opening prompt as a leak — flag it only if it
lands in a commit or memory file. Daily rotation remains the right
mitigation for the chat-log exposure.

## Files outside the repo

`.gitignore` blocks binaries (PDFs, DOCX, XLSX, PNGs, JPGs, MP3s, etc.)
by default. Deliverables, screenshots, and other binary files live in
`/home/z/my-project/download/` (or wherever your workspace keeps
downloads) — not in this repo. The reason: every push of a binary
stores a new copy in git history forever, which bloats the repo and
slows future clones.

If you specifically want to back up a binary to git, override
`.gitignore` explicitly:

```sh
git add -f path/to/file.pdf
```

Only do this when the file genuinely needs version control here.
Routine large-file backup should use Git LFS or a separate repo.

## Credits

The persistent memory pattern (private GitHub repo + opening prompt +
per-session transcripts) is based on the
[Persistent Memory Guide](https://persistent-memory-deploy.vercel.app/)
by [Rommark.Dev](https://rommark.dev), built with Z.ai.

The pre-commit secret scanner, CI workflows, retrieval tools
(prune / index / embeddings), alternating-session sync, and
`new_session.sh` auto-generation were added by the assistant
(GLM on chat.z.ai) in collaboration with the user.
