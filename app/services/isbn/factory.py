from __future__ import annotations

from typing import Optional

from app.services.isbn.types import NormalizedBook
from app.services.isbn import (
    SOURCE_GOOGLE_BOOKS,
    SOURCE_OPEN_LIBRARY,
    SOURCE_ISBNDB,
    SOURCE_LOC,
    SOURCE_WORLDCAT,
    SOURCE_NDL,
    SOURCE_BRITISH_LIBRARY,
    SOURCE_KOLISNET,
    SOURCE_NLC_CHINA,
    SOURCE_HKPL,
    SOURCE_JUHE_ISBN,
)
from app.services.isbn import google_books, open_library, isbndb, loc, worldcat, ndl, british_library, kolisnet, nlc, hkpl, juhe


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
    if source == SOURCE_WORLDCAT:
        if not api_key:
            raise ValueError("WorldCat requires wskey")
        return worldcat.fetch_by_isbn(isbn, wskey=api_key, timeout=timeout)
    if source == SOURCE_NDL:
        return ndl.fetch_by_isbn(isbn, timeout=timeout)
    if source == SOURCE_BRITISH_LIBRARY:
        return british_library.fetch_by_isbn(isbn, timeout=timeout)
    if source == SOURCE_KOLISNET:
        if not api_key:
            raise ValueError("KOLIS-NET requires service_key")
        return kolisnet.fetch_by_isbn(isbn, service_key=api_key, timeout=timeout)
    if source == SOURCE_NLC_CHINA:
        return nlc.fetch_by_isbn(isbn, timeout=timeout)
    if source == SOURCE_HKPL:
        return hkpl.fetch_by_isbn(isbn, timeout=timeout)
    if source == SOURCE_JUHE_ISBN:
        if not api_key:
            raise ValueError("Juhe ISBN requires api_key")
        return juhe.fetch_by_isbn(isbn, api_key=api_key, timeout=timeout)
    raise ValueError(f"Unsupported source: {source}")


def search_by_title(source: str, title: str, *, api_key: Optional[str] = None, lang: Optional[str] = None, max_results: int = 5, timeout: float = 10.0) -> list[NormalizedBook]:
    if source == SOURCE_GOOGLE_BOOKS:
        return google_books.search_by_title(title, api_key=api_key, lang=lang, max_results=max_results, timeout=timeout)
    if source == SOURCE_OPEN_LIBRARY:
        return open_library.search_by_title(title, max_results=max_results, timeout=timeout)
    if source == SOURCE_LOC:
        return loc.search_by_title(title, max_results=max_results, timeout=timeout)
    # WorldCat/NDL/BL/KOLISNET 官方搜索接口存在但需更复杂鉴权或 XML 解析，这里先不实现，返回空并由上层选择其他来源
    if source in (SOURCE_WORLDCAT, SOURCE_NDL, SOURCE_BRITISH_LIBRARY, SOURCE_KOLISNET, SOURCE_NLC_CHINA, SOURCE_HKPL, SOURCE_ISBNDB):
        raise NotImplementedError(f"title search not implemented for {source}")
    raise ValueError(f"Unsupported source: {source}")
