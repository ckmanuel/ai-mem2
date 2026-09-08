# Chat History

Verbatim transcripts of conversations, organized by AI model and then by
session. Each file is one session.

## Structure

```
chat_history/
  GLM/
    <session_id>-<YYYY-MM-DD>.md
    <session_id>-<YYYY-MM-DD>.md
  Claude/
    <session_id>-<YYYY-MM-DD>.md
  ChatGPT/
    <session_id>-<YYYY-MM-DD>.md
```

## File naming convention

`<session_id>-<YYYY-MM-DD>.md`

- `session_id`: the session ID from the IM gateway metadata, used as a
  stable identifier across files.
- Date: ISO 8601, the date the session started.

## Per-file format

Each file starts with a header block:

```
# Session: <session_id> - <date>

**Model:** <model name and channel>
**Channel:** <channel>
**Started:** <date>

[brief note about transcript conventions]

---

#### Exchange 1 - trace <trace_id>

**User:**

> [verbatim user message]

**Assistant:**

> [verbatim assistant reply]

#### Exchange 2 - trace <trace_id>
...
```

## Conventions

- **Verbatim.** User messages and assistant replies are recorded as-is.
- **PAT and other secrets are redacted** before writing. The
  "never commit token" rule overrides "verbatim."
- **Tool calls and tool output are omitted.** Only user-visible
  messages appear.
- **Append-only within a session.** Once an exchange is written, it
  isn't edited. Corrections happen in a later exchange.
- **One file per session.** Don't merge sessions.
- **Best-effort.** If the chat context window is truncated, older
  messages may be lost.

## Creating a new session transcript

Run from the repo root at the start of a new session:

```sh
./scripts/new_session.sh <session_id> <YYYY-MM-DD> [model]
```

`model` is optional, defaults to `GLM`. Use `Claude`, `ChatGPT`, etc.
for other models. The script creates the file with the correct header
block. Refuses to overwrite an existing file (warns instead).

See `context.md` "FIRST ACTION AT SESSION START" block — running this
script is the first thing the assistant should do at the start of any
new session.
