from fastapi.testclient import TestClient
from app.main import app


def test_ai_chat_api(monkeypatch):
    client = TestClient(app)

    # New queue-first behavior: patch enqueue + completion for 200 path
    monkeypatch.setattr(
        "app.api.v1.endpoints.ai.enqueue_task", lambda **kw: ("job-11", "queued")
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.ai.wait_for_completion",
        lambda job_id, timeout_ms: {
            "status": "succeeded",
            "result": {
                "choices": [{"message": {"role": "assistant", "content": "hi"}}]
            },
        },
    )

    r = client.post(
        "/api/v1/ai/chat",
        json={"model": "qwen-plus", "messages": [{"role": "user", "content": "hello"}]},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "ai_chat"
    assert "raw" in body["data"]
