from fastapi.testclient import TestClient
from app.main import app


def test_welcome_health_live():
    client = TestClient(app)
    res = client.get("/api/v1/welcome/health")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["dataType"] == "health"
    assert "services" in body["data"]
    assert set(body["data"]["services"].keys()) >= {"mongodb", "redis", "qdrant"}
