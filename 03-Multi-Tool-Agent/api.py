# api.py

from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from main import run_agent
from db import get_all_notes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Multi-Tool Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Request(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be empty")
        return v


@app.get("/")
def root():
    return {"status": "Multi-Tool Agent is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: Request):
    return run_agent(request.query)


@app.get("/notes")
def notes():
    """Return all saved notes from the database."""
    rows = get_all_notes()
    return [
        {"id": r[0], "title": r[1], "content": r[2], "timestamp": r[3]}
        for r in rows
    ]
