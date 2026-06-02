# app.py — works on Streamlit Cloud (direct agent call, no FastAPI needed)

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Autonomous Business Agent", page_icon="🏢", layout="wide")
st.title("🏢 Autonomous Business Agent")
st.caption("Multi-step reasoning · Task planning · Execution logs — powered by Groq LLaMA")
st.divider()

def _get(key):
    try: return st.secrets[key]
    except Exception: return os.getenv(key, "")

for k in ["GROQ_API_KEY","SERPAPI_KEY","EMAIL_ADDRESS","EMAIL_PASSWORD"]:
    val = _get(k)
    if val: os.environ[k] = val

tab1, tab2, tab3 = st.tabs(["🚀 Run Task","📋 Execution Logs","📄 Reports"])

with tab1:
    with st.expander("💡 Example tasks"):
        st.markdown("""
- `Research the latest trends in AI and save a report`
- `Calculate the ROI: revenue is 50000, cost is 30000, then save the result`
- `Search for top 3 project management tools and send a summary to nexeagent@gmail.com`
""")
    task_input = st.text_area("Enter your business task:", height=100)
    run_btn = st.button("🚀 Run Agent", type="primary", use_container_width=True)

    if run_btn:
        if not task_input.strip():
            st.warning("⚠️ Please enter a task.")
        else:
            with st.spinner("🤖 Agent is planning and executing..."):
                try:
                    from agent import run_agent
                    data = run_agent(task_input)
                    st.divider()
                    st.success(f"✅ Completed — Log ID: {data.get('log_id')}")
                    st.subheader("📋 Plan")
                    for i,s in enumerate(data.get("plan",[]),1): st.markdown(f"**{i}.** {s}")
                    st.divider()
                    st.subheader("⚙️ Steps")
                    for step in data.get("steps",[]):
                        icon = "✅" if step["status"]=="completed" else "❌"
                        with st.expander(f"{icon} Step {step['step_number']}: {step['step_description']}"):
                            if step.get("tool_used"): st.markdown(f"**Tool:** `{step['tool_used']}`")
                            if step.get("tool_output"): st.markdown(str(step["tool_output"]))
                    st.divider()
                    st.subheader("💡 Final Answer")
                    st.markdown(data.get("final_answer",""))
                    with st.expander("🔍 Raw JSON"): st.json(data)
                except Exception as e:
                    st.error(f"❌ {e}")

with tab2:
    st.subheader("📋 Execution Logs")
    if st.button("🔄 Refresh", key="rl"): st.rerun()
    try:
        from db import get_logs, get_log_detail
        logs = get_logs(20)
        if not logs: st.info("No executions yet.")
        else:
            for log in logs:
                icon = "✅" if log["status"]=="success" else "⚠️"
                with st.expander(f"{icon} [{log['id']}] {log['task'][:80]}"):
                    st.markdown(f"**Status:** `{log['status']}`")
                    st.markdown(f"**Answer:** {log['final_answer'][:300]}")
    except Exception as e: st.error(f"❌ {e}")

with tab3:
    st.subheader("📄 Reports")
    if st.button("🔄 Refresh", key="rr"): st.rerun()
    try:
        from db import get_reports
        reports = get_reports(20)
        if not reports: st.info("No reports yet.")
        else:
            for r in reports:
                with st.expander(f"📄 {r['title']}  —  {r['timestamp'][:19]}"): st.markdown(r["content"])
    except Exception as e: st.error(f"❌ {e}")
