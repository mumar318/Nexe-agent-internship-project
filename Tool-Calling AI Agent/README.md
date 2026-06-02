# 🤖 Tool-Calling AI Agent

**Beginner Project 1 of 6 · NexeAgent Internship Series**

An AI agent that understands natural language queries and calls the correct tool — addition, multiplication, or real-time weather — returning a clean structured JSON response.

---

## ✨ Features

- Natural language → tool selection via Groq LLaMA
- Real-time weather data via OpenWeatherMap API
- Math operations (add, multiply)
- Structured JSON responses for every query
- All interactions logged to SQLite
- FastAPI backend + Streamlit UI

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   User (Browser)                     │
└────────────────────────┬─────────────────────────────┘
                         │  natural language query
                         ▼
┌──────────────────────────────────────────────────────┐
│              Streamlit UI  (app.py)                  │
│         text input → POST /chat → display result     │
└────────────────────────┬─────────────────────────────┘
                         │  HTTP POST /chat
                         ▼
┌──────────────────────────────────────────────────────┐
│              FastAPI Server  (api.py)                │
│         CORS · Pydantic validation · routing         │
└────────────────────────┬─────────────────────────────┘
                         │  run_agent(query)
                         ▼
┌──────────────────────────────────────────────────────┐
│              Agent Controller  (main.py)             │
│                                                      │
│   Query ──► Groq LLaMA 3.1 ──► JSON tool call       │
│                                      │               │
│              ┌───────────────────────┤               │
│              ▼           ▼           ▼               │
│           add()     multiply()  get_weather()        │
│         (tools.py)  (tools.py)   (tools.py)          │
│              │                       │               │
│              │               OpenWeatherMap API      │
│              └───────────────────────┘               │
│                         │                            │
│                  save_log() ──► SQLite (logs.db)     │
└────────────────────────┬─────────────────────────────┘
                         │  structured JSON result
                         ▼
                    Response to UI
```

---

## 🛠️ Tools

| Tool | Description | Parameters |
|------|-------------|-----------|
| `add(a, b)` | Add two numbers | `a: float, b: float` |
| `multiply(a, b)` | Multiply two numbers | `a: float, b: float` |
| `get_weather(city)` | Real-time weather | `city: string` |

---

## 📁 Project Structure

```
Tool-Calling AI Agent/
├── main.py          # Agent logic — LLM call + tool dispatch
├── tools.py         # Tool implementations
├── api.py           # FastAPI server
├── app.py           # Streamlit UI
├── db.py            # SQLite logging
├── run.py           # Launch both servers
├── requirements.txt
└── .env             # API keys
```

---

## 🚀 Installation & Usage

### 1. Clone & navigate
```bash
git clone https://github.com/mumar318/Nexe-agent-internship-project.git
cd "Nexe-agent-internship-project/01-Tool-Calling-AI-Agent"
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
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_openweathermap_api_key
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
What is 25 plus 38?
Multiply 12 by 15
What's the weather in Lahore?
What is the weather in London today?
```

---

## 📡 API

### `POST /chat`
```json
// Request
{ "query": "What is the weather in Karachi?" }

// Response
{
  "tool_used": "get_weather",
  "input": { "city": "Karachi" },
  "result": "🌤️ Weather in Karachi:\n🌡️ Temperature: 32°C..."
}
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
| OpenWeatherMap API | v2.5 | Weather data |
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

*Part of the [NexeAgent Internship Projects](../README.md) · Project 1 of 6*
