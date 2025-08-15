from __future__ import annotations


from app.services.isbn.types import NormalizedBook


def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> NormalizedBook:
    # 占位：建议通过正式 SRU/合作接口接入。此处不抓取 HTML。
    return {
        "source": "nlc_china",
        "isbn": isbn,
        "title": None,
        "subtitle": None,
        "creators": [],
        "publisher": None,
        "published_date": None,
        "language": "zh",
        "subjects": [],
        "description": None,
        "page_count": None,
        "identifiers": {},
        "cover": {},
        "preview_urls": [],
        "raw": {"message": "未配置官方 API 通道（SRU/JSON）。"},
    }
