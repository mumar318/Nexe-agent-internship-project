# db.py

import sqlite3
from datetime import datetime

# Create database connection
conn = sqlite3.connect("logs.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists (with timestamp column)
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    query     TEXT,
    response  TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


def save_log(query: str, response) -> None:
    """Save a query/response pair to the database. Failures are non-blocking."""
    try:
        cursor.execute(
            "INSERT INTO logs (query, response, timestamp) VALUES (?, ?, ?)",
            (query, str(response), datetime.utcnow().isoformat())
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] Failed to save log: {e}")
