# REMINDER: LOG EACH MESSAGE FIRST

Before responding to each user message, run:

```sh
echo "<user's message>" | ./scripts/begin_exchange.sh <trace_id>
```

This appends the message to the transcript immediately. Fill in your reply
when done. If you skip it and the session truncates, the exchange is lost.

This file exists because the pre-commit hook only catches skips at commit
time, and conversation-only exchanges never reach a commit. It sits on disk
so the reminder survives after the conversation context scrolls away.

Read it at session start and whenever you're unsure you've been logging.
