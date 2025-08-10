from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.services.isbn.client_base import HttpClient, RateLimitError, HttpError, filter_alive_urls
from app.services.isbn.types import NormalizedBook


def _split_authors(author_field: Optional[str]) -> List[Dict[str, Optional[str]]]:
    if not author_field:
        return []
    separators = ["；", "，", ",", "/", "|", "、"]
    parts = [author_field]
    for sep in separators:
        parts = sum([p.split(sep) for p in parts], [])
    cleaned = [p.strip() for p in parts if p and p.strip()]
    return [{"name": name, "role": None} for name in cleaned]


def fetch_by_isbn(isbn: str, *, api_key: str, timeout: float = 10.0) -> NormalizedBook:
    client = HttpClient(base_url="http://apis.juhe.cn", timeout=timeout)
    r = client.get(
        "/isbn/query",
        params={"key": api_key, "isbn": isbn},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if r.status_code == 429:
        client.close()
        raise RateLimitError("juhe rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    data = r.json()
    # Juhe top-level: { reason, result: { data, orderid }, error_code }
    if not isinstance(data, dict):
        client.close()
        return {"source": "juhe_isbn", "isbn": isbn, "raw": {"unexpected": data}}

    if data.get("error_code") not in (0, "0"):
        client.close()
        return {"source": "juhe_isbn", "isbn": isbn, "raw": data}

    result = data.get("result") or {}
    payload = result.get("data") or {}

    # Map fields
    title = payload.get("title")
    subtitle = payload.get("subtitle")
    publisher = payload.get("publisher")
    pub_date = payload.get("pubDate")
    language = payload.get("language")
    description = payload.get("gist") or payload.get("summary")
    page_count: Optional[int] = None
    try:
        if payload.get("page") is not None:
            page_count = int(str(payload.get("page")).strip())
    except Exception:
        page_count = None
    isbn10 = payload.get("isbn10")
    isbn13 = payload.get("isbn")

    cover_url = payload.get("img")
    cover: Dict[str, Optional[str]] = {}
    if cover_url:
        cover = {"small": cover_url, "medium": cover_url, "large": cover_url}

    # Preview/related URLs
    preview_candidates: List[str] = []
    for key in ("ebookUrl", "previewUrl", "detailUrl", "doubanUrl", "url"):
        val = payload.get(key)
        if isinstance(val, str) and val.startswith("http"):
            preview_candidates.append(val)
    access_urls = filter_alive_urls(preview_candidates, timeout=5.0) if preview_candidates else []

    book: NormalizedBook = {
        "source": "juhe_isbn",
        "isbn": isbn,
        "title": title,
        "subtitle": subtitle,
        "creators": _split_authors(payload.get("author")),
        "publisher": publisher,
        "published_date": pub_date,
        "language": language,
        "subjects": [],
        "description": description,
        "page_count": page_count,
        "identifiers": {"isbn_10": isbn10, "isbn_13": isbn13},
        "cover": cover,
        "preview_urls": access_urls,
        "access_urls": [],
        "raw": data,
    }
    client.close()
    return book
