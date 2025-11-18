🚀 LangGraph Research Assistant

A multi-step, AI-powered research pipeline built using FastAPI, LangGraph, Gemini, and Ollama.
The system performs:

Web search

Web content extraction

Intelligent summarization

Structured report generation

Conditional routing (simple vs complex queries)

Background task execution

Fully async processing

```

📁 Project Structure

app/
├── api/
│   ├── router.py
│   └── research.py
│
├── models/
│   ├── request_models.py
│   ├── response_models.py
│   └── task_store.py
│
├── utils/
│   ├── logger.py
│   ├── retry.py
│   └── text_cleaner.py
│
├── tools/
│   ├── web_search_tool.py
│   ├── content_extractor_tool.py
│   └── summarizer_tool.py
│
├── services/
│   ├── graph/
│   │   ├── nodes.py
│   │   ├── router.py
│   │   └── executor.py
│   │
│   ├── research_service.py
│
├── config/
│   ├── settings.py
│   └── environment.py
│
└── main.py
```

```
⚙️ Installation
1️⃣ Clone the repository

git clone https://github.com/yourusername/langgraph-research-assistant.git
cd langgraph-research-assistant

2️⃣ create virtual environment and install dependencies
python -m venv env

3️⃣ Create .env file

Copy the example:

cp .env.example .env


🧠 Run the Application

Start FastAPI server:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000






