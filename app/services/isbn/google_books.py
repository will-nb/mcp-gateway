from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.isbn.client_base import HttpClient
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, api_key: Optional[str] = None, lang: Optional[str] = None, timeout: float = 10.0) -> NormalizedBook:
    client = HttpClient(base_url="https://www.googleapis.com/books/v1", timeout=timeout)
    params: Dict[str, Any] = {"q": f"isbn:{isbn}", "maxResults": 1}
    if api_key:
        params["key"] = api_key
    if lang:
        params["langRestrict"] = lang
    r = client.get("/volumes", params=params)
    data = r.json()
    book: NormalizedBook = {
        "source": "google_books",
        "isbn": isbn,
        "title": None,
        "subtitle": None,
        "creators": [],
        "publisher": None,
        "published_date": None,
        "language": None,
        "subjects": [],
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": data,
    }
    try:
        items = data.get("items") or []
        if not items:
            return book
        vi = items[0].get("volumeInfo", {})
        book["title"] = vi.get("title")
        book["subtitle"] = vi.get("subtitle")
        book["creators"] = [{"name": a, "role": None} for a in (vi.get("authors") or [])]
        book["publisher"] = vi.get("publisher")
        book["published_date"] = vi.get("publishedDate")
        book["language"] = vi.get("language")
        book["subjects"] = list(vi.get("categories") or [])
        book["description"] = vi.get("description")
        book["page_count"] = vi.get("pageCount")
        ids = vi.get("industryIdentifiers") or []
        for it in ids:
            t = (it.get("type") or "").lower()
            val = it.get("identifier")
            if t == "isbn_10":
                book.setdefault("identifiers", {})["isbn_10"] = val
            if t == "isbn_13":
                book.setdefault("identifiers", {})["isbn_13"] = val
        links = vi.get("imageLinks") or {}
        if links:
            book["cover"] = {
                "small": links.get("smallThumbnail"),
                "thumbnail": links.get("thumbnail"),
            }
        if vi.get("previewLink"):
            book["preview_urls"].append(vi.get("previewLink"))
        if vi.get("infoLink"):
            book["preview_urls"].append(vi.get("infoLink"))
    finally:
        client.close()
    return book
