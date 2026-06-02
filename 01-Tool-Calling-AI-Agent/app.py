# app.py — works both locally (calls FastAPI) and on Streamlit Cloud (direct)

import streamlit as st
import os, json, re

st.set_page_config(page_title="AI Tool Calling Agent", page_icon="🤖", layout="centered")
st.title("🤖 AI Tool Calling Agent")
st.caption("Math operations · Real-time weather — powered by Groq LLaMA")
st.divider()

with st.expander("💡 Example queries"):
    st.markdown("""
- `What is 25 plus 38?`
- `Multiply 12 by 15`
- `What's the weather in Lahore?`
- `What is the weather in London today?`
""")

user_input = st.text_input("Enter your query:", placeholder="e.g. What is the weather in Karachi?")
run_btn = st.button("Run", type="primary", use_container_width=True)

def _get(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")

if run_btn:
    if not user_input.strip():
        st.warning("⚠️ Please enter a query first.")
    else:
        with st.spinner("Thinking..."):
            try:
                from groq import Groq
                import requests as http_requests
                from dotenv import load_dotenv
                load_dotenv()

                client = Groq(api_key=_get("GROQ_API_KEY"))

                SYSTEM_PROMPT = """You are a strict tool-calling AI.
RULES: DO NOT write code. DO NOT explain. ONLY return JSON. NO markdown.
TOOLS:
- add(a, b)
- multiply(a, b)
- get_weather(city)
FORMAT: {"name": "tool_name", "arguments": {}}"""

                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_input}
                    ]
                )
                message = resp.choices[0].message.content.strip()
                cleaned = re.sub(r"```(?:json)?", "", message, flags=re.IGNORECASE).replace("```", "").strip()
                data     = json.loads(cleaned)
                tool     = data.get("name", "")
                args     = data.get("arguments", {})

                result = None
                if tool == "add":
                    result = float(args["a"]) + float(args["b"])
                elif tool == "multiply":
                    result = float(args["a"]) * float(args["b"])
                elif tool == "get_weather":
                    city        = str(args.get("city", "")).title()
                    weather_key = _get("WEATHER_API_KEY")
                    if not weather_key:
                        result = "❌ WEATHER_API_KEY not set in secrets."
                    else:
                        r = http_requests.get(
                            f"http://api.openweathermap.org/data/2.5/weather"
                            f"?q={city}&appid={weather_key}&units=metric",
                            timeout=10
                        ).json()
                        if r.get("cod") != 200:
                            result = f"❌ {r.get('message', 'City not found')}"
                        else:
                            result = (
                                f"🌤️ Weather in {city}:\n"
                                f"🌡️ {r['main']['temp']}°C "
                                f"(feels like {r['main']['feels_like']}°C)\n"
                                f"☁️ {r['weather'][0]['description'].capitalize()}\n"
                                f"💧 Humidity: {r['main']['humidity']}%"
                            )
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
