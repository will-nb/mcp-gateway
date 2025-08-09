import types
from fastapi.testclient import TestClient
from app.main import app


def test_ai_chat_api(monkeypatch):
    client = TestClient(app)

    class FakeQwen:
        def chat_completion(self, model, messages, stream=False, extra_body=None):
            return {"choices": [{"message": {"role": "assistant", "content": "hi"}}]}

    monkeypatch.setattr("app.api.v1.endpoints.ai.get_qwen_client", lambda: FakeQwen())

    r = client.post("/api/v1/ai/chat", json={
        "model": "qwen-plus",
        "messages": [{"role": "user", "content": "hello"}]
    })
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "ai_chat"
    assert "raw" in body["data"]
