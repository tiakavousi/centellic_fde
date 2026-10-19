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
FAKE_ANSWER = {"text": "Complaints must be acknowledged within three days [doc-001].",
                "input_tokens": 400, "output_tokens": 30, "stop_reason": "end_turn"}

def search_returns_ranked_hits(monkeypatch):
    monkeypatch.setattr(knowledge_router, "search", lambda q,top_k=3: [STRONG_HIT])
    response = client.get("/knowledge/search", params={'query': "complaint handling policy"})
    assert response.status_code == 200
    assert response.json()['hits'][0]['id'] == 'doc-001'

def test_search_before_indexing_is_409(monkeypatch):
    def not_built(q, top_k=3):
        raise RuntimeError("Index empty, build it via POST /knowledge/index")
    monkeypatch.setattr(knowledge_router, 'search', not_built)
    response = client.get('/knowledge/search', params={'query': 'anything'})
    assert response.status_code == 409

def test_ask_refuses_without_calling_the_model(monkeypatch):
    monkeypatch.setattr(knowledge_router, "search", lambda q, top_k=3: [WEAK_HIT])

    def must_not_be_called(system, user_prompt):
        raise AssertionError("The model was called despite no relevant context")

    monkeypatch.setattr(llm, "generate", must_not_be_called)

    body = client.post("/knowledge/ask", params={"query": "what is the capital of France"}).json()
    assert body["refused"] is True
    assert body['answer'] is None

def test_ask_answers_and_cites_sources(monkeypatch):
    monkeypatch.setattr(knowledge_router, 'search',lambda q, top_k=3: [STRONG_HIT])
    monkeypatch.setattr(llm, "generate", lambda system, user_prompt: FAKE_ANSWER)
    body = client.post("/knowledge/ask", params={"query": "how quickly must complaints be acknowledged"}).json()
    assert body["refused"] is False
    assert body["sources"][0]["id"] == "doc-001"
    assert body["input_tokens"] == 400