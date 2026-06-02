import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

from tools import add, multiply, get_weather
from db import save_log

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Map tool functions
function_map = {
    "add": add,
    "multiply": multiply,
    "get_weather": get_weather
}

# ➤ System prompt (INSIDE FUNCTION ONLY)

def run_agent(user_input):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a strict tool-calling AI.

RULES:
- DO NOT write code
- DO NOT explain
- ONLY return JSON
- NO markdown (no ```)

TOOLS:
- add(a, b)
- multiply(a, b)
- get_weather(city)

FORMAT:
{
  "name": "tool_name",
  "arguments": {}
}
"""
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        # Extract response
        message = response.choices[0].message.content.strip()

        # Clean markdown if any
        cleaned = re.sub(r"```.*?```", "", message, flags=re.DOTALL).strip()

        data = json.loads(cleaned)

        # Tool execution
        if "name" in data:
            function_name = data["name"]
            arguments = data["arguments"]

            result = function_map[function_name](**arguments)

            output = {
                "tool_used": function_name,
                "input": arguments,
                "result": result
            }
        else:
            output = {"response": data}

        # Save logs
        save_log(user_input, output)

        return output

    except Exception as e:
        return {
            "error": f"Parsing failed: {str(e)}",
            "raw_response": message if 'message' in locals() else None
        }