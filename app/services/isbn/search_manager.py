from __future__ import annotations

from typing import Dict, List, Optional

from app.services.isbn.factory import search_by_title as search_from_source
from app.services.isbn.types import NormalizedBook
from app.services.isbn import (
    SOURCE_LOC,
    SOURCE_OPEN_LIBRARY,
    SOURCE_GOOGLE_BOOKS,
)
from app.utils.text_similarity import jaccard_token_similarity

# 默认顺序：免费强 → 免费小 → 另一个全球
DEFAULT_SOURCES = [SOURCE_LOC, SOURCE_OPEN_LIBRARY, SOURCE_GOOGLE_BOOKS]


def search_title(title: str, *, max_results_per_source: int = 5, min_similarity: float = 0.5, api_keys: Optional[Dict[str, str]] = None, lang: Optional[str] = None, timeout: float = 10.0, prefer_order: Optional[List[str]] = None, force_source: Optional[str] = None) -> List[NormalizedBook]:
    order = list(DEFAULT_SOURCES)
    if prefer_order:
        for s in reversed(prefer_order):
            if s in order:
                order.remove(s)
            order.insert(0, s)
    if force_source:
        order = [force_source]

    collected: List[NormalizedBook] = []
    seen = set()
    for src in order:
        try:
            if src == SOURCE_GOOGLE_BOOKS:
                items = search_from_source(src, title, api_key=(api_keys or {}).get("google_books"), lang=lang, max_results=max_results_per_source, timeout=timeout)
            elif src == SOURCE_OPEN_LIBRARY:
                items = search_from_source(src, title, max_results=max_results_per_source, timeout=timeout)
            elif src == SOURCE_LOC:
                items = search_from_source(src, title, max_results=max_results_per_source, timeout=timeout)
            else:
                continue
        except Exception:
            continue
        for nb in items:
            sim = jaccard_token_similarity(title, nb.get("title") or "")
            if sim >= min_similarity:
                key = (nb.get("title") or "") + "|" + (nb.get("isbn") or "")
                if key in seen:
                    continue
                seen.add(key)
                collected.append(nb)
    return collected
