#!/usr/bin/env python3
"""Build and search embeddings for chat history transcripts.

Subcommands:
  build    Build/update the embeddings database from chat_history/.
  search   Search the embeddings database for a query.
  status   Show database status.

Database location: ~/.cache/ai-memory-embeddings.db (outside the repo).
The DB is a derived artifact — regeneratable from transcripts. Not
committed to git.

Dependencies:
  pip install -r scripts/requirements.txt

  Or directly:
  pip install sentence-transformers numpy

  First run downloads the all-MiniLM-L6-v2 model (~80MB) to:
  ~/.cache/torch/sentence_transformers/

Usage:
  python scripts/embeddings.py build
  python scripts/embeddings.py status
  python scripts/embeddings.py search "what did I say about token rotation"
  python scripts/embeddings.py search "test query" -k 10
"""
import argparse
import hashlib
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".cache" / "ai-memory-embeddings.db"
REPO_ROOT = Path(__file__).resolve().parent.parent
CHAT_HISTORY = REPO_ROOT / "chat_history"

# Match "#### Exchange N — trace <id>" or "#### Exchange N - trace <id>"
EXCHANGE_RE = re.compile(
    r"^####\s+Exchange\s+(\d+)\s+[-—]\s+trace\s+([\w-]+)",
    re.MULTILINE,
)


def get_embedder():
    """Load the sentence-transformers model. Print install help if missing."""
    try:
        import numpy as np  # noqa: F401
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: required packages not installed.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Install with:", file=sys.stderr)
        print("  pip install -r scripts/requirements.txt", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or directly:", file=sys.stderr)
        print("  pip install sentence-transformers numpy", file=sys.stderr)
        sys.exit(1)

    print("Loading embedder (first run downloads ~80MB model)...",
          file=sys.stderr)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model, np


def split_exchanges(content):
    """Split a transcript into exchanges."""
    matches = list(EXCHANGE_RE.finditer(content))
    if not matches:
        return []

    exchanges = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end]
        exchange_num = int(match.group(1))
        trace_id = match.group(2)
        exchanges.append({
            "exchange_num": exchange_num,
            "trace_id": trace_id,
            "text": block.strip(),
        })
    return exchanges


def find_transcripts():
    """Walk chat_history/ and find all transcript files."""
    if not CHAT_HISTORY.exists():
        return []
    transcripts = []
    for path in CHAT_HISTORY.rglob("*.md"):
        if path.name in ("README.md", "INDEX.md"):
            continue
        transcripts.append(path)
    return transcripts


def file_hash(path):
    """SHA256 of file contents for change detection."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transcripts (
            path TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            indexed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS exchanges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript_path TEXT NOT NULL,
            exchange_num INTEGER NOT NULL,
            trace_id TEXT,
            text TEXT NOT NULL,
            embedding BLOB,
            FOREIGN KEY (transcript_path) REFERENCES transcripts(path)
        );
        CREATE INDEX IF NOT EXISTS idx_exchanges_transcript
            ON exchanges(transcript_path);
    """)


def build():
    """Build/update the embeddings database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    cur = conn.execute("SELECT path, file_hash FROM transcripts")
    indexed = {row[0]: row[1] for row in cur.fetchall()}

    transcripts = find_transcripts()
    if not transcripts:
        print("No transcripts found in chat_history/.")
        return

    print(f"Found {len(transcripts)} transcript(s).")

    to_index = []
    for path in transcripts:
        rel = str(path.relative_to(REPO_ROOT))
        h = file_hash(path)
        if rel not in indexed or indexed[rel] != h:
            to_index.append((path, rel, h))

    if not to_index:
        print("All transcripts up to date.")
        return

    print(f"{len(to_index)} transcript(s) need (re)indexing.")
    model, np = get_embedder()

    for path, rel, h in to_index:
        print(f"  Indexing: {rel}")
        content = path.read_text(encoding="utf-8")
        exchanges = split_exchanges(content)

        if not exchanges:
            print(f"    WARNING: no exchanges found in {rel}", file=sys.stderr)
            print(f"    File is invisible to semantic search.", file=sys.stderr)
            print(f"    Check that the transcript uses the expected format:", file=sys.stderr)
            print(f"      #### Exchange N - trace <trace_id>", file=sys.stderr)
            print(f"    Skipping.", file=sys.stderr)
            # Mark as indexed with zero exchanges so we don't keep retrying.
            conn.execute(
                "DELETE FROM exchanges WHERE transcript_path = ?", (rel,))
            conn.execute(
                "DELETE FROM transcripts WHERE path = ?", (rel,))
            conn.execute(
                "INSERT INTO transcripts (path, file_hash, indexed_at) "
                "VALUES (?, ?, ?)",
                (rel, h, datetime.now().isoformat()),
            )
            conn.commit()
            continue

        texts = [ex["text"] for ex in exchanges]
        embeddings = model.encode(texts, convert_to_numpy=True)

        conn.execute(
            "DELETE FROM exchanges WHERE transcript_path = ?", (rel,))
        conn.execute(
            "DELETE FROM transcripts WHERE path = ?", (rel,))

        for ex, emb in zip(exchanges, embeddings):
            conn.execute(
                "INSERT INTO exchanges "
                "(transcript_path, exchange_num, trace_id, text, embedding) "
                "VALUES (?, ?, ?, ?, ?)",
                (rel, ex["exchange_num"], ex["trace_id"], ex["text"],
                 emb.astype("float32").tobytes()),
            )
        conn.execute(
            "INSERT INTO transcripts (path, file_hash, indexed_at) "
            "VALUES (?, ?, ?)",
            (rel, h, datetime.now().isoformat()),
        )
        conn.commit()

    print(f"Done. {len(to_index)} transcript(s) indexed.")
    print(f"Database: {DB_PATH}")


def search(query, k=5):
    """Search the embeddings database."""
    if not DB_PATH.exists():
        print(f"Error: database not found at {DB_PATH}.", file=sys.stderr)
        print("Run: python scripts/embeddings.py build", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)

    cur = conn.execute("SELECT COUNT(*) FROM exchanges")
    count = cur.fetchone()[0]
    if count == 0:
        print("Database is empty. Run: python scripts/embeddings.py build")
        return

    print(f"Searching {count} exchange(s) for: {query!r}",
          file=sys.stderr)

    model, np = get_embedder()
    query_emb = model.encode([query], convert_to_numpy=True)[0]
    query_norm = np.linalg.norm(query_emb)

    cur = conn.execute(
        "SELECT id, transcript_path, exchange_num, trace_id, text, embedding "
        "FROM exchanges"
    )
    results = []
    for row in cur.fetchall():
        _id, tpath, ex_num, trace_id, text, emb_bytes = row
        emb = np.frombuffer(emb_bytes, dtype="float32")
        emb_norm = np.linalg.norm(emb)
        if emb_norm == 0 or query_norm == 0:
            sim = 0.0
        else:
            sim = float(np.dot(query_emb, emb) / (query_norm * emb_norm))
        results.append((sim, tpath, ex_num, trace_id, text))

    results.sort(reverse=True)

    print(f"\nTop {k} matches:")
    for i, (sim, tpath, ex_num, trace_id, text) in enumerate(
        results[:k], 1
    ):
        preview = text[:240].replace("\n", " ")
        if len(text) > 240:
            preview += "..."
        print(f"\n{i}. (sim={sim:.3f}) {tpath} :: Exchange {ex_num}")
        print(f"   trace: {trace_id}")
        print(f"   {preview}")


def status():
    """Show database status."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run: python scripts/embeddings.py build")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT COUNT(*) FROM transcripts")
    t_count = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM exchanges")
    e_count = cur.fetchone()[0]

    transcripts = find_transcripts()
    print(f"Database: {DB_PATH}")
    print(f"  size: {DB_PATH.stat().st_size} bytes")
    print(f"  indexed transcripts: {t_count}")
    print(f"  indexed exchanges:   {e_count}")
    print(f"  on-disk transcripts: {len(transcripts)}")

    cur = conn.execute("SELECT path FROM transcripts")
    indexed_paths = {row[0] for row in cur.fetchall()}
    disk_paths = {str(p.relative_to(REPO_ROOT)) for p in transcripts}

    stale = indexed_paths - disk_paths
    missing = disk_paths - indexed_paths

    if stale:
        print(f"  stale (deleted from disk): {len(stale)}")
        for p in sorted(stale):
            print(f"    {p}")
    if missing:
        print(f"  not yet indexed: {len(missing)}")
        for p in sorted(missing):
            print(f"    {p}")

    if not stale and not missing and t_count == len(transcripts):
        print("  all in sync.")


def main():
    parser = argparse.ArgumentParser(
        description="Embeddings for chat history transcripts."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="Build/update embeddings database.")
    sub.add_parser("status", help="Show database status.")
    search_p = sub.add_parser("search", help="Search exchanges.")
    search_p.add_argument("query", help="Search query.")
    search_p.add_argument(
        "-k", "--top-k", type=int, default=5,
        help="Number of results (default: 5)."
    )

    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "status":
        status()
    elif args.command == "search":
        search(args.query, args.top_k)


if __name__ == "__main__":
    main()
