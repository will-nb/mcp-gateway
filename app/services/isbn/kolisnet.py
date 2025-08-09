from __future__ import annotations

from typing import Any, Dict

from app.services.isbn.client_base import HttpClient, RateLimitError, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, service_key: str, timeout: float = 10.0) -> NormalizedBook:
    # Placeholder endpoint form; exact path to be updated per official docs
    client = HttpClient(base_url="https://api.nl.go.kr", timeout=timeout)
    r = client.get("/search", params={"serviceKey": service_key, "isbn": isbn, "format": "json"})
    if r.status_code in (403, 429):
        client.close()
        raise RateLimitError("kolisnet rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
    book: NormalizedBook = {
        "source": "kolisnet",
        "isbn": isbn,
        "title": None,
        "subtitle": None,
        "creators": [],
        "publisher": None,
        "published_date": None,
        "language": "ko",
        "subjects": [],
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": data if isinstance(data, dict) else {},
    }
    client.close()
    return book
