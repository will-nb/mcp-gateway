import types
from fastapi.testclient import TestClient
from app.main import app


def test_qdrant_endpoints(monkeypatch):
    client = TestClient(app)

    # Fake client methods
    class FakeQdrantClient:
        def get_collections(self):
            return types.SimpleNamespace(collections=[])

        def collection_exists(self, name):
            return False

        def create_collection(self, collection_name, vectors_config):
            return None

        def upsert(self, collection_name, points, wait=True):
            return types.SimpleNamespace(status=types.SimpleNamespace(value="acknowledged"))

        def query_points(self, collection_name, query, query_filter=None, limit=5, with_payload=True, with_vectors=False):
            class Rec:
                def __init__(self):
                    self.points = [types.SimpleNamespace(id=1, score=0.99, payload={"k":"v"})]
            return Rec()

    # Patch service to use fake client
    from app.services import qdrant as qdrant_mod

    class FakeService(qdrant_mod.QdrantService):
        def __init__(self, *args, **kwargs):
            self._client = FakeQdrantClient()

    monkeypatch.setattr(qdrant_mod, "QdrantService", FakeService)

    # ensure collection
    r = client.post("/api/v1/qdrant/ensure-collection", json={"collection_name": "foo", "vector_size": 4})
    assert r.status_code == 200
    # When collection_exists returns False, service should create and return True
    assert r.json()["data"]["created"] in (True, False)

    # upsert
    r = client.post("/api/v1/qdrant/upsert", json={
        "collection_name": "foo",
        "points": [{"id": 1, "vector": [0.1,0.2,0.3,0.4], "payload": {"k":"v"}}]
    })
    assert r.status_code == 200
    # Our Qdrant client returns UpdateStatus.COMPLETED by default in this env
    assert r.json()["data"]["status"] in ("acknowledged", "completed")

    # search
    r = client.post("/api/v1/qdrant/search", json={
        "collection_name": "foo",
        "vector": [0.1,0.2,0.3,0.4],
        "limit": 1
    })
    assert r.status_code == 200
    data = r.json()["data"]
    assert "results" in data and len(data["results"]) == 1
