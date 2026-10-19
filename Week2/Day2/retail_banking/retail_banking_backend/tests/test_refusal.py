from fastapi.testclient import TestClient

import agent
import agent_tools
from main import app

client = TestClient(app)

class FakeTextBlock:
    type = "text"

    def __init__(self, text: str):
        self.text = text


class FakeUsage:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens = i, o


class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.content, self.stop_reason, self.usage = content, stop_reason, usage


REFUSAL_SENTENCE = "The provided documents do not answer that question."


def test_refuses_when_no_documents_clear_relevance_floor(monkeypatch):
    monkeypatch.setattr(agent_tools, "search_knowledge_base", lambda query, top_k=3: [])

    def fake_generate(**kwargs):
        return FakeResponse([FakeTextBlock(REFUSAL_SENTENCE)], "end_turn", FakeUsage(100, 10))

    monkeypatch.setattr(agent, "generate_with_tools", fake_generate)

    response = client.post("/agent/ask", json={"question": "what is the exact redress amount?"})
    assert REFUSAL_SENTENCE in response.json()["answer"]


def test_refuses_to_state_specific_redress_amount(monkeypatch):
    def fake_generate(**kwargs):
        return FakeResponse(
            [FakeTextBlock("I cannot advise a specific redress amount. Please apply the redress methodology.")],
            "end_turn",
            FakeUsage(100, 20),
        )

    monkeypatch.setattr(agent, "generate_with_tools", fake_generate)

    response = client.post("/agent/ask", json={"question": "how much should we pay for complaint 3?"})
    body = response.json()

    assert "£" not in body["answer"]
    assert body["complete"] is True


def test_complete_is_true_on_refusal(monkeypatch):
    def fake_generate(**kwargs):
        return FakeResponse([FakeTextBlock(REFUSAL_SENTENCE)], "end_turn", FakeUsage(100, 10))

    monkeypatch.setattr(agent, "generate_with_tools", fake_generate)

    response = client.post("/agent/ask", json={"question": "anything unanswerable"})
    assert response.json()["complete"] is True