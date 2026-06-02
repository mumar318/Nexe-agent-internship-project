# app.py

import streamlit as st
import requests
import os
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Calculator Agent",
    page_icon="🧮",
    layout="centered"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧮 AI Calculator Agent")
st.caption("Powered by Groq LLaMA · Supports math, memory, and natural language")

st.divider()

# ── Example queries ───────────────────────────────────────────────────────────
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

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.text_input(
    "Enter your query:",
    placeholder="e.g. What is 15 multiplied by 8?"
)

calculate_btn = st.button("Calculate", type="primary", use_container_width=True)

# ── Logic ─────────────────────────────────────────────────────────────────────
if calculate_btn:
    if not user_input.strip():
        st.warning("⚠️ Please enter a query first.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"query": user_input},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                st.divider()

                if "result" in data:
                    st.success("✅ Result")
                    st.metric(label=f"Tool used: `{data.get('tool_used', 'N/A')}`", value=str(data["result"]))

                elif "error" in data:
                    st.error(f"❌ Error: {data['error']}")

                else:
                    st.info("Response received:")
                    st.json(data)

                # Raw JSON expandable
                with st.expander("🔍 Raw JSON response"):
                    st.json(data)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API server. Make sure FastAPI is running on port 8000.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except requests.exceptions.HTTPError as e:
                st.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
