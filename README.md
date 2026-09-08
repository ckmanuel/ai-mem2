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

## Setup after cloning

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
