import anthropic
import httpx
from fastapi.testclient import TestClient

import llm
import routers.insights as insights_router
from main import app

client = TestClient(app)

FAKE_SUMMARY = {
    "text": "This complaint concerns a late payment fee applied in error.",
    "input_tokens": 120,
    "output_tokens": 40,
    "stop_reason": "end_turn",
}

FAKE_ANALYSIS = {
    "structured_output": {
        "theme": "fees",
        "severity": "medium",
        "vulnerability_concern": False,
        "consumer_duty_risk": False,
        "recommended_next_step": "offer_redress",
        "redress_category": ["fee_refund"],
        "rationale": "A late payment fee was applied in error. The bank should refund it.",
        "confidence": "high",
        "caveats": [],
    },
    "input_tokens": 200,
    "output_tokens": 60,
    "stop_reason": "end_turn",
}


# --- summary ---

def test_summary_returns_text_and_usage(monkeypatch):
    monkeypatch.setattr(insights_router, "generate", lambda system, user: FAKE_SUMMARY)
    response = client.post("/complaints/1/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["input_tokens"] == 120
    assert "text" in body


def test_summary_provider_timeout_returns_504(monkeypatch):
    def boom(system, user):
        raise anthropic.APITimeoutError(request=None)
    monkeypatch.setattr(insights_router, "generate", boom)
    assert client.post("/complaints/1/summary").status_code == 504


def test_summary_rate_limit_returns_429(monkeypatch):
    def boom(system, user):
        raise anthropic.RateLimitError(
            message="rate limited",
            response=httpx.Response(429, request=httpx.Request("POST", "https://api.anthropic.com")),
            body=None,
        )
    monkeypatch.setattr(insights_router, "generate", boom)
    assert client.post("/complaints/1/summary").status_code == 429


def test_summary_unknown_complaint_returns_404():
    assert client.post("/complaints/999/summary").status_code == 404


# --- token estimate ---

def test_estimate_does_not_call_the_model(monkeypatch):
    monkeypatch.setattr(llm, "estimate_input_tokens", lambda system, user: 137)
    response = client.get("/complaints/1/summary/estimate")
    assert response.status_code == 200
    assert response.json()["estimated_input_tokens"] == 137


# --- streaming ---

def test_stream_yields_chunks(monkeypatch):
    monkeypatch.setattr(insights_router, "stream", lambda system, user: iter(["Late ", "payment ", "fee."]))
    with client.stream("GET", "/complaints/1/summary/stream") as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    assert body == "Late payment fee."


# --- structured analysis ---

def test_analyse_returns_all_schema_fields(monkeypatch):
    monkeypatch.setattr(llm, "generate_structured", lambda system, user, response_model: FAKE_ANALYSIS)
    response = client.post("/complaints/1/analyse")
    assert response.status_code == 200
    analysis = response.json()["analysis"]
    assert analysis["theme"] == "fees"
    assert analysis["recommended_next_step"] == "offer_redress"
    assert isinstance(analysis["redress_category"], list)
    assert analysis["vulnerability_concern"] is False


def test_analyse_unknown_complaint_returns_404():
    assert client.post("/complaints/999/analyse").status_code == 404
