from fastapi.testclient import TestClient
from app.main import app


def test_books_search_title_minimal(monkeypatch):
    # New behavior: enqueue + completion; patch endpoint symbols
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.enqueue_task",
        lambda **kw: ("job-2", "queued"),
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.wait_for_completion",
        lambda job_id, timeout_ms: {
            "status": "succeeded",
            "result": [
                {
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
                    "identifiers": {
                        "isbn_10": "0134685997",
                        "isbn_13": "9780134685991",
                    },
                    "cover": {},
                    "preview_urls": [],
                    "raw": {},
                }
            ],
        },
    )

    client = TestClient(app)
    r = client.post("/api/v1/books/search-title", json={"title": "Effective Java"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "list"
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["title"] == "Effective Java"


def test_books_search_isbn_minimal(monkeypatch):
    # New behavior: enqueue + completion; patch endpoint symbols
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.enqueue_task",
        lambda **kw: ("job-3", "queued"),
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.book_search.wait_for_completion",
        lambda job_id, timeout_ms: {
            "status": "succeeded",
            "result": {
                "source": "juhe_isbn",
                "isbn": "9787801207647",
                "title": "成功人士的七个习惯",
                "creators": [{"name": "史蒂芬·柯维", "role": None}],
                "publisher": "中国华侨出版社",
                "published_date": "2003-12",
                "language": "zh",
                "subjects": [],
                "description": "...",
                "page_count": None,
                "identifiers": {"isbn_10": "7801207645", "isbn_13": "9787801207647"},
                "cover": {},
                "preview_urls": [],
                "raw": {},
            },
        },
    )

    client = TestClient(app)
    r = client.post("/api/v1/books/search-isbn", json={"isbn": "9787801207647"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["dataType"] == "object"
    assert body["data"]["identifiers"]["isbn_13"] == "9787801207647"
