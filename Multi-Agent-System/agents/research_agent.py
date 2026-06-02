# agents/research_agent.py — Research Agent
# Specialises in web search and information summarisation.

import os
import re
import json
from groq import Groq
from dotenv import load_dotenv
import requests as http_requests
from config import get

load_dotenv()
client = Groq(api_key=get("GROQ_API_KEY"))

AGENT_ID = "research_agent"

SYSTEM_PROMPT = """You are a research specialist agent. Your job is to gather information.

AVAILABLE TOOLS:
- web_search(query)      → search the web for information
- summarize(text)        → summarise a block of text

RULES:
- Return ONLY a single valid JSON object
- NO markdown, NO backticks, NO explanation
- Format: {"name": "tool_name", "arguments": {"param": "value"}}
- If no tool needed, return: {"name": "done", "arguments": {"answer": "your answer"}}

Current step: {step}
Context: {context}
"""


def _call_llm(step: str, context: str) -> str:
    prompt = SYSTEM_PROMPT.format(step=step, context=context)
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Execute this research step: {step}"}
        ]
    )
    return resp.choices[0].message.content.strip()


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def web_search(query: str) -> str:
    """Search the web using SerpAPI."""
    key = get("SERPAPI_KEY")
    if not key:
        return "❌ SERPAPI_KEY not set in .env"
    try:
        resp = http_requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": key, "num": 3, "engine": "google"},
            timeout=15
        )
        data = resp.json()
        if "error" in data:
            return f"❌ Search error: {data['error']}"
        results = data.get("organic_results", [])
        if not results:
            return "⚠️ No results found."
        out = f"🔍 Results for '{query}':\n\n"
        for i, r in enumerate(results[:3], 1):
            out += f"{i}. {r.get('title','')}\n   {r.get('snippet','')}\n   🔗 {r.get('link','')}\n\n"
        return out.strip()
    except Exception as e:
        return f"❌ Search failed: {e}"


def summarize(text: str) -> str:
    """Summarise text using the LLM."""
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Summarise the following text concisely in 3-5 sentences."},
                {"role": "user",   "content": text}
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Summarisation failed: {e}"


TOOL_MAP = {
    "web_search": web_search,
    "summarize":  summarize,
}


def execute(step: str, context: str) -> dict:
    """Execute a research step and return result."""
    try:
        raw  = _call_llm(step, context)
        data = _parse_json(raw)

        tool_name = data.get("name", "done")
        arguments = data.get("arguments", {})

        if tool_name == "done":
            return {"status": "completed", "result": arguments.get("answer", step), "tool": "done"}

        if tool_name not in TOOL_MAP:
            # Fallback: try web_search with the step as query
            result = web_search(step)
            return {"status": "completed", "result": result, "tool": "web_search"}

        result = TOOL_MAP[tool_name](**arguments)
        return {"status": "completed", "result": result, "tool": tool_name}

    except Exception as e:
        # Fallback: direct web search
        result = web_search(step)
        return {"status": "completed", "result": result, "tool": "web_search"}
