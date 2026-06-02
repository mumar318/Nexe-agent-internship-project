# db.py — Execution log persistence

import sqlite3
import json
from datetime import datetime

DB_FILE = "business_agent.db"


def _conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            task        TEXT,
            plan        TEXT,
            steps       TEXT,
            final_answer TEXT,
            status      TEXT,
            timestamp   TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT,
            content   TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn


def save_execution_log(task: str, plan: list, steps: list,
                       final_answer: str, status: str) -> int:
    conn = _conn()
    cur = conn.execute(
        """INSERT INTO execution_logs
           (task, plan, steps, final_answer, status, timestamp)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (task, json.dumps(plan), json.dumps(steps),
         final_answer, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_logs(limit: int = 20) -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT id, task, final_answer, status, timestamp "
        "FROM execution_logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "task": r[1], "final_answer": r[2],
         "status": r[3], "timestamp": r[4]}
        for r in rows
    ]


def get_log_detail(log_id: int) -> dict | None:
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM execution_logs WHERE id = ?", (log_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "task": row[1],
        "plan": json.loads(row[2]),
        "steps": json.loads(row[3]),
        "final_answer": row[4],
        "status": row[5], "timestamp": row[6]
    }


def get_reports(limit: int = 20) -> list:
    conn = _conn()
    rows = conn.execute(
        "SELECT id, title, content, timestamp FROM reports "
        "ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "content": r[2], "timestamp": r[3]}
            for r in rows]
