import types
from fastapi.testclient import TestClient

from app.main import app


def test_health_mongo_ok(monkeypatch):
    # Patch qdrant reachability
    def fake_qdrant_get_collections(self):
        return types.SimpleNamespace(collections=[])

    # Patch redis ping
    class FakeRedisService:
        def ping(self):
            return True

    class FakeMongoClient:
        def server_info(self):
            return {"ok": 1}

    monkeypatch.setattr("qdrant_client.QdrantClient.get_collections", fake_qdrant_get_collections, raising=False)
    monkeypatch.setattr("app.services.redis_client.get_redis_service", lambda: FakeRedisService())
    monkeypatch.setattr("app.services.mongo_client.get_mongo_client", lambda: FakeMongoClient())

    client = TestClient(app)
    res = client.get("/api/v1/welcome/health").json()
    assert res["success"] is True
    assert res["dataType"] == "health"
    assert res["data"]["services"]["mongodb"]["status"] == "healthy"


def test_health_mongo_down(monkeypatch):
    def fake_qdrant_get_collections(self):
        return types.SimpleNamespace(collections=[])

    class FakeRedisService:
        def ping(self):
            return True

    class FakeMongoClient:
        def server_info(self):
            raise RuntimeError("down")

    monkeypatch.setattr("qdrant_client.QdrantClient.get_collections", fake_qdrant_get_collections, raising=False)
    monkeypatch.setattr("app.services.redis_client.get_redis_service", lambda: FakeRedisService())
    monkeypatch.setattr("app.services.mongo_client.get_mongo_client", lambda: FakeMongoClient())

    client = TestClient(app)
    res = client.get("/api/v1/welcome/health").json()
    assert res["success"] is True
    assert res["dataType"] == "health"
    assert res["data"]["services"]["mongodb"]["status"] == "unhealthy"
