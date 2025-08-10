from fastapi.testclient import TestClient
from app.main import app


def test_isbn_resolve_force_source_rate_limited(monkeypatch):
    # Simulate rate-limited source via manager raising RateLimitError
    from app.services.isbn.client_base import RateLimitError

    def fake_resolve(*args, **kwargs):
        raise RateLimitError("google_books currently rate-limited")

    monkeypatch.setattr("app.services.isbn.manager.resolve_isbn", fake_resolve)

    client = TestClient(app)
    r = client.post("/api/v1/books/search-isbn", json={
        "isbn": "9780134685991",
        "forceSource": "google_books"
    })
    assert r.status_code == 429


def test_isbn_resolve_ok(monkeypatch):
    def fake_resolve(isbn, **kwargs):
        return {
            "source": "open_library",
            "isbn": isbn,
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
            "raw": {}
        }

    monkeypatch.setattr("app.services.isbn.manager.resolve_isbn", fake_resolve)

    client = TestClient(app)
    r = client.post("/api/v1/books/search-isbn", json={
        "isbn": "9780134685991"
    })
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "object"
    assert body["data"]["title"] == "Effective Java"
