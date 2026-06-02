# api.py

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from rag_chain import answer_question
from vector_store import ingest_document, list_documents, delete_document

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="RAG Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question must not be empty")
        return v


@app.get("/")
def root():
    return {"status": "RAG Assistant is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT document and ingest it into the vector store."""
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, TXT, or MD file."
        )

    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        chunks = ingest_document(file_path, filename)

        return {
            "message": f"✅ '{filename}' uploaded and indexed successfully.",
            "filename": filename,
            "chunks_stored": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask_question(request: QueryRequest):
    """Ask a question and get a contextual answer from uploaded documents."""
    result = answer_question(request.question)
    return result


@app.get("/documents")
def get_documents():
    """List all documents currently in the vector store."""
    docs = list_documents()
    return {"documents": docs, "count": len(docs)}


@app.delete("/documents/{filename}")
def remove_document(filename: str):
    """Delete a document and all its chunks from the vector store."""
    deleted = delete_document(filename)

    # Also remove the uploaded file if it exists
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return {
        "message": f"✅ '{filename}' removed from knowledge base.",
        "chunks_deleted": deleted
    }
