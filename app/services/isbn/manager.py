from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.services.mongo_client import get_database
from app.services.redis_client import get_redis_service
from app.services.isbn.factory import fetch_by_isbn as fetch_from_source
from app.services.isbn.types import NormalizedBook
from app.services.isbn import (
    SOURCE_LOC,
    SOURCE_NLC_CHINA,
    SOURCE_NDL,
    SOURCE_KOLISNET,
    SOURCE_BRITISH_LIBRARY,
    SOURCE_HKPL,
    SOURCE_GOOGLE_BOOKS,
    SOURCE_OPEN_LIBRARY,
    SOURCE_ISBNDB,
    SOURCE_WORLDCAT,
)
from app.services.isbn.client_base import RateLimitError

# 国别优先级映射（示例，可扩展）
COUNTRY_PRIORITY: Dict[str, List[str]] = {
    "CN": [SOURCE_NLC_CHINA],
    "HK": [SOURCE_HKPL],
    "JP": [SOURCE_NDL],
    "KR": [SOURCE_KOLISNET],
    "GB": [SOURCE_BRITISH_LIBRARY],
    "US": [SOURCE_LOC],
}

# 通用优先级：免费强 → 免费小 → 收费
GLOBAL_PRIORITY = [SOURCE_LOC, SOURCE_OPEN_LIBRARY, SOURCE_GOOGLE_BOOKS, SOURCE_WORLDCAT, SOURCE_ISBNDB]


def _rate_limit_key(source: str) -> str:
    return f"isbn:ratelimit:{source}"


def _is_rate_limited(source: str) -> bool:
    r = get_redis_service().get_client()
    return bool(r.get(_rate_limit_key(source)))


def _set_rate_limited(source: str, ttl_seconds: int = 86400) -> None:
    r = get_redis_service().get_client()
    r.setex(_rate_limit_key(source), ttl_seconds, "1")


def _cache_book(doc: NormalizedBook) -> None:
    # 简易缓存：以 isbn 为 key 写入 mongo 集合 books（若采用我们之前的 schema）
    db = get_database()
    isbn = doc.get("identifiers", {}).get("isbn_13") or doc.get("isbn")
    if not isbn:
        return
    db["books"].update_one({"_id": isbn}, {"$set": {"lastFetched": doc}}, upsert=True)


def resolve_isbn(isbn: str, *, country_code: Optional[str] = None, prefer_order: Optional[List[str]] = None, api_keys: Optional[Dict[str, str]] = None, timeout: float = 10.0, force_source: Optional[str] = None) -> Optional[NormalizedBook]:
    # 1) 本地 Mongo 查询（简单示例）
    db = get_database()
    cached = db["books"].find_one({"_id": isbn})
    if cached and cached.get("lastFetched"):
        return cached["lastFetched"]

    # 2) 构造候选来源列表
    order: List[str] = []
    if country_code:
        order += COUNTRY_PRIORITY.get(country_code.upper(), [])
    order += GLOBAL_PRIORITY
    # 去重，保持顺序
    seen = set()
    order = [s for s in order if not (s in seen or seen.add(s))]
    if prefer_order:
        # 可选：将外部传入的覆盖到最前
        for src in reversed(prefer_order):
            if src in order:
                order.remove(src)
            order.insert(0, src)

    # 如果强制指定来源，优先且仅尝试该来源。如果该来源在屏蔽期内，直接返回限流错误。
    if force_source:
        if _is_rate_limited(force_source):
            raise RateLimitError(f"{force_source} currently rate-limited")
        order = [force_source]

    # 3) 逐一尝试调用，遇到 429 或明确限流错误则标记 24h 不再调用
    for src in order:
        if _is_rate_limited(src):
            continue
        try:
            if src == SOURCE_GOOGLE_BOOKS:
                doc = fetch_from_source(src, isbn, api_key=(api_keys or {}).get("google_books"), timeout=timeout)
            elif src == SOURCE_OPEN_LIBRARY:
                doc = fetch_from_source(src, isbn, timeout=timeout)
            elif src == SOURCE_ISBNDB:
                key = (api_keys or {}).get("isbndb")
                if not key:
                    continue
                doc = fetch_from_source(src, isbn, api_key=key, timeout=timeout)
            elif src == SOURCE_LOC:
                doc = fetch_from_source(src, isbn, timeout=timeout)
            else:
                # 其他来源暂未实现或需要签约：跳过
                continue
            # 命中标题或作者等基本字段即认为有效
            if doc and (doc.get("title") or doc.get("creators")):
                _cache_book(doc)
                return doc
        except RateLimitError:
            _set_rate_limited(src)
            if force_source:
                # 用户强制的来源被限流，则直接抛出
                raise
            continue
        except Exception as e:
            msg = str(e).lower()
            if "429" in msg or "rate limit" in msg or "too many requests" in msg:
                _set_rate_limited(src)
                continue
            # 其他错误继续下一个来源
            continue
    return None
