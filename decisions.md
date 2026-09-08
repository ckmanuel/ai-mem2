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
