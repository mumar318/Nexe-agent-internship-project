from fastapi import FastAPI
from pydantic import BaseModel
from main import run_agent
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request format
class Request(BaseModel):
    query: str

# Health check endpoint (Railway needs this)
@app.get("/")
def root():
    return {"status": "AI Tool Calling Agent is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# API endpoint
@app.post("/chat")
def chat(request: Request):
    return run_agent(request.query)
