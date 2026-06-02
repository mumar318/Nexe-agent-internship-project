# agents/orchestrator.py — Orchestrator Agent
# Receives the user task, plans it, delegates each step to the right specialist agent,
# collects results through the communication layer, and synthesises a final answer.

import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

from communication.message_bus import MessageBus
from communication.messages import Message, MessageType
from config import get

load_dotenv()
client = Groq(api_key=get("GROQ_API_KEY"))

AGENT_ID = "orchestrator"

# ── Planner prompt ─────────────────────────────────────────────────────────────
PLANNER_PROMPT = """You are a task orchestrator. Break the user's task into clear, ordered steps.
Assign each step to the most suitable agent.

AVAILABLE AGENTS:
- research_agent   → web search, information gathering, summarising
- writer_agent     → drafting reports, formatting content, writing documents
- email_agent      → composing and sending emails
- calculator_agent → math calculations, numeric analysis

Return ONLY a JSON array. No markdown, no explanation.

Format:
[
  {"step": "description of step", "agent": "agent_name"},
  ...
]

Maximum 6 steps. Keep steps concise and actionable.
"""

# ── Synthesiser prompt ─────────────────────────────────────────────────────────
SYNTHESISER_PROMPT = """You are a helpful business assistant.
Given the original task and the results from each execution step,
write a concise, professional final summary for the user.
Be direct and informative. No fluff."""


def _call_llm(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ]
    )
    return resp.choices[0].message.content.strip()


def _parse_json(text: str):
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "").strip()
    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
    return json.loads(cleaned)


def run_orchestrator(task: str, bus: MessageBus) -> dict:
    """
    1. Plan the task into delegated steps
    2. Send delegation messages to specialist agents via the bus
    3. Collect results
    4. Synthesise final answer
    """
    execution_steps = []
    context_parts   = []

    # ── Step 1: Plan ────────────────────────────────────────────────────────────
    try:
        plan_raw = _call_llm(PLANNER_PROMPT, f"Task: {task}")
        plan     = _parse_json(plan_raw)
        if not isinstance(plan, list):
            plan = [{"step": str(plan), "agent": "research_agent"}]
    except Exception:
        plan = [{"step": f"Execute task: {task}", "agent": "research_agent"}]

    # Announce plan on the bus
    bus.publish(Message(
        sender=AGENT_ID,
        recipient="broadcast",
        msg_type=MessageType.TASK_PLAN,
        payload={"task": task, "plan": plan}
    ))

    # ── Step 2: Delegate each step ──────────────────────────────────────────────
    for i, item in enumerate(plan, 1):
        step_desc  = item.get("step", "")
        target     = item.get("agent", "research_agent")

        step_log = {
            "step_number":       i,
            "step_description":  step_desc,
            "assigned_agent":    target,
            "result":            None,
            "status":            "pending"
        }

        # Send delegation message
        context_str = "\n".join(context_parts[-3:])
        delegation_msg = Message(
            sender=AGENT_ID,
            recipient=target,
            msg_type=MessageType.TASK_DELEGATION,
            payload={
                "step":    step_desc,
                "context": context_str,
                "task":    task
            }
        )
        bus.publish(delegation_msg)

        # Receive result (synchronous — agent processes inline)
        result_msg = bus.get_result(target, delegation_msg.msg_id)

        if result_msg:
            result = result_msg.payload.get("result", "No result returned.")
            step_log["result"] = result
            step_log["status"] = result_msg.payload.get("status", "completed")
            context_parts.append(f"Step {i} ({target}): {result}")
        else:
            step_log["result"] = "Agent did not respond."
            step_log["status"] = "error"

        execution_steps.append(step_log)

    # ── Step 3: Synthesise ──────────────────────────────────────────────────────
    synthesis_input = f"Task: {task}\n\nExecution results:\n" + "\n".join(context_parts)
    try:
        final_answer = _call_llm(SYNTHESISER_PROMPT, synthesis_input)
    except Exception:
        final_answer = context_parts[-1] if context_parts else "Task completed."

    # Publish completion
    bus.publish(Message(
        sender=AGENT_ID,
        recipient="broadcast",
        msg_type=MessageType.TASK_COMPLETE,
        payload={"task": task, "final_answer": final_answer}
    ))

    return {
        "task":         task,
        "plan":         plan,
        "steps":        execution_steps,
        "final_answer": final_answer,
    }
