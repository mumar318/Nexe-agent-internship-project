# 🧮 AI Calculator Agent

**Beginner Project 2 of 6 · NexeAgent Internship Series**

A math-focused AI agent that understands natural language arithmetic queries. Supports 6 math operations plus in-session memory — store a result and recall it in a follow-up query to chain calculations together.

---

## ✨ Features

- Natural language → math tool selection via Groq LLaMA
- 6 math operations: add, subtract, multiply, divide, power, square root
- In-session memory: save a result and recall it later
- Division by zero and negative square root handled gracefully
- Float operands supported for all operations
- All interactions logged to SQLite (`logs.db`)
- FastAPI backend + Streamlit UI

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      User (Browser)                      │
└──────────────────────────┬───────────────────────────────┘
                           │  e.g. "Square root of 144"
                           ▼
┌──────────────────────────────────────────────────────────┐
│                Streamlit UI  (app.py)                    │
│   text input ──► "Calculate" button ──► display result   │
└──────────────────────────┬───────────────────────────────┘
                           │  HTTP POST /chat
                           ▼
┌──────────────────────────────────────────────────────────┐
│               FastAPI Server  (api.py)                   │
│          CORS · Pydantic validation · /chat              │
└──────────────────────────┬───────────────────────────────┘
                           │  run_agent(query)
                           ▼
┌──────────────────────────────────────────────────────────┐
│             Agent Controller  (main.py)                  │
│                                                          │
│  Query ──► Groq LLaMA 3.1 ──► JSON {"name","arguments"} │
│                                         │                │
│    ┌────────────────────────────────────┤                │
│    ▼       ▼        ▼       ▼     ▼     ▼                │
│  add() subtract() multiply() divide() power() sqrt()     │
│                                                          │
│           store_memory() ◄──► recall_memory()            │
│               │                    │                     │
│           _memory_store        _memory_store             │
│           (in-session dict)                              │
│                                                          │
│                    save_log() ──► SQLite (logs.db)       │
└──────────────────────────┬───────────────────────────────┘
                           │  {tool_used, input, result}
                           ▼
                     Response to UI
```

---

## 🛠️ Tools

| Tool | Description | Parameters |
|------|-------------|-----------|
| `add(a, b)` | a + b | `a: float, b: float` |
| `subtract(a, b)` | a − b | `a: float, b: float` |
| `multiply(a, b)` | a × b | `a: float, b: float` |
| `divide(a, b)` | a ÷ b (safe) | `a: float, b: float` |
| `power(base, exponent)` | base ^ exponent | `base: float, exponent: float` |
| `square_root(a)` | √a (safe) | `a: float` |
| `store_memory(value)` | Save value to session memory | `value: float` |
| `recall_memory()` | Retrieve saved value | _(no args)_ |

---

## 📁 Project Structure

```
Ai_calculater_Agent/
├── main.py          # Agent logic — LLM call + tool dispatch
├── tools.py         # Math tools + in-session memory store
├── api.py           # FastAPI server (GET /, GET /health, POST /chat)
├── app.py           # Streamlit UI with examples
├── db.py            # SQLite interaction logging
├── run.py           # Launch both servers
├── logs.db          # Auto-created SQLite database
├── requirements.txt
└── .env             # GROQ_API_KEY
```

---

## 🚀 Installation & Usage

### 1. Clone & navigate
```bash
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd "Nexe-agent-internship-project/02-AI-Calculator-Agent"
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

- **UI** → http://localhost:8501
- **API docs** → http://localhost:8000/docs

---

## 💬 Example Queries

```
Add 25 and 37
Subtract 100 from 250
Multiply 12 by 15
Divide 144 by 12
2 to the power of 10
Square root of 225
Save 500 to memory
Recall my saved value
Recall my saved value and multiply it by 3
```

---

## 📡 API

### `POST /chat`
```json
// Request
{ "query": "What is 2 to the power of 8?" }

// Response
{
  "tool_used": "power",
  "input": { "base": 2, "exponent": 8 },
  "result": 256.0
}
```

### `GET /health`
```json
{ "status": "healthy" }
```

---

## 🔧 Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| Groq (LLaMA 3.1-8B) | latest | NLU + tool selection |
| FastAPI | 0.136.1 | REST API |
| Streamlit | 1.57.0 | Web UI |
| SQLite | built-in | Interaction logging |
| python-dotenv | 1.2.2 | Env config |

---

## 🗄️ Database Schema

```sql
CREATE TABLE logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    query     TEXT,
    response  TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

*Part of the [NexeAgent Internship Projects](../README.md) · Project 2 of 6*
