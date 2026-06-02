# streamlit_app.py — Streamlit Cloud entry point for AI Calculator Agent
# Runs agent logic directly — no FastAPI server needed.

import streamlit as st
import os, json, re, math
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Calculator Agent", page_icon="🧮", layout="centered")
st.title("🧮 AI Calculator Agent")
st.caption("8 math tools · In-session memory — powered by Groq LLaMA")
st.divider()

# In-session memory (persists across reruns via st.session_state)
if "memory" not in st.session_state:
    st.session_state.memory = None

with st.expander("💡 Example queries"):
    st.markdown("""
- `Add 25 and 37`
- `Subtract 100 from 250`
- `Multiply 12 by 15`
- `Divide 144 by 12`
- `2 to the power of 10`
- `Square root of 225`
- `Save 500 to memory`
- `Recall my saved value`
- `Recall my saved value and multiply it by 3`
""")

if st.session_state.memory is not None:
    st.info(f"💾 Memory: `{st.session_state.memory}`")

user_input = st.text_input("Enter your query:", placeholder="e.g. What is 15 multiplied by 8?")
calc_btn = st.button("Calculate", type="primary", use_container_width=True)

if calc_btn:
    if not user_input.strip():
        st.warning("⚠️ Please enter a query first.")
    else:
        with st.spinner("Thinking..."):
            try:
                from groq import Groq

                def _get(key):
                    try:
                        return st.secrets[key]
                    except Exception:
                        return os.getenv(key, "")

                client = Groq(api_key=_get("GROQ_API_KEY"))

                SYSTEM_PROMPT = """You are a strict tool-calling AI Calculator.
RULES: ONLY return JSON. NO markdown. NO explanation.
TOOLS:
- add(a, b)             → adds two numbers
- subtract(a, b)        → subtracts b from a
- multiply(a, b)        → multiplies two numbers
- divide(a, b)          → divides a by b
- power(base, exponent) → raises base to the power of exponent
- square_root(a)        → square root of a
- store_memory(value)   → saves a number to memory
- recall_memory()       → retrieves last saved number
FORMAT: {"name": "tool_name", "arguments": {}}
For recall_memory use: "arguments": {}"""

                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_input}
                    ]
                )
                message = resp.choices[0].message.content.strip()
                cleaned = re.sub(r"```(?:json)?", "", message, flags=re.IGNORECASE).replace("```", "").strip()
                data    = json.loads(cleaned)
                tool    = data.get("name", "")
                args    = data.get("arguments", {})

                # Execute tool
                result = None
                if tool == "add":
                    result = float(args["a"]) + float(args["b"])
                elif tool == "subtract":
                    result = float(args["a"]) - float(args["b"])
                elif tool == "multiply":
                    result = float(args["a"]) * float(args["b"])
                elif tool == "divide":
                    b = float(args["b"])
                    result = "❌ Division by zero" if b == 0 else float(args["a"]) / b
                elif tool == "power":
                    result = math.pow(float(args["base"]), float(args["exponent"]))
                elif tool == "square_root":
                    a = float(args["a"])
                    result = "❌ Cannot take sqrt of negative number" if a < 0 else math.sqrt(a)
                elif tool == "store_memory":
                    val = float(args["value"])
                    st.session_state.memory = val
                    result = f"✅ Value {val} saved to memory."
                elif tool == "recall_memory":
                    result = st.session_state.memory if st.session_state.memory is not None else "⚠️ No value stored yet."
                else:
                    result = f"Unknown tool: {tool}"

                st.divider()
                st.success("✅ Result")
                st.metric(label=f"Tool: `{tool}`", value=str(result))
                with st.expander("🔍 Raw response"):
                    st.json({"tool_used": tool, "input": args, "result": str(result)})

            except json.JSONDecodeError:
                st.error("❌ Could not parse LLM response as JSON.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
