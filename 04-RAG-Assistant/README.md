# 📚 RAG Assistant

**Intermediate Project 4 of 6 · NexeAgent Internship Series**

A Retrieval-Augmented Generation (RAG) assistant. Upload PDF, TXT, or Markdown documents, then ask questions in natural language. Answers are grounded strictly in your documents using ChromaDB for vector search and Groq LLaMA for generation — with source citations.

---

## ✨ Features

- Upload PDF, TXT, or Markdown documents
- Documents chunked and stored as vector embeddings in ChromaDB
- Natural language Q&A grounded in your uploaded documents
- Source citations — every answer shows which document it came from
- Document management — list and delete documents from the knowledge base
- Answers refuse to hallucinate ("I couldn't find relevant information")
- FastAPI backend + Streamlit 3-tab UI

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      User (Browser)                          │
└──────────────┬───────────────────────────────────────────────┘
               │
       ┌───────┴──────────────────────────────┐
       │ Upload document       Ask a question  │
       ▼                              ▼        │
┌─────────────────────────────────────────────┤
│            Streamlit UI  (app.py)           │
│  Tab 1: 📤 Upload  Tab 2: 💬 Ask  Tab 3: 📂 Docs │
└──────┬──────────────────────────┬───────────┘
       │  POST /upload            │  POST /ask
       ▼                          ▼
┌─────────────────────────────────────────────┐
│           FastAPI Server  (api.py)          │
│   /upload · /ask · /documents · /documents  │
└──────┬──────────────────────────┬───────────┘
       │                          │
       ▼                          ▼
┌─────────────────┐    ┌──────────────────────────────────────┐
│  vector_store.py│    │           rag_chain.py               │
│                 │    │                                      │
│  PyPDFLoader /  │    │  1. similarity_search(query, k=4)    │
│  TextLoader     │    │         │                            │
│       ↓         │    │         ▼                            │
│  Text chunking  │    │   top-k relevant chunks              │
│  (500 chars,    │    │         │                            │
│   50 overlap)   │    │         ▼                            │
│       ↓         │    │  Groq LLaMA 3.1 (with context)      │
│  ONNX embeddings│    │         │                            │
│       ↓         │    │         ▼                            │
│  ChromaDB store │    │  Answer + source citations           │
└────────┬────────┘    └──────────────────────────────────────┘
         │
    ┌────▼─────────────┐
    │  ChromaDB        │
    │  (chroma_db/)    │
    │  vector index    │
    └──────────────────┘
```

---

## 🛠️ Key Components

| File | Role |
|------|------|
| `vector_store.py` | Document loading, chunking, embedding, ChromaDB CRUD |
| `rag_chain.py` | Retrieve chunks → build context → Groq LLM → answer |
| `api.py` | FastAPI endpoints (upload, ask, list, delete) |
| `app.py` | Streamlit UI (3 tabs) |

---

## 📁 Project Structure

```
RAG-Assistant/
├── api.py            # FastAPI backend
├── app.py            # Streamlit UI (3 tabs)
├── rag_chain.py      # RAG: retrieve + generate
├── vector_store.py   # ChromaDB: ingest, search, manage
├── run.py            # Launch FastAPI :8003 + Streamlit :8504
├── requirements.txt
├── .env              # GROQ_API_KEY
├── uploaded_docs/    # Uploaded files stored here
└── chroma_db/        # ChromaDB vector index (auto-created)
```

---

## 🚀 Installation & Usage

### 1. Clone & navigate
```bash
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd "Nexe-agent-internship-project/04-RAG-Assistant"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API key
```bash
cp .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run
```bash
python run.py
```

- **UI** → http://localhost:8504
- **API docs** → http://localhost:8003/docs

---

## 💬 Example Usage

1. Open the **Upload** tab and upload a PDF document
2. Switch to the **Ask** tab
3. Type a question about the document's content
4. Get a grounded answer with source citation

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | `{"status": "healthy"}` |
| POST | `/upload` | Upload and index a document |
| POST | `/ask` | Ask a question |
| GET | `/documents` | List all indexed documents |
| DELETE | `/documents/{filename}` | Remove a document |

### `POST /ask`
```json
// Request
{ "question": "What is supervised learning?" }

// Response
{
  "answer": "Supervised learning is...",
  "sources": ["Introduction to ML.pdf"],
  "context_used": "..."
}
```

---

## 🔧 Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| Groq (LLaMA 3.1-8B) | 0.11.0 | Answer generation |
| FastAPI | 0.115.0 | REST API |
| Streamlit | latest | Web UI |
| ChromaDB | 0.5.11 | Vector store |
| LangChain | 0.3.1 | Document loading + chunking |
| ONNX MiniLM-L6 | built-in | Local text embeddings |
| PyPDF | 4.3.1 | PDF parsing |
| python-dotenv | 1.0.1 | Env config |

---

## ⚙️ RAG Configuration

| Parameter | Value |
|-----------|-------|
| Chunk size | 500 characters |
| Chunk overlap | 50 characters |
| Retrieved chunks (k) | 4 |
| Embedding model | ONNX MiniLM-L6-V2 (local) |
| LLM | LLaMA 3.1-8B-Instant |

---

*Part of the [NexeAgent Internship Projects](../README.md) · Project 4 of 6*
