from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import rag
import db_queries

app = FastAPI()

print("\n\n==================================================")
print("   RAG CHATBOT SERVER STARTING")
print("==================================================\n")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    query: str

# API Endpoints
@app.get("/api/health")
async def health_check():
    articles = db_queries.get_all_articles()
    return {"status": "ok", "service": "RAG Chatbot", "articles": len(articles)}

@app.post("/api/ask")
def ask_rag(request: QueryRequest):
    print(f"Received query: {request.query}")
    try:
        response = rag.query_rag(request.query)
        return {"response": response}
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_general(request: QueryRequest):
    print(f"Received chat: {request.query}")
    response = rag.query_general(request.query)
    return {"response": response}

@app.get("/api/queries")
def get_logs():
    print("Fetching logs...")
    logs = db_queries.get_recent_queries()
    return logs

@app.get("/api/articles")
def get_articles():
    print("Fetching articles...")
    return db_queries.get_all_articles()

@app.get("/api/users")
def get_users():
    print("Fetching users...")
    return db_queries.get_all_users()

@app.get("/api/categories")
def get_categories():
    print("Fetching categories...")
    return db_queries.get_all_categories()

@app.get("/api/feedback")
def get_feedback():
    print("Fetching feedback...")
    return db_queries.get_all_feedback()

# Serve Frontend
# Ensure frontend directory exists
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(
        os.path.join(frontend_path, 'index.html'),
        headers={"Cache-Control": "no-store, max-age=0"},
    )

if __name__ == "__main__":
    import uvicorn
    import traceback
    try:
        print("Starting server on http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print("\nCRITICAL SERVER ERROR:")
        traceback.print_exc()
        input("Press Enter to exit...")
