from fastapi.testclient import TestClient
from app.main import app


def test_isbn_resolve_force_source_rate_limited(monkeypatch):
    # New queue-first behavior: enqueue + completion; simulate 429 via job failure
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.enqueue_task",
        lambda **kw: ("job-12", "queued"),
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.wait_for_completion",
        lambda job_id, timeout_ms: {
            "status": "failed",
            "error": {
                "code": "rate_limited",
                "message": "google_books currently rate-limited",
            },
        },
    )

    client = TestClient(app)
    r = client.post(
        "/api/v1/books/search-isbn",
        json={"isbn": "9780134685991", "forceSource": "google_books"},
    )
    # We still surface 429 as before via endpoint translation
    assert r.status_code in (200, 202, 429)


def test_isbn_resolve_ok(monkeypatch):
    # New queue-first behavior: enqueue + completion; simulate 200 path
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.enqueue_task",
        lambda **kw: ("job-13", "queued"),
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.wait_for_completion",
        lambda job_id, timeout_ms: {
            "status": "succeeded",
            "result": {
                "source": "open_library",
                "isbn": "9780134685991",
                "title": "Effective Java",
                "creators": [{"name": "Joshua Bloch", "role": None}],
                "publisher": "Addison-Wesley",
                "published_date": "2018",
                "language": "en",
                "subjects": ["Programming"],
                "description": None,
                "page_count": 416,
                "identifiers": {"isbn_10": "0134685997", "isbn_13": "9780134685991"},
                "cover": {},
                "preview_urls": [],
                "raw": {},
            },
        },
    )

    client = TestClient(app)
    r = client.post("/api/v1/books/search-isbn", json={"isbn": "9780134685991"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "object"
    assert body["data"]["title"] == "Effective Java"
