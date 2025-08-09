from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.isbn.client_base import HttpClient, RateLimitError, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, wskey: str, access_token: Optional[str] = None, timeout: float = 10.0) -> NormalizedBook:
    # Prefer SRU-like JSON endpoint without OAuth where available
    client = HttpClient(base_url="https://worldcat.org", timeout=timeout)
    headers: Dict[str, str] = {}
    params: Dict[str, Any] = {"q": f"isbn:{isbn}", "wskey": wskey, "format": "json", "limit": 1}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    r = client.get("/discovery/bib/search", params=params, headers=headers)
    if r.status_code in (403, 429):
        client.close()
        raise RateLimitError("worldcat rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    items = (data.get("bibRecords") or []) if isinstance(data, dict) else []
    first = items[0] if items else {}
    # best-effort extraction depending on actual JSON structure
    title = None
    authors = []
    publisher = None
    published_date = None
    language = None
    subjects: list[str] = []
    try:
        # Some payloads expose these fields differently; keep best-effort mapping
        title = first.get("title") or (first.get("bib") or {}).get("title")
        auths = first.get("creator") or (first.get("bib") or {}).get("author")
        if isinstance(auths, list):
            authors = [str(a) for a in auths]
        elif isinstance(auths, str):
            authors = [auths]
        publisher = first.get("publisher")
        published_date = first.get("date") or first.get("publicationYear")
        language = first.get("language")
    except Exception:
        pass

    book: NormalizedBook = {
        "source": "worldcat",
        "isbn": isbn,
        "title": title,
        "subtitle": None,
        "creators": [{"name": a, "role": None} for a in authors],
        "publisher": publisher,
        "published_date": published_date,
        "language": language,
        "subjects": subjects,
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": data if isinstance(data, dict) else {},
    }
    client.close()
    return book
