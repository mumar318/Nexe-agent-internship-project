# tools.py

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from db import save_to_db

load_dotenv(override=True)


# ─────────────────────────────────────────────
# ➤ Tool 1: Web Search (SerpAPI - Google Search)
# ─────────────────────────────────────────────
def web_search(query: str) -> str:
    """Search the web using SerpAPI and return top results."""
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    if not SERPAPI_KEY:
        return "❌ Error: SERPAPI_KEY not set in .env"

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3,
        "engine": "google"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if "error" in data:
            return f"❌ Search error: {data['error']}"

        results = data.get("organic_results", [])
        if not results:
            return "⚠️ No results found."

        output = f"🔍 Top results for: '{query}'\n\n"
        for i, r in enumerate(results[:3], 1):
            title = r.get("title", "No title")
            snippet = r.get("snippet", "No description")
            link = r.get("link", "")
            output += f"{i}. **{title}**\n   {snippet}\n   🔗 {link}\n\n"

        return output.strip()

    except requests.exceptions.Timeout:
        return "❌ Error: Search request timed out."
    except Exception as e:
        return f"❌ Search failed: {str(e)}"


# ─────────────────────────────────────────────
# ➤ Tool 2: Save to Database
# ─────────────────────────────────────────────
def save_note(title: str, content: str) -> str:
    """Save a note/result to the SQLite database."""
    try:
        save_to_db(title, content)
        return f"✅ Note saved successfully!\n📌 Title: {title}\n📝 Content: {content}"
    except Exception as e:
        return f"❌ Failed to save note: {str(e)}"


# ─────────────────────────────────────────────
# ➤ Tool 3: Send Email (Gmail SMTP)
# ─────────────────────────────────────────────
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email using Gmail SMTP."""
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return "❌ Error: EMAIL_ADDRESS or EMAIL_PASSWORD not set in .env"

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())

        return f"✅ Email sent successfully!\n📧 To: {to}\n📌 Subject: {subject}"

    except smtplib.SMTPAuthenticationError:
        return "❌ Email authentication failed. Check your EMAIL_ADDRESS and EMAIL_PASSWORD (use Gmail App Password)."
    except smtplib.SMTPException as e:
        return f"❌ SMTP error: {str(e)}"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"
