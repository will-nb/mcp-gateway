from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.isbn.client_base import HttpClient
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, api_key: str, timeout: float = 10.0) -> NormalizedBook:
    client = HttpClient(base_url="https://api2.isbndb.com", timeout=timeout)
    r = client.get(f"/book/{isbn}", headers={"X-API-KEY": api_key})
    data = r.json()
    payload = data.get("book", {})
    book: NormalizedBook = {
        "source": "isbndb",
        "isbn": isbn,
        "title": payload.get("title"),
        "subtitle": payload.get("edition_info"),
        "creators": [{"name": a, "role": None} for a in (payload.get("authors") or [])],
        "publisher": payload.get("publisher"),
        "published_date": payload.get("date_published") or payload.get("date_published_print") or payload.get("date_published_ebook"),
        "language": payload.get("language"),
        "subjects": payload.get("subjects") or [],
        "description": payload.get("overview"),
        "page_count": payload.get("pages"),
        "identifiers": {"isbn_10": payload.get("isbn"), "isbn_13": payload.get("isbn13")},
        "cover": {},
        "preview_urls": [],
        "raw": data,
    }
    client.close()
    return book
