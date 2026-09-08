# Retrieval Tools — Agent Guide

Read this after `context.md` at session start. It tells you (the
assistant) when and how to use the three retrieval tools mid-session.

## The three tools

1. **`update_index.py`** — generates `chat_history/INDEX.md`. One-line
   summary per session. Cheap, no deps. Run after each new session.
2. **`prune_chat_history.sh`** — moves old transcripts to
   `archive/chat-history-<date>/`. Run when `chat_history/` crosses 50
   files. Default threshold: 180 days.
3. **`embeddings.py`** — semantic search across all transcripts. Run
   when the user asks "what did I say about X?" and you don't remember.
   Requires optional dep: `pip install -r scripts/requirements.txt`.

## When to invoke each tool

### Run `update_index.py` when:
- A new session just finished (the transcript file was committed).
- The user asks "regenerate the index" or "update INDEX.md."
- You notice `INDEX.md` is missing or stale (file count doesn't match).

Command:
```sh
python3 scripts/update_index.py
```

Output: prints how many transcripts were indexed, writes to
`chat_history/INDEX.md`. Commit and push the result.

### Run `prune_chat_history.sh` when:
- `chat_history/` has more than 50 transcript files.
- The user asks to "clean up old transcripts" or "archive old sessions."
- The user mentions a date threshold ("delete anything older than a year").

Command:
```sh
./scripts/prune_chat_history.sh        # default: 180 days
./scripts/prune_chat_history.sh 365    # custom threshold
```

Output: prints which files were archived. Transcripts move to
`archive/chat-history-<today>/`. After running, commit and push.

### Run `embeddings.py search` when:
- User asks "what did I say about X?" or "did we discuss Y before?"
- User references a past decision and you want to find the original
  conversation.
- You're uncertain whether something was already decided in a prior
  session.

Command:
```sh
python3 scripts/embeddings.py search "your query here"
python3 scripts/embeddings.py search "token rotation policy" -k 10
```

Output: top-K matching exchanges with similarity scores, file paths,
exchange numbers, and trace_ids. Use the file path + exchange number
to read the full context:

```sh
sed -n '<start_line>,<end_line>p' <file_path>
```

Or just open the file and search for "#### Exchange <N>".

### Run `embeddings.py build` when:
- First time setting up embeddings on this machine.
- New transcripts have been added since the last build.
- `embeddings.py status` shows transcripts as "not yet indexed."

Command:
```sh
python3 scripts/embeddings.py build
python3 scripts/embeddings.py status    # check first
```

## How to use search results

When `embeddings.py search` returns results:

1. **Read the top match in full.** The preview is 240 chars. Open the
   file and read the whole exchange for context.
2. **Cite the source.** When you tell the user what was said, include
   the trace_id or exchange number so they can verify:
   > "In session `web-dbcfad74` (2026-09-08), exchange 19, you said
   > that rotation is damage control and env var is prevention."
3. **Don't trust the similarity score blindly.** A 0.7 match might
   be a tangent. Read the actual exchange before quoting it.
4. **If no good matches, say so.** Don't fabricate. If the user asks
   "did I ever mention X?" and search returns nothing above 0.5,
   tell them you couldn't find it.

## When NOT to use these tools

- **Don't run `embeddings.py build` mid-session unless necessary.** It
  takes time on first run (downloads ~80MB model). Run it at the end
  of a session or when the user explicitly asks.
- **Don't run `prune_chat_history.sh` without confirmation.** It
  moves files, which is reversible but annoying. Confirm with the
  user first if they didn't explicitly ask.
- **Don't run `update_index.py` if the only change is the current
  in-progress session.** Wait until the session transcript is committed
  and pushed. Otherwise the index will reference an uncommitted file.

## Failure modes

- **`embeddings.py build` fails with "required packages not installed."**
  Run `pip install -r scripts/requirements.txt` once on this machine.
  The model downloads to `~/.cache/torch/sentence_transformers/`.

- **`embeddings.py search` returns zero results.** Either the DB is
  empty (run `build` first) or the query is too specific. Try broader
  terms.

- **`update_index.py` returns "no transcripts found."** Either
  `chat_history/` is empty (new repo) or all files match the exclusion
  list (README.md, INDEX.md). Normal for a fresh fork.

- **`prune_chat_history.sh` returns "no transcripts older than N days."**
  Either nothing is old enough yet, or the script can't parse commit
  dates (rare — falls back to file mtime).

## Opening prompt addition

If you're a future assistant reading this at session start, add this
line to your context after reading `context.md`:

```
I have read RETRIEVAL.md. I will use embeddings.py search when the
user asks about past conversations, update_index.py after each new
session, and prune_chat_history.sh when chat_history/ crosses 50 files.
```

This makes the convention explicit. The user can grep the transcript
to verify you actually read it.
