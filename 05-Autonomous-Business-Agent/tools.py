# tools.py — Business tools available to the agent

import os
import smtplib
import requests
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY   = os.getenv("SERPAPI_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# ── Tool 1: Web Search ────────────────────────────────────────────────────────
def web_search(query: str) -> str:
    """Search the web and return top 3 results."""
    if not SERPAPI_KEY:
        return "❌ SERPAPI_KEY not set in .env"
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": SERPAPI_KEY, "num": 3, "engine": "google"},
            timeout=15
        )
        data = resp.json()
        if "error" in data:
            return f"❌ Search error: {data['error']}"
        results = data.get("organic_results", [])
        if not results:
            return "⚠️ No results found."
        out = f"🔍 Search results for: '{query}'\n\n"
        for i, r in enumerate(results[:3], 1):
            out += f"{i}. {r.get('title','')}\n   {r.get('snippet','')}\n   🔗 {r.get('link','')}\n\n"
        return out.strip()
    except Exception as e:
        return f"❌ Search failed: {e}"


# ── Tool 2: Send Email ────────────────────────────────────────────────────────
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail SMTP."""
    addr = os.getenv("EMAIL_ADDRESS")
    pwd  = os.getenv("EMAIL_PASSWORD")
    if not addr or not pwd:
        return "❌ EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env"
    try:
        msg = MIMEMultipart()
        msg["From"] = addr
        msg["To"]   = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(addr, pwd)
            s.sendmail(addr, to, msg.as_string())
        return f"✅ Email sent to {to} — Subject: {subject}"
    except smtplib.SMTPAuthenticationError:
        return "❌ Gmail auth failed. Use an App Password."
    except Exception as e:
        return f"❌ Email failed: {e}"


# ── Tool 3: Save Report to DB ─────────────────────────────────────────────────
def save_report(title: str, content: str) -> str:
    """Persist a business report to SQLite."""
    try:
        conn = sqlite3.connect("business_agent.db")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT,
                content   TEXT,
                timestamp TEXT
            )
        """)
        conn.execute(
            "INSERT INTO reports (title, content, timestamp) VALUES (?, ?, ?)",
            (title, content, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        return f"✅ Report '{title}' saved to database."
    except Exception as e:
        return f"❌ Failed to save report: {e}"


# ── Tool 4: Summarise Text ────────────────────────────────────────────────────
def summarize_text(text: str) -> str:
    """Return a short summary placeholder (LLM does the real work)."""
    words = text.split()
    preview = " ".join(words[:40])
    return f"📝 Text received ({len(words)} words). First 40 words: {preview}..."


# ── Tool 5: Calculate ─────────────────────────────────────────────────────────
def calculate(expression: str) -> str:
    """Safely evaluate a simple math expression."""
    try:
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "❌ Invalid characters in expression."
        result = eval(expression, {"__builtins__": {}})  # noqa: S307
        return str(result)
    except Exception as e:
        return f"❌ Calculation error: {e}"
