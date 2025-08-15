from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.isbn.client_base import (
    HttpClient,
    RateLimitError,
    HttpError,
    filter_alive_urls,
)
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(
    isbn: str,
    *,
    api_key: Optional[str] = None,
    lang: Optional[str] = None,
    timeout: float = 10.0,
) -> NormalizedBook:
    client = HttpClient(base_url="https://www.googleapis.com/books/v1", timeout=timeout)
    params: Dict[str, Any] = {"q": f"isbn:{isbn}", "maxResults": 1}
    if api_key:
        params["key"] = api_key
    if lang:
        params["langRestrict"] = lang
    r = client.get("/volumes", params=params)
    if r.status_code == 429 or r.status_code == 403:
        client.close()
        raise RateLimitError("google_books rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
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
        "access_urls": [],
        "raw": data,
    }
    try:
        items = data.get("items") or []
        if not items:
            return book
        vi = items[0].get("volumeInfo", {})
        book["title"] = vi.get("title")
        book["subtitle"] = vi.get("subtitle")
        book["creators"] = [
            {"name": a, "role": None} for a in (vi.get("authors") or [])
        ]
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
        # accessInfo for potential epub/pdf availability
        ai = items[0].get("accessInfo", {})
        urls: list[str] = []
        if ai.get("webReaderLink"):
            urls.append(ai.get("webReaderLink"))
        epub = ai.get("epub") or {}
        if epub.get("acsTokenLink"):
            urls.append(epub.get("acsTokenLink"))
        pdf = ai.get("pdf") or {}
        if pdf.get("acsTokenLink"):
            urls.append(pdf.get("acsTokenLink"))
        if urls:
            book["access_urls"] = filter_alive_urls(urls, timeout=5.0)
    finally:
        client.close()
    return book


def search_by_title(
    title: str,
    *,
    api_key: Optional[str] = None,
    lang: Optional[str] = None,
    max_results: int = 5,
    timeout: float = 10.0,
) -> List[NormalizedBook]:
    client = HttpClient(base_url="https://www.googleapis.com/books/v1", timeout=timeout)
    params: Dict[str, Any] = {"q": f"intitle:{title}", "maxResults": max_results}
    if api_key:
        params["key"] = api_key
    if lang:
        params["langRestrict"] = lang
    r = client.get("/volumes", params=params)
    if r.status_code == 429 or r.status_code == 403:
        client.close()
        raise RateLimitError("google_books rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    items = data.get("items") or []
    results: List[NormalizedBook] = []
    for it in items:
        vi = it.get("volumeInfo", {})
        nb: NormalizedBook = {
            "source": "google_books",
            "isbn": (
                next(
                    (
                        i.get("identifier")
                        for i in (vi.get("industryIdentifiers") or [])
                        if i.get("type") == "ISBN_13"
                    ),
                    None,
                )
                or ""
            ),
            "title": vi.get("title"),
            "subtitle": vi.get("subtitle"),
            "creators": [{"name": a, "role": None} for a in (vi.get("authors") or [])],
            "publisher": vi.get("publisher"),
            "published_date": vi.get("publishedDate"),
            "language": vi.get("language"),
            "subjects": list(vi.get("categories") or []),
            "description": vi.get("description"),
            "page_count": vi.get("pageCount"),
            "identifiers": {},
            "cover": vi.get("imageLinks") or {},
            "preview_urls": [
                u for u in [vi.get("previewLink"), vi.get("infoLink")] if u
            ],
            "access_urls": [],
            "raw": it,
        }
        results.append(nb)
    client.close()
    return results
