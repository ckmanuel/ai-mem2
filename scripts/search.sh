#!/bin/sh
# Literal, case-insensitive search over memory files and transcripts.
# Zero dependencies, so it works where the embeddings tool cannot.
#
# Usage: ./scripts/search.sh <term>
#   MEM_SEARCH_LIMIT=25   max result lines printed (default 25)
#
# Search ONE distinctive word, not a sentence. Matching is literal, so a
# full error line finds nothing while one unusual word in it does.
# Order: lessons.md, other top-level memory files, then transcripts.
# One line per file until the cap, so one chatty file can't crowd out others.
# Exit 0 on matches, 1 on none, 2 on bad usage.

TERM_="$1"
LIMIT="${MEM_SEARCH_LIMIT:-25}"

[ -n "$TERM_" ] || { echo "Usage: $0 <term>" >&2; exit 2; }
case "$LIMIT" in ''|*[!0-9]*) echo "MEM_SEARCH_LIMIT must be a number." >&2; exit 2;; esac

cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$0"/..)" || exit 2

RAW=$(grep -rniF --include='*.md' --exclude-dir=.git --exclude-dir=archive \
        --exclude-dir=tests -- "$TERM_" . 2>/dev/null | sed 's#^\./##')

if [ -z "$RAW" ]; then
    echo "0 matches for '$TERM_'. This is a real zero, not a truncated result."
    echo "Matching is literal and case-insensitive: a typo or a whole sentence finds nothing."
    echo "Try one distinctive word, or two or three separately."
    exit 1
fi

TOTAL=$(printf '%s\n' "$RAW" | wc -l | tr -d ' ')
FILES=$(printf '%s\n' "$RAW" | cut -d: -f1 | sort -u | wc -l | tr -d ' ')

SHOWN=$(printf '%s\n' "$RAW" \
  | awk -F: '{ r=3; if ($1=="lessons.md") r=0; else if ($1 !~ /\//) r=1;
               else if ($1 ~ /^chat_history\//) r=2; print r "\t" $0 }' \
  | sort -s -k1,1n | cut -f2- \
  | awk -F: -v lim="$LIMIT" '
      { if (!($1 in seen)) { seen[$1]=1; a[++na]=$0 } else { b[++nb]=$0 } }
      END { n=0
            for (i=1; i<=na && n<lim; i++) { print a[i]; n++ }
            for (i=1; i<=nb && n<lim; i++) { print b[i]; n++ } }' \
  | awk '{ if (length($0) > 200) $0 = substr($0, 1, 200) "..."; print }')

echo "$TOTAL match(es) for '$TERM_' in $FILES file(s)"
echo "--"
printf '%s\n' "$SHOWN"
COUNT=$(printf '%s\n' "$SHOWN" | wc -l | tr -d ' ')
if [ "$COUNT" -lt "$TOTAL" ]; then
    echo "--"
    echo "showing $COUNT of $TOTAL ($((TOTAL - COUNT)) hidden). Narrow the term, or raise MEM_SEARCH_LIMIT."
fi
