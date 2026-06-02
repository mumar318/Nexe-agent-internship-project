# 🔧 Multi-Tool Agent

**Beginner Project 3 of 6 · NexeAgent Internship Series**

A natural language AI agent with real-world utility tools: search the web via SerpAPI, save notes to a SQLite database, and send emails via Gmail — all through a single chat interface.

---

## ✨ Features

- Web search using SerpAPI (Google results)
- Save notes / results to SQLite database
- Send emails via Gmail SMTP
- Natural language → tool selection via Groq LLaMA
- Notes viewer tab — browse all saved notes
- All interactions logged to SQLite
- FastAPI backend + Streamlit 2-tab UI

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User (Browser)                          │
└───────────────────────────┬─────────────────────────────────┘
                            │  natural language query
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Streamlit UI  (app.py)                       │
│                                                             │
│      Tab 1: 💬 Chat          Tab 2: 📋 Saved Notes         │
│      text input + Run btn    list all saved notes           │
└───────────────────────────┬─────────────────────────────────┘
                            │  HTTP POST /chat
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Server  (api.py)                       │
│      POST /chat · GET /notes · GET / · GET /health          │
└───────────────────────────┬─────────────────────────────────┘
                            │  run_agent(query)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             Agent Controller  (main.py)                     │
│                                                             │
│  Query ──► Groq LLaMA 3.1 ──► {"name": ..., "arguments"}  │
│                                          │                  │
│              ┌───────────────────────────┤                  │
│              ▼               ▼           ▼                  │
│        web_search()      save_note()  send_email()          │
│              │               │           │                  │
│         SerpAPI          SQLite DB    Gmail SMTP            │
│        (Google)         (agent.db)   (smtp.gmail.com)       │
│                                                             │
│                   save_log() ──► SQLite logs table          │
└───────────────────────────┬─────────────────────────────────┘
                            │  {tool_used, input, result}
                            ▼
                      Response to UI
```

---

## 🛠️ Tools

| Tool | Description | Parameters |
|------|-------------|-----------|
| `web_search(query)` | Search Google via SerpAPI, returns top 3 results | `query: str` |
| `save_note(title, content)` | Save a note to SQLite database | `title: str, content: str` |
| `send_email(to, subject, body)` | Send email via Gmail SMTP | `to: str, subject: str, body: str` |

---

## 📁 Project Structure

```
Multi-Tool Agent/
├── main.py          # Agent logic — LLM call + tool dispatch
├── tools.py         # web_search · save_note · send_email
├── api.py           # FastAPI server (chat + notes endpoints)
├── app.py           # Streamlit UI (Chat + Saved Notes tabs)
├── db.py            # SQLite — logs table + notes table
├── run.py           # Launch FastAPI :8002 + Streamlit :8503
├── agent.db         # Auto-created SQLite database
├── requirements.txt
└── .env             # API keys
```

---

## 🚀 Installation & Usage

### 1. Clone & navigate
```bash
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd "Nexe-agent-internship-project/03-Multi-Tool-Agent"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API keys
```bash
cp .env.example .env
```
Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

> **Gmail note:** Use a [Gmail App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 4. Run
```bash
python run.py
```

- **UI** → http://localhost:8503
- **API docs** → http://localhost:8002/docs

---

## 💬 Example Queries

```
Search for latest AI news
Search what is Python programming language
Save a note titled Project Ideas with content: Build a RAG chatbot
Send an email to someone@gmail.com about the meeting tomorrow
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | `{"status": "healthy"}` |
| POST | `/chat` | Run agent with a query |
| GET | `/notes` | List all saved notes |

### `POST /chat`
```json
// Request
{ "query": "Search for the latest Python news" }

// Response
{
  "tool_used": "web_search",
  "input": { "query": "latest Python news" },
  "result": "🔍 Top results for: 'latest Python news'\n\n1. ..."
}
```

---

## 🔧 Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| Groq (LLaMA 3.1-8B) | 0.37.1 | NLU + tool selection |
| FastAPI | 0.136.1 | REST API |
| Streamlit | 1.57.0 | Web UI |
| SerpAPI | — | Google web search |
| SQLite | built-in | Notes + logs storage |
| smtplib | built-in | Gmail email sending |
| python-dotenv | 1.2.2 | Env config |

---

## 🗄️ Database Schema

```sql
-- Interaction logs
CREATE TABLE logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    query     TEXT,
    response  TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Saved notes
CREATE TABLE notes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT,
    content   TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

*Part of the [NexeAgent Internship Projects](../README.md) · Project 3 of 6*
