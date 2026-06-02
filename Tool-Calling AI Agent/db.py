# db.py

import sqlite3

# Create database connection
conn = sqlite3.connect("logs.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    response TEXT
)
""")
conn.commit()

# Function to save logs
def save_log(query, response):
    cursor.execute(
        "INSERT INTO logs (query, response) VALUES (?, ?)",
        (query, str(response))
    )
    conn.commit()
    