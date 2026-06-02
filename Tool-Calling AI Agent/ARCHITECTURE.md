# 🏗️ AI Tool Calling Agent - Architecture Documentation

## 📋 System Overview

The AI Tool Calling Agent is a microservices-based application that combines AI-powered natural language processing with tool execution capabilities. The system processes user queries, determines appropriate tools to use, executes them, and returns formatted results.

## 🎯 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │   Streamlit     │              │   External      │          │
│  │   Web App       │              │   API Clients   │          │
│  │   (app.py)      │              │                 │          │
│  └─────────────────┘              └─────────────────┘          │
│           │                                │                    │
│           │ HTTP Requests                  │ HTTP Requests      │
│           ▼                                ▼                    │
└─────────────────────────────────────────────────────────────────┘
           │                                │
           └────────────────┬───────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                FastAPI Server                           │   │
│  │                  (api.py)                               │   │
│  │                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │   CORS      │  │   Request   │  │   Response  │    │   │
│  │  │ Middleware  │  │ Validation  │  │ Formatting  │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                Agent Controller                          │   │
│  │                  (main.py)                              │   │
│  │                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │   │
│  │  │   Query     │  │    Tool     │  │   Response  │    │   │
│  │  │ Processing  │  │ Execution   │  │ Generation  │    │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
└─────────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│ │    Groq     │  │    Tool     │  │      Database           │  │
│ │ AI Service  │  │  Functions  │  │      Service            │  │
│ │             │  │ (tools.py)  │  │      (db.py)            │  │
│ │ ┌─────────┐ │  │             │  │                         │  │
│ │ │ LLaMA   │ │  │ ┌─────────┐ │  │ ┌─────────────────────┐ │  │
│ │ │ 3.1-8B  │ │  │ │   Add   │ │  │ │     SQLite          │ │  │
│ │ └─────────┘ │  │ └─────────┘ │  │ │   logs.db           │ │  │
│ └─────────────┘  │ ┌─────────┐ │  │ └─────────────────────┘ │  │
│                  │ │Multiply │ │  └─────────────────────────┘  │
│                  │ └─────────┘ │                               │
│                  │ ┌─────────┐ │                               │
│                  │ │Weather  │ │                               │
│                  │ │   API   │ │                               │
│                  │ └─────────┘ │                               │
│                  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐              ┌─────────────────────────┐   │
│ │ OpenWeatherMap  │              │      Groq Cloud         │   │
│ │      API        │              │      Platform           │   │
│ │                 │              │                         │   │
│ │ • Weather Data  │              │ • LLM Processing        │   │
│ │ • City Lookup   │              │ • Tool Recognition      │   │
│ │ • Forecasts     │              │ • JSON Generation       │   │
│ └─────────────────┘              └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Details

### 1. **User Interface Layer**

#### Streamlit Web App (`app.py`)
- **Purpose**: Provides interactive web interface
- **Features**: 
  - Text input for user queries
  - Real-time response display
  - JSON formatting for results
- **Technology**: Streamlit framework
- **Port**: 8501 (default)

#### External API Clients
- **Purpose**: Allow programmatic access
- **Protocol**: HTTP/REST
- **Format**: JSON requests/responses

### 2. **API Gateway Layer**

#### FastAPI Server (`api.py`)
- **Purpose**: HTTP API endpoint and request routing
- **Features**:
  - CORS middleware for cross-origin requests
  - Request validation using Pydantic models
  - Error handling and response formatting
- **Endpoint**: `POST /chat`
- **Port**: 8000 (default)

### 3. **Business Logic Layer**

#### Agent Controller (`main.py`)
- **Purpose**: Core orchestration and decision-making
- **Responsibilities**:
  - Parse user queries
  - Communicate with Groq AI
  - Determine appropriate tools
  - Execute tool functions
  - Format responses
  - Handle errors and logging

**Key Functions**:
```python
run_agent(user_input) -> dict
├── Query Processing
├── AI Model Communication  
├── Tool Selection & Execution
├── Response Generation
└── Error Handling
```

### 4. **Service Layer**

#### Tool Functions (`tools.py`)
- **Mathematical Operations**:
  - `add(a, b)`: Addition calculator
  - `multiply(a, b)`: Multiplication calculator
- **Weather Service**:
  - `get_weather(city)`: Real-time weather data
  - Integration with OpenWeatherMap API
  - User-friendly formatting

#### Database Service (`db.py`)
- **Purpose**: Persistent storage for interactions
- **Technology**: SQLite
- **Schema**:
  ```sql
  CREATE TABLE logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      query TEXT,
      response TEXT
  )
  ```

#### Groq AI Service
- **Model**: LLaMA 3.1-8B-Instant
- **Purpose**: Natural language understanding and tool selection
- **Output**: Structured JSON for tool calling

### 5. **External Services**

#### OpenWeatherMap API
- **Purpose**: Real-time weather data
- **Features**: Current conditions, temperature, humidity
- **Authentication**: API key required

#### Groq Cloud Platform
- **Purpose**: AI model hosting and inference
- **Model**: LLaMA 3.1-8B-Instant
- **Authentication**: API key required

## 🔄 Data Flow

### 1. **Request Flow**
```
User Input → Streamlit → FastAPI → Agent Controller → Groq AI
                                        ↓
                                   Tool Selection
                                        ↓
                                 Tool Execution → External APIs
                                        ↓
                                  Response Format → Database Log
                                        ↓
                                FastAPI → Streamlit → User
```

### 2. **Tool Execution Flow**
```
AI Response → JSON Parse → Function Map Lookup → Tool Execution
     ↓              ↓              ↓                    ↓
Error Handle → Validation → Parameter Extract → Result Return
```

## 🛡️ Security Architecture

### Authentication & Authorization
- **API Keys**: Secure storage in environment variables
- **CORS**: Configured for cross-origin requests
- **Input Validation**: Pydantic models for request validation

### Data Protection
- **Environment Variables**: Sensitive data isolation
- **Local Database**: SQLite for local data storage
- **No User Data Transmission**: Weather queries only send city names

## 📊 Performance Considerations

### Scalability
- **Stateless Design**: Each request is independent
- **Async Support**: FastAPI supports async operations
- **Database**: SQLite suitable for moderate loads

### Optimization
- **Connection Reuse**: Database connection persistence
- **Error Handling**: Graceful degradation
- **Response Caching**: Potential for weather data caching

## 🔧 Configuration Management

### Environment Variables
```env
GROQ_API_KEY=<groq_api_key>
WEATHER_API_KEY=<openweathermap_api_key>
```

### Application Settings
- **Model**: llama-3.1-8b-instant
- **Temperature**: Default (controlled by Groq)
- **Max Tokens**: Default (controlled by Groq)

## 🚀 Deployment Architecture

### Development
```
Local Machine
├── Python Environment
├── SQLite Database
├── Environment Variables (.env)
└── Multiple Processes (FastAPI + Streamlit)
```

### Production Options

#### Option 1: Streamlit Cloud
```
Streamlit Cloud
├── GitHub Integration
├── Environment Variables (Streamlit Secrets)
├── Automatic Deployments
└── HTTPS/SSL Included
```

#### Option 2: Container Deployment
```
Docker Container
├── Python Runtime
├── Application Code
├── Dependencies (requirements.txt)
└── Environment Variables
```

## 🔍 Monitoring & Logging

### Application Logs
- **Database Logging**: All interactions stored in SQLite
- **Error Tracking**: Exception handling and logging
- **Request Tracking**: API endpoint monitoring

### Health Checks
- **API Endpoint**: `/chat` availability
- **Database**: Connection status
- **External APIs**: Service availability

## 🔮 Future Architecture Enhancements

### Scalability Improvements
- **Database Migration**: PostgreSQL for production
- **Caching Layer**: Redis for response caching
- **Load Balancing**: Multiple API instances

### Feature Extensions
- **Authentication**: User management system
- **Rate Limiting**: API usage controls
- **Monitoring**: Application performance monitoring
- **Message Queue**: Async task processing

### Security Enhancements
- **API Authentication**: JWT tokens
- **Input Sanitization**: Enhanced validation
- **Audit Logging**: Comprehensive activity logs

---

This architecture provides a solid foundation for the AI Tool Calling Agent while maintaining flexibility for future enhancements and scalability requirements.