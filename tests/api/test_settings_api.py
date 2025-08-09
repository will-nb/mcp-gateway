from fastapi.testclient import TestClient
from app.main import app


def test_public_settings_api():
    client = TestClient(app)
    r = client.get("/api/v1/settings")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "object"
    # camelCase not enforced for settings; ensure keys exist
    assert "app_name" in body["data"]
    assert "version" in body["data"]
