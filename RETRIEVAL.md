# Retrieval Tools: Agent Guide

Read this after `context.md`. It covers when to use each tool to find things
in past sessions. All commands run from the repo root.

## Which tool, when

**`./scripts/search.sh <term>`** is the default. It is literal, case-insensitive
grep over memory files and transcripts, with no dependencies. Output is capped
and says how many results are hidden, and a zero result says so plainly. Search
one distinctive word, not a sentence, and try two or three words separately.
Lessons are listed first. Reach for the tools below only when this isn't enough.

**`python3 scripts/update_index.py`** writes `chat_history/INDEX.md`, one line
per session. Run it after a session's transcript is committed and pushed, or
when the index is missing or stale. Don't run it while the only change is the
in-progress session, or the index will point at an uncommitted file. Commit
and push the result.

**`python3 scripts/embeddings.py search "query" [-k 10]`** does semantic
search over all transcripts. Use it when the user asks "what did I say about
X?", references a past decision you can't place, or you're unsure whether
something was already settled. It needs a one-time
`pip install -r scripts/requirements.txt`, and `embeddings.py build` before
the first search. Run `build` at the end of a session or on request, not
mid-session, since the first run downloads a model. `embeddings.py status`
shows what isn't indexed yet.

**`./scripts/prune_chat_history.sh [days]`** moves transcripts older than the
threshold (default 180) to `archive/chat-history-<date>/`. Consider it when
`chat_history/` passes about 50 files. Confirm with the user first unless they
asked for it. Commit and push afterward.

## Using search results

- Open the matched file and read the whole exchange. The preview is only 240
  characters.
- A similarity score isn't proof. A 0.7 match can be a tangent. Read it
  before quoting it.
- Cite the trace_id or exchange number so the user can verify.
- If nothing scores above about 0.5, say you couldn't find it. Don't
  fabricate.
