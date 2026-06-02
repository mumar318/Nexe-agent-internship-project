# streamlit_app.py — Streamlit Cloud entry point
# Runs the agent logic directly (no separate FastAPI server needed).
# Used for deployment on Streamlit Cloud.

import streamlit as st
import os
import json

st.set_page_config(
    page_title="Multi-Agent System",
    page_icon="🤝",
    layout="wide"
)

# ── Agent colour map ───────────────────────────────────────────────────────────
AGENT_COLORS = {
    "orchestrator":    "🎯",
    "research_agent":  "🔍",
    "writer_agent":    "✍️",
    "email_agent":     "📧",
    "calculator_agent":"🔢",
    "broadcast":       "📢",
}

def agent_icon(name: str) -> str:
    return AGENT_COLORS.get(name, "🤖")


# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤝 Multi-Agent System")
st.caption("Orchestrator · Research · Writer · Email · Calculator — powered by Groq LLaMA")
st.divider()

tabs = st.tabs(["🚀 Run Task", "📋 Task Logs", "💬 Message Bus", "📄 Reports"])

# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: Run Task
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    with st.expander("💡 Example tasks"):
        st.markdown("""
- `Research the latest trends in AI and save a report`
- `Search for Python best practices, summarize them, and send a report to nexeagent@gmail.com`
- `Calculate the ROI if revenue is 80000 and cost is 50000, then save the result as a report`
- `Find information about machine learning, write a business report, and email it to nexeagent@gmail.com`
- `Search for top project management tools and format the results as bullet points`
- `Calculate compound growth: 10000 principal, 8% rate, 5 periods, then save a report`
""")

    task_input = st.text_area(
        "Enter your task:",
        placeholder="e.g. Research AI trends, write a report, and email it to nexeagent@gmail.com",
        height=100
    )
    run_btn = st.button("🚀 Run Multi-Agent Task", type="primary", use_container_width=True)

    if run_btn:
        if not task_input.strip():
            st.warning("⚠️ Please enter a task.")
        else:
            with st.spinner("🤖 Agents are collaborating on your task..."):
                try:
                    from coordinator import run_system
                    data = run_system(task_input)

                    st.divider()

                    # Status
                    status = data.get("status", "unknown")
                    if status == "success":
                        st.success(f"✅ Task completed — Log ID: {data.get('log_id')}")
                    else:
                        st.warning(f"⚠️ Task completed with partial errors — Log ID: {data.get('log_id')}")

                    # Plan
                    st.subheader("📋 Execution Plan")
                    plan = data.get("plan", [])
                    if plan:
                        cols = st.columns(min(len(plan), 3))
                        for i, item in enumerate(plan):
                            col   = cols[i % len(cols)]
                            agent = item.get("agent", "")
                            with col:
                                st.info(
                                    f"{agent_icon(agent)} **Step {i+1}**\n\n"
                                    f"{item.get('step','')}\n\n*→ {agent}*"
                                )

                    st.divider()

                    # Step-by-step execution
                    st.subheader("⚙️ Agent Execution")
                    for step in data.get("steps", []):
                        icon   = "✅" if step["status"] == "completed" else "❌"
                        agent  = step.get("assigned_agent", "")
                        a_icon = agent_icon(agent)
                        with st.expander(
                            f"{icon} Step {step['step_number']}: "
                            f"{step['step_description']}  — {a_icon} `{agent}`"
                        ):
                            if step.get("result"):
                                st.markdown("**Result:**")
                                st.markdown(str(step["result"]))

                    st.divider()

                    # Final answer
                    st.subheader("💡 Final Answer")
                    st.markdown(data.get("final_answer", "No answer generated."))

                    # Agent communication summary
                    history = data.get("message_history", [])
                    if history:
                        with st.expander(f"💬 Agent Communication ({len(history)} messages)"):
                            for msg in history:
                                sender    = msg.get("sender", "")
                                recipient = msg.get("recipient", "")
                                mtype     = msg.get("msg_type", "")
                                st.markdown(
                                    f"`{msg.get('timestamp','')[:19]}` "
                                    f"{agent_icon(sender)} **{sender}** → "
                                    f"{agent_icon(recipient)} **{recipient}** "
                                    f"[`{mtype}`]"
                                )

                    with st.expander("🔍 Raw JSON response"):
                        st.json(data)

                except Exception as e:
                    st.error(f"❌ Error running agent: {e}")
                    st.info("Make sure all API keys are set in Streamlit Cloud secrets.")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: Task Logs
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("📋 Task Execution Logs")
    if st.button("🔄 Refresh Logs", use_container_width=True, key="refresh_logs"):
        st.rerun()

    try:
        from communication.message_bus import MessageBus
        bus  = MessageBus()
        logs = bus.get_task_logs(20)

        if not logs:
            st.info("No tasks run yet. Use the Run Task tab.")
        else:
            for log in logs:
                icon = "✅" if log["status"] == "success" else "⚠️"
                with st.expander(
                    f"{icon} [{log['id']}] {log['task'][:80]}  —  {log['timestamp'][:19]}"
                ):
                    st.markdown(f"**Status:** `{log['status']}`")
                    st.markdown(f"**Final Answer:** {log['final_answer'][:300]}")
                    detail = bus.get_task_log_detail(log["id"])
                    if detail:
                        st.markdown("**Plan:**")
                        for i, item in enumerate(detail.get("plan", []), 1):
                            agent = item.get("agent", "")
                            st.markdown(
                                f"  {i}. {agent_icon(agent)} `{agent}` — {item.get('step','')}"
                            )
                        st.markdown("**Steps:**")
                        for step in detail.get("steps", []):
                            s_icon = "✅" if step["status"] == "completed" else "❌"
                            st.markdown(
                                f"  {s_icon} Step {step['step_number']} "
                                f"[{agent_icon(step.get('assigned_agent',''))} "
                                f"`{step.get('assigned_agent','')}`]: "
                                f"{str(step.get('result',''))[:120]}"
                            )
    except Exception as e:
        st.error(f"Failed to load logs: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: Message Bus
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("💬 Inter-Agent Message Bus")
    st.caption("Live view of all messages exchanged between agents")

    if st.button("🔄 Refresh Messages", use_container_width=True, key="refresh_msgs"):
        st.rerun()

    try:
        from communication.message_bus import MessageBus
        bus      = MessageBus()
        messages = bus.get_message_log(100)

        if not messages:
            st.info("No messages yet. Run a task to see agent communication.")
        else:
            all_types = list({m["msg_type"] for m in messages})
            selected  = st.multiselect("Filter by message type:", all_types, default=all_types)
            filtered  = [m for m in messages if m["msg_type"] in selected]

            st.markdown(f"**{len(filtered)} messages**")
            st.divider()

            color_map = {
                "task_plan":       "🟦",
                "task_delegation": "🟨",
                "task_result":     "🟩",
                "task_complete":   "🟪",
                "error":           "🟥",
            }

            for msg in filtered:
                sender    = msg.get("sender", "")
                recipient = msg.get("recipient", "")
                mtype     = msg.get("msg_type", "")
                ts        = msg.get("timestamp", "")[:19]
                dot       = color_map.get(mtype, "⬜")

                with st.expander(
                    f"{dot} `{ts}` {agent_icon(sender)} **{sender}** → "
                    f"{agent_icon(recipient)} **{recipient}** [`{mtype}`]"
                ):
                    payload = msg.get("payload", {})
                    if "step"   in payload: st.markdown(f"**Step:** {payload['step']}")
                    if "result" in payload: st.markdown(f"**Result:** {str(payload['result'])[:400]}")
                    if "tool"   in payload: st.markdown(f"**Tool used:** `{payload['tool']}`")
                    if "plan"   in payload:
                        st.markdown("**Plan:**")
                        for i, item in enumerate(payload["plan"], 1):
                            st.markdown(
                                f"  {i}. {item.get('step','')} → `{item.get('agent','')}`"
                            )
                    with st.expander("Full payload"):
                        st.json(payload)

    except Exception as e:
        st.error(f"Failed to load messages: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# Tab 4: Reports
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("📄 Saved Reports")
    if st.button("🔄 Refresh Reports", use_container_width=True, key="refresh_reports"):
        st.rerun()

    try:
        from communication.message_bus import MessageBus
        bus     = MessageBus()
        reports = bus.get_reports(20)

        if not reports:
            st.info("No reports saved yet. Ask the writer agent to save a report.")
        else:
            for r in reports:
                with st.expander(
                    f"📄 [{r['id']}] {r['title']}  —  {r['timestamp'][:19]}"
                ):
                    st.markdown(r["content"])

    except Exception as e:
        st.error(f"Failed to load reports: {e}")
