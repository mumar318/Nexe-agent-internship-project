# agents/calculator_agent.py — Calculator Agent
# Specialises in math calculations and numeric analysis.

import os
import re
import json
import math
from groq import Groq
from dotenv import load_dotenv
from config import get

load_dotenv()
client = Groq(api_key=get("GROQ_API_KEY"))

AGENT_ID = "calculator_agent"

SYSTEM_PROMPT = """You are a calculator specialist agent. Your job is to perform math operations.

AVAILABLE TOOLS:
- calculate(expression)          → evaluate a safe math expression (e.g. "100 * 0.15", "2 ** 8")
- percentage(value, percent)     → calculate percent of a value
- compound_growth(principal, rate, periods) → compound growth calculation
- statistics(numbers)            → mean, min, max of a list of numbers (pass as comma-separated string)

RULES:
- Return ONLY a single valid JSON object
- NO markdown, NO backticks, NO explanation
- Format: {"name": "tool_name", "arguments": {"param": "value"}}
- If no tool needed, return: {"name": "done", "arguments": {"answer": "your answer"}}

Current step: {step}
Context: {context}
"""


def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed = set("0123456789+-*/(). %")
        safe_expr = expression.replace("^", "**").replace("×", "*").replace("÷", "/")
        if not all(c in allowed or c == "*" for c in safe_expr):
            return f"❌ Invalid characters in expression: {expression}"
        result = eval(safe_expr, {"__builtins__": {}, "math": math})  # noqa: S307
        return f"📊 {expression} = {result}"
    except Exception as e:
        return f"❌ Calculation error: {e}"


def percentage(value: float, percent: float) -> str:
    """Calculate a percentage of a value."""
    try:
        result = float(value) * float(percent) / 100
        return f"📊 {percent}% of {value} = {result}"
    except Exception as e:
        return f"❌ Percentage error: {e}"


def compound_growth(principal: float, rate: float, periods: int) -> str:
    """Calculate compound growth: A = P(1 + r)^n"""
    try:
        p = float(principal)
        r = float(rate) / 100  # rate as percentage
        n = int(periods)
        result = p * (1 + r) ** n
        growth = result - p
        return (
            f"📊 Compound Growth:\n"
            f"   Principal: {p:,.2f}\n"
            f"   Rate: {rate}% per period\n"
            f"   Periods: {n}\n"
            f"   Final Value: {result:,.2f}\n"
            f"   Total Growth: {growth:,.2f}"
        )
    except Exception as e:
        return f"❌ Compound growth error: {e}"


def statistics(numbers: str) -> str:
    """Compute basic statistics from a comma-separated list of numbers."""
    try:
        nums = [float(x.strip()) for x in numbers.split(",")]
        mean = sum(nums) / len(nums)
        return (
            f"📊 Statistics:\n"
            f"   Count: {len(nums)}\n"
            f"   Mean:  {mean:.4f}\n"
            f"   Min:   {min(nums)}\n"
            f"   Max:   {max(nums)}\n"
            f"   Sum:   {sum(nums)}"
        )
    except Exception as e:
        return f"❌ Statistics error: {e}"


TOOL_MAP = {
    "calculate":       calculate,
    "percentage":      percentage,
    "compound_growth": compound_growth,
    "statistics":      statistics,
}


def _call_llm(step: str, context: str) -> str:
    prompt = SYSTEM_PROMPT.format(step=step, context=context)
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": f"Execute this calculation step: {step}"}
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
    """Execute a calculation step and return result."""
    try:
        raw  = _call_llm(step, context)
        data = _parse_json(raw)

        tool_name = data.get("name", "done")
        arguments = data.get("arguments", {})

        if tool_name == "done":
            return {"status": "completed", "result": arguments.get("answer", step), "tool": "done"}

        if tool_name not in TOOL_MAP:
            # Fallback: try to extract and calculate expression from step
            result = calculate(step)
            return {"status": "completed", "result": result, "tool": "calculate"}

        result = TOOL_MAP[tool_name](**arguments)
        return {"status": "completed", "result": result, "tool": tool_name}

    except Exception as e:
        return {"status": "error", "result": f"Calculator agent error: {e}", "tool": "none"}
