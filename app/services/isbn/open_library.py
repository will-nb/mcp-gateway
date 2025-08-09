from __future__ import annotations

from typing import Any, Dict, List

from app.services.isbn.client_base import HttpClient, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    client = HttpClient(base_url="https://openlibrary.org", timeout=timeout)
    # Try data API first
    r = client.get("/api/books", params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"})
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    book_key = f"ISBN:{isbn}"
    payload = data.get(book_key) or {}
    book: NormalizedBook = {
        "source": "open_library",
        "isbn": isbn,
        "title": payload.get("title"),
        "subtitle": payload.get("subtitle"),
        "creators": [{"name": a.get("name"), "role": None} for a in (payload.get("authors") or [])],
        "publisher": (payload.get("publishers") or [{}])[0].get("name") if payload.get("publishers") else None,
        "published_date": payload.get("publish_date"),
        "language": None,
        "subjects": [s.get("name") for s in (payload.get("subjects") or []) if s.get("name")],
        "description": payload.get("description") if isinstance(payload.get("description"), str) else None,
        "page_count": payload.get("number_of_pages"),
        "identifiers": {},
        "cover": payload.get("cover") or {},
        "preview_urls": [],
        "raw": data,
    }
    # identifiers if present in "identifiers" field
    ids = payload.get("identifiers") or {}
    if isinstance(ids, dict):
        if ids.get("isbn_10"):
            book["identifiers"]["isbn_10"] = ids.get("isbn_10")[0]
        if ids.get("isbn_13"):
            book["identifiers"]["isbn_13"] = ids.get("isbn_13")[0]
    # Preview
    if payload.get("url"):
        book["preview_urls"].append(payload.get("url"))
    client.close()
    return book
