"""
knowledge endpoints tests
"""
from fastapi.testclient import TestClient
from main import app
import llm
import knowledge_store as knowledge


client = TestClient(app)
