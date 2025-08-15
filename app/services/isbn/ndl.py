from __future__ import annotations


from app.services.isbn.client_base import HttpClient, RateLimitError, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    # NDL SRU endpoint (XML). Here we call JSON if ever available; otherwise leave raw as placeholder.
    client = HttpClient(base_url="https://ndlsearch.ndl.go.jp", timeout=timeout)
    r = client.get(
        "/api/sru",
        params={
            "operation": "searchRetrieve",
            "recordSchema": "dcndl",
            "maximumRecords": 1,
            "query": f"isbn={isbn}",
        },
    )
    if r.status_code in (403, 429):
        client.close()
        raise RateLimitError("ndl rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    # For simplicity retain raw XML as string; a full XML parse can be added later
    data = r.text
    book: NormalizedBook = {
        "source": "ndl",
        "isbn": isbn,
        "title": None,
        "subtitle": None,
        "creators": [],
        "publisher": None,
        "published_date": None,
        "language": "ja",
        "subjects": [],
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": {"xml": data},
    }
    client.close()
    return book
