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

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = self._url(path)
        return self._client.get(url, params=params, headers=headers)

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass
