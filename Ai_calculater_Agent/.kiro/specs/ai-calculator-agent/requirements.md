# Requirements Document

## Introduction

The AI Calculator Agent is the second project in the NexeAgent beginner internship series. It extends the patterns established in Task 1 (Tool-Calling AI Agent) by building a focused, math-capable AI agent. Users interact with the agent using natural language (e.g., "What is 12 to the power of 3?" or "Recall my last result and multiply it by 5"), and the agent uses Groq's LLaMA model to understand the intent, select the correct math tool, execute it, and return a clean JSON response. Results can be stored in memory and retrieved in follow-up queries. All interactions are logged to SQLite.

The project uses the same tech stack as Task 1: Python, Groq AI (LLaMA model), FastAPI, Streamlit, and SQLite.

---

## Glossary

- **Agent**: The AI Calculator Agent system as a whole.
- **Calculator**: The component responsible for executing mathematical operations.
- **Memory**: The in-session store that holds the most recent calculation result for recall.
- **Memory_Store**: The in-memory data structure (Python dict or variable) that persists the last result within a session.
- **LLM**: The Groq-hosted LLaMA language model used for natural language understanding and tool selection.
- **Tool**: A Python function exposed to the LLM for execution (e.g., `add`, `divide`, `power`).
- **Tool_Dispatcher**: The component in `main.py` that maps LLM-selected tool names to Python functions and executes them.
- **API_Server**: The FastAPI application (`api.py`) that exposes the HTTP interface.
- **UI**: The Streamlit web application (`app.py`) that provides the user-facing interface.
- **DB_Logger**: The SQLite-backed component (`db.py`) that persists query/response pairs.
- **Structured_Response**: A JSON object with a fixed schema returned for every request.
- **Session**: A single continuous run of the FastAPI server process.

---

## Requirements

### Requirement 1: Basic Math Operations

**User Story:** As an intern learning AI tool-calling, I want the agent to perform basic arithmetic operations via natural language, so that I can understand how LLMs select and call tools.

#### Acceptance Criteria

1. WHEN a user submits a natural language query requesting addition, THE Agent SHALL invoke the `add` tool and return the numeric result.
2. WHEN a user submits a natural language query requesting subtraction, THE Agent SHALL invoke the `subtract` tool and return the numeric result.
3. WHEN a user submits a natural language query requesting multiplication, THE Agent SHALL invoke the `multiply` tool and return the numeric result.
4. WHEN a user submits a natural language query requesting division, THE Agent SHALL invoke the `divide` tool and return the numeric result.
5. IF a division query contains a divisor of zero, THEN THE Calculator SHALL return a descriptive error message without raising an unhandled exception.
6. WHEN a user submits a query with numeric operands, THE LLM SHALL extract the operands and pass them as arguments to the selected tool.

---

### Requirement 2: Advanced Math Operations

**User Story:** As an intern, I want the agent to support power and square root operations, so that I can see how a richer tool set is exposed to an LLM.

#### Acceptance Criteria

1. WHEN a user submits a natural language query requesting exponentiation (e.g., "2 to the power of 8"), THE Agent SHALL invoke the `power` tool with the correct base and exponent and return the result.
2. WHEN a user submits a natural language query requesting a square root (e.g., "square root of 144"), THE Agent SHALL invoke the `square_root` tool and return the result.
3. IF a square root query contains a negative number, THEN THE Calculator SHALL return a descriptive error message without raising an unhandled exception.
4. THE Calculator SHALL support operands of type float, not only integers, for all six operations (add, subtract, multiply, divide, power, square_root).

---

### Requirement 3: Memory — Store and Recall

**User Story:** As a user, I want to store a calculation result and recall it in a later query, so that I can chain operations across multiple messages.

#### Acceptance Criteria

1. WHEN a user submits a query that includes an instruction to save or remember the result, THE Agent SHALL invoke the `store_memory` tool and persist the numeric result in the Memory_Store.
2. WHEN a user submits a query that references a previously stored result (e.g., "use my saved result"), THE Agent SHALL invoke the `recall_memory` tool and return the value currently held in the Memory_Store.
3. IF a user invokes `recall_memory` when no value has been stored in the current Session, THEN THE Memory_Store SHALL return a descriptive message indicating that no result is currently saved.
4. WHILE a Session is active, THE Memory_Store SHALL retain the most recently stored value across multiple queries.
5. WHEN a new value is stored via `store_memory`, THE Memory_Store SHALL overwrite the previously stored value.

---

### Requirement 4: Structured JSON Output

**User Story:** As a developer integrating this agent, I want every response to follow a consistent JSON schema, so that I can reliably parse and display results.

#### Acceptance Criteria

1. THE API_Server SHALL return a JSON response for every request, including error cases.
2. WHEN a tool executes successfully, THE Structured_Response SHALL contain the fields `tool_used`, `input`, and `result`.
3. IF an error occurs during tool execution or LLM parsing, THE Structured_Response SHALL contain an `error` field with a human-readable description.
4. THE Structured_Response SHALL not contain fields outside the defined schema (`tool_used`, `input`, `result`, `error`).
5. WHEN the LLM returns a response that cannot be parsed as valid JSON, THE Tool_Dispatcher SHALL catch the parse error and return a Structured_Response containing an `error` field.

---

### Requirement 5: FastAPI Backend

**User Story:** As a developer, I want a FastAPI backend that exposes the agent over HTTP, so that the Streamlit UI and any external client can call it consistently.

#### Acceptance Criteria

1. THE API_Server SHALL expose a `POST /chat` endpoint that accepts a JSON body with a `query` field of type string.
2. THE API_Server SHALL expose a `GET /` health-check endpoint that returns a status message.
3. THE API_Server SHALL expose a `GET /health` endpoint that returns `{"status": "healthy"}`.
4. WHEN a request is received at `POST /chat`, THE API_Server SHALL pass the `query` value to the Tool_Dispatcher and return its output as the HTTP response body.
5. THE API_Server SHALL include CORS middleware configured to allow all origins, enabling the Streamlit UI to connect.
6. IF the `query` field is missing or empty in the request body, THEN THE API_Server SHALL return an HTTP 422 response with a validation error message.

---

### Requirement 6: Streamlit User Interface

**User Story:** As an intern, I want a simple web UI to interact with the calculator agent, so that I can test it without writing API calls manually.

#### Acceptance Criteria

1. THE UI SHALL display a text input field where users can type natural language queries.
2. WHEN a user clicks the "Calculate" button, THE UI SHALL send the query to the `POST /chat` endpoint and display the response.
3. WHEN the response contains a `result` field, THE UI SHALL display the result prominently, regardless of whether a connection warning is also present.
4. WHEN the response contains an `error` field, THE UI SHALL display the error message in a visually distinct style.
5. WHEN the API_Server is unreachable, THE UI SHALL display a connection error message without crashing, and SHALL continue to display any previously received results.
6. THE UI SHALL display the full JSON response in an expandable section so users can inspect the raw output.

---

### Requirement 7: SQLite Interaction Logging

**User Story:** As an intern, I want every query and response to be logged to a SQLite database, so that I can review past interactions for learning and debugging.

#### Acceptance Criteria

1. THE DB_Logger SHALL create a `logs` table in `logs.db` on startup if it does not already exist.
2. WHEN the Tool_Dispatcher produces a response (success or error), THE DB_Logger SHALL insert a row containing the original query and the serialized response into the `logs` table.
3. THE `logs` table SHALL contain at minimum the columns: `id` (auto-increment integer primary key), `query` (text), `response` (text), and `timestamp` (datetime, defaulting to the current time).
4. IF a database write fails, THE DB_Logger SHALL log the failure to the console without interrupting the HTTP response to the caller.

---

### Requirement 8: LLM Tool Selection

**User Story:** As an intern, I want the LLM to correctly identify which math tool to call from a natural language query, so that I can learn how prompt engineering drives tool selection.

#### Acceptance Criteria

1. THE LLM SHALL be provided a system prompt that lists all available tools with their names and parameter signatures.
2. WHEN given a valid math query, THE LLM SHALL return a JSON object with the fields `name` (tool name) and `arguments` (parameter dict) and no other top-level fields.
3. THE Tool_Dispatcher SHALL strip any markdown code fences from the LLM response before attempting JSON parsing.
4. IF the LLM returns a tool name not present in the function map, THEN THE Tool_Dispatcher SHALL return a Structured_Response with an `error` field describing the unknown tool.
5. THE system prompt SHALL instruct the LLM to return only JSON with no explanatory text, code, or markdown.
