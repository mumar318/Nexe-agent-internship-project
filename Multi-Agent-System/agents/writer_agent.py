# agents/writer_agent.py — Writer Agent
# Specialises in drafting reports, formatting content, and writing documents.

import os
import re
import json
import sqlite3
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from config import get

load_dotenv()
client = Groq(api_key=get("GROQ_API_KEY"))

AGENT_ID = "writer_agent"

SYSTEM_PROMPT = """You are a professional writer agent. Your job is to draft and format content.

AVAILABLE TOOLS:
- draft_report(title, content)  → write and save a formatted business report
- format_content(text, style)   → reformat text (styles: bullet_points, numbered, paragraph, executive_summary)
- write_document(title, body)   → create a structured document

RULES:
- Return ONLY a single valid JSON object
- NO markdown, NO backticks, NO explanation
- Format: {"name": "tool_name", "arguments": {"param": "value"}}
- If no tool needed, return: {"name": "done", "arguments": {"answer": "your answer"}}

Current step: {step}
Context: {context}
"""

DB_FILE = "multi_agent.db"


def _ensure_db():
    conn = sqlite3.connect(DB_FILE)
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


def draft_report(title: str, content: str) -> str:
    """Draft and save a business report to SQLite."""
    try:
        # Use LLM to enhance the report
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional business writer. Format the given content into a clean, well-structured business report with sections. Be concise and professional."},
                {"role": "user",   "content": f"Title: {title}\n\nContent to format:\n{content}"}
            ]
        )
        formatted = resp.choices[0].message.content.strip()

        conn = _ensure_db()
        conn.execute(
            "INSERT INTO reports (title, content, timestamp) VALUES (?, ?, ?)",
            (title, formatted, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        return f"✅ Report '{title}' drafted and saved.\n\n{formatted[:500]}{'...' if len(formatted) > 500 else ''}"
    except Exception as e:
        return f"❌ Failed to draft report: {e}"


def format_content(text: str, style: str = "paragraph") -> str:
    """Reformat text into the requested style."""
    style_instructions = {
        "bullet_points":      "Convert the text into clear bullet points.",
        "numbered":           "Convert the text into a numbered list.",
        "paragraph":          "Rewrite the text as clean, professional paragraphs.",
        "executive_summary":  "Condense the text into a 3-sentence executive summary."
    }
    instruction = style_instructions.get(style, style_instructions["paragraph"])
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user",   "content": text}
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Formatting failed: {e}"


def write_document(title: str, body: str) -> str:
    """Create a structured document and save it."""
    try:
        conn = _ensure_db()
        conn.execute(
            "INSERT INTO reports (title, content, timestamp) VALUES (?, ?, ?)",
            (title, body, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        return f"✅ Document '{title}' created and saved.\n\nPreview: {body[:300]}{'...' if len(body) > 300 else ''}"
    except Exception as e:
        return f"❌ Failed to write document: {e}"


TOOL_MAP = {
    "draft_report":    draft_report,
    "format_content":  format_content,
    "write_document":  write_document,
}


def _call_llm(step: str, context: str) -> str:
    prompt = SYSTEM_PROMPT.format(step=step, context=context)
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Execute this writing step: {step}"}
        ]
    )
    return resp.choices[0].message.content.strip()


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def execute(step: str, context: str) -> dict:
    """Execute a writing step and return result."""
    try:
        raw  = _call_llm(step, context)
        data = _parse_json(raw)

        tool_name = data.get("name", "done")
        arguments = data.get("arguments", {})

        if tool_name == "done":
            return {"status": "completed", "result": arguments.get("answer", step), "tool": "done"}

        if tool_name not in TOOL_MAP:
            # Fallback: draft a report from context
            result = draft_report(step, context if context else step)
            return {"status": "completed", "result": result, "tool": "draft_report"}

        result = TOOL_MAP[tool_name](**arguments)
        return {"status": "completed", "result": result, "tool": tool_name}

    except Exception as e:
        result = draft_report(step, context if context else step)
        return {"status": "completed", "result": result, "tool": "draft_report"}
