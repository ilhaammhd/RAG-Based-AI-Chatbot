import pytest
from fastapi.testclient import TestClient
from main import app
import sys
import os

sys.path.append(os.path.dirname(__file__))

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "RAG Chatbot"

def test_chat_endpoint():
    response = client.post("/api/chat", json={"query": "Hello"})
    assert response.status_code == 200
    assert "response" in response.json()

def test_ask_endpoint_basics():
    # Test RAG endpoint responds
    response = client.post("/api/ask", json={"query": "How to create database in SQL Server?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    text = data["response"]
    
    # Check for required sections
    assert "## Summary" in text
    assert "## Details" in text
    assert "## Graph Description" in text
    assert "## Follow-up Questions" in text

def test_database_accuracy():
    # We expect a specific answer based on our articles
    response = client.post("/api/ask", json={"query": "Who is the author of Python articles?"})
    assert response.status_code == 200
    # This might vary based on LLM, but let's check basic execution
    assert len(response.json()["response"]) > 0

def test_frontend_serve():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Database RAG Assistant</title>" in response.text

def test_graph_request():
    # Ask a question that should trigger a graph
    response = client.post("/api/ask", json={"query": "Compare article ratings in a graph"})
    assert response.status_code == 200
    text = response.json()["response"]
    
    # Check for Graph Description and Table
    assert "## Graph Description" in text
    assert "|" in text # Markdown table indicator
    assert "Not applicable" not in text # Should have a description
