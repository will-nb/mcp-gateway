from __future__ import annotations

from typing import Any, Dict

from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    # 占位：HKPL 未公开稳定 JSON API，建议使用开放数据或正式合作接口。
    return {
        "source": "hkpl",
        "isbn": isbn,
        "title": None,
        "subtitle": None,
        "creators": [],
        "publisher": None,
        "published_date": None,
        "language": "zh-Hant",
        "subjects": [],
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": {"message": "HKPL 未提供公开 JSON API"},
    }
