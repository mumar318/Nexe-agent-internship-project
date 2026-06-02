# 🤝 Multi-Agent System

**Advanced Project 6 of 6 · NexeAgent Internship Series**

The most sophisticated project in the series. A central Orchestrator agent plans any task and delegates each step to the most suitable specialist agent through a typed, logged message bus. Each specialist agent has its own identity, LLM prompt, and set of tools.

---

## ✨ Features

- **Orchestrator agent** — plans tasks, delegates to specialists, synthesises final answer
- **4 specialist agents** — Research, Writer, Email, Calculator, each with own tools
- **Typed message bus** — all inter-agent messages are typed, routed, and persisted to SQLite
- **Full visibility** — UI shows the plan, each agent's output, and every message exchanged
- **Task delegation** — each step automatically assigned to the best-fit agent
- **4-tab Streamlit UI** — Run Task / Task Logs / Message Bus / Reports
- **Streamlit Cloud ready** — `streamlit_app.py` runs agent logic directly without FastAPI

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          User (Browser)                              │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  high-level task
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│           Streamlit UI  (app.py / streamlit_app.py)                  │
│  Tab 1: 🚀 Run  Tab 2: 📋 Logs  Tab 3: 💬 Messages  Tab 4: 📄 Reports│
└───────────────────────────────┬──────────────────────────────────────┘
                                │  POST /run  (or direct call)
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  coordinator.py                                      │
│     Creates MessageBus → runs orchestrator → saves task log          │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│              Orchestrator Agent  (agents/orchestrator.py)            │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ PLANNER LLM → [{"step":"...","agent":"research_agent"}, ...]  │   │
│  └─────────────────────────────┬────────────────────────────────┘   │
│                                │  for each step                      │
│                                ▼                                     │
│          publish(TASK_DELEGATION) ──► MessageBus                     │
└────────────────────────────────────────────────────────────────────┬─┘
                                                                     │
                    ┌────────────────────────────────────────────────▼─┐
                    │           Message Bus  (communication/)          │
                    │  routes · persists · dispatches · logs all msgs  │
                    └──┬──────────────┬──────────────┬─────────────┬───┘
                       │              │              │             │
              DELEGATE  │    DELEGATE  │    DELEGATE  │   DELEGATE  │
                       ▼              ▼              ▼             ▼
          ┌────────────────┐ ┌──────────────┐ ┌──────────┐ ┌────────────┐
          │ research_agent │ │ writer_agent │ │email_agt │ │ calc_agent │
          │                │ │              │ │          │ │            │
          │ web_search()   │ │draft_report()│ │send_email│ │ calculate()│
          │ summarize()    │ │format_content│ │compose_  │ │ percentage │
          │                │ │write_document│ │  email() │ │ compound_  │
          │   SerpAPI      │ │  Groq LLM    │ │  Gmail   │ │  growth()  │
          │   Groq LLM     │ │  SQLite      │ │  SMTP    │ │statistics()│
          └────────┬───────┘ └──────┬───────┘ └────┬─────┘ └─────┬──────┘
                   │                │              │             │
                   └────────────────┴──────────────┴─────────────┘
                                         │
                                TASK_RESULT messages
                                         │
                                         ▼
                    ┌────────────────────────────────────────┐
                    │      Orchestrator: collect results      │
                    │      SYNTHESISER LLM → final answer     │
                    └────────────────────────────────────────┘
                                         │
                               SQLite (multi_agent.db)
                     task_log · message_log · reports tables
```

---

## 🤖 Agents

| Agent | Role | Tools |
|-------|------|-------|
| `orchestrator` | Plans task, delegates steps, synthesises answer | Planner LLM · Synthesiser LLM |
| `research_agent` | Web research and summarisation | `web_search` · `summarize` |
| `writer_agent` | Content creation and formatting | `draft_report` · `format_content` · `write_document` |
| `email_agent` | Email composition and delivery | `send_email` · `compose_email` |
| `calculator_agent` | Numeric analysis and math | `calculate` · `percentage` · `compound_growth` · `statistics` |

---

## 💬 Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `task_plan` | Orchestrator → broadcast | Execution plan announced |
| `task_delegation` | Orchestrator → specialist | Step assigned to agent |
| `task_result` | Specialist → Orchestrator | Step result returned |
| `task_complete` | Orchestrator → broadcast | Task finished |

---

## 📁 Project Structure

```
Multi-Agent-System/
├── agents/
│   ├── orchestrator.py       # Plans + delegates + synthesises
│   ├── research_agent.py     # web_search · summarize
│   ├── writer_agent.py       # draft_report · format_content · write_document
│   ├── email_agent.py        # send_email · compose_email
│   └── calculator_agent.py   # calculate · percentage · compound_growth · statistics
├── communication/
│   ├── message_bus.py        # Router · dispatcher · SQLite persistence
│   └── messages.py           # Message dataclass · MessageType enum
├── coordinator.py            # Wires bus + orchestrator per request
├── config.py                 # Unified config (Streamlit secrets / .env)
├── api.py                    # FastAPI server
├── app.py                    # Streamlit UI (local, calls FastAPI)
├── streamlit_app.py          # Streamlit Cloud entry point (direct agent call)
├── run.py                    # Launch FastAPI :8006 + Streamlit :8507
├── requirements.txt
├── .env
├── .env.example
└── .streamlit/
    ├── config.toml           # Theme + server settings
    └── secrets.toml.example  # Secrets template for Streamlit Cloud
```

---

## 🚀 Installation & Usage

### 1. Clone & navigate
```bash
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd "Nexe-agent-internship-project/06-Multi-Agent-System"
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

### 4. Run locally
```bash
python run.py
```

- **UI** → http://localhost:8507
- **API docs** → http://localhost:8006/docs

---

## ☁️ Deploy on Streamlit Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set **Main file:** `streamlit_app.py`
4. Under **Secrets**, paste your keys in TOML format:
```toml
GROQ_API_KEY = "..."
SERPAPI_KEY  = "..."
EMAIL_ADDRESS  = "..."
EMAIL_PASSWORD = "..."
```
5. Click Deploy

---

## 💬 Example Tasks

```
Research the latest trends in AI and save a report
Search for Python best practices, summarize them, and send to nexeagent@gmail.com
Calculate compound growth: 10000 principal, 8% rate, 5 periods, then save a report
Find information about machine learning, write a business report, and email it
Calculate the ROI if revenue is 80000 and cost is 50000, then save the result
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Status + agent list |
| GET | `/health` | Health check |
| POST | `/run` | Submit a task |
| GET | `/logs` | List task logs |
| GET | `/logs/{id}` | Full log detail |
| GET | `/messages` | Inter-agent message history |
| GET | `/reports` | Saved reports |

---

## 🔧 Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| Groq (LLaMA 3.1-8B) | 0.37.1 | All LLM calls |
| FastAPI | 0.136.1 | REST API |
| Streamlit | 1.57.0 | Web UI |
| SerpAPI | — | Web search |
| SQLite | built-in | All persistence |
| smtplib | built-in | Gmail email |
| python-dotenv | 1.2.2 | Env config |

---

## 🗄️ Database Schema

```sql
CREATE TABLE message_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id    TEXT, sender TEXT, recipient TEXT,
    msg_type  TEXT, payload TEXT, timestamp TEXT
);

CREATE TABLE task_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    task         TEXT, plan TEXT, steps TEXT,
    final_answer TEXT, status TEXT, timestamp TEXT
);

CREATE TABLE reports (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, content TEXT, timestamp TEXT
);
```

---

*Part of the [NexeAgent Internship Projects](../README.md) · Project 6 of 6*
