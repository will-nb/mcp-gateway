import types
from fastapi.testclient import TestClient

from app.main import app


def test_health_ok(monkeypatch):
    # Patch qdrant reachability
    def fake_qdrant_get_collections(self):
        return types.SimpleNamespace(collections=[])

    # Patch redis ping
    class FakeRedisService:
        def ping(self):
            return True

    monkeypatch.setattr("qdrant_client.QdrantClient.get_collections", fake_qdrant_get_collections, raising=False)
    monkeypatch.setattr("app.services.redis_client.get_redis_service", lambda: FakeRedisService())

    client = TestClient(app)
    res = client.get("/api/v1/health").json()
    assert res["code"] == 0
    data = res["data"]
    assert data["qdrant"]["reachable"] is True
    assert data["redis"]["reachable"] is True


def test_health_qdrant_down(monkeypatch):
    def fake_qdrant_get_collections(self):
        raise RuntimeError("down")

    class FakeRedisService:
        def ping(self):
            return True

    monkeypatch.setattr("qdrant_client.QdrantClient.get_collections", fake_qdrant_get_collections, raising=False)
    monkeypatch.setattr("app.services.redis_client.get_redis_service", lambda: FakeRedisService())

    client = TestClient(app)
    res = client.get("/api/v1/health").json()
    assert res["code"] == 0
    assert res["data"]["qdrant"]["reachable"] is False
    assert res["data"]["redis"]["reachable"] is True


def test_health_redis_down(monkeypatch):
    def fake_qdrant_get_collections(self):
        return types.SimpleNamespace(collections=[])

    class FakeRedisService:
        def ping(self):
            return False

    monkeypatch.setattr("qdrant_client.QdrantClient.get_collections", fake_qdrant_get_collections, raising=False)
    monkeypatch.setattr("app.services.redis_client.get_redis_service", lambda: FakeRedisService())

    client = TestClient(app)
    res = client.get("/api/v1/health").json()
    assert res["code"] == 0
    assert res["data"]["qdrant"]["reachable"] is True
    assert res["data"]["redis"]["reachable"] is False
