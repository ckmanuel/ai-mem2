#!/bin/sh
# Print a size-capped memory pack to paste into a chat that cannot reach the repo.
#
# Usage: ./scripts/paste_pack.sh [> pack.txt]
#   MEM_PACK_LIMIT=12000   max bytes of pack body (default 12000, about 3k tokens)
#
# Order matters because the cap drops from the end: preferences, current
# focus, lessons, knowledge, then decision titles. Template comments are
# stripped. Anything dropped is named at the bottom, so a silent cut can't
# pass for a complete pack.

LIMIT="${MEM_PACK_LIMIT:-12000}"
case "$LIMIT" in ''|*[!0-9]*) echo "MEM_PACK_LIMIT must be a number." >&2; exit 2;; esac

cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$0"/..)" || exit 2

strip_comments() { awk '/<!--/{c=1} !c{print} /-->/{c=0}'; }

section() {  # title, body-producing command output on stdin
    body=$(cat | strip_comments | sed '/^[[:space:]]*$/N;/^\n$/D')
    [ -n "$body" ] || return 0
    printf '## %s\n%s\n\n' "$1" "$body"
}

focus() {  # Current focus + Open threads from context.md
    awk '/^## (Current focus|Open threads)/{p=1; print; next} /^## /{p=0} p' context.md 2>/dev/null
}

decisions() {  # titles and decision lines only
    grep -E '^## |^- \*\*Decision:\*\*' decisions.md 2>/dev/null | grep -v '^## YYYY'
}

OUT=""
OMITTED=""
add() {  # title, file-or-function
    chunk=$(if [ -f "$2" ]; then section "$1" < "$2"; else "$2" | section "$1"; fi)
    [ -n "$chunk" ] || return 0
    if [ $(( $(printf '%s' "$OUT" | wc -c) + $(printf '%s' "$chunk" | wc -c) )) -le "$LIMIT" ]; then
        OUT="$OUT$chunk"
    else
        OMITTED="$OMITTED $1;"
    fi
}

add "Preferences" preferences.md
add "Current focus and open threads" focus
add "Lessons" lessons.md
add "Knowledge" knowledge.md
add "Decisions (titles only)" decisions

printf 'MEMORY PACK from my private memory repo, generated %s.\n' "$(date +%F)"
printf 'Treat it as background context. If it conflicts with my latest message, my message wins.\n\n'
printf '%s' "$OUT"
[ -z "$OMITTED" ] || printf '\n(Omitted to stay under %s bytes:%s ask me for these.)\n' "$LIMIT" "$OMITTED"
