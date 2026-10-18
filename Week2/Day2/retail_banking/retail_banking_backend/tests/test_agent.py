import agent
import agent_tools
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class FakeToolUseBlock:
    type = "tool_use"
    id = "toolu_1"
    name = "search_knowledge_base"

    def __init__(self, input_: dict):
        self.input = input_


class FakeUsage:
    def __init__(self, i, o):
        self.input_tokens, self.output_tokens = i, o


class FakeResponse:
    def __init__(self, content, stop_reason, usage):
        self.content, self.stop_reason, self.usage = content, stop_reason, usage


def test_agent_stops_at_max_iterations_instead_of_looping_forever(monkeypatch):
    # always returns tool_use — agent must stop itself at MAX_ITERATIONS
    def fake_generate(**kwargs):
        return FakeResponse(
            [FakeToolUseBlock({"query": "anything"})],
            "tool_use",
            FakeUsage(100, 15),
        )

    monkeypatch.setattr(agent, "generate_with_tools", fake_generate)
    monkeypatch.setattr(
        agent_tools, "search_knowledge_base",
        lambda query, top_k=3: [{"id": "doc-001", "title": "t", "body": "x", "score": 0.9}],
    )

    response = client.post("/agent/ask", json={"question": "never resolves"})
    body = response.json()

    assert body["complete"] is False
    assert body["stop_reason"] == "tool_use"
    assert body["tool_calls_made"] == 4