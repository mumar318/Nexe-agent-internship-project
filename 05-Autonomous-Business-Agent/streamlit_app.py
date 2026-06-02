# streamlit_app.py — Streamlit Cloud entry point for Autonomous Business Agent
# Runs agent logic directly — no FastAPI server needed.

import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Autonomous Business Agent", page_icon="🏢", layout="wide")
st.title("🏢 Autonomous Business Agent")
st.caption("Multi-step reasoning · Task planning · Execution logs — powered by Groq LLaMA")
st.divider()

def _get(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, "")

# Inject secrets as env vars before importing agent modules
for k in ["GROQ_API_KEY", "SERPAPI_KEY", "EMAIL_ADDRESS", "EMAIL_PASSWORD"]:
    val = _get(k)
    if val:
        os.environ[k] = val

tab1, tab2, tab3 = st.tabs(["🚀 Run Task", "📋 Execution Logs", "📄 Reports"])

# ── Tab 1: Run Task ────────────────────────────────────────────────────────────
with tab1:
    with st.expander("💡 Example tasks"):
        st.markdown("""
- `Research the latest trends in AI and save a report`
- `Search for Python FastAPI best practices and summarize the findings`
- `Calculate the ROI: revenue is 50000, cost is 30000, then save the result`
- `Search for top 3 project management tools and send a summary to nexeagent@gmail.com`
- `Find information about machine learning and create a business report`
""")

    task_input = st.text_area("Enter your business task:",
                              placeholder="e.g. Research AI trends and save a report", height=100)
    run_btn = st.button("🚀 Run Agent", type="primary", use_container_width=True)

    if run_btn:
        if not task_input.strip():
            st.warning("⚠️ Please enter a task.")
        else:
            with st.spinner("🤖 Agent is planning and executing your task..."):
                try:
                    from agent import run_agent
                    data = run_agent(task_input)

                    st.divider()
                    status = data.get("status", "success")
                    if status == "success":
                        st.success(f"✅ Task completed — Log ID: {data.get('log_id')}")
                    else:
                        st.warning(f"⚠️ Partial completion — Log ID: {data.get('log_id')}")

                    st.subheader("📋 Execution Plan")
                    for i, step in enumerate(data.get("plan", []), 1):
                        st.markdown(f"**{i}.** {step}")

                    st.divider()
                    st.subheader("⚙️ Execution Steps")
                    for step in data.get("steps", []):
                        icon = "✅" if step["status"] == "completed" else "❌"
                        with st.expander(f"{icon} Step {step['step_number']}: {step['step_description']}"):
                            if step.get("tool_used"):
                                st.markdown(f"**Tool:** `{step['tool_used']}`")
                            if step.get("tool_input"):
                                st.json(step["tool_input"])
                            if step.get("tool_output"):
                                st.markdown(str(step["tool_output"]))

                    st.divider()
                    st.subheader("💡 Final Answer")
                    st.markdown(data.get("final_answer", "No answer generated."))

                    with st.expander("🔍 Raw JSON"):
                        st.json(data)

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.info("Make sure all API keys are set in Streamlit Cloud secrets.")

# ── Tab 2: Execution Logs ──────────────────────────────────────────────────────
with tab2:
    st.subheader("📋 Recent Execution Logs")
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()
    try:
        from db import get_logs, get_log_detail
        logs = get_logs(20)
        if not logs:
            st.info("No executions yet. Run a task first.")
        else:
            for log in logs:
                icon = "✅" if log["status"] == "success" else "⚠️"
                with st.expander(f"{icon} [{log['id']}] {log['task'][:80]}  —  {log['timestamp'][:19]}"):
                    st.markdown(f"**Status:** `{log['status']}`")
                    st.markdown(f"**Answer:** {log['final_answer'][:300]}")
                    detail = get_log_detail(log["id"])
                    if detail:
                        for i, s in enumerate(detail.get("plan", []), 1):
                            st.markdown(f"  {i}. {s}")
    except Exception as e:
        st.error(f"Failed to load logs: {e}")

# ── Tab 3: Reports ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📄 Saved Business Reports")
    if st.button("🔄 Refresh Reports", use_container_width=True):
        st.rerun()
    try:
        from db import get_reports
        reports = get_reports(20)
        if not reports:
            st.info("No reports saved yet.")
        else:
            for r in reports:
                with st.expander(f"📄 [{r['id']}] {r['title']}  —  {r['timestamp'][:19]}"):
                    st.markdown(r["content"])
    except Exception as e:
        st.error(f"Failed to load reports: {e}")
