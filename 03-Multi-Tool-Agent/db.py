# db.py

import sqlite3
from datetime import datetime

conn = sqlite3.connect("agent.db", check_same_thread=False)
cursor = conn.cursor()

# ── Interaction logs table ────────────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    query     TEXT,
    response  TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# ── Notes / saved results table ───────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT,
    content   TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def save_log(query: str, response) -> None:
    """Log every agent interaction. Non-blocking on failure."""
    try:
        cursor.execute(
            "INSERT INTO logs (query, response, timestamp) VALUES (?, ?, ?)",
            (query, str(response), datetime.utcnow().isoformat())
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] Failed to save log: {e}")


def save_to_db(title: str, content: str) -> None:
    """Save a note to the notes table."""
    cursor.execute(
        "INSERT INTO notes (title, content, timestamp) VALUES (?, ?, ?)",
        (title, content, datetime.utcnow().isoformat())
    )
    conn.commit()


def get_all_notes() -> list:
    """Retrieve all saved notes."""
    cursor.execute("SELECT id, title, content, timestamp FROM notes ORDER BY id DESC")
    return cursor.fetchall()
