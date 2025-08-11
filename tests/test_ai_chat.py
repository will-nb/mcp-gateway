from fastapi.testclient import TestClient
from app.main import app


def test_chat_completion_invalid_model():
    client = TestClient(app)
    r = client.post('/api/v1/ai/chat', json={
        'model': 'not-allowed',
        'messages': [{'role': 'user', 'content': 'hi'}]
    })
    assert r.status_code == 400


def test_chat_completion_ok(monkeypatch):
    client = TestClient(app)

    # New behavior: enqueue + wait_for_completion; we simulate immediate success
    monkeypatch.setattr('app.api.v1.endpoints.ai.enqueue_task', lambda **kw: ("job-1", "queued"))
    monkeypatch.setattr('app.api.v1.endpoints.ai.wait_for_completion', lambda job_id, timeout_ms: {
        "status": "succeeded",
        "result": {"choices": [{"message": {"role": "assistant", "content": "hello"}}]}
    })

    r = client.post('/api/v1/ai/chat', json={
        'model': 'qwen-plus',
        'messages': [{'role': 'user', 'content': 'hi'}]
    })
    assert r.status_code == 200
    body = r.json()
    assert body['success'] is True
    assert body['dataType'] == 'ai_chat'
    assert 'raw' in body['data']
