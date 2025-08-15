from __future__ import annotations

from typing import Dict, List, Optional

from app.core.config import get_settings
from app.services.mongo_client import get_database
from app.services.redis_client import get_redis_service
from app.services.isbn.factory import fetch_by_isbn as fetch_from_source
from app.services.isbn.types import NormalizedBook
from app.services.isbn import (
    SOURCE_LOC,
    SOURCE_NDL,
    SOURCE_KOLISNET,
    SOURCE_BRITISH_LIBRARY,
    SOURCE_HKPL,
    SOURCE_GOOGLE_BOOKS,
    SOURCE_OPEN_LIBRARY,
    SOURCE_ISBNDB,
    SOURCE_WORLDCAT,
    SOURCE_JUHE_ISBN,
)
from app.services.isbn.client_base import RateLimitError

# 固定请求超时时间（秒）
DEFAULT_FETCH_TIMEOUT = 10.0

# 国别优先级映射（示例，可扩展）
COUNTRY_PRIORITY: Dict[str, List[str]] = {
    "CN": [SOURCE_JUHE_ISBN],
    "HK": [SOURCE_HKPL],
    "JP": [SOURCE_NDL],
    "KR": [SOURCE_KOLISNET],
    "GB": [SOURCE_BRITISH_LIBRARY],
    "US": [SOURCE_LOC],
}

# 通用优先级：免费强 → 免费小 → 收费
GLOBAL_PRIORITY = [
    SOURCE_LOC,
    SOURCE_OPEN_LIBRARY,
    SOURCE_GOOGLE_BOOKS,
    SOURCE_WORLDCAT,
    SOURCE_ISBNDB,
]


def _infer_country_code_from_isbn(isbn: str) -> Optional[str]:
    # 仅做简单启发式，无需完全覆盖所有组号
    s = isbn.replace("-", "").strip()
    if len(s) == 13:
        if s.startswith("9787"):
            return "CN"
        if s.startswith("9784"):
            return "JP"
        if s.startswith("97911"):
            return "KR"
        if s.startswith("978962") or s.startswith("978988"):
            return "HK"
        if s.startswith("9780") or s.startswith("9781"):
            return "US"  # US/GB 共用段，按 US 处理
    elif len(s) == 10:
        if s.startswith("7"):
            return "CN"
        if s.startswith("4"):
            return "JP"
        if s.startswith("962") or s.startswith("988"):
            return "HK"
        if s.startswith("0") or s.startswith("1"):
            return "US"
    return None


def _rate_limit_key(source: str) -> str:
    return f"isbn:ratelimit:{source}"


def _is_rate_limited(source: str) -> bool:
    try:
        r = get_redis_service().get_client()
        return bool(r.get(_rate_limit_key(source)))
    except Exception:
        # If Redis is unavailable, treat as not rate-limited
        return False


def _set_rate_limited(source: str, ttl_seconds: int = 86400) -> None:
    try:
        r = get_redis_service().get_client()
        r.setex(_rate_limit_key(source), ttl_seconds, "1")
    except Exception:
        # Ignore if Redis is unavailable
        return


def _cache_book(doc: NormalizedBook) -> None:
    # 简易缓存：以 isbn 为 key 写入 mongo 集合 books（若采用我们之前的 schema）
    try:
        db = get_database()
        isbn = doc.get("identifiers", {}).get("isbn_13") or doc.get("isbn")
        if not isbn:
            return
        db["books"].update_one(
            {"_id": isbn}, {"$set": {"lastFetched": doc}}, upsert=True
        )
    except Exception:
        # Ignore cache errors
        return


def resolve_isbn(
    isbn: str, *, force_source: Optional[str] = None
) -> Optional[NormalizedBook]:
    # 1) 本地 Mongo 查询（简单示例）
    try:
        db = get_database()
        cached = db["books"].find_one({"_id": isbn})
        if cached and cached.get("lastFetched"):
            return cached["lastFetched"]
    except Exception:
        # Ignore cache read errors
        pass

    # 2) 构造候选来源列表
    order: List[str] = []
    inferred = _infer_country_code_from_isbn(isbn)
    if inferred:
        order += COUNTRY_PRIORITY.get(inferred, [])
    order += GLOBAL_PRIORITY
    # 去重，保持顺序
    seen = set()
    order = [s for s in order if not (s in seen or seen.add(s))]

    # 如果强制指定来源，优先且仅尝试该来源。如果该来源在屏蔽期内，直接返回限流错误。
    if force_source:
        if _is_rate_limited(force_source):
            raise RateLimitError(f"{force_source} currently rate-limited")
        order = [force_source]

    # 3) 逐一尝试调用，遇到 429 或明确限流错误则标记 24h 不再调用
    s = get_settings()
    for src in order:
        if _is_rate_limited(src):
            continue
        try:
            if src == SOURCE_GOOGLE_BOOKS:
                doc = fetch_from_source(
                    src,
                    isbn,
                    api_key=s.google_books_api_key,
                    timeout=DEFAULT_FETCH_TIMEOUT,
                )
            elif src == SOURCE_OPEN_LIBRARY:
                doc = fetch_from_source(src, isbn, timeout=DEFAULT_FETCH_TIMEOUT)
            elif src == SOURCE_ISBNDB:
                key = s.isbndb_api_key
                if not key:
                    continue
                doc = fetch_from_source(
                    src, isbn, api_key=key, timeout=DEFAULT_FETCH_TIMEOUT
                )
            elif src == SOURCE_LOC:
                doc = fetch_from_source(src, isbn, timeout=DEFAULT_FETCH_TIMEOUT)
            elif src == SOURCE_WORLDCAT:
                key = s.worldcat_wskey
                if not key:
                    continue
                doc = fetch_from_source(
                    src, isbn, api_key=key, timeout=DEFAULT_FETCH_TIMEOUT
                )
            elif src == SOURCE_JUHE_ISBN:
                key = s.juhe_isbn_api_key
                if not key:
                    continue
                doc = fetch_from_source(
                    src, isbn, api_key=key, timeout=DEFAULT_FETCH_TIMEOUT
                )
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
