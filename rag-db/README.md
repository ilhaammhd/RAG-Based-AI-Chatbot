# Database RAG Assistant

A lightweight local RAG-style chatbot that answers questions from a SQL-like knowledge base stored in `database.txt`.

The app parses the uploaded database file, retrieves relevant records, and returns structured answers through a simple web chat interface. It runs fully locally and does not require Groq, OpenAI, MongoDB, FAISS, or sentence-transformers.

## Features

- Local chatbot over `database.txt`
- FastAPI backend
- Plain HTML/CSS/JavaScript frontend
- Local keyword-based retrieval
- Article, category, author, user, email, and role lookup
- Article feedback ratings with a visual graph
- Query history stored locally in `query_logs.json`
- No external AI API required

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Vanilla JavaScript
- HTML/CSS

## Project Structure

```text
ai-database-assistant/
├── .gitignore
├── database.txt
└── rag-db/
    ├── backend/
    │   ├── db_queries.py
    │   ├── kb_loader.py
    │   ├── main.py
    │   ├── rag.py
    │   ├── requirements.txt
    │   └── test_system.py
    ├── frontend/
    │   └── index.html
    └── README.md
```

`query_logs.json` is created automatically at runtime and is ignored by Git.

## Data Source

The chatbot reads from `../database.txt`.

Implemented tables:

- `kb_categories`
- `kb_users`
- `kb_articles`
- `kb_article_feedback`

Books are not implemented because the current database file does not include book tables or book records.

## Setup

From the `rag-db/backend` folder, install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

Start the backend server:

```bash
cd rag-db/backend
python main.py
```

Open the app in your browser:

```text
http://127.0.0.1:8000
```

Keep the terminal open while using the chatbot.

## Stop

Press `Ctrl+C` in the terminal running `python main.py`.

If port `8000` is already in use, another server instance is already running. Open `http://127.0.0.1:8000` or stop the old process before starting again.

## Example Questions

- How do I create a database in SQL Server?
- What are Table Valued Parameters?
- How to read emails using IMAP?
- Explain JWT authentication.
- Compare article ratings in a graph.
- Show users name and gmail.
- What is Srini email?
- Who are the authors?

## API Endpoints

```text
GET  /              Web chat UI
GET  /api/health    Server status
POST /api/ask       Ask a database question
POST /api/chat      General local database chat
GET  /api/articles  List articles
GET  /api/users     List users
GET  /api/queries   Query history
GET  /api/feedback  Article feedback
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/ask \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Who are the authors?\"}"
```

## Notes

- This project is intentionally local-only.
- No `.env` file is required.
- No `run.bat` file is required.
- Query logs are stored locally in `query_logs.json`.
- Delete `query_logs.json` to clear chat history.
