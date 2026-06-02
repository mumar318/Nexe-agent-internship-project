# agents/email_agent.py — Email Agent
# Specialises in composing and sending emails via Gmail SMTP.

import os
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from dotenv import load_dotenv
from config import get

load_dotenv()
client = Groq(api_key=get("GROQ_API_KEY"))

AGENT_ID = "email_agent"

SYSTEM_PROMPT = """You are an email specialist agent. Your job is to compose and send emails.

AVAILABLE TOOLS:
- send_email(to, subject, body)          → send an email
- compose_email(to, topic, context)      → compose a professional email from a topic and context, then send it

RULES:
- Return ONLY a single valid JSON object
- NO markdown, NO backticks, NO explanation
- Format: {"name": "tool_name", "arguments": {"param": "value"}}
- If no tool needed, return: {"name": "done", "arguments": {"answer": "your answer"}}
- For send_email: to must be a valid email address
- Default recipient if none specified: nexeagent@gmail.com

Current step: {step}
Context: {context}
"""


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail SMTP."""
    addr = get("EMAIL_ADDRESS")
    pwd  = get("EMAIL_PASSWORD")
    if not addr or not pwd:
        return "❌ EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env"
    try:
        msg = MIMEMultipart()
        msg["From"]    = addr
        msg["To"]      = to
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


def compose_email(to: str, topic: str, context: str) -> str:
    """Use LLM to compose a professional email, then send it."""
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional email writer. Write a clear, concise business email. Return ONLY the email body text, no subject line, no greeting header."},
                {"role": "user",   "content": f"Topic: {topic}\nContext/Information to include:\n{context}"}
            ]
        )
        body    = resp.choices[0].message.content.strip()
        subject = topic[:80]  # use topic as subject
        return send_email(to, subject, body)
    except Exception as e:
        return f"❌ Email composition failed: {e}"


TOOL_MAP = {
    "send_email":    send_email,
    "compose_email": compose_email,
}


def _call_llm(step: str, context: str) -> str:
    prompt = SYSTEM_PROMPT.format(step=step, context=context)
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Execute this email step: {step}"}
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
    """Execute an email step and return result."""
    try:
        raw  = _call_llm(step, context)
        data = _parse_json(raw)

        tool_name = data.get("name", "done")
        arguments = data.get("arguments", {})

        if tool_name == "done":
            return {"status": "completed", "result": arguments.get("answer", step), "tool": "done"}

        if tool_name not in TOOL_MAP:
            return {"status": "error", "result": f"Unknown email tool: {tool_name}", "tool": tool_name}

        result = TOOL_MAP[tool_name](**arguments)
        return {"status": "completed", "result": result, "tool": tool_name}

    except Exception as e:
        return {"status": "error", "result": f"Email agent error: {e}", "tool": "none"}
