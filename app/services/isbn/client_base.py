from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class HttpClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _url(self, path: str) -> str:
        if self.base_url:
            if path.startswith("http://") or path.startswith("https://"):
                return path
            return f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        return path

    def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        url = self._url(path)
        return self._client.get(url, params=params, headers=headers)

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass


class RateLimitError(Exception):
    pass


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | None = None):
        super().__init__(message or f"HTTP error: {status_code}")
        self.status_code = status_code


def filter_alive_urls(urls: list[str], timeout: float = 5.0) -> list[str]:
    if not urls:
        return []
    alive: list[str] = []
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        for u in urls:
            try:
                resp = client.head(u)
                if resp.status_code >= 400:
                    resp = client.get(u)
                if 200 <= resp.status_code < 300:
                    alive.append(u)
            except Exception:
                continue
    return alive
