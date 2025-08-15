from __future__ import annotations


from app.services.isbn.client_base import HttpClient, RateLimitError, HttpError
from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    # British Library SRU (XML)
    client = HttpClient(base_url="https://sru.bl.uk", timeout=timeout)
    r = client.get(
        "/SRU",
        params={
            "operation": "searchRetrieve",
            "version": "1.2",
            "query": f'isbn="{isbn}"',
            "maximumRecords": 1,
            "recordSchema": "mods",
        },
    )
    if r.status_code in (403, 429):
        client.close()
        raise RateLimitError("british_library rate limited")
    if r.status_code >= 400:
        client.close()
        raise HttpError(r.status_code, r.text)
    xml = r.text
    book: NormalizedBook = {
        "source": "british_library",
        "isbn": isbn,
        "title": None,
        "subtitle": None,
        "creators": [],
        "publisher": None,
        "published_date": None,
        "language": "en",
        "subjects": [],
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": {"xml": xml},
    }
    client.close()
    return book
