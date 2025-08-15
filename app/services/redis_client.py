from __future__ import annotations

from functools import lru_cache
from typing import Optional, Any

from app.core.config import get_settings


class RedisService:
    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: Optional[str],
        key_prefix: str,
    ) -> None:
        self._prefix = key_prefix
        # Lazy import to avoid hard dependency during tests unless used
        import importlib

        redis_mod: Any = importlib.import_module("redis")
        self._client = redis_mod.Redis(
            host=host, port=port, db=db, password=password, decode_responses=True
        )

    def prefixed(self, key: str) -> str:
        return f"{self._prefix}:{key}" if self._prefix else key

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def get_client(self) -> Any:
        return self._client


@lru_cache(maxsize=1)
def get_redis_service() -> RedisService:
    s = get_settings()
    return RedisService(
        host=s.redis_host,
        port=s.redis_port,
        db=s.redis_db,
        password=s.redis_password,
        key_prefix=s.redis_key_prefix,
    )
