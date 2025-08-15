from __future__ import annotations

from typing import List

from app.services.isbn.client_base import HttpClient, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    client = HttpClient(base_url="https://openlibrary.org", timeout=timeout)
    # Try data API first
    r = client.get(
        "/api/books",
        params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
    )
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
        "creators": [
            {"name": a.get("name"), "role": None}
            for a in (payload.get("authors") or [])
        ],
        "publisher": (payload.get("publishers") or [{}])[0].get("name")
        if payload.get("publishers")
        else None,
        "published_date": payload.get("publish_date"),
        "language": None,
        "subjects": [
            s.get("name") for s in (payload.get("subjects") or []) if s.get("name")
        ],
        "description": payload.get("description")
        if isinstance(payload.get("description"), str)
        else None,
        "page_count": payload.get("number_of_pages"),
        "identifiers": {},
        "cover": payload.get("cover") or {},
        "preview_urls": [],
        "access_urls": [],
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
    # ebooks/download links via Internet Archive when available
    ebooks = payload.get("ebooks") or []
    candidates: list[str] = []
    for e in ebooks:
        if e.get("availability") == "full" and e.get("formats"):
            for f in e.get("formats"):
                href = f.get("url") or f.get("read_url")
                if href:
                    candidates.append(href)
    if candidates:
        from app.services.isbn.client_base import filter_alive_urls

        book["access_urls"] = filter_alive_urls(candidates, timeout=5.0)
    client.close()
    return book


def search_by_title(
    title: str, *, max_results: int = 5, timeout: float = 10.0
) -> List[NormalizedBook]:
    # Open Library search API
    client = HttpClient(base_url="https://openlibrary.org", timeout=timeout)
    r = client.get("/search.json", params={"title": title, "limit": max_results})
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    docs = data.get("docs") or []
    results: List[NormalizedBook] = []
    for d in docs:
        nb: NormalizedBook = {
            "source": "open_library",
            "isbn": (d.get("isbn") or [""])[0]
            if isinstance(d.get("isbn"), list)
            else "",
            "title": d.get("title"),
            "subtitle": None,
            "creators": [
                {"name": a, "role": None} for a in (d.get("author_name") or [])
            ],
            "publisher": (d.get("publisher") or [None])[0]
            if d.get("publisher")
            else None,
            "published_date": str(d.get("first_publish_year"))
            if d.get("first_publish_year")
            else None,
            "language": None,
            "subjects": d.get("subject") or [],
            "description": None,
            "page_count": None,
            "identifiers": {},
            "cover": {},
            "preview_urls": [],
            "raw": d,
        }
        results.append(nb)
    client.close()
    return results
