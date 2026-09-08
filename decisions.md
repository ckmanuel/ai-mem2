# Key Decisions

Append-only log. Newest at top. Don't edit past entries — supersede with a new entry.

**Three sources of truth, no overlap:**
1. `chat_history/` — verbatim transcript.
2. `decisions.md` — durable decisions (this file).
3. `context.md` Recently Completed — short-term pointer list.

No parallel summary files. They drift.

**Memory file routing:**
- Facts → `knowledge.md`
- Preferences → `preferences.md`
- Decisions → `decisions.md`
- Current focus → `context.md`
- Projects → `projects.md`
- Verbatim record → `chat_history/`

<!--
Entry template:

## YYYY-MM-DD — <Short title>
- **Context:** <what triggered this>
- **Decision:** <what was decided>
- **Rationale:** <why>
- **Status:** active | superseded by <date>
-->

## 2026-09-08 — Retrieval tools: prune, index, embeddings
- **Context:** As `chat_history/` grows, finding what was said in past
  sessions becomes a grep problem. Three layers added to address
  different scales of corpus.
- **Decision:** Three scripts, each solving a different retrieval
  problem:
  1. `scripts/prune_chat_history.sh` — moves transcripts older than N
     days (default 180) to `archive/chat-history-<date>/`. Reduces
     active corpus size. Doesn't solve semantic search; solves the
     "500 transcripts" problem by reducing 500 to 50.
  2. `scripts/update_index.py` — generates `chat_history/INDEX.md`
     with one-line summary per session (date, model, session_id,
     first user message). Grep this file instead of grepping every
     transcript. Pure Python, no deps.
  3. `scripts/embeddings.py` — builds SQLite DB of exchange embeddings
     at `~/.cache/ai-memory-embeddings.db` (outside the repo,
     regeneratable). Uses `sentence-transformers` with
     `all-MiniLM-L6-v2` model (~80MB). Provides `build`, `status`,
     `search` subcommands. Optional dep documented in
     `scripts/requirements.txt`.
- **Why three layers, not one:** each layer addresses a different
  scale. Pruning handles 500+ transcripts by reducing the active
  corpus. Index handles 50+ transcripts by giving grep a smaller
  target. Embeddings handle semantic search that grep can't do.
  User adopts each layer as the corpus grows, not all at once.
- **Embeddings DB outside repo:** derived artifact, regeneratable
  from transcripts, user-specific. Doesn't pollute git history.
  If DB corrupts, delete and rebuild.
- **Status:** active — scripts implemented and tested on empty repo.
  Embeddings not tested end-to-end in this workspace (sentence-
  transformers requires torch which exceeds workspace disk). Script
  handles missing dependency with clear install instructions.

