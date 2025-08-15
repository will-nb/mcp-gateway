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

    # Patch mongo health to avoid real connection
    async def fake_mongo_health():
        return {"status": "healthy", "message": "ok"}

    monkeypatch.setattr("app.core.mongo_async.get_mongo_health", fake_mongo_health)
    monkeypatch.setattr(
        "qdrant_client.QdrantClient.get_collections",
        fake_qdrant_get_collections,
        raising=False,
    )
    monkeypatch.setattr(
        "app.services.redis_client.get_redis_service", lambda: FakeRedisService()
    )

    client = TestClient(app)
    res = client.get("/api/v1/welcome/health").json()
    assert res["success"] is True
    assert res["dataType"] == "health"
    services = res["data"]["services"]
    assert services["qdrant"]["status"] in ("healthy", "unhealthy")
    assert services["redis"]["status"] in ("healthy", "unhealthy")


def test_health_qdrant_down(monkeypatch):
    def fake_qdrant_get_collections(self):
        raise RuntimeError("down")

    class FakeRedisService:
        def ping(self):
            return True

    async def fake_mongo_health2():
        return {"status": "healthy", "message": "ok"}

    monkeypatch.setattr("app.core.mongo_async.get_mongo_health", fake_mongo_health2)
    monkeypatch.setattr(
        "qdrant_client.QdrantClient.get_collections",
        fake_qdrant_get_collections,
        raising=False,
    )
    monkeypatch.setattr(
        "app.services.redis_client.get_redis_service", lambda: FakeRedisService()
    )

    client = TestClient(app)
    res = client.get("/api/v1/welcome/health").json()
    assert res["success"] is True
    assert res["dataType"] == "health"
    assert res["data"]["services"]["qdrant"]["status"] == "unhealthy"


def test_health_redis_down(monkeypatch):
    def fake_qdrant_get_collections(self):
        return types.SimpleNamespace(collections=[])

    class FakeRedisService:
        def ping(self):
            return False

    async def fake_mongo_health3():
        return {"status": "healthy", "message": "ok"}

    monkeypatch.setattr("app.core.mongo_async.get_mongo_health", fake_mongo_health3)
    monkeypatch.setattr(
        "qdrant_client.QdrantClient.get_collections",
        fake_qdrant_get_collections,
        raising=False,
    )
    monkeypatch.setattr(
        "app.services.redis_client.get_redis_service", lambda: FakeRedisService()
    )

    client = TestClient(app)
    res = client.get("/api/v1/welcome/health").json()
    assert res["success"] is True
    assert res["dataType"] == "health"
    assert res["data"]["services"]["redis"]["status"] == "unhealthy"
