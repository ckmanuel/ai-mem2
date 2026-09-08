# REMINDER: UPDATE THE TRANSCRIPT

Before responding to each user message, run:

  echo "<user's message>" | ./scripts/begin_exchange.sh <trace_id>

This appends the user message to the transcript immediately. Fill in
your reply later. If you skip this and the session truncates, the
exchange is lost forever.

## Why this file exists

The pre-commit hook only catches skips at commit time. Conversation-only
exchanges that don't touch memory files slip past it. This file is the
failsafe — a persistent reminder that doesn't depend on conversation
context staying intact.

## When to read this

- At session start (after context.md).
- Whenever you're about to respond to a user message.
- If you're unsure whether you've been updating the transcript.

## The discipline problem

This file can't force you to read it. But it's here, on disk, even
after the conversation that created it has scrolled out of the context
window. That's the point — persistence without depending on memory.
