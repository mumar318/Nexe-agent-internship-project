# coordinator.py — Top-level entry point that wires everything together.
# Creates a fresh MessageBus per request, runs the orchestrator,
# persists the task log, and returns the full result.

from communication.message_bus import MessageBus
from agents.orchestrator import run_orchestrator


def run_system(task: str) -> dict:
    """
    Run the full multi-agent pipeline for a given task.

    Returns a dict with:
      - task, plan, steps, final_answer
      - message_history (all inter-agent messages)
      - log_id
      - status
    """
    bus = MessageBus()

    # Run orchestrator (which delegates to specialist agents via the bus)
    result = run_orchestrator(task, bus)

    # Determine overall status
    statuses = [s.get("status", "completed") for s in result.get("steps", [])]
    status   = "partial" if "error" in statuses else "success"

    # Persist task log
    log_id = bus.save_task_log(
        task         = task,
        plan         = result["plan"],
        steps        = result["steps"],
        final_answer = result["final_answer"],
        status       = status
    )

    return {
        "task":            task,
        "plan":            result["plan"],
        "steps":           result["steps"],
        "final_answer":    result["final_answer"],
        "message_history": bus.get_history(),
        "log_id":          log_id,
        "status":          status,
    }
