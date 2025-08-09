from __future__ import annotations

from typing import Optional

from app.services.isbn.types import NormalizedBook
from app.services.isbn import (
    SOURCE_GOOGLE_BOOKS,
    SOURCE_OPEN_LIBRARY,
    SOURCE_ISBNDB,
    SOURCE_LOC,
)
from app.services.isbn import google_books, open_library, isbndb, loc


def fetch_by_isbn(source: str, isbn: str, *, api_key: Optional[str] = None, lang: Optional[str] = None, timeout: float = 10.0) -> NormalizedBook:
    if source == SOURCE_GOOGLE_BOOKS:
        return google_books.fetch_by_isbn(isbn, api_key=api_key, lang=lang, timeout=timeout)
    if source == SOURCE_OPEN_LIBRARY:
        return open_library.fetch_by_isbn(isbn, timeout=timeout)
    if source == SOURCE_ISBNDB:
        if not api_key:
            raise ValueError("ISBNdb requires api_key")
        return isbndb.fetch_by_isbn(isbn, api_key=api_key, timeout=timeout)
    if source == SOURCE_LOC:
        return loc.fetch_by_isbn(isbn, timeout=timeout)
    raise ValueError(f"Unsupported source: {source}")
