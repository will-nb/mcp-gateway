from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class NormalizedBook(TypedDict, total=False):
    source: str
    isbn: str
    title: Optional[str]
    subtitle: Optional[str]
    creators: List[Dict[str, Optional[str]]]
    publisher: Optional[str]
    published_date: Optional[str]
    language: Optional[str]
    subjects: List[str]
    description: Optional[str]
    page_count: Optional[int]
    identifiers: Dict[str, Optional[str]]
    cover: Dict[str, Optional[str]]
    preview_urls: List[str]
    raw: Dict[str, Any]


class SearchResult(TypedDict, total=False):
    source: str
    items: List[NormalizedBook]
