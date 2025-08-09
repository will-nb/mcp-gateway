from __future__ import annotations

from typing import Any, Dict

from app.services.isbn.client_base import HttpClient, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    client = HttpClient(base_url="https://www.loc.gov", timeout=timeout)
    r = client.get("/books/", params={"q": f"isbn:{isbn}", "fo": "json", "at": "results", "c": 1})
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    results = data.get("results") or []
    payload = results[0] if results else {}
    book: NormalizedBook = {
        "source": "loc",
        "isbn": isbn,
        "title": payload.get("title"),
        "subtitle": None,
        "creators": [{"name": payload.get("creator"), "role": None}] if payload.get("creator") else [],
        "publisher": payload.get("publisher"),
        "published_date": payload.get("date"),
        "language": payload.get("language"),
        "subjects": payload.get("subject") or [],
        "description": None,
        "page_count": None,
        "identifiers": {"loc_item": payload.get("id")},
        "cover": {},
        "preview_urls": [payload.get("id")] if payload.get("id") else [],
        "access_urls": [],
        "raw": data,
    }
    client.close()
    return book


def search_by_title(title: str, *, max_results: int = 5, timeout: float = 10.0) -> list[NormalizedBook]:
    client = HttpClient(base_url="https://www.loc.gov", timeout=timeout)
    r = client.get("/books/", params={"q": title, "fo": "json", "c": max_results})
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    results = []
    for it in (data.get("results") or [])[:max_results]:
        nb: NormalizedBook = {
            "source": "loc",
            "isbn": "",
            "title": it.get("title"),
            "subtitle": None,
            "creators": [{"name": it.get("creator"), "role": None}] if it.get("creator") else [],
            "publisher": it.get("publisher"),
            "published_date": it.get("date"),
            "language": it.get("language"),
            "subjects": it.get("subject") or [],
            "description": None,
            "page_count": None,
            "identifiers": {"loc_item": it.get("id")},
            "cover": {},
            "preview_urls": [it.get("id")] if it.get("id") else [],
            "raw": it,
        }
        results.append(nb)
    client.close()
    return results
