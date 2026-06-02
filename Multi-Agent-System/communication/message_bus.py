# communication/message_bus.py — Central message bus for inter-agent communication
#
# The MessageBus is the communication backbone of the multi-agent system.
# It routes messages between agents, persists the full message history to SQLite,
# and dispatches delegation messages synchronously to specialist agents.

import sqlite3
import json
from datetime import datetime
from typing import Optional

from communication.messages import Message, MessageType

DB_FILE = "multi_agent.db"


class MessageBus:
    """
    Central pub/sub message bus.

    - publish()    → route a message; if it's a TASK_DELEGATION, execute the
                     target agent inline and store the result.
    - get_result() → retrieve the result message for a given delegation.
    - get_history()→ return all messages for a task (for logging/UI).
    """

    def __init__(self):
        self._results: dict[str, Message] = {}   # msg_id → result Message
        self._history: list[Message]      = []
        self._init_db()

    # ── DB setup ───────────────────────────────────────────────────────────────
    def _init_db(self):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message_log (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id    TEXT,
                sender    TEXT,
                recipient TEXT,
                msg_type  TEXT,
                payload   TEXT,
                timestamp TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                task         TEXT,
                plan         TEXT,
                steps        TEXT,
                final_answer TEXT,
                status       TEXT,
                timestamp    TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _persist(self, msg: Message):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.execute(
                "INSERT INTO message_log (msg_id, sender, recipient, msg_type, payload, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (msg.msg_id, msg.sender, msg.recipient,
                 msg.msg_type.value, json.dumps(msg.payload), msg.timestamp)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[MessageBus] DB persist error: {e}")

    # ── Core publish ───────────────────────────────────────────────────────────
    def publish(self, msg: Message) -> None:
        """Publish a message. Delegation messages are executed synchronously."""
        self._history.append(msg)
        self._persist(msg)

        if msg.msg_type == MessageType.TASK_DELEGATION:
            self._dispatch(msg)

    def _dispatch(self, msg: Message) -> None:
        """Route a delegation message to the correct specialist agent."""
        # Import agents lazily to avoid circular imports
        agent_map = self._get_agent_map()

        target = msg.recipient
        agent  = agent_map.get(target)

        if agent is None:
            result_msg = Message(
                sender    = target,
                recipient = msg.sender,
                msg_type  = MessageType.TASK_RESULT,
                payload   = {
                    "ref_msg_id": msg.msg_id,
                    "result":     f"❌ Unknown agent: {target}",
                    "status":     "error"
                }
            )
        else:
            step    = msg.payload.get("step", "")
            context = msg.payload.get("context", "")
            outcome = agent.execute(step, context)

            result_msg = Message(
                sender    = target,
                recipient = msg.sender,
                msg_type  = MessageType.TASK_RESULT,
                payload   = {
                    "ref_msg_id": msg.msg_id,
                    "result":     outcome.get("result", ""),
                    "tool":       outcome.get("tool", ""),
                    "status":     outcome.get("status", "completed")
                }
            )

        self._results[msg.msg_id] = result_msg
        self._history.append(result_msg)
        self._persist(result_msg)

    def _get_agent_map(self) -> dict:
        from agents import research_agent, writer_agent, email_agent, calculator_agent
        return {
            "research_agent":    research_agent,
            "writer_agent":      writer_agent,
            "email_agent":       email_agent,
            "calculator_agent":  calculator_agent,
        }

    # ── Result retrieval ───────────────────────────────────────────────────────
    def get_result(self, agent_id: str, msg_id: str) -> Optional[Message]:
        """Retrieve the result message for a given delegation msg_id."""
        return self._results.get(msg_id)

    def get_history(self) -> list[dict]:
        """Return full message history as list of dicts."""
        return [m.to_dict() for m in self._history]

    # ── Task log ───────────────────────────────────────────────────────────────
    def save_task_log(self, task: str, plan: list, steps: list,
                      final_answer: str, status: str) -> int:
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.execute(
                "INSERT INTO task_log (task, plan, steps, final_answer, status, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (task, json.dumps(plan), json.dumps(steps),
                 final_answer, status, datetime.utcnow().isoformat())
            )
            conn.commit()
            row_id = cur.lastrowid
            conn.close()
            return row_id
        except Exception as e:
            print(f"[MessageBus] Task log error: {e}")
            return -1

    def get_task_logs(self, limit: int = 20) -> list:
        try:
            conn = sqlite3.connect(DB_FILE)
            rows = conn.execute(
                "SELECT id, task, final_answer, status, timestamp "
                "FROM task_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            return [{"id": r[0], "task": r[1], "final_answer": r[2],
                     "status": r[3], "timestamp": r[4]} for r in rows]
        except Exception:
            return []

    def get_task_log_detail(self, log_id: int) -> Optional[dict]:
        try:
            conn = sqlite3.connect(DB_FILE)
            row = conn.execute(
                "SELECT * FROM task_log WHERE id = ?", (log_id,)
            ).fetchone()
            conn.close()
            if not row:
                return None
            return {
                "id": row[0], "task": row[1],
                "plan":  json.loads(row[2]),
                "steps": json.loads(row[3]),
                "final_answer": row[4],
                "status": row[5], "timestamp": row[6]
            }
        except Exception:
            return None

    def get_message_log(self, limit: int = 50) -> list:
        try:
            conn = sqlite3.connect(DB_FILE)
            rows = conn.execute(
                "SELECT msg_id, sender, recipient, msg_type, payload, timestamp "
                "FROM message_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            return [
                {"msg_id": r[0], "sender": r[1], "recipient": r[2],
                 "msg_type": r[3], "payload": json.loads(r[4]), "timestamp": r[5]}
                for r in rows
            ]
        except Exception:
            return []

    def get_reports(self, limit: int = 20) -> list:
        try:
            conn = sqlite3.connect(DB_FILE)
            rows = conn.execute(
                "SELECT id, title, content, timestamp FROM reports "
                "ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            conn.close()
            return [{"id": r[0], "title": r[1], "content": r[2], "timestamp": r[3]}
                    for r in rows]
        except Exception:
            return []
