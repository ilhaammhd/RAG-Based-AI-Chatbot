# RAG Based AI Chatbot

A lightweight local RAG-style chatbot that answers questions from a SQL-like knowledge base stored in `database.txt`.

The app parses the uploaded database file, retrieves relevant records, and returns structured answers through a simple web chat interface. It runs fully locally and does not require Groq, OpenAI, MongoDB, FAISS, or sentence-transformers.

## Features

- Local chatbot over `database.txt`
- FastAPI backend
- Plain HTML/CSS/JavaScript frontend
- Local keyword-based retrieval
- Article, category, author, user, email, and role lookup
- Article feedback ratings with a visual graph
- Query history stored locally at runtime
- No external AI API required

## Tech Stack

- Python
- FastAPI
- Uvicorn
- HTML
- CSS
- JavaScript

## Project Structure

```text
RAG-Based-AI-Chatbot/
├── .gitignore
├── database.txt
└── rag-db/
    ├── README.md
    ├── backend/
    │   ├── db_queries.py
    │   ├── kb_loader.py
    │   ├── main.py
    │   ├── rag.py
    │   ├── requirements.txt
    │   └── test_system.py
    └── frontend/
        └── index.html


        Setup
Install the required Python packages:

cd rag-db/backend
python -m pip install -r requirements.txt

Run
Start the FastAPI server:
python main.py

Open the chatbot in your browser:

http://127.0.0.1:8000
Keep the terminal open while using the chatbot.

Example Questions
How do I create a database in SQL Server?
What are Table Valued Parameters?
How to read emails using IMAP?
Explain JWT authentication.
Compare article ratings in a graph.
Show users name and gmail.
What is Srini email?
Who are the authors?
API Endpoints
GET  /              Web chat UI
GET  /api/health    Server status
POST /api/ask       Ask a database question
POST /api/chat      General local database chat
GET  /api/articles  List articles
GET  /api/users     List users
GET  /api/queries   Query history
GET  /api/feedback  Article feedback
Data Source
The chatbot reads from database.txt.

Implemented tables:

kb_categories
kb_users
kb_articles
kb_article_feedback
