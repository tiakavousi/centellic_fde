"""
knowledge endpoints tests
"""
from fastapi.testclient import TestClient

import llm
import routers.knowledge as knowledge_router
from main import app

client = TestClient(app)

WEAK_HIT = {"id": "doc-001", "title": "some doc", "body": "some text", "score": 0.3}
STRONG_HIT = {"id": "doc-001", "title": "some doc", "body": "some text", "score": 0.9}


def test_ask_refuses_without_calling_the_model(monkeypatch):
    monkeypatch.setattr(knowledge_router, "search", lambda q, top_k=3: [WEAK_HIT])

    def must_not_be_called(q, c):
        raise AssertionError("The model was called despite no relevant context")

    monkeypatch.setattr(llm, "generate", must_not_be_called)

    body = client.post("/knowledge/ask", params={"query": "what is the capital of France"}).json()
    assert body["refused"] is True