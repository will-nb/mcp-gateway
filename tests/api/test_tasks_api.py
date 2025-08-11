from __future__ import annotations

import json
from fastapi.testclient import TestClient

from app.main import app


def test_tasks_enqueue_ocr_accepts_defaults(monkeypatch):
    client = TestClient(app)

    # Patch the symbol used by the endpoint module to avoid touching Mongo/Redis
    monkeypatch.setattr("app.api.v1.endpoints.tasks.enqueue_task", lambda **kw: ("job-123", "queued"))

    r = client.post(
        "/api/v1/tasks/ocr",
        headers={"X-Task-Class": "interactive"},
        json={"payloadRef": "r2://bucket/key", "syncTimeoutMs": 0}
    )
    assert r.status_code in (200, 202)
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "object"
    assert body["data"]["job_id"] == "job-123" or body["data"].get("jobId") == "job-123"


def test_tasks_enqueue_rejects_callback_outside_whitelist(monkeypatch):
    client = TestClient(app)

    # Patch endpoint-level function to raise validation error
    def raise_error(**kwargs):
        raise ValueError("callbackUrl not allowed by whitelist")

    monkeypatch.setattr("app.api.v1.endpoints.tasks.enqueue_task", lambda **kw: raise_error(**kw))

    r = client.post(
        "/api/v1/tasks/isbn",
        headers={"X-Task-Class": "interactive"},
        json={"payloadRef": "r2://bucket/key", "callbackUrl": "https://evil.example.com/hook"}
    )
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["message"].endswith("callbackUrl not allowed by whitelist")


def test_jobs_status_and_cancel(monkeypatch):
    client = TestClient(app)

    # Patch symbols used by jobs endpoint
    monkeypatch.setattr("app.api.v1.endpoints.jobs.get_job", lambda job_id: {"id": job_id, "status": "queued"})
    monkeypatch.setattr("app.api.v1.endpoints.jobs.cancel_job", lambda job_id: True)

    r = client.get("/api/v1/jobs/job-xyz")
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["id"] == "job-xyz"

    r2 = client.delete("/api/v1/jobs/job-xyz")
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["data"]["jobId"] == "job-xyz"
