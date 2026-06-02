# app.py — Streamlit UI for Autonomous Business Agent

import streamlit as st
import requests
import os
import json

st.set_page_config(
    page_title="Autonomous Business Agent",
    page_icon="🏢",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8004")

st.title("🏢 Autonomous Business Agent")
st.caption("Multi-step reasoning · Task planning · Execution logs — powered by Groq LLaMA")
st.divider()

tab1, tab2, tab3 = st.tabs(["🚀 Run Task", "📋 Execution Logs", "📄 Reports"])

# ─────────────────────────────────────────────────────────────────────────────
# Tab 1: Run Task
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    with st.expander("💡 Example tasks"):
        st.markdown("""
- `Research the latest trends in AI and save a report`
- `Search for Python FastAPI best practices and summarize the findings`
- `Calculate the ROI: revenue is 50000, cost is 30000, then save the result`
- `Search for top 3 project management tools and send a summary to nexeagent@gmail.com`
- `Find information about machine learning and create a business report`
""")

    task_input = st.text_area(
        "Enter your business task:",
        placeholder="e.g. Research AI trends, summarize findings, and save a report",
        height=100
    )
    run_btn = st.button("🚀 Run Agent", type="primary", use_container_width=True)

    if run_btn:
        if not task_input.strip():
            st.warning("⚠️ Please enter a task.")
        else:
            with st.spinner("🤖 Agent is planning and executing your task..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/run",
                        json={"task": task_input},
                        timeout=120
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    st.divider()

                    # Status badge
                    status = data.get("status", "unknown")
                    if status == "success":
                        st.success(f"✅ Task completed — Log ID: {data.get('log_id')}")
                    else:
                        st.warning(f"⚠️ Task completed with partial errors — Log ID: {data.get('log_id')}")

                    # Plan
                    st.subheader("📋 Execution Plan")
                    for i, step in enumerate(data.get("plan", []), 1):
                        st.markdown(f"**{i}.** {step}")

                    st.divider()

                    # Step-by-step execution
                    st.subheader("⚙️ Execution Steps")
                    for step in data.get("steps", []):
                        icon = "✅" if step["status"] == "completed" else "❌"
                        with st.expander(f"{icon} Step {step['step_number']}: {step['step_description']}"):
                            if step.get("tool_used"):
                                st.markdown(f"**Tool:** `{step['tool_used']}`")
                            if step.get("tool_input"):
                                st.markdown("**Input:**")
                                st.json(step["tool_input"])
                            if step.get("tool_output"):
                                st.markdown("**Output:**")
                                st.markdown(str(step["tool_output"]))

                    st.divider()

                    # Final answer
                    st.subheader("💡 Final Answer")
                    st.markdown(data.get("final_answer", "No answer generated."))

                    # Raw JSON
                    with st.expander("🔍 Raw JSON response"):
                        st.json(data)

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure FastAPI is running on port 8004.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The agent may still be running.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP {e.response.status_code}: {e.response.text}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Tab 2: Execution Logs
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("📋 Recent Execution Logs")
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()

    try:
        resp = requests.get(f"{API_URL}/logs", timeout=10)
        resp.raise_for_status()
        logs = resp.json().get("logs", [])

        if not logs:
            st.info("No executions yet. Run a task first.")
        else:
            for log in logs:
                status_icon = "✅" if log["status"] == "success" else "⚠️"
                with st.expander(f"{status_icon} [{log['id']}] {log['task'][:80]}  —  {log['timestamp']}"):
                    st.markdown(f"**Status:** {log['status']}")
                    st.markdown(f"**Final Answer:** {log['final_answer']}")

                    # Load full detail
                    try:
                        detail_resp = requests.get(f"{API_URL}/logs/{log['id']}", timeout=10)
                        detail = detail_resp.json()
                        st.markdown("**Plan:**")
                        for i, s in enumerate(detail.get("plan", []), 1):
                            st.markdown(f"  {i}. {s}")
                        st.markdown("**Steps:**")
                        for step in detail.get("steps", []):
                            icon = "✅" if step["status"] == "completed" else "❌"
                            st.markdown(f"  {icon} Step {step['step_number']}: `{step.get('tool_used','—')}` — {str(step.get('tool_output',''))[:100]}")
                    except Exception:
                        pass

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API.")
    except Exception as e:
        st.error(f"Failed to load logs: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Tab 3: Reports
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📄 Saved Business Reports")
    if st.button("🔄 Refresh Reports", use_container_width=True):
        st.rerun()

    try:
        resp = requests.get(f"{API_URL}/reports", timeout=10)
        resp.raise_for_status()
        reports = resp.json().get("reports", [])

        if not reports:
            st.info("No reports saved yet. Ask the agent to save a report.")
        else:
            for r in reports:
                with st.expander(f"📄 [{r['id']}] {r['title']}  —  {r['timestamp']}"):
                    st.markdown(r["content"])

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API.")
    except Exception as e:
        st.error(f"Failed to load reports: {e}")
