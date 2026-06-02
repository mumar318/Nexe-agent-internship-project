# 🏢 Autonomous Business Agent

**Advanced Project 5 of 6 · NexeAgent Internship Series**

Give it a high-level business task in plain English. It plans the work into ordered steps, executes each step using the right tool, and logs the full trace — fully autonomously. No step-by-step instructions needed.

---

## ✨ Features

- **Task planning** — Planner LLM breaks any task into up to 6 ordered steps
- **Autonomous execution** — Executor LLM selects and calls the right tool per step
- **Final synthesis** — Synthesiser LLM generates a concise final answer
- **5 business tools** — web search, email, save report, summarize, calculate
- **Full execution trace** — every step logged with tool, input, output, status
- **3-tab Streamlit UI** — Run Task / Execution Logs / Reports

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  User (Browser)                              │
└────────────────────────────┬─────────────────────────────────┘
                             │  high-level business task
                             ▼
┌──────────────────────────────────────────────────────────────┐
│              Streamlit UI  (app.py)                          │
│  Tab 1: 🚀 Run Task  Tab 2: 📋 Logs  Tab 3: 📄 Reports      │
└────────────────────────────┬─────────────────────────────────┘
                             │  POST /run
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                FastAPI Server  (api.py)                      │
│     POST /run · GET /logs · GET /logs/{id} · GET /reports    │
└────────────────────────────┬─────────────────────────────────┘
                             │  run_agent(task)
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  Agent  (agent.py)                           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  STEP 1: PLANNER LLM                                │    │
│  │  "Break task into steps" → ["step1","step2",...]    │    │
│  └────────────────────────┬────────────────────────────┘    │
│                           │  for each step                   │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  STEP 2: EXECUTOR LLM (per step)                    │    │
│  │  "Which tool?" → {"name":..., "arguments":{...}}    │    │
│  └──────┬──────────────────────────────────────────────┘    │
│         │                                                    │
│    ┌────┼──────────────────────────────────────┐            │
│    ▼    ▼         ▼           ▼          ▼      ▼           │
│  web  send_   save_    summarize_    calculate()            │
│ search email  report    text()                              │
│    │    │        │           │          │                    │
│  SERP  Gmail  SQLite      Groq LLM    eval()               │
│         │    (reports)                                      │
│         └──────────────────────────────────────────────────┤│
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  STEP 3: SYNTHESISER LLM                            │    │
│  │  All step results → concise final answer            │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│              save_execution_log() ──► SQLite                 │
└────────────────────────────┬─────────────────────────────────┘
                             │  {task, plan, steps, final_answer}
                             ▼
                       Response to UI
```

---

## 🛠️ Tools

| Tool | Description | Parameters |
|------|-------------|-----------|
| `web_search(query)` | Google search via SerpAPI | `query: str` |
| `send_email(to, subject, body)` | Gmail SMTP | `to, subject, body: str` |
| `save_report(title, content)` | Persist to SQLite reports table | `title, content: str` |
| `summarize_text(text)` | Summarise via Groq LLM | `text: str` |
| `calculate(expression)` | Safe math eval | `expression: str` |

---

## 📁 Project Structure

```
Autonomous-Business-Agent/
├── agent.py         # Planner + executor + synthesiser
├── tools.py         # 5 business tools
├── api.py           # FastAPI (run, logs, reports)
├── app.py           # Streamlit UI (3 tabs)
├── db.py            # SQLite execution log + reports
├── run.py           # Launch FastAPI :8004 + Streamlit :8505
├── business_agent.db
├── requirements.txt
└── .env
```

---

## 🚀 Installation & Usage

### 1. Clone & navigate
```bash
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd "Nexe-agent-internship-project/05-Autonomous-Business-Agent"
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

### 4. Run
```bash
python run.py
```

- **UI** → http://localhost:8505
- **API docs** → http://localhost:8004/docs

---

## 💬 Example Tasks

```
Research the latest trends in AI and save a report
Search for Python FastAPI best practices and summarize the findings
Calculate the ROI: revenue is 50000, cost is 30000, then save the result
Search for top 3 project management tools and send a summary to nexeagent@gmail.com
Find information about machine learning and create a business report
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Status |
| GET | `/health` | Health check |
| POST | `/run` | Submit a business task |
| GET | `/logs` | List execution logs |
| GET | `/logs/{id}` | Full log detail |
| GET | `/reports` | List saved reports |

---

## 🔧 Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| Groq (LLaMA 3.1-8B) | 0.37.1 | Planner · Executor · Synthesiser |
| FastAPI | 0.136.1 | REST API |
| Streamlit | 1.57.0 | Web UI |
| SerpAPI | — | Web search |
| SQLite | built-in | Execution logs + reports |
| smtplib | built-in | Gmail email |
| python-dotenv | 1.2.2 | Env config |

---

## 🗄️ Database Schema

```sql
CREATE TABLE execution_logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    task         TEXT,
    plan         TEXT,   -- JSON array of steps
    steps        TEXT,   -- JSON array of step logs
    final_answer TEXT,
    status       TEXT,
    timestamp    TEXT
);

CREATE TABLE reports (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT,
    content   TEXT,
    timestamp TEXT
);
```

---

*Part of the [NexeAgent Internship Projects](../README.md) · Project 5 of 6*
