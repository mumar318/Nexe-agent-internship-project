# main.py

import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

from tools import add, subtract, multiply, divide, power, square_root, store_memory, recall_memory
from db import save_log

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Map tool names to functions
function_map = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
    "square_root": square_root,
    "store_memory": store_memory,
    "recall_memory": recall_memory,
}

SYSTEM_PROMPT = """
You are a strict tool-calling AI Calculator.

RULES:
- DO NOT write code
- DO NOT explain anything
- ONLY return JSON
- NO markdown (no ```)

AVAILABLE TOOLS:
- add(a, b)           → adds two numbers
- subtract(a, b)      → subtracts b from a
- multiply(a, b)      → multiplies two numbers
- divide(a, b)        → divides a by b
- power(base, exponent) → raises base to the power of exponent
- square_root(a)      → returns the square root of a
- store_memory(value) → saves a number to memory
- recall_memory()     → retrieves the last saved number from memory

RESPONSE FORMAT (always return exactly this):
{
  "name": "tool_name",
  "arguments": {}
}

For tools with no arguments (like recall_memory), use: "arguments": {}
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
