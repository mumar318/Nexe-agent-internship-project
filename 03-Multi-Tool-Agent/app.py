# app.py

import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Multi-Tool Agent",
    page_icon="🤖",
    layout="centered"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8002")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 Multi-Tool Agent")
st.caption("Web Search · Save to DB · Send Email — powered by Groq LLaMA")
st.divider()

# ── Example queries ───────────────────────────────────────────────────────────
with st.expander("💡 Example queries"):
    st.markdown("""
- `Search for latest AI news`
- `Search what is Python programming language`
- `Save a note titled Project Ideas with content: Build a RAG chatbot`
- `Send an email to someone@gmail.com about the meeting tomorrow`
""")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Chat", "📋 Saved Notes"])

# ── Tab 1: Chat ───────────────────────────────────────────────────────────────
with tab1:
    user_input = st.text_input(
        "Enter your query:",
        placeholder="e.g. Search for latest AI news"
    )
    run_btn = st.button("Run", type="primary", use_container_width=True)

    if run_btn:
        if not user_input.strip():
            st.warning("⚠️ Please enter a query first.")
        else:
            with st.spinner("Working on it..."):
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
                        tool = data.get("tool_used", "")

                        if tool == "web_search":
                            st.success("🔍 Search Results")
                            st.markdown(data["result"])

                        elif tool == "save_note":
                            st.success("💾 Note Saved")
                            st.info(data["result"])

                        elif tool == "send_email":
                            st.success("📧 Email Status")
                            st.info(data["result"])

                        else:
                            st.success("✅ Result")
                            st.write(data["result"])

                    elif "error" in data:
                        st.error(f"❌ {data['error']}")

                    with st.expander("🔍 Raw JSON response"):
                        st.json(data)

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure FastAPI is running on port 8002.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP {e.response.status_code}: {e.response.text}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

# ── Tab 2: Saved Notes ────────────────────────────────────────────────────────
with tab2:
    st.subheader("📋 All Saved Notes")
    refresh = st.button("🔄 Refresh", use_container_width=True)

    if refresh or True:
        try:
            resp = requests.get(f"{API_URL}/notes", timeout=10)
            resp.raise_for_status()
            notes = resp.json()

            if not notes:
                st.info("No notes saved yet. Use the Chat tab to save one.")
            else:
                for note in notes:
                    with st.expander(f"📌 {note['title']}  —  {note['timestamp']}"):
                        st.write(note["content"])

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure FastAPI is running.")
        except Exception as e:
            st.error(f"Failed to load notes: {e}")
