# api.py — FastAPI backend for the Multi-Agent System

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from coordinator import run_system
from communication.message_bus import MessageBus

app = FastAPI(title="Multi-Agent System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared bus instance for read-only queries (logs, reports, messages)
_bus = MessageBus()


class TaskRequest(BaseModel):
    task: str

    @field_validator("task")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("task must not be empty")
        return v


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Multi-Agent System is running!", "agents": [
        "orchestrator", "research_agent", "writer_agent",
        "email_agent", "calculator_agent"
    ]}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Core: run a task ───────────────────────────────────────────────────────────
@app.post("/run")
def run_task(request: TaskRequest):
    """Submit a task to the multi-agent system."""
    result = run_system(request.task)
    return result


# ── Task logs ──────────────────────────────────────────────────────────────────
@app.get("/logs")
def list_logs(limit: int = 20):
    return {"logs": _bus.get_task_logs(limit)}


@app.get("/logs/{log_id}")
def get_log(log_id: int):
    log = _bus.get_task_log_detail(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


# ── Message history ────────────────────────────────────────────────────────────
@app.get("/messages")
def list_messages(limit: int = 50):
    """Return recent inter-agent messages (communication layer visibility)."""
    return {"messages": _bus.get_message_log(limit)}


# ── Reports ────────────────────────────────────────────────────────────────────
@app.get("/reports")
def list_reports(limit: int = 20):
    return {"reports": _bus.get_reports(limit)}
