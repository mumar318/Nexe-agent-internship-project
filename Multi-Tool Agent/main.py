# main.py

import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

from tools import web_search, save_note, send_email
from db import save_log

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Tool registry ─────────────────────────────────────────────────────────────
function_map = {
    "web_search": web_search,
    "save_note": save_note,
    "send_email": send_email,
}

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a strict tool-calling AI assistant with three tools.

RULES:
- DO NOT write code
- DO NOT explain anything
- ONLY return JSON
- NO markdown (no ```)

AVAILABLE TOOLS:
- web_search(query)                        → search the web for information
- save_note(title, content)                → save a note or result to the database
- send_email(to, subject, body)            → send an email to someone

RESPONSE FORMAT (always return exactly this):
{
  "name": "tool_name",
  "arguments": {
    "param1": "value1"
  }
}

EXAMPLES:
User: "Search for latest AI news"
→ {"name": "web_search", "arguments": {"query": "latest AI news"}}

User: "Save a note titled Meeting Summary with content: Discussed Q3 goals"
→ {"name": "save_note", "arguments": {"title": "Meeting Summary", "content": "Discussed Q3 goals"}}

User: "Send an email to john@example.com about the project update"
→ {"name": "send_email", "arguments": {"to": "john@example.com", "subject": "Project Update", "body": "Here is the latest project update."}}
"""


def run_agent(user_input: str) -> dict:
    message = None
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        message = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        cleaned = re.sub(r"```(?:json)?", "", message, flags=re.IGNORECASE).replace("```", "").strip()

        data = json.loads(cleaned)

        if "name" not in data:
            output = {"error": "LLM did not return a tool name.", "raw_response": message}
            save_log(user_input, output)
            return output

        tool_name = data["name"]
        arguments = data.get("arguments", {})

        if tool_name not in function_map:
            output = {"error": f"Unknown tool: '{tool_name}'", "raw_response": message}
            save_log(user_input, output)
            return output

        result = function_map[tool_name](**arguments)

        output = {
            "tool_used": tool_name,
            "input": arguments,
            "result": result
        }

    except json.JSONDecodeError:
        output = {
            "error": "Failed to parse LLM response as JSON.",
            "raw_response": message
        }
    except TypeError as e:
        output = {
            "error": f"Tool argument error: {str(e)}",
            "raw_response": message
        }
    except Exception as e:
        output = {
            "error": f"Unexpected error: {str(e)}",
            "raw_response": message if message else None
        }

    save_log(user_input, output)
    return output
