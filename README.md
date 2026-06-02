# 🤖 NexeAgent Internship Projects

> A collection of 6 AI-powered projects built during the NexeAgent internship — progressing from basic tool-calling agents to multi-agent systems with autonomous reasoning.

**Intern:** Muhammad Umar Ihsan &nbsp;|&nbsp; **Email:** nexeagent@gmail.com &nbsp;|&nbsp; **LinkedIn:** [Nexe-Agent](https://linkedin.com/in/nexe-agent) &nbsp;|&nbsp; **GitHub:** [@mumar318](https://github.com/mumar318)

---

## 🗺️ Repository Structure

```
Nexe-agent-internship-project/
├── 01-Tool-Calling-AI-Agent/       ← Beginner 1: Basic tool-calling with weather & math
├── 02-AI-Calculator-Agent/         ← Beginner 2: Math agent with memory
├── 03-Multi-Tool-Agent/            ← Beginner 3: Web search + notes + email
├── 04-RAG-Assistant/               ← Intermediate: Document Q&A with vector search
├── 05-Autonomous-Business-Agent/   ← Advanced 1: Multi-step planning & execution
└── 06-Multi-Agent-System/          ← Advanced 2: Orchestrator + 4 specialist agents
```

---

## 📦 Projects Overview

### 01 · Tool-Calling AI Agent `Beginner`
> The foundation project. An AI agent that understands natural language and calls the right tool — math or real-time weather.

| | |
|---|---|
| **Tech** | Python · Groq LLaMA · FastAPI · Streamlit · SQLite |
| **Tools** | `add` · `multiply` · `get_weather` |
| **Ports** | API :8000 · UI :8501 |

📁 [Go to project →](./01-Tool-Calling-AI-Agent/)

---

### 02 · AI Calculator Agent `Beginner`
> Extends tool-calling with a full math toolkit and in-session memory. Users can save results and recall them in follow-up queries.

| | |
|---|---|
| **Tech** | Python · Groq LLaMA · FastAPI · Streamlit · SQLite |
| **Tools** | `add` · `subtract` · `multiply` · `divide` · `power` · `square_root` · `store_memory` · `recall_memory` |
| **Ports** | API :8000 · UI :8501 |

📁 [Go to project →](./02-AI-Calculator-Agent/)

---

### 03 · Multi-Tool Agent `Beginner`
> Adds real-world utility: web search via SerpAPI, note saving to SQLite, and Gmail email sending — all via natural language.

| | |
|---|---|
| **Tech** | Python · Groq LLaMA · FastAPI · Streamlit · SerpAPI · SQLite |
| **Tools** | `web_search` · `save_note` · `send_email` |
| **Ports** | API :8002 · UI :8503 |

📁 [Go to project →](./03-Multi-Tool-Agent/)

---

### 04 · RAG Assistant `Intermediate`
> Upload PDF/TXT/MD documents and ask questions in natural language. Answers are grounded in your documents using ChromaDB vector search.

| | |
|---|---|
| **Tech** | Python · Groq LLaMA · FastAPI · Streamlit · ChromaDB · LangChain |
| **Features** | Document upload · Vector embeddings · Source citations · Document management |
| **Ports** | API :8003 · UI :8504 |

📁 [Go to project →](./04-RAG-Assistant/)

---

### 05 · Autonomous Business Agent `Advanced`
> Give it a high-level business task. It plans the steps, executes each one with the right tool, and logs the full trace — fully autonomously.

| | |
|---|---|
| **Tech** | Python · Groq LLaMA · FastAPI · Streamlit · SQLite |
| **Tools** | `web_search` · `send_email` · `save_report` · `summarize_text` · `calculate` |
| **Ports** | API :8004 · UI :8505 |

📁 [Go to project →](./05-Autonomous-Business-Agent/)

---

### 06 · Multi-Agent System `Advanced`
> The most advanced project. An Orchestrator agent plans tasks and delegates each step to specialist agents through a typed message bus.

| | |
|---|---|
| **Tech** | Python · Groq LLaMA · FastAPI · Streamlit · SQLite |
| **Agents** | Orchestrator · ResearchAgent · WriterAgent · EmailAgent · CalculatorAgent |
| **Ports** | API :8006 · UI :8507 |

📁 [Go to project →](./06-Multi-Agent-System/)

---

## 🧠 Learning Progression

```
Beginner ──────────────────────────────────────────── Advanced
   │                                                      │
[01] Single tool-calling                                  │
   ↓                                                      │
[02] Richer tool set + memory                             │
   ↓                                                      │
[03] Real-world tools (search · email · DB)               │
   ↓                                                      │
[04] RAG: document-grounded answers                       │
   ↓                                                      │
[05] Autonomous multi-step planning                       │
   ↓                                                      │
[06] Multi-agent orchestration ───────────────────────────┘
```

---

## 🛠️ Tech Stack Summary

| Technology | Used In |
|-----------|---------|
| **Groq LLaMA 3.1-8B** | All projects |
| **FastAPI** | All projects |
| **Streamlit** | All projects |
| **SQLite** | 01, 02, 03, 05, 06 |
| **SerpAPI** | 03, 05, 06 |
| **Gmail SMTP** | 03, 05, 06 |
| **ChromaDB** | 04 |
| **LangChain** | 04 |
| **OpenWeatherMap** | 01 |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd Nexe-agent-internship-project

# Navigate to any project and install dependencies
cd 06-Multi-Agent-System
pip install -r requirements.txt

# Add your API keys to .env (copy from .env.example)
cp .env.example .env

# Run
python run.py
```

Each project has a detailed README with its own setup steps.

---

## 📊 Project Status

| # | Project | Status |
|---|---------|--------|
| 01 | Tool-Calling AI Agent | ✅ Complete |
| 02 | AI Calculator Agent | ✅ Complete |
| 03 | Multi-Tool Agent | ✅ Complete |
| 04 | RAG Assistant | ✅ Complete |
| 05 | Autonomous Business Agent | ✅ Complete |
| 06 | Multi-Agent System | ✅ Complete |

---

*Built with 💙 during the NexeAgent Internship · 2025*
