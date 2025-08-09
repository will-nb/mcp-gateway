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

    class FakeQwen:
        def chat_completion(self, model, messages, stream=False, extra_body=None):
            return {'choices': [{'message': {'role': 'assistant', 'content': 'hello'}}]}

    # monkeypatch the factory used inside endpoint module
    monkeypatch.setattr('app.api.v1.endpoints.ai.get_qwen_client', lambda: FakeQwen())

    r = client.post('/api/v1/ai/chat', json={
        'model': 'qwen-plus',
        'messages': [{'role': 'user', 'content': 'hi'}]
    })
    assert r.status_code == 200
    body = r.json()
    assert body['success'] is True
    assert body['dataType'] == 'ai_chat'
    assert 'raw' in body['data']
