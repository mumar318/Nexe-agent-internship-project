# agent.py — Autonomous multi-step reasoning agent

import json
import os
import re
from dotenv import load_dotenv
from groq import Groq
from tools import web_search, send_email, save_report, summarize_text, calculate
from db import save_execution_log

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Tool registry ─────────────────────────────────────────────────────────────
TOOLS = {
    "web_search":     web_search,
    "send_email":     send_email,
    "save_report":    save_report,
    "summarize_text": summarize_text,
    "calculate":      calculate,
}

# ── Planner prompt ────────────────────────────────────────────────────────────
PLANNER_PROMPT = """You are a business task planner. Break the user's task into clear, ordered steps.

Return ONLY a JSON array of step descriptions. No markdown, no explanation.

Example:
["Search for competitor pricing", "Summarize findings", "Save report to database", "Send report by email"]

Keep steps concise and actionable. Maximum 6 steps.
"""

# ── Executor prompt ───────────────────────────────────────────────────────────
EXECUTOR_PROMPT = """You are a strict tool-calling business agent.

AVAILABLE TOOLS:
- web_search(query)                          → search the web
- send_email(to, subject, body)              → send an email
- save_report(title, content)                → save a report to database
- summarize_text(text)                       → summarize a block of text
- calculate(expression)                      → evaluate a math expression

RULES:
- Return ONLY a single valid JSON object
- NO markdown, NO backticks, NO explanation, NO extra text
- Use double quotes for all keys and string values
- Format: {{"name": "tool_name", "arguments": {{"param": "value"}}}}
- If no tool is needed, return: {{"name": "done", "arguments": {{"answer": "your final answer"}}}}

Current task step: {step}
Context from previous steps: {context}

Respond with JSON only:"""


def _call_llm(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ]
    )
    return resp.choices[0].message.content.strip()


def _parse_json(text: str) -> dict | list:
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()
    # Unescape escaped quotes (LLM sometimes returns {\"name\": ...})
    if cleaned.startswith("{\\") or cleaned.startswith("[\\"):
        cleaned = cleaned.encode().decode("unicode_escape")
    # Extract first JSON object or array if surrounded by extra text
    match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
    return json.loads(cleaned)


def run_agent(task: str) -> dict:
    """
    1. Plan: break task into steps
    2. Execute: run each step with the right tool
    3. Log: persist the full execution trace
    """
    execution_steps = []
    context_parts   = []
    status          = "success"
    final_answer    = ""

    # ── Step 1: Plan ──────────────────────────────────────────────────────────
    try:
        plan_raw  = _call_llm(PLANNER_PROMPT, f"Task: {task}")
        plan      = _parse_json(plan_raw)
        if not isinstance(plan, list):
            plan = [str(plan)]
    except Exception as e:
        plan = [f"Execute task directly: {task}"]

    # ── Step 2: Execute each planned step ─────────────────────────────────────
    for i, step in enumerate(plan, 1):
        step_log = {
            "step_number": i,
            "step_description": step,
            "tool_used": None,
            "tool_input": None,
            "tool_output": None,
            "status": "pending"
        }

        context_str = "\n".join(context_parts[-3:])  # last 3 results as context

        try:
            prompt = EXECUTOR_PROMPT.format(step=step, context=context_str)
            raw    = _call_llm(prompt, f"Execute this step: {step}")
            data   = _parse_json(raw)

            tool_name = data.get("name", "done")
            arguments = data.get("arguments", {})

            if tool_name == "done":
                final_answer = arguments.get("answer", step)
                step_log["tool_used"]   = "done"
                step_log["tool_output"] = final_answer
                step_log["status"]      = "completed"
                context_parts.append(f"Step {i} result: {final_answer}")
            elif tool_name in TOOLS:
                result = TOOLS[tool_name](**arguments)
                step_log["tool_used"]   = tool_name
                step_log["tool_input"]  = arguments
                step_log["tool_output"] = result
                step_log["status"]      = "completed"
                context_parts.append(f"Step {i} ({tool_name}): {result}")
                final_answer = result
            else:
                step_log["tool_output"] = f"Unknown tool: {tool_name}"
                step_log["status"]      = "error"

        except Exception as e:
            step_log["tool_output"] = f"Error: {str(e)} | Raw LLM: {raw[:200] if 'raw' in dir() else 'N/A'}"
            step_log["status"]      = "error"
            status = "partial"

        execution_steps.append(step_log)

    # ── Step 3: Synthesise final answer ───────────────────────────────────────
    try:
        synthesis_prompt = f"""Task: {task}

Execution results:
{chr(10).join(context_parts)}

Write a concise final summary/answer for the user based on the above results."""
        final_answer = _call_llm("You are a helpful business assistant. Summarize concisely.", synthesis_prompt)
    except Exception:
        pass  # keep last tool output as final answer

    # ── Step 4: Persist log ───────────────────────────────────────────────────
    log_id = save_execution_log(task, plan, execution_steps, final_answer, status)

    return {
        "task":           task,
        "plan":           plan,
        "steps":          execution_steps,
        "final_answer":   final_answer,
        "status":         status,
        "log_id":         log_id
    }
