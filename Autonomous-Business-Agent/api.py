# api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from agent import run_agent
from db import get_logs, get_log_detail, get_reports

app = FastAPI(title="Autonomous Business Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str

    @field_validator("task")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("task must not be empty")
        return v


@app.get("/")
def root():
    return {"status": "Autonomous Business Agent is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/run")
def run_task(request: TaskRequest):
    """Run a multi-step business task autonomously."""
    result = run_agent(request.task)
    return result


@app.get("/logs")
def list_logs(limit: int = 20):
    """List recent execution logs."""
    return {"logs": get_logs(limit)}


@app.get("/logs/{log_id}")
def get_log(log_id: int):
    """Get full detail of a specific execution log."""
    log = get_log_detail(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@app.get("/reports")
def list_reports(limit: int = 20):
    """List saved business reports."""
    return {"reports": get_reports(limit)}
